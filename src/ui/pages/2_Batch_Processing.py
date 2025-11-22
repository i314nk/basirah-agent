"""
Batch processing interface for basīrah.

Allows users to upload CSV files and run automated screening protocols.
"""

import streamlit as st
import time
import sys
from datetime import datetime
from pathlib import Path
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.batch.protocols import list_protocols, get_protocol
from src.batch.batch_processor import BatchProcessor
from src.storage import AnalysisStorage


def main():
    """Main batch processing page."""
    st.title("🔄 Batch Processing")
    st.markdown("Automate screening of multiple companies following a protocol.")

    # Initialize storage
    if 'analysis_storage' not in st.session_state:
        st.session_state['analysis_storage'] = AnalysisStorage()

    storage = st.session_state['analysis_storage']

    # Check if batch is running
    if st.session_state.get('batch_running', False):
        render_running_batch()
    else:
        render_batch_setup(storage)


def render_batch_setup(storage: AnalysisStorage):
    """Render batch setup interface."""

    st.subheader("📁 Upload Companies")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload CSV file with tickers",
        type=['csv'],
        help="CSV file with single 'ticker' column"
    )

    if uploaded_file:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        # Load tickers
        try:
            processor = BatchProcessor(
                protocol=get_protocol("value_only"),  # Dummy for loading
                storage=storage
            )
            tickers = processor.load_tickers_from_csv(tmp_path)

            st.success(f"✅ Loaded {len(tickers)} companies")

            # Preview
            with st.expander("📋 Preview Tickers", expanded=False):
                cols = st.columns(5)
                for i, ticker in enumerate(tickers[:50]):  # Show first 50
                    cols[i % 5].markdown(f"- {ticker}")

                if len(tickers) > 50:
                    st.info(f"... and {len(tickers) - 50} more")

            # Store in session
            st.session_state['batch_tickers'] = tickers
            st.session_state['batch_csv_path'] = tmp_path

        except Exception as e:
            st.error(f"❌ Error loading CSV: {e}")
            return

    # Protocol selection
    if st.session_state.get('batch_tickers'):
        st.divider()
        st.subheader("⚙️ Select Protocol")

        protocols = list_protocols()
        protocol_options = {p.name: p for p in protocols}

        selected_protocol_name = st.selectbox(
            "Screening Protocol",
            options=list(protocol_options.keys()),
            help="Choose how to screen companies"
        )

        selected_protocol = protocol_options[selected_protocol_name]

        # Batch name input
        st.divider()
        batch_name = st.text_input(
            "📝 Batch Name (optional)",
            placeholder="e.g., Tech Stocks Q4 2025, Halal Portfolio Screen",
            help="Give this batch a memorable name, or leave blank for auto-generated timestamp name"
        )

        # Show protocol details
        st.divider()
        st.markdown(f"**{selected_protocol.description}**")

        st.markdown("**Stages:**")
        for i, stage in enumerate(selected_protocol.stages, 1):
            st.markdown(f"{i}. **{stage.name}** - {stage.description}")

        # Check if protocol has Deep Dive stage
        from src.batch.protocols import AnalysisType
        has_deep_dive = any(stage.analysis_type == AnalysisType.DEEP_DIVE for stage in selected_protocol.stages)

        # Deep Dive years configuration
        deep_dive_years = None
        if has_deep_dive:
            st.divider()
            st.subheader("📅 Deep Dive Configuration")

            # Find default years from protocol
            default_years = 5
            for stage in selected_protocol.stages:
                if stage.analysis_type == AnalysisType.DEEP_DIVE and stage.years_to_analyze:
                    default_years = stage.years_to_analyze
                    break

            deep_dive_years = st.slider(
                "Years to Analyze (Deep Dive Stage)",
                min_value=5,
                max_value=10,
                value=min(max(default_years, 5), 10),  # Clamp to 5-10
                help="Number of years to analyze in Deep Dive stage. More years = deeper insights but higher cost."
            )

            st.info(
                f"**Selected:** {deep_dive_years} years\n\n"
                f"**Cost per company:** ~${2.09 + (deep_dive_years-1)*0.18:.2f}\n"
                f"**Time per company:** ~{10 + (deep_dive_years-5)*2} minutes"
            )

            # Update protocol with custom years
            import copy
            selected_protocol = copy.deepcopy(selected_protocol)
            for stage in selected_protocol.stages:
                if stage.analysis_type == AnalysisType.DEEP_DIVE:
                    stage.years_to_analyze = deep_dive_years
                    stage.description = f"Complete Warren Buffett analysis ({deep_dive_years} years)"

        # Cost estimate
        st.divider()
        st.subheader("💰 Cost Estimate")

        num_companies = len(st.session_state['batch_tickers'])
        estimate = selected_protocol.estimate_cost(num_companies)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Companies",
                estimate['total_companies']
            )

        with col2:
            st.metric(
                "Estimated Time",
                f"{estimate['total_time_hours']}h"
            )

        with col3:
            st.metric(
                "Estimated Cost",
                f"${estimate['total_cost_min']} - ${estimate['total_cost_max']}"
            )

        # Stage breakdown
        with st.expander("📊 Stage Breakdown", expanded=False):
            for stage_est in estimate['stage_breakdown']:
                st.markdown(
                    f"**{stage_est['stage_name']}**: "
                    f"{stage_est['companies']} companies, "
                    f"${stage_est['cost']:.2f}, "
                    f"{stage_est['time_minutes']} min"
                )

        st.info(
            "💡 **Note:** Actual cost may be lower due to filtering at each stage. "
            "Estimates assume all companies pass all stages."
        )

        # Start button
        st.divider()

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown("**Ready to start batch processing?**")
            st.markdown(f"- {num_companies} companies will be analyzed")
            st.markdown(f"- Following {selected_protocol.name} protocol")
            if deep_dive_years:
                st.markdown(f"- Deep Dive: {deep_dive_years} years of analysis")
            st.markdown(f"- Estimated duration: {estimate['total_time_hours']} hours")

        with col2:
            if st.button("🚀 Start Batch", type="primary", use_container_width=True):
                # Initialize batch processor
                processor = BatchProcessor(
                    protocol=selected_protocol,
                    storage=storage,
                    progress_callback=update_progress
                )

                # Store in session
                st.session_state['batch_processor'] = processor
                st.session_state['batch_running'] = True
                st.session_state['batch_start_time'] = datetime.now()

                # Start batch
                batch_id = processor.start_batch(
                    st.session_state['batch_tickers'],
                    batch_name=batch_name if batch_name and batch_name.strip() else None
                )
                st.session_state['batch_id'] = batch_id

                st.rerun()


