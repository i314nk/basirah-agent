"""
basīrah - Warren Buffett AI Investment Agent Web Interface

Main Streamlit application for running investment analysis through a web UI.

Usage:
    streamlit run src/ui/app.py
"""

import streamlit as st
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agent.buffett_agent import WarrenBuffettAgent
from src.agent.translator import ThesisTranslator
from src.agent.sharia_screener import ShariaScreener
from src.storage import AnalysisStorage
from src.ui.cost_estimator import CostEstimator
from src.ui.components import (
    render_header,
    render_ticker_input,
    render_analysis_type_selector,
    render_progress_info,
    render_results,
    render_footer,
    render_sidebar_info,
    display_cost_information,
    display_quick_screen_recommendation,
    display_sharia_screening_result,
    display_sharia_screening_with_translation,
    display_analysis_type_badge,
    display_thesis_with_translation
)
from src.ui.utils import (
    validate_ticker,
    estimate_cost,
    estimate_duration,
    estimate_analysis_cost
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

    # Initialize translator (cache in session state)
    if 'translator' not in st.session_state:
        st.session_state['translator'] = ThesisTranslator()

    translator = st.session_state['translator']

    # Initialize Sharia screener (cache in session state)
    if 'sharia_screener' not in st.session_state:
        try:
            st.session_state['sharia_screener'] = ShariaScreener()
        except Exception as e:
            st.sidebar.warning(f"Sharia screening unavailable: {e}")
            st.session_state['sharia_screener'] = None

    # Initialize Analysis Storage (cache in session state)
    if 'analysis_storage' not in st.session_state:
        try:
            st.session_state['analysis_storage'] = AnalysisStorage()
        except Exception as e:
            st.sidebar.warning(f"Analysis history unavailable: {e}")
            st.session_state['analysis_storage'] = None

    # Initialize Cost Estimator (cache in session state)
    if 'cost_estimator' not in st.session_state:
        try:
            st.session_state['cost_estimator'] = CostEstimator()
        except Exception as e:
            st.sidebar.warning(f"Cost estimation unavailable: {e}")
            st.session_state['cost_estimator'] = None

    sharia_screener = st.session_state['sharia_screener']
    storage = st.session_state['analysis_storage']
    cost_estimator = st.session_state['cost_estimator']

    # Sidebar info
    render_sidebar_info()

    # Session cost tracking in sidebar
    with st.sidebar:
        st.divider()
        st.markdown("### 💰 Session Costs")

        if 'session_costs' not in st.session_state:
            st.session_state['session_costs'] = []
        if 'session_translation_costs' not in st.session_state:
            st.session_state['session_translation_costs'] = []

        analysis_costs = st.session_state['session_costs']
        translation_costs = st.session_state['session_translation_costs']

        if analysis_costs or translation_costs:
            total_analysis = sum(analysis_costs)
            total_translation = sum(translation_costs)
            total_cost = total_analysis + total_translation

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Analyses", len(analysis_costs))
            with col2:
                st.metric("Translations", len(translation_costs))

            st.metric("Total Spent", f"${total_cost:.2f}")

            with st.expander("💸 Cost Breakdown"):
                st.write(f"**Analysis Costs:** ${total_analysis:.2f}")
                st.write(f"**Translation Costs:** ${total_translation:.2f}")
        else:
            st.info("No analyses yet")

    # Advanced settings in sidebar
    with st.sidebar:
        st.divider()
        st.markdown("### ⚙️ Advanced Settings")

        with st.expander("Analysis Configuration", expanded=False):
            years_to_analyze = st.slider(
                "Years to Analyze (Deep Dive)",
                min_value=5,
                max_value=10,
                value=5,
                help="Number of years to include in multi-year analysis. Deep Dive requires 5-10 years for meaningful trend analysis and to assess management quality over time. More years = longer analysis time and deeper insights."
            )

            # Calculate fiscal years dynamically
            current_calendar_year = datetime.now().year
            most_recent_fiscal_year = current_calendar_year - 1  # Most recent complete FY with 10-K
            oldest_fiscal_year = most_recent_fiscal_year - (years_to_analyze - 1)

            # Build year range display
            if years_to_analyze == 1:
                year_range = f"FY {most_recent_fiscal_year}"
            else:
                year_range = f"FY {oldest_fiscal_year}-{most_recent_fiscal_year}"

            st.info(
                f"**Selected:** {years_to_analyze} year{'s' if years_to_analyze > 1 else ''}\n\n"
                f"**Analysis includes:**\n"
                f"- Most recent fiscal year: {most_recent_fiscal_year} (latest 10-K available)\n"
                f"- Prior years: {years_to_analyze-1} year{'s' if years_to_analyze > 1 else ''}\n"
                f"- Year range: {year_range}\n"
                f"- Total: {years_to_analyze} year{'s' if years_to_analyze > 1 else ''} analyzed\n\n"
                f"**Estimated time:** ~{2 + (years_to_analyze-1)*2}-{3 + (years_to_analyze-1)*2} minutes\n"
                f"**Estimated cost:** ~${2.09 + (years_to_analyze-1)*0.18:.2f}\n"
                f"💡 Use 'Check Cost' button for exact estimate"
            )

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🎯 Enter Company to Analyze")

        # Ticker input
        ticker = render_ticker_input()

        # Analysis type selector
        analysis_type = st.selectbox(
            "📊 Analysis Type",
            ["Quick Screen", "Deep Dive", "Sharia Compliance"],
            help="""
            - **Quick Screen**: Fast 1-year snapshot with Deep Dive recommendation (~$1.14, 2-3 min)
            - **Deep Dive**: Complete 5-10 year Warren Buffett analysis ($2.81-$3.71, 10-20 min)
            - **Sharia Compliance**: AAOIFI standard Islamic finance screening (~$0.98, 3-5 min)
            """
        )

        deep_dive = (analysis_type == "Deep Dive")

    with col2:
        # Expected analysis info
        if ticker:
            render_progress_info(deep_dive)

    st.divider()

    # Check Cost and Analyze buttons
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        check_cost_clicked = st.button("💰 Check Cost", use_container_width=True)

    with col_btn2:
        analyze_clicked = st.button("🎯 Analyze Company", type="primary", use_container_width=True)

    # Handle Check Cost button click
    if check_cost_clicked:
        if not ticker:
            st.error("⚠️ Please enter a stock ticker symbol")
        elif not validate_ticker(ticker):
            st.error(
                f"⚠️ Invalid ticker format: '{ticker}'\n\n"
                "Please enter a valid US stock ticker (1-5 uppercase letters, e.g., AAPL, MSFT, KO)"
            )
        elif not cost_estimator:
            st.error("⚠️ Cost estimation is not available. Please check API configuration.")
        else:
            st.divider()
            st.markdown(f"### 💰 Cost Estimate for {ticker.upper()}")

            with st.spinner("Calculating exact cost using token counting..."):
                try:
                    # Get cost estimate based on analysis type
                    if analysis_type == "Quick Screen":
                        agent = get_agent()
                        estimate = cost_estimator.estimate_quick_screen_cost(ticker, agent)
                    elif analysis_type == "Deep Dive":
                        agent = get_agent()
                        estimate = cost_estimator.estimate_deep_dive_cost(ticker, years_to_analyze, agent)
                    else:  # Sharia Compliance
                        if not sharia_screener:
                            st.error("⚠️ Sharia screening is not available.")
                        else:
                            estimate = cost_estimator.estimate_sharia_screen_cost(ticker, sharia_screener)

                    # Display the estimate
                    if estimate.get('success'):
                        st.success("✅ Cost Estimate Complete")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                "Total Estimated Cost",
                                f"${estimate['total_estimated_cost']:.2f}",
                                help="Based on exact token counting"
                            )

                        with col2:
                            st.metric(
                                "Min Cost",
                                f"${estimate['min_cost']:.2f}",
                                help="Lower bound estimate"
                            )

                        with col3:
                            st.metric(
                                "Max Cost",
                                f"${estimate['max_cost']:.2f}",
                                help="Upper bound estimate"
                            )

                        # Show detailed breakdown
                        with st.expander("📊 Detailed Breakdown"):
                            st.markdown(f"""
                            **Analysis Type:** {estimate.get('analysis_type', 'N/A').replace('_', ' ').title()}

                            **Token Counts:**
                            - Input Tokens: {estimate.get('input_tokens', 'N/A'):,}
                            - Estimated Output Tokens: {estimate.get('estimated_output_tokens', 'N/A'):,}

                            **Cost Breakdown:**
                            - Input Cost: ${estimate.get('input_cost', 0):.2f}
                            - Output Cost: ${estimate.get('estimated_output_cost', 0):.2f}
                            - **Total: ${estimate['total_estimated_cost']:.2f}**

                            **Confidence:** {estimate.get('confidence', 'N/A').upper()}
                            """)

                            if 'years_to_analyze' in estimate:
                                st.info(f"📅 This estimate is for {estimate['years_to_analyze']} year(s) of analysis")

                        st.info("💡 Click 'Analyze Company' to proceed with the analysis")
                    else:
                        # Fallback estimate
                        st.warning(f"⚠️ Token counting unavailable: {estimate.get('error', 'Unknown error')}")
                        st.info(f"📊 Using historical average: ${estimate['total_estimated_cost']:.2f} (${estimate['min_cost']:.2f} - ${estimate['max_cost']:.2f})")
                        st.caption(estimate.get('note', ''))

                except Exception as e:
                    st.error(f"❌ Cost estimation failed: {str(e)}")

    # Handle Analyze button click
    if analyze_clicked:
        if not ticker:
            st.error("⚠️ Please enter a stock ticker symbol")
        elif not validate_ticker(ticker):
            st.error(
                f"⚠️ Invalid ticker format: '{ticker}'\n\n"
                "Please enter a valid US stock ticker (1-5 uppercase letters, e.g., AAPL, MSFT, KO)"
            )
        else:
            # Handle different analysis types
            if analysis_type == "Sharia Compliance":
                # Sharia compliance screening
                if not sharia_screener:
                    st.error("⚠️ Sharia screening is not available. Please check API configuration.")
                else:
                    st.divider()
                    st.markdown(f"### ☪️ Analyzing {ticker} for Sharia Compliance...")

                    with st.spinner("Performing Sharia compliance screening..."):
                        start_time = time.time()

                        result = sharia_screener.screen_company(ticker)

                        duration = time.time() - start_time
                        result['metadata']['analysis_duration_seconds'] = duration

                        # Store result
                        st.session_state['last_result'] = result
                        st.session_state['last_analysis_type'] = 'sharia'

                        # Track cost
                        if 'token_usage' in result.get('metadata', {}):
                            cost = result['metadata']['token_usage']['total_cost']
                            if 'session_costs' not in st.session_state:
                                st.session_state['session_costs'] = []
                            st.session_state['session_costs'].append(cost)

                        # Auto-save to history
                        if storage:
                            try:
                                save_result = storage.save_analysis(result)
                                if save_result['success']:
                                    st.sidebar.success(f"Saved to history: {save_result['analysis_id']}")
                            except Exception as e:
                                st.sidebar.warning(f"Failed to save to history: {e}")

                    st.rerun()
            else:
                # Regular or Quick Screen analysis
                run_analysis(ticker, deep_dive, years_to_analyze)

    # Show last result if available
    if 'last_result' in st.session_state and st.session_state['last_result'] is not None:
        st.divider()
        result = st.session_state['last_result']
        last_analysis_type = st.session_state.get('last_analysis_type', 'quick')

        st.markdown("## 📊 Latest Analysis")

        # Show analysis type badge
        display_analysis_type_badge(last_analysis_type)

        # Display cost
        display_cost_information(result)

        if last_analysis_type == 'sharia':
            # Sharia compliance results with translation option
            display_sharia_screening_with_translation(result, translator)

        else:
            # Investment analysis results
            # Check if this was a quick screen
            is_quick_screen = False
            metadata = result.get('metadata', {})
            if 'deep_dive' in metadata and not metadata['deep_dive']:
                is_quick_screen = True
            elif metadata.get('years_analyzed') == 1 and 'context_management' not in metadata:
                is_quick_screen = True

            # Render basic results (without thesis)
            render_results(result)

            # If Quick Screen, show prominent recommendation
            if is_quick_screen:
                display_quick_screen_recommendation(result)

            # Display thesis with translation option
            display_thesis_with_translation(result, translator)

    # Handle deep dive trigger from quick screen
    if st.session_state.get('run_deep_dive', False):
        ticker = st.session_state.get('deep_dive_ticker', '')
        if ticker:
            st.info(f"🔍 Starting Deep Dive Analysis for {ticker}...")

            # Clear trigger
            st.session_state['run_deep_dive'] = False

            # Run deep dive
            run_analysis(ticker, deep_dive=True, years_to_analyze=years_to_analyze)

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
    # Get detailed cost estimate
    cost_estimate = estimate_analysis_cost(
        "deep_dive" if deep_dive else "quick",
        years_to_analyze
    )

    # Analysis info
    analysis_type = "Deep Dive" if deep_dive else "Quick Screen"

    st.markdown(f"""
    ### 🚀 Starting {analysis_type} Analysis

    **Company:** {ticker}
    **Years to Analyze:** {years_to_analyze if deep_dive else 'N/A (Quick Screen)'}
    """)

    # Show cost estimate
    st.info(
        f"💰 **Estimated Cost:** ${cost_estimate['estimated_cost']:.2f} "
        f"(${cost_estimate['min_cost']:.2f} - ${cost_estimate['max_cost']:.2f})\n\n"
        f"⏱️ **Estimated Duration:** ~{cost_estimate['duration_minutes']} minutes"
    )

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

        # Create progress tracking containers
        progress_bar = None
        status_text = None

        # Define progress callback to update UI in real-time
        def update_progress(progress_info: dict):
            """Update Streamlit UI with current progress."""
            nonlocal progress_bar, status_text

            stage = progress_info.get("stage", "")
            progress = progress_info.get("progress", 0.0)
            message = progress_info.get("message", "")

            # Create progress bar and status on first call
            if progress_bar is None:
                with progress_container:
                    progress_bar = st.progress(0.0)
                    status_text = st.empty()

            # Update progress bar and message
            progress_bar.progress(progress)
            status_text.info(f"{message}\n\nProgress: {progress*100:.0f}%")

        with progress_container:
            # Show initial status
            if deep_dive:
                st.info(
                    f"🚀 Starting Deep Dive Analysis on {ticker}\n\n"
                    f"Analyzing {years_to_analyze} year{'s' if years_to_analyze > 1 else ''} total. "
                    f"This may take 2-3 minutes per year."
                )

            # Run analysis with progress callback
            result = agent.analyze_company(
                ticker,
                deep_dive=deep_dive,
                years_to_analyze=years_to_analyze if deep_dive else 1,
                progress_callback=update_progress if deep_dive else None
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

        # Track session costs (if token usage available)
        if "token_usage" in result.get("metadata", {}):
            cost = result["metadata"]["token_usage"]["total_cost"]
            if 'session_costs' not in st.session_state:
                st.session_state['session_costs'] = []
            st.session_state['session_costs'].append(cost)

        # Success message
        st.success(
            f"✅ Analysis Complete! Completed in {duration:.0f} seconds "
            f"({duration/60:.1f} minutes)"
        )

        # Store result in session state
        # (Results will be displayed automatically by main() after rerun)
        st.session_state['last_result'] = result
        st.session_state['last_analysis_type'] = 'deep_dive' if deep_dive else 'quick'

        # Add analysis_type to metadata for proper storage classification
        if 'metadata' not in result:
            result['metadata'] = {}
        result['metadata']['analysis_type'] = 'deep_dive' if deep_dive else 'quick'

        # Auto-save to history
        storage = st.session_state.get('analysis_storage')
        if storage:
            try:
                save_result = storage.save_analysis(result)
                if save_result['success']:
                    st.sidebar.success(f"Saved to history: {save_result['analysis_id']}")
            except Exception as e:
                st.sidebar.warning(f"Failed to save to history: {e}")

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
