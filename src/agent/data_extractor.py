"""
Data extraction utilities for Phase 7.7 hybrid architecture.

Module: src.agent.data_extractor
Purpose: Extract structured metrics from tool outputs (GuruFocus, Calculator, etc.)
Status: Phase 7.7 - In Development
Created: 2025-11-16

This module provides functions to extract quantitative metrics from various
tool outputs into structured AnalysisMetrics objects.

Functions:
- extract_gurufocus_metrics: Extract metrics from GuruFocus API responses
- extract_calculator_metrics: Extract metrics from Calculator tool outputs
- extract_sec_filing_insights: Extract qualitative insights from SEC filings
- merge_metrics: Combine metrics from multiple sources
"""

from typing import Dict, List, Optional, Any
import logging

from src.agent.data_structures import AnalysisMetrics, AnalysisInsights, ToolCache

logger = logging.getLogger(__name__)


def extract_gurufocus_metrics(
    summary: Optional[Dict[str, Any]] = None,
    financials: Optional[Dict[str, Any]] = None,
    keyratios: Optional[Dict[str, Any]] = None,
    valuation: Optional[Dict[str, Any]] = None
) -> AnalysisMetrics:
    """
    Extract structured metrics from GuruFocus API responses.

    Args:
        summary: GuruFocus summary endpoint response
        financials: GuruFocus financials endpoint response
        keyratios: GuruFocus keyratios endpoint response
        valuation: GuruFocus valuation endpoint response

    Returns:
        AnalysisMetrics object with extracted data

    Example:
        ```python
        metrics = extract_gurufocus_metrics(
            summary=gf_summary_data,
            financials=gf_financials_data
        )
        print(f"ROIC: {metrics.roic:.1%}")
        print(f"Revenue: ${metrics.revenue:,.0f}")
        ```
    """
    metrics = AnalysisMetrics()

    # Extract from summary
    if summary:
        company = summary.get("company", {})
        metrics.market_share = _safe_float(company.get("market_share"))
        metrics.current_price = _safe_float(summary.get("price"))
        metrics.pe_ratio = _safe_float(summary.get("pe_ratio"))
        metrics.pb_ratio = _safe_float(summary.get("pb_ratio"))

    # Extract from financials
    if financials:
        # Get most recent year data (index 0)
        if "financials" in financials and len(financials["financials"]) > 0:
            latest = financials["financials"][0]

            # Income statement
            metrics.revenue = _safe_float(latest.get("revenue"))
            metrics.operating_income = _safe_float(latest.get("operating_income"))
            metrics.net_income = _safe_float(latest.get("net_income"))

            # Balance sheet
            metrics.total_assets = _safe_float(latest.get("total_assets"))
            metrics.total_debt = _safe_float(latest.get("total_debt"))
            metrics.cash_and_equivalents = _safe_float(latest.get("cash_and_equivalents"))
            metrics.shareholders_equity = _safe_float(latest.get("shareholders_equity"))

            # Cash flow
            metrics.operating_cash_flow = _safe_float(latest.get("operating_cash_flow"))
            metrics.capex = _safe_float(latest.get("capex"))
            if metrics.operating_cash_flow and metrics.capex:
                metrics.free_cash_flow = metrics.operating_cash_flow - metrics.capex

            # Margins (may be pre-calculated or need calculation)
            metrics.gross_margin = _safe_float(latest.get("gross_margin"))
            metrics.operating_margin = _safe_float(latest.get("operating_margin"))
            metrics.net_margin = _safe_float(latest.get("net_margin"))

            # Calculate margins if not provided
            if metrics.revenue:
                if not metrics.gross_margin and latest.get("gross_profit"):
                    metrics.gross_margin = _safe_float(latest.get("gross_profit")) / metrics.revenue
                if not metrics.operating_margin and metrics.operating_income:
                    metrics.operating_margin = metrics.operating_income / metrics.revenue
                if not metrics.net_margin and metrics.net_income:
                    metrics.net_margin = metrics.net_income / metrics.revenue

    # Extract from keyratios
    if keyratios:
        keyratios_data = keyratios.get("keyratios", {})

        # Returns
        metrics.roic = _safe_float(keyratios_data.get("roic"))
        metrics.roe = _safe_float(keyratios_data.get("roe"))
        metrics.roa = _safe_float(keyratios_data.get("roa"))

        # Debt coverage
        metrics.debt_equity = _safe_float(keyratios_data.get("debt_equity"))
        metrics.interest_coverage = _safe_float(keyratios_data.get("interest_coverage"))

        # Calculate cash to debt if we have the data
        if metrics.cash_and_equivalents and metrics.total_debt and metrics.total_debt > 0:
            metrics.cash_to_debt = metrics.cash_and_equivalents / metrics.total_debt

        # ROIC history (10-year)
        roic_history = keyratios_data.get("roic_10yr", [])
        if roic_history and len(roic_history) > 0:
            metrics.roic_10yr = [_safe_float(r) for r in roic_history]
            # Calculate average and std dev
            valid_roics = [r for r in metrics.roic_10yr if r is not None]
            if valid_roics:
                metrics.roic_avg = sum(valid_roics) / len(valid_roics)
                if len(valid_roics) > 1:
                    mean = metrics.roic_avg
                    variance = sum((r - mean) ** 2 for r in valid_roics) / (len(valid_roics) - 1)
                    metrics.roic_stddev = variance ** 0.5

    # Extract from valuation
    if valuation:
        val_data = valuation.get("valuation", {})
        metrics.ev_ebitda = _safe_float(val_data.get("ev_ebitda"))
        # Note: We do NOT extract GF Value or DCF Value here - only market price
        # Per FIX_INTRINSIC_VALUE_METHODOLOGY.md: GuruFocus is for DATA only

    # Screen criteria flags
    if metrics.roic is not None:
        # Phase 1 screen: ROIC > 15%
        if metrics.debt_equity is not None:
            # Check if passes initial screen
            metrics.earnings_consistent = (
                metrics.roic >= 0.15 and
                metrics.debt_equity < 1.0
            )

    return metrics


