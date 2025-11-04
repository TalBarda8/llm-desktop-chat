"""
Conversation storage - handles persistence of conversations to disk
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from ..core.message import Conversation, Message, Role
from ..utils.logger import setup_logger

logger = setup_logger("storage", "logs/app.log")


class ConversationStorage:
    """
    Manages conversation persistence to disk using JSON files

    Each conversation is stored as a separate JSON file in the
    conversations directory with metadata (title, timestamp, model)
    """

    def __init__(self, storage_dir: str = "conversations"):
        """
        Initialize conversation storage

        Args:
            storage_dir: Directory to store conversation files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        logger.info(f"Initialized conversation storage at: {self.storage_dir}")

    def save_conversation(self, conversation: Conversation) -> None:
        """
        Save a conversation to disk

        Args:
            conversation: Conversation object to save
        """
        try:
            file_path = self.storage_dir / f"{conversation.id}.json"

            # Generate title from first user message if not set
            title = self._generate_title(conversation)

            # Prepare conversation data
            data = {
                "id": conversation.id,
                "title": title,
                "model": conversation.model,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": datetime.now().isoformat(),
                "messages": [
                    {
                        "id": msg.id,
                        "role": msg.role.value,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in conversation.messages
                ]
            }

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved conversation: {conversation.id} - {title}")

        except Exception as e:
            logger.error(f"Failed to save conversation {conversation.id}: {e}")
            raise

    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Load a conversation from disk

        Args:
            conversation_id: ID of the conversation to load

        Returns:
            Conversation object or None if not found
        """
        try:
            file_path = self.storage_dir / f"{conversation_id}.json"

            if not file_path.exists():
                logger.warning(f"Conversation file not found: {conversation_id}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Reconstruct conversation
            conversation = Conversation(
                model=data["model"],
                conversation_id=data["id"]
            )
            conversation.created_at = datetime.fromisoformat(data["created_at"])

            # Reconstruct messages
            for msg_data in data["messages"]:
                message = Message(
                    role=Role(msg_data["role"]),
                    content=msg_data["content"]
                )
                message.id = msg_data["id"]
                message.timestamp = datetime.fromisoformat(msg_data["timestamp"])
                conversation.messages.append(message)

            logger.info(f"Loaded conversation: {conversation_id}")
            return conversation

        except Exception as e:
            logger.error(f"Failed to load conversation {conversation_id}: {e}")
            return None

    def list_conversations(self) -> List[Dict[str, str]]:
        """
        List all saved conversations with metadata

        Returns:
            List of conversation metadata dictionaries containing:
            - id: conversation ID
            - title: conversation title
            - model: model used
            - created_at: creation timestamp
            - updated_at: last update timestamp
            - message_count: number of messages
        """
        conversations = []

        try:
            for file_path in self.storage_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    conversations.append({
                        "id": data["id"],
                        "title": data.get("title", "Untitled Conversation"),
                        "model": data["model"],
                        "created_at": data["created_at"],
                        "updated_at": data.get("updated_at", data["created_at"]),
                        "message_count": len(data.get("messages", []))
                    })

                except Exception as e:
                    logger.warning(f"Failed to read conversation file {file_path}: {e}")
                    continue

            # Sort by updated_at (most recent first)
            conversations.sort(key=lambda x: x["updated_at"], reverse=True)

            logger.info(f"Listed {len(conversations)} conversations")
            return conversations

        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return []

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation from disk

        Args:
            conversation_id: ID of conversation to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            file_path = self.storage_dir / f"{conversation_id}.json"

            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted conversation: {conversation_id}")
                return True
            else:
                logger.warning(f"Conversation not found for deletion: {conversation_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            return False

    def _generate_title(self, conversation: Conversation) -> str:
        """
        Generate a title for the conversation from first user message

        Args:
            conversation: Conversation object

        Returns:
            Generated title string
        """
        # Find first user message
        for msg in conversation.messages:
            if msg.role == Role.USER:
                # Take first 50 characters
                title = msg.content[:50].strip()
                # Remove newlines
                title = title.replace('\n', ' ')
                # Add ellipsis if truncated
                if len(msg.content) > 50:
                    title += "..."
                return title

        # Fallback to timestamp-based title
        return f"Chat {conversation.created_at.strftime('%Y-%m-%d %H:%M')}"

    def conversation_exists(self, conversation_id: str) -> bool:
        """
        Check if a conversation file exists

        Args:
            conversation_id: ID of conversation to check

        Returns:
            True if exists, False otherwise
        """
        file_path = self.storage_dir / f"{conversation_id}.json"
        return file_path.exists()