def render_running_batch():
    """Render running batch interface with progress."""

    processor = st.session_state.get('batch_processor')
    if not processor:
        st.session_state['batch_running'] = False
        st.rerun()
        return

    batch_name = processor.state.get('batch_name', 'Batch Processing')
    st.subheader(f"🔄 {batch_name}")

    # Progress display
    state = processor.state

    # Overall progress
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Status", state['status'].title())

    with col2:
        current_stage = state['current_stage'] + 1
        total_stages = processor.protocol.total_stages()
        st.metric("Stage", f"{current_stage}/{total_stages}")

    with col3:
        elapsed = (datetime.now() - state['start_time']).total_seconds()
        st.metric("Elapsed Time", f"{elapsed/60:.0f} min")

    # Stage progress
    st.divider()
    st.markdown("### Current Stage Progress")

    if state['current_stage'] < processor.protocol.total_stages():
        current_stage_obj = processor.protocol.get_stage(state['current_stage'])
        st.markdown(f"**{current_stage_obj.name}**")

        # Get companies for this stage
        companies_in_stage = processor._get_companies_for_stage(state['current_stage'])
        total_in_stage = len(companies_in_stage)
        current_index = state['current_company_index']

        # Progress bar
        if total_in_stage > 0:
            progress = min(current_index / total_in_stage, 1.0)
            st.progress(progress)
            st.markdown(f"**{current_index}/{total_in_stage}** companies processed")

    # Stage statistics
    if state['stage_stats']:
        st.divider()
        st.markdown("### Stage Results")

        for stage_stat in state['stage_stats']:
            with st.expander(f"✅ {stage_stat['stage_name']}", expanded=False):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Processed", stage_stat['companies_processed'])

                with col2:
                    st.metric("Passed", stage_stat['passed'])

                with col3:
                    st.metric("Failed", stage_stat['failed'])

                if stage_stat.get('duration_seconds'):
                    st.caption(f"Duration: {stage_stat['duration_seconds']/60:.1f} minutes")

    # Control buttons
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⏸️ Stop Batch", type="secondary", use_container_width=True):
            processor.stop()
            st.success("Stopping batch (will complete current company)...")
            time.sleep(2)
            st.rerun()

    # Auto-refresh
    if state['status'] == 'running':
        time.sleep(2)
        st.rerun()
    elif state['status'] == 'complete':
        render_batch_complete(processor)
    elif state['status'] == 'paused':
        with col2:
            if st.button("▶️ Resume Batch", type="primary", use_container_width=True):
                processor.resume()
                st.rerun()


def render_batch_complete(processor: BatchProcessor):
    """Render completion summary."""
    summary = processor.get_summary()
    batch_name = summary.get('batch_name', 'Batch')

    st.success(f"✅ {batch_name} Complete!")

    st.divider()
    st.markdown(f"## 📊 Summary Report - {batch_name}")

    # Overall stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Companies", summary['total_companies'])

    with col2:
        duration_hours = summary['duration_seconds'] / 3600
        st.metric("Duration", f"{duration_hours:.1f}h")

    with col3:
        st.metric("Total Cost", f"${summary['total_cost']:.2f}")

    with col4:
        num_recommendations = len(summary.get('top_recommendations', []))
        st.metric("BUY Decisions", num_recommendations)

    # Funnel visualization
    st.divider()
    st.markdown("### 📉 Screening Funnel")

    for i, stage in enumerate(summary['stages']):
        processed = stage['companies_processed']
        passed = stage['passed']
        failed = stage['failed']

        st.markdown(f"**Stage {i+1}: {stage['name']}**")

        col1, col2 = st.columns([3, 1])

        with col1:
            if processed > 0:
                pass_rate = passed / processed * 100
                st.progress(pass_rate / 100)

        with col2:
            st.markdown(f"{passed}/{processed} passed")

        st.markdown(f"↓ *{passed} companies continue to next stage*")
        st.markdown("")

    # Top recommendations
    if summary.get('top_recommendations'):
        st.divider()
        st.markdown("### ⭐ Top Recommendations")

        for rec in summary['top_recommendations'][:10]:  # Top 10
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**{rec['ticker']}** - {rec.get('decision', 'BUY')}")

                with col2:
                    st.markdown(f"**{rec.get('conviction', 'N/A')}** conviction")

                st.divider()

    # Actions
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📁 View All Results in History", type="primary", use_container_width=True):
            st.switch_page("pages/1_History.py")

    with col3:
        if st.button("🔄 Start New Batch", use_container_width=True):
            # Reset state
            st.session_state['batch_running'] = False
            st.session_state['batch_processor'] = None
            st.session_state['batch_tickers'] = None
            st.rerun()


def update_progress(state: dict):
    """Callback for progress updates."""
    # Store in session for display
    st.session_state['batch_state'] = state


if __name__ == "__main__":
    main()
