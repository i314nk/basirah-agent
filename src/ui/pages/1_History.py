"""
Analysis History Page - basīrah

Browse and search past analyses.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.storage import AnalysisStorage, AnalysisSearchEngine

# Page config
st.set_page_config(
    page_title="Analysis History - basīrah",
    page_icon="📁",
    layout="wide"
)

# Initialize
@st.cache_resource
def get_storage():
    return AnalysisStorage()

@st.cache_resource
def get_search():
    return AnalysisSearchEngine()

storage = get_storage()
search = get_search()

# Header
st.title("📁 Analysis History")
st.markdown("Browse and search your past investment analyses")

st.divider()

# Statistics
st.subheader("📊 Overview")
stats = search.get_statistics()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Analyses", stats.get('total_analyses', 0) or 0)
with col2:
    st.metric("Unique Companies", stats.get('unique_companies', 0) or 0)
with col3:
    st.metric("Total Cost", f"${stats.get('total_cost') or 0:.2f}")
with col4:
    st.metric("Avg Cost", f"${stats.get('avg_cost') or 0:.2f}")

st.divider()

# Search
st.subheader("🔍 Search")

col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input("Search by ticker or company name", placeholder="e.g., AAPL, Apple")

with col2:
    days_back = st.selectbox("Time Period", [7, 30, 90, 365, "All Time"], index=1)

# Filters
with st.expander("⚙️ Advanced Filters"):
    col1, col2, col3 = st.columns(3)

    with col1:
        analysis_types = st.multiselect(
            "Analysis Type",
            ["quick", "deep_dive", "sharia"],
            default=["quick", "deep_dive", "sharia"]
        )

    with col2:
        decisions = st.multiselect(
            "Decision",
            ["buy", "watch", "avoid", "investigate", "pass", "compliant", "doubtful", "non_compliant"],
            default=["buy", "watch", "avoid", "investigate", "pass", "compliant", "doubtful", "non_compliant"]
        )

    with col3:
        sort_by = st.selectbox("Sort By", ["date", "ticker", "cost", "roic"], index=0)

# Get results
if search_query:
    results = search.quick_search(search_query)
elif days_back == "All Time":
    results = search.search(
        analysis_types=analysis_types if analysis_types else None,
        decisions=decisions if decisions else None,
        sort_by=sort_by,
        sort_order="desc",
        limit=100
    )
else:
    results = search.search(
        analysis_types=analysis_types if analysis_types else None,
        decisions=decisions if decisions else None,
        date_from=str((datetime.now() - timedelta(days=days_back)).date()),
        sort_by=sort_by,
        sort_order="desc",
        limit=100
    )

# Display results
st.divider()
st.subheader(f"📋 Results ({len(results)} found)")

if not results:
    st.info("No analyses found. Start by running some analyses from the main page!")
else:
    for result in results:
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.markdown(f"### {result['ticker']} - {result['company_name']}")

            with col2:
                type_emoji = {'quick': '⚡', 'deep_dive': '🔍', 'sharia': '☪️'}
                emoji = type_emoji.get(result['analysis_type'], '📊')
                analysis_type_display = result['analysis_type'].replace('_', ' ').title()

                # Add years info for deep dive analyses
                if result['analysis_type'] == 'deep_dive' and result.get('years_analyzed'):
                    years = result['years_analyzed']
                    analysis_type_display = f"{analysis_type_display} ({years} year{'s' if years > 1 else ''})"

                st.markdown(f"{emoji} **{analysis_type_display}**")

            with col3:
                st.markdown(f"*{result['analysis_date']}*")

            # Metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                decision = result['decision'].upper()
                if decision in ['BUY', 'INVESTIGATE', 'COMPLIANT']:
                    st.success(f"**{decision}**")
                elif decision in ['WATCH', 'DOUBTFUL']:
                    st.warning(f"**{decision}**")
                else:
                    st.error(f"**{decision}**")

            with col2:
                if result.get('conviction'):
                    st.markdown(f"**Conviction:** {result['conviction']}")

            with col3:
                if result.get('roic'):
                    st.markdown(f"**ROIC:** {result['roic']:.1f}%")

            with col4:
                if result.get('margin_of_safety'):
                    st.markdown(f"**MoS:** {result['margin_of_safety']:.1f}%")

            # Thesis preview
            if result.get('thesis_preview'):
                with st.expander("📄 Thesis Preview"):
                    st.markdown(result['thesis_preview'])

            # Actions
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                if st.button(f"View Full Analysis", key=f"view_{result['id']}"):
                    analysis = storage.load_analysis(result['analysis_id'])
                    if analysis:
                        with st.expander("Full Analysis", expanded=True):
                            st.markdown(analysis.get('thesis', analysis.get('analysis', 'No content')))

            with col2:
                cost_duration = f"Cost: ${result.get('cost', 0):.2f} | Duration: {result.get('duration_seconds', 0)}s"
                # Add years for deep dive analyses
                if result['analysis_type'] == 'deep_dive' and result.get('years_analyzed'):
                    cost_duration += f" | Years: {result['years_analyzed']}"
                st.markdown(cost_duration)

            with col3:
                if st.button("Delete", key=f"delete_{result['id']}", type="secondary", use_container_width=True):
                    st.session_state[f'confirm_delete_{result["id"]}'] = True

            # Confirmation dialog
            if st.session_state.get(f'confirm_delete_{result["id"]}', False):
                with st.container():
                    st.warning(f"⚠️ Are you sure you want to delete this analysis for **{result['ticker']}**?")
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("Yes, Delete", key=f"confirm_yes_{result['id']}", type="primary"):
                            if storage.delete_analysis(result['analysis_id']):
                                st.success(f"✓ Deleted analysis: {result['analysis_id']}")
                                # Clear confirmation state
                                st.session_state[f'confirm_delete_{result["id"]}'] = False
                                # Clear cache and refresh
                                get_storage.clear()
                                get_search.clear()
                                st.rerun()
                            else:
                                st.error("Failed to delete analysis")

                    with col2:
                        if st.button("Cancel", key=f"confirm_no_{result['id']}"):
                            st.session_state[f'confirm_delete_{result["id"]}'] = False
                            st.rerun()

            st.divider()

# Sidebar
with st.sidebar:
    st.header("Analysis History")

    # Recent analyses
    st.subheader("Recent Analyses")
    recent = search.get_recent(days=7, limit=5)

    if recent:
        for r in recent:
            st.markdown(f"**{r['ticker']}** - {r['analysis_date']}")
            st.markdown(f"_{r['analysis_type'].replace('_', ' ').title()}: {r['decision'].upper()}_")
            st.markdown("---")
    else:
        st.info("No recent analyses")

    # Companies
    st.subheader("Companies Analyzed")
    companies = search.get_companies()[:5]

    if companies:
        for company in companies:
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"**{company['ticker']}** - {company['total_analyses']} analyses")

            with col2:
                if st.button("🗑️", key=f"delete_company_{company['ticker']}",
                           help=f"Delete {company['ticker']} and all analyses",
                           use_container_width=True):
                    st.session_state[f'confirm_delete_company_{company["ticker"]}'] = True

            # Confirmation dialog
            if st.session_state.get(f'confirm_delete_company_{company["ticker"]}', False):
                st.warning(f"⚠️ Delete **{company['ticker']}** and all {company['total_analyses']} analyses?")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Yes, Delete All",
                               key=f"confirm_yes_company_{company['ticker']}",
                               type="primary"):
                        result = storage.delete_company(company['ticker'])
                        if result['success']:
                            st.success(f"✓ {result['message']}")
                            st.session_state[f'confirm_delete_company_{company["ticker"]}'] = False
                            # Clear cache and refresh
                            get_storage.clear()
                            get_search.clear()
                            st.rerun()
                        else:
                            st.error(f"Failed: {result['message']}")

                with col2:
                    if st.button("Cancel", key=f"confirm_no_company_{company['ticker']}"):
                        st.session_state[f'confirm_delete_company_{company["ticker"]}'] = False
                        st.rerun()

            st.markdown("---")
    else:
        st.info("No companies yet")
