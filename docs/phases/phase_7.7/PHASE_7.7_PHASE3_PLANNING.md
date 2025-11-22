# Phase 7.7 Phase 3: Qualitative Insights Extraction - Planning Document

**Date:** November 16, 2025
**Status:** 📋 PLANNING
**Estimated Time:** 1-2 weeks (2-3 hours for Phase 3.1, 1-2 weeks for Phase 3.2)
**Depends On:** Phase 2 (Structured Metrics Extraction) ✅ Complete

---

## Executive Summary

Phase 3 extracts **qualitative insights** from LLM analysis text and structures them into `AnalysisInsights` objects. This complements Phase 2's quantitative metrics extraction, enabling a complete hybrid analysis architecture.

**Two-Phase Approach:**
1. **Phase 3.1: Text Parsing Prototype** (2-3 hours) - Quick win for validation
2. **Phase 3.2: Structured LLM Output** (1-2 weeks) - Production-ready solution

---

## Goals

### Primary Goals

1. **Extract Qualitative Assessments** from existing analysis text
   - Business model understanding
   - Economic moat evaluation (STRONG/MODERATE/WEAK)
   - Management quality assessment
   - Risk analysis (LOW/MODERATE/HIGH)
   - Decision rationale

2. **Provide Structured Insights** in final result metadata
   - `structured_insights` with same 3-view structure as metrics
   - `current_year`, `prior_years`, `all_years` views
   - Enable trend tracking for qualitative factors

3. **Foundation for Phase 4** (Synthesis Optimization)
   - Provide both metrics + insights to synthesis
   - Enable hybrid quantitative + qualitative analysis
   - Improve synthesis quality and speed

### Secondary Goals

4. **Backward Compatibility** - No breaking changes to existing analyses
5. **Graceful Degradation** - Return empty insights if extraction fails
6. **Easy to Test** - Independent testing of extraction logic

---

## Phase 3.1: Text Parsing Prototype

**Goal:** Quick prototype to validate structured insights provide value
**Time:** 2-3 hours
**Approach:** Parse existing thesis text using pattern matching

### Fields to Extract (Priority Order)

**High Priority (Core Insights):**
1. `decision` - BUY/WATCH/AVOID
2. `conviction` - HIGH/MODERATE/LOW
3. `moat_rating` - STRONG/MODERATE/WEAK
4. `risk_rating` - LOW/MODERATE/HIGH
5. `primary_risks` - List of key risks
6. `moat_sources` - List of moat types

**Medium Priority (Detailed Assessments):**
7. `business_model` - How business makes money (first paragraph)
8. `management_assessment` - Management evaluation summary
9. `decision_reasoning` - Why BUY/WATCH/AVOID

**Low Priority (Advanced Insights):**
10. `integrity_evidence` - Evidence of management integrity
11. `red_flags` - Management concerns
12. `discount_rate_reasoning` - DCF assumptions rationale

### Text Parsing Patterns

**Pattern 1: Decision & Conviction**
```
Decision: BUY | WATCH | AVOID
Conviction: HIGH | MODERATE | LOW
```
- Look for: "Decision:", "Conviction:", "Recommendation:"
- Extract: Uppercase word after colon

**Pattern 2: Rating Fields**
```
Economic Moat: STRONG | MODERATE | WEAK
Risk Level: LOW | MODERATE | HIGH
```
- Look for: "Economic Moat:", "Risk Level:", "Risk Assessment:"
- Extract: Uppercase word after colon

**Pattern 3: List Extraction**
```
Key Risks:
- Risk 1
- Risk 2
- Risk 3

Moat Sources:
• Brand power
• Switching costs
• Network effects
```
- Look for section headers + bullet points
- Extract list items (-, •, *, 1., etc.)

**Pattern 4: Section Extraction**
```
Business Model:
[First 1-2 paragraphs of business model section]

Management Quality:
[Summary paragraph]
```
- Look for section headers
- Extract following paragraph(s) until next header

### Implementation Approach

