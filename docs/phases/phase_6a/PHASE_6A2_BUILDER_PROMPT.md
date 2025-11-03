# BUILDER PROMPT: Phase 6A.2 - Cost Display + Arabic Translation

## Overview

This phase adds two key features to the basīrah Streamlit UI:

1. **Cost Display** - Show token usage and actual API costs for analyses
2. **Arabic Translation** - Translate investment theses to Arabic with RTL formatting

## Feature 1: Cost Display

### Requirements

Track and display the actual cost of each analysis based on Claude API token usage.

**Claude Sonnet 4.5 Pricing:**
- Input tokens: $0.01 per 1,000 tokens
- Output tokens: $0.30 per 1,000 tokens

### Implementation Steps

#### Step 1: Update `buffett_agent.py` to Track Token Usage

**File:** `src/agent/buffett_agent.py`

**Location:** In `_run_react_loop()` method (around line 1200, after the API call)

Add token tracking after each API response:

```python
# After: response = self.client.messages.create(...)

# Track token usage for cost calculation
if not hasattr(self, '_total_input_tokens'):
    self._total_input_tokens = 0
    self._total_output_tokens = 0

self._total_input_tokens += response.usage.input_tokens
self._total_output_tokens += response.usage.output_tokens
```

**Location:** In `analyze_company()` method (around line 193, at start of method)

Reset token counters at the start of each analysis:

```python
def analyze_company(
    self,
    ticker: str,
    deep_dive: bool = True,
    years_to_analyze: int = 3
) -> dict:
    """Analyze a company using Warren Buffett's investment criteria."""

    # Reset token counters for this analysis
    self._total_input_tokens = 0
    self._total_output_tokens = 0

    # ... rest of method
```

**Location:** In return statement of `_run_react_loop()` (around line 1350)

Add cost calculation to the return dict:

```python
# Calculate costs
input_cost = (self._total_input_tokens / 1000) * 0.01
output_cost = (self._total_output_tokens / 1000) * 0.30
total_cost = input_cost + output_cost

return {
    "decision": decision,
    "conviction": conviction_level,
    "thesis": thesis,
    "intrinsic_value": intrinsic_value,
    "current_price": current_price,
    "margin_of_safety": margin_of_safety,
    "metadata": {
        "ticker": ticker,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "deep_dive": deep_dive,
        "years_analyzed": years_to_analyze,
        "strategy_used": strategy_used,
        "token_usage": {
            "input_tokens": self._total_input_tokens,
            "output_tokens": self._total_output_tokens,
            "input_cost": round(input_cost, 2),
            "output_cost": round(output_cost, 2),
            "total_cost": round(total_cost, 2)
        }
    }
}
```

#### Step 2: Add Cost Estimation Function

**File:** `src/ui/utils.py`

Add function to estimate cost before analysis:

```python
def estimate_analysis_cost(analysis_type: str, years_to_analyze: int) -> dict:
    """
    Estimate the cost of an analysis based on historical data.

    Args:
        analysis_type: "quick" or "deep_dive"
        years_to_analyze: Number of years to analyze (1-10)

    Returns:
        dict with estimated_cost, min_cost, max_cost, duration_minutes
    """
    # Historical cost data (approximate)
    if analysis_type == "quick":
        base_cost = 0.50
        time_minutes = 1
    else:  # deep_dive
        if years_to_analyze == 1:
            base_cost = 1.50
            time_minutes = 3
        elif years_to_analyze == 3:
            base_cost = 2.50
            time_minutes = 6
        elif years_to_analyze == 5:
            base_cost = 4.50
            time_minutes = 12
        elif years_to_analyze >= 10:
            base_cost = 7.00
            time_minutes = 25
        else:
            # Interpolate for other values
            base_cost = 1.50 + (years_to_analyze - 1) * 0.75
            time_minutes = 3 + (years_to_analyze - 1) * 3

    # Add variance margin
    min_cost = round(base_cost * 0.8, 2)
    max_cost = round(base_cost * 1.2, 2)

    return {
        "estimated_cost": round(base_cost, 2),
        "min_cost": min_cost,
        "max_cost": max_cost,
        "duration_minutes": time_minutes
    }
```

#### Step 3: Add Cost Display Component

**File:** `src/ui/components.py`

