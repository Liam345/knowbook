"""
Main Chat Service - Orchestrates chat message processing and AI responses.

Educational Note: This service handles the core chat logic with tool support.

Message Flow:
1. User message - What the user types in chat
2. Assistant response - Two types:
   a. Text response - Final answer to user (stored and displayed)
   b. Tool use - Claude wants to search sources
3. User message (tool_result) - Results from tool execution sent back
4. Repeat 2-3 until Claude gives text response

The service uses message_service for all message handling and tool parsing.
"""
from typing import Dict, Any, Tuple, List, Optional

from app.services.chat_service import chat_service
from app.services.claude_service import claude_service
from app.services.message_service import message_service
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
        self._memory_tool = None
        # Future: Additional tools will be loaded here

    def _get_memory_tool(self) -> Dict[str, Any]:
        """Load the store_memory tool definition (basic version for now)."""
        if self._memory_tool is None:
            # Basic memory tool definition - simplified version
            self._memory_tool = {
                "name": "store_memory",
                "description": "Store important information to remember for future conversations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_memory": {
                            "type": "string",
                            "description": "Personal information about the user to remember"
                        },
                        "project_memory": {
                            "type": "string", 
                            "description": "Information about this specific project to remember"
                        },
                        "why_generated": {
                            "type": "string",
                            "description": "Brief explanation of why this memory is important"
                        }
                    }
                }
            }
        return self._memory_tool

    def _get_tools(self, has_active_sources: bool = False) -> List[Dict[str, Any]]:
        """
        Get tools list for Claude API call.

        Educational Note: Memory tool is always available.
        Search tool would be available when there are active sources (future implementation).

        Args:
            has_active_sources: Whether project has active sources

        Returns:
            List of tool definitions
        """
        # Always include memory tool
        tools = [self._get_memory_tool()]

        # Future: Add search_sources tool when has_active_sources is True
        # if has_active_sources:
        #     tools.append(self._get_search_tool())

        return tools

    def _build_system_prompt(self, project_id: str, base_prompt: str = "") -> str:
        """
        Build system prompt with memory and source context appended.

        Educational Note: Context is rebuilt on every message to reflect
        current state (memory updates, active/inactive sources).
        """
        if not base_prompt:
            base_prompt = """You are KnowBook, an AI assistant that helps users work with their documents and sources.

You are knowledgeable, helpful, and concise. You can help users understand their content, answer questions about their sources, and assist with various tasks.

If users ask questions that would benefit from searching their sources, let them know that source search capabilities will be available soon.

You have access to a memory tool to remember important information about users and their projects."""

        # Future: Add memory and source context loading
        # full_context = context_loader.build_full_context(project_id)
        # if full_context:
        #     return base_prompt + "\n" + full_context

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
        Currently only supports store_memory (basic implementation).
        """
        if tool_name == "store_memory":
            # Basic memory implementation - just acknowledge for now
            user_memory = tool_input.get("user_memory", "")
            project_memory = tool_input.get("project_memory", "")
            why_generated = tool_input.get("why_generated", "")
            
            # Future: Implement actual memory storage
            # For now, just acknowledge the memory request
            return f"Memory stored successfully. Reason: {why_generated}"

        else:
            return f"Unknown tool: {tool_name}"

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

        # Step 2: Build system prompt
        system_prompt = self._build_system_prompt(project_id)

        # Step 3: Get tools (memory always available)
        tools = self._get_tools(has_active_sources=False)  # Future: check for actual sources

        try:
            # Step 4: Build messages and call Claude
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

            # Step 5: Handle tool use loop
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

            # Step 6: Store final text response
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

        # Step 7: Sync chat index
        chat_service.sync_chat_to_index(project_id, chat_id)

        # Future: Auto-rename chat on first message (background task)
        # if chat.get("message_count", 0) == 0:
        #     # Submit naming task to background
        #     pass

        return user_msg, assistant_msg


# Singleton instance
main_chat_service = MainChatService()