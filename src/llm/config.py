"""
LLM configuration management.
"""

import os
from typing import Dict, Any, Optional
from enum import Enum

from src.llm.base import LLMProvider


class LLMConfig:
    """
    Centralized LLM configuration.

    Reads from environment variables and provides defaults.
    """

    # Model aliases - maps actual model names to config keys
    MODEL_ALIASES = {
        # Claude aliases
        "claude-sonnet-4-20250514": "claude-sonnet-4.5",
        "claude-3-5-sonnet-20241022": "claude-3.5-sonnet",
    }

    # Model configurations
    MODELS = {
        # Claude models (Anthropic)
        "claude-sonnet-4.5": {
            "provider": LLMProvider.CLAUDE,
            "model_id": "claude-sonnet-4-20250514",
            "description": "Claude 4 Sonnet - Best quality, realistic tests",
            "cost": "$$$ (High)",
            "speed": "Fast",
            "quality": "Excellent (95%)"
        },
        "claude-3.5-sonnet": {
            "provider": LLMProvider.CLAUDE,
            "model_id": "claude-3-5-sonnet-20241022",
            "description": "Claude 3.5 Sonnet - Previous generation",
            "cost": "$$$ (High)",
            "speed": "Fast",
            "quality": "Excellent (92%)"
        }
    }

    @classmethod
    def get_default_model(cls) -> str:
        """Get default model from environment or fallback."""
        return os.getenv("LLM_MODEL", "claude-sonnet-4.5")

    @classmethod
    def get_model_config(cls, model_key: str) -> Dict[str, Any]:
        """
        Get configuration for a model.

        Supports both config keys and actual model names via aliases.

        Args:
            model_key: Config key (e.g., "gpt-oss-cloud") or actual model name (e.g., "gpt-oss:120b-cloud")

        Returns:
            Model configuration dict

        Raises:
            ValueError: If model not found
        """
        # First try direct lookup
        if model_key in cls.MODELS:
            return cls.MODELS[model_key]

        # Try alias lookup
        if model_key in cls.MODEL_ALIASES:
            resolved_key = cls.MODEL_ALIASES[model_key]
            return cls.MODELS[resolved_key]

        # Not found - provide helpful error
        available_keys = list(cls.MODELS.keys())
        available_aliases = list(cls.MODEL_ALIASES.keys())

        raise ValueError(
            f"Unknown model: {model_key}\n"
            f"Available config keys: {available_keys}\n"
            f"Available model names: {available_aliases}"
        )

    @classmethod
    def get_fallback_models(cls, provider: LLMProvider) -> list:
        """Get fallback models for a provider."""
        fallbacks = {
            LLMProvider.CLAUDE: ["claude-sonnet-4.5", "claude-3.5-sonnet"]
        }
        return fallbacks.get(provider, [])

    @classmethod
    def list_available_models(cls) -> Dict[str, Dict[str, Any]]:
        """List all available models with their configurations."""
        return cls.MODELS

    @classmethod
    def get_recommended_models(cls) -> list:
        """Get list of recommended models."""
        return [
            key for key, config in cls.MODELS.items()
            if config.get("recommended", False)
        ]

    @classmethod
    def resolve_model_key(cls, model_key: str) -> str:
        """
        Resolve a model key or alias to the canonical config key.

        Args:
            model_key: Config key or actual model name

        Returns:
            Canonical config key

        Raises:
            ValueError: If model not found
        """
        # Direct lookup
        if model_key in cls.MODELS:
            return model_key

        # Alias lookup
        if model_key in cls.MODEL_ALIASES:
            return cls.MODEL_ALIASES[model_key]

        # Not found
        raise ValueError(
            f"Unknown model: {model_key}\n"
            f"Available: {list(cls.MODELS.keys())}\n"
            f"Aliases: {list(cls.MODEL_ALIASES.keys())}"
        )


__all__ = ["LLMConfig"]
