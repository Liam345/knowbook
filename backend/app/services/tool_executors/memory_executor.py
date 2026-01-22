"""
Memory Executor for KnowBook.

Executes the store_memory tool for Claude.
Uses non-blocking pattern: returns success immediately,
queues background task for actual memory update.
"""
import threading
from typing import Dict, Any, Optional, List

from app.services.memory_service import memory_service


class MemoryExecutor:
    """
    Executes store_memory tool calls.

    Non-blocking design: Returns immediately while memory
    update happens in background thread.
    """

    def execute(
        self,
        project_id: str,
        user_memory: Optional[str] = None,
        project_memory: Optional[str] = None,
        why_generated: str = ""
    ) -> Dict[str, Any]:
        """
        Execute memory storage request.

        Returns immediately with success message,
        actual memory update runs in background.

        Args:
            project_id: Project UUID (for project memory)
            user_memory: User-level information to store
            project_memory: Project-specific information to store
            why_generated: Reason for storing

        Returns:
            Dictionary with success status and message
        """
        storing = []

        # Queue user memory update
        if user_memory:
            thread = threading.Thread(
                target=self._update_user_memory,
                args=(user_memory, why_generated),
                daemon=True
            )
            thread.start()
            storing.append("user memory")

        # Queue project memory update
        if project_memory:
            thread = threading.Thread(
                target=self._update_project_memory,
                args=(project_id, project_memory, why_generated),
                daemon=True
            )
            thread.start()
            storing.append("project memory")

        if not storing:
            return {
                "success": False,
                "message": "No memory provided to store"
            }

        return {
            "success": True,
            "message": f"Memory update queued: {', '.join(storing)}"
        }

    def _update_user_memory(
        self,
        new_memory: str,
        reason: str
    ):
        """Background task to update user memory."""
        try:
            memory_service.update_user_memory(new_memory, reason)
        except Exception as e:
            print(f"Error updating user memory: {e}")

    def _update_project_memory(
        self,
        project_id: str,
        new_memory: str,
        reason: str
    ):
        """Background task to update project memory."""
        try:
            memory_service.update_project_memory(project_id, new_memory, reason)
        except Exception as e:
            print(f"Error updating project memory: {e}")


# Global instance
memory_executor = MemoryExecutor()
