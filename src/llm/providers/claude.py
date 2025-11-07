"""
Claude (Anthropic) LLM provider.
"""

import os
import logging
from typing import List, Dict, Any
from anthropic import Anthropic

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


__all__ = ["ClaudeProvider"]
