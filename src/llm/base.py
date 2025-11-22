"""
Base interface for LLM providers.

All LLM providers must implement this interface to ensure compatibility
with basīrah's agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class LLMProvider(str, Enum):
    """Available LLM providers."""
    CLAUDE = "claude"
    KIMI = "kimi"
    OPENAI = "openai"  # Future support


@dataclass
class LLMMessage:
    """Standard message format for all LLMs."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Standard response format from all LLMs."""
    content: str
    model: str
    provider: str
    tokens_input: int
    tokens_output: int
    cost: float
    metadata: Dict[str, Any]


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All concrete providers must implement these methods to ensure
    consistent behavior across different LLMs.
    """

    def __init__(self, model_name: str, **kwargs):
        """
        Initialize provider.

        Args:
            model_name: Name/ID of the model to use
            **kwargs: Provider-specific configuration
        """
        self.model_name = model_name
        self.config = kwargs

    @abstractmethod
    def generate(
        self,
        messages: List[LLMMessage],
        max_tokens: int = 16000,
        temperature: float = 1.0,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response from LLM.

        Args:
            messages: List of conversation messages
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            **kwargs: Provider-specific parameters

        Returns:
            LLMResponse with generated content and metadata
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if provider is available and properly configured.

        Returns:
            True if provider can be used, False otherwise
        """
        pass

    @abstractmethod
    def get_cost_per_token(self) -> Dict[str, float]:
        """
        Get cost per token for this provider/model.

        Returns:
            Dict with 'input' and 'output' cost per token
        """
        pass

    def calculate_cost(self, tokens_input: int, tokens_output: int) -> float:
        """
        Calculate cost for token usage.

        Args:
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens

        Returns:
            Total cost in USD
        """
        costs = self.get_cost_per_token()
        return (tokens_input * costs['input']) + (tokens_output * costs['output'])

    @abstractmethod
    def run_react_loop(
        self,
        system_prompt: str,
        initial_message: str,
        tools: Dict[str, Any],
        tool_executor: callable,
        max_iterations: int = 30
    ) -> Dict[str, Any]:
        """
        Run ReAct (Reasoning + Acting) loop with tool calling.

        Each provider implements this with their native tool calling protocol:
        - Claude: Extended Thinking + Native Tool Use API
        - Kimi: OpenAI-compatible tool calling
        - Others: Provider-specific implementation

        Args:
            system_prompt: System prompt defining agent personality/task
            initial_message: Initial user message to start analysis
            tools: Tool definitions in provider-specific format
            tool_executor: Callback function(tool_name, tool_input) -> result dict
            max_iterations: Maximum ReAct iterations (default 30)

        Returns:
            Dict with:
                - success: bool - Whether analysis completed successfully
                - thesis: str - Final analysis text from agent
                - metadata: dict - Usage stats (iterations, tool_calls, tokens, cost)
        """
        pass

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return self.__class__.__name__.replace("Provider", "")


__all__ = [
    "BaseLLMProvider",
    "LLMProvider",
    "LLMMessage",
    "LLMResponse"
]
