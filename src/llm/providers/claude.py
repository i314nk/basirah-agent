"""
Claude (Anthropic) LLM provider.
"""

import os
import logging
from typing import List, Dict, Any, Callable
from anthropic import Anthropic
import anthropic

from src.llm.base import BaseLLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseLLMProvider):
    """
    Provider for Claude models via Anthropic API.

    Supported models:
    - claude-sonnet-4-20250514 (Claude 4 Sonnet)
    - claude-3-5-sonnet-20241022 (Claude 3.5 Sonnet)
    - claude-3-opus-20240229 (Claude 3 Opus)
    """

    # Model name mappings
    MODEL_ALIASES = {
        "claude-sonnet-4.5": "claude-sonnet-4-20250514",
        "claude-4-sonnet": "claude-sonnet-4-20250514",
        "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
        "claude-3-opus": "claude-3-opus-20240229"
    }

    # Cost per 1M tokens (as of Nov 2025)
    COSTS = {
        "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
        "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
        "claude-3-opus-20240229": {"input": 15.0, "output": 75.0}
    }

    def __init__(self, model_name: str, **kwargs):
        """Initialize Claude provider."""
        super().__init__(model_name, **kwargs)

        # Resolve model alias
        self.model_id = self.MODEL_ALIASES.get(model_name, model_name)

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=api_key)

        logger.info(f"Initialized ClaudeProvider with model: {self.model_id}")

    def generate(
        self,
        messages: List[LLMMessage],
        max_tokens: int = 16000,
        temperature: float = 1.0,
        **kwargs
    ) -> LLMResponse:
        """Generate response from Claude."""

        # Convert messages to Anthropic format
        formatted_messages = []
        system_prompt = None

        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        try:
            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else None,
                messages=formatted_messages
            )

            # Extract response
            content = response.content[0].text
            tokens_input = response.usage.input_tokens
            tokens_output = response.usage.output_tokens

            # Calculate cost
            cost = self.calculate_cost(tokens_input, tokens_output)

            return LLMResponse(
                content=content,
                model=self.model_id,
                provider="claude",
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost=cost,
                metadata={
                    "stop_reason": response.stop_reason,
                    "model_version": self.model_id
                }
            )

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    def is_available(self) -> bool:
        """Check if Claude API is available."""
        try:
            return bool(os.getenv("ANTHROPIC_API_KEY"))
        except:
            return False

    def get_cost_per_token(self) -> Dict[str, float]:
        """Get cost per token for Claude model."""
        costs = self.COSTS.get(
            self.model_id,
            {"input": 3.0, "output": 15.0}  # Default to Sonnet pricing
        )

        # Convert from per 1M tokens to per token
        return {
            "input": costs["input"] / 1_000_000,
            "output": costs["output"] / 1_000_000
        }

    def run_react_loop(
        self,
        system_prompt: str,
        initial_message: str,
        tools: List[Dict[str, Any]],
        tool_executor: Callable[[str, Dict[str, Any]], Dict[str, Any]],
        max_iterations: int = 30,
        max_tokens: int = 32000,
        thinking_budget: int = 10000
    ) -> Dict[str, Any]:
        """
        Run Claude-native ReAct loop with Extended Thinking and native tool use.

        Uses Claude's Extended Thinking and native Tool Use API for optimal
        performance and reasoning quality.

        Args:
            system_prompt: System prompt defining agent personality/task
            initial_message: Initial user message to start analysis
            tools: List of tool definitions in Claude format (name, description, input_schema)
            tool_executor: Callback function(tool_name, tool_input) -> result dict
            max_iterations: Maximum ReAct iterations (default 30)
            max_tokens: Maximum tokens per response (default 32000)
            thinking_budget: Thinking token budget (default 10000)

        Returns:
            Dict with:
                - success: bool - Whether analysis completed successfully
                - thesis: str - Final analysis text from agent
                - metadata: dict - Usage stats (iterations, tool_calls, tokens, cost)
        """
        messages = [{"role": "user", "content": initial_message}]
        tool_calls_made = 0
        iteration = 0

        # Token tracking
        total_input_tokens = 0
        total_output_tokens = 0
        total_web_search_requests = 0  # Track Claude native web searches

        # Context management constants
        CONTEXT_PRUNE_THRESHOLD = 180000  # Start pruning at 180K tokens
        MIN_RECENT_MESSAGES = 8  # Keep at least 4 exchanges

        logger.info(f"Starting Claude ReAct loop (max {max_iterations} iterations)")

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"\n--- Iteration {iteration} ---")

            try:
                # Call Claude with extended thinking using STREAMING
                stream = self.client.messages.create(
                    model=self.model_id,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=messages,
                    tools=tools,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": thinking_budget
                    },
                    stream=True  # Enable streaming for long operations
                )

                # Accumulate response from stream
                assistant_content = []
                tool_uses = []
                current_block = None

                input_tokens = 0
                output_tokens = 0

                logger.debug("Processing streaming response...")

                for event in stream:
                    # Message start - contains initial usage info
                    if event.type == "message_start":
                        input_tokens = event.message.usage.input_tokens
                        logger.debug(f"Stream started - input tokens: {input_tokens}")

                        # Track web search requests if present (Claude native web search)
                        if hasattr(event.message.usage, 'server_tool_use'):
                            web_searches = getattr(event.message.usage.server_tool_use, 'web_search_requests', 0)
                            if web_searches > 0:
                                total_web_search_requests += web_searches
                                logger.info(f"[Web Search] {web_searches} searches executed by Claude")

                    # Content block start - new thinking, text, tool_use, or server_tool_use block
                    elif event.type == "content_block_start":
                        block = event.content_block

                        if block.type == "thinking":
                            current_block = {"type": "thinking", "thinking": "", "signature": ""}
                        elif block.type == "text":
                            current_block = {"type": "text", "text": ""}
                        elif block.type == "tool_use":
                            current_block = {
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": {}
                            }
                            logger.info(f"[Tool Use] {block.name} (id: {block.id})")
                        elif block.type == "server_tool_use":
                            # Claude native web search - executed by Claude automatically
                            current_block = {
                                "type": "server_tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": {}
                            }
                            logger.info(f"[Server Tool Use - Native Web Search] {block.name} (id: {block.id})")
                        elif block.type == "web_search_tool_result":
                            # Results from Claude native web search
                            current_block = {
                                "type": "web_search_tool_result",
                                "tool_use_id": getattr(block, 'tool_use_id', None),
                                "content": []
                            }
                            logger.info(f"[Web Search Results] Received from Claude")

                    # Content block delta - incremental content
                    elif event.type == "content_block_delta":
                        if current_block is None:
                            continue

                        delta = event.delta

                        if delta.type == "thinking_delta":
                            current_block["thinking"] += delta.thinking
                        elif delta.type == "signature_delta":
                            if "signature" not in current_block:
                                current_block["signature"] = ""
                            current_block["signature"] += delta.signature
                        elif delta.type == "text_delta":
                            current_block["text"] += delta.text
                        elif delta.type == "input_json_delta":
                            if "input_json" not in current_block:
                                current_block["input_json"] = ""
                            current_block["input_json"] += delta.partial_json

                    # Content block stop - block complete
                    elif event.type == "content_block_stop":
                        if current_block is None:
                            continue

                        # Finalize tool_use/server_tool_use input if needed
                        if current_block["type"] in ["tool_use", "server_tool_use"] and "input_json" in current_block:
                            import json
                            current_block["input"] = json.loads(current_block["input_json"])
                            del current_block["input_json"]

                        if current_block["type"] == "thinking":
                            logger.debug(f"[Thinking] {len(current_block['thinking'])} characters")
                            assistant_content.append(current_block)
                        elif current_block["type"] == "text":
                            logger.info(f"[Agent] {current_block['text'][:200]}...")
                            assistant_content.append(current_block)
                        elif current_block["type"] == "tool_use":
                            # Regular tool - add to tool_uses for execution
                            from types import SimpleNamespace
                            tool_use_obj = SimpleNamespace(
                                type="tool_use",
                                id=current_block["id"],
                                name=current_block["name"],
                                input=current_block["input"]
                            )
                            tool_uses.append(tool_use_obj)
                            assistant_content.append(current_block)
                        elif current_block["type"] == "server_tool_use":
                            # Claude native tool (web search) - just add to content, Claude handles execution
                            logger.info(f"[Server Tool] {current_block['name']} - query: {current_block.get('input', {}).get('query', 'N/A')}")
                            assistant_content.append(current_block)
                        elif current_block["type"] == "web_search_tool_result":
                            # Web search results from Claude - just add to content
                            result_count = len(current_block.get("content", []))
                            logger.info(f"[Web Search Results] {result_count} results received")
                            assistant_content.append(current_block)

                        current_block = None

                    # Message delta - usage updates
                    elif event.type == "message_delta":
                        if hasattr(event, 'usage') and event.usage:
                            output_tokens = event.usage.output_tokens

                    # Message stop - stream complete
                    elif event.type == "message_stop":
                        logger.debug("Stream completed")

                # Update token usage
                total_input_tokens += input_tokens
                total_output_tokens += output_tokens
                logger.debug(f"Tokens - Input: {input_tokens}, Output: {output_tokens}")

                # Add assistant's response to conversation
                messages.append({
                    "role": "assistant",
                    "content": assistant_content
                })

                # If agent used tools, execute them
                if tool_uses:
                    tool_results = []

                    for tool_use in tool_uses:
                        tool_calls_made += 1
                        result = tool_executor(tool_use.name, tool_use.input)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": str(result)
                        })

                    # Add tool results to conversation
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })

                    # Check context size and prune if approaching limit
                    estimated_tokens = self._estimate_message_tokens(messages)
                    logger.debug(f"Current context: ~{estimated_tokens} tokens")

                    if estimated_tokens > CONTEXT_PRUNE_THRESHOLD:
                        logger.warning(
                            f"Context size ({estimated_tokens} tokens) exceeds threshold. Pruning..."
                        )
                        messages = self._prune_old_messages(messages, MIN_RECENT_MESSAGES)
                        estimated_tokens = self._estimate_message_tokens(messages)
                        logger.info(f"After pruning: ~{estimated_tokens} tokens")

                    # Continue loop (agent will process results)
                    continue

                # No tool use - agent has finished
                final_text = ""
                for block in assistant_content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        final_text += block.get("text", "") + "\n\n"

                logger.info(f"Agent finished after {tool_calls_made} tool calls")

                # Calculate costs (total and breakdown)
                cost_per_token = self.get_cost_per_token()
                input_cost = total_input_tokens * cost_per_token["input"]
                output_cost = total_output_tokens * cost_per_token["output"]

                # Add web search cost if applicable ($10 per 1,000 searches)
                web_search_cost = (total_web_search_requests / 1000) * 10.0 if total_web_search_requests > 0 else 0.0

                total_cost = input_cost + output_cost + web_search_cost

                metadata = {
                    "iterations": iteration,
                    "tool_calls": tool_calls_made,
                    "tokens_input": total_input_tokens,
                    "tokens_output": total_output_tokens,
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                    "cost": total_cost
                }

                # Add web search stats if used
                if total_web_search_requests > 0:
                    metadata["web_search_requests"] = total_web_search_requests
                    metadata["web_search_cost"] = web_search_cost
                    logger.info(f"Total web searches: {total_web_search_requests} (cost: ${web_search_cost:.4f})")

                return {
                    "success": True,
                    "thesis": final_text.strip(),
                    "metadata": metadata
                }

            except anthropic.RateLimitError as e:
                logger.warning(f"Rate limit hit: {e}")
                raise

            except anthropic.BadRequestError as e:
                # Handle "prompt is too long" errors
                error_msg = str(e)
                if "prompt is too long" in error_msg.lower() or "too many tokens" in error_msg.lower():
                    logger.error(f"Context window exceeded: {error_msg}")

                    # Try aggressive pruning as last resort
                    if len(messages) > 3:
                        logger.warning("Attempting aggressive context pruning...")
                        initial_prompt = messages[0]
                        last_two = messages[-2:]
                        messages = [initial_prompt] + last_two
                        logger.info(f"After aggressive pruning: {len(messages)} messages")
                        continue
                    else:
                        logger.error("Cannot prune further.")
                        raise
                else:
                    logger.error(f"Bad request error: {e}")
                    raise

            except anthropic.APIError as e:
                logger.error(f"Anthropic API error: {e}")
                raise

            except Exception as e:
                logger.error(f"Unexpected error in ReAct loop: {e}", exc_info=True)
                raise

        # Max iterations reached
        logger.warning(f"Max iterations ({max_iterations}) reached")
        return {
            "success": False,
            "thesis": "Analysis did not complete within reasonable time.",
            "metadata": {
                "iterations": iteration,
                "tool_calls": tool_calls_made,
                "tokens_input": total_input_tokens,
                "tokens_output": total_output_tokens,
                "error": "Max iterations reached"
            }
        }

    def _estimate_message_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """
        Estimate total tokens in message history.

        Uses rough heuristic: 1 token ≈ 4 characters.

        Args:
            messages: List of message dicts with role and content

        Returns:
            Estimated token count
        """
        total_chars = 0

        for msg in messages:
            content = msg.get("content", "")

            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        # Tool result or text/thinking block
                        if "content" in block:
                            total_chars += len(str(block["content"]))
                        if "text" in block:
                            total_chars += len(block["text"])
                        if "thinking" in block:
                            total_chars += len(block["thinking"])
                        if "input" in block:
                            total_chars += len(str(block["input"]))

        return total_chars // 4

    def _prune_old_messages(
        self,
        messages: List[Dict[str, Any]],
        min_recent_messages: int
    ) -> List[Dict[str, Any]]:
        """
        Prune old messages to keep context under threshold.

        Strategy:
        1. Always keep initial user prompt (messages[0])
        2. Keep only recent N message pairs (user + assistant)
        3. Ensure Extended Thinking format requirements are met

        Args:
            messages: Current message history
            min_recent_messages: Minimum recent messages to keep

        Returns:
            Pruned message list
        """
        if len(messages) <= min_recent_messages + 1:
            return messages

        logger.warning(
            f"Pruning old messages to keep last {min_recent_messages // 2} exchanges."
        )

        # Keep initial prompt
        initial_prompt = messages[0]

        # Search backwards for assistant message with thinking block
        recent_start_idx = len(messages) - min_recent_messages
        for i in range(len(messages) - 1, 0, -1):
            msg = messages[i]
            if msg.get("role") == "assistant":
                content = msg.get("content", [])
                if isinstance(content, list) and len(content) > 0:
                    first_block = content[0]
                    if isinstance(first_block, dict) and first_block.get("type") == "thinking":
                        recent_start_idx = i
                        break

        # Keep initial + recent messages
        pruned = [initial_prompt] + messages[recent_start_idx:]
        logger.info(f"Kept {len(pruned)} messages after pruning")

        return pruned


__all__ = ["ClaudeProvider"]
