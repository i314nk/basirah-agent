"""
Sharia Compliance Screening Module

Analyzes companies for Islamic finance compliance according to AAOIFI standards.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

from src.llm import LLMClient
from src.llm.config import LLMConfig
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

    # Provider-agnostic configuration (uses selected LLM)
    MAX_TOKENS = 8000  # Response limit
    THINKING_BUDGET = 6000  # Extended thinking for quality reasoning (but MUST use tools!)
    MAX_ITERATIONS = 15  # Maximum tool call iterations

    # AAOIFI Financial Ratio Thresholds
    DEBT_THRESHOLD = 0.30  # Debt/Market Cap < 30%
    CASH_THRESHOLD = 0.30  # (Cash + Interest Securities)/Market Cap < 30%
    AR_THRESHOLD = 0.50    # Accounts Receivable/Total Assets < 50%
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

    def __init__(
        self,
        model_key: str = None,
        enable_validation: bool = True,
        max_validation_iterations: int = 3
    ):
        """
        Initialize Sharia screener with provider-agnostic LLM.

        Args:
            model_key: LLM model to use (defaults to environment LLM_MODEL)
            enable_validation: Whether to enable Phase 7.6B validation (default: True)
            max_validation_iterations: Maximum validation iterations (default: 3)
        """
        # Initialize LLM client (provider-agnostic)
        model_key = model_key or os.getenv("LLM_MODEL") or LLMConfig.get_default_model()
        self.llm = LLMClient(model_key=model_key)

        # Get provider info
        provider_info = self.llm.get_provider_info()
        logger.info(f"Initialized LLM: {provider_info}")

        # Phase 7.6B: Validation configuration
        self.enable_validation = enable_validation
        self.max_validation_iterations = max_validation_iterations
        logger.info(
            f"Validation: {'ENABLED' if enable_validation else 'DISABLED'} "
            f"(max {max_validation_iterations} iterations)"
        )

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
        Convert tools to provider-native tool format.

        Uses provider-native web search when available:
        - Claude: web_search_20250305
        - Kimi: $web_search builtin_function

        Returns:
            List of tool definitions for API
        """
        # Get provider info
        provider_info = self.llm.get_provider_info()
        provider = provider_info.get("provider", "").lower()

        tools = []

        # Add standard tools
        tools.append({
            "name": "gurufocus_tool",
            "description": self.tools["gurufocus"].description,
            "input_schema": self.tools["gurufocus"].parameters
        })
        tools.append({
            "name": "sec_filing_tool",
            "description": self.tools["sec_filing"].description,
            "input_schema": self.tools["sec_filing"].parameters
        })
        tools.append({
            "name": "calculator_tool",
            "description": self.tools["calculator"].description,
            "input_schema": self.tools["calculator"].parameters
        })

        # Add provider-native web search
        if provider == "claude":
            tools.append({
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 10,
                "allowed_domains": [
                    "sec.gov", "investor.com", "nasdaq.com",
                    "reuters.com", "bloomberg.com", "ft.com",
                    "wsj.com", "marketwatch.com", "investopedia.com"
                ]
            })
            logger.info("Using Claude native web search (web_search_20250305)")

        elif provider == "kimi":
            # Use Kimi official $web_search builtin function
            # Reference: https://platform.moonshot.ai/docs/guide/use-web-search
            tools.append({
                "type": "builtin_function",
                "function": {
                    "name": "$web_search"
                }
            })
            logger.info("Using Kimi official $web_search builtin function")

        else:
            # Unknown provider - add regular web_search_tool
            logger.warning(f"Unknown provider '{provider}' - using standard web_search_tool")
            tools.append({
                "name": "web_search_tool",
                "description": self.tools["web_search"].description,
                "input_schema": self.tools["web_search"].parameters
            })

        return tools

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
        Perform complete Sharia compliance screening using provider-agnostic ReAct loop.

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

        # Get provider info
        provider_info = self.llm.get_provider_info()
        provider_name = provider_info['provider']
        logger.info(f"Using provider: {provider_name}")

        # Build screening prompt
        prompt = self._build_sharia_screening_prompt(ticker)

        # Get provider instance and tool definitions
        provider = self.llm.provider
        tool_definitions = self._get_tool_definitions()

        try:
            # Run provider's native ReAct loop
            result = provider.run_react_loop(
                system_prompt="",  # Sharia prompt is comprehensive and includes everything
                initial_message=prompt,
                tools=tool_definitions,
                tool_executor=self._execute_tool,
                max_iterations=self.MAX_ITERATIONS,
                max_tokens=self.MAX_TOKENS,
                thinking_budget=self.THINKING_BUDGET
            )

            if not result["success"]:
                logger.error(f"Sharia screening failed: {result['metadata'].get('error')}")
                result["metadata"]["analysis_type"] = "sharia_screen"  # Phase 7.6B: For validator
                return {
                    "ticker": ticker,
                    "status": "ERROR",
                    "analysis": f"Screening failed: {result['metadata'].get('error')}",
                    "purification_rate": 0.0,
                    "metadata": result["metadata"]
                }

            # Extract analysis text
            analysis_text = result["thesis"]

            # CRITICAL: Verify that tools were actually used
            tool_calls_made = result["metadata"]["tool_calls"]

            # Reject if NO tools used (hallucinated)
            if tool_calls_made == 0:
                logger.error(f"Sharia screening REJECTED: No tools were used (hallucinated analysis)")
                return {
                    "ticker": ticker,
                    "status": "ERROR",
                    "analysis": (
                        "# SHARIA COMPLIANCE ANALYSIS - REJECTED\n\n"
                        "**ERROR: Invalid Analysis**\n\n"
                        "This Sharia compliance analysis was rejected because no tools were used to gather live data. "
                        "The LLM attempted to provide analysis based solely on training data, which is completely "
                        "unreliable for religious compliance screening.\n\n"
                        "Sharia compliance REQUIRES verification with current financial data from SEC filings and "
                        "financial APIs. Using outdated or hallucinated data for religious rulings is irresponsible "
                        "and potentially harmful to Muslim investors.\n\n"
                        "**Resolution:** Please try again. The LLM must use tools to fetch:\n"
                        "1. Latest 10-K filing (sec_filing_tool)\n"
                        "2. Current financial data (gurufocus_tool)\n"
                        "3. Compliance ratio calculations (calculator_tool)\n\n"
                        f"**Original hallucinated output (DO NOT USE):**\n\n{analysis_text}"
                    ),
                    "purification_rate": 0.0,
                    "metadata": {
                        "analysis_type": "sharia_screen",
                        "analysis_date": datetime.now().isoformat(),
                        "error": "No tools used - hallucinated analysis rejected",
                        "tool_calls_made": 0
                    }
                }

            # Warn if insufficient tools used (but don't reject - let validator score it)
            elif tool_calls_made < 3:
                logger.warning(
                    f"Sharia screening used only {tool_calls_made} tools "
                    f"(expected 5+: 1 sec_filing + 3 gurufocus + 1 calculator). "
                    f"Data quality may be insufficient. Validator will assess quality."
                )

            # Parse status and purification rate
            status = self._extract_status(analysis_text)
            purification_rate = self._extract_purification_rate(analysis_text)

            # Calculate cost using provider
            input_tokens = result["metadata"]["tokens_input"]
            output_tokens = result["metadata"]["tokens_output"]

            # Calculate individual costs
            cost_per_token = self.llm.provider.get_cost_per_token()
            input_cost = input_tokens * cost_per_token["input"]
            output_cost = output_tokens * cost_per_token["output"]
            total_cost = input_cost + output_cost

            logger.info(
                f"Sharia screening complete for {ticker}: {status}, "
                f"purification {purification_rate:.1f}%, "
                f"{result['metadata']['tool_calls']} tool calls, cost ${total_cost:.2f}"
            )

            # Build screening result
            screening_result = {
                "ticker": ticker,
                "status": status,
                "analysis": analysis_text,
                "purification_rate": purification_rate,
                "metadata": {
                    "analysis_type": "sharia_screen",  # Phase 7.6B: For validator
                    "analysis_date": datetime.now().isoformat(),
                    "standard": "AAOIFI",
                    "provider": provider_name,
                    "model": provider_info['model_id'],
                    "tool_calls_made": result["metadata"]["tool_calls"],
                    "iterations": result["metadata"]["iterations"],
                    "token_usage": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "input_cost": round(input_cost, 2),
                        "output_cost": round(output_cost, 2),
                        "total_cost": round(total_cost, 2)
                    }
                }
            }

            # Phase 7.6B: Validate screening if enabled
            if self.enable_validation:
                logger.info("\n" + "=" * 80)
                logger.info("  Phase 7.6B: Sharia Screening Quality Validation")
                logger.info("=" * 80)

                try:
                    critique = self._validate_analysis(screening_result, iteration=0)

                    # Add validation metadata to result
                    screening_result["validation"] = {
                        "enabled": True,
                        "approved": critique.get("approved", False),
                        "score": critique.get("score", 0),
                        "overall_assessment": critique.get("overall_assessment", ""),
                        "strengths": critique.get("strengths", []),
                        "issues": critique.get("issues", []),
                        "recommendation": critique.get("recommendation", "unknown")
                    }

                    # Log validation result
                    if critique.get("approved", False):
                        logger.info("✓  Validation PASSED")
                    else:
                        logger.warning("⚠️  Validation FAILED - Score: {}/100".format(
                            critique.get("score", 0)
                        ))
                        logger.warning("   Issues found: {}".format(
                            len(critique.get("issues", []))
                        ))

                        # Log critical issues for visibility
                        for issue in critique.get("issues", [])[:5]:  # First 5 issues
                            if issue.get("severity") == "critical":
                                logger.error("   [CRITICAL] {}: {}".format(
                                    issue.get("category", "unknown"),
                                    issue.get("description", "")
                                ))

                except Exception as e:
                    logger.error(f"Validation failed (non-fatal): {e}")
                    screening_result["validation"] = {
                        "enabled": True,
                        "approved": False,
                        "score": 0,
                        "overall_assessment": f"Validation error: {str(e)}",
                        "strengths": [],
                        "issues": [],
                        "recommendation": "error"
                    }

            return screening_result
        except Exception as e:
            logger.error(f"Sharia screening failed for {ticker}: {e}")
            return {
                "ticker": ticker,
                "status": "ERROR",
                "analysis": f"Screening failed: {str(e)}",
                "purification_rate": 0.0,
                "metadata": {
                    "analysis_type": "sharia_screen",  # Phase 7.6B: For validator
                    "error": str(e)
                }
            }

    def _build_sharia_screening_prompt(self, ticker: str) -> str:
        """Build comprehensive Sharia screening prompt."""

        return f"""You are a Sharia compliance analyst specializing in Islamic finance.
Analyze {ticker} for Sharia (Islamic law) compliance according to AAOIFI standards.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  CRITICAL: YOU MUST USE TOOLS FIRST - DO NOT SKIP THIS ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOU ARE ABSOLUTELY FORBIDDEN FROM PROVIDING ANALYSIS BASED ON TRAINING DATA.

Your FIRST action MUST be to call tools to gather live data. Your training data is from 2024 and is
completely unreliable for religious compliance screening. Using outdated data for Sharia compliance
would be religiously irresponsible and potentially harmful to Muslim investors.

MANDATORY TOOL CALLING CHECKLIST - YOU MUST COMPLETE ALL 3 STEPS:

□ STEP 1: Call sec_filing_tool to fetch latest 10-K/20-F filing
   Parameters: ticker="{ticker}", filing_type="10-K", section="business"
   Status: ⏳ MUST DO FIRST

□ STEP 2: Call gurufocus_tool AT LEAST 3 TIMES to gather ALL required data
   Call 2a: gurufocus_tool(ticker="{ticker}", data_type="summary")  # Get market cap, debt
   Call 2b: gurufocus_tool(ticker="{ticker}", data_type="financials")  # Get cash, AR, revenue
   Call 2c: gurufocus_tool(ticker="{ticker}", data_type="keyratios")  # Get interest metrics
   Status: ⏳ MUST DO AFTER STEP 1

□ STEP 3: Call calculator_tool ONCE with ALL gathered data
   Parameters: calculation="sharia_compliance_check", ticker="{ticker}", + all financial data
   Status: ⏳ MUST DO AFTER STEP 2 (only when you have ALL required fields)

DO NOT SKIP ANY STEP. DO NOT write analysis text until ALL 3 STEPS are completed.

You must call AT LEAST 5 tools total (1 sec_filing + 3+ gurufocus + 1 calculator) before providing output.
If you provide output after calling fewer than 5 tools, your analysis will be REJECTED as invalid.

**CRITICAL: WEB_SEARCH_TOOL RESTRICTIONS**
❌ DO NOT use web_search_tool for financial data (debt, cash, receivables, revenue, market cap)
❌ DO NOT use web_search for compliance ratios or calculations
✅ ONLY use web_search for business activity questions (e.g., "Does company operate casinos?")
✅ ALL financial data MUST come from sec_filing_tool + gurufocus_tool

If gurufocus doesn't have a field, extract it manually from the 10-K filing text, DO NOT web search for it.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**TOOL INSTRUCTIONS:**

1. **USE TOOLS TO GATHER LIVE DATA** - You have access to 4 tools:
   - sec_filing_tool: Fetch actual 10-K annual reports from SEC EDGAR (PRIMARY SOURCE for business + financials)
   - gurufocus_tool: Get real-time financial metrics and ratios (PRIMARY SOURCE for market data)
   - web_search_tool: ONLY for business activity questions (NOT for financial data)
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
- Use section="business" to get the business description (more efficient than full filing)
- Look for: Business description, revenue breakdown by segment, any prohibited activities
- Example: sec_filing_tool(ticker="{ticker}", filing_type="10-K", section="business")

Step 2: Get ALL financial metrics using gurufocus_tool (make MULTIPLE calls)

REQUIRED GURUFOCUS CALLS (in this exact sequence):

Call 2a: gurufocus_tool(ticker="{ticker}", data_type="summary")
Returns: market_cap, total_debt, cash_and_equivalents, latest_price
→ Extract: market_cap, total_debt, cash (for compliance ratios)

Call 2b: gurufocus_tool(ticker="{ticker}", data_type="financials")
Returns: Balance sheet and income statement data
→ Extract: accounts_receivable, total_revenue, cash_and_liquid_assets, total_assets

Call 2c: gurufocus_tool(ticker="{ticker}", data_type="keyratios")
Returns: Financial ratios and performance metrics
→ Extract: Any remaining fields (interest coverage, ROE, etc.)

CRITICAL: If gurufocus is missing a required field, check if it's in the 10-K filing you already downloaded.
DO NOT use web_search to find financial data - extract it from the 10-K text or estimate from available data.

REQUIRED DATA CHECKLIST before calling calculator:
  ✓ total_debt (from gurufocus summary)
  ✓ market_cap (from gurufocus summary)
  ✓ cash_and_liquid_assets (from gurufocus financials)
  ✓ accounts_receivable (from gurufocus financials)
  ✓ total_revenue (from gurufocus financials)
  ✓ total_assets (from gurufocus financials)
  ✓ interest_income (from gurufocus financials, may be 0)

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
3. **Accounts Receivable / Total Assets** < {self.AR_THRESHOLD * 100}%
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
| **AR / Total Assets** | X.X% | < 50% | [✅/❌] |
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
8. **CITE ALL SOURCES** - Every financial metric and business fact requires citation

**CITATION REQUIREMENTS (MANDATORY):**

Every data point in your Sharia analysis MUST include specific source citations.
This is essential for transparency and verification of religious compliance.

**Citation Format Examples:**
- "Total Debt $15.2B (GuruFocus Summary, accessed Nov 11, 2025)"
- "Market Cap $82.5B (GuruFocus Valuation, accessed Nov 11, 2025)"
- "Debt/Market Cap ratio: $15.2B / $82.5B = 18.4% (calculated from GuruFocus data)"
- "Revenue breakdown: Software 65%, Services 35% (10-K FY2024, Note 17 - Segment Information, page 87)"
- "No interest income disclosed (10-K FY2024, Income Statement, page 45)"
- "Accounts Receivable $12.3B (10-K FY2024, Balance Sheet, page 43)"
- "Operates casino gaming segment with $500M revenue (10-K FY2024, Business section, page 5)"

**What to cite:**
✅ ALL financial ratios and their component values (debt, market cap, cash, AR, revenue)
✅ Business activity descriptions and revenue breakdowns (with 10-K section and page)
✅ All calculations (show your math with sourced inputs)
✅ Any claim about prohibited activities (cite 10-K section proving presence/absence)
✅ Interest income (or explicit statement of no interest income with 10-K reference)
✅ Scholarly opinions (cite specific AAOIFI standard or scholar name)

**For Sharia compliance, citations serve two purposes:**
1. **Verification** - Allow scholars and investors to verify your analysis
2. **Religious obligation** - Investors may need to prove compliance to their own scholars

**Golden Rule:** If you cannot cite the source (with specific 10-K section/page or API data source),
do not include that data point. Sharia compliance analysis requires bulletproof documentation.

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

    # ========================================================================
    # PHASE 7.6B: QUALITY VALIDATION
    # ========================================================================

    def _validate_analysis(
        self,
        analysis_result: Dict[str, Any],
        iteration: int = 0
    ) -> Dict[str, Any]:
        """
        Validate Sharia screening using Validator Agent.

        Phase 7.6B: Validator Agent reviews screening for quality, methodology,
        and completeness, providing detailed critique.

        Args:
            analysis_result: Screening dict from Sharia Agent
            iteration: Current iteration number (0-based)

        Returns:
            Validator critique dict with:
                - approved: bool
                - score: int (0-100)
                - overall_assessment: str
                - strengths: List[str]
                - issues: List[Dict]
                - recommendation: str ("approve"|"revise"|"reject")
        """
        from src.agent.prompts import get_validator_prompt

        logger.info(f"[VALIDATOR] Reviewing Sharia screening (iteration {iteration + 1})")

        # Get LLM knowledge cutoff for validator context
        provider_info = self.llm.get_provider_info()
        knowledge_cutoff = provider_info.get("knowledge_cutoff", "Unknown")

        # Build validator prompt with knowledge cutoff
        prompt = get_validator_prompt(analysis_result, iteration, knowledge_cutoff)

        # Call validator LLM with tools for verification
        try:
            # Get validator tools (web_search and calculator for verification)
            validator_tools = self._get_validator_tool_definitions()

            # Use provider's native ReAct loop for validation
            response = self.llm.provider.run_react_loop(
                system_prompt="You are a validator reviewing Sharia compliance screening. Use tools to verify claims before flagging issues.",
                initial_message=prompt,
                tools=validator_tools,
                tool_executor=self._execute_validator_tool,
                max_iterations=10,  # Allow validator to call tools
                max_tokens=8000,
                thinking_budget=0  # Deterministic validation, no extended thinking needed
            )

            # Parse JSON response from validator's final output
            critique = self._parse_json_response(response.get("thesis", ""), "validation")

            # Log validation results
            score = critique.get('score', 0)
            approved = critique.get('approved', False)
            issues_count = len(critique.get('issues', []))

            logger.info(f"[VALIDATOR] Score: {score}/100, Approved: {approved}, Issues: {issues_count}")

            if not approved:
                # Log issues for visibility
                for issue in critique.get('issues', []):
                    severity = issue.get('severity', 'unknown').upper()
                    category = issue.get('category', 'unknown')
                    description = issue.get('description', '')
                    logger.warning(f"[{severity}] {category}: {description}")

            return critique

        except Exception as e:
            logger.error(f"Validator failed: {e}", exc_info=True)
            # Return a failed validation instead of crashing
            return {
                "approved": False,
                "score": 0,
                "overall_assessment": f"Validator error: {str(e)}",
                "strengths": [],
                "issues": [{
                    "severity": "critical",
                    "category": "validation",
                    "description": f"Validator failed: {str(e)}",
                    "how_to_fix": "Check validator configuration and LLM availability"
                }],
                "methodology_correct": False,
                "calculations_complete": False,
                "sources_adequate": False,
                "buffett_principles_followed": False,
                "recommendation": "reject"
            }

    def _get_validator_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for validator (web_search, calculator, and gurufocus).

        Validator needs limited tools to verify claims:
        - web_search: Verify recent events beyond knowledge cutoff (business activities)
        - calculator: Verify Sharia compliance calculations (ratios, percentages)
        - gurufocus: Verify financial metrics (revenue sources, debt levels)

        Returns:
            List of tool definitions in provider-specific format
        """
        # Only expose web_search, calculator, and gurufocus to validator
        validator_tool_names = ["web_search", "calculator", "gurufocus"]

        # Get all tools with provider-native formatting
        all_tools = self._get_tool_definitions()

        # Filter to only validator tools (handle both standard and builtin_function formats)
        validator_tools = []
        for tool in all_tools:
            # Extract tool name (handle different formats)
            if tool.get("type") == "builtin_function":
                # Kimi builtin function (e.g., $web_search)
                tool_name = tool.get("function", {}).get("name", "")
            else:
                # Standard tool (Claude format or converted OpenAI format)
                tool_name = tool.get("name", "")

            # Check if this tool should be available to validator
            if any(name in tool_name.lower().replace("$", "") for name in validator_tool_names):
                validator_tools.append(tool)

        logger.info(f"[VALIDATOR] Tools available: {len(validator_tools)} tools")
        for tool in validator_tools:
            if tool.get("type") == "builtin_function":
                logger.info(f"  - {tool.get('function', {}).get('name', 'unknown')} (builtin)")
            else:
                logger.info(f"  - {tool.get('name', 'unknown')}")

        return validator_tools

    def _execute_validator_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool for validator with logging.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Tool parameters

        Returns:
            Tool execution result
        """
        logger.info(f"[VALIDATOR] Executing {tool_name}")

        # Find the tool
        tool = self.tools.get(tool_name)
        if not tool:
            # Try to find by partial match (e.g., "calculator_tool" -> "calculator")
            for name, t in self.tools.items():
                if name.lower() in tool_name.lower():
                    tool = t
                    break

        if not tool:
            logger.warning(f"[VALIDATOR] Tool '{tool_name}' not found")
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not available to validator"
            }

        try:
            # Execute tool
            result = tool.execute(**tool_input)

            # Log success/failure
            if result.get("success"):
                logger.info(f"[VALIDATOR] {tool_name} succeeded")
            else:
                logger.warning(f"[VALIDATOR] {tool_name} failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"[VALIDATOR] {tool_name} error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_json_response(self, text: str, context: str) -> Dict:
        """
        Parse JSON response from LLM (handles markdown blocks, text noise, and malformed JSON).

        Args:
            text: LLM response text
            context: Context for error reporting

        Returns:
            Parsed JSON dict
        """
        import re
        import json

        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)

        # Extract JSON object (handles text before/after)
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError(f"No JSON object found in {context} response")

        json_str = json_match.group(0)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse full JSON in {context}: {e}")
            logger.warning(f"JSON string excerpt: {json_str[:500]}...")

            # Fallback: Extract key fields with regex for partial validation results
            if context == "validation":
                logger.info("Attempting fallback parsing for validation critique...")

                # Extract score
                score_match = re.search(r'"score"\s*:\s*(\d+)', json_str)
                score = int(score_match.group(1)) if score_match else 0

                # Extract approved
                approved_match = re.search(r'"approved"\s*:\s*(true|false)', json_str, re.IGNORECASE)
                approved = approved_match.group(1).lower() == 'true' if approved_match else False

                # Extract overall_assessment
                assessment_match = re.search(r'"overall_assessment"\s*:\s*"([^"]*)"', json_str)
                assessment = assessment_match.group(1) if assessment_match else f"JSON parse error: {str(e)}"

                logger.info(f"Fallback parsing extracted: score={score}, approved={approved}")

                return {
                    "approved": approved,
                    "score": score,
                    "overall_assessment": assessment,
                    "strengths": [],
                    "issues": [{
                        "severity": "minor",
                        "category": "validation",
                        "description": f"Validator JSON was malformed (parse error at char {e.pos}), using fallback parsing. Score and approval extracted successfully.",
                        "how_to_fix": "N/A - technical issue, not analysis issue"
                    }],
                    "methodology_correct": score >= 70,
                    "calculations_complete": score >= 70,
                    "sources_adequate": score >= 70,
                    "buffett_principles_followed": score >= 70,
                    "recommendation": "approve" if approved else "revise"
                }
            else:
                # For non-validation contexts, raise the error
                raise ValueError(f"Invalid JSON in {context} response: {e}")


__all__ = ["ShariaScreener"]
