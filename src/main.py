"""
Main entry point for the Local LLM Desktop Chat Application

This application provides a desktop GUI for chatting with local LLM models
via the Ollama API. It features a simple, clean interface for sending messages
and receiving streaming responses.

Usage:
    python -m src.main

Requirements:
    - Ollama must be installed and running locally
    - At least one model must be pulled (e.g., ollama pull llama2)
"""
import sys
from tkinter import messagebox
from .gui.app import ChatApplication
from .core.chat_manager import ChatManager
from .api.ollama_client import OllamaClient
from .config.settings import settings
from .utils.logger import setup_logger
from .utils.exceptions import OllamaConnectionError


def main():
    """Application entry point"""

    # Setup logging
    logger = setup_logger("main", settings.log_file, settings.log_level)
    logger.info("=" * 60)
    logger.info("Starting Local LLM Desktop Chat Application")
    logger.info("=" * 60)

    try:
        # Initialize Ollama API client
        logger.info(f"Connecting to Ollama at {settings.ollama_base_url}")
        ollama_client = OllamaClient(base_url=settings.ollama_base_url)

        # Verify Ollama connection
        if not ollama_client.check_connection():
            error_msg = (
                "Cannot connect to Ollama API.\n\n"
                "Please ensure:\n"
                "1. Ollama is installed\n"
                "2. Ollama is running (try: ollama serve)\n"
                f"3. API is accessible at {settings.ollama_base_url}"
            )
            logger.error("Ollama connection failed")
            messagebox.showerror("Connection Error", error_msg)
            sys.exit(1)

        logger.info("Successfully connected to Ollama")

        # Check if any models are available
        try:
            models = ollama_client.list_models()
            if not models:
                warning_msg = (
                    "No models found in Ollama.\n\n"
                    "Please pull a model first:\n"
                    "  ollama pull llama2\n"
                    "  ollama pull mistral\n\n"
                    "You can continue, but won't be able to chat until a model is available."
                )
                logger.warning("No models found")
                messagebox.showwarning("No Models", warning_msg)
        except Exception as e:
            logger.warning(f"Could not check models: {e}")

        # Initialize chat manager
        logger.info("Initializing chat manager")
        chat_manager = ChatManager(ollama_client)
        chat_manager.set_model(settings.default_model)

        # Launch GUI application
        logger.info("Launching GUI")
        app = ChatApplication(chat_manager)
        app.run()

    except OllamaConnectionError as e:
        logger.error(f"Ollama connection error: {e}")
        messagebox.showerror("Connection Error", str(e))
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
        sys.exit(1)

    finally:
        # Cleanup
        if 'ollama_client' in locals():
            ollama_client.close()
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()