Add function to display cost information:

```python
def display_cost_information(result: dict):
    """Display cost information for completed analysis."""
    if "token_usage" not in result.get("metadata", {}):
        return

    usage = result["metadata"]["token_usage"]

    st.divider()
    st.subheader("💰 Analysis Cost")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Input Tokens", f"{usage['input_tokens']:,}")
        st.caption(f"Cost: ${usage['input_cost']:.2f}")

    with col2:
        st.metric("Output Tokens", f"{usage['output_tokens']:,}")
        st.caption(f"Cost: ${usage['output_cost']:.2f}")

    with col3:
        st.metric("Total Cost", f"${usage['total_cost']:.2f}")
        st.caption(f"${usage['total_cost'] / usage['output_tokens'] * 1000:.3f} per 1K output")
```

#### Step 4: Update Streamlit App

**File:** `src/ui/app.py`

**Location:** Before analysis starts (in `run_analysis()` function, before the agent call)

Add cost estimate display:

```python
# Show cost estimate
estimate = estimate_analysis_cost(
    "deep_dive" if deep_dive else "quick",
    years_to_analyze
)

st.info(
    f"💰 **Estimated Cost:** ${estimate['estimated_cost']:.2f} "
    f"(${estimate['min_cost']:.2f} - ${estimate['max_cost']:.2f})\n\n"
    f"⏱️ **Estimated Duration:** ~{estimate['duration_minutes']} minutes"
)
```

**Location:** In sidebar (in `main()` function)

Add session cost tracking:

```python
# In sidebar - add after the existing sidebar content
st.sidebar.divider()
st.sidebar.subheader("💰 Session Costs")

if 'session_costs' not in st.session_state:
    st.session_state['session_costs'] = []

if st.session_state['session_costs']:
    total_cost = sum(st.session_state['session_costs'])
    st.sidebar.metric("Total Spent", f"${total_cost:.2f}")
    st.sidebar.metric("Analyses", len(st.session_state['session_costs']))
else:
    st.sidebar.info("No analyses yet")
```

**Location:** After analysis completes (in `run_analysis()` function)

Track session costs:

```python
# After analysis completes
if "token_usage" in result.get("metadata", {}):
    cost = result["metadata"]["token_usage"]["total_cost"]
    st.session_state['session_costs'].append(cost)
```

**Location:** In results display (after `render_results()` call)

Display cost information:

```python
# After rendering results
display_cost_information(result)
```

## Feature 2: Arabic Translation

### Requirements

Provide on-demand translation of investment theses to Arabic with proper RTL (right-to-left) formatting.

### Implementation Steps

#### Step 1: Create Translation Module

**File:** `src/agent/translator.py` (NEW FILE)

```python
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
```

#### Step 2: Add Translation UI Component

**File:** `src/ui/components.py`

Add function to display thesis with translation option:

```python
def display_thesis_with_translation(result: dict, translator):
    """Display thesis with Arabic translation option."""

    st.divider()
    st.subheader("📄 Investment Thesis")

    # Language selector
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🌍 Translate to Arabic" if 'arabic_thesis' not in st.session_state else "🇺🇸 Show English"):
            if 'arabic_thesis' not in st.session_state:
                # Translate
                with st.spinner("Translating to Arabic..."):
                    translation_result = translator.translate_to_arabic(
                        result['thesis'],
                        result['metadata']['ticker']
                    )
                    st.session_state['arabic_thesis'] = translation_result['translated_thesis']
                    st.session_state['translation_cost'] = translation_result['cost']

                    # Add translation cost to session costs
                    if 'session_costs' not in st.session_state:
                        st.session_state['session_costs'] = []
                    st.session_state['session_costs'].append(translation_result['cost'])
            else:
                # Toggle back to English
                del st.session_state['arabic_thesis']
                if 'translation_cost' in st.session_state:
                    del st.session_state['translation_cost']

            st.rerun()

    # Display thesis (English or Arabic)
    if 'arabic_thesis' in st.session_state:
        # Arabic display with RTL
        st.markdown(
            f"""<div dir="rtl" style="text-align: right; font-size: 16px;">
            {st.session_state['arabic_thesis'].replace(chr(10), '<br>')}
            </div>""",
            unsafe_allow_html=True
        )

        # Show translation cost
        if 'translation_cost' in st.session_state:
            st.caption(f"💰 Translation cost: ${st.session_state['translation_cost']:.2f}")
    else:
        # English display
        st.markdown(result['thesis'])
```

