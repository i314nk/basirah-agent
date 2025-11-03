"""
Arabic translation module for investment theses.

This module provides translation of investment theses from English to Arabic
using Claude API, with proper RTL formatting and preservation of key terms.
"""

from anthropic import Anthropic
import os
from typing import Dict

class ThesisTranslator:
    """Translates investment theses to Arabic with proper formatting."""

    def __init__(self):
        """Initialize the translator with Claude API."""
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-5-20250929"

    def translate_to_arabic(self, thesis: str, ticker: str) -> Dict[str, any]:
        """
        Translate an investment thesis to Arabic.

        Args:
            thesis: The English investment thesis
            ticker: The stock ticker (for context)

        Returns:
            dict with:
                - translated_thesis: Arabic translation
                - input_tokens: Tokens used for input
                - output_tokens: Tokens used for output
                - cost: Translation cost in USD
        """

        # Create translation prompt
        prompt = f"""Please translate the following investment thesis about {ticker} to Arabic.

IMPORTANT INSTRUCTIONS:
1. Translate the content naturally to Arabic while preserving the tone and style
2. Keep all company names, ticker symbols, and proper nouns in English
3. Keep all numbers, percentages, and dollar amounts exactly as is
4. Keep financial terms that are commonly used in English (e.g., "P/E ratio", "DCF", "ROIC")
5. Keep Warren Buffett's name in English
6. Preserve all section headings and structure
7. Use formal Arabic suitable for financial analysis

THESIS TO TRANSLATE:

{thesis}

Please provide ONLY the Arabic translation without any explanations or notes."""

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            temperature=0.3,  # Lower temperature for more consistent translation
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract translation
        translated_thesis = response.content[0].text

        # Calculate cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        input_cost = (input_tokens / 1000) * 0.01
        output_cost = (output_tokens / 1000) * 0.30
        total_cost = input_cost + output_cost

        return {
            "translated_thesis": translated_thesis,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": round(total_cost, 2)
        }
