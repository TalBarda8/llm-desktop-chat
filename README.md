# Local LLM Desktop Chat Application

A desktop chat application that connects to local LLM models via the Ollama API. Chat privately with AI models running entirely on your machine.

## Features

- **Private & Local**: All conversations happen on your machine - no data sent to external servers
- **Real-time Streaming**: See AI responses as they're generated
- **Multiple Models**: Switch between different Ollama models on the fly
- **Simple UI**: Clean, intuitive Tkinter-based interface
- **Conversation Management**: Start new chats and maintain conversation context

## Prerequisites

1. **Python 3.10 or higher** installed on your system (Python 3.12+ recommended)

   **macOS Users**: If you're on macOS Sequoia (15.0+), use Homebrew Python to avoid Tkinter compatibility issues:
   ```bash
   brew install python@3.12
   ```
   Then use `python3.12` instead of `python3` for all commands below.

2. **Ollama** installed and running
   - Download from: https://ollama.ai
   - Install and start the Ollama service

3. **At least one model pulled** in Ollama:
   ```bash
   ollama pull llama2
   # or
   ollama pull mistral
   # or
   ollama pull codellama
   ```

## Installation

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/llm-desktop-chat.git
   cd llm-desktop-chat
   ```

2. **Create a virtual environment** (recommended):

   For most systems:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

   For macOS Sequoia users with Homebrew Python:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional: Create a `.env` file for custom configuration**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` to customize settings:
   ```bash
   OLLAMA_BASE_URL=http://localhost:11434
   DEFAULT_MODEL=llama2
   WINDOW_WIDTH=900
   WINDOW_HEIGHT=700
   ```

## Usage

### Starting the Application

**Easiest method** - Use the startup script:
```bash
./start.sh
```

This script automatically activates the virtual environment and launches the application.

**Alternative methods**:

1. Activate venv first, then run:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python -m src.main
   ```

2. Run directly with venv Python:
   ```bash
   venv/bin/python -m src.main
   ```

**Important**: Don't use `python3 -m src.main` directly without activating the venv first, as it may use your system Python which could have an incompatible Tkinter version.

### Using the Chat Interface

1. **Select a Model**: Use the dropdown in the top toolbar to choose your model
2. **Type Your Message**: Enter your message in the text box at the bottom
3. **Send**: Click "Send" or press Enter (Shift+Enter for new line)
4. **View Response**: Watch the AI's response stream in real-time
5. **New Chat**: Click "New Chat" to start a fresh conversation

### Example Conversation

```
You: What is Python?
Assistant: Python is a high-level, interpreted programming language...
(Streaming response displays in real-time)

You: Write a hello world program in Python
Assistant: Here's a simple hello world program in Python:

print("Hello, World!")

That's it! Python's syntax is designed to be clean and readable...
```

## Project Structure

```
llm-desktop-chat/
├── src/
│   ├── main.py                 # Application entry point
│   ├── api/
│   │   └── ollama_client.py    # Ollama API client
│   ├── core/
│   │   ├── chat_manager.py     # Business logic
│   │   └── message.py          # Data models
│   ├── gui/
│   │   └── app.py              # Tkinter GUI
│   ├── config/
│   │   └── settings.py         # Configuration
│   └── utils/
│       ├── logger.py           # Logging setup
│       └── exceptions.py       # Custom exceptions
├── tests/
│   └── test_message.py         # Unit tests
├── logs/                       # Application logs
├── requirements.txt
└── README.md
```

## Code Overview

### Key Components

1. **OllamaClient** (`src/api/ollama_client.py`)
   - Communicates with Ollama API
   - Handles streaming responses
   - Lists available models

2. **ChatManager** (`src/core/chat_manager.py`)
   - Manages conversation state
   - Orchestrates API calls
   - Maintains message history

3. **ChatApplication** (`src/gui/app.py`)
   - Tkinter-based user interface
   - Real-time message display
   - Input handling and validation

4. **Message & Conversation** (`src/core/message.py`)
   - Data models for messages
   - Conversation management
   - API format conversion

### How It Works

```
User types message
    ↓
GUI captures input
    ↓
ChatManager adds user message to conversation
    ↓
OllamaClient sends request to Ollama API
    ↓
API streams response chunks
    ↓
GUI displays each chunk in real-time
    ↓
ChatManager adds complete response to conversation
```

## Testing

Run the unit tests:

```bash
pytest tests/ -v
```

Run specific test file:

```bash
pytest tests/test_message.py -v
```

## Troubleshooting

### "Cannot connect to Ollama"

1. Verify Ollama is installed:
   ```bash
   ollama --version
   ```

2. Start Ollama service:
   ```bash
   ollama serve
   ```

3. Test Ollama is working:
   ```bash
   ollama list
   ```

### "No models found"

Pull a model:
```bash
ollama pull llama2
```

### Application won't start

1. Check Python version (must be 3.10+):
   ```bash
   python --version
   ```

2. Verify dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

3. Check logs in `logs/app.log` for error details

### macOS Tkinter Error: "macOS 15 (1507) or later required"

This error occurs on macOS Sequoia when using the system Python with an outdated Tkinter version.

**Solution**:
1. Install Python via Homebrew:
   ```bash
   brew install python@3.12
   ```

2. Recreate your virtual environment with Homebrew Python:
   ```bash
   rm -rf venv
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python -m src.main
   ```

**Why this happens**: macOS Sequoia (15.0+) requires Tkinter 9.0+, but system Python 3.9 includes an older version. Homebrew Python 3.12 includes the compatible Tkinter version.

## Configuration Options

All settings can be customized in `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `DEFAULT_MODEL` | `llama2` | Model to use by default |
| `WINDOW_TITLE` | `Local LLM Chat` | Application window title |
| `WINDOW_WIDTH` | `900` | Window width in pixels |
| `WINDOW_HEIGHT` | `700` | Window height in pixels |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | `logs/app.log` | Path to log file |

## MVP Scope (Current Features)

- ✅ Single conversation interface
- ✅ Send and receive messages
- ✅ Streaming responses
- ✅ Model selection
- ✅ New chat functionality
- ✅ Connection error handling

## Future Enhancements (Post-MVP)

- 💡 Save/load conversation history to disk
- 💡 Multiple conversation tabs
- 💡 Message editing and regeneration
- 💡 Code syntax highlighting
- 💡 Export conversations (markdown, PDF)
- 💡 Custom system prompts
- 💡 Model parameter tuning (temperature, top_p)
- 💡 Dark mode theme
- 💡 Keyboard shortcuts

## Requirements

**Python Version**: 3.10 or higher (3.12+ recommended for macOS Sequoia users)

See `requirements.txt` for full list. Main dependencies:

- `httpx` - HTTP client for API communication
- `pydantic` - Data validation and settings
- `pydantic-settings` - Settings management
- `python-dotenv` - Environment variable loading
- Tkinter - GUI framework (included with Python, requires version 9.0+ on macOS 15+)

## License

This project is provided as-is for educational and personal use.

## Contributing

This is a prototype/MVP. Feel free to fork and extend for your own use.

## Acknowledgments

- Built for use with [Ollama](https://ollama.ai)
- Designed for local, private AI conversations
