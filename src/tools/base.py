"""
Base Tool Interface for Agent

Module: src.tools.base
Purpose: Define standard interface all tools must implement
Status: Complete - Core interface
Created: 2025-10-28

This module defines the abstract base class that all agent tools must implement
to ensure consistent interaction patterns and integration with the agent framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class Tool(ABC):
    """
    Base class for all agent tools.

    Tools provide capabilities to the agent (data access, calculations, etc.)
    All tools must implement this interface for consistent agent interaction.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Tool name for agent to reference.

        Returns:
            str: Unique tool identifier (e.g., 'gurufocus_api')
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        What this tool does (for agent decision-making).

        Returns:
            str: Clear description of tool capabilities
        """
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        JSON schema for tool parameters.

        Returns:
            Dict: OpenAPI-style parameter schema
        """
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Dict containing:
                - success: bool
                - data: Any (tool-specific output)
                - error: str or None
        """
        pass


__all__ = ["Tool"]
