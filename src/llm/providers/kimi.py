"""
Kimi K2 (Moonshot AI) LLM provider.

Uses OpenAI-compatible API for native tool calling.
"""

import os
import logging
from typing import List, Dict, Any, Callable
from openai import OpenAI

from src.llm.base import BaseLLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class KimiProvider(BaseLLMProvider):
    """
    Provider for Kimi K2 models via Moonshot AI API.

    Supported models:
    - kimi-k2-thinking (Best reasoning, slower)
    - kimi-k2-thinking-turbo (Fast reasoning)
    - kimi-k2-turbo-preview (Fast, less reasoning)
    """

    # Model configurations
    MODEL_CONFIGS = {
        "kimi-k2-thinking": {
            "temperature": 1.0,  # Recommended for thinking models
            "description": "Best reasoning quality, slower"
        },
        "kimi-k2-thinking-turbo": {
            "temperature": 1.0,
            "description": "Fast reasoning with good quality"
        },
        "kimi-k2-turbo-preview": {
            "temperature": 0.6,  # Recommended for non-thinking models
            "description": "Fastest, less reasoning"
        }
    }

    # Cost per 1M tokens (estimated - update with actual pricing)
    COSTS = {
        "kimi-k2-thinking": {"input": 2.0, "output": 10.0},
        "kimi-k2-thinking-turbo": {"input": 1.5, "output": 7.5},
        "kimi-k2-turbo-preview": {"input": 1.0, "output": 5.0}
    }

    def __init__(self, model_name: str, **kwargs):
        """Initialize Kimi provider."""
        super().__init__(model_name, **kwargs)

        self.model_id = model_name

        # Initialize OpenAI client with Kimi API
        api_key = os.getenv("KIMI_API_KEY")
        if not api_key:
            raise ValueError("KIMI_API_KEY environment variable not set")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.ai/v1"
        )

        # Get model config
        self.model_config = self.MODEL_CONFIGS.get(
            model_name,
            {"temperature": 0.6, "description": "Unknown model"}
        )

        logger.info(f"Initialized KimiProvider with model: {self.model_id}")

    def generate(
        self,
        messages: List[LLMMessage],
        max_tokens: int = 16000,
        temperature: float = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response from Kimi."""

        # Use model-specific temperature if not provided
        if temperature is None:
            temperature = self.model_config["temperature"]

        # Convert messages to OpenAI format
        formatted_messages = []

        for msg in messages:
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })

        try:
            # Call Kimi API (OpenAI-compatible)
            response = self.client.chat.completions.create(
                model=self.model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=formatted_messages
            )

            # Extract response
            content = response.choices[0].message.content
            tokens_input = response.usage.prompt_tokens
            tokens_output = response.usage.completion_tokens

            # Calculate cost
            cost = self.calculate_cost(tokens_input, tokens_output)

            return LLMResponse(
                content=content,
                model=self.model_id,
                provider="kimi",
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost=cost,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "model_version": self.model_id
                }
            )

        except Exception as e:
            logger.error(f"Kimi API error: {e}")
            raise

    def is_available(self) -> bool:
        """Check if Kimi API is available."""
        try:
            return bool(os.getenv("KIMI_API_KEY"))
        except:
            return False

    def get_cost_per_token(self) -> Dict[str, float]:
        """Get cost per token for Kimi model."""
        costs = self.COSTS.get(
            self.model_id,
            {"input": 1.5, "output": 7.5}  # Default pricing
        )

        # Convert from per 1M tokens to per token
        return {
            "input": costs["input"] / 1_000_000,
            "output": costs["output"] / 1_000_000
        }

    def _convert_tools_to_openai_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert Claude tool format to OpenAI/Kimi format.

        Claude format:
        {
            "name": "tool_name",
            "description": "...",
            "input_schema": {...}
        }

        OpenAI/Kimi format:
        {
            "type": "function",
            "function": {
                "name": "tool_name",
                "description": "...",
                "parameters": {...}
            }
        }

        Kimi builtin_function format (passed through unchanged):
        {
            "type": "builtin_function",
            "function": {
                "name": "$web_search"
            }
        }

        Args:
            tools: Tools in Claude format or Kimi builtin_function format

        Returns:
            Tools in OpenAI/Kimi format
        """
        openai_tools = []

        for tool in tools:
            # Check if this is already a Kimi builtin function (e.g., $web_search)
            if tool.get("type") == "builtin_function":
                # Pass through unchanged - it's already in the correct format
                openai_tools.append(tool)
                logger.debug(f"Passing through builtin function: {tool.get('function', {}).get('name', 'unknown')}")
            else:
                # Convert from Claude format to OpenAI function format
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.get("name"),
                        "description": tool.get("description"),
                        "parameters": tool.get("input_schema", {})
                    }
                }
                openai_tools.append(openai_tool)

        return openai_tools

    def run_react_loop(
        self,
        system_prompt: str,
        initial_message: str,
        tools: List[Dict[str, Any]],
        tool_executor: Callable[[str, Dict[str, Any]], Dict[str, Any]],
        max_iterations: int = 30,
        max_tokens: int = 32000,
        thinking_budget: int = None  # Not used by Kimi but kept for interface compatibility
    ) -> Dict[str, Any]:
        """
        Run Kimi-native ReAct loop with OpenAI-compatible tool calling.

        Uses Kimi's native tool calling API (OpenAI-compatible format).

        Args:
            system_prompt: System prompt defining agent personality/task
            initial_message: Initial user message to start analysis
            tools: List of tool definitions in Claude format (will be converted)
            tool_executor: Callback function(tool_name, tool_input) -> result dict
            max_iterations: Maximum ReAct iterations (default 30)
            max_tokens: Maximum tokens per response (default 32000)
            thinking_budget: Ignored (for interface compatibility)

        Returns:
            Dict with:
                - success: bool - Whether analysis completed successfully
                - thesis: str - Final analysis text from agent
                - metadata: dict - Usage stats (iterations, tool_calls, tokens, cost)
        """
        # Convert tools to OpenAI/Kimi format
        openai_tools = self._convert_tools_to_openai_format(tools)

        # Build initial messages (Kimi doesn't accept empty system messages)
        messages = []
        if system_prompt and system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": initial_message})

        tool_calls_made = 0
        iteration = 0

        # Token tracking
        total_input_tokens = 0
        total_output_tokens = 0

        # Get recommended temperature for this model
        temperature = self.model_config["temperature"]

        logger.info(f"Starting Kimi ReAct loop (max {max_iterations} iterations)")
        logger.info(f"Using temperature: {temperature}")

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"\n--- Iteration {iteration} ---")

            try:
                # Call Kimi with tool calling (streaming recommended for large responses)
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=messages,
                    tools=openai_tools,  # Use converted tools
                    tool_choice="auto"
                )

                # Extract response
                choice = response.choices[0]
                message = choice.message

                # Track tokens
                total_input_tokens += response.usage.prompt_tokens
                total_output_tokens += response.usage.completion_tokens

                logger.debug(
                    f"Tokens - Input: {response.usage.prompt_tokens}, "
                    f"Output: {response.usage.completion_tokens}"
                )

                # Add assistant's response to conversation
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": message.tool_calls if message.tool_calls else None
                })

                # Check if agent used tools
                if message.tool_calls:
                    logger.info(f"Agent requested {len(message.tool_calls)} tool calls")

                    for tool_call in message.tool_calls:
                        tool_calls_made += 1

                        tool_name = tool_call.function.name
                        # Parse JSON arguments safely
                        import json
                        tool_args = json.loads(tool_call.function.arguments)

                        logger.info(f"[Tool Call] {tool_name}")

                        # Handle Kimi native web search specially
                        if tool_name == "$web_search":
                            # Kimi builtin web search - just pass arguments back as-is
                            # Kimi executes search internally
                            logger.info(f"[Kimi Native Web Search] Query: {tool_args.get('query', 'N/A')}")

                            # Log token usage for web search results
                            search_tokens = tool_args.get("usage", {}).get("total_tokens", 0)
                            if search_tokens > 0:
                                logger.info(f"[Web Search] Will use ~{search_tokens} tokens for results")

                            # Pass arguments back unchanged (Kimi handles execution)
                            result_content = json.dumps(tool_args)
                        else:
                            # Regular tool - execute it
                            logger.debug(f"Arguments: {tool_args}")
                            result = tool_executor(tool_name, tool_args)
                            result_content = str(result)

                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": result_content
                        })

                    # Continue loop (agent will process results)
                    continue

                # No tool calls - agent has finished
                final_text = message.content or ""

                logger.info(f"Agent finished after {tool_calls_made} tool calls")

                # Calculate costs (total and breakdown)
                cost_per_token = self.get_cost_per_token()
                input_cost = total_input_tokens * cost_per_token["input"]
                output_cost = total_output_tokens * cost_per_token["output"]
                total_cost = input_cost + output_cost

                return {
                    "success": True,
                    "thesis": final_text.strip(),
                    "metadata": {
                        "iterations": iteration,
                        "tool_calls": tool_calls_made,
                        "tokens_input": total_input_tokens,
                        "tokens_output": total_output_tokens,
                        "input_cost": input_cost,
                        "output_cost": output_cost,
                        "cost": total_cost
                    }
                }

            except Exception as e:
                logger.error(f"Error in Kimi ReAct loop: {e}", exc_info=True)
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


__all__ = ["KimiProvider"]