**Step 1: Create Extraction Function**
```python
def _extract_insights_from_analysis(
    self,
    ticker: str,
    year: int,
    analysis_text: str
) -> Dict[str, Any]:
    """
    Extract qualitative insights from analysis text.

    Returns dictionary of AnalysisInsights fields.
    """
    insights = AnalysisInsights()

    # Extract decision & conviction
    decision_match = re.search(r'Decision:\s*(BUY|WATCH|AVOID)', analysis_text, re.I)
    if decision_match:
        insights.decision = decision_match.group(1).upper()

    # Extract moat rating
    moat_match = re.search(r'(?:Economic Moat|Moat Rating):\s*(STRONG|MODERATE|WEAK)', analysis_text, re.I)
    if moat_match:
        insights.moat_rating = moat_match.group(1).upper()

    # Extract risk rating
    risk_match = re.search(r'(?:Risk Level|Risk Assessment):\s*(LOW|MODERATE|HIGH)', analysis_text, re.I)
    if risk_match:
        insights.risk_rating = risk_match.group(1).upper()

    # Extract primary risks (list)
    risks = self._extract_bullet_list(analysis_text, r'(?:Key Risks|Primary Risks):')
    if risks:
        insights.primary_risks = risks

    # Extract moat sources (list)
    moat_sources = self._extract_bullet_list(analysis_text, r'(?:Moat Sources|Sources of Moat):')
    if moat_sources:
        insights.moat_sources = moat_sources

    # Log extraction results
    insights_count = len([v for v in insights.to_dict().values() if v])
    logger.info(f"[INSIGHTS] Extracted {insights_count} insights for {ticker} ({year})")

    return insights.to_dict()
```

**Step 2: Helper Functions**
```python
def _extract_bullet_list(self, text: str, header_pattern: str) -> List[str]:
    """Extract bulleted list following a header."""
    # Find header
    header_match = re.search(header_pattern, text, re.I)
    if not header_match:
        return []

    # Extract text after header
    start = header_match.end()
    # Find next section header or end of text
    next_section = re.search(r'\n\n[A-Z][a-z]+:', text[start:])
    end = start + next_section.start() if next_section else len(text)
    section_text = text[start:end]

    # Extract bullet points
    bullets = re.findall(r'[-•*]\s*(.+)', section_text)
    return [b.strip() for b in bullets if b.strip()]
```

**Step 3: Integration Points**
- After Stage 1 current year analysis
- After Stage 2 prior year summaries
- Before final result assembly

**Step 4: Final Result Structure**
```json
{
  "decision": "WATCH",
  "thesis": "...",
  "metadata": {
    "structured_metrics": { ... },
    "structured_insights": {
      "current_year": {
        "year": 2024,
        "insights": {
          "decision": "WATCH",
          "conviction": "MODERATE",
          "moat_rating": "MODERATE",
          "risk_rating": "MODERATE",
          "primary_risks": ["Market concentration", "Commodity costs"],
          "moat_sources": ["Brand power", "Switching costs"]
        }
      },
      "prior_years": [
        {
          "year": 2023,
          "insights": { ... }
        }
      ],
      "all_years": [
        {"year": 2024, "insights": { ... }},
        {"year": 2023, "insights": { ... }}
      ]
    }
  }
}
```

### Testing Approach

**Test 1: Unit Test Extraction**
```python
def test_extract_insights():
    agent = WarrenBuffettAgent()

    sample_text = """
    Decision: WATCH
    Conviction: MODERATE
    Economic Moat: MODERATE
    Risk Level: MODERATE

    Key Risks:
    - Market concentration in residential water heaters
    - Commodity cost fluctuations
    - Regulatory changes
    """

    insights = agent._extract_insights_from_analysis("AOS", 2024, sample_text)

    assert insights["decision"] == "WATCH"
    assert insights["conviction"] == "MODERATE"
    assert insights["moat_rating"] == "MODERATE"
    assert insights["risk_rating"] == "MODERATE"
    assert len(insights["primary_risks"]) == 3
```

**Test 2: Integration Test**
```python
def test_phase3_insights_extraction():
    agent = WarrenBuffettAgent()
    result = agent.analyze_company("AOS", deep_dive=True, years_to_analyze=2)

    # Check structured_insights exists
    assert "structured_insights" in result["metadata"]

    # Check structure
    insights = result["metadata"]["structured_insights"]
    assert "current_year" in insights
    assert "prior_years" in insights
    assert "all_years" in insights

    # Check current year has insights
    current = insights["current_year"]
    assert current["year"] == 2024
    assert "insights" in current
    assert len(current["insights"]) > 0
```

### Success Criteria (Phase 3.1)

- [ ] Extraction function implemented
- [ ] Extracts 5+ high-priority insights
- [ ] Integrated into Stage 1 and Stage 2
- [ ] `structured_insights` in final result
- [ ] Test passes with real analysis
- [ ] No breaking changes

