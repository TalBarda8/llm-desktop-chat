"""
Unit tests for ConversationStorage
"""
import pytest
import json
import os
from pathlib import Path
from datetime import datetime
from src.storage.conversation_storage import ConversationStorage
from src.core.message import Conversation, Message, Role


class TestConversationStorage:
    """Test suite for ConversationStorage class"""

    @pytest.fixture
    def temp_storage_dir(self, tmp_path):
        """Create a temporary storage directory"""
        storage_dir = tmp_path / "test_conversations"
        return str(storage_dir)

    @pytest.fixture
    def storage(self, temp_storage_dir):
        """Create ConversationStorage instance with temp directory"""
        return ConversationStorage(temp_storage_dir)

    @pytest.fixture
    def sample_conversation(self):
        """Create a sample conversation for testing"""
        conv = Conversation(model="llama2")
        conv.add_message(Message(role=Role.USER, content="Hello"))
        conv.add_message(Message(role=Role.ASSISTANT, content="Hi there!"))
        return conv

    def test_initialization(self, temp_storage_dir):
        """Test storage initialization creates directory"""
        storage = ConversationStorage(temp_storage_dir)
        assert storage.storage_dir.exists()
        assert storage.storage_dir.is_dir()

    def test_save_conversation(self, storage, sample_conversation):
        """Test saving a conversation to disk"""
        storage.save_conversation(sample_conversation)

        # Check file exists
        file_path = storage.storage_dir / f"{sample_conversation.id}.json"
        assert file_path.exists()

        # Check file content
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data['id'] == sample_conversation.id
        assert data['model'] == "llama2"
        assert len(data['messages']) == 2
        assert data['messages'][0]['content'] == "Hello"
        assert data['messages'][1]['content'] == "Hi there!"

    def test_save_conversation_generates_title(self, storage, sample_conversation):
        """Test that saving generates a title from first user message"""
        storage.save_conversation(sample_conversation)

        file_path = storage.storage_dir / f"{sample_conversation.id}.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data['title'] == "Hello"

    def test_save_conversation_truncates_long_title(self, storage):
        """Test that long titles are truncated to 50 chars"""
        conv = Conversation(model="llama2")
        long_message = "This is a very long message that exceeds fifty characters and should be truncated"
        conv.add_message(Message(role=Role.USER, content=long_message))

        storage.save_conversation(conv)

        file_path = storage.storage_dir / f"{conv.id}.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data['title']) == 53  # 50 chars + "..."
        assert data['title'].endswith("...")

    def test_load_conversation(self, storage, sample_conversation):
        """Test loading a conversation from disk"""
        # Save first
        storage.save_conversation(sample_conversation)

        # Load
        loaded_conv = storage.load_conversation(sample_conversation.id)

        assert loaded_conv is not None
        assert loaded_conv.id == sample_conversation.id
        assert loaded_conv.model == "llama2"
        assert len(loaded_conv.messages) == 2
        assert loaded_conv.messages[0].content == "Hello"
        assert loaded_conv.messages[1].content == "Hi there!"

    def test_load_nonexistent_conversation(self, storage):
        """Test loading a conversation that doesn't exist"""
        result = storage.load_conversation("nonexistent-id")
        assert result is None

    def test_list_conversations(self, storage):
        """Test listing all conversations"""
        # Create and save multiple conversations
        conv1 = Conversation(model="llama2")
        conv1.add_message(Message(role=Role.USER, content="First conversation"))
        storage.save_conversation(conv1)

        conv2 = Conversation(model="mistral")
        conv2.add_message(Message(role=Role.USER, content="Second conversation"))
        storage.save_conversation(conv2)

        # List conversations
        conversations = storage.list_conversations()

        assert len(conversations) == 2
        assert all('id' in conv for conv in conversations)
        assert all('title' in conv for conv in conversations)
        assert all('model' in conv for conv in conversations)
        assert all('message_count' in conv for conv in conversations)

    def test_list_conversations_sorted_by_updated_at(self, storage, sample_conversation):
        """Test that conversations are sorted by updated_at (most recent first)"""
        import time

        # Save first conversation
        storage.save_conversation(sample_conversation)

        # Wait a bit
        time.sleep(0.1)

        # Create and save second conversation
        conv2 = Conversation(model="mistral")
        conv2.add_message(Message(role=Role.USER, content="Newer conversation"))
        storage.save_conversation(conv2)

        # List conversations
        conversations = storage.list_conversations()

        # Second conversation should be first (most recent)
        assert conversations[0]['id'] == conv2.id
        assert conversations[1]['id'] == sample_conversation.id

    def test_delete_conversation(self, storage, sample_conversation):
        """Test deleting a conversation"""
        # Save first
        storage.save_conversation(sample_conversation)

        # Verify it exists
        file_path = storage.storage_dir / f"{sample_conversation.id}.json"
        assert file_path.exists()

        # Delete
        result = storage.delete_conversation(sample_conversation.id)
        assert result is True
        assert not file_path.exists()

    def test_delete_nonexistent_conversation(self, storage):
        """Test deleting a conversation that doesn't exist"""
        result = storage.delete_conversation("nonexistent-id")
        assert result is False

    def test_conversation_exists(self, storage, sample_conversation):
        """Test checking if a conversation exists"""
        # Should not exist initially
        assert not storage.conversation_exists(sample_conversation.id)

        # Save conversation
        storage.save_conversation(sample_conversation)

        # Should exist now
        assert storage.conversation_exists(sample_conversation.id)

    def test_generate_title_no_user_messages(self, storage):
        """Test title generation when there are no user messages"""
        conv = Conversation(model="llama2")
        conv.add_message(Message(role=Role.ASSISTANT, content="Only assistant message"))

        storage.save_conversation(conv)

        file_path = storage.storage_dir / f"{conv.id}.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Should fallback to timestamp-based title
        assert "Chat" in data['title']
        assert data['title'] != "Only assistant message"

    def test_save_updates_existing_conversation(self, storage, sample_conversation):
        """Test that saving an existing conversation updates it"""
        # Save initially
        storage.save_conversation(sample_conversation)

        # Add another message
        sample_conversation.add_message(Message(role=Role.USER, content="Another message"))

        # Save again
        storage.save_conversation(sample_conversation)

        # Load and verify
        loaded_conv = storage.load_conversation(sample_conversation.id)
        assert len(loaded_conv.messages) == 3
        assert loaded_conv.messages[2].content == "Another message"

    def test_conversation_metadata_includes_timestamps(self, storage, sample_conversation):
        """Test that saved conversations include created_at and updated_at"""
        storage.save_conversation(sample_conversation)

        file_path = storage.storage_dir / f"{sample_conversation.id}.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert 'created_at' in data
        assert 'updated_at' in data

        # Verify they are valid ISO format timestamps
        datetime.fromisoformat(data['created_at'])
        datetime.fromisoformat(data['updated_at'])

    def test_message_preservation(self, storage, sample_conversation):
        """Test that message IDs and timestamps are preserved"""
        original_msg_ids = [msg.id for msg in sample_conversation.messages]
        original_timestamps = [msg.timestamp for msg in sample_conversation.messages]

        storage.save_conversation(sample_conversation)
        loaded_conv = storage.load_conversation(sample_conversation.id)

        loaded_msg_ids = [msg.id for msg in loaded_conv.messages]
        loaded_timestamps = [msg.timestamp for msg in loaded_conv.messages]

        assert original_msg_ids == loaded_msg_ids
        assert original_timestamps == loaded_timestamps
