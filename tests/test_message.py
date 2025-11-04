"""
Unit tests for message and conversation models
"""
import pytest
from datetime import datetime
from src.core.message import Message, Role, Conversation


class TestMessage:
    """Test cases for Message class"""

    def test_create_message(self):
        """Test creating a basic message"""
        msg = Message(role=Role.USER, content="Hello")

        assert msg.role == Role.USER
        assert msg.content == "Hello"
        assert isinstance(msg.timestamp, datetime)
        assert msg.id is not None

    def test_message_to_dict(self):
        """Test converting message to dictionary"""
        msg = Message(role=Role.ASSISTANT, content="Hi there")
        msg_dict = msg.to_dict()

        assert msg_dict["role"] == "assistant"
        assert msg_dict["content"] == "Hi there"
        assert "timestamp" in msg_dict
        assert "id" in msg_dict


class TestConversation:
    """Test cases for Conversation class"""

    def test_create_conversation(self):
        """Test creating a new conversation"""
        conv = Conversation(model="llama2")

        assert conv.model == "llama2"
        assert len(conv.messages) == 0
        assert conv.id is not None
        assert isinstance(conv.created_at, datetime)

    def test_add_message(self):
        """Test adding messages to conversation"""
        conv = Conversation(model="llama2")
        msg1 = Message(role=Role.USER, content="Hello")
        msg2 = Message(role=Role.ASSISTANT, content="Hi")

        conv.add_message(msg1)
        conv.add_message(msg2)

        assert len(conv.messages) == 2
        assert conv.messages[0].content == "Hello"
        assert conv.messages[1].content == "Hi"

    def test_get_messages_for_api(self):
        """Test converting messages to API format"""
        conv = Conversation(model="llama2")
        conv.add_message(Message(role=Role.USER, content="Hello"))
        conv.add_message(Message(role=Role.ASSISTANT, content="Hi"))

        api_messages = conv.get_messages_for_api()

        assert len(api_messages) == 2
        assert api_messages[0] == {"role": "user", "content": "Hello"}
        assert api_messages[1] == {"role": "assistant", "content": "Hi"}

    def test_clear_conversation(self):
        """Test clearing conversation messages"""
        conv = Conversation(model="llama2")
        conv.add_message(Message(role=Role.USER, content="Hello"))
        conv.add_message(Message(role=Role.ASSISTANT, content="Hi"))

        assert len(conv.messages) == 2

        conv.clear()

        assert len(conv.messages) == 0


# Run tests with: pytest tests/test_message.py -v
