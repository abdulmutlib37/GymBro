# Gymbro (Console) — Local AI Fitness Coach

Gymbro is a console-based AI fitness coach that runs fully locally using an Ollama-hosted LLM and a LangGraph agent. It supports free-form fitness chat with short-term conversational context and can generate two artifacts:

- A workout plan exported to a text file
- A progress report exported to a CSV file

## Features

- **Local LLM via Ollama**: No cloud APIs.
- **Conversational coaching**: Fitness-centric guidance with session memory.
- **Workout plan export**: Writes `outputs/workout_plan.txt`.
- **Progress report export**: Writes `outputs/progress_report.csv`.
- **Tool routing**: Selects between chat vs. tools based on user intent.

## Prerequisites

- **Python 3.8+**
- **Ollama** installed and running
- An Ollama model available locally (recommended: `llama3.2` or `llama3.2:3b`)

### Installing Ollama

1. Download Ollama from https://ollama.ai
2. Install Ollama for your OS and start the Ollama service
3. Pull a model:
    ```bash
    ollama pull llama3.2
    ```
    Optional smaller/faster model:
    ```bash
    ollama pull llama3.2:3b
    ```

## Installation

1. Clone or download this repository.
2. Create and activate a virtual environment (recommended).
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Confirm Ollama is running and the model is available:
    ```bash
    ollama list
    ```
2. Run the app:
    ```bash
    python app.py
    ```
3. Example prompts:
    - `I'm a beginner and want to build muscle.`
    - `Create a workout plan for me.`
    - `Generate a progress report.`
4. Type `exit` to quit.

## Configuration

Gymbro can be tuned via environment variables (useful for balancing speed vs. completeness):

- `GYMBRO_MODEL` (default: `llama3.2`)
- `GYMBRO_NATIVE_TOOL_CALLING` (default: `0`) — enable LLM-decided tool calling when supported; otherwise the app falls back to intent/keyword routing
- `GYMBRO_TEMPERATURE` (default: `0.4`)
- `GYMBRO_NUM_PREDICT` (default: `96`) — max tokens generated per response
- `GYMBRO_NUM_CTX` (default: `1024`) — context window size sent to the model
- `GYMBRO_MAX_CONTEXT_MESSAGES` (default: `6`) — number of recent messages sent each turn

Example (PowerShell):
```powershell
$env:GYMBRO_MODEL="llama3.2:3b"
$env:GYMBRO_NATIVE_TOOL_CALLING="1"
$env:GYMBRO_MAX_CONTEXT_MESSAGES="12"
$env:GYMBRO_NUM_CTX="2048"
$env:GYMBRO_NUM_PREDICT="400"
python app.py
```

### Switching to a different Ollama model

1. Pull the model:
```bash
ollama pull <model-name>
```

2. Verify it is installed:
```bash
ollama list
```

3. Run Gymbro with the model:
```powershell
$env:GYMBRO_MODEL="<model-name>"
python app.py
```

### Increase context size, output size, and memory/history

Gymbro’s effective “memory” is controlled by:

- `GYMBRO_MAX_CONTEXT_MESSAGES`: how many recent messages are sent to the model each turn
- `GYMBRO_NUM_CTX`: how large the model context window is (token budget for prompt + history)

Output length is controlled by:

- `GYMBRO_NUM_PREDICT`: maximum tokens the model can generate before it stops

PowerShell examples:

**More memory/history (remember more of the conversation):**
```powershell
$env:GYMBRO_MAX_CONTEXT_MESSAGES="16"
python app.py
```

**Larger context window (fit more text/history per turn):**
```powershell
$env:GYMBRO_NUM_CTX="4096"
python app.py
```

**Longer answers (reduce “cut off” responses):**
```powershell
$env:GYMBRO_NUM_PREDICT="600"
python app.py
```

**Detailed profile (slower, but more complete):**
```powershell
$env:GYMBRO_MODEL="llama3.2:3b"
$env:GYMBRO_MAX_CONTEXT_MESSAGES="16"
$env:GYMBRO_NUM_CTX="4096"
$env:GYMBRO_NUM_PREDICT="600"
python app.py
```

**Fast profile (quicker, but shorter answers and less history):**
```powershell
$env:GYMBRO_MODEL="llama3.2:3b"
$env:GYMBRO_MAX_CONTEXT_MESSAGES="6"
$env:GYMBRO_NUM_CTX="1024"
$env:GYMBRO_NUM_PREDICT="128"
python app.py
```

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

1. **Agent orchestration (LangGraph)**: Controls the flow between chat and tool execution.
2. **Local LLM (Ollama)**: The app calls Ollama's `/api/chat` endpoint.
3. **Session memory**: Recent messages plus extracted `fitness_level` and `fitness_goals` are included in the prompt each turn.
4. **Tool routing**: In the current implementation, tool usage is selected via simple intent/keyword routing (for reliability with local models).

## Example Workflow

```
You: I'm a beginner and want to lose weight
...
You: Show me my progress
Gymbro: [Agent invokes generate_progress_report tool]
        Progress report generated successfully and saved to outputs/progress_report.csv
```

## Output Files

- `outputs/workout_plan.txt`: A personalized workout plan.
- `outputs/progress_report.csv`: A CSV progress report.

## Troubleshooting

### Ollama connection issues
- Ensure Ollama is running: `ollama list`
- Confirm the service is reachable at `http://localhost:11434`

### Dependency/import errors
- Reinstall dependencies: `pip install -r requirements.txt`
- Confirm you are using the intended Python interpreter/venv

### Tool output issues
- Ensure the app can create/write to the `outputs/` directory (permissions)

## License

This project is provided as-is for educational and personal use.

## Contributing

Feel free to submit issues or pull requests if you'd like to improve Gymbro!
