"""
Gymbro - AI Fitness Coach Console Application

Main entry point for the Gymbro fitness coach application.
Handles user input/output and coordinates with the LangGraph agent.
"""

from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agent.graph import create_agent, extract_fitness_info


def main():
    """
    Main application loop for the Gymbro fitness coach.
    """
    print("=" * 60)
    print("Welcome to Gymbro - Your AI Fitness Coach!")
    print("=" * 60)
    print("\nI'm here to help you achieve your fitness goals.")
    print("You can ask me about workouts, nutrition, or request a workout plan.")
    print("Type 'exit' to quit.\n")
    
    # Create the agent
    try:
        print("Initializing AI agent...")
        agent = create_agent()
        print("Agent ready!\n")
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("\nPlease make sure:")
        print("1. Ollama is running (check with: ollama list)")
        print("2. A model that supports tools is installed:")
        print("   - llama3.2 (recommended): ollama pull llama3.2")
        print("   - llama3.1: ollama pull llama3.1")
        print("   Note: Base llama3 does NOT support tool calling")
        return
    
    # Initialize conversation state
    config = {"configurable": {"thread_id": "1"}, "recursion_limit": 25}
    fitness_level = "intermediate"
    fitness_goals = "general fitness"
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nThanks for using Gymbro! Stay fit and healthy!")
                break
            
            if not user_input:
                continue
            
            # Create state update with user message
            # LangGraph will merge this with existing state from memory
            state_update = {
                "messages": [HumanMessage(content=user_input)],
                "fitness_level": fitness_level,
                "fitness_goals": fitness_goals
            }
            
            # Invoke agent - it will use memory to maintain conversation history
            print("Gymbro is thinking...", flush=True)
            result = agent.invoke(state_update, config)
            
            # Extract fitness info from conversation for next iteration
            updated_fitness_info = extract_fitness_info(result["messages"])
            if updated_fitness_info[0]:
                fitness_level = updated_fitness_info[0]
            if updated_fitness_info[1]:
                fitness_goals = updated_fitness_info[1]
            
            # Print the latest useful output (prefer AI content; otherwise tool output)
            ai_response: Optional[str] = None
            tool_result: Optional[str] = None

            for msg in reversed(result.get("messages", [])):
                if ai_response is None and isinstance(msg, AIMessage):
                    content = getattr(msg, "content", None)
                    if content and str(content).strip():
                        ai_response = str(content)
                        break

                if tool_result is None and isinstance(msg, ToolMessage):
                    content = getattr(msg, "content", None)
                    if content and str(content).strip():
                        tool_result = str(content)

            if ai_response:
                print(f"\nGymbro: {ai_response}\n")
            elif tool_result:
                print(f"\nGymbro: {tool_result}\n")
            else:
                print("\nGymbro: I've processed your request. How can I help you further?\n")
            
        except EOFError:
            # Handle EOF error (e.g., when stdin is closed)
            print("\n\nInput stream closed. Exiting...")
            print("Thanks for using Gymbro! Stay fit and healthy!")
            break
        except KeyboardInterrupt:
            print("\n\nThanks for using Gymbro! Stay fit and healthy!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            import traceback
            print("Full error details:")
            traceback.print_exc()
            print("\nPlease try again or type 'exit' to quit.\n")


if __name__ == "__main__":
    main()
