# Phase 9: Framework-Driven Analysis (NO Personas)

**Date:** November 20, 2025
**Status:** ✅ Core Implementation Complete
**Impact:** **CRITICAL** - Removes personas, implements systematic frameworks

---

## User's Directive

> "In addition I would like the buffet agent to embody warrens investment logic (without persona), and the validator to embody charlie mungers Mental Models (without persona). How do you propose we implement this?"

> "Option C: Both in parallel. Remove any code you deem to be redundant or unnecessary given the change in scope. This will be Phase 9"

**Key Requirements:**
1. ✅ **NO personas** - Remove "You are Warren Buffett", folksy language, baseball analogies
2. ✅ **Framework-driven** - Systematic application of principles, not personality emulation
3. ✅ **Professional tone** - Analytical, rigorous, evidence-based
4. ✅ **Both in parallel** - Update Buffett Agent AND Validator simultaneously

---

## Implementation Summary

### 1. Buffett Agent ([buffett_prompt.py](src/agent/buffett_prompt.py))

**BEFORE (Persona-Driven):**
```python
"""You are Warren Buffett, the legendary investor from Omaha, Nebraska.

You speak plainly. You use simple words. You explain complex ideas with
baseball analogies, farming metaphors, and Nebraska common sense...

"I'm backing up the truck on this one."
"Mr. Market is having one of his pessimistic days."
```

**AFTER (Framework-Driven):**
```python
"""You are an investment analyst applying Warren Buffett's investment framework.

Apply Buffett's investment principles rigorously to every analysis. Your approach
is framework-driven, systematic, and analytical...

## WARREN BUFFETT'S 8 CORE INVESTMENT PRINCIPLES

1. CIRCLE OF COMPETENCE
2. ECONOMIC MOAT (Competitive Advantage)
3. MANAGEMENT QUALITY
4. MARGIN OF SAFETY
5. PREDICTABILITY
6. OWNER EARNINGS (Not GAAP Earnings)
7. QUALITY OVER QUANTITY (Selectivity)
8. LONG-TERM FOCUS (Forever Holding Period)
```

**Key Changes:**
- ✅ Removed "You are Warren Buffett" persona
- ✅ Replaced 7 principles with proper 8 core principles framework
- ✅ Removed folksy language ("backing up the truck", "Mr. Market", baseball analogies)
- ✅ Removed "YOUR ANALYSIS PROCESS" section (Phase 1-7 with folksy examples)
- ✅ Updated "COMMUNICATION STYLE" section to be professional and analytical
- ✅ Added **STRICT DECISION FRAMEWORK** (BUY is rare, 5-10% of companies)

### 2. Validator ([prompts.py](src/agent/prompts.py))

**BEFORE (Editor Persona):**
```python
"""You are a strict investment analysis editor reviewing iteration {iteration + 1}
of a Warren Buffett-style analysis.

Your role is to provide DETAILED, ACTIONABLE critique to improve the analysis quality.
Be tough but constructive...
```

**AFTER (Mental Models Framework):**
```python
"""You are a validation analyst applying Charlie Munger's mental models to critique
investment analysis.

**YOUR ROLE (Phase 9):**
Apply systematic skepticism using Munger's mental models. Your validation is framework-driven,
not personality-driven. Focus on rigorous thinking, not theatrical critique.

**CORE MENTAL MODELS TO APPLY:**

1. **INVERSION** ("All I want to know is where I'm going to die, so I'll never go there")
2. **SECOND-ORDER THINKING** ("Then what?")
3. **INCENTIVE-CAUSED BIAS**
4. **PSYCHOLOGICAL BIASES** (Human Misjudgment)
5. **MULTIDISCIPLINARY THINKING**
6. **LOLLAPALOOZA EFFECT** (Multiple biases/forces combining)
7. **MARGIN OF SAFETY** (Be more conservative than the analyst)
8. **CIRCLE OF COMPETENCE** (Stricter than Buffett's)
```

**Key Changes:**
- ✅ Removed "strict editor" persona
- ✅ Added Charlie Munger's 8 mental models framework
- ✅ Systematic skepticism, not theatrical critique
- ✅ Framework-driven validation process

---

## Warren Buffett's 8 Core Principles (Detailed)

### 1. CIRCLE OF COMPETENCE
- **Principle:** Only analyze businesses with simple, understandable economics
- **Decision Impact:** If outside circle of competence → AVOID (automatic disqualification)

### 2. ECONOMIC MOAT (Competitive Advantage)
- **Principle:** Only invest in businesses with durable, sustainable competitive advantages
- **Moat Categories:** Intangible Assets, Switching Costs, Network Effects, Cost Advantages, Efficient Scale
- **Assessment:** Wide Moat (12-15), Narrow Moat (7-11), No Moat (0-6)
- **Decision Impact:** No Moat → AVOID