def extract_calculator_metrics(
    calculator_outputs: Dict[str, Any]
) -> AnalysisMetrics:
    """
    Extract structured metrics from Calculator tool outputs.

    Args:
        calculator_outputs: Dictionary of calculator results keyed by calculation type

    Returns:
        AnalysisMetrics object with calculated values

    Example:
        ```python
        calc_outputs = {
            "owner_earnings": {"result": 473_800_000, "per_share": 3.71},
            "roic": {"result": 0.28, "nopat": 810_000_000},
            "dcf": {"intrinsic_value": 61.26, "margin_of_safety": -0.057}
        }
        metrics = extract_calculator_metrics(calc_outputs)
        ```
    """
    metrics = AnalysisMetrics()

    # Owner Earnings calculation
    if "owner_earnings" in calculator_outputs:
        oe = calculator_outputs["owner_earnings"]
        metrics.owner_earnings = _safe_float(oe.get("result"))
        # Could also extract components (OCF, CapEx) if needed

    # ROIC calculation
    if "roic" in calculator_outputs:
        roic_data = calculator_outputs["roic"]
        metrics.roic = _safe_float(roic_data.get("result"))

    # DCF Valuation
    if "dcf" in calculator_outputs:
        dcf = calculator_outputs["dcf"]
        metrics.dcf_intrinsic_value = _safe_float(dcf.get("intrinsic_value"))
        metrics.growth_rate = _safe_float(dcf.get("growth_rate"))
        metrics.discount_rate = _safe_float(dcf.get("discount_rate"))
        metrics.terminal_growth = _safe_float(dcf.get("terminal_growth"))
        metrics.owner_earnings_normalized = _safe_float(dcf.get("normalized_owner_earnings"))

    # Margin of Safety
    if "margin_of_safety" in calculator_outputs:
        mos = calculator_outputs["margin_of_safety"]
        metrics.margin_of_safety = _safe_float(mos.get("result"))
        if not metrics.dcf_intrinsic_value:
            metrics.dcf_intrinsic_value = _safe_float(mos.get("intrinsic_value"))
        if not metrics.current_price:
            metrics.current_price = _safe_float(mos.get("current_price"))

    # Shares outstanding (often included in calculator outputs)
    for calc_type, calc_data in calculator_outputs.items():
        if "shares_outstanding" in calc_data and not metrics.shares_outstanding:
            metrics.shares_outstanding = _safe_float(calc_data.get("shares_outstanding"))
            break

    return metrics


def merge_metrics(
    base: AnalysisMetrics,
    *additional: AnalysisMetrics
) -> AnalysisMetrics:
    """
    Merge multiple AnalysisMetrics objects.

    Non-None values from additional metrics override base metrics.

    Args:
        base: Base AnalysisMetrics object
        *additional: Additional AnalysisMetrics objects to merge

    Returns:
        Merged AnalysisMetrics object

    Example:
        ```python
        gf_metrics = extract_gurufocus_metrics(summary, financials)
        calc_metrics = extract_calculator_metrics(calculator_outputs)
        combined = merge_metrics(gf_metrics, calc_metrics)
        ```
    """
    # Pydantic: Use model_dump() instead of to_dict()
    result_dict = base.model_dump(exclude_none=False)

    for metrics in additional:
        # Only merge non-None values
        override_dict = metrics.model_dump(exclude_none=True)
        result_dict.update(override_dict)

    # Create new AnalysisMetrics from merged dict (Pydantic will validate)
    return AnalysisMetrics(**result_dict)


