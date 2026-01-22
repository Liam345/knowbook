"""
Tool definitions for KnowBook AI chat system.

Provides JSON tool schemas for Claude API integration.
"""
import json
from pathlib import Path
from typing import Dict, Any, List

TOOLS_DIR = Path(__file__).parent


def load_tool(tool_name: str) -> Dict[str, Any]:
    """
    Load a tool definition from JSON file.

    Args:
        tool_name: Name of the tool (without .json extension)

    Returns:
        Tool definition dictionary
    """
    tool_path = TOOLS_DIR / f"{tool_name}.json"
    if not tool_path.exists():
        raise FileNotFoundError(f"Tool definition not found: {tool_name}")

    with open(tool_path, 'r') as f:
        return json.load(f)


def get_chat_tools(has_sources: bool = False, has_csv: bool = False) -> List[Dict[str, Any]]:
    """
    Get available tools for chat based on project context.

    Args:
        has_sources: Whether project has active sources
        has_csv: Whether project has CSV sources

    Returns:
        List of tool definitions
    """
    tools = [
        load_tool("store_memory"),
        load_tool("studio_signal")
    ]

    if has_sources:
        tools.append(load_tool("search_sources"))

    if has_csv:
        tools.append(load_tool("analyze_csv"))

    return tools


__all__ = ['load_tool', 'get_chat_tools']
