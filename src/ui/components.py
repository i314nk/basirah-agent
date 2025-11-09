"""
Reusable UI components for basīrah
"""

import streamlit as st
import json
from typing import Dict, Any
from src.ui.utils import (
    get_decision_emoji,
    format_currency,
    format_percentage,
    format_duration,
    get_strategy_badge
)


def render_header():
    """Render application header with branding"""
    st.markdown(
        '<h1 style="color: #1f77b4; font-size: 2.5rem;">📈 basīrah</h1>',
        unsafe_allow_html=True
    )
    st.markdown("**Warren Buffett AI Investment Agent**")
    st.markdown(
        "Autonomous investment analysis using Warren Buffett's 70+ years of wisdom"
    )
    st.divider()


def render_ticker_input() -> str:
    """
    Render ticker input field.

    Returns:
        Uppercase ticker symbol
    """
    ticker = st.text_input(
        "Stock Ticker",
        placeholder="e.g., AAPL, MSFT, KO",
        help="Enter a US stock ticker symbol",
        max_chars=5
    ).upper().strip()
    return ticker


def render_analysis_type_selector() -> bool:
    """
    Render analysis type selector.

    Returns:
        True if Deep Dive selected, False for Quick Screen
    """
    analysis_type = st.radio(
        "Analysis Type",
        ["Deep Dive", "Quick Screen"],
        help=(
            "**Deep Dive**: Reads full 10-Ks (5-7 min), comprehensive multi-year analysis. "
            "Cost: ~$2-5.\n\n"
            "**Quick Screen**: Fast screening (30-60 sec), basic metrics only. "
            "Cost: ~$0.50."
        ),
        horizontal=True
    )
    return analysis_type == "Deep Dive"


def render_progress_info(deep_dive: bool):
    """
    Render expected analysis progress information.

    Args:
        deep_dive: Whether this is a deep dive analysis
    """
    if deep_dive:
        st.info(
            "📊 **Deep Dive Analysis**\n\n"
            "Warren AI will:\n"
            "- Read complete 10-K annual reports (200+ pages)\n"
            "- Analyze 3 years of financial history\n"
            "- Use GuruFocus, SEC Filing, Web Search, and Calculator tools\n"
            "- Generate comprehensive investment thesis\n\n"
            "Expected time: 5-7 minutes\n"
            "Expected cost: ~$2-5"
        )
    else:
        st.info(
            "⚡ **Quick Screen**\n\n"
            "Warren AI will:\n"
            "- Review key financial metrics\n"
            "- Apply initial screening criteria\n"
            "- Provide quick BUY/WATCH/AVOID decision\n\n"
            "Expected time: 30-60 seconds\n"
            "Expected cost: ~$0.50"
        )


