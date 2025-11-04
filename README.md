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

## Screenshots

Visual guide to the application interface and features.

### Main Chat Interface
**Description**: The main application window showing the clean, intuitive chat interface.
- **Top Toolbar**: Model selection dropdown and "New Chat" button
- **Chat Display Area**: Scrollable conversation history with user and assistant messages
- **Input Area**: Text box for typing messages with "Send" button

**What to show**: Full application window with an active conversation displayed.

### Model Selection
**Description**: The model dropdown menu showing available Ollama models.
- Shows all locally available models (llama2, mistral, codellama, etc.)
- Selected model is highlighted
- Easy switching between models mid-conversation

**What to show**: Dropdown menu expanded with multiple model options visible.

### Real-Time Streaming
**Description**: Live streaming of AI response as it's being generated.
- Text appears word-by-word in real-time
- Demonstrates the streaming capability
- Shows natural conversation flow

**What to show**: Screenshot captured during streaming with partial AI response visible.

### Multi-Turn Conversation
**Description**: Extended conversation showing context retention.
- Multiple back-and-forth exchanges
- AI remembers previous context
- Clean message separation between user and assistant

**What to show**: Conversation with at least 4-6 messages showing context awareness.

### New Chat Functionality
**Description**: Starting a fresh conversation.
- Empty chat display after clicking "New Chat"
- Model selector ready for new conversation
- Clean slate for new topic

**What to show**: Empty chat interface after starting new conversation.

### Error Handling
**Description**: User-friendly error messages when issues occur.
- Connection error when Ollama is not running
- Clear error message displayed in the interface
- Guidance on how to resolve the issue

**What to show**: Error message dialog or inline error notification.

### Code Formatting Example
**Description**: How the application displays code in responses.
- AI response containing code blocks
- Monospace font for code sections
- Readable formatting

**What to show**: Conversation where AI provides code examples (Python, JavaScript, etc.).

---

**Note**: To add actual screenshots, capture the application running locally and save images in a `docs/images/` directory. Then update this section with image references:
```markdown
![Main Chat Interface](docs/images/main-interface.png)
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

The project includes comprehensive unit tests covering all core functionality with 47 test cases.

### Running Tests

**Run all tests:**
```bash
source venv/bin/activate
pytest tests/ -v
```

**Run specific test file:**
```bash
pytest tests/test_message.py -v          # Message and Conversation tests
pytest tests/test_chat_manager.py -v     # ChatManager tests
pytest tests/test_ollama_client.py -v    # OllamaClient tests
pytest tests/test_settings.py -v         # Settings configuration tests
```

**Run with coverage report:**
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

**Run tests with detailed output:**
```bash
pytest tests/ -v -s
```

### Test Coverage

Current test coverage for core modules (as of latest test run):
- **ChatManager**: 100% coverage
- **Message & Conversation**: 100% coverage
- **OllamaClient**: 87% coverage
- **Settings**: 100% coverage
- **Exceptions**: 100% coverage
- **Logger**: 100% coverage

*Note: Run `pytest tests/ --cov=src --cov-report=term-missing` to see the latest coverage report.*

### Test Structure

```
tests/
├── __init__.py
├── test_message.py          # Tests for Message and Conversation models
├── test_chat_manager.py     # Tests for ChatManager business logic
├── test_ollama_client.py    # Tests for Ollama API client (with mocks)
└── test_settings.py         # Tests for configuration settings
```

### What's Tested

#### Message & Conversation (`test_message.py`)
- Message creation and serialization
- Conversation management
- Message history tracking
- API format conversion

#### ChatManager (`test_chat_manager.py`)
- Conversation lifecycle management
- Message sending and receiving
- Streaming response handling
- Model switching
- Multi-turn conversations
- Error handling

#### OllamaClient (`test_ollama_client.py`)
- API connection testing
- Model listing
- Streaming generation
- Request payload formatting
- Error handling and retries
- Invalid JSON handling

#### Settings (`test_settings.py`)
- Default configuration values
- Environment variable loading
- Custom configuration
- Type validation
- Case-insensitive environment variables

### Writing New Tests

When adding new features, follow these guidelines:

1. **Create test file** matching the module name: `test_<module_name>.py`
2. **Use pytest fixtures** for common setup
3. **Mock external dependencies** (API calls, file I/O)
4. **Test edge cases** and error conditions
5. **Maintain coverage** above 80% for core modules

Example test structure:
```python
import pytest
from unittest.mock import Mock

class TestYourFeature:
    @pytest.fixture
    def setup(self):
        # Setup code
        return instance

    def test_basic_functionality(self, setup):
        # Test code
        assert result == expected
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