def extract_sec_filing_insights(
    sec_10k_full: Optional[str] = None,
    sec_10k_mda: Optional[str] = None,
    sec_10k_risk_factors: Optional[str] = None,
    sec_proxy: Optional[str] = None
) -> AnalysisInsights:
    """
    Extract qualitative insights from SEC filings.

    Note: This is a placeholder for now. Full extraction requires NLP/LLM analysis.
    For Phase 7.7, the LLM still generates insights text - we just structure it.

    Args:
        sec_10k_full: Complete 10-K text
        sec_10k_mda: MD&A section
        sec_10k_risk_factors: Risk factors section
        sec_proxy: Proxy statement

    Returns:
        AnalysisInsights object (mostly empty - to be populated by LLM)
    """
    insights = AnalysisInsights()

    # For now, just return empty structure
    # The LLM will populate these fields in the analysis stage
    # This function exists for future enhancement (e.g., keyword extraction)

    logger.debug("SEC filing insights extraction placeholder called")
    return insights


def create_tool_cache(
    gurufocus_summary: Optional[Dict[str, Any]] = None,
    gurufocus_financials: Optional[Dict[str, Any]] = None,
    gurufocus_keyratios: Optional[Dict[str, Any]] = None,
    gurufocus_valuation: Optional[Dict[str, Any]] = None,
    sec_10k_full: Optional[str] = None,
    sec_10k_business: Optional[str] = None,
    sec_10k_mda: Optional[str] = None,
    sec_10k_risk_factors: Optional[str] = None,
    sec_10q: Optional[str] = None,
    sec_proxy: Optional[str] = None,
    web_search_results: Optional[Dict[str, Any]] = None,
    calculator_outputs: Optional[Dict[str, Any]] = None
) -> ToolCache:
    """
    Create a ToolCache object from tool outputs.

    Args:
        gurufocus_*: GuruFocus API responses
        sec_*: SEC filing texts
        web_search_results: Web search results
        calculator_outputs: Calculator tool results

    Returns:
        ToolCache object with all provided data

    Example:
        ```python
        cache = create_tool_cache(
            gurufocus_summary=gf_summary,
            sec_10k_full=filing_text,
            calculator_outputs=calc_results
        )
        ```
    """
    return ToolCache(
        gurufocus_summary=gurufocus_summary,
        gurufocus_financials=gurufocus_financials,
        gurufocus_keyratios=gurufocus_keyratios,
        gurufocus_valuation=gurufocus_valuation,
        sec_10k_full=sec_10k_full,
        sec_10k_business=sec_10k_business,
        sec_10k_mda=sec_10k_mda,
        sec_10k_risk_factors=sec_10k_risk_factors,
        sec_10q=sec_10q,
        sec_proxy=sec_proxy,
        web_search_results=web_search_results or {},
        calculator_outputs=calculator_outputs or {}
    )


def _safe_float(value: Any) -> Optional[float]:
    """
    Safely convert value to float, returning None if conversion fails.

    Args:
        value: Value to convert (can be str, int, float, or None)

    Returns:
        Float value or None

    Example:
        >>> _safe_float("123.45")
        123.45
        >>> _safe_float("N/A")
        None
        >>> _safe_float(None)
        None
    """
    if value is None or value == "" or value == "N/A":
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _safe_int(value: Any) -> Optional[int]:
    """
    Safely convert value to int, returning None if conversion fails.

    Args:
        value: Value to convert

    Returns:
        Integer value or None
    """
    if value is None or value == "" or value == "N/A":
        return None

    try:
        return int(float(value))  # Convert via float first to handle "123.0"
    except (ValueError, TypeError):
        return None


# Utility function for extracting 10-year ROIC trend
def extract_roic_trend(keyratios: Dict[str, Any]) -> Optional[List[float]]:
    """
    Extract 10-year ROIC trend from GuruFocus keyratios.

    Args:
        keyratios: GuruFocus keyratios endpoint response

    Returns:
        List of ROIC values [current, -1yr, -2yr, ..., -9yr] or None

    Example:
        ```python
        roic_trend = extract_roic_trend(gf_keyratios)
        if roic_trend:
            print(f"ROIC consistency: {min(roic_trend):.1%} to {max(roic_trend):.1%}")
        ```
    """
    keyratios_data = keyratios.get("keyratios", {})
    roic_history = keyratios_data.get("roic_10yr", [])

    if not roic_history or len(roic_history) == 0:
        return None

    return [_safe_float(r) for r in roic_history]


__all__ = [
    "extract_gurufocus_metrics",
    "extract_calculator_metrics",
    "merge_metrics",
    "extract_sec_filing_insights",
    "create_tool_cache",
    "extract_roic_trend"
]