def render_results(result: Dict[str, Any]):
    """
    Render analysis results.

    Args:
        result: Analysis result dictionary from WarrenBuffettAgent
    """
    # Container for better styling
    with st.container():
        st.markdown("## 📝 Investment Analysis Results")
        st.divider()

        # Check if this is a Quick Screen
        # Check both metadata and the absence of deep dive indicators
        analysis_type = result.get('metadata', {}).get('analysis_type', '')
        is_quick_screen = (
            analysis_type == 'quick' or
            analysis_type == 'quick_screen' or
            result.get('intrinsic_value') is None
        )

        if is_quick_screen:
            # Extract Quick Screen recommendation from thesis
            thesis = result.get('thesis', '')

            # Handle None or empty thesis (analysis failed)
            if not thesis:
                st.error("❌ Analysis failed - No thesis generated")
                st.info("This can happen when the LLM provider is unavailable or encounters an error.")
                return

            thesis_upper = thesis.upper()

            # Check for various patterns of INVESTIGATE recommendation
            if any(pattern in thesis_upper for pattern in [
                '🟢 INVESTIGATE',
                'INVESTIGATE',
                'RECOMMENDATION: INVESTIGATE',
                'RECOMMENDATION:** INVESTIGATE',
                'RECOMMENDATION: 🟢 INVESTIGATE'
            ]):
                # Try to extract confidence level from thesis
                confidence = ""
                if "HIGH CONFIDENCE" in thesis_upper or "CONFIDENCE: HIGH" in thesis_upper:
                    confidence = " (High Confidence)"
                elif "MEDIUM CONFIDENCE" in thesis_upper or "CONFIDENCE: MEDIUM" in thesis_upper:
                    confidence = " (Medium Confidence)"
                elif "MODERATE CONFIDENCE" in thesis_upper or "CONFIDENCE: MODERATE" in thesis_upper:
                    confidence = " (Moderate Confidence)"
                elif "LOW CONFIDENCE" in thesis_upper or "CONFIDENCE: LOW" in thesis_upper:
                    confidence = " (Low Confidence)"

                st.success(f"🟢 **INVESTIGATE**{confidence} - Deep Dive Recommended")
            # Check for various patterns of PASS recommendation
            elif any(pattern in thesis_upper for pattern in [
                '🔴 PASS',
                'RECOMMENDATION: PASS',
                'RECOMMENDATION:** PASS',
                'RECOMMENDATION: 🔴 PASS'
            ]):
                st.error("🔴 **PASS** - Skip Deep Dive")
            else:
                st.info("⚪ **UNCLEAR** - Review Analysis")
        else:
            # Deep Dive: Show traditional decision
            decision = result.get('decision', 'ERROR')
            conviction = result.get('conviction', 'UNKNOWN')
            emoji = get_decision_emoji(decision)

            if decision == 'BUY':
                st.success(f"{emoji} **{decision}** - {conviction} Conviction")
            elif decision == 'AVOID':
                st.error(f"{emoji} **{decision}** - {conviction} Conviction")
            elif decision == 'WATCH':
                st.warning(f"{emoji} **{decision}** - {conviction} Conviction")
            else:
                st.error(f"{emoji} **{decision}**")

        st.markdown("---")

        # Key Metrics (only show for Deep Dive)
        if not is_quick_screen:
            st.markdown("### Key Metrics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                iv = result.get('intrinsic_value')
                st.metric("Intrinsic Value", format_currency(iv))

            with col2:
                cp = result.get('current_price')
                st.metric("Current Price", format_currency(cp))

            with col3:
                mos = result.get('margin_of_safety', 0)
                st.metric("Margin of Safety", format_percentage(mos))

            with col4:
                duration = result.get('metadata', {}).get('analysis_duration_seconds', 0)
                st.metric("Analysis Time", format_duration(duration))

            st.markdown("---")

        # Context Management Info (if deep dive)
        cm = result.get('metadata', {}).get('context_management', {})
        if cm:
            with st.expander("📊 Context Management Details"):
                col1, col2 = st.columns(2)

                with col1:
                    strategy = cm.get('strategy', 'N/A')
                    st.markdown(f"**Strategy:** {get_strategy_badge(strategy)}")

                    years = cm.get('years_analyzed', [])
                    years_requested = cm.get('years_requested', len(years))
                    st.markdown(f"**Years Analyzed:** {', '.join(map(str, years))} ({len(years)} of {years_requested} requested)")

                    # Show missing years if any
                    missing_years = cm.get('years_skipped')
                    if missing_years:
                        st.warning(f"⚠️ **Years Skipped:** {', '.join(map(str, sorted(missing_years, reverse=True)))}\n\n"
                                   f"These fiscal years were requested but 10-K filings were not available. "
                                   f"This is common for companies that were spun off from parent companies or have limited filing history.")

                    current_tokens = cm.get('current_year_tokens', 0)
                    st.markdown(f"**Current Year Tokens:** ~{current_tokens:,}")

                with col2:
                    prior_tokens = cm.get('prior_years_tokens', 0)
                    st.markdown(f"**Prior Years Tokens:** ~{prior_tokens:,}")

                    total_tokens = cm.get('total_token_estimate', 0)
                    st.markdown(f"**Total Tokens:** ~{total_tokens:,}")

                    tool_calls = result.get('metadata', {}).get('tool_calls_made', 0)
                    st.markdown(f"**Tool Calls:** {tool_calls}")

                # If adaptive was used, show additional details
                if cm.get('adaptive_used', False):
                    st.info(
                        f"📦 **Adaptive Summarization Applied**\n\n"
                        f"This company has an exceptionally large 10-K filing "
                        f"({cm.get('filing_size', 0):,} characters). "
                        f"Warren AI read the complete filing and created a comprehensive summary "
                        f"({cm.get('summary_size', 0):,} characters, "
                        f"{cm.get('reduction_percent', 0):.1f}% reduction) "
                        f"to stay within context limits while maintaining 100% analytical quality."
                    )

        # Analysis Metadata
        with st.expander("🔍 Analysis Metadata"):
            metadata = result.get('metadata', {})
            st.json(metadata)

        st.markdown("---")

        # Download Options
        st.markdown("### 💾 Export Results")
        col1, col2, col3 = st.columns(3)

        with col1:
            # JSON download
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"{result.get('ticker', 'analysis')}_analysis.json",
                mime="application/json",
                key=f"download_json_{result.get('ticker', 'analysis')}"
            )

        with col2:
            # Markdown download
            md_content = generate_markdown_report(result)
            st.download_button(
                label="📄 Download Markdown",
                data=md_content,
                file_name=f"{result.get('ticker', 'analysis')}_thesis.md",
                mime="text/markdown",
                key=f"download_md_{result.get('ticker', 'analysis')}"
            )

        with col3:
            # Copy to clipboard button (requires user interaction)
            if st.button("📋 Copy Thesis", key=f"copy_thesis_{result.get('ticker', 'analysis')}"):
                st.code(thesis, language=None)
                st.success("Thesis displayed above - use Ctrl+C to copy")


