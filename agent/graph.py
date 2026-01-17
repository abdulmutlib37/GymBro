"""
LangGraph agent implementation for the fitness coach.

Sets up the agent graph with tool routing, memory management,
and conversation handling using Ollama and LangGraph.
"""

from typing import Dict, Any, List, Optional, Tuple
import os
import requests
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agent.state import AgentState
from agent.prompts import SYSTEM_PROMPT
from tools.workout_plan import generate_workout_plan as generate_workout_plan_func
from tools.progress_report import generate_progress_report as generate_progress_report_func


# Define tools using LangChain's @tool decorator
@tool
def generate_workout_plan(fitness_level: str = "", fitness_goals: str = "") -> str:
    """
    Generate a personalized 3-day workout plan based on user's fitness level and goals.
    IMPORTANT: Use the current user's fitness level and goals from the conversation context.
    If the user mentioned their fitness level or goals in the chat, use those values.
    
    Args:
        fitness_level: User's fitness level (beginner, intermediate, advanced) - use the value discussed in conversation
        fitness_goals: User's fitness goals (e.g., "build muscle", "lose weight") - use the value discussed in conversation
    
    Returns:
        Success message with file path
    """
    level = (fitness_level or "intermediate").strip()
    goals = (fitness_goals or "general fitness").strip()
    result = generate_workout_plan_func(level, goals)
    return result["message"]


@tool
def generate_progress_report() -> str:
    """
    Generate a CSV report with exercise progress data.
    
    Returns:
        Success message with file path and record count
    """
    result = generate_progress_report_func()
    return f"{result['message']} ({result['records']} records)"


