"""
Studio Signal Executor for KnowBook.

Executes the studio_signal tool for Claude.
Stores signals about studio tools that might help the user.
Signals are saved to the chat and displayed in the UI.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class StudioSignalExecutor:
    """
    Executes studio_signal tool calls.

    Stores signals synchronously (unlike memory executor)
    since they need to be immediately available for UI.
    """

    def __init__(self):
        """Initialize the studio signal executor."""
        self.data_dir = Path(__file__).parent.parent.parent / 'data'

    def execute(
        self,
        project_id: str,
        chat_id: str,
        signals: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Execute studio signal storage.

        Args:
            project_id: Project UUID
            chat_id: Chat UUID
            signals: List of signal objects with tool_type and reason

        Returns:
            Dictionary with success status and message
        """
        if not signals:
            return {
                "success": False,
                "message": "No signals provided"
            }

        try:
            # Load current chat
            chat_path = self.data_dir / 'projects' / project_id / 'chats' / f"{chat_id}.json"
            if not chat_path.exists():
                return {
                    "success": False,
                    "message": "Chat not found"
                }

            with open(chat_path, 'r', encoding='utf-8') as f:
                chat = json.load(f)

            # Add signals to chat
            existing_signals = chat.get('studio_signals', [])

            for signal in signals:
                signal_entry = {
                    'tool_type': signal.get('tool_type'),
                    'reason': signal.get('reason'),
                    'created_at': datetime.utcnow().isoformat()
                }
                existing_signals.append(signal_entry)

            chat['studio_signals'] = existing_signals
            chat['updated_at'] = datetime.utcnow().isoformat()

            # Save updated chat
            with open(chat_path, 'w', encoding='utf-8') as f:
                json.dump(chat, f, indent=2)

            tool_types = [s.get('tool_type') for s in signals]
            return {
                "success": True,
                "message": f"Studio signals stored: {', '.join(tool_types)}"
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }


# Global instance
studio_signal_executor = StudioSignalExecutor()
