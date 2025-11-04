"""
Custom exceptions for the application
"""


class OllamaConnectionError(Exception):
    """Raised when cannot connect to Ollama API"""
    pass


class ModelNotFoundError(Exception):
    """Raised when requested model is not available"""
    pass


class ChatError(Exception):
    """Base exception for chat-related errors"""
    pass