def create_agent():
    """
    Create and configure the LangGraph agent for the fitness coach.
    
    Returns:
        Configured StateGraph agent
    """
    base_url = "http://localhost:11434"
    model = os.environ.get("GYMBRO_MODEL", "llama3.2")
    temperature = float(os.environ.get("GYMBRO_TEMPERATURE", "0.4"))
    num_predict = int(os.environ.get("GYMBRO_NUM_PREDICT", "96"))
    num_ctx = int(os.environ.get("GYMBRO_NUM_CTX", "1024"))
    max_context_messages = int(os.environ.get("GYMBRO_MAX_CONTEXT_MESSAGES", "6"))
    native_tool_calling = os.environ.get("GYMBRO_NATIVE_TOOL_CALLING", "0").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    tool_schemas = [
        {
            "type": "function",
            "function": {
                "name": "generate_workout_plan",
                "description": "Generate a personalized workout plan and export it to outputs/workout_plan.txt.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fitness_level": {
                            "type": "string",
                            "description": "User fitness level (beginner/intermediate/advanced).",
                        },
                        "fitness_goals": {
                            "type": "string",
                            "description": "User fitness goals (e.g., build muscle, lose weight).",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "generate_progress_report",
                "description": "Generate a CSV progress report and export it to outputs/progress_report.csv.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
    ]

    def _ollama_chat(messages: List) -> str:
        messages = list(messages)[-max_context_messages:]
        payload_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                role = "system"
            elif isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            elif isinstance(msg, ToolMessage):
                role = "tool"
            else:
                role = "user"

            payload_messages.append({"role": role, "content": str(getattr(msg, "content", "") or "")})

        payload = {
            "model": model,
            "stream": True,
            "messages": payload_messages,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
                "num_ctx": num_ctx,
            },
        }

        resp = requests.post(
            f"{base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=(10, 600),
        )
        resp.raise_for_status()

        parts: list[str] = []
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue

            import json

            data = json.loads(line)

            msg = data.get("message") or {}
            chunk = msg.get("content")
            if chunk:
                parts.append(str(chunk))

            if data.get("done") is True:
                break

        return "".join(parts).strip()

    def _ollama_chat_with_tools(messages: List) -> Tuple[str, Optional[list]]:
        messages = list(messages)[-max_context_messages:]
        payload_messages: list[dict] = []

        for msg in messages:
            if isinstance(msg, SystemMessage):
                role = "system"
            elif isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            elif isinstance(msg, ToolMessage):
                role = "tool"
            else:
                role = "user"

            payload_messages.append({"role": role, "content": str(getattr(msg, "content", "") or "")})

        payload = {
            "model": model,
            "stream": True,
            "messages": payload_messages,
            "tools": tool_schemas,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
                "num_ctx": num_ctx,
            },
        }

        resp = requests.post(
            f"{base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=(10, 600),
        )
        resp.raise_for_status()

        import json

        parts: list[str] = []
        tool_calls: Optional[list] = None
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue

            data = json.loads(line)

            msg = data.get("message") or {}
            chunk = msg.get("content")
            if chunk:
                parts.append(str(chunk))

            if msg.get("tool_calls"):
                tool_calls = msg.get("tool_calls")

            if data.get("done") is True:
                break

        return "".join(parts).strip(), tool_calls

    # Create the graph
    graph = StateGraph(AgentState)

    def _latest_user_text(state: AgentState) -> str:
        for msg in reversed(state.get("messages", [])):
            if isinstance(msg, HumanMessage):
                return str(msg.content or "").strip()
        return ""

    def route_node(state: AgentState) -> Dict[str, Any]:
        """Decide next step without native tool calling."""
        if native_tool_calling:
            return {"route": "chat"}
        user_text = _latest_user_text(state).lower()

        if any(kw in user_text for kw in ["workout plan", "routine", "workout routine", "training plan", "program"]):
            return {"route": "workout_tool"}
        if any(kw in user_text for kw in ["progress", "report", "csv", "track"]):
            return {"route": "progress_tool"}
        return {"route": "chat"}

    def chat_node(state: AgentState) -> Dict[str, Any]:
        messages = list(state.get("messages", []))

        system_content = SYSTEM_PROMPT
        system_content += "\n\nKeep responses concise: 3-6 sentences unless the user asks for more detail."
        if state.get("fitness_level"):
            system_content += f"\n\nCurrent user fitness level: {state['fitness_level']}"
        if state.get("fitness_goals"):
            system_content += f"\nCurrent user fitness goals: {state['fitness_goals']}"

        messages = [SystemMessage(content=system_content)] + messages

        user_text = _latest_user_text(state).lower()

        if native_tool_calling:
            try:
                content, tool_calls = _ollama_chat_with_tools(messages)

                if tool_calls:
                    out_messages: list = []
                    for call in tool_calls:
                        fn = (call.get("function") or {}).get("name")
                        args = (call.get("function") or {}).get("arguments") or {}

                        if isinstance(args, str):
                            import json

                            try:
                                args = json.loads(args)
                            except Exception:
                                args = {}

                        if fn == "generate_workout_plan":
                            level = str(args.get("fitness_level") or state.get("fitness_level") or "intermediate")
                            goals = str(args.get("fitness_goals") or state.get("fitness_goals") or "general fitness")
                            result = generate_workout_plan_func(level, goals)
                            out_messages.append(ToolMessage(content=result["message"], tool_call_id=str(call.get("id", ""))))
                        elif fn == "generate_progress_report":
                            result = generate_progress_report_func()
                            out_messages.append(ToolMessage(content=result["message"], tool_call_id=str(call.get("id", ""))))

                    if out_messages:
                        followup_messages = list(messages)
                        if content:
                            followup_messages.append(AIMessage(content=content))
                        followup_messages.extend(out_messages)
                        final = _ollama_chat(followup_messages)
                        return {"messages": out_messages + [AIMessage(content=final)]}

                if any(kw in user_text for kw in ["workout plan", "routine", "workout routine", "training plan", "program"]):
                    result = generate_workout_plan_func(
                        str(state.get("fitness_level", "intermediate") or "intermediate"),
                        str(state.get("fitness_goals", "general fitness") or "general fitness"),
                    )
                    return {"messages": [AIMessage(content=result["message"])]}
                if any(kw in user_text for kw in ["progress", "report", "csv", "track"]):
                    result = generate_progress_report_func()
                    return {"messages": [AIMessage(content=result["message"])]}

                return {"messages": [AIMessage(content=content)]}
            except Exception:
                pass

        content = _ollama_chat(messages)
        return {"messages": [AIMessage(content=content)]}

    def workout_tool_node(state: AgentState) -> Dict[str, Any]:
        level = str(state.get("fitness_level", "intermediate") or "intermediate")
        goals = str(state.get("fitness_goals", "general fitness") or "general fitness")
        result = generate_workout_plan_func(level, goals)
        return {"messages": [AIMessage(content=result["message"])]}

    def progress_tool_node(state: AgentState) -> Dict[str, Any]:
        result = generate_progress_report_func()
        return {"messages": [AIMessage(content=result["message"])]}

    def should_continue(state: AgentState) -> str:
        route = state.get("route", "chat")
        if route == "workout_tool":
            return "workout_tool"
        if route == "progress_tool":
            return "progress_tool"
        return "chat"
    
    graph.add_node("route", route_node)
    graph.add_node("chat", chat_node)
    graph.add_node("workout_tool", workout_tool_node)
    graph.add_node("progress_tool", progress_tool_node)

    graph.set_entry_point("route")
    graph.add_conditional_edges(
        "route",
        should_continue,
        {
            "chat": "chat",
            "workout_tool": "workout_tool",
            "progress_tool": "progress_tool",
        },
    )

    graph.add_edge("chat", END)
    graph.add_edge("workout_tool", END)
    graph.add_edge("progress_tool", END)
    
    # Compile graph with memory
    memory = MemorySaver()
    app = graph.compile(checkpointer=memory)
    
    return app


def extract_fitness_info(messages: List) -> tuple[str, str]:
    """
    Extract fitness level and goals from conversation messages.
    
    Args:
        messages: List of conversation messages
    
    Returns:
        Tuple of (fitness_level, fitness_goals)
    """
    fitness_level = ""
    fitness_goals = ""
    
    # Simple extraction from recent messages
    for msg in messages[-5:]:  # Check last 5 messages
        if isinstance(msg, HumanMessage):
            content = msg.content.lower()
            # Look for fitness level mentions
            if "beginner" in content:
                fitness_level = "beginner"
            elif "intermediate" in content:
                fitness_level = "intermediate"
            elif "advanced" in content:
                fitness_level = "advanced"
            
            # Look for goal mentions
            if "muscle" in content or "strength" in content:
                fitness_goals = "build muscle"
            elif "weight" in content or "lose" in content or "fat" in content:
                fitness_goals = "lose weight"
            elif "endurance" in content or "cardio" in content:
                fitness_goals = "improve endurance"
    
    return fitness_level or "intermediate", fitness_goals or "general fitness"
