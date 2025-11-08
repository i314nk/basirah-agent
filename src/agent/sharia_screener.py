"""
Sharia Compliance Screening Module

Analyzes companies for Islamic finance compliance according to AAOIFI standards.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
import anthropic

from src.tools.calculator_tool import CalculatorTool
from src.tools.gurufocus_tool import GuruFocusTool
from src.tools.web_search_tool import WebSearchTool
from src.tools.sec_filing_tool import SECFilingTool

load_dotenv()

logger = logging.getLogger(__name__)


class ShariaScreener:
    """
    Analyzes companies for Sharia (Islamic law) compliance.

    Uses AAOIFI (Accounting and Auditing Organization for Islamic
    Financial Institutions) standards for screening.
    """

    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 8000  # Response limit (reduced to allow larger filings in context)
    THINKING_BUDGET = 6000  # Extended thinking budget (must be < MAX_TOKENS)
    MAX_ITERATIONS = 15  # Maximum tool call iterations

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

        # Initialize all 4 tools for data gathering
        logger.info("Initializing tools...")
        self.tools = {
            "calculator": CalculatorTool(),
            "gurufocus": GuruFocusTool(),
            "web_search": WebSearchTool(),
            "sec_filing": SECFilingTool()
        }
        logger.info(f"ShariaScreener initialized with {len(self.tools)} tools")

    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Convert tools to Claude API format.

        Returns:
            List of tool definitions for Claude API
        """
        return [
            {
                "name": "gurufocus_tool",
                "description": self.tools["gurufocus"].description,
                "input_schema": self.tools["gurufocus"].parameters
            },
            {
                "name": "sec_filing_tool",
                "description": self.tools["sec_filing"].description,
                "input_schema": self.tools["sec_filing"].parameters
            },
            {
                "name": "web_search_tool",
                "description": self.tools["web_search"].description,
                "input_schema": self.tools["web_search"].parameters
            },
            {
                "name": "calculator_tool",
                "description": self.tools["calculator"].description,
                "input_schema": self.tools["calculator"].parameters
            }
        ]

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool and return results.

        Args:
            tool_name: Name of tool to execute
            tool_input: Parameters for tool

        Returns:
            dict: Tool execution result
        """
        # Map tool names to tool instances
        tool_map = {
            "gurufocus_tool": "gurufocus",
            "sec_filing_tool": "sec_filing",
            "web_search_tool": "web_search",
            "calculator_tool": "calculator"
        }

        tool_key = tool_map.get(tool_name)
        if not tool_key:
            logger.error(f"Unknown tool: {tool_name}")
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "data": None
            }

        tool = self.tools[tool_key]

        logger.info(f"Executing {tool_name}")
        logger.debug(f"Parameters: {tool_input}")

        try:
            result = tool.execute(**tool_input)
            if result.get('success'):
                logger.info(f"{tool_name} succeeded")
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.warning(f"{tool_name} failed: {error_msg}")
            return result
        except Exception as e:
            logger.error(f"{tool_name} execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    def screen_company(self, ticker: str) -> Dict[str, Any]:
        """
        Perform complete Sharia compliance screening using ReAct loop with tools.

        Args:
            ticker: Stock ticker symbol

        Returns:
            {
                "ticker": str,
                "status": "COMPLIANT" | "DOUBTFUL" | "NON-COMPLIANT",
                "analysis": str,  # Full markdown analysis
                "purification_rate": float,  # % of dividends to donate
                "metadata": dict
            }
        """
        logger.info(f"Starting Sharia screening for {ticker}")

        prompt = self._build_sharia_screening_prompt(ticker)

        try:
            # Track tokens and tool calls
            total_input_tokens = 0
            total_output_tokens = 0
            tool_calls_made = 0

            # Initialize conversation
            messages = [{
                "role": "user",
                "content": prompt
            }]

            # ReAct loop - agent gathers data using tools, then provides analysis
            for iteration in range(self.MAX_ITERATIONS):
                logger.info(f"Iteration {iteration + 1}/{self.MAX_ITERATIONS}")

                response = self.client.messages.create(
                    model=self.MODEL,
                    max_tokens=self.MAX_TOKENS,
                    messages=messages,
                    tools=self._get_tool_definitions(),
                    thinking={
                        "type": "enabled",
                        "budget_tokens": self.THINKING_BUDGET
                    }
                )

                total_input_tokens += response.usage.input_tokens
                total_output_tokens += response.usage.output_tokens

                # Check stop reason
                stop_reason = response.stop_reason

                # Extract content blocks
                assistant_content = []
                tool_uses = []

                for block in response.content:
                    if block.type == "thinking":
                        # Include signature if present (required for Extended Thinking)
                        thinking_block = {
                            "type": "thinking",
                            "thinking": block.thinking
                        }
                        if hasattr(block, 'signature') and block.signature:
                            thinking_block["signature"] = block.signature
                        assistant_content.append(thinking_block)
                    elif block.type == "text":
                        assistant_content.append({
                            "type": "text",
                            "text": block.text
                        })
                    elif block.type == "tool_use":
                        assistant_content.append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        })
                        tool_uses.append(block)

                # Add assistant's response to conversation
                messages.append({
                    "role": "assistant",
                    "content": assistant_content
                })

                # If agent finished (no tool use), extract final analysis
                if stop_reason == "end_turn":
                    logger.info("Agent finished screening")

                    # Extract analysis text
                    analysis_text = ""
                    for block in response.content:
                        if block.type == "text":
                            analysis_text += block.text

                    # Parse status and purification rate
                    status = self._extract_status(analysis_text)
                    purification_rate = self._extract_purification_rate(analysis_text)

                    # Calculate cost
                    input_cost = (total_input_tokens / 1000) * 0.01
                    output_cost = (total_output_tokens / 1000) * 0.30
                    total_cost = input_cost + output_cost

                    logger.info(
                        f"Sharia screening complete for {ticker}: {status}, "
                        f"purification {purification_rate:.1f}%, "
                        f"{tool_calls_made} tool calls, cost ${total_cost:.2f}"
                    )

                    return {
                        "ticker": ticker,
                        "status": status,
                        "analysis": analysis_text,
                        "purification_rate": purification_rate,
                        "metadata": {
                            "analysis_date": datetime.now().isoformat(),
                            "standard": "AAOIFI",
                            "tool_calls_made": tool_calls_made,
                            "token_usage": {
                                "input_tokens": total_input_tokens,
                                "output_tokens": total_output_tokens,
                                "input_cost": round(input_cost, 2),
                                "output_cost": round(output_cost, 2),
                                "total_cost": round(total_cost, 2)
                            }
                        }
                    }

                # If agent used tools, execute them
                if tool_uses:
                    tool_results = []

                    for tool_use in tool_uses:
                        tool_calls_made += 1
                        result = self._execute_tool(
                            tool_use.name,
                            tool_use.input
                        )

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

                    # Continue loop to next iteration
                    continue

                # If neither end_turn nor tool_use, something unexpected happened
                logger.warning(f"Unexpected stop reason: {stop_reason}")
                break

            # If we hit max iterations
            logger.warning(f"Reached max iterations ({self.MAX_ITERATIONS})")

            return {
                "ticker": ticker,
                "status": "ERROR",
                "analysis": f"Screening incomplete - reached maximum iterations ({self.MAX_ITERATIONS})",
                "purification_rate": 0.0,
                "metadata": {
                    "error": "max_iterations_reached"
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

**CRITICAL INSTRUCTIONS:**

1. **USE TOOLS TO GATHER LIVE DATA** - You have access to 4 tools:
   - sec_filing_tool: Fetch actual 10-K annual reports from SEC EDGAR
   - gurufocus_tool: Get real-time financial metrics and ratios
   - web_search_tool: Search for recent news or business changes
   - calculator_tool: Perform accurate calculations

2. **DO NOT RELY ON TRAINING DATA** - Your training data is outdated. You MUST use tools to:
   - Fetch the latest 10-K filing to understand current business segments
   - Get current market cap, debt, cash, and receivables
   - Calculate accurate financial ratios from live data
   - Search for any recent business changes or acquisitions

3. **GATHER DATA FIRST, THEN ANALYZE** - Follow this sequence STRICTLY:
   a) Use sec_filing_tool to get latest 10-K or 20-F filing
   b) Use gurufocus_tool MULTIPLE TIMES to gather ALL required financial data
   c) ONLY after you have ALL required data, use calculator_tool ONCE to compute ratios
   d) ONLY THEN provide your final formatted analysis

4. **FINAL OUTPUT FORMAT** - After gathering all data, provide formatted analysis starting with:
   "# SHARIA COMPLIANCE ANALYSIS - {ticker}"

**YOUR ANALYSIS PROCESS:**

**PHASE 1: DATA GATHERING (USE TOOLS)**

Step 1: Fetch latest 10-K or 20-F annual report using sec_filing_tool
- Look for: Business description, revenue breakdown by segment, any prohibited activities

Step 2: Get ALL financial metrics using gurufocus_tool (make MULTIPLE calls if needed)
- REQUIRED DATA YOU MUST GATHER BEFORE USING CALCULATOR:
  * total_debt (Total interest-bearing debt)
  * total_assets (Total assets from balance sheet)
  * cash_and_liquid_assets (Cash + marketable securities)
  * market_cap (Current market capitalization)
  * accounts_receivable (Accounts receivable from balance sheet)
  * total_revenue (Total revenue)
  * interest_income (Interest income, if any)
- You may need to call gurufocus_tool with different data_type parameters (financials, summary, keyratios, valuation)
- Do NOT proceed to calculator until you have gathered ALL of the above data

Step 3: Calculate AAOIFI ratios using calculator_tool
- CRITICAL: Only call calculator_tool ONCE you have gathered ALL required fields listed above
- The calculator will reject your request if ANY field is missing
- Pass all gathered data to calculator_tool with calculation="sharia_compliance_check"

**PHASE 2: BUSINESS ACTIVITY SCREENING**

Based on data from 10-K filing:
- What is the company's primary business?
- What are all revenue sources (with % breakdown)?
- Are any activities from the prohibited list below?

**Prohibited Business Activities (AAOIFI):**
{chr(10).join(f"- {activity}" for activity in self.PROHIBITED_ACTIVITIES)}

**Compliance Levels:**
- ✅ **COMPLIANT:** 0% revenue from prohibited activities
- ⚠️ **DOUBTFUL:** <5% revenue from prohibited activities (requires purification)
- ❌ **NON-COMPLIANT:** ≥5% revenue from prohibited activities

**PHASE 3: FINANCIAL RATIO SCREENING**

Calculate these ratios using LIVE DATA from tools:

**AAOIFI Financial Thresholds:**
1. **Debt / Market Capitalization** < {self.DEBT_THRESHOLD * 100}%
2. **(Cash + Interest-bearing Securities) / Market Cap** < {self.CASH_THRESHOLD * 100}%
3. **Accounts Receivable / Market Cap** < {self.AR_THRESHOLD * 100}%
4. **Interest Income / Total Revenue** < {self.INTEREST_INCOME_THRESHOLD * 100}%

All four ratios must pass for compliance.

**PHASE 4: PURIFICATION CALCULATION**

If company has minor non-compliant income (<5%) based on actual data:
- Calculate % of revenue from prohibited sources (from 10-K)
- Calculate % of interest income (from financial data)
- Total = Purification Rate (what % of dividends to donate to charity)

**PHASE 5: PROVIDE FINAL ANALYSIS**

After gathering ALL data with tools and performing calculations, provide your comprehensive
Sharia compliance analysis in the format below.

IMPORTANT:
- Do NOT show your tool usage or thinking process in the final output
- Jump straight to the formatted analysis
- Use only ACTUAL DATA from tools, not estimates or training data
- Cite specific numbers from the 10-K and financial statements

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
