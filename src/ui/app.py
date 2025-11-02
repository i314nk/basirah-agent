"""
basīrah - Warren Buffett AI Investment Agent Web Interface

Main Streamlit application for running investment analysis through a web UI.

Usage:
    streamlit run src/ui/app.py
"""

import streamlit as st
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agent.buffett_agent import WarrenBuffettAgent
from src.ui.components import (
    render_header,
    render_ticker_input,
    render_analysis_type_selector,
    render_progress_info,
    render_results,
    render_footer,
    render_sidebar_info
)
from src.ui.utils import (
    validate_ticker,
    estimate_cost,
    estimate_duration
)

# Page config
st.set_page_config(
    page_title="basīrah - Warren Buffett AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .thesis-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .stButton>button {
        width: 100%;
        font-size: 1.1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Initialize agent (cache it for performance)
@st.cache_resource
def get_agent():
    """Initialize and cache the Warren Buffett AI Agent"""
    return WarrenBuffettAgent()


def main():
    """Main application entry point"""

    # Render header
    render_header()

    # Sidebar info
    render_sidebar_info()

    # Advanced settings in sidebar
    with st.sidebar:
        st.divider()
        st.markdown("### ⚙️ Advanced Settings")

        with st.expander("Analysis Configuration", expanded=False):
            years_to_analyze = st.slider(
                "Years to Analyze (Deep Dive)",
                min_value=1,
                max_value=10,
                value=3,
                help="Number of years to include in multi-year analysis. More years = longer analysis time and deeper trend insights."
            )

            st.info(
                f"**Selected:** {years_to_analyze} year{'s' if years_to_analyze > 1 else ''}\n\n"
                f"**Analysis includes:**\n"
                f"- Current year: 2024\n"
                f"- Prior years: {years_to_analyze-1} year{'s' if years_to_analyze > 1 else ''}\n"
                f"- Total: {years_to_analyze} year{'s' if years_to_analyze > 1 else ''} analyzed\n\n"
                f"**Estimated time:** ~{2 + (years_to_analyze-1)*2}-{3 + (years_to_analyze-1)*2} minutes\n"
                f"**Estimated cost:** ~${1.5 + (years_to_analyze-1)*0.5:.2f}"
            )

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🎯 Enter Company to Analyze")

        # Ticker input
        ticker = render_ticker_input()

        # Analysis type selector
        deep_dive = render_analysis_type_selector()

    with col2:
        # Expected analysis info
        if ticker:
            render_progress_info(deep_dive)

    st.divider()

    # Analyze button
    if st.button("🔍 Analyze Company", type="primary", use_container_width=True):
        if not ticker:
            st.error("⚠️ Please enter a stock ticker symbol")
        elif not validate_ticker(ticker):
            st.error(
                f"⚠️ Invalid ticker format: '{ticker}'\n\n"
                "Please enter a valid US stock ticker (1-5 uppercase letters, e.g., AAPL, MSFT, KO)"
            )
        else:
            # Run analysis with configured years
            run_analysis(ticker, deep_dive, years_to_analyze)

    # Show last result if available
    if 'last_result' in st.session_state and st.session_state['last_result'] is not None:
        st.divider()
        st.markdown("## 📊 Latest Analysis")
        render_results(st.session_state['last_result'])

    # Footer
    render_footer()


def run_analysis(ticker: str, deep_dive: bool, years_to_analyze: int = 3):
    """
    Run investment analysis on a company.

    Args:
        ticker: Stock ticker symbol
        deep_dive: Whether to run deep dive analysis
        years_to_analyze: Number of years to analyze (for deep dive)
    """
    # Analysis info
    analysis_type = "Deep Dive" if deep_dive else "Quick Screen"
    estimated_time = estimate_duration(deep_dive)
    estimated_cost = estimate_cost(deep_dive)

    st.markdown(f"""
    ### 🚀 Starting {analysis_type} Analysis

    **Company:** {ticker}
    **Years to Analyze:** {years_to_analyze if deep_dive else 'N/A (Quick Screen)'}
    **Estimated Time:** {estimated_time}
    **Estimated Cost:** ${estimated_cost:.2f}
    """)

    # Progress container
    progress_container = st.empty()
    status_container = st.empty()

    try:
        # Initialize agent
        with progress_container:
            with st.spinner("Initializing Warren Buffett AI Agent..."):
                agent = get_agent()

        # Start analysis
        start_time = time.time()

        with progress_container:
            with st.spinner(f"Warren Buffett AI is analyzing {ticker}..."):
                # Show status updates
                if deep_dive:
                    status_container.info(
                        f"📖 **Stage 1:** Reading current year 10-K (200+ pages)...\n\n"
                        f"Analyzing {years_to_analyze} years total. This may take 2-3 minutes per year."
                    )

                # Run analysis
                result = agent.analyze_company(
                    ticker,
                    deep_dive=deep_dive,
                    years_to_analyze=years_to_analyze if deep_dive else 1
                )

                # Calculate duration
                duration = time.time() - start_time

                # Add duration to metadata if not present
                if 'analysis_duration_seconds' not in result.get('metadata', {}):
                    if 'metadata' not in result:
                        result['metadata'] = {}
                    result['metadata']['analysis_duration_seconds'] = duration

        # Clear progress indicators
        progress_container.empty()
        status_container.empty()

        # Success message
        st.success(
            f"✅ Analysis Complete! Completed in {duration:.0f} seconds "
            f"({duration/60:.1f} minutes)"
        )

        # Store result in session state
        # (Results will be displayed automatically by main() after rerun)
        st.session_state['last_result'] = result

    except Exception as e:
        # Clear progress indicators
        progress_container.empty()
        status_container.empty()

        # Error handling
        st.error(
            f"❌ **Analysis Failed**\n\n"
            f"Error: {str(e)}\n\n"
            f"**Common causes:**\n"
            f"- Invalid ticker symbol\n"
            f"- API rate limits (wait a few seconds and try again)\n"
            f"- Network issues\n"
            f"- Missing API keys (check .env file)"
        )

        # Show retry button
        if st.button("🔄 Retry Analysis"):
            st.rerun()

        # Store error in session state
        st.session_state['last_result'] = {
            'ticker': ticker,
            'decision': 'ERROR',
            'conviction': 'N/A',
            'thesis': f"Analysis failed: {str(e)}",
            'metadata': {
                'error': str(e),
                'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }


if __name__ == "__main__":
    main()
