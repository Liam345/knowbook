"""
Memory Service for KnowBook.

Handles user and project memory storage and retrieval.
- User memory: Global across all projects
- Project memory: Specific to one project, deleted with project

Uses AI (Haiku) to intelligently merge new memories with existing.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from app.services.claude_service import claude_service


class MemoryService:
    """
    Service for managing user and project memory.

    Memory is stored as plain text and intelligently merged
    using Haiku when new information is added.
    """

    # Maximum memory length (tokens)
    MAX_MEMORY_TOKENS = 150

    def __init__(self):
        """Initialize the memory service."""
        self.data_dir = Path(__file__).parent.parent / 'data'

    def get_user_memory(self) -> Optional[str]:
        """
        Get the global user memory.

        Returns:
            User memory text or None if not set
        """
        memory_path = self.data_dir / 'user_memory.json'
        if not memory_path.exists():
            return None

        try:
            with open(memory_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('memory')
        except (json.JSONDecodeError, IOError):
            return None

    def get_project_memory(self, project_id: str) -> Optional[str]:
        """
        Get memory for a specific project.

        Args:
            project_id: Project UUID

        Returns:
            Project memory text or None if not set
        """
        memory_path = self.data_dir / 'projects' / project_id / 'memory.json'
        if not memory_path.exists():
            return None

        try:
            with open(memory_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('memory')
        except (json.JSONDecodeError, IOError):
            return None

    def update_user_memory(
        self,
        new_memory: str,
        reason: str = ""
    ) -> bool:
        """
        Update the global user memory.

        Uses AI to intelligently merge with existing memory.

        Args:
            new_memory: New information to add
            reason: Why this is being stored

        Returns:
            True if successful
        """
        return self._update_memory(
            memory_type='user',
            new_memory=new_memory,
            reason=reason,
            project_id=None
        )

    def update_project_memory(
        self,
        project_id: str,
        new_memory: str,
        reason: str = ""
    ) -> bool:
        """
        Update memory for a specific project.

        Uses AI to intelligently merge with existing memory.

        Args:
            project_id: Project UUID
            new_memory: New information to add
            reason: Why this is being stored

        Returns:
            True if successful
        """
        return self._update_memory(
            memory_type='project',
            new_memory=new_memory,
            reason=reason,
            project_id=project_id
        )

    def _update_memory(
        self,
        memory_type: str,
        new_memory: str,
        reason: str,
        project_id: Optional[str]
    ) -> bool:
        """
        Internal method to update memory with AI merge.

        Args:
            memory_type: 'user' or 'project'
            new_memory: New information to add
            reason: Why this is being stored
            project_id: Project UUID (for project memory)

        Returns:
            True if successful
        """
        try:
            # Get current memory
            if memory_type == 'user':
                current_memory = self.get_user_memory() or ""
            else:
                current_memory = self.get_project_memory(project_id) or ""

            # Use AI to merge memories
            merged_memory = self._ai_merge_memory(
                memory_type=memory_type,
                current_memory=current_memory,
                new_memory=new_memory,
                reason=reason
            )

            if not merged_memory:
                # AI merge failed, just append
                if current_memory:
                    merged_memory = f"{current_memory}\n{new_memory}"
                else:
                    merged_memory = new_memory

            # Save merged memory
            return self._save_memory(
                memory_type=memory_type,
                memory=merged_memory,
                project_id=project_id
            )

        except Exception as e:
            print(f"Error updating {memory_type} memory: {e}")
            return False

    def _ai_merge_memory(
        self,
        memory_type: str,
        current_memory: str,
        new_memory: str,
        reason: str
    ) -> Optional[str]:
        """
        Use Haiku to intelligently merge memories.

        Args:
            memory_type: 'user' or 'project'
            current_memory: Existing memory content
            new_memory: New information to add
            reason: Why this is being stored

        Returns:
            Merged memory text or None if merge failed
        """
        if not claude_service.is_configured():
            return None

        try:
            system_prompt = """You are a memory management assistant. Your job is to merge new information with existing memory, keeping the result concise and well-organized.

Rules:
- Keep the merged result under 150 words
- Remove redundant or duplicate information
- Organize related facts together
- Preserve important details
- Use clear, concise language
- Don't include explanations of what you're doing

Output ONLY the merged memory text, nothing else."""

            user_message = f"""Memory type: {memory_type}

Current memory:
{current_memory if current_memory else "(empty)"}

New information to add:
{new_memory}

Reason for adding: {reason}

Please merge this into a single, concise memory."""

            # Call Haiku for efficient merge
            response = claude_service.send_message(
                messages=[{"role": "user", "content": user_message}],
                system_prompt=system_prompt,
                model="claude-3-5-haiku-latest",
                max_tokens=300
            )

            # Extract text from response content_blocks
            from app.utils.claude_parsing_utils import extract_text
            merged_text = extract_text(response)
            if merged_text:
                return merged_text.strip()

            return None

        except Exception as e:
            print(f"AI memory merge failed: {e}")
            return None

    def _save_memory(
        self,
        memory_type: str,
        memory: str,
        project_id: Optional[str]
    ) -> bool:
        """
        Save memory to file.

        Args:
            memory_type: 'user' or 'project'
            memory: Memory text to save
            project_id: Project UUID (for project memory)

        Returns:
            True if successful
        """
        try:
            if memory_type == 'user':
                memory_path = self.data_dir / 'user_memory.json'
            else:
                memory_path = self.data_dir / 'projects' / project_id / 'memory.json'

            # Ensure directory exists
            memory_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'memory': memory,
                'updated_at': datetime.utcnow().isoformat()
            }

            with open(memory_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving {memory_type} memory: {e}")
            return False

    def delete_project_memory(self, project_id: str) -> bool:
        """
        Delete memory for a project.

        Called when project is deleted.

        Args:
            project_id: Project UUID

        Returns:
            True if successful
        """
        try:
            memory_path = self.data_dir / 'projects' / project_id / 'memory.json'
            if memory_path.exists():
                memory_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting project memory: {e}")
            return False

    def build_memory_context(self, project_id: str) -> str:
        """
        Build memory context for chat system prompt.

        Args:
            project_id: Project UUID

        Returns:
            Formatted memory context string
        """
        user_memory = self.get_user_memory()
        project_memory = self.get_project_memory(project_id)

        if not user_memory and not project_memory:
            return ""

        lines = ["## Memory Context"]

        if user_memory:
            lines.append("")
            lines.append("### User Memory")
            lines.append(user_memory)

        if project_memory:
            lines.append("")
            lines.append("### Project Memory")
            lines.append(project_memory)

        return "\n".join(lines)


# Global instance
memory_service = MemoryService()