def generate_markdown_report(result: Dict[str, Any]) -> str:
    """
    Generate markdown report from analysis result.

    Args:
        result: Analysis result dictionary

    Returns:
        Markdown-formatted report
    """
    ticker = result.get('ticker', 'UNKNOWN')
    decision = result.get('decision', 'ERROR')
    conviction = result.get('conviction', 'UNKNOWN')
    emoji = get_decision_emoji(decision)

    md = f"""# basīrah Investment Analysis - {ticker}

**Decision:** {emoji} {decision} ({conviction} conviction)

---

## Key Metrics

| Metric | Value |
|--------|-------|
| **Intrinsic Value** | {format_currency(result.get('intrinsic_value'))} |
| **Current Price** | {format_currency(result.get('current_price'))} |
| **Margin of Safety** | {format_percentage(result.get('margin_of_safety', 0))} |
| **Analysis Date** | {result.get('metadata', {}).get('analysis_date', 'N/A')} |
| **Analysis Duration** | {format_duration(result.get('metadata', {}).get('analysis_duration_seconds', 0))} |

---

## Investment Thesis

{result.get('thesis', 'No thesis generated.')}

---

## Analysis Details

**Strategy:** {get_strategy_badge(result.get('metadata', {}).get('context_management', {}).get('strategy', 'N/A'))}
**Years Analyzed:** {', '.join(map(str, result.get('metadata', {}).get('context_management', {}).get('years_analyzed', [])))}
**Tool Calls:** {result.get('metadata', {}).get('tool_calls_made', 0)}
**Total Tokens:** ~{result.get('metadata', {}).get('context_management', {}).get('total_token_estimate', 0):,}

---

## Disclaimer

This analysis is generated by an AI agent that embodies Warren Buffett's investment philosophy.
It is for educational and informational purposes only and does not constitute financial advice.
Always conduct your own due diligence and consult with a qualified financial advisor before
making investment decisions.

---

*Generated by basīrah - Warren Buffett AI Investment Agent*
"""
    return md


def display_cost_information(result: Dict[str, Any]):
    """
    Display cost information for completed analysis.

    Args:
        result: Analysis result dictionary containing token_usage metadata
    """
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
        cost_per_1k = usage['total_cost'] / usage['output_tokens'] * 1000 if usage['output_tokens'] > 0 else 0
        st.caption(f"${cost_per_1k:.3f} per 1K output")