#### Step 3: Update Streamlit App

**File:** `src/ui/app.py`

**Location:** At top of file with imports

Add translator import:

```python
from src.agent.translator import ThesisTranslator
```

**Location:** In `main()` function, after agent initialization

Initialize translator:

```python
# Initialize translator
if 'translator' not in st.session_state:
    st.session_state['translator'] = ThesisTranslator()

translator = st.session_state['translator']
```

**Location:** In results display section (replace existing thesis display)

Use new translation-enabled component:

```python
# Replace the existing st.markdown(result['thesis']) with:
display_thesis_with_translation(result, translator)
```

#### Step 4: Update Export Functions

**File:** `src/ui/utils.py`

Update export functions to handle Arabic translations:

```python
def export_to_json(result: dict) -> str:
    """Export result to JSON with optional Arabic translation."""
    export_data = result.copy()

    # Add Arabic translation if available
    if 'arabic_thesis' in st.session_state:
        export_data['thesis_arabic'] = st.session_state['arabic_thesis']
        export_data['metadata']['translation_cost'] = st.session_state.get('translation_cost', 0)

    return json.dumps(export_data, indent=2, ensure_ascii=False)

def export_to_markdown(result: dict) -> str:
    """Export result to Markdown with optional Arabic translation."""
    md = generate_markdown_report(result)

    # Add Arabic translation if available
    if 'arabic_thesis' in st.session_state:
        md += "\n\n---\n\n"
        md += "## الأطروحة الاستثمارية (Arabic Translation)\n\n"
        md += f"<div dir=\"rtl\" style=\"text-align: right;\">\n\n"
        md += st.session_state['arabic_thesis']
        md += "\n\n</div>\n\n"

        if 'translation_cost' in st.session_state:
            md += f"\n*Translation cost: ${st.session_state['translation_cost']:.2f}*\n"

    return md
```

## Testing Checklist

### Cost Display Testing

- [ ] Start fresh session, verify session costs show "No analyses yet"
- [ ] Run quick screen analysis, verify cost estimate shows before analysis
- [ ] Verify cost breakdown shows after analysis (input tokens, output tokens, total)
- [ ] Run second analysis, verify session costs accumulate correctly
- [ ] Test with different year configurations (1, 3, 5, 10 years)
- [ ] Verify cost estimates are reasonably accurate (within 20%)

### Arabic Translation Testing

- [ ] Complete an analysis with thesis
- [ ] Click "Translate to Arabic" button
- [ ] Verify Arabic text displays with RTL formatting
- [ ] Verify ticker symbols and company names remain in English
- [ ] Verify numbers and percentages are preserved correctly
- [ ] Verify Warren Buffett quotes are preserved
- [ ] Click "Show English" to toggle back
- [ ] Verify translation cost is added to session costs
- [ ] Export to JSON and verify Arabic text is included
- [ ] Export to Markdown and verify Arabic text with RTL formatting

## Success Criteria

1. **Cost Display:**
   - ✅ Real-time token tracking with 100% accuracy
   - ✅ Cost breakdown displayed after every analysis
   - ✅ Session cost accumulation across multiple analyses
   - ✅ Cost estimates provided before analysis (±20% accuracy)

2. **Arabic Translation:**
   - ✅ One-click translation to Arabic
   - ✅ Proper RTL formatting
   - ✅ Preservation of English terms (ticker, companies, Warren Buffett)
   - ✅ Preservation of numbers and financial data
   - ✅ Toggle between English and Arabic
   - ✅ Translation cost tracking
   - ✅ Export support for bilingual reports

## Performance Targets

- **Cost Display:** No performance impact (passive tracking)
- **Arabic Translation:** < 30 seconds for typical thesis (3,000-5,000 words)
- **Translation Cost:** ~$0.50-$1.50 per thesis (depending on length)

## Estimated Implementation Time

- **Cost Display:** ~1 hour
- **Arabic Translation:** ~1.5 hours
- **Testing & Documentation:** ~30 minutes
- **Total:** 2.5-3 hours
