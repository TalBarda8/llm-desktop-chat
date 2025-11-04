"""
Chat manager - orchestrates conversation state and API communication
"""
from typing import List, Callable, Optional
from .message import Message, Role, Conversation
from ..api.ollama_client import OllamaClient
from ..utils.logger import setup_logger

logger = setup_logger("chat_manager", "logs/app.log")


class ChatManager:
    """
    Manages conversation state and orchestrates API calls

    This class serves as the business logic layer between the GUI
    and the Ollama API. It maintains conversation state and handles
    message sending/receiving.
    """

    def __init__(self, ollama_client: OllamaClient):
        """
        Initialize the chat manager

        Args:
            ollama_client: Instance of OllamaClient for API communication
        """
        self.client = ollama_client
        self.current_conversation: Optional[Conversation] = None
        self.current_model: str = "llama2"
        logger.info("Chat manager initialized")

    def start_new_conversation(self, model: str = None) -> None:
        """
        Start a new conversation, clearing any existing messages

        Args:
            model: Model to use (optional, uses current model if not specified)
        """
        if model:
            self.current_model = model

        self.current_conversation = Conversation(model=self.current_model)
        logger.info(f"Started new conversation with model: {self.current_model}")

    def send_message(self, content: str, on_chunk: Callable[[str], None]) -> None:
        """
        Send a user message and stream the AI response

        This method:
        1. Adds the user message to conversation
        2. Sends conversation to Ollama API
        3. Streams response chunks via callback
        4. Adds complete assistant response to conversation

        Args:
            content: User's message text
            on_chunk: Callback function called for each response chunk
                      Should accept a single string argument

        Raises:
            ValueError: If no conversation exists
        """
        if not self.current_conversation:
            logger.warning("No active conversation, creating new one")
            self.start_new_conversation()

        # Create and add user message
        user_message = Message(role=Role.USER, content=content)
        self.current_conversation.add_message(user_message)
        logger.info(f"User message added: {content[:50]}...")

        # Get messages in API format
        api_messages = self.current_conversation.get_messages_for_api()

        # Stream response from API
        logger.info("Starting streaming response from API")
        full_response = ""

        try:
            for chunk in self.client.generate_stream(self.current_model, api_messages):
                full_response += chunk
                on_chunk(chunk)  # Call callback with each chunk

            # Add complete assistant response to conversation
            assistant_message = Message(role=Role.ASSISTANT, content=full_response)
            self.current_conversation.add_message(assistant_message)
            logger.info(f"Assistant response completed: {len(full_response)} chars")

        except Exception as e:
            logger.error(f"Error during message sending: {e}")
            raise

    def set_model(self, model_name: str) -> None:
        """
        Change the active model

        Args:
            model_name: Name of the model to use
        """
        self.current_model = model_name
        if self.current_conversation:
            self.current_conversation.model = model_name
        logger.info(f"Model changed to: {model_name}")

    def get_messages(self) -> List[Message]:
        """
        Get all messages from current conversation

        Returns:
            List of Message objects
        """
        if not self.current_conversation:
            return []
        return self.current_conversation.messages

    def clear_conversation(self) -> None:
        """Clear all messages from current conversation"""
        if self.current_conversation:
            self.current_conversation.clear()
            logger.info("Conversation cleared")