def display_quick_screen_recommendation(result: Dict[str, Any]):
    """
    Display quick screen recommendation prominently.

    Args:
        result: Analysis result with thesis
    """
    thesis = result.get('thesis', '')

    # Extract recommendation (look for 🟢 INVESTIGATE or 🔴 PASS)
    if '🟢 INVESTIGATE' in thesis or 'RECOMMENDATION:** 🟢 INVESTIGATE' in thesis:
        recommendation = 'INVESTIGATE'
        emoji = '🟢'
        color = 'green'
        message = 'Deep Dive Recommended'
    elif '🔴 PASS' in thesis or 'RECOMMENDATION:** 🔴 PASS' in thesis:
        recommendation = 'PASS'
        emoji = '🔴'
        color = 'red'
        message = 'Skip Deep Dive'
    else:
        recommendation = 'UNCLEAR'
        emoji = '⚪'
        color = 'gray'
        message = 'Review Required'

    # Display prominent recommendation card
    st.divider()

    if recommendation == 'INVESTIGATE':
        st.success(f"### {emoji} Warren's Recommendation: {message}")
        st.markdown("""
        **This company shows potential and deserves deeper investigation.**

        Consider running a **Deep Dive Analysis** to:
        - Read complete 10-Ks across multiple years
        - Assess management quality in detail
        - Calculate precise intrinsic value
        - Make final investment decision
        """)

        # Add button for deep dive
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔍 Run Deep Dive Analysis", type="primary", use_container_width=True):
                st.session_state['run_deep_dive'] = True
                st.session_state['deep_dive_ticker'] = result.get('ticker')
                st.rerun()

    elif recommendation == 'PASS':
        st.error(f"### {emoji} Warren's Recommendation: {message}")
        st.markdown("""
        **This company doesn't meet the quality criteria for further analysis.**

        Better to spend time finding truly exceptional businesses than trying
        to make mediocre ones work. As Warren says: *"It's far better to buy
        a wonderful company at a fair price than a fair company at a wonderful price."*
        """)

    else:
        st.warning(f"### {emoji} Warren's Recommendation: {message}")
        st.markdown("Review the analysis below for details.")


def display_sharia_screening_result(result: Dict[str, Any]):
    """
    Display Sharia compliance screening results.

    Args:
        result: Sharia screening result dictionary
    """
    status = result.get('status', 'UNCLEAR')
    purification_rate = result.get('purification_rate', 0.0)
    analysis = result.get('analysis', '')

    st.divider()
    st.subheader("☪️ Sharia Compliance Status")

    # Status card with appropriate color
    if status == "COMPLIANT":
        st.success("### ✅ COMPLIANT")
        st.markdown("""
        **This company meets AAOIFI standards for Sharia compliance.**

        - ✅ Permissible business activities
        - ✅ Financial ratios within limits
        - ✅ No purification required
        - ✅ Suitable for all Muslim investors
        """)

    elif status == "DOUBTFUL":
        st.warning(f"### ⚠️ DOUBTFUL (Purification Required)")
        st.markdown(f"""
        **This company has minor non-compliant elements.**

        - ⚠️ Contains <5% non-compliant income
        - ⚠️ Requires dividend purification: **{purification_rate:.1f}%**
        - ✅ Suitable for moderate interpretations
        - ❌ May not suit strict interpretations

        **Purification Example:**
        For every $100 in dividends: Donate ${purification_rate:.2f} to charity
        """)

    elif status == "NON-COMPLIANT":
        st.error("### ❌ NON-COMPLIANT")
        st.markdown("""
        **This company does not meet AAOIFI standards.**

        - ❌ Significant prohibited activities OR
        - ❌ Financial ratios exceed thresholds
        - ❌ Not suitable for Sharia portfolios
        - 💡 Consider halal alternatives
        """)

    else:
        st.info("### ⚪ STATUS UNCLEAR")
        st.markdown("Review the detailed analysis below.")

    # Display full analysis
    st.divider()
    st.markdown("### 📋 Detailed Analysis")
    st.markdown(analysis)


