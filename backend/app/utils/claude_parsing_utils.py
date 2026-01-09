"""
Claude Response Parsing Utilities.

Educational Note: Centralized parsing for Claude API responses.
Clean separation of concerns between API calls and response processing.

Response Flow:
claude_service.py (API call) → returns raw {content_blocks, stop_reason, usage, model}
         ↓
claude_parsing_utils.py (parse response)
   - is_tool_use(response) / is_end_turn(response)
   - extract_text(response)
   - extract_tool_use_blocks(response)
   - build_tool_result_content(results)
   - serialize_content_blocks(blocks)
         ↓
message_service.py (store if needed - pure CRUD)
"""
from typing import Dict, List, Any, Optional


def is_tool_use(response: Dict[str, Any]) -> bool:
    """
    Check if Claude response contains tool use.

    Educational Note: When Claude wants to use tools, stop_reason is "tool_use".
    This indicates we need to execute tools and send back tool results.

    Args:
        response: Raw Claude API response

    Returns:
        True if response contains tool use blocks
    """
    return response.get("stop_reason") == "tool_use"


def is_end_turn(response: Dict[str, Any]) -> bool:
    """
    Check if Claude response indicates conversation end.

    Educational Note: When stop_reason is "end_turn", Claude has finished
    and doesn't need any more input from us.

    Args:
        response: Raw Claude API response

    Returns:
        True if conversation has ended
    """
    return response.get("stop_reason") == "end_turn"


def extract_text(response: Dict[str, Any]) -> str:
    """
    Extract text content from Claude response.

    Educational Note: Claude can respond with text + tool_use together.
    This extracts just the text parts that should be shown to the user.

    Args:
        response: Raw Claude API response

    Returns:
        Combined text content from all text blocks
    """
    content_blocks = response.get("content_blocks", [])
    text_parts = []

    for block in content_blocks:
        if hasattr(block, 'type') and block.type == "text":
            text_parts.append(block.text)
        elif isinstance(block, dict) and block.get("type") == "text":
            text_parts.append(block.get("text", ""))

    return "".join(text_parts)


def extract_tool_use_blocks(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract tool use blocks from Claude response.

    Educational Note: When Claude wants to use tools, the response contains
    tool_use blocks with tool name, id, and input parameters.

    Args:
        response: Raw Claude API response

    Returns:
        List of tool use blocks: [{"id": "...", "name": "...", "input": {...}}]
    """
    content_blocks = response.get("content_blocks", [])
    tool_blocks = []

    for block in content_blocks:
        if hasattr(block, 'type') and block.type == "tool_use":
            # Anthropic SDK object
            tool_blocks.append({
                "id": block.id,
                "name": block.name,
                "input": block.input
            })
        elif isinstance(block, dict) and block.get("type") == "tool_use":
            # Dictionary format
            tool_blocks.append({
                "id": block.get("id"),
                "name": block.get("name"),
                "input": block.get("input", {})
            })

    return tool_blocks


def extract_tool_inputs(response: Dict[str, Any], tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Extract inputs for a specific tool from Claude response.

    Educational Note: Sometimes you only care about one specific tool's inputs.
    This is a convenience method for single-tool scenarios.

    Args:
        response: Raw Claude API response
        tool_name: Name of the tool to extract inputs for

    Returns:
        Tool inputs dict or None if tool not found
    """
    tool_blocks = extract_tool_use_blocks(response)
    
    for block in tool_blocks:
        if block.get("name") == tool_name:
            return block.get("input", {})
    
    return None


def build_tool_result_content(results: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Build tool result content for sending back to Claude.

    Educational Note: After executing tools, we need to send results back
    in a specific format that Claude expects.

    Args:
        results: List of tool results: [{"tool_use_id": "...", "content": "..."}]

    Returns:
        Formatted tool result content blocks
    """
    content_blocks = []
    
    for result in results:
        content_blocks.append({
            "type": "tool_result",
            "tool_use_id": result["tool_use_id"],
            "content": result["content"]
        })
    
    return content_blocks


def serialize_content_blocks(content_blocks: List[Any]) -> List[Dict[str, Any]]:
    """
    Serialize Anthropic content blocks to JSON-compatible format.

    Educational Note: Anthropic SDK returns objects that need to be converted
    to dictionaries for JSON storage in message files.

    Args:
        content_blocks: Raw Anthropic content blocks

    Returns:
        JSON-serializable list of content block dictionaries
    """
    serialized = []
    
    for block in content_blocks:
        if hasattr(block, 'type'):
            # Anthropic SDK object - convert to dict
            if block.type == "text":
                serialized.append({
                    "type": "text",
                    "text": block.text
                })
            elif block.type == "tool_use":
                serialized.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
        elif isinstance(block, dict):
            # Already a dictionary
            serialized.append(block)
    
    return serialized