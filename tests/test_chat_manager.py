"""
Unit tests for ChatManager class
"""
import pytest
from unittest.mock import Mock
from src.core.chat_manager import ChatManager
from src.core.message import Message, Role, Conversation
from src.api.ollama_client import OllamaClient


class TestChatManager:
    """Test cases for ChatManager class"""

    @pytest.fixture
    def mock_ollama_client(self):
        """Create a mock OllamaClient for testing"""
        client = Mock(spec=OllamaClient)
        return client

    @pytest.fixture
    def chat_manager(self, mock_ollama_client):
        """Create a ChatManager instance with mock client"""
        return ChatManager(mock_ollama_client)

    def test_initialization(self, chat_manager, mock_ollama_client):
        """Test ChatManager initializes correctly"""
        assert chat_manager.client == mock_ollama_client
        assert chat_manager.current_conversation is None
        assert chat_manager.current_model == "llama2"

    def test_start_new_conversation_default_model(self, chat_manager):
        """Test starting a new conversation with default model"""
        chat_manager.start_new_conversation()

        assert chat_manager.current_conversation is not None
        assert isinstance(chat_manager.current_conversation, Conversation)
        assert chat_manager.current_conversation.model == "llama2"
        assert len(chat_manager.current_conversation.messages) == 0

    def test_start_new_conversation_custom_model(self, chat_manager):
        """Test starting a new conversation with custom model"""
        chat_manager.start_new_conversation(model="mistral")

        assert chat_manager.current_conversation is not None
        assert chat_manager.current_conversation.model == "mistral"
        assert chat_manager.current_model == "mistral"

    def test_send_message_creates_conversation_if_none(self, chat_manager, mock_ollama_client):
        """Test send_message creates conversation if none exists"""
        mock_ollama_client.generate_stream.return_value = iter(["Hello", " there", "!"])
        chunks_received = []

        def on_chunk(chunk):
            chunks_received.append(chunk)

        chat_manager.send_message("Hi", on_chunk)

        assert chat_manager.current_conversation is not None
        assert len(chat_manager.current_conversation.messages) == 2  # user + assistant

    def test_send_message_adds_user_message(self, chat_manager, mock_ollama_client):
        """Test send_message adds user message to conversation"""
        mock_ollama_client.generate_stream.return_value = iter(["Response"])
        chat_manager.start_new_conversation()

        chat_manager.send_message("Hello", lambda x: None)

        messages = chat_manager.current_conversation.messages
        assert len(messages) == 2
        assert messages[0].role == Role.USER
        assert messages[0].content == "Hello"

    def test_send_message_streams_response(self, chat_manager, mock_ollama_client):
        """Test send_message streams response chunks"""
        mock_ollama_client.generate_stream.return_value = iter(["Hello", " ", "World"])
        chat_manager.start_new_conversation()

        chunks_received = []
        chat_manager.send_message("Hi", lambda chunk: chunks_received.append(chunk))

        assert chunks_received == ["Hello", " ", "World"]

    def test_send_message_adds_assistant_response(self, chat_manager, mock_ollama_client):
        """Test send_message adds complete assistant response"""
        mock_ollama_client.generate_stream.return_value = iter(["Hello", " ", "World"])
        chat_manager.start_new_conversation()

        chat_manager.send_message("Hi", lambda x: None)

        messages = chat_manager.current_conversation.messages
        assert len(messages) == 2
        assert messages[1].role == Role.ASSISTANT
        assert messages[1].content == "Hello World"

    def test_send_message_calls_ollama_with_correct_params(self, chat_manager, mock_ollama_client):
        """Test send_message calls OllamaClient with correct parameters"""
        mock_ollama_client.generate_stream.return_value = iter(["Response"])
        chat_manager.start_new_conversation()
        chat_manager.send_message("Test message", lambda x: None)

        mock_ollama_client.generate_stream.assert_called_once()
        call_args = mock_ollama_client.generate_stream.call_args

        assert call_args[0][0] == "llama2"  # model
        assert len(call_args[0][1]) == 1  # messages list
        assert call_args[0][1][0]["role"] == "user"
        assert call_args[0][1][0]["content"] == "Test message"

    def test_send_message_handles_exception(self, chat_manager, mock_ollama_client):
        """Test send_message propagates exceptions"""
        mock_ollama_client.generate_stream.side_effect = Exception("API Error")
        chat_manager.start_new_conversation()

        with pytest.raises(Exception, match="API Error"):
            chat_manager.send_message("Hi", lambda x: None)

    def test_set_model(self, chat_manager):
        """Test setting a new model"""
        chat_manager.set_model("mistral")
        assert chat_manager.current_model == "mistral"

    def test_set_model_updates_conversation(self, chat_manager):
        """Test setting model updates current conversation"""
        chat_manager.start_new_conversation()
        chat_manager.set_model("codellama")

        assert chat_manager.current_model == "codellama"
        assert chat_manager.current_conversation.model == "codellama"

    def test_get_messages_no_conversation(self, chat_manager):
        """Test get_messages returns empty list when no conversation"""
        messages = chat_manager.get_messages()
        assert messages == []

    def test_get_messages_with_conversation(self, chat_manager, mock_ollama_client):
        """Test get_messages returns messages from conversation"""
        mock_ollama_client.generate_stream.return_value = iter(["Response"])
        chat_manager.start_new_conversation()
        chat_manager.send_message("Hello", lambda x: None)

        messages = chat_manager.get_messages()
        assert len(messages) == 2
        assert all(isinstance(msg, Message) for msg in messages)

    def test_clear_conversation(self, chat_manager, mock_ollama_client):
        """Test clearing conversation removes all messages"""
        mock_ollama_client.generate_stream.return_value = iter(["Response"])
        chat_manager.start_new_conversation()
        chat_manager.send_message("Hello", lambda x: None)

        assert len(chat_manager.current_conversation.messages) == 2

        chat_manager.clear_conversation()
        assert len(chat_manager.current_conversation.messages) == 0

    def test_clear_conversation_no_conversation(self, chat_manager):
        """Test clearing when no conversation exists doesn't raise error"""
        chat_manager.clear_conversation()  # Should not raise exception

    def test_multi_turn_conversation(self, chat_manager, mock_ollama_client):
        """Test multiple message exchanges in same conversation"""
        mock_ollama_client.generate_stream.side_effect = [
            iter(["Response 1"]),
            iter(["Response 2"]),
            iter(["Response 3"])
        ]

        chat_manager.start_new_conversation()
        chat_manager.send_message("Message 1", lambda x: None)
        chat_manager.send_message("Message 2", lambda x: None)
        chat_manager.send_message("Message 3", lambda x: None)

        messages = chat_manager.get_messages()
        assert len(messages) == 6  # 3 user + 3 assistant
        assert messages[0].content == "Message 1"
        assert messages[1].content == "Response 1"
        assert messages[2].content == "Message 2"
        assert messages[3].content == "Response 2"


# Run tests with: pytest tests/test_chat_manager.py -v
