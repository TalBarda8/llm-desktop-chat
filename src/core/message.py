"""
Data models for chat messages and conversations
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
import uuid


class Role(Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """
    Represents a single chat message

    Attributes:
        role: Who sent the message (user, assistant, system)
        content: The message text
        timestamp: When the message was created
        id: Unique identifier for the message
    """
    role: Role
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        """Convert message to dictionary format"""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "id": self.id
        }


@dataclass
class Conversation:
    """
    Represents a chat conversation with multiple messages

    Attributes:
        model: The LLM model being used
        conversation_id: Optional ID (generates new UUID if not provided)
        id: Unique conversation identifier (alias for conversation_id)
        messages: List of messages in the conversation
        created_at: When the conversation started
    """
    model: str = "llama2"
    conversation_id: str = None
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Initialize conversation ID if not provided"""
        if self.conversation_id is None:
            self.conversation_id = str(uuid.uuid4())

    @property
    def id(self) -> str:
        """Get conversation ID (alias for conversation_id)"""
        return self.conversation_id

    @id.setter
    def id(self, value: str):
        """Set conversation ID (alias for conversation_id)"""
        self.conversation_id = value

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation"""
        self.messages.append(message)

    def get_messages_for_api(self) -> List[dict]:
        """
        Convert messages to format expected by Ollama API

        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in self.messages
        ]

    def clear(self) -> None:
        """Clear all messages from conversation"""
        self.messages.clear()
