"""
Main Chat Service - Orchestrates chat message processing and AI responses.

Educational Note: This service handles the core chat logic with tool support.

Message Flow:
1. User message - What the user types in chat
2. Assistant response - Two types:
   a. Text response - Final answer to user (stored and displayed)
   b. Tool use - Claude wants to search sources or store memory
3. User message (tool_result) - Results from tool execution sent back
4. Repeat 2-3 until Claude gives text response

The service uses message_service for all message handling and tool parsing.
Tool executors handle the actual tool execution (search, memory, signals).
"""
from typing import Dict, Any, Tuple, List, Optional

from app.services.chat_service import chat_service
from app.services.claude_service import claude_service
from app.services.message_service import message_service
from app.services.source_service import source_service
from app.services.memory_service import memory_service
from app.services.tool_executors import (
    source_search_executor,
    memory_executor,
    studio_signal_executor
)
from app.tools import get_chat_tools
from app.utils import claude_parsing_utils


class MainChatService:
    """
    Service class for orchestrating chat conversations with tool support.

    Educational Note: This service coordinates the message flow between
    user, Claude, and tools. It uses message_service for all message
    operations and tool parsing.
    """

    # Maximum tool iterations to prevent infinite loops
    MAX_TOOL_ITERATIONS = 10

    def __init__(self):
        """Initialize the service."""
        pass

    def _get_active_sources(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get list of active, ready sources for a project.

        Educational Note: Only sources that are both active AND ready
        (fully processed) are available for searching.

        Args:
            project_id: Project UUID

        Returns:
            List of active source metadata
        """
        all_sources = source_service.list_sources(project_id)
        return [
            s for s in all_sources
            if s.get('active', True) and s.get('status') == 'ready'
        ]

    def _get_tools(self, has_sources: bool = False, has_csv: bool = False) -> List[Dict[str, Any]]:
        """
        Get tools list for Claude API call.

        Educational Note: Tools are loaded from JSON definitions.
        - Memory and studio_signal are always available
        - search_sources only when project has active sources
        - analyze_csv only when project has CSV sources (future)

        Args:
            has_sources: Whether project has active sources
            has_csv: Whether project has CSV sources

        Returns:
            List of tool definitions
        """
        return get_chat_tools(has_sources=has_sources, has_csv=has_csv)

    def _build_system_prompt(
        self,
        project_id: str,
        active_sources: List[Dict[str, Any]],
        base_prompt: str = ""
    ) -> str:
        """
        Build system prompt with memory and source context appended.

        Educational Note: Context is rebuilt on every message to reflect
        current state (memory updates, active/inactive sources).

        Args:
            project_id: Project UUID
            active_sources: List of active source metadata
            base_prompt: Optional custom base prompt

        Returns:
            Complete system prompt with all context
        """
        if not base_prompt:
            base_prompt = """You are KnowBook, an AI assistant that helps users work with their documents and sources.

You are knowledgeable, helpful, and concise. You can help users understand their content, answer questions about their sources, and assist with various tasks.

When answering questions about sources, use the search_sources tool to find relevant information. Include citations in your response using the format [[cite:CHUNK_ID]] where CHUNK_ID comes from the search results.

You have access to tools:
- search_sources: Search through project sources using keywords or semantic search
- store_memory: Remember important information about users and projects
- studio_signal: Signal when studio tools might help the user"""

        # Add memory context
        memory_context = memory_service.build_memory_context(project_id)
        if memory_context:
            base_prompt += "\n\n" + memory_context

        # Add available sources context
        if active_sources:
            sources_list = "\n".join([
                f"- {s.get('name', 'Unnamed')} (ID: {s['id']}, Type: {s.get('file_type', 'unknown')})"
                for s in active_sources
            ])
            base_prompt += f"\n\n## Available Sources\nThe user has the following sources available for searching:\n{sources_list}"

        return base_prompt

    def _execute_tool(
        self,
        project_id: str,
        chat_id: str,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> str:
        """
        Execute a tool and return result string.

        Educational Note: Routes tool calls to appropriate executor.
        Each executor handles its specific tool logic.

        Args:
            project_id: Project UUID
            chat_id: Chat UUID
            tool_name: Name of tool to execute
            tool_input: Tool input parameters

        Returns:
            Tool result as string (JSON for structured data)
        """
        import json

        if tool_name == "search_sources":
            # Execute source search
            result = source_search_executor.execute(
                project_id=project_id,
                source_id=tool_input.get("source_id"),
                keywords=tool_input.get("keywords"),
                query=tool_input.get("query")
            )
            return json.dumps(result)

        elif tool_name == "store_memory":
            # Execute memory storage (non-blocking)
            result = memory_executor.execute(
                project_id=project_id,
                user_memory=tool_input.get("user_memory"),
                project_memory=tool_input.get("project_memory"),
                why_generated=tool_input.get("why_generated", "")
            )
            return json.dumps(result)

        elif tool_name == "studio_signal":
            # Execute studio signal storage
            signals = tool_input.get("signals", [])
            result = studio_signal_executor.execute(
                project_id=project_id,
                chat_id=chat_id,
                signals=signals
            )
            return json.dumps(result)

        elif tool_name == "analyze_csv":
            # Future: CSV analysis tool
            return json.dumps({
                "success": False,
                "message": "CSV analysis not yet implemented"
            })

        else:
            return json.dumps({
                "success": False,
                "message": f"Unknown tool: {tool_name}"
            })

    def send_message(
        self,
        project_id: str,
        chat_id: str,
        user_message_text: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process a user message and get AI response.

        Educational Note: This method handles the complete message flow:
        1. Store user message
        2. Build context and call Claude
        3. If tool_use: execute tool, send result, call again
        4. When text response: store and return

        Args:
            project_id: The project UUID
            chat_id: The chat UUID
            user_message_text: The user's message text

        Returns:
            Tuple of (user_message_dict, assistant_message_dict)
        """
        # Verify chat exists
        chat = chat_service.get_chat(project_id, chat_id)
        if not chat:
            raise ValueError("Chat not found")

        # Step 1: Store user message
        user_msg = message_service.add_user_message(project_id, chat_id, user_message_text)

        # Step 2: Get active sources for this project
        active_sources = self._get_active_sources(project_id)
        has_sources = len(active_sources) > 0

        # Step 3: Build system prompt with memory and source context
        system_prompt = self._build_system_prompt(project_id, active_sources)

        # Step 4: Get tools (search available when sources exist)
        tools = self._get_tools(has_sources=has_sources, has_csv=False)

        try:
            # Step 5: Build messages and call Claude
            api_messages = message_service.build_api_messages(project_id, chat_id)

            response = claude_service.send_message(
                messages=api_messages,
                system_prompt=system_prompt,
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                temperature=0.2,
                tools=tools,
                project_id=project_id
            )

            # Step 6: Handle tool use loop
            iteration = 0
            accumulated_text_parts = []

            while claude_parsing_utils.is_tool_use(response) and iteration < self.MAX_TOOL_ITERATIONS:
                iteration += 1

                # Get tool_use blocks from response
                tool_use_blocks = claude_parsing_utils.extract_tool_use_blocks(response)

                if not tool_use_blocks:
                    break

                # Extract text from this response BEFORE storing
                response_text = claude_parsing_utils.extract_text(response)
                if response_text.strip():
                    accumulated_text_parts.append(response_text)

                # Store the assistant's tool_use response
                serialized_content = claude_parsing_utils.serialize_content_blocks(
                    response.get("content_blocks", [])
                )
                message_service.add_message(
                    project_id=project_id,
                    chat_id=chat_id,
                    role="assistant",
                    content=serialized_content
                )

                # Execute each tool and add results
                for tool_block in tool_use_blocks:
                    tool_id = tool_block.get("id")
                    tool_name = tool_block.get("name")
                    tool_input = tool_block.get("input", {})

                    # Execute tool
                    result = self._execute_tool(project_id, chat_id, tool_name, tool_input)

                    # Add tool result as user message
                    message_service.add_tool_result_message(
                        project_id=project_id,
                        chat_id=chat_id,
                        tool_use_id=tool_id,
                        result=result
                    )

                # Rebuild messages and call Claude again
                api_messages = message_service.build_api_messages(project_id, chat_id)

                response = claude_service.send_message(
                    messages=api_messages,
                    system_prompt=system_prompt,
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=4096,
                    temperature=0.2,
                    tools=tools,
                    project_id=project_id
                )

            # Step 7: Store final text response
            final_response_text = claude_parsing_utils.extract_text(response)
            if final_response_text.strip():
                accumulated_text_parts.append(final_response_text)

            # Combine all accumulated text
            final_text = "\n\n".join(accumulated_text_parts) if accumulated_text_parts else ""

            assistant_msg = message_service.add_assistant_message(
                project_id=project_id,
                chat_id=chat_id,
                content=final_text if final_text.strip() else "I've processed your request.",
                model=response.get("model"),
                tokens=response.get("usage")
            )

        except Exception as api_error:
            # Store error message
            assistant_msg = message_service.add_assistant_message(
                project_id=project_id,
                chat_id=chat_id,
                content=f"Sorry, I encountered an error: {str(api_error)}",
                error=True
            )

        # Step 8: Sync chat index
        chat_service.sync_chat_to_index(project_id, chat_id)

        # Future: Auto-rename chat on first message (background task)
        # if chat.get("message_count", 0) == 0:
        #     # Submit naming task to background
        #     pass

        return user_msg, assistant_msg


# Singleton instance
main_chat_service = MainChatService()