def display_sharia_screening_with_translation(result: Dict[str, Any], translator):
    """
    Display Sharia compliance screening results with Arabic translation option.

    Args:
        result: Sharia screening result dictionary
        translator: ThesisTranslator instance
    """
    status = result.get('status', 'UNCLEAR')
    purification_rate = result.get('purification_rate', 0.0)
    analysis = result.get('analysis', '')
    ticker = result.get('ticker', 'UNKNOWN')

    st.divider()
    st.subheader("☪️ Sharia Compliance Status")

    # Status card with appropriate color
    if status == "COMPLIANT":
        st.success("### ✅ COMPLIANT")
        st.markdown("""
        **This company meets AAOIFI standards for Sharia compliance.**

        - ✅ Permissible business activities
        - ✅ Financial ratios within limits
        - ✅ No purification required
        - ✅ Suitable for all Muslim investors
        """)

    elif status == "DOUBTFUL":
        st.warning(f"### ⚠️ DOUBTFUL (Purification Required)")
        st.markdown(f"""
        **This company has minor non-compliant elements.**

        - ⚠️ Contains <5% non-compliant income
        - ⚠️ Requires dividend purification: **{purification_rate:.1f}%**
        - ✅ Suitable for moderate interpretations
        - ❌ May not suit strict interpretations

        **Purification Example:**
        For every $100 in dividends: Donate ${purification_rate:.2f} to charity
        """)

    elif status == "NON-COMPLIANT":
        st.error("### ❌ NON-COMPLIANT")
        st.markdown("""
        **This company does not meet AAOIFI standards.**

        - ❌ Significant prohibited activities OR
        - ❌ Financial ratios exceed thresholds
        - ❌ Not suitable for Sharia portfolios
        - 💡 Consider halal alternatives
        """)

    else:
        st.info("### ⚪ STATUS UNCLEAR")
        st.markdown("Review the detailed analysis below.")

    # Display detailed analysis with translation option
    st.divider()
    st.markdown("### 📋 Detailed Analysis")

    # Initialize translation cache for Sharia screens
    if 'sharia_translation_cache' not in st.session_state:
        st.session_state['sharia_translation_cache'] = {}
    if 'show_sharia_arabic' not in st.session_state:
        st.session_state['show_sharia_arabic'] = False

    # Language selector
    col1, col2 = st.columns([3, 1])
    with col2:
        button_label = "🌍 عربي" if not st.session_state['show_sharia_arabic'] else "🇺🇸 English"
        if st.button(button_label, key="sharia_translation_button"):
            if not st.session_state['show_sharia_arabic']:
                # Check if translation is cached for this ticker
                if ticker not in st.session_state['sharia_translation_cache']:
                    # Translate and cache
                    with st.spinner("Translating to Arabic... / جاري الترجمة إلى العربية..."):
                        translation_result = translator.translate_to_arabic(
                            analysis,
                            ticker
                        )
                        st.session_state['sharia_translation_cache'][ticker] = {
                            'translated_analysis': translation_result['translated_thesis'],
                            'cost': translation_result['cost']
                        }

                        # Add translation cost to session translation costs
                        if 'session_translation_costs' not in st.session_state:
                            st.session_state['session_translation_costs'] = []
                        st.session_state['session_translation_costs'].append(translation_result['cost'])

                # Show Arabic
                st.session_state['show_sharia_arabic'] = True
            else:
                # Toggle back to English (keep cached translation)
                st.session_state['show_sharia_arabic'] = False

            st.rerun()

    # Display analysis (English or Arabic)
    if st.session_state['show_sharia_arabic'] and ticker in st.session_state['sharia_translation_cache']:
        # Arabic display with RTL
        arabic_text = st.session_state['sharia_translation_cache'][ticker]['translated_analysis']

        # Add RTL styling
        st.markdown(
            """<style>
            .rtl-container {
                direction: rtl !important;
                text-align: right !important;
                font-size: 1.2rem !important;
                line-height: 1.8 !important;
            }
            .rtl-container h1 {
                direction: rtl !important;
                text-align: right !important;
                font-size: 2.2rem !important;
            }
            .rtl-container h2 {
                direction: rtl !important;
                text-align: right !important;
                font-size: 1.8rem !important;
            }
            .rtl-container h3 {
                direction: rtl !important;
                text-align: right !important;
                font-size: 1.5rem !important;
            }
            </style>""",
            unsafe_allow_html=True
        )

        st.markdown(f'<div class="rtl-container">{arabic_text}</div>', unsafe_allow_html=True)

        # Show translation cost
        cost = st.session_state['sharia_translation_cache'][ticker]['cost']
        st.caption(f"💰 Translation cost: ${cost:.2f}")
    else:
        # English display
        st.markdown(analysis)


