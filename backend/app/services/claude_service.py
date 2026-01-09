"""
Claude Service - Wrapper for Claude API interactions.

Educational Note: This service provides a clean interface to the Claude API.
It's designed to be used by multiple callers (chat, subagents, tools, etc.)
with different configurations (prompts, tools, temperature).

Key Design Decisions:
- Stateless: Each call is independent, caller provides all context
- Flexible: Accepts variable parameters for different use cases
- Reusable: Can be called from main chat, subagents, RAG pipeline, etc.
"""
import os
from typing import Optional, List, Dict, Any

try:
    import anthropic
except ImportError:
    anthropic = None


class ClaudeService:
    """
    Service class for Claude API interactions.

    Educational Note: This is a thin wrapper around the Anthropic client.
    It handles client initialization and provides a consistent interface
    for making API calls with various configurations.
    """

    def __init__(self):
        """Initialize the Claude service."""
        self._client: Optional[Any] = None

    def _get_client(self):
        """
        Get or create the Anthropic client.

        Educational Note: Lazy initialization to avoid errors if API key
        is not set at import time.

        Raises:
            ValueError: If ANTHROPIC_API_KEY is not set or anthropic package not installed
        """
        if not anthropic:
            raise ValueError("anthropic package is not installed. Please install it with: pip install anthropic")
            
        if self._client is None:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            self._client = anthropic.Anthropic(api_key=api_key)
        return self._client

    def send_message(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 4096,
        temperature: float = 0.2,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send messages to Claude and get a response.

        Educational Note: This is the core method for Claude API interaction.
        Different callers can customize behavior via parameters:
        - Main chat: Just messages + system prompt
        - Subagents: Messages + tools + specific prompts
        - RAG: Messages with context + retrieval tools

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt for this conversation
            model: Claude model to use (default: claude-sonnet-4-5-20250929)
            max_tokens: Maximum tokens in response (default: 4096)
            temperature: Sampling temperature (default: 0.2)
            tools: Optional list of tool definitions for tool use
            tool_choice: Optional tool choice configuration
            extra_headers: Optional headers for beta features
            project_id: Optional project ID for cost tracking (future implementation)

        Returns:
            Dict containing:
                - content_blocks: The response content (text or tool_use blocks)
                - model: Model used
                - usage: Token usage stats
                - stop_reason: Why the response ended

        Raises:
            ValueError: If API key is not configured
            Exception: If API call fails
        """
        client = self._get_client()

        # Build API call parameters
        api_params = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }

        # Add optional parameters only if provided
        if system_prompt:
            api_params["system"] = system_prompt

        if temperature != 0.2:  # Only set if not default
            api_params["temperature"] = temperature

        if tools:
            api_params["tools"] = tools

        if tool_choice:
            api_params["tool_choice"] = tool_choice

        # Add extra headers for beta features (e.g., web_fetch)
        if extra_headers:
            api_params["extra_headers"] = extra_headers

        # Make API call
        response = client.messages.create(**api_params)

        # TODO: Track costs if project_id provided
        # This would integrate with a cost tracking system

        # Return raw response data - all parsing happens in claude_parsing_utils
        return {
            "content_blocks": response.content,  # Raw Anthropic content blocks
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            "stop_reason": response.stop_reason,
        }

    def count_tokens(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        """
        Count tokens for a message chain without sending to Claude.

        Educational Note: Uses Claude's beta token counting API for accurate counts.
        This is useful for billing estimation and context length management.

        Args:
            messages: List of message dicts
            system_prompt: Optional system prompt
            model: Model to count tokens for
            tools: Optional tools (affect token count)

        Returns:
            Total token count for the input

        Raises:
            ValueError: If API key is not configured
            Exception: If API call fails
        """
        client = self._get_client()

        # Build parameters for token counting
        count_params = {
            "model": model,
            "messages": messages,
        }

        if system_prompt:
            count_params["system"] = system_prompt

        if tools:
            count_params["tools"] = tools

        # Use Claude's token counting API
        response = client.messages.count_tokens(**count_params)
        return response.input_tokens


# Singleton instance
claude_service = ClaudeService()