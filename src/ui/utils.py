"""
Utility functions for basīrah UI
"""

import re
from typing import Optional


def validate_ticker(ticker: str) -> bool:
    """
    Validate ticker symbol format.

    Args:
        ticker: Stock ticker symbol

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_ticker("AAPL")
        True
        >>> validate_ticker("MSFT")
        True
        >>> validate_ticker("invalid123")
        False
        >>> validate_ticker("")
        False
    """
    if not ticker:
        return False
    # Basic validation: 1-5 uppercase letters
    pattern = r'^[A-Z]{1,5}$'
    return bool(re.match(pattern, ticker))


def format_thesis(thesis: str) -> str:
    """
    Format thesis for better display.

    Args:
        thesis: Raw thesis text

    Returns:
        Formatted thesis
    """
    # Add any formatting enhancements
    return thesis


def estimate_cost(deep_dive: bool, adaptive: bool = False) -> float:
    """
    Estimate analysis cost.

    Args:
        deep_dive: Whether this is a deep dive analysis
        adaptive: Whether adaptive strategy was used

    Returns:
        Estimated cost in USD

    Examples:
        >>> estimate_cost(deep_dive=False)
        0.5
        >>> estimate_cost(deep_dive=True, adaptive=False)
        2.5
        >>> estimate_cost(deep_dive=True, adaptive=True)
        4.0
    """
    if deep_dive:
        return 4.00 if adaptive else 2.50
    else:
        return 0.50


def estimate_duration(deep_dive: bool) -> str:
    """
    Estimate analysis duration.

    Args:
        deep_dive: Whether this is a deep dive analysis

    Returns:
        Estimated duration as string

    Examples:
        >>> estimate_duration(False)
        '30-60 seconds'
        >>> estimate_duration(True)
        '5-7 minutes'
    """
    return "5-7 minutes" if deep_dive else "30-60 seconds"


def format_currency(value: Optional[float]) -> str:
    """
    Format currency value.

    Args:
        value: Currency value

    Returns:
        Formatted string

    Examples:
        >>> format_currency(123.45)
        '$123.45'
        >>> format_currency(None)
        'N/A'
    """
    if value is None:
        return "N/A"
    return f"${value:.2f}"


def format_percentage(value: Optional[float]) -> str:
    """
    Format percentage value.

    Args:
        value: Percentage as decimal (0.25 = 25%)

    Returns:
        Formatted string

    Examples:
        >>> format_percentage(0.25)
        '25.0%'
        >>> format_percentage(-0.10)
        '-10.0%'
        >>> format_percentage(None)
        'N/A'
    """
    if value is None:
        return "N/A"
    return f"{value * 100:.1f}%"


def get_decision_emoji(decision: str) -> str:
    """
    Get emoji for decision type.

    Args:
        decision: Decision type (BUY, WATCH, AVOID)

    Returns:
        Emoji string

    Examples:
        >>> get_decision_emoji("BUY")
        '✅'
        >>> get_decision_emoji("WATCH")
        '⏸️'
        >>> get_decision_emoji("AVOID")
        '🚫'
    """
    emojis = {
        "BUY": "✅",
        "WATCH": "⏸️",
        "AVOID": "🚫",
        "ERROR": "❌"
    }
    return emojis.get(decision.upper(), "❓")


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string

    Examples:
        >>> format_duration(45)
        '45s'
        >>> format_duration(125)
        '2m 5s'
        >>> format_duration(3665)
        '1h 1m 5s'
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:.0f}m {secs:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:.0f}h {minutes:.0f}m {secs:.0f}s"


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text

    Examples:
        >>> truncate_text("Hello world", 5)
        'Hello...'
        >>> truncate_text("Hello", 10)
        'Hello'
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def get_strategy_badge(strategy: str) -> str:
    """
    Get badge text for context management strategy.

    Args:
        strategy: Strategy type ('standard' or 'adaptive_summarization')

    Returns:
        Badge text

    Examples:
        >>> get_strategy_badge("standard")
        'Standard'
        >>> get_strategy_badge("adaptive_summarization")
        'Adaptive'
    """
    if strategy == "adaptive_summarization":
        return "Adaptive"
    return "Standard"
