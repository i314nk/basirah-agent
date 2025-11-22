"""
LLM Factory for creating and managing LLM providers.
"""

import os
import logging
from typing import Optional, Dict, Any, List

from src.llm.base import BaseLLMProvider, LLMProvider, LLMMessage, LLMResponse
from src.llm.config import LLMConfig
from src.llm.providers.claude import ClaudeProvider
from src.llm.providers.kimi import KimiProvider

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory for creating LLM provider instances.

    Handles provider selection, initialization, and fallback logic.
    """

    # Provider class mapping
    PROVIDER_CLASSES = {
        LLMProvider.CLAUDE: ClaudeProvider,
        LLMProvider.KIMI: KimiProvider
    }

    @classmethod
    def create_provider(
        cls,
        model_key: Optional[str] = None,
        **kwargs
    ) -> BaseLLMProvider:
        """
        Create LLM provider instance.

        Args:
            model_key: Model key from LLMConfig (e.g., "claude-sonnet-4.5")
            **kwargs: Additional provider-specific configuration

        Returns:
            Initialized LLM provider

        Raises:
            ValueError: If model not found
            RuntimeError: If provider initialization fails
        """
        # Get model key from env if not provided
        if model_key is None:
            model_key = LLMConfig.get_default_model()

        # Resolve alias if needed
        original_key = model_key
        try:
            model_key = LLMConfig.resolve_model_key(model_key)
            if model_key != original_key:
                logger.info(f"Resolved alias '{original_key}' -> '{model_key}'")
        except ValueError as e:
            logger.error(f"Invalid model key: {original_key}")
            raise

        logger.info(f"Creating LLM provider for model: {model_key}")

        # Get model configuration
        try:
            model_config = LLMConfig.get_model_config(model_key)
        except ValueError as e:
            logger.error(f"Failed to get config for: {model_key}")
            raise

        # Get provider class
        provider_type = model_config["provider"]
        provider_class = cls.PROVIDER_CLASSES.get(provider_type)

        if not provider_class:
            raise ValueError(f"Unknown provider type: {provider_type}")

        # Initialize provider
        try:
            model_id = model_config["model_id"]
            # Pass model_name as keyword argument to avoid conflicts
            provider = provider_class(model_name=model_id, **kwargs)

            # Check if provider is available
            if not provider.is_available():
                raise RuntimeError(
                    f"Provider {provider_type} not available. "
                    f"Check configuration and dependencies."
                )

            logger.info(
                f"Successfully created {provider_type} provider "
                f"with model {model_id}"
            )

            return provider

        except Exception as e:
            logger.error(f"Failed to create provider: {e}")
            raise

    @classmethod
    def create_with_fallback(
        cls,
        primary_model: str,
        fallback_models: Optional[List[str]] = None,
        **kwargs
    ) -> BaseLLMProvider:
        """
        Create provider with automatic fallback.

        Tries primary model first, falls back to alternatives if unavailable.

        Args:
            primary_model: Primary model to try
            fallback_models: List of fallback models (optional)
            **kwargs: Provider configuration

        Returns:
            First available provider
        """
        models_to_try = [primary_model]

        if fallback_models:
            models_to_try.extend(fallback_models)

        last_error = None

        for model_key in models_to_try:
            try:
                logger.info(f"Attempting to create provider for: {model_key}")
                return cls.create_provider(model_key, **kwargs)
            except Exception as e:
                logger.warning(f"Failed to create {model_key}: {e}")
                last_error = e
                continue

        # All providers failed
        raise RuntimeError(
            f"Failed to create any provider. Tried: {models_to_try}. "
            f"Last error: {last_error}"
        )

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of currently available providers.

        Returns:
            List of model keys that are available
        """
        available = []

        for model_key in LLMConfig.MODELS.keys():
            try:
                provider = cls.create_provider(model_key)
                if provider.is_available():
                    available.append(model_key)
            except:
                continue

        return available


class LLMClient:
    """
    High-level LLM client with automatic provider management.

    This is the main interface that basīrah agents should use.
    """

    def __init__(self, model_key: Optional[str] = None, **kwargs):
        """
        Initialize LLM client.

        Args:
            model_key: Model to use (defaults to LLM_MODEL env var)
            **kwargs: Provider configuration
        """
        self.model_key = model_key or LLMConfig.get_default_model()
        self.provider = LLMFactory.create_provider(self.model_key, **kwargs)

        logger.info(f"LLMClient initialized with {self.model_key}")

    def generate(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 16000,
        temperature: float = 1.0,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response from LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse with generated content
        """
        # Convert dict messages to LLMMessage objects
        llm_messages = [
            LLMMessage(role=msg["role"], content=msg["content"])
            for msg in messages
        ]

        return self.provider.generate(
            llm_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about current provider."""
        config = LLMConfig.get_model_config(self.model_key)
        return {
            "model_key": self.model_key,
            "provider": self.provider.provider_name,
            "model_id": self.provider.model_name,
            "description": config.get("description"),
            "cost": config.get("cost"),
            "quality": config.get("quality"),
            "knowledge_cutoff": config.get("knowledge_cutoff", "Unknown")
        }


__all__ = ["LLMFactory", "LLMClient"]
