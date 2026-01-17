# Gymbro - AI Fitness Coach

Gymbro is an AI-powered fitness coach console application that provides personalized workout plans, progress tracking, and fitness guidance using a local LLM via Ollama.

## Features

- 🤖 **AI-Powered Coaching**: Conversational AI fitness coach powered by Ollama's llama3 model
- 💪 **Personalized Workout Plans**: Generate customized 3-day workout plans based on your fitness level and goals
- 📊 **Progress Tracking**: Generate CSV reports to track your exercise progress over time
- 🧠 **Memory & Context**: The agent remembers your fitness level and goals throughout the conversation
- 🔧 **Tool Routing**: Intelligent tool selection based on conversation context
- 🏠 **Fully Local**: No cloud APIs or external services required - everything runs locally

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Ollama** installed and running with a tool-capable model (recommended: `llama3.2`)

### Installing Ollama

1. Download Ollama from [https://ollama.ai](https://ollama.ai)
2. Install Ollama according to your operating system
3. Pull a model that supports tool calling (required for this app):
   ```bash
   ollama pull llama3.2
   ```
   **Important:** The base `llama3` model does NOT support tool calling. You need `llama3.2` or `llama3.1` for this application to work.

## Installation

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd Gymbro
   ```

3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Make sure Ollama is running and a tool-capable model is available:
   ```bash
   ollama list
   ```
   You should see `llama3.2` (or `llama3.1`) in the list.

2. Run the application:
   ```bash
   python app.py
   ```

3. Start chatting with your AI fitness coach! Here are some example interactions:
   - "I'm a beginner and want to build muscle"
   - "Can you create a workout plan for me?"
   - "Show me my progress report"
   - "I want to lose weight"

4. Type `exit` to quit the application.

## Project Structure

```
Gymbro/
├── app.py                 # Main application entry point
├── agent/
│   ├── __init__.py
│   ├── graph.py          # LangGraph agent setup and configuration
│   ├── state.py          # Agent state schema definition
│   └── prompts.py        # System prompts for the fitness coach
├── tools/
│   ├── __init__.py
│   ├── workout_plan.py   # Workout plan generation tool
│   └── progress_report.py # Progress report generation tool
├── outputs/              # Generated files (created automatically)
│   ├── workout_plan.txt  # Generated workout plans
│   └── progress_report.csv # Generated progress reports
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## How It Works

1. **Agent Framework**: Uses LangGraph to manage conversation flow, memory, and tool routing
2. **LLM Integration**: Connects to Ollama's local llama3 model for natural language understanding
3. **State Management**: Tracks conversation history, fitness level, and goals throughout the session
4. **Tool Execution**: The agent intelligently decides when to use tools based on conversation context:
   - `generate_workout_plan`: Creates personalized workout plans
   - `generate_progress_report`: Generates CSV reports with exercise data
5. **Memory**: Conversation context is maintained using LangGraph's memory checkpointing

## Example Workflow

```
You: I'm a beginner and want to lose weight
Gymbro: Great! I'll help you create a workout plan focused on fat loss...

You: Can you create a workout plan for me?
Gymbro: [Agent invokes generate_workout_plan tool]
        Workout plan generated successfully and saved to outputs/workout_plan.txt

You: Show me my progress
Gymbro: [Agent invokes generate_progress_report tool]
        Progress report generated successfully and saved to outputs/progress_report.csv
```

## Output Files

- **workout_plan.txt**: Contains a personalized 3-day workout plan tailored to your fitness level and goals
- **progress_report.csv**: Contains sample exercise progress data in CSV format for tracking improvements

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama list`
- Verify a tool-capable model is installed: `ollama pull llama3.2`
- Check Ollama is accessible: The default endpoint is `http://localhost:11434`

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're using the correct Python version (3.8+)
- Check that you're in the correct virtual environment

### Tool Execution Errors
- Ensure the `outputs/` directory can be created (check write permissions)
- Verify file paths are correct

## License

This project is provided as-is for educational and personal use.

## Contributing

Feel free to submit issues or pull requests if you'd like to improve Gymbro!

---

**Stay fit and healthy! 💪**
