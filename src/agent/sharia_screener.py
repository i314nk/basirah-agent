"""
Sharia Compliance Screening Module

Analyzes companies for Islamic finance compliance according to AAOIFI standards.
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()

logger = logging.getLogger(__name__)


class ShariaScreener:
    """
    Analyzes companies for Sharia (Islamic law) compliance.

    Uses AAOIFI (Accounting and Auditing Organization for Islamic
    Financial Institutions) standards for screening.
    """

    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 16000  # Must be > thinking budget (10000)
    THINKING_BUDGET = 10000

    # AAOIFI Financial Ratio Thresholds
    DEBT_THRESHOLD = 0.30  # Debt/Market Cap < 30%
    CASH_THRESHOLD = 0.30  # (Cash + Interest Securities)/Market Cap < 30%
    AR_THRESHOLD = 0.50    # Accounts Receivable/Market Cap < 50%
    INTEREST_INCOME_THRESHOLD = 0.05  # Interest Income/Revenue < 5%

    # Prohibited Business Activities
    PROHIBITED_ACTIVITIES = [
        "alcohol production or distribution",
        "gambling or casino operations",
        "pork products",
        "conventional banking (interest-based)",
        "pornography or adult entertainment",
        "tobacco",
        "weapons or defense (per some scholars)",
        "music or entertainment (strict interpretation)"
    ]

    def __init__(self, api_key: str = None):
        """
        Initialize Sharia screener.

        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.info("ShariaScreener initialized")

    def screen_company(self, ticker: str) -> Dict[str, Any]:
        """
        Perform complete Sharia compliance screening.

        Args:
            ticker: Stock ticker symbol

        Returns:
            {
                "ticker": str,
                "status": "COMPLIANT" | "DOUBTFUL" | "NON-COMPLIANT",
                "analysis": str,  # Full markdown analysis
                "business_activity_status": str,
                "financial_ratios_status": str,
                "purification_rate": float,  # % of dividends to donate
                "suitable_for": list,  # Types of investors
                "metadata": dict
            }
        """
        logger.info(f"Starting Sharia screening for {ticker}")

        prompt = self._build_sharia_screening_prompt(ticker)

        try:
            # Track tokens
            total_input_tokens = 0
            total_output_tokens = 0

            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=self.MAX_TOKENS,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                thinking={
                    "type": "enabled",
                    "budget_tokens": self.THINKING_BUDGET
                }
            )

            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens

            # Extract analysis (Extended Thinking separates thinking from output)
            analysis_text = ""
            for block in response.content:
                if block.type == "text":
                    analysis_text += block.text

            # Parse status and purification rate from response
            status = self._extract_status(analysis_text)
            purification_rate = self._extract_purification_rate(analysis_text)

            # Calculate cost
            input_cost = (total_input_tokens / 1000) * 0.01
            output_cost = (total_output_tokens / 1000) * 0.30
            total_cost = input_cost + output_cost

            logger.info(
                f"Sharia screening complete for {ticker}: {status}, "
                f"purification {purification_rate:.1f}%, cost ${total_cost:.2f}"
            )

            return {
                "ticker": ticker,
                "status": status,
                "analysis": analysis_text,
                "purification_rate": purification_rate,
                "metadata": {
                    "analysis_date": datetime.now().isoformat(),
                    "standard": "AAOIFI",
                    "token_usage": {
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                        "input_cost": round(input_cost, 2),
                        "output_cost": round(output_cost, 2),
                        "total_cost": round(total_cost, 2)
                    }
                }
            }

        except Exception as e:
            logger.error(f"Sharia screening failed for {ticker}: {e}")
            return {
                "ticker": ticker,
                "status": "ERROR",
                "analysis": f"Screening failed: {str(e)}",
                "purification_rate": 0.0,
                "metadata": {
                    "error": str(e)
                }
            }

    def _build_sharia_screening_prompt(self, ticker: str) -> str:
        """Build comprehensive Sharia screening prompt."""

        return f"""You are a Sharia compliance analyst specializing in Islamic finance.
Analyze {ticker} for Sharia (Islamic law) compliance according to AAOIFI standards.

**CRITICAL INSTRUCTION:**
Your response must start IMMEDIATELY with the formatted analysis output shown below.
Do NOT write any preamble, thinking process, or explanatory text before the analysis.
Do NOT show tool usage or data gathering steps.
Jump straight to: "# SHARIA COMPLIANCE ANALYSIS - {ticker}"

**YOUR ANALYSIS PROCESS:**

**PHASE 1: BUSINESS ACTIVITY SCREENING**

Research the company's business from their most recent 10-K annual report:
- What is the company's primary business?
- What are all revenue sources (with % breakdown if available)?
- Are any activities from the prohibited list below?

**Prohibited Business Activities (AAOIFI):**
{chr(10).join(f"- {activity}" for activity in self.PROHIBITED_ACTIVITIES)}

**Compliance Levels:**
- ✅ **COMPLIANT:** 0% revenue from prohibited activities
- ⚠️ **DOUBTFUL:** <5% revenue from prohibited activities (requires purification)
- ❌ **NON-COMPLIANT:** ≥5% revenue from prohibited activities

**PHASE 2: FINANCIAL RATIO SCREENING**

Gather financial data and calculate these ratios:

**AAOIFI Financial Thresholds:**
1. **Debt / Market Capitalization** < {self.DEBT_THRESHOLD * 100}%
2. **(Cash + Interest-bearing Securities) / Market Cap** < {self.CASH_THRESHOLD * 100}%
3. **Accounts Receivable / Market Cap** < {self.AR_THRESHOLD * 100}%
4. **Interest Income / Total Revenue** < {self.INTEREST_INCOME_THRESHOLD * 100}%

All four ratios must pass for compliance.

**PHASE 3: PURIFICATION CALCULATION**

If company has minor non-compliant income (<5%):
- Calculate % of revenue from prohibited sources
- Calculate % of interest income
- Total = Purification Rate (what % of dividends to donate to charity)

**YOUR OUTPUT:**

IMPORTANT: Start your response directly with the analysis below. Do NOT include any
preamble, thinking process, or tool usage descriptions. Jump straight to the formatted analysis.

Provide a comprehensive Sharia compliance analysis in this format:

---

# SHARIA COMPLIANCE ANALYSIS - {ticker}

**Status:** [✅ COMPLIANT / ⚠️ DOUBTFUL / ❌ NON-COMPLIANT]
**Purification Required:** [Yes/No] ([X.X]% if applicable)
**Analysis Date:** {datetime.now().strftime('%B %d, %Y')}
**Standard:** AAOIFI Guidelines

---

## 1. Business Activity Review

**Primary Business:**
[What does the company do? 2-3 sentences]

**Revenue Breakdown (Most Recent Year):**
- [Revenue source 1]: X% ($XXB)
- [Revenue source 2]: X% ($XXB)
- [Continue for major segments]

**Sharia Compliance Assessment:**

[For each revenue source, assess:]
✅ **[Segment Name] (X%):** COMPLIANT
   - [Brief explanation why permissible]

OR

⚠️ **[Segment Name] (X%):** DOUBTFUL
   - [Brief explanation of concern]
   - [Scholarly opinion if relevant]

OR

❌ **[Segment Name] (X%):** NON-COMPLIANT
   - [Brief explanation why prohibited]

**Business Activity Verdict:** [✅ Compliant / ⚠️ Substantially Compliant / ❌ Non-Compliant]
[2-3 sentences explaining overall assessment]

---

## 2. Financial Ratios Screening

[Use actual calculated values for the company]

| Ratio | Value | AAOIFI Threshold | Status |
|-------|-------|------------------|--------|
| **Debt / Market Cap** | X.X% | < 30% | [✅/❌] |
| **Cash / Market Cap** | X.X% | < 30% | [✅/❌] |
| **AR / Market Cap** | X.X% | < 50% | [✅/❌] |
| **Interest Income / Revenue** | X.X% | < 5% | [✅/❌] |

**Financial Ratios Verdict:** [✅ All Pass / ❌ Some Fail]

**Notes on Ratios:**
[2-3 sentences explaining any concerns or notable observations]

---

## 3. Overall Sharia Compliance

**FINAL STATUS: [✅ COMPLIANT / ⚠️ DOUBTFUL / ❌ NON-COMPLIANT]**

[3-4 paragraphs explaining:]
- Overall assessment combining business activity + financial ratios
- Why this classification was assigned
- Key concerns or positive factors
- Scholarly opinions if relevant

**Purification Requirement:**

IF status is DOUBTFUL:
**Purification Rate: X.X% of dividends**

Breakdown:
- Non-compliant business income: X.X%
- Interest income: X.X%
- **Total purification rate: X.X%**

**Example:** For every $100 in dividends received, donate $X.XX to charity.

IF status is COMPLIANT:
**No purification required** - Business is fully compliant with AAOIFI standards.

IF status is NON-COMPLIANT:
**Not suitable for Sharia-compliant portfolios** - Purification does not apply as
non-compliant income exceeds acceptable thresholds.

---

## 4. Investment Suitability

**Who This Is Suitable For:**

[Based on status:]

IF COMPLIANT:
✅ All Muslim investors (strict and moderate)
✅ Sharia-compliant funds
✅ Conservative investors seeking zero non-compliant income

IF DOUBTFUL:
✅ Moderate Muslim investors (majority scholarly opinion)
✅ Investors following AAOIFI standards
⚠️ May not suit strict/conservative interpretations
⚠️ Requires dividend purification

IF NON-COMPLIANT:
❌ Not suitable for Sharia-compliant portfolios
❌ Exceeds AAOIFI thresholds
❌ Alternative halal investments recommended

**Alternative Considerations:**
[Suggest 2-3 similar companies with better Sharia compliance if current is doubtful/non-compliant]

---

## 5. Scholarly References & Disclaimer

**Standards Applied:**
- AAOIFI Sharia Standard No. 21 (Financial Papers - Shares)
- AAOIFI Sharia Standard No. 6 (Conversion of Conventional Bank)
- Majority scholarly opinion from AAOIFI Sharia Board

**Important Notes:**
1. This analysis follows mainstream AAOIFI standards
2. Some scholars may have stricter interpretations
3. Purification rates are approximations based on public data
4. Business activities may change - review annually

**Disclaimer:**
This is an educational analysis based on publicly available data and mainstream
Islamic finance principles. It is NOT a fatwa (religious ruling). Individual
investors should consult qualified Islamic scholars for personalized guidance
based on their specific circumstances and interpretation.

---

**STATUS: [{ticker} STATUS]**
**PURIFICATION RATE: [X.X]%** (if applicable)

---

*Analysis generated by basīrah - Warren Buffett AI with Sharia Screening*

---

**CRITICAL REQUIREMENTS:**

1. **NO THINKING PROCESS** - Your output should start directly with "# SHARIA COMPLIANCE ANALYSIS"
2. **Use actual data** - Calculate real ratios with current financial information
3. **Be specific** - Don't say "alcohol may be involved" - find out yes/no
4. **Be balanced** - Present both strict and lenient scholarly views when relevant
5. **Be educational** - Explain WHY something is compliant/non-compliant
6. **Be accurate** - This affects people's religious obligations
7. **Be respectful** - This is about faith, not just finance

Now perform the complete Sharia compliance screening for {ticker}.
"""

    def _extract_status(self, text: str) -> str:
        """Extract compliance status from analysis text."""
        text_upper = text.upper()

        if '❌ NON-COMPLIANT' in text or 'STATUS: NON-COMPLIANT' in text_upper:
            return "NON-COMPLIANT"
        elif '⚠️ DOUBTFUL' in text or 'STATUS: DOUBTFUL' in text_upper:
            return "DOUBTFUL"
        elif '✅ COMPLIANT' in text or 'STATUS: COMPLIANT' in text_upper:
            return "COMPLIANT"
        else:
            return "UNCLEAR"

    def _extract_purification_rate(self, text: str) -> float:
        """Extract purification rate from analysis text."""
        import re

        # Look for patterns like "PURIFICATION RATE: 2.3%"
        patterns = [
            r'PURIFICATION RATE:\s*(\d+\.?\d*)%',
            r'purification rate:\s*(\d+\.?\d*)%',
            r'Total purification rate:\s*(\d+\.?\d*)%'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue

        return 0.0


__all__ = ["ShariaScreener"]
