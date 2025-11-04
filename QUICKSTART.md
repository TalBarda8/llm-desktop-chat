# Quick Start Guide

## Get Up and Running in 2 Steps

### Step 1: Start Ollama (if not already running)

```bash
ollama serve
```

In another terminal, pull a model:

```bash
ollama pull llama2
```

### Step 2: Run the Application

**Option A - Use the startup script (Easiest):**

```bash
./start.sh
```

**Option B - Manual activation:**

```bash
source venv/bin/activate
python run.py
```

**Note:** Dependencies are already installed in the `venv/` virtual environment!

## That's It!

The application window will open. Select your model from the dropdown and start chatting!

## Common Issues

**"Cannot connect to Ollama"**
- Make sure Ollama is running: `ollama serve`

**"No models found"**
- Pull a model first: `ollama pull llama2`

**Import errors**
- Install dependencies: `pip install -r requirements.txt`

For more details, see the full [README.md](README.md)