### Expected Results

**Extraction Accuracy:**
- Decision/Conviction: 95%+ (highly structured)
- Moat/Risk Rating: 80-90% (somewhat structured)
- Lists (risks, moat sources): 60-80% (format-dependent)
- Free text (business model): 40-60% (variable quality)

**Overall Success:** If we extract 5+ insights per year, Phase 3.1 is successful

---

## Phase 3.2: Structured LLM Output

**Goal:** Production-ready solution with high accuracy
**Time:** 1-2 weeks
**Approach:** Update prompts to request structured output from LLM

### Design Approach

**Option A: Response Schema (Preferred)**
- Define JSON schema for `AnalysisInsights`
- Request LLM to follow schema in response
- Parse JSON from response
- Fallback to text parsing if JSON parsing fails

**Option B: Function Calling**
- Define `provide_insights()` function with AnalysisInsights parameters
- LLM calls function with structured data
- Extract insights from function call arguments
- Fallback to text parsing if no function call

**Option C: Two-Pass Analysis**
- First pass: Standard analysis (current behavior)
- Second pass: Extract insights using separate LLM call
- Trade-off: More tokens, better accuracy

**Recommendation:** Start with Option A (Response Schema), fallback to Option C if needed

### Implementation Plan

**Week 1: Design & Prototype**
1. **Day 1-2:** Design structured output schema
   - Define JSON schema for AnalysisInsights
   - Create prompt templates
   - Test with simple examples

2. **Day 3-4:** Implement schema-based extraction
   - Update system prompts to request JSON
   - Implement JSON parsing with error handling
   - Add fallback to Phase 3.1 text parsing

3. **Day 5:** Initial testing
   - Test with 3-5 companies
   - Measure extraction accuracy
   - Identify failure modes

**Week 2: Refinement & Testing**
4. **Day 6-8:** Quality improvements
   - Refine prompts based on failures
   - Add validation for extracted insights
   - Improve error handling

5. **Day 9-10:** Comprehensive testing
   - Test with 10+ companies
   - Test edge cases (REITs, financials, tech)
   - Validate multi-year consistency

6. **Day 11-12:** Documentation & deployment
   - Document implementation
   - Update Phase 3 summary
   - Mark Phase 3 complete

### Prompt Engineering Strategy

**System Prompt Addition:**
```
IMPORTANT: After your analysis, provide structured insights in JSON format:

{
  "decision": "BUY|WATCH|AVOID",
  "conviction": "HIGH|MODERATE|LOW",
  "moat_rating": "STRONG|MODERATE|WEAK",
  "risk_rating": "LOW|MODERATE|HIGH",
  "primary_risks": ["risk1", "risk2", ...],
  "moat_sources": ["source1", "source2", ...],
  "business_model": "How the business makes money",
  "management_assessment": "Management quality evaluation",
  "decision_reasoning": "Why BUY/WATCH/AVOID"
}

Place this JSON block after your full written analysis.
```

**Validation Rules:**
- decision must be one of: BUY, WATCH, AVOID
- conviction must be one of: HIGH, MODERATE, LOW
- moat_rating must be one of: STRONG, MODERATE, WEAK
- risk_rating must be one of: LOW, MODERATE, HIGH
- Lists must have at least 1 item
- Text fields must be non-empty strings

### Success Criteria (Phase 3.2)

- [ ] Structured output schema implemented
- [ ] Prompts updated and tested
- [ ] Extraction accuracy >90% for ratings
- [ ] Extraction accuracy >80% for lists
- [ ] Fallback to text parsing works
- [ ] Tested with 10+ companies
- [ ] No breaking changes
- [ ] Full documentation complete

### Expected Results

**Extraction Accuracy (Phase 3.2):**
- Decision/Conviction: 98%+ (LLM explicitly provides)
- Moat/Risk Rating: 95%+ (LLM explicitly provides)
- Lists (risks, moat sources): 90%+ (structured JSON)
- Text (business model, reasoning): 95%+ (structured JSON)

**Overall Success:** >90% of insights correctly extracted across all companies

---

## Benefits

### Phase 3.1 Benefits

1. **Quick Validation** - Know if structured insights are useful (2-3 hours)
2. **Immediate Value** - Works with existing analyses (no prompt changes)
3. **Low Risk** - Additive only, backward compatible
4. **Foundation** - Infrastructure for Phase 3.2

