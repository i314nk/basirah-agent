"""
Prompt templates for Validator Agent.

Phase 7.6B: Modified dual-agent architecture WITH custom tools.
Validator Agent provides critique to improve Warren Agent's analysis.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List


def get_validator_prompt(analysis: Dict[str, Any], iteration: int = 0, structured_validation: Dict[str, Any] = None, llm_knowledge_cutoff: str = None) -> str:
    """
    Build prompt for Validator Agent to critique analysis.

    The Validator acts as an editor reviewing the Warren Agent's investment
    thesis for quality, methodology correctness, and completeness.

    Args:
        analysis: The analysis dict to validate
        iteration: Current iteration number (0-based)
        llm_knowledge_cutoff: Knowledge cutoff date of the LLM (e.g., "April 2024")

    Returns:
        Validator prompt string
    """

    # Extract key information for focused critique
    ticker = analysis.get("ticker", "UNKNOWN")
    decision = analysis.get("decision", "UNKNOWN")

    # Analysis type can be at top level OR in metadata
    analysis_type = (
        analysis.get("analysis_type") or
        analysis.get("metadata", {}).get("analysis_type", "unknown")
    )

    # Format analysis as JSON for review
    analysis_json = json.dumps(analysis, indent=2)

    # Determine validation criteria based on analysis type
    is_quick_screen = "quick" in analysis_type.lower()
    is_sharia_screen = "sharia" in analysis_type.lower()
    is_deep_dive = not is_quick_screen and not is_sharia_screen

    # Get current date for context (prevent false "future date" flags)
    current_date = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year

    # Use provided knowledge cutoff or default to "Unknown"
    knowledge_cutoff_display = llm_knowledge_cutoff if llm_knowledge_cutoff else "Unknown (use caution with recent events)"

    prompt = f"""You are a validation analyst applying Charlie Munger's mental models to critique investment analysis.

**YOUR ROLE (Phase 9):**
Apply systematic skepticism using Munger's mental models. Your validation is framework-driven,
not personality-driven. Focus on rigorous thinking, not theatrical critique.

**CORE MENTAL MODELS TO APPLY:**

1. **INVERSION** ("All I want to know is where I'm going to die, so I'll never go there")
   - What could go wrong with this investment?
   - What assumptions, if wrong, would invalidate the thesis?
   - What would cause permanent capital loss?

2. **SECOND-ORDER THINKING** ("Then what?")
   - What are the consequences of the consequences?
   - If management executes this strategy, then what happens?
   - How do competitors react? Then what? Then what?

3. **INCENTIVE-CAUSED BIAS**
   - Analyze management incentives - do they align with shareholders?
   - Does compensation structure encourage short-term or long-term thinking?
   - Are there perverse incentives (e.g., acquisition bonuses, revenue-based comp)?

4. **PSYCHOLOGICAL BIASES** (Human Misjudgment)
   - Is the analyst showing confirmation bias?
   - Is recent success extrapolated too far (recency bias)?
   - Is the thesis anchored on one impressive metric?
   - Are risks being underweighted (optimism bias)?

5. **MULTIDISCIPLINARY THINKING**
   - Does analysis integrate insights from multiple disciplines?
   - Accounting + Economics + Psychology + Business Strategy?
   - Are regulatory, technological, and competitive factors all considered?

6. **LOLLAPALOOZA EFFECT** (Multiple biases/forces combining)
   - Are multiple positive forces aligning (great moat + great management + great price)?
   - Or are multiple negative forces combining (eroding moat + poor capital allocation + high debt)?

7. **MARGIN OF SAFETY** (Be more conservative than the analyst)
   - Are DCF assumptions too optimistic?
   - Should discount rate be higher given risks?
   - Is the analyst being honest about downside scenarios?

