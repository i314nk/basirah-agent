# ARCHITECTURAL DECISION: Hybrid Calculator/GuruFocus Approach

**Date:** October 29, 2025  
**Decision Made By:** Strategic Planner + User  
**Status:** APPROVED  
**Impact:** Phase 2 (GuruFocus Tool) implementation  

---

## DECISION

**Adopt Hybrid Approach:** Use GuruFocus pre-calculated metrics for standard financial ratios, reserve Calculator Tool for specialized calculations unique to basīrah.

---

## CONTEXT

### The Question

GuruFocus API provides pre-calculated financial metrics including:
- Owner Earnings (Buffett's formula)
- ROIC (Return on Invested Capital)
- ROE, ROA, Gross Margin
- Debt ratios
- Historical trends (10 years)

**Question:** Should we use GuruFocus's calculations or recalculate everything ourselves using Calculator Tool?

### Options Considered

**Option A:** Use GuruFocus metrics exclusively
- Simplest approach
- Trust GuruFocus calculations
- Calculator Tool limited to DCF/MoS/Sharia only

**Option B:** Calculate everything ourselves
- Full transparency
- Complete control over formulas
- More complex integration

**Option C:** Hybrid approach ⭐ SELECTED
- Use GuruFocus for standard metrics (Owner Earnings, ROIC)
- Use Calculator for specialized calculations (DCF, MoS, Sharia, verification)
- Best balance of simplicity and control

---

## DECISION RATIONALE

### Why Hybrid Approach (Option C)

**1. GuruFocus Metrics Are Trusted**
- Used by thousands of investors
- Calculations are accurate and well-tested
- No need to reinvent the wheel for standard metrics
- Reduces complexity and potential for calculation errors

**2. Calculator Tool Still Essential**
- **DCF:** Our conservative Buffett-style model may differ from GuruFocus's approach
- **Margin of Safety:** Our specific thresholds (40%/25%/15%) may differ
- **Sharia Compliance:** Unique to basīrah, GuruFocus doesn't provide this
- **Verification:** Ability to recalculate if GuruFocus data seems wrong
- **What-if Scenarios:** Custom assumptions for sensitivity analysis

**3. Phase 1 Work Not Wasted**
- Calculator Tool provides value for specialized calculations
- DCF, Margin of Safety, Sharia Compliance are core differentiators
- Verification capability is valuable for data quality
- Clean, tested code we can trust and extend

**4. Simpler Integration**
- GuruFocus Tool can be simpler (less data extraction)
- Agent workflow is cleaner (fewer tool calls)
- Faster analysis (use pre-calculated metrics)
- Still flexible when needed (can verify via Calculator)

**5. Cost Efficiency**
- Fewer calculations = less code to maintain
- Fewer API calls (don't need all raw components)
- Faster agent execution

---

## CONSEQUENCES

### What This Means for Each Tool

**GuruFocus Tool (Phase 2):**
```python
# Returns both pre-calculated metrics AND raw data
{
    "success": True,
    "data": {
        # Pre-calculated metrics (use these by default)
        "owner_earnings": 97200000000,
        "owner_earnings_10y_avg": 85000000000,
        "roic": 0.28,
        "roic_10y_avg": 0.25,
        "roe": 0.45,
        "debt_to_equity": 1.2,
        
        # Raw financial data (for verification if needed)
        "financials": {
            "net_income": 99800000000,
            "depreciation_amortization": 11100000000,
            "capex": 10700000000,
            "working_capital_change": 3000000000
        },
        
        # Valuation data
        "price": 150.00,
        "market_cap": 2400000000000,
        
        # Metadata
        "source": "gurufocus",
        "ticker": "AAPL",
        "company_name": "Apple Inc."
    }
}
```

**Calculator Tool (Phase 1 - Already Complete):**
- Primary use: DCF valuation
- Primary use: Margin of Safety calculation
- Primary use: Sharia Compliance checking
- Secondary use: Verification of GuruFocus metrics
- Secondary use: What-if scenario analysis

**Agent Workflow:**
```python
# Phase 5: Financial Analysis - Use GuruFocus metrics
gf_data = gurufocus_tool.execute(ticker, endpoint="keyratios")
owner_earnings = gf_data["owner_earnings"]  # Use GuruFocus
roic = gf_data["roic"]  # Use GuruFocus

# Phase 6: Valuation - Use Calculator for DCF
dcf_result = calculator_tool.execute(
    calculation="dcf",
    data={"owner_earnings": owner_earnings, ...}  # GuruFocus input
)

# Phase 6: Margin of Safety - Use Calculator
mos_result = calculator_tool.execute(
    calculation="margin_of_safety",
    data={"intrinsic_value": dcf_value, "current_price": gf_data["price"]}
)

# Phase 8: Sharia - Use Calculator (unique to basīrah)
sharia_result = calculator_tool.execute(
    calculation="sharia_compliance_check",
    data=gf_data
)

# Verification (if suspicious data)
if owner_earnings < 0 or roic > 1.0:
    # Recalculate from raw data to verify
    verify_oe = calculator_tool.execute(
        calculation="owner_earnings",
        data=gf_data["financials"]
    )
```

---

## IMPLEMENTATION IMPACT

### Phase 2: GuruFocus Tool

**Simplified Requirements:**
- Return GuruFocus's pre-calculated metrics (primary data)
- Also include raw financial data (for verification)
- Handle special values (9999, 10000, 0)
- Organize data for agent consumption

**Don't Need:**
- Complex field extraction for Owner Earnings components
- Complex calculation logic (GuruFocus already did this)
- Duplicate Calculator Tool formulas

**Result:** Phase 2 is simpler and faster to implement

### Phase 3-4: Other Tools

**SEC Filing Tool:** Unchanged (qualitative analysis)
**Web Search Tool:** Unchanged (news, management, context)

### Phase 5: Agent Core

**Agent Decision Logic:**
```
1. Call GuruFocus Tool → Get pre-calculated metrics
2. Evaluate using Buffett criteria (thresholds from BUFFETT_PRINCIPLES.md)
3. If passes initial screens:
   → Call Calculator for DCF valuation (our model)
   → Call Calculator for Margin of Safety (our thresholds)
   → Call Calculator for Sharia Compliance (unique check)
4. Make BUY/WATCH/AVOID decision
```

---

## BENEFITS

**✅ Simpler Integration**
- GuruFocus metrics used directly
- Fewer data extraction steps
- Cleaner agent workflow

**✅ Trusted Data**
- GuruFocus calculations are well-tested
- Used by investment community
- Reduces calculation error risk

**✅ Calculator Still Valuable**
- DCF with our conservative assumptions
- Margin of Safety with our thresholds
- Sharia Compliance (unique differentiator)
- Verification when needed

**✅ Faster Execution**
- Fewer tool calls
- Less computation
- Quicker analysis

**✅ Cost Efficiency**
- Less code to maintain
- Fewer API fields needed
- Reduced complexity

---

## TRADE-OFFS ACCEPTED

**❌ Less Transparency for Owner Earnings/ROIC**
- We don't see exact formula GuruFocus uses
- Mitigation: Can verify using Calculator if suspicious

**❌ Dependency on GuruFocus Calculations**
- Trust their methodology
- Mitigation: Calculator provides verification capability

**❌ Some Calculator Code Underutilized**
- Owner Earnings and ROIC calculations less used
- Mitigation: Still valuable for verification and what-if scenarios

**Assessment:** Trade-offs are acceptable given benefits

---

## VERIFICATION STRATEGY

**When to Use Calculator for Verification:**

```python
# Check if GuruFocus data is suspicious
def should_verify(gf_data):
    suspicious = False
    
    # Owner Earnings checks
    if gf_data["owner_earnings"] < 0:
        suspicious = True  # Verify negative OE
    if abs(gf_data["owner_earnings"]) > gf_data["revenue"]:
        suspicious = True  # OE shouldn't exceed revenue
    
    # ROIC checks
    if gf_data["roic"] < 0 or gf_data["roic"] > 1.0:
        suspicious = True  # ROIC outside normal range
    
    # Special values
    if gf_data["owner_earnings"] in [9999, 10000]:
        suspicious = True  # Special value codes
    
    return suspicious

# Agent logic
gf_data = gurufocus_tool.execute(ticker)

if should_verify(gf_data):
    # Recalculate using Calculator Tool
    verified_oe = calculator_tool.execute(
        calculation="owner_earnings",
        data=gf_data["financials"]
    )
    owner_earnings = verified_oe["result"]  # Use verified value
else:
    owner_earnings = gf_data["owner_earnings"]  # Use GuruFocus
```

---

## SUCCESS METRICS

**Phase 2 Implementation:**
- [ ] GuruFocus Tool returns pre-calculated metrics
- [ ] GuruFocus Tool also provides raw data
- [ ] Agent successfully uses GuruFocus metrics
- [ ] Calculator DCF integrates with GuruFocus data
- [ ] Calculator Sharia Compliance works with GuruFocus data
- [ ] Verification flow works when needed

**Overall System:**
- [ ] Analysis is faster (fewer calculations)
- [ ] Results are accurate (verified against known companies)
- [ ] Code is simpler (less duplication)
- [ ] All tools integrate smoothly

---

## REVIEW AND ADAPTATION

**Review Point:** After Phase 5 (Agent Core) complete

**Questions to Ask:**
1. Are GuruFocus metrics accurate? (compare to manual calculations)
2. Do we need verification often? (if yes, may need more Calculator use)
3. Is DCF model working well? (validate against known valuations)
4. Is Sharia Compliance accurate? (cross-check with Zoya app)

**Adaptation Strategy:**
- If GuruFocus metrics prove unreliable → Increase Calculator usage
- If verification never needed → Can simplify further
- If DCF assumptions need tuning → Adjust Calculator defaults

**Flexibility:** Architecture allows us to shift between GuruFocus and Calculator as needed

---

## DOCUMENTATION UPDATES NEEDED

**✅ Phase 2 GuruFocus Tool Spec:** Emphasize returning pre-calculated metrics
**✅ Phase 5 Agent Core Spec:** Update workflow to use GuruFocus metrics first
**⏸️ Calculator Tool Spec:** No changes needed (already complete)
**⏸️ Architecture.md:** Update investigation workflow (minor adjustments)

---

## CONCLUSION

**Decision:** Hybrid approach using GuruFocus pre-calculated metrics + Calculator for specialized calculations

**Status:** APPROVED and will be implemented in Phase 2

**Next Steps:**
1. Proceed with Phase 2 (GuruFocus Tool) using hybrid approach
2. GuruFocus Tool returns both pre-calculated metrics and raw data
3. Agent uses GuruFocus metrics by default
4. Calculator reserved for DCF, Margin of Safety, Sharia, verification

**Expected Outcome:** Simpler, faster system that leverages GuruFocus's trusted calculations while maintaining unique basīrah capabilities (Sharia compliance, conservative DCF model)

---

**ARCHITECTURAL DECISION APPROVED**

**Date:** October 29, 2025  
**Approver:** Strategic Planner + User  
**Implementation:** Phase 2 onwards
