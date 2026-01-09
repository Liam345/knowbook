"""
Message Service - CRUD operations for message entities within chats.

Educational Note: This service handles individual message persistence
and the message chain building for Claude API calls.

Message Types:
- user: Human messages
- assistant: AI responses (text or tool_use)
- tool_result: Results from tool execution (sent as user role to Claude)

Message Chain Flow:
user -> assistant (may contain tool_use) -> user (tool_result) -> assistant -> ...
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from app.services.chat_service import chat_service


class MessageService:
    """
    Service class for message management within chats.

    Educational Note: Messages are stored within chat files as an array.
    This service provides methods to add, retrieve, and build API message chains.
    """

    def add_user_message(self, project_id: str, chat_id: str, content: str) -> Dict[str, Any]:
        """
        Add a user message to a chat.

        Educational Note: This is called when the user sends a message.
        """
        return self.add_message(project_id, chat_id, "user", content)

    def add_assistant_message(
        self,
        project_id: str,
        chat_id: str,
        content: str,
        model: Optional[str] = None,
        tokens: Optional[Dict[str, int]] = None,
        error: bool = False
    ) -> Dict[str, Any]:
        """
        Add an assistant message to a chat.

        Educational Note: This is called when Claude provides a final text response.
        """
        metadata = {}
        if model:
            metadata["model"] = model
        if tokens:
            metadata["tokens"] = tokens
        if error:
            metadata["error"] = True

        return self.add_message(project_id, chat_id, "assistant", content, metadata)

    def add_tool_result_message(
        self,
        project_id: str,
        chat_id: str,
        tool_use_id: str,
        result: str
    ) -> Dict[str, Any]:
        """
        Add a tool result message to a chat.

        Educational Note: Tool results are sent back to Claude as user messages
        with special tool_result content structure.
        """
        content = [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": result
            }
        ]
        return self.add_message(project_id, chat_id, "user", content)

    def add_message(
        self,
        project_id: str,
        chat_id: str,
        role: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to a chat.

        Args:
            project_id: Project UUID
            chat_id: Chat UUID
            role: Message role (user, assistant)
            content: Message content (string or structured for tool_result)
            metadata: Optional metadata (model, tokens, etc.)

        Returns:
            The created message object
        """
        chat = chat_service.get_chat(project_id, chat_id)
        if not chat:
            raise ValueError(f"Chat {chat_id} not found")

        now = datetime.now().isoformat()
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": now,
            **(metadata or {})
        }

        # Add message to chat
        if "messages" not in chat:
            chat["messages"] = []
        chat["messages"].append(message)

        # Update chat metadata
        chat["message_count"] = len(chat["messages"])
        chat["last_message_at"] = now
        chat["updated_at"] = now

        # Save chat
        chat_service._save_chat(project_id, chat)

        return message

    def get_messages(self, project_id: str, chat_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for a chat.

        Returns:
            List of message objects in chronological order
        """
        chat = chat_service.get_chat(project_id, chat_id)
        if not chat:
            return []

        return chat.get("messages", [])

    def build_api_messages(self, project_id: str, chat_id: str) -> List[Dict[str, Any]]:
        """
        Build message chain for Claude API calls.

        Educational Note: Converts our internal message format to Claude API format.
        Filters out metadata and ensures proper role sequence.

        Returns:
            List of messages in Claude API format: [{"role": "user|assistant", "content": "..."}]
        """
        messages = self.get_messages(project_id, chat_id)
        api_messages = []

        for msg in messages:
            # Convert to Claude API format
            api_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            api_messages.append(api_msg)

        return api_messages


# Singleton instance
message_service = MessageService()