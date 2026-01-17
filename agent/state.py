"""
State management for the LangGraph agent.

Defines the state schema that tracks conversation history,
user fitness information, and tool execution results.
"""

from typing import TypedDict, Annotated, Sequence, NotRequired
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    State schema for the fitness coach agent.
    
    Attributes:
        messages: Conversation history between user and agent
        fitness_level: User's current fitness level (e.g., "beginner", "intermediate", "advanced")
        fitness_goals: User's fitness goals (e.g., "build muscle", "lose weight", "improve endurance")
    """
    messages: Annotated[Sequence, add_messages]
    fitness_level: str
    fitness_goals: str
    route: NotRequired[str]