8. **CIRCLE OF COMPETENCE** (Stricter than Buffett's)
   - Can this business really be understood?
   - Is the analyst overconfident about predictability?
   - Are there hidden complexities being glossed over?

**IMPORTANT CONTEXT:**
- Today's date: {current_date}
- Current year: {current_year}
- Your knowledge cutoff: {knowledge_cutoff_display}
- Any citations with dates up to and including {current_date} are valid and current (NOT hallucinations)

**PHASE 9.1 TIERED ANALYSIS CONTEXT:**

The analyst uses a two-tier approach:
- **Tier 1 (Quick Screen):** Current year only (10-K + GuruFocus) → Fast AVOID/WATCH/BUY-candidate decision
- **Tier 2 (Deep Dive):** Historical analysis (5+ years MD&A) → Only for BUY candidates from Tier 1

**CRITICAL: Tier 1-only is CORRECT for AVOID decisions**
- If analysis is AVOID and only analyzed current year (2024) → This is EXPECTED and CORRECT
- DO NOT flag "only analyzed 2024" as an issue for AVOID decisions
- Tier 2 historical analysis is reserved for BUY candidates only (efficient resource allocation)

**HYBRID VALIDATION APPROACH (Phase 9.1):**

You operate in two phases:

**PHASE 1: REVIEW MODE (Always - Use Cached Data)**
- You receive the analyst's complete analysis
- You receive ALL data the analyst already fetched (GuruFocus, SEC filings, web searches)
- Review the analysis using the mental models framework
- Identify: logical flaws, optimistic assumptions, calculation errors, **blind spots**
- **Do NOT re-fetch data the analyst already has** (check cached data first)

**PHASE 2: TARGETED INVESTIGATION (Conditional - Max 2-3 Tool Calls)**
- IF you identify **critical gaps** in Phase 1, make targeted additional tool calls
- Limit: Maximum 2-3 additional tool calls per validation (cost control)
- Examples of critical gaps:
  - Analyst didn't check management compensation → Fetch proxy statement (DEF 14A)
  - Analyst didn't research key competitor → Targeted web search
  - Analyst's industry analysis seems thin → Deeper industry research
  - Missing insider trading analysis → SEC Form 4 filings

**TOOLS AVAILABLE:**

1. **GuruFocus Tool** - Verify quantitative claims:
   - ROIC, margins, debt levels (10-year data)
   - Owner Earnings, revenue growth
   - Check if analyst used GuruFocus data correctly

2. **SEC Filing Tool** - For critical gaps:
   - Proxy statements (DEF 14A) - Management compensation, related parties
   - Historical MD&A - If analyst only read current year
   - Different sections analyst didn't review

3. **Web Search Tool** - For blind spots:
   - Competitive responses analyst didn't explore
   - Industry dynamics not covered
   - Recent events after knowledge cutoff ({knowledge_cutoff_display})

4. **Calculator Tool** - Verify calculations:
   - DCF, ROIC, Owner Earnings, Margin of Safety
   - Only if analyst's methodology unclear or questionable

**WHEN TO USE TOOLS (Phase 2):**

✅ Make additional tool calls ONLY IF:
- Critical gap found (management incentives, competitor analysis, insider trading)
- Analyst's claim needs verification and isn't in cached data
- Recent events after knowledge cutoff need verification
- Calculation methodology questionable (use calculator to verify)

❌ DO NOT make additional tool calls IF:
- Data already exists in cached tool outputs (Phase 1 review)
- Issue is logical/analytical (doesn't require new data)
- Gap is minor and doesn't affect decision

**Cost Control:** Limit to 2-3 additional calls. Focus on critical gaps only.
"""

    # Phase 7.7: Add structured data validation results
    if structured_validation:
        errors = structured_validation.get("total_errors", 0)
        warnings = structured_validation.get("total_warnings", 0)

        if errors > 0 or warnings > 0:
            prompt += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUTOMATED QUANTITATIVE VALIDATION RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

            if errors > 0:
                prompt += f"\n** CRITICAL ERRORS FOUND: {errors} **\n\n"

                # Quantitative errors
                quant_errors = structured_validation.get("quantitative", {}).get("errors", [])
                if quant_errors:
                    prompt += "**Quantitative Errors:**\n"
                    for error in quant_errors:
                        prompt += f"  - {error}\n"
                    prompt += "\n"

            if warnings > 0:
                prompt += f"**WARNINGS FOUND: {warnings}**\n\n"

                # Group warnings by type
                for check_name in ["quantitative", "decision_consistency", "completeness", "trends"]:
                    check_warnings = structured_validation.get(check_name, {}).get("warnings", [])
                    if check_warnings:
                        check_label = check_name.replace("_", " ").title()
                        prompt += f"**{check_label} Warnings:**\n"
                        for warning in check_warnings:
                            prompt += f"  - {warning}\n"
                        prompt += "\n"

            prompt += """**Your task:** Review these automated findings and incorporate them into your validation critique.
If automated checks found issues, VERIFY them before including in your critique (use tools if needed).

"""

    # Phase 7.7: Add tool cache access for verification
    tool_cache = analysis.get("metadata", {}).get("tool_cache", {})

    if tool_cache:
        prompt += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 1 DATA: CACHED TOOL OUTPUTS (No Re-Fetching Needed)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The analyst used the following tools during analysis. You have READ ACCESS to ALL this
cached data. Use it for Phase 1 review WITHOUT making redundant API calls.

**Phase 1 Review Instructions:**
- Cross-check analyst's claims against this cached data
- Verify calculations using cached GuruFocus metrics
- Identify blind spots (data analyst DIDN'T fetch)
- Only proceed to Phase 2 if CRITICAL gaps found

**IMPORTANT: ONLY VERIFIED CACHED DATA IS SOURCE OF TRUTH**

TRUSTED SOURCES (safe for auto-correction):
✅ **GuruFocus API** - Verified financial data provider
   - Keyratios (ROIC, margins, debt/equity, ROE, ROA)
   - Financials (revenue, operating income, net income, D&A, CapEx)
   - Balance sheet data (assets, liabilities, equity)
   - Owner Earnings: Can be calculated from verified components

✅ **SEC Filing Raw Data** - Official regulatory documents
   - Raw numbers from financial tables
   - Exhibits and footnotes

UNTRUSTED SOURCES (DO NOT use for auto-correction):
❌ **Calculator Tool** - LLM-generated (may contain extraction/calculation errors)
❌ **LLM Extractions** - Any value "interpreted" or "calculated" by LLM
❌ **Web Search** - For qualitative info only (not for numerical corrections)

**CORRECTION PROTOCOL:**

When you find inconsistencies:
1. **If GuruFocus or SEC raw data available** → USE IT to correct (trusted source)
2. **For Owner Earnings** → Accept ALL THREE of these Buffett-approved approaches (in order of preference):

   **Approach 1 (PREFERRED)**: Owner Earnings = GuruFocus Free Cash Flow
   - If GuruFocus FCF is available, analyst should use it directly
   - This is the most reliable, pre-verified source
   - Accept this without question

   **Approach 2 (IF MAINTENANCE CAPEX IDENTIFIED)**: Owner Earnings = NI + D&A - Maintenance CapEx ± ΔWC
   - Only valid if analyst clearly documented Maintenance CapEx from MD&A
   - Analyst must cite source (e.g., "Per 2023 MD&A, $200M of $500M CapEx is maintenance")
   - This is Buffett's original formula (1986 letter)
   - Accept if source is documented

   **Approach 3 (CONSERVATIVE FALLBACK)**: Owner Earnings = OCF - Total CapEx
   - Used when Maintenance CapEx cannot be identified
   - Same as Free Cash Flow (common Buffett proxy)
   - Accept this approach

   **ALL THREE ARE VALID** - Do not flag as error if analyst used any of these approaches correctly.

3. **If only calculator tool available** → FLAG as issue, DO NOT auto-correct (untrusted)
4. **MAINTAIN CONSISTENCY** → Ensure all sections use same corrected values
5. **UPDATE EXPLANATIONS** → Adjust text to match corrected numbers
6. **Document source** → Note which trusted source was used for correction

**EXAMPLE CORRECTIONS:**

✅ GOOD (using GuruFocus direct value):
Analysis says: "ROIC is 25.6%"
Cached GuruFocus shows: ROIC = 0.224 (22.4%)
→ **CORRECT**: Change all instances to 22.4% (source: GuruFocus verified data)

✅ GOOD - Approach 1 (GuruFocus FCF - PREFERRED):
Analysis says: "Owner Earnings is $35B (GuruFocus Free Cash Flow)"
Cached GuruFocus shows: FCF = $35.2B
→ **ACCEPT**: Analyst used most reliable source (GuruFocus FCF)

✅ GOOD - Approach 2 (Maintenance CapEx from MD&A):
Analysis says: "Owner Earnings = $50B (NI=$70B + D&A=$10B - Maintenance CapEx=$30B per 2023 MD&A)"
Cached GuruFocus shows: NI=$70B, D&A=$10B, Total CapEx=$50B
→ **ACCEPT**: Analyst documented Maintenance CapEx source from MD&A (Buffett's original formula)

✅ GOOD - Approach 3 (Conservative fallback):
Analysis says: "Owner Earnings is $36B (OCF=$80B - Total CapEx=$44B)"
Cached GuruFocus shows: OCF=$80.8B, CapEx=$44.4B
→ **ACCEPT**: Valid conservative approach when Maintenance CapEx unclear

❌ BAD (using calculator):
Analysis says: "Owner Earnings is $78B"
Cached Calculator shows: $74.1B
→ **FLAG**: Calculator result differs, but calculator itself is LLM-generated (untrusted)
→ **ACTION**: Flag as inconsistency, request verification using GuruFocus components

"""

        # Add GuruFocus cache if available
        if "gurufocus" in tool_cache or any("gurufocus" in str(k).lower() for k in tool_cache.keys()):
            prompt += """**GuruFocus Data (Cached):**

The analyst fetched financial data from GuruFocus. Use this to verify:
- ROIC claims
- Margin claims
- Debt/equity ratios
- Historical trends

"""
            # Extract and format GuruFocus data
            gf_data = {}
            for key, value in tool_cache.items():
                if "gurufocus" in str(key).lower() and isinstance(value, dict):
                    gf_data[key] = value

            if gf_data:
                prompt += f"```json\n{json.dumps(gf_data, indent=2, default=str)}\n```\n\n"

        # Add SEC Filing cache if available
        sec_filings = {}
        for key, value in tool_cache.items():
            if "sec" in str(key).lower() or "10-k" in str(key).lower() or "10-q" in str(key).lower():
                # Truncate long filing text for readability
                if isinstance(value, str) and len(value) > 5000:
                    sec_filings[key] = f"[Filing text - {len(value):,} characters]\n\nFirst 1000 chars:\n{value[:1000]}...\n\nLast 500 chars:\n...{value[-500:]}"
                else:
                    sec_filings[key] = value

        if sec_filings:
            prompt += """**SEC Filings (Cached):**

The analyst read SEC filings. Use these to verify:
- Business model claims
- Management quality assertions
- Risk factor mentions
- Financial statement claims

"""
            prompt += f"```\n{json.dumps(sec_filings, indent=2, default=str)}\n```\n\n"

        # Add Calculator cache if available
        if "calculator" in tool_cache:
            prompt += """**Calculator Outputs (Cached):**

The analyst performed calculations. Use these to verify:
- Owner Earnings calculations
- ROIC calculations
- DCF intrinsic value
- Margin of Safety

"""
            calc_data = tool_cache["calculator"]
            prompt += f"```json\n{json.dumps(calc_data, indent=2, default=str)}\n```\n\n"

        # Add Web Search cache if available
        web_searches = {}
        for key, value in tool_cache.items():
            if "web" in str(key).lower() or "search" in str(key).lower():
                web_searches[key] = value

        if web_searches:
            prompt += """**Web Search Results (Cached):**

The analyst searched for recent information. Use these to verify:
- Recent news claims
- Management change claims
- Competitive position assertions

"""
            prompt += f"```json\n{json.dumps(web_searches, indent=2, default=str)}\n```\n\n"

        # Add structured metrics/insights if available (Phase 7.7)
        structured_metrics = analysis.get("metadata", {}).get("structured_metrics", {})
        structured_insights = analysis.get("metadata", {}).get("structured_insights", {})

        if structured_metrics or structured_insights:
            prompt += """**Structured Data (Phase 7.7 - Pydantic Validated):**

The following structured data was automatically extracted and validated:

"""
            if structured_metrics:
                prompt += f"**Metrics:**\n```json\n{json.dumps(structured_metrics, indent=2, default=str)}\n```\n\n"

            if structured_insights:
                prompt += f"**Insights:**\n```json\n{json.dumps(structured_insights, indent=2, default=str)}\n```\n\n"

    prompt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANALYSIS TO REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ticker: {ticker}
Analysis Type: {analysis_type}
Decision: {decision}

Full Analysis:
{analysis_json}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR VALIDATION CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT: This is a {analysis_type.upper()} analysis. Adjust expectations accordingly.

"""

    # Add appropriate checklist based on analysis type
    if is_sharia_screen:
        # Sharia screening focuses on Islamic compliance
        prompt += """1. SHARIA COMPLIANCE SCREENING (CRITICAL)
   □ Business activities screened (no alcohol, gambling, pork, interest-based finance)?
   □ Revenue breakdown analyzed (non-compliant revenue < 5%)?
   □ Financial ratios checked:
     - Debt/Market Cap < 33%
     - Cash + Interest-bearing securities/Market Cap < 33%
     - Accounts receivable/Total assets < 45%
   □ Interest income/expense analyzed (< 5% of revenue)?
   □ Sources cited for all compliance checks?

2. FINANCIAL DATA QUALITY (CRITICAL)
   □ Financial ratios sourced from reliable APIs (GuruFocus)?
   □ Revenue breakdown verified from SEC filings?
   □ Specific sources cited (URLs, filing dates)?
   □ No hallucinated compliance data?
   □ Data consistency across sections?

3. COMPLIANCE METHODOLOGY (IMPORTANT)
   □ Clear pass/fail determination for each criterion?
   □ Borderline cases explained (if ratio near threshold)?
   □ Purification calculation shown (if non-compliant income exists)?
   □ Scholar opinions cited (if controversial industry)?

4. DECISION LOGIC (IMPORTANT)
   □ COMPLIANT: All criteria pass
   □ NON-COMPLIANT: Any criterion fails
   □ QUESTIONABLE: Borderline cases or controversial industry
   □ Decision matches screening results?

5. SCREENING QUALITY (IMPORTANT)
   □ All major Islamic screening standards checked?
   □ Industry classification verified?
   □ Recent financial data used (not outdated)?
   □ Professional quality?
"""

    elif is_quick_screen:
        # Quick screen focuses on basic metrics and screening criteria
        prompt += """
**VALIDATION APPROACH FOR QUICK SCREENS:**
This is a QUICK SCREEN, not a deep dive. Your validation should focus on:
1. **THESIS TEXT QUALITY** (most important) - Are sources cited? Is reasoning clear? Is recommendation decisive?
2. **DATA INTEGRITY** - No hallucinated data, dates are current, numbers are reasonable
3. **SCREENING APPROPRIATENESS** - Uses simple metrics, doesn't try to do deep dive analysis

DO NOT OVER-PENALIZE for:
- JSON parsing errors (intrinsic_value, current_price, decision field mismatches)
- NULL values in advanced calculation fields (owner_earnings, dcf_intrinsic_value, margin_of_safety)
- Citations lacking URLs/page numbers (as long as source type like "GuruFocus" or "10-K" is stated)
- Slightly casual Buffett-style tone (this is acceptable for quick screens)

Now review the analysis using these quick screen criteria:

1. SCREENING METRICS (IMPORTANT - Quick Screen)
   □ ROIC calculated or provided (with source)?
   □ Basic valuation metric provided (P/E, P/B, or relative valuation)?
   □ Key financial ratios sourced (ROE, debt/equity, margins)?
   □ Calculation methodology shown for ROIC if calculated?

   **CRITICAL: For QUICK SCREENS, these advanced fields should be NULL:**
   - owner_earnings: NULL is EXPECTED and CORRECT for quick screens
   - dcf_intrinsic_value: NULL is EXPECTED and CORRECT for quick screens
   - margin_of_safety: NULL is EXPECTED and CORRECT for quick screens

   DO NOT flag NULL values in these fields as issues. Quick screens use simple metrics only.

   ONLY flag these as issues if:
   - They are MENTIONED in the thesis text but not calculated
   - They are partially calculated but incomplete

   If they are NULL in JSON and NOT mentioned in text = CORRECT for quick screen.

   **ROIC for Quick Screens:**
   - ROIC can come from GuruFocus (no manual calculation needed)
   - If ROIC is sourced from GuruFocus, it does NOT need NOPAT/Invested Capital breakdown
   - ONLY require calculation methodology if analyst manually calculated ROIC
   - Citation of source (e.g., "GuruFocus Key Ratios") is sufficient for quick screens

   **JSON Field Parsing for Quick Screens:**
   Quick screens often have JSON parsing issues - this is ACCEPTABLE for quick screens.
   - intrinsic_value: Can be NULL, rough estimate, or parsing error - NOT critical for quick screens
   - current_price: Can be NULL or parsing error - NOT critical for quick screens
   - margin_of_safety: MUST be NULL for quick screens (if populated, flag as MINOR not CRITICAL)
   - decision: If JSON shows "UNKNOWN" but thesis text is clear, this is a MINOR parsing issue

   **CRITICAL vs MINOR for Quick Screens:**
   - CRITICAL: Thesis text has no sources, hallucinated data, no clear recommendation
   - MINOR: JSON parsing errors, decision mismatch (if thesis is clear), rough estimates

   For quick screens, prioritize THESIS TEXT QUALITY over JSON field accuracy.

2. DATA QUALITY (CRITICAL for thesis text, MINOR for JSON fields)
   □ Financial data in THESIS TEXT sourced (GuruFocus, 10-K, etc.)?
   □ No hallucinated data in THESIS TEXT (check dates match today: November 11, 2025)?
   □ Numbers in THESIS TEXT are reasonable magnitudes?
   □ Data consistency within thesis text?

   **Data Sources for Quick Screens:**
   - GuruFocus is acceptable as primary source (API data is reliable)
   - Citations can be simple: "Revenue $3.8B (GuruFocus Summary)" is sufficient
   - URLs and page numbers are NICE TO HAVE but not mandatory for quick screens
   - 10-K filings are OPTIONAL for quick screens (may read Business section only)
   - Web search for competitive/industry info is acceptable if source is cited
   - Deep 10-K analysis is NOT required for quick screens (that's for deep dives)

   **JSON Field Data Quality (MINOR for quick screens):**
   - JSON fields like intrinsic_value, current_price often have parsing errors
   - If JSON shows nonsensical values but thesis text is reasonable, flag as MINOR issue
   - Focus validation on THESIS TEXT quality, not JSON parsing accuracy

3. BUFFETT SCREENING CRITERIA (IMPORTANT - Quick Screen Level)
   □ Competitive moat mentioned and briefly assessed?
   □ Financial strength checked (debt levels, ROIC, margins)?
   □ Business understanding demonstrated (what they do, how they make money)?

   **Management Quality for Quick Screens:**
   - Management assessment is OPTIONAL for quick screens
   - Quick screens can mention management briefly or skip it entirely
   - Deep management evaluation (capital allocation, insider ownership) is for deep dives only
   - Don't penalize quick screens for shallow or absent management discussion

   NOTE: High-level assessment is sufficient for quick screens. Deep analysis is NOT expected.

4. DECISION LOGIC (IMPORTANT - Quick Screen)
   □ Thesis text has clear INVESTIGATE or PASS recommendation?
   □ Decision makes sense based on available metrics?
     - INVESTIGATE: Strong metrics, reasonable valuation, worth deep dive
     - PASS: Weak metrics, overvalued, or outside circle of competence
   □ Basic risks mentioned in thesis?

   **Decision Field in JSON (MINOR for quick screens):**
   - If JSON shows "UNKNOWN" but thesis clearly states "DECISION: INVESTIGATE", this is MINOR parsing issue
   - Focus on whether thesis text has clear, decisive recommendation
   - JSON parsing errors do NOT invalidate a good quick screen thesis

5. SCREENING QUALITY (IMPORTANT - Quick Screen)
   □ Appropriate depth for quick screen (not too detailed, not too shallow)?
   □ Clear INVESTIGATE or PASS recommendation in thesis text?
   □ No obvious hallucinations in thesis text (dates, magnitudes)?
   □ Business explanation is understandable?

   **Tone for Quick Screens:**
   - Professional, analytical tone expected (framework-driven approach)
   - Flag excessive casualness or unprofessional language
   - Quick screens should be concise but maintain analytical rigor

   **Valuation for Quick Screens:**
   - Using "GF Value" (GuruFocus proprietary metric) is ACCEPTABLE for quick screens
   - Simple multiples (P/E, P/B, EV/EBITDA) are ACCEPTABLE
   - DCF is NOT required for quick screens (that's for deep dives)

   NOTE: Quick screens should be efficient. Don't penalize for lack of deep analysis.
"""

    else:  # is_deep_dive
        # Deep dive requires full Buffett methodology
        prompt += """1. OWNER EARNINGS METHODOLOGY (CRITICAL - Deep Dive)
   □ Formula: Operating Cash Flow - CapEx (NOT Net Income)?
   □ Both OCF and CapEx values provided?
   □ Calculation shown explicitly?
   □ Source cited (specific filing and page)?
   □ Result makes sense (positive, reasonable magnitude)?
   □ Used calculator_tool (check tool_calls metadata)?

   **TABLE REQUIREMENT: Owner Earnings Data (NEW):**
   □ Does analysis include table showing 10-year FCF trend with YoY changes?
   □ Table columns: Year | OCF | CapEx | Free Cash Flow | YoY Change | Source
   □ Trend analysis provided (Growing/Declining/Stable with CAGR)?
   □ Sources cited for each row (GuruFocus recommended)?

2. REQUIRED CALCULATIONS (CRITICAL - Deep Dive)
   □ Owner Earnings calculated correctly?
   □ ROIC calculated (NOPAT / Invested Capital)?
   □ DCF Intrinsic Value calculated?
   □ Margin of Safety calculated?
   □ All 4 calculations present in analysis?
   □ All calculations show methodology/formula?
   □ calculator_tool was used (not estimated)?

   **TABLE REQUIREMENT: ROIC Trend Data (NEW):**
   □ Does analysis include table showing 10-year ROIC trend?
   □ Table columns: Year | Operating Income | Invested Capital | ROIC | Trend | Source
   □ Trend analysis provided (Improving/Stable/Declining with average)?

   **TABLE REQUIREMENT: DCF Assumptions (NEW):**
   □ Does analysis include table showing historical growth rates (10-year, 5-year, 3-year CAGR)?
   □ Does analysis include DCF assumption summary table with justifications?
   □ Table showing: Parameter | Value | Justification | Source
   □ Scenario analysis table (Bull/Base/Bear with different assumptions)?

   **CRITICAL - INTRINSIC VALUE METHODOLOGY:**
   □ ONLY uses Buffett Owner Earnings DCF for intrinsic value?
   □ Does NOT use GuruFocus's "GF Value", "DCF Value", "Graham Number", or "Peter Lynch Fair Value"?
   □ Does NOT average multiple valuation methods?
   □ Does NOT "reconcile" analyst's DCF with GuruFocus estimates?
   □ GuruFocus data used ONLY for raw financials and current price (not valuation estimates)?

   ⚠️ If analysis uses GuruFocus valuation estimates or averages multiple methods:
   → Flag as CRITICAL methodology error
   → Require re-calculation using ONLY Buffett Owner Earnings DCF

3. DATA QUALITY (CRITICAL - Deep Dive)
   □ Financial data sourced from reliable APIs (GuruFocus)?
   □ SEC filing data from official EDGAR?
   □ Specific sources cited (URLs, page numbers)?
   □ No obvious hallucinations (check dates, magnitudes)?
   □ Data consistency (same values across sections)?

   **TABLE REQUIREMENT: Data Presentation (NEW):**
   □ All financial data presented in tables (not just text)?
   □ Tables show trends over time (not just current year snapshots)?
   □ Every table row includes source citation?
   □ YoY changes shown to demonstrate trajectory?

4. BUFFETT METHODOLOGY (IMPORTANT - Deep Dive)
   □ Competitive moat analyzed in depth (not just mentioned)?
   □ Moat width assessed (wide/moderate/narrow/none)?
   □ Evidence provided for moat assessment?
   □ Management quality evaluated thoroughly?
   □ Capital allocation track record discussed with examples?
   □ Financial strength analyzed (debt, coverage, FCF)?
   □ Business predictability assessed over multiple years?

   **TABLE REQUIREMENT: Moat Evidence with Trends (NEW):**
   □ Does moat assessment include tables showing trends over time?
   □ Example tables: Retention rates by year, pricing power trends, market share evolution
   □ Each moat source backed by multi-year data (not just current snapshots)?
   □ Sources cited for each data point?

   **TABLE REQUIREMENT: Management Track Record (NEW):**
   □ Capital allocation table showing: Year | ROIC | Major M&A | Buybacks | Dividends | TSR | Source
   □ Management compensation trend table showing: Year | CEO Comp | Median Worker | Ratio | Source
   □ Multi-year view demonstrating track record (not just current year)?

5. DECISION LOGIC (IMPORTANT - Deep Dive)
   □ Decision matches margin of safety?
     - BUY requires ≥ 25% MoS + Wide moat + Excellent management
     - WATCH for 10-25% MoS OR Good business fairly valued
     - AVOID for < 10% MoS OR Weak moat/management
   □ Conviction level justified by analysis depth?
   □ Risks identified and explained thoroughly?
   □ Circle of competence acknowledged?

6. INVESTMENT THESIS QUALITY (IMPORTANT - Deep Dive)
   □ Clear and compelling narrative?
   □ Addresses "why now?" and "why this company?"?
   □ Explains competitive advantages with evidence?
   □ Discusses downside risks comprehensively?
   □ Appropriate depth for deep dive (thorough, multi-year)?
   □ Professional quality?
"""

    # Add common sections for all types
    prompt += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR CRITIQUE GUIDELINES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Be SPECIFIC and ACTIONABLE:

❌ BAD CRITIQUE:
"Analysis needs improvement"
"Missing sources"
"Moat analysis weak"

✅ GOOD CRITIQUE:
"DCF growth rate of 8% is too aggressive given 5-year historical average of 3.2%.
Recommendation: Re-run DCF with 4% growth rate (conservative)."

"Owner Earnings calculation missing source. The analysis shows OCF=$700M and CapEx=$86M
but doesn't cite which 10-K filing these came from.
Recommendation: Add specific SEC filing URL and page numbers."

"Competitive moat section only mentions 'strong brand' without evidence.
Recommendation: Analyze: 1) Brand strength vs competitors (market share trends),
2) Customer switching costs (retention rates), 3) Pricing power (margin trends vs peers)."

Prioritize by SEVERITY:
- **CRITICAL**: Methodology errors, missing required calculations, no sources, hallucinated data
- **IMPORTANT**: Weak analysis, missing Buffett methodology elements, decision logic errors
- **MINOR**: Formatting issues, wording improvements, additional context

{"" if iteration < 1 else f'''
ITERATION {iteration + 1} FOCUS:
Since this is iteration {iteration + 1}, check if previous issues were actually FIXED:
- Don't repeat issues that were already addressed
- Focus on NEW issues or PERSISTENT problems that weren't fixed
- If progress was made, acknowledge it before listing remaining issues
'''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (JSON)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Respond with ONLY valid JSON (no markdown, no explanation):

{{
  "approved": true|false,
  "score": 0-100,

  "overall_assessment": "1-2 sentence summary of analysis quality and main issues",

  "strengths": [
    "Specific strength 1 (what's good about this analysis)",
    "Specific strength 2"
  ],

  "issues": [
    {{
      "severity": "critical|important|minor",
      "category": "methodology|calculations|data|moat|management|decision|thesis",
      "description": "Specific issue description",
      "how_to_fix": "Actionable steps to fix (be very specific)"
    }}
  ],

  "methodology_correct": true|false,
  "calculations_complete": true|false,
  "sources_adequate": true|false,
  "buffett_principles_followed": true|false,

  "recommendation": "approve|revise|reject"
}}

DECISION CRITERIA:
- **APPROVE** (approved: true): Score ≥ 85, no critical issues, methodology correct
- **REVISE** (approved: false): Score 50-84, fixable issues identified, show how to fix
- **REJECT** (approved: false): Score < 50, fundamental methodology errors

SCORING GUIDE ({analysis_type.upper()}):"""

    # Add type-specific scoring guidance
    if is_sharia_screen:
        prompt += """
- 90-100: Excellent screening, all criteria checked properly, well-sourced
- 80-89: Good screening, minor source or explanation issues
- 70-79: Adequate screening, some criteria need better verification
- 60-69: Weak screening, multiple criteria not properly checked
- 50-59: Poor screening, critical compliance checks missing
- 0-49: Unacceptable, fundamental screening errors or hallucinated data

For Sharia screens, CRITICAL issues include:
- Missing business activity screening
- Financial ratios not checked or hallucinated
- No sources for compliance data
- Incorrect pass/fail determination
"""
    elif is_quick_screen:
        prompt += """
- 90-100: Excellent quick screen, well-sourced thesis, clear recommendation
- 80-89: Good quick screen, minor citation or clarity issues in thesis
- 70-79: Adequate quick screen, some missing citations or shallow analysis in thesis
- 60-69: Weak quick screen, thesis missing sources or unclear recommendation
- 50-59: Poor quick screen, thesis has serious quality problems
- 0-49: Unacceptable, hallucinated data in thesis or no coherent analysis

**For Quick screens, remember:**
- **NULL values for owner_earnings, dcf_intrinsic_value, and margin_of_safety are EXPECTED and CORRECT**
- These advanced calculations are reserved for deep dives only
- **JSON parsing errors (intrinsic_value, current_price, decision mismatches) are MINOR issues**
- **Focus validation on THESIS TEXT quality, not JSON field accuracy**
- What matters: Are sources cited in thesis? Is reasoning sound? Is recommendation clear?
- Professional, analytical tone expected (Phase 9 framework-driven approach)
- DO NOT penalize for:
  - NULL or parsing errors in JSON fields
  - Using GuruFocus as primary source
  - Lack of deep 10-K analysis
  - Using simple valuation multiples (P/E, GF Value) instead of DCF

**CRITICAL issues for quick screens (thesis text):**
- No citations for financial metrics in thesis text
- Hallucinated data in thesis (wrong dates, impossible numbers)
- No clear INVESTIGATE/PASS recommendation in thesis
- Mentioning Owner Earnings/DCF without calculating them

**MINOR issues for quick screens:**
- JSON parsing errors (wrong intrinsic_value, current_price)
- Decision mismatch between JSON and thesis (if thesis is clear)
- margin_of_safety populated (should be NULL)
- Citations lack URLs or page numbers (as long as source type is stated)
"""
    else:  # deep_dive
        prompt += """
- 90-100: Excellent deep dive, all 4 calculations present, thorough analysis
- 80-89: Good deep dive, some important analysis gaps
- 70-79: Adequate deep dive, several important issues (missing calculations or weak moat analysis)
- 60-69: Weak deep dive, critical calculations missing or methodology errors
- 50-59: Poor deep dive, multiple critical issues
- 0-49: Unacceptable, fundamental methodology errors or hallucinated valuations

For Deep dives, CRITICAL issues include:
- Owner Earnings not calculated or wrong formula (using Net Income instead of OCF - CapEx)
- Missing any of the 4 calculations (Owner Earnings, ROIC, DCF, MoS)
- No sources cited for financial data
- Hallucinated valuations or financial data
"""

    prompt += """
Be tough! Warren Buffett's reputation is on the line.
Only approve truly excellent analysis (score ≥ 85).
"""

    return prompt


def _format_critique_issues(issues: List[Dict]) -> str:
    """
    Format critique issues for display in analyst prompt.

    Args:
        issues: List of issue dicts from validator

    Returns:
        Formatted string for display
    """
    if not issues:
        return "No issues found."

    formatted = []
    for i, issue in enumerate(issues, 1):
        severity = issue.get('severity', 'unknown').upper()
        category = issue.get('category', 'unknown')
        description = issue.get('description', '')
        how_to_fix = issue.get('how_to_fix', '')

        formatted.append(f"""
{i}. [{severity}] {category}
   Problem: {description}
   How to fix: {how_to_fix}
""")

    return "\n".join(formatted)


def get_improvement_guidance(previous_critique: Dict[str, Any]) -> str:
    """
    Build guidance section for analyst prompt when improving analysis.

    This is appended to the analyst's system prompt to guide improvements
    based on validator feedback.

    Args:
        previous_critique: Validator's critique from previous iteration

    Returns:
        Formatted guidance string
    """

    score = previous_critique.get('score', 0)
    assessment = previous_critique.get('overall_assessment', 'Issues found')
    issues = previous_critique.get('issues', [])

    guidance = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VALIDATOR FEEDBACK FROM PREVIOUS ITERATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your previous analysis was reviewed by a validator and received:

SCORE: {score}/100 (Need ≥85 to be approved)
ASSESSMENT: {assessment}

ISSUES TO FIX:
{_format_critique_issues(issues)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR TASK: FIX EVERY ISSUE ABOVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Don't just acknowledge the feedback - actually FIX the issues!

For each issue:
1. Re-run the appropriate tool (calculator_tool, gurufocus_tool, etc.)
2. Get the missing data or corrected calculation
3. Update the analysis with the fix
4. Add any missing sources or citations

The validator will check if you ACTUALLY fixed these issues.

IMPORTANT:
- If a calculation was wrong, re-run calculator_tool with correct methodology
- If a source was missing, add the specific URL and page number
- If analysis was shallow, provide deeper analysis with evidence
- If methodology was incorrect, follow Buffett methodology exactly

The validator approved analyses only score ≥85 with no critical issues.
Your goal: Address ALL feedback and improve the score above 85.
"""

    return guidance


def build_analysis_request_with_feedback(
    ticker: str,
    deep_dive: bool,
    years_to_analyze: int,
    previous_critique: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build user message for analyst with optional validator feedback.

    This is the message sent to the Warren Agent to request analysis.
    If previous_critique is provided, includes improvement guidance.

    Args:
        ticker: Company ticker
        deep_dive: Whether deep dive or quick screen
        years_to_analyze: Number of years to analyze
        previous_critique: Optional validator feedback from previous iteration

    Returns:
        User message string
    """

    analysis_type = "Deep Dive" if deep_dive else "Quick Screen"

    base_message = f"""Analyze {ticker} using Warren Buffett's investment principles.

Analysis Type: {analysis_type}
Years to Analyze: {years_to_analyze}

CRITICAL REQUIREMENTS:
1. Use calculator_tool for ALL financial calculations (Owner Earnings, ROIC, DCF, MoS)
2. Use gurufocus_tool to fetch financial data
3. Use sec_filing_tool to get 10-K documents
4. Use web_search_tool for company research
5. Cite ALL sources with specific URLs and page numbers
6. Show calculation methodology for all metrics
7. Follow strict Buffett methodology (OCF - CapEx for Owner Earnings, NOT Net Income)

You will be reviewed by a validator who checks your methodology and calculations.
"""

    if previous_critique:
        # This is an improvement iteration
        improvement_guidance = get_improvement_guidance(previous_critique)
        return base_message + improvement_guidance
    else:
        # This is the first iteration
        return base_message + "\nProvide a complete, high-quality analysis that would earn a validation score ≥85."


__all__ = [
    'get_validator_prompt',
    'get_improvement_guidance',
    'build_analysis_request_with_feedback',
    # Phase 9: Qualitative Analysis
    'get_moat_assessment_prompt',
    'get_management_quality_prompt',
    'get_competitive_position_prompt',
    'get_buffett_filters_prompt'
]


# =========================================================================
# PHASE 9: QUALITATIVE ANALYSIS PROMPTS
# =========================================================================

def get_moat_assessment_prompt(
    ticker: str,
    company_name: str,
    business_description: str,
    risk_factors: str
) -> str:
    """
    Phase 9: Moat assessment prompt using Buffett/Munger framework.

    Assesses competitive advantages across 5 categories:
    1. Intangible Assets (brand, patents, licenses, data)
    2. Switching Costs (customer lock-in)
    3. Network Effects (direct, indirect, data)
    4. Cost Advantages (scale, process, location)
    5. Efficient Scale (market saturation, regional monopoly)

    Args:
        ticker: Stock ticker
        company_name: Company name
        business_description: Item 1 from 10-K (full text)
        risk_factors: Item 1A from 10-K (full text)

    Returns:
        str: Structured prompt for LLM
    """
    return f"""
You are analyzing {company_name} ({ticker}) to assess its competitive moat using Warren Buffett and Charlie Munger's framework.

**10-K Business Description (Item 1):**
{business_description[:10000]}...
[Business description truncated for brevity]

**10-K Risk Factors (Item 1A):**
{risk_factors[:5000]}...
[Risk factors truncated for brevity]

---

**TASK: Assess the company's competitive moat across 5 categories.**

For each category, provide:
- **Score (0-3)**: Strong (3), Moderate (2), Weak (1), None (0)
- **Evidence**: Specific quotes or facts from the 10-K
- **Durability**: How long will this advantage last? (10+ years, 5-10 years, <5 years)

---

### 1. INTANGIBLE ASSETS (Brand, Patents, Licenses, Data)

**Questions to answer:**
- Does the company have strong brand value with pricing power?
- Are there patents or proprietary technology protecting from competition?
- Are there regulatory licenses creating barriers to entry (banking, pharma, utilities)?
- Does the company have unique datasets competitors can't replicate?

**Score:**
- Strong (3): Multiple intangible assets, clear pricing power
- Moderate (2): Some intangible assets, limited pricing power
- Weak (1): Few intangible assets, commoditized
- None (0): No meaningful intangible advantages

**Provide:**
- Score: [0-3]
- Evidence: [Specific examples from 10-K]
- Durability: [How long will this advantage last?]

---

### 2. SWITCHING COSTS (Customer Lock-In)

**Questions to answer:**
- Do customers face high friction when changing providers?
- Is the product deeply integrated into customer workflows?
- Are there long-term contracts or subscription models?
- Would switching require retraining, data migration, or process changes?

**Score:**
- Strong (3): Very high switching costs (enterprise software, mission-critical systems)
- Moderate (2): Moderate switching costs (some friction but possible)
- Weak (1): Low switching costs (easy to switch)
- None (0): No switching costs (commoditized)

**Provide:**
- Score: [0-3]
- Evidence: [Specific examples from 10-K]
- Durability: [How long will this advantage last?]

---

### 3. NETWORK EFFECTS (Product Value Increases with Users)

**Questions to answer:**
- Does product value increase as more users join (social networks, marketplaces)?
- Are there indirect network effects from complementary products (platforms, ecosystems)?
- Does the product improve with usage data (data network effects)?

**Score:**
- Strong (3): Strong, durable network effects (winner-take-most dynamics)
- Moderate (2): Moderate network effects (helpful but not dominant)
- Weak (1): Weak network effects (minimal advantage)
- None (0): No network effects

**Provide:**
- Score: [0-3]
- Evidence: [Specific examples from 10-K]
- Durability: [How long will this advantage last?]

---

### 4. COST ADVANTAGES (Scale, Process, Location)

**Questions to answer:**
- Does the company have lower unit costs from scale (manufacturing, distribution)?
- Are there proprietary processes or operational excellence?
- Are there location advantages (resource access, logistics)?
- Does the company have unique supplier relationships or vertical integration?

**Score:**
- Strong (3): Significant cost advantage (>20% lower than competitors)
- Moderate (2): Moderate cost advantage (10-20% lower)
- Weak (1): Small cost advantage (<10% lower)
- None (0): No cost advantage

**Provide:**
- Score: [0-3]
- Evidence: [Specific examples from 10-K]
- Durability: [How long will this advantage last?]

---

### 5. EFFICIENT SCALE (Market Saturation, Regional Monopoly)

**Questions to answer:**
- Is the market small enough to support only a few competitors?
- Are there geographic barriers preventing competition (regional monopolies)?
- Is the company dominant in a niche that's unattractive to larger competitors?

**Score:**
- Strong (3): Clear efficient scale dynamics (regional monopoly, utilities)
- Moderate (2): Some efficient scale benefits
- Weak (1): Limited efficient scale
- None (0): No efficient scale advantages

**Provide:**
- Score: [0-3]
- Evidence: [Specific examples from 10-K]
- Durability: [How long will this advantage last?]

---

**OUTPUT FORMAT (JSON):**

Return your assessment as valid JSON only (no markdown, no explanation):

{{
  "moat_assessment": {{
    "intangible_assets": {{
      "score": 3,
      "evidence": "Brand value: Customers willing to pay premium for products. Patents: 1,200+ patents in core technology.",
      "durability": "10+ years - Brand built over decades, patents extend for 15+ years"
    }},
    "switching_costs": {{
      "score": 2,
      "evidence": "Enterprise customers deeply integrated. Average customer tenure 7+ years.",
      "durability": "5-10 years - Integration depth creates friction, but new entrants could offer easier onboarding"
    }},
    "network_effects": {{
      "score": 0,
      "evidence": "No network effects. Product value doesn't increase with more users.",
      "durability": "N/A"
    }},
    "cost_advantages": {{
      "score": 2,
      "evidence": "Scale advantages in manufacturing. Unit costs 15% lower than competitors.",
      "durability": "5-10 years - Scale advantage persists but could be matched by large entrants"
    }},
    "efficient_scale": {{
      "score": 1,
      "evidence": "Niche market with limited growth potential. Market supports 3-4 players.",
      "durability": "5-10 years - Niche dynamics stable but could change with market growth"
    }},
    "overall_score": 8,
    "overall_assessment": "Narrow Moat",
    "key_advantages": [
      "Strong brand value with pricing power",
      "Customer integration creates switching costs",
      "Scale advantages in manufacturing"
    ],
    "vulnerabilities": [
      "No network effects - vulnerable to innovative entrants",
      "Limited efficient scale - market growing, attracting new competitors"
    ],
    "10yr_moat_durability": "Narrow Moat - Advantages are real but vulnerable to disruption from well-funded entrants or technology shifts"
  }}
}}

**CRITICAL INSTRUCTIONS:**
1. Be **rigorous and honest** - Most companies do NOT have wide moats
2. Use **specific evidence** from the 10-K, not generic statements
3. Assess **durability** - Will this advantage last 10+ years?
4. **Overall Score** = Sum of 5 category scores (max 15)
5. **Overall Assessment**:
   - Wide Moat (12-15): Multiple strong competitive advantages, durable for 10+ years
   - Narrow Moat (7-11): Some competitive advantages, durable for 5-10 years
   - No Moat (0-6): Few or no competitive advantages, vulnerable

Provide your analysis in the JSON format above. Return ONLY valid JSON.
"""


def get_management_quality_prompt(
    ticker: str,
    company_name: str,
    mda: str,
    roic_10yr: List[float],
    revenue_10yr: List[float],
    owner_earnings_10yr: List[float]
) -> str:
    """
    Phase 9: Management quality assessment prompt.

    Assesses management across 4 dimensions:
    1. Capital Allocation (ROIC, M&A, buybacks, dividends)
    2. Honesty & Transparency (candid about challenges, conservative accounting)
    3. Rationality (long-term focus, evidence-based, avoids fads)
    4. Owner Orientation (ownership stake, tenure, shareholder-friendly)

    Args:
        ticker: Stock ticker
        company_name: Company name
        mda: Item 7 from 10-K (full text)
        roic_10yr: 10 years of ROIC data (GuruFocus verified)
        revenue_10yr: 10 years of revenue data (GuruFocus verified)
        owner_earnings_10yr: 10 years of owner earnings (GuruFocus verified)

    Returns:
        str: Structured prompt for LLM
    """
    # Format financial data
    roic_str = ", ".join([f"{r:.1%}" if r else "N/A" for r in roic_10yr])
    revenue_str = ", ".join([f"${r/1000:.1f}B" if r else "N/A" for r in revenue_10yr])
    owner_earnings_str = ", ".join([f"${oe/1000:.1f}B" if oe else "N/A" for oe in owner_earnings_10yr])

    return f"""
You are analyzing {company_name} ({ticker}) to assess management quality using Warren Buffett's framework.

**10-K Management Discussion & Analysis (Item 7):**
{mda[:15000]}...
[MD&A truncated for brevity]

**10-Year Financial Performance (GuruFocus verified):**

**ROIC (Return on Invested Capital) - Last 10 Years:**
{roic_str}

**Revenue - Last 10 Years (in billions):**
{revenue_str}

**Owner Earnings - Last 10 Years (in billions):**
{owner_earnings_str}

---

**TASK: Assess management quality across 4 dimensions.**

For each dimension, provide:
- **Score (0-3)**: Excellent (3), Good (2), Mixed (1), Poor (0)
- **Evidence**: Specific examples from MD&A and financial performance
- **Red Flags**: Any concerning patterns or behaviors

[Rest of management quality prompt template - similar to moat prompt structure with JSON output]

Return ONLY valid JSON with your management assessment.
"""


def get_competitive_position_prompt(
    ticker: str,
    company_name: str,
    business_description: str,
    risk_factors: str
) -> str:
    """
    Phase 9: Competitive position assessment prompt.

    Assesses strategic position across 3 dimensions:
    1. Market Position (market share, competitive intensity, barriers)
    2. Strategic Positioning (differentiation, pricing power, innovation)
    3. Competitive Threats (disruption risk, new entrants, substitutes)

    Args:
        ticker: Stock ticker
        company_name: Company name
        business_description: Item 1 from 10-K (full text)
        risk_factors: Item 1A from 10-K (full text)

    Returns:
        str: Structured prompt for LLM
    """
    return f"""
You are analyzing {company_name} ({ticker}) to assess its competitive position.

**10-K Business Description (Item 1):**
{business_description[:10000]}...

**10-K Risk Factors (Item 1A):**
{risk_factors[:5000]}...

[Rest of competitive position prompt template with JSON output]

Return ONLY valid JSON with your competitive position assessment.
"""


def get_buffett_filters_prompt(
    ticker: str,
    company_name: str,
    business_description: str,
    roic_10yr: List[float],
    owner_earnings_10yr: List[float],
    current_market_cap: float
) -> str:
    """
    Phase 9: Buffett's filters prompt.

    Applies 3 core Buffett principles:
    1. Circle of Competence (Is business simple and understandable?)
    2. Predictability (Can we predict this business 10 years from now?)
    3. Margin of Safety (Is there sufficient discount to intrinsic value?)

    Args:
        ticker: Stock ticker
        company_name: Company name
        business_description: Item 1 from 10-K (full text)
        roic_10yr: 10 years of ROIC data (GuruFocus verified)
        owner_earnings_10yr: 10 years of owner earnings (GuruFocus verified)
        current_market_cap: Current market capitalization

    Returns:
        str: Structured prompt for LLM
    """
    # Calculate Owner Earnings Yield
    latest_owner_earnings = next((oe for oe in reversed(owner_earnings_10yr) if oe), None)
    owner_earnings_yield = (latest_owner_earnings / current_market_cap * 100) if latest_owner_earnings and current_market_cap else None

    roic_str = ", ".join([f"{r:.1%}" if r else "N/A" for r in roic_10yr])
    owner_earnings_str = ", ".join([f"${oe/1000:.1f}B" if oe else "N/A" for oe in owner_earnings_10yr])

    return f"""
You are applying Warren Buffett's core investment filters to {company_name} ({ticker}).

**10-K Business Description (Item 1):**
{business_description[:10000]}...

**10-Year Financial Data (GuruFocus verified):**

**ROIC - Last 10 Years:**
{roic_str}

**Owner Earnings - Last 10 Years (in billions):**
{owner_earnings_str}

**Current Market Cap:** ${current_market_cap/1000:.1f}B

**Latest Owner Earnings:** {f"${latest_owner_earnings/1000:.1f}B" if latest_owner_earnings else "N/A"}

**Owner Earnings Yield:** {f"{owner_earnings_yield:.1f}%" if owner_earnings_yield else "N/A"}

[Rest of Buffett filters prompt template with JSON output]

Return ONLY valid JSON with your Buffett filters assessment.
"""