def display_analysis_type_badge(analysis_type: str):
    """
    Display badge showing which analysis type was run.

    Args:
        analysis_type: "quick" | "deep_dive" | "sharia"
    """
    if analysis_type == "quick":
        st.info("⚡ **Quick Screen** - 1-year snapshot + Deep Dive recommendation")
    elif analysis_type == "deep_dive":
        st.success("🔍 **Deep Dive** - Complete multi-year Warren Buffett analysis")
    elif analysis_type == "sharia":
        st.warning("☪️ **Sharia Compliance** - AAOIFI standard Islamic finance screening")


def display_thesis_with_translation(result: Dict[str, Any], translator):
    """
    Display thesis with Arabic translation option.

    Args:
        result: Analysis result dictionary
        translator: ThesisTranslator instance
    """
    st.divider()
    st.subheader("📄 Investment Thesis")

    ticker = result.get('ticker', 'UNKNOWN')

    # Initialize translation cache and display state
    if 'translation_cache' not in st.session_state:
        st.session_state['translation_cache'] = {}
    if 'show_arabic' not in st.session_state:
        st.session_state['show_arabic'] = False

    # Language selector
    col1, col2 = st.columns([3, 1])
    with col2:
        button_label = "🌍 عربي" if not st.session_state['show_arabic'] else "🇺🇸 English"
        if st.button(button_label):
            if not st.session_state['show_arabic']:
                # Check if translation is cached for this ticker
                if ticker not in st.session_state['translation_cache']:
                    # Translate and cache
                    with st.spinner("Translating to Arabic..."):
                        translation_result = translator.translate_to_arabic(
                            result['thesis'],
                            ticker
                        )
                        st.session_state['translation_cache'][ticker] = {
                            'translated_thesis': translation_result['translated_thesis'],
                            'cost': translation_result['cost']
                        }

                        # Add translation cost to session translation costs (separate from analysis costs)
                        if 'session_translation_costs' not in st.session_state:
                            st.session_state['session_translation_costs'] = []
                        st.session_state['session_translation_costs'].append(translation_result['cost'])

                # Show Arabic
                st.session_state['show_arabic'] = True
            else:
                # Toggle back to English (keep cached translation)
                st.session_state['show_arabic'] = False

            st.rerun()

    # Display thesis (English or Arabic)
    if st.session_state['show_arabic'] and ticker in st.session_state['translation_cache']:
        # Arabic display with RTL - position on right side
        arabic_text = st.session_state['translation_cache'][ticker]['translated_thesis']

        # Add RTL styling
        st.markdown(
            """<style>
            .rtl-container {
                direction: rtl !important;
                text-align: right !important;
                font-size: 1.2rem !important;
                line-height: 1.8 !important;
            }
            .rtl-container h1 {
                direction: rtl !important;
                text-align: right !important;
                font-size: 2.2rem !important;
            }
            .rtl-container h2 {
                direction: rtl !important;
                text-align: right !important;
                font-size: 1.8rem !important;
            }
            .rtl-container h3 {
                direction: rtl !important;
                text-align: right !important;
                font-size: 1.5rem !important;
            }
            .rtl-container h4,
            .rtl-container h5,
            .rtl-container h6 {
                direction: rtl !important;
                text-align: right !important;
                font-size: 1.3rem !important;
            }
            .rtl-container p {
                direction: rtl !important;
                text-align: right !important;
                font-size: 1.2rem !important;
            }
            .rtl-container ul,
            .rtl-container ol {
                direction: rtl !important;
                text-align: right !important;
                padding-right: 0 !important;
                padding-left: 0 !important;
                margin-right: 1.5rem !important;
                margin-left: 0 !important;
                font-size: 1.2rem !important;
            }
            .rtl-container li {
                direction: rtl !important;
                text-align: right !important;
                list-style-position: outside !important;
                font-size: 1.2rem !important;
                line-height: 1.8 !important;
                margin-right: 0 !important;
                padding-right: 0 !important;
            }
            /* Force list markers to appear on the right */
            .rtl-container ol li::marker,
            .rtl-container ul li::marker {
                unicode-bidi: isolate !important;
                direction: rtl !important;
                text-align: right !important;
            }
            .rtl-container table {
                direction: rtl !important;
                font-size: 1.2rem !important;
            }
            .rtl-container strong,
            .rtl-container em {
                direction: rtl !important;
                font-size: 1.2rem !important;
            }
            .rtl-container code {
                direction: rtl !important;
                font-size: 1.1rem !important;
            }
            </style>""",
            unsafe_allow_html=True
        )

        # Create columns - empty left column, content on right
        col_left, col_right = st.columns([1, 4])

        with col_right:
            # Wrap markdown content in RTL HTML tags
            # This allows markdown to be processed while maintaining RTL layout
            rtl_wrapped_text = f"""
<div class="rtl-container" dir="rtl" style="direction: rtl; text-align: right; unicode-bidi: embed; font-size: 1.2rem; line-height: 1.8;">

{arabic_text}

</div>
"""
            # Render with markdown processing enabled
            st.markdown(rtl_wrapped_text, unsafe_allow_html=True)

            # Show translation cost
            translation_cost = st.session_state['translation_cache'][ticker]['cost']
            st.caption(f"💰 Translation cost: ${translation_cost:.2f}")
    else:
        # English display (full width)
        st.markdown(result['thesis'])


