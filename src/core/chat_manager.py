"""
Chat manager - orchestrates conversation state and API communication
"""
from typing import List, Callable, Optional, Dict
from .message import Message, Role, Conversation
from ..api.ollama_client import OllamaClient
from ..storage.conversation_storage import ConversationStorage
from ..utils.logger import setup_logger

logger = setup_logger("chat_manager", "logs/app.log")


class ChatManager:
    """
    Manages conversation state and orchestrates API calls

    This class serves as the business logic layer between the GUI
    and the Ollama API. It maintains conversation state and handles
    message sending/receiving.
    """

    def __init__(self, ollama_client: OllamaClient, storage_dir: str = "conversations"):
        """
        Initialize the chat manager

        Args:
            ollama_client: Instance of OllamaClient for API communication
            storage_dir: Directory to store conversation files
        """
        self.client = ollama_client
        self.storage = ConversationStorage(storage_dir)
        self.current_conversation: Optional[Conversation] = None
        self.current_model: str = "llama2"
        logger.info("Chat manager initialized with conversation storage")

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

            # Auto-save conversation after each message exchange
            self.storage.save_conversation(self.current_conversation)
            logger.info(f"Conversation auto-saved: {self.current_conversation.id}")

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

    def load_conversation(self, conversation_id: str) -> bool:
        """
        Load a conversation from storage and make it the current conversation

        Args:
            conversation_id: ID of conversation to load

        Returns:
            True if loaded successfully, False otherwise
        """
        conversation = self.storage.load_conversation(conversation_id)
        if conversation:
            self.current_conversation = conversation
            self.current_model = conversation.model
            logger.info(f"Loaded conversation: {conversation_id}")
            return True
        else:
            logger.warning(f"Failed to load conversation: {conversation_id}")
            return False

    def switch_conversation(self, conversation_id: str) -> bool:
        """
        Switch to a different conversation

        This is an alias for load_conversation for clarity in UI code

        Args:
            conversation_id: ID of conversation to switch to

        Returns:
            True if switched successfully, False otherwise
        """
        return self.load_conversation(conversation_id)

    def get_conversation_list(self) -> List[Dict[str, str]]:
        """
        Get list of all saved conversations with metadata

        Returns:
            List of conversation metadata dictionaries
        """
        return self.storage.list_conversations()

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation from storage

        Args:
            conversation_id: ID of conversation to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        success = self.storage.delete_conversation(conversation_id)
        if success:
            # If we deleted the current conversation, clear it
            if self.current_conversation and self.current_conversation.id == conversation_id:
                self.current_conversation = None
                logger.info("Deleted current conversation, cleared active conversation")
        return success

    def get_current_conversation_id(self) -> Optional[str]:
        """
        Get the ID of the current conversation

        Returns:
            Conversation ID or None if no active conversation
        """
        if self.current_conversation:
            return self.current_conversation.id
        return None