### Phase 3.2 Benefits

1. **High Accuracy** - 90%+ extraction accuracy (vs 60-80% for text parsing)
2. **Comprehensive** - Extract 15+ insights per year (vs 5-8 for text parsing)
3. **Consistent** - Structured format guaranteed
4. **Flexible** - Easy to add new insight fields
5. **Production-Ready** - Reliable for user-facing features

### Combined Benefits (Phase 3 Complete)

6. **Hybrid Analysis** - Quantitative metrics + qualitative insights together
7. **Trend Tracking** - Track qualitative changes over time
8. **Better Synthesis** - Phase 4 can use structured data
9. **Programmatic Validation** - Check qualitative criteria automatically
10. **UI/UX Ready** - Structured data perfect for dashboards

---

## Risk Assessment

### Phase 3.1 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Low extraction accuracy | High | Low | Expected for prototype, Phase 3.2 fixes |
| Format inconsistency | Medium | Low | Return empty dict if parsing fails |
| Breaking changes | Very Low | High | 100% backward compatible |

**Overall Risk:** ✅ LOW (prototype only, Phase 3.2 is real solution)

### Phase 3.2 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Prompt engineering complexity | Medium | Medium | Iterative refinement, testing |
| LLM doesn't follow schema | Low | Medium | Fallback to text parsing |
| Increased token usage | Low | Low | Structured output is compact |
| Breaking changes | Very Low | High | 100% backward compatible |

**Overall Risk:** ✅ LOW-MEDIUM (well-scoped, fallback strategy)

---

## Architecture

### Data Flow (Phase 3 Added)

```
STAGE 1 (Current Year Analysis)
   ↓
LLM ReAct Loop → Text Analysis
   ↓
Extract Metrics (Phase 2) → { roic, revenue, ... }
   ↓
Extract Insights (Phase 3) → { moat: MODERATE, risks: [...], ... }
   ↓
Return: { full_analysis, metrics, insights }

STAGE 2 (Prior Years)
   ↓
For each year:
   LLM Summarization → Text Summary
   ↓
   Extract Metrics (Phase 2) → { roic, revenue, ... }
   ↓
   Extract Insights (Phase 3) → { moat: STRONG, risks: [...], ... }
   ↓
Return: [{ summary, metrics, insights }, ...]

STAGE 3 (Synthesis)
   ↓
LLM Synthesis → Final Thesis
   ↓
Aggregate Metrics (Phase 2) → all_years metrics
   ↓
Aggregate Insights (Phase 3) → all_years insights
   ↓
Return: {
  decision, thesis,
  metadata: {
    structured_metrics: { ... },
    structured_insights: { ... }
  }
}
```

---

## Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 3.1** | 2-3 hours | Design, implement, test text parsing |
| **Phase 3.2** | 1-2 weeks | Design schema, update prompts, test, refine |
| **Total** | 1-2 weeks | Complete qualitative insights extraction |

---

## Next Actions

### Immediate (Phase 3.1 - Today)

1. ✅ Create planning document (this file)
2. ⏳ Implement `_extract_insights_from_analysis()` method
3. ⏳ Implement helper functions (`_extract_bullet_list`, etc.)
4. ⏳ Integrate into Stage 1 and Stage 2
5. ⏳ Add `structured_insights` to final result
6. ⏳ Test with AOS analysis
7. ⏳ Document Phase 3.1 results

### Short-term (Phase 3.2 - Next 1-2 weeks)

1. Design structured output JSON schema
2. Create prompt templates with schema request
3. Implement JSON parsing and validation
4. Add fallback to Phase 3.1 text parsing
5. Test with 10+ companies
6. Refine prompts based on failures
7. Document Phase 3.2 complete

---

## Success Definition

**Phase 3.1 Success:**
- Extract 5+ insights per year
- `structured_insights` in final result
- Test passes
- 2-3 hours implementation time

**Phase 3.2 Success:**
- Extract 15+ insights per year
- 90%+ extraction accuracy
- Tested with 10+ companies
- 1-2 weeks implementation time

**Phase 3 Complete:**
- Both quantitative (metrics) and qualitative (insights) data structured
- Foundation ready for Phase 4 (Synthesis Optimization)
- No breaking changes
- Full documentation

---

**Status:** 📋 PLANNING COMPLETE
**Next:** Begin Phase 3.1 Implementation
**Date:** November 16, 2025