def render_footer():
    """Render footer with disclaimers and attribution"""
    st.divider()
    st.markdown("""
    ### ⚠️ Disclaimer

    This is an AI-powered analytical tool, not financial advice.
    Past performance does not guarantee future results. Always do your own research
    and consult with a qualified financial advisor before making investment decisions.

    ---

    Built with Warren Buffett's investment principles | Powered by Claude 4.5 Sonnet
    """)


def render_sidebar_info():
    """Render sidebar with additional information and settings"""
    with st.sidebar:
        st.markdown("### 📊 About Warren AI")

        st.markdown("""
        This agent embodies Warren Buffett's investment philosophy:

        - **Circle of Competence**: Only analyzes businesses it understands
        - **Economic Moat**: Seeks competitive advantages
        - **Management Quality**: Evaluates capital allocation
        - **Financial Strength**: Requires fortress balance sheets
        - **Margin of Safety**: Conservative valuations only
        - **Patience**: Comfortable saying "pass"
        """)

        st.divider()

        st.markdown("### ⚙️ How It Works")

        st.markdown("""
        **Quick Screen** (~$1.14, 2-3 min):
        - Analyzes 1 year of data
        - Reads business section from 10-K
        - Provides Deep Dive recommendation

        **Deep Dive** ($2.81-$3.71, 10-20 min):
        - Reads complete 10-K annual reports (200+ pages)
        - Analyzes 5-10 years of financial history
        - Uses 4 specialized tools (GuruFocus, SEC Filing, Web Search, Calculator)
        - Context management: Full current year + summarized prior years
        - Generates comprehensive investment thesis

        **Sharia Compliance** (~$0.98, 3-5 min):
        - AAOIFI standard screening
        - Business activity verification
        - Financial ratio compliance check
        - Purification rate calculation
        """)

        st.divider()

        st.markdown("### 📚 Resources")

        st.markdown("""
        - [User Guide](https://github.com/i314nk/basirah-agent)
        - [Warren Buffett's Letters](https://berkshirehathaway.com/letters/letters.html)
        - [Documentation](https://github.com/i314nk/basirah-agent/tree/main/docs)
        """)
