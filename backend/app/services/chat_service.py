"""
Chat Service - CRUD operations for chat entities.

Educational Note: This service manages chat entity lifecycle within projects.
It handles creating, listing, getting, updating, and deleting chats.

Separation of Concerns:
- chat_service.py: Chat CRUD (this file)
- claude_service.py: Claude API interactions
- message_service.py: Message persistence
- main_chat_service.py: Chat orchestration with AI
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

from config import Config


class ChatService:
    """
    Service class for chat entity management.

    Educational Note: A chat is a conversation container within a project.
    It has metadata (title, timestamps) and holds messages.
    """

    def __init__(self):
        """Initialize the chat service."""
        self.projects_dir = Path(Config.PROJECTS_DIR)

    def _get_chats_dir(self, project_id: str) -> Path:
        """Get the chats directory for a project."""
        chats_dir = self.projects_dir / project_id / "chats"
        chats_dir.mkdir(exist_ok=True, parents=True)
        return chats_dir

    def _get_index_file(self, project_id: str) -> Path:
        """Get the chats index file path."""
        return self._get_chats_dir(project_id) / "chats_index.json"

    def _get_chat_file(self, project_id: str, chat_id: str) -> Path:
        """Get a specific chat's file path."""
        return self._get_chats_dir(project_id) / f"{chat_id}.json"

    def _load_index(self, project_id: str) -> Dict[str, Any]:
        """
        Load the chats index for a project.

        Educational Note: The index provides quick access to chat metadata
        without loading full chat files with all messages.
        """
        index_file = self._get_index_file(project_id)

        if not index_file.exists():
            # Initialize empty index
            initial_index = {
                "project_id": project_id,
                "chats": [],
                "last_updated": datetime.now().isoformat()
            }
            self._save_index(project_id, initial_index)
            return initial_index

        try:
            with open(index_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Reinitialize if corrupted
            initial_index = {
                "project_id": project_id,
                "chats": [],
                "last_updated": datetime.now().isoformat()
            }
            self._save_index(project_id, initial_index)
            return initial_index

    def _save_index(self, project_id: str, index_data: Dict[str, Any]) -> bool:
        """Save the chats index."""
        try:
            index_file = self._get_index_file(project_id)
            index_data["last_updated"] = datetime.now().isoformat()
            
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            return True
        except Exception:
            return False

    def _load_chat(self, project_id: str, chat_id: str) -> Optional[Dict[str, Any]]:
        """Load a specific chat from its file."""
        chat_file = self._get_chat_file(project_id, chat_id)
        
        if not chat_file.exists():
            return None

        try:
            with open(chat_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    def _save_chat(self, project_id: str, chat_data: Dict[str, Any]) -> bool:
        """Save a chat to its file."""
        try:
            chat_file = self._get_chat_file(project_id, chat_data["id"])
            chat_data["updated_at"] = datetime.now().isoformat()
            
            with open(chat_file, 'w') as f:
                json.dump(chat_data, f, indent=2)
            return True
        except Exception:
            return False

    def list_chats(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all chats for a project.

        Returns only metadata, not full message content.
        """
        index = self._load_index(project_id)
        return index.get("chats", [])

    def create_chat(self, project_id: str, title: str = "New Chat") -> Dict[str, Any]:
        """
        Create a new chat in a project.

        Educational Note: Creates both the chat file and updates the index.
        """
        now = datetime.now().isoformat()
        chat_id = str(uuid.uuid4())

        # Create chat data
        chat = {
            "id": chat_id,
            "project_id": project_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "last_message_at": None,
            "message_count": 0,
            "messages": [],
            "studio_signals": []  # For future studio integration
        }

        # Save chat file
        self._save_chat(project_id, chat)

        # Update index with chat metadata
        index = self._load_index(project_id)
        chat_metadata = {
            "id": chat_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "last_message_at": None,
            "message_count": 0
        }
        index["chats"].append(chat_metadata)
        self._save_index(project_id, index)

        return chat

    def get_chat(self, project_id: str, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific chat with all its messages.

        Educational Note: Loads the complete conversation history.
        """
        return self._load_chat(project_id, chat_id)

    def update_chat(self, project_id: str, chat_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a chat's metadata.

        Educational Note: Currently supports updating title.
        """
        chat = self._load_chat(project_id, chat_id)
        if not chat:
            return None

        # Apply updates
        if "title" in updates:
            chat["title"] = updates["title"]

        # Save updated chat
        self._save_chat(project_id, chat)

        # Update index
        index = self._load_index(project_id)
        for chat_meta in index["chats"]:
            if chat_meta["id"] == chat_id:
                if "title" in updates:
                    chat_meta["title"] = updates["title"]
                chat_meta["updated_at"] = chat["updated_at"]
                break
        self._save_index(project_id, index)

        return chat

    def delete_chat(self, project_id: str, chat_id: str) -> bool:
        """
        Delete a chat and all its messages.

        Educational Note: This is a hard delete. Removes both the chat file
        and updates the index.
        """
        chat_file = self._get_chat_file(project_id, chat_id)
        
        # Remove chat file
        if chat_file.exists():
            try:
                chat_file.unlink()
            except Exception:
                return False

        # Update index
        index = self._load_index(project_id)
        index["chats"] = [chat for chat in index["chats"] if chat["id"] != chat_id]
        return self._save_index(project_id, index)

    def sync_chat_to_index(self, project_id: str, chat_id: str) -> bool:
        """
        Sync a chat's current state to the index.

        Educational Note: Called after messages are added to update
        metadata like message_count and last_message_at in the index.
        """
        chat = self._load_chat(project_id, chat_id)
        if not chat:
            return False

        index = self._load_index(project_id)
        for chat_meta in index["chats"]:
            if chat_meta["id"] == chat_id:
                chat_meta["message_count"] = chat.get("message_count", 0)
                chat_meta["last_message_at"] = chat.get("last_message_at")
                chat_meta["updated_at"] = chat.get("updated_at", datetime.now().isoformat())
                break

        return self._save_index(project_id, index)


# Singleton instance
chat_service = ChatService()