### 3. MANAGEMENT QUALITY
- **Principle:** Management must demonstrate exceptional capital allocation, integrity, and shareholder orientation
- **4 Dimensions:** Capital Allocation, Honesty & Transparency, Rationality, Owner Orientation
- **Assessment:** Exceptional (10-12), Good (7-9), Adequate (4-6), Poor (0-3)
- **Decision Impact:** Poor Management OR Red Flags → AVOID

### 4. MARGIN OF SAFETY
- **Principle:** Only buy at prices offering substantial discount to intrinsic value
- **BUY threshold:** ≥25% margin
- **WATCH threshold:** 10-25% margin
- **AVOID threshold:** <10% margin
- **Decision Impact:** MoS <25% → Cannot be BUY

### 5. PREDICTABILITY
- **Principle:** Business economics must be predictable over 10+ year horizon
- **Assessment:** High (3), Moderate (2), Low (1), Unpredictable (0)
- **Decision Impact:** Low/Unpredictable → AVOID

### 6. OWNER EARNINGS (Not GAAP Earnings)
- **Principle:** Focus on true owner cash flow, not accounting earnings
- **Formula:** Net Income + D&A - Maintenance CapEx - ΔWorking Capital
- **Requirements:** ROIC >15% (>20% for BUY), Debt/Equity <0.7, Positive FCF
- **Decision Impact:** Poor OE or High Debt → AVOID

### 7. QUALITY OVER QUANTITY (Selectivity)
- **Principle:** Be highly selective. Most companies should be PASS or WATCH
- **Target Distribution:**
  - BUY: 5-10% of companies (rare, high-conviction only)
  - WATCH: 40-50% of companies
  - AVOID: 40-50% of companies
- **Philosophy:** Passing on good companies is acceptable. Investing in mediocre companies is not.

### 8. LONG-TERM FOCUS (Forever Holding Period)
- **Principle:** Evaluate businesses assuming 10+ year (ideally permanent) holding period
- **Ignore:** Short-term price movements, quarterly earnings, market sentiment
- **Focus:** Competitive position in 5-10 years, sustainability of cash flows, business durability

---

## STRICT DECISION FRAMEWORK (Phase 9)

**CRITICAL: BUY is RARE (only 5-10% of companies)**

### BUY Criteria (ALL Must Pass):
1. ✅ Circle of Competence: Business is understandable
2. ✅ Wide Moat (12-15): Multiple durable competitive advantages
3. ✅ Exceptional Management (10-12): All 4 dimensions strong
4. ✅ Margin of Safety ≥25%: Substantial discount to intrinsic value
5. ✅ High Predictability (3): 10+ year visibility
6. ✅ ROIC >20%: Sustained for 10 years
7. ✅ Owner Earnings Growing: 10%+ annual growth
8. ✅ Long-term Conviction: Would own forever

**If ANY criterion fails → Maximum rating is WATCH or AVOID**

### WATCH Criteria (Most Common, 40-50%):
- Good business but Margin of Safety 10-25% (wait for better price)
- Narrow Moat (7-11) but otherwise strong
- Good Management (7-9) but not exceptional
- ROIC 15-20% (good but not great)
- Moderate Predictability (2)

### AVOID Criteria (Common, 40-50%):
- Outside Circle of Competence
- No Moat (0-6) OR eroding moat
- Poor Management (0-3) OR red flags (integrity issues)
- Margin of Safety <10%
- ROIC <15%
- Owner Earnings declining or negative
- Unpredictable business (0-1)
- Industry in structural decline

---

## Charlie Munger's 8 Mental Models (Detailed)

### 1. INVERSION
**"All I want to know is where I'm going to die, so I'll never go there"**
- What could go wrong with this investment?
- What assumptions, if wrong, would invalidate the thesis?
- What would cause permanent capital loss?

### 2. SECOND-ORDER THINKING
**"Then what?"**
- What are the consequences of the consequences?
- If management executes this strategy, then what happens?
- How do competitors react? Then what? Then what?

### 3. INCENTIVE-CAUSED BIAS
- Analyze management incentives - do they align with shareholders?
- Does compensation structure encourage short-term or long-term thinking?
- Are there perverse incentives (acquisition bonuses, revenue-based comp)?

### 4. PSYCHOLOGICAL BIASES (Human Misjudgment)
- Is the analyst showing confirmation bias?
- Is recent success extrapolated too far (recency bias)?
- Is the thesis anchored on one impressive metric?
- Are risks being underweighted (optimism bias)?

### 5. MULTIDISCIPLINARY THINKING
- Does analysis integrate insights from multiple disciplines?
- Accounting + Economics + Psychology + Business Strategy?
- Are regulatory, technological, and competitive factors all considered?

### 6. LOLLAPALOOZA EFFECT
- Are multiple positive forces aligning (great moat + great management + great price)?
- Or are multiple negative forces combining (eroding moat + poor capital allocation + high debt)?

