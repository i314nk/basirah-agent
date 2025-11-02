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

        # Decision badge
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

        # Key Metrics
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

        # Investment Thesis
        st.markdown("### 📄 Investment Thesis")
        thesis = result.get('thesis', 'No thesis generated.')
        st.markdown(thesis)

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
                    st.markdown(f"**Years Analyzed:** {', '.join(map(str, years))}")

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
        **Deep Dive Analysis:**
        1. Reads complete 10-K annual reports (200+ pages)
        2. Analyzes 3 years of financial history
        3. Uses 4 specialized tools (GuruFocus, SEC Filing, Web Search, Calculator)
        4. Generates comprehensive investment thesis in Buffett's voice

        **Context Management:**
        - Automatically handles companies of any size
        - Adaptive summarization for large filings (e.g., Coca-Cola)
        - 100% company coverage achieved
        """)

        st.divider()

        st.markdown("### 📚 Resources")

        st.markdown("""
        - [User Guide](https://github.com/i314nk/basirah-agent)
        - [Warren Buffett's Letters](https://berkshirehathaway.com/letters/letters.html)
        - [Documentation](https://github.com/i314nk/basirah-agent/tree/main/docs)
        """)