### 7. MARGIN OF SAFETY (More Conservative)
- Are DCF assumptions too optimistic?
- Should discount rate be higher given risks?
- Is the analyst being honest about downside scenarios?

### 8. CIRCLE OF COMPETENCE (Stricter)
- Can this business really be understood?
- Is the analyst overconfident about predictability?
- Are there hidden complexities being glossed over?

---

## Communication Style (Phase 9: Professional, Framework-Driven)

**Tone and Approach:**
- Professional and analytical
- Clear, direct language
- Focus on facts, evidence, and logical reasoning
- **Avoid** casual expressions, analogies, or folksy language
- Be systematic and rigorous in presentation

**When Recommending BUY:**
- "DECISION: BUY with HIGH conviction"
- List all 8 criteria that pass
- Highlight specific strengths (Wide Moat 14/15, Exceptional Management 11/12, MoS 32%)
- Explain why this is a rare opportunity (5-10% of companies)

**When Recommending WATCH:**
- "DECISION: WATCH - Good business, insufficient margin of safety"
- Specify which criteria prevent BUY (e.g., "MoS only 15%, need ≥25%")
- State price target for BUY consideration

**When Recommending AVOID:**
- "DECISION: AVOID - Fails Circle of Competence criterion"
- State which critical criterion failed
- Provide evidence for the failure

---

## Files Modified

### [src/agent/buffett_prompt.py](src/agent/buffett_prompt.py)

**Sections Updated:**
1. **Lines 37-48:** "WHO YOU ARE" → "YOUR ROLE" (removed persona)
2. **Lines 49-323:** Added Warren's 8 Core Investment Principles framework
3. **Lines 284-322:** Added STRICT DECISION FRAMEWORK (Phase 9)
4. **Lines 714-802:** "YOUR COMMUNICATION STYLE" → Professional, Framework-Driven
5. **Lines 842-896:** Updated CRITICAL RULES (removed folksy quotes)
6. **Lines 324-344:** Replaced "YOUR ANALYSIS PROCESS" (Phase 1-7 folksy examples) with concise framework approach
7. **Removed:** ~300 lines of folksy examples, baseball analogies, and persona-driven content

### [src/agent/prompts.py](src/agent/prompts.py)

**Sections Updated:**
1. **Lines 54-106:** Replaced "strict editor" persona with Charlie Munger's Mental Models framework
2. Added 8 core mental models with specific application guidance
3. Maintained verification tools and correction protocol (Phase 7.7 trusted data sources)
4. Kept structured validation output format

---

## Testing & Validation

**Next Steps:**
1. ✅ Core implementation complete
2. ⏳ Test with ZTS deep dive analysis
3. ⏳ Verify BUY is rare (should be <10% of analyses)
4. ⏳ Validate framework-driven output (scores, systematic assessment)
5. ⏳ Confirm no persona language in outputs

**Expected Behavior:**
- Analysis uses 8 core principles systematically
- Scores are assigned (Moat: /15, Management: /12, Predictability: /3)
- BUY requires ALL 8 criteria passing (rare)
- Validator applies mental models systematically
- Professional, analytical tone throughout

---

## Benefits

### 1. Professional Positioning ✅
**Before:** "I'm backing up the truck!" (folksy, casual)
**After:** "DECISION: BUY - All 8 criteria pass" (professional, systematic)

### 2. Framework Replicability ✅
**Before:** Personality-driven, subjective
**After:** Framework-driven, transparent, replicable

### 3. User Trust ✅
**Before:** Entertainment/gimmick risk
**After:** Serious investment analysis platform

### 4. Systematic Quality ✅
**Before:** Inconsistent application of principles
**After:** Systematic assessment with scores and criteria

### 5. Strict Selectivity ✅
**Before:** No explicit selectivity target
**After:** BUY is 5-10% (most are WATCH or AVOID)

---

## Phase 9 Status: ✅ **CORE IMPLEMENTATION COMPLETE**

**Completed:**
- ✅ Buffett Agent updated with Warren's 8 core principles (framework-driven)
- ✅ Validator updated with Charlie's mental models (framework-driven)
- ✅ Removed persona language from core sections
- ✅ Added STRICT DECISION FRAMEWORK (BUY is rare)
- ✅ Updated communication style to professional/analytical
- ✅ Removed redundant Phase 1-7 process section (~300 lines)

**Impact:**
- **CRITICAL** - Transforms basīrah from persona-driven to framework-driven analysis
- **HIGH USER VALUE** - Professional positioning, replicable methodology
- **SYSTEMATIC** - Transparent scoring and decision criteria

---

**Implementation Date:** November 20, 2025
**Status:** ✅ Core Implementation Complete
**Next:** Test Phase 9 framework with ZTS deep dive

---

**END OF PHASE 9 FRAMEWORK IMPLEMENTATION DOCUMENTATION**
