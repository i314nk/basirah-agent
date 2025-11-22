"""
Validator enhancement module for Phase 7.7 structured data validation.

Module: src.agent.validator_checks
Purpose: Quantitative and qualitative validation checks using structured_metrics and structured_insights
Created: 2025-11-18

This module provides validation functions that leverage Phase 7.7's structured data
to catch errors that text-only validation misses.
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


def validate_quantitative_claims(structured_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate numerical claims using structured metrics data.

    Checks:
    - ROIC sanity (0-200%)
    - Margin consistency (net <= operating <= gross)
    - Free cash flow vs owner earnings consistency
    - Debt levels reasonable
    - Valuation metrics reasonable

    Args:
        structured_metrics: Dictionary containing current_year, prior_years, all_years

    Returns:
        Dictionary with validation results: {
            "passed": bool,
            "errors": List[str],
            "warnings": List[str]
        }
    """
    errors = []
    warnings = []

    if not structured_metrics or "current_year" not in structured_metrics:
        return {"passed": True, "errors": [], "warnings": ["No structured metrics available"]}

    current_metrics = structured_metrics["current_year"].get("metrics", {})

    # 1. ROIC Sanity Check
    roic = current_metrics.get("roic")
    if roic is not None:
        if roic < 0.0:
            errors.append(f"ROIC is negative ({roic*100:.1f}%). This is impossible - check calculation")
        elif roic > 2.0:  # >200%
            errors.append(f"ROIC is {roic*100:.0f}%. This seems unrealistic - likely a calculation error")
        elif roic > 1.0:  # >100% but <200%
            warnings.append(f"ROIC is very high ({roic*100:.0f}%). Verify this is not a data error")

    # 2. Margin Consistency Check
    gross_margin = current_metrics.get("gross_margin")
    operating_margin = current_metrics.get("operating_margin")
    net_margin = current_metrics.get("net_margin")

    if operating_margin is not None and gross_margin is not None:
        if operating_margin > gross_margin:
            errors.append(
                f"Operating margin ({operating_margin*100:.1f}%) exceeds gross margin "
                f"({gross_margin*100:.1f}%). This violates accounting logic"
            )

    if net_margin is not None and operating_margin is not None:
        if net_margin > operating_margin + 0.05:  # Allow small variance for one-time gains
            warnings.append(
                f"Net margin ({net_margin*100:.1f}%) significantly exceeds operating margin "
                f"({operating_margin*100:.1f}%). Check for one-time gains"
            )

    # 3. Free Cash Flow vs Owner Earnings
    fcf = current_metrics.get("free_cash_flow")
    owner_earnings = current_metrics.get("owner_earnings")

    if fcf is not None and owner_earnings is not None and fcf > 0 and owner_earnings > 0:
        diff_pct = abs(fcf - owner_earnings) / max(fcf, owner_earnings)
        if diff_pct > 0.5:  # >50% difference
            warnings.append(
                f"FCF (${fcf:.0f}M) and Owner Earnings (${owner_earnings:.0f}M) differ by "
                f"{diff_pct*100:.0f}%. Investigate the discrepancy"
            )

    # 4. Debt/Equity Reasonableness
    debt_equity = current_metrics.get("debt_equity")
    if debt_equity is not None:
        if debt_equity < 0:
            errors.append(f"Debt/Equity is negative ({debt_equity:.2f}). This is impossible")
        elif debt_equity > 10:
            warnings.append(f"Debt/Equity is extremely high ({debt_equity:.1f}). Verify this is correct")

    # 5. Valuation Metrics
    margin_of_safety = current_metrics.get("margin_of_safety")
    if margin_of_safety is not None:
        if margin_of_safety < -2.0:  # >200% overvalued
            warnings.append(f"Margin of Safety is {margin_of_safety*100:.0f}%. Stock appears extremely overvalued")

    current_price = current_metrics.get("current_price")
    dcf_intrinsic_value = current_metrics.get("dcf_intrinsic_value")
    if current_price is not None and dcf_intrinsic_value is not None:
        if current_price <= 0 or dcf_intrinsic_value <= 0:
            errors.append(f"Price (${current_price}) or Intrinsic Value (${dcf_intrinsic_value}) is non-positive")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_decision_consistency(
    decision: str,
    conviction: str,
    structured_metrics: Dict[str, Any],
    structured_insights: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Verify investment decision aligns with Warren Buffett's criteria.

    Checks:
    - BUY requires: STRONG/DOMINANT moat + ROIC >15% + MoS >20%
    - BUY shouldn't have HIGH risk rating
    - AVOID should have clear reasons (weak moat OR high debt OR low ROIC)

    Args:
        decision: BUY/WATCH/AVOID
        conviction: HIGH/MODERATE/LOW
        structured_metrics: Metrics data
        structured_insights: Insights data

    Returns:
        Dictionary with validation results
    """
    errors = []
    warnings = []

    if not structured_metrics or not structured_insights:
        return {"passed": True, "errors": [], "warnings": ["No structured data available"]}

    current_metrics = structured_metrics.get("current_year", {}).get("metrics", {})
    current_insights = structured_insights.get("current_year", {}).get("insights", {})

    # Extract key metrics
    roic = current_metrics.get("roic")
    margin_of_safety = current_metrics.get("margin_of_safety")
    debt_equity = current_metrics.get("debt_equity")

    # Extract key insights
    moat_rating = current_insights.get("moat_rating")
    risk_rating = current_insights.get("risk_rating")

    # Validate BUY decision
    if decision == "BUY":
        # Must have strong moat
        if moat_rating and moat_rating not in ["STRONG", "DOMINANT"]:
            warnings.append(
                f"BUY decision with only {moat_rating} moat. Buffett typically requires STRONG+ moat for BUY"
            )

        # Must have high ROIC
        if roic is not None and roic < 0.15:
            warnings.append(
                f"BUY decision but ROIC only {roic*100:.0f}%. Buffett typically requires >15% ROIC"
            )

        # Should have margin of safety
        if margin_of_safety is not None and margin_of_safety < 0.20:
            warnings.append(
                f"BUY decision but Margin of Safety only {margin_of_safety*100:.0f}%. "
                f"Buffett typically requires >20% MoS"
            )

        # Shouldn't have HIGH risk
        if risk_rating == "HIGH":
            warnings.append(
                "BUY decision despite HIGH risk rating. Ensure risk assessment is accurate"
            )

        # Should have HIGH conviction for BUY
        if conviction != "HIGH":
            warnings.append(
                f"BUY decision but only {conviction} conviction. Buffett rarely buys without high conviction"
            )

    # Validate AVOID decision
    elif decision == "AVOID":
        # Should have clear reason: weak moat OR high debt OR low ROIC
        has_avoid_reason = False

        if moat_rating and moat_rating == "WEAK":
            has_avoid_reason = True

        if roic is not None and roic < 0.10:
            has_avoid_reason = True

        if debt_equity is not None and debt_equity > 2.0:
            has_avoid_reason = True

        if not has_avoid_reason:
            warnings.append(
                "AVOID decision but metrics don't show obvious red flags. "
                "Verify qualitative concerns are well-documented"
            )

    # Validate WATCH decision
    elif decision == "WATCH":
        # WATCH is appropriate - just check conviction isn't too high
        if conviction == "HIGH":
            warnings.append(
                "WATCH decision with HIGH conviction seems contradictory. "
                "Consider BUY if highly convicted, or MODERATE conviction for WATCH"
            )

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_completeness(
    structured_metrics: Dict[str, Any],
    structured_insights: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Check if all required data fields are populated.

    Required metrics: ROIC, revenue, operating_margin, debt_equity
    Required insights: decision, conviction, moat_rating, risk_rating

    Args:
        structured_metrics: Metrics data
        structured_insights: Insights data

    Returns:
        Dictionary with validation results
    """
    errors = []
    warnings = []

    # Required metrics
    required_metrics = ["roic", "revenue", "operating_margin", "debt_equity"]
    missing_metrics = []

    if structured_metrics and "current_year" in structured_metrics:
        current_metrics = structured_metrics["current_year"].get("metrics", {})
        for metric in required_metrics:
            if metric not in current_metrics or current_metrics[metric] is None:
                missing_metrics.append(metric)

        if missing_metrics:
            warnings.append(f"Missing required metrics: {', '.join(missing_metrics)}")

    # Required insights
    required_insights = ["decision", "conviction", "moat_rating", "risk_rating"]
    missing_insights = []

    if structured_insights and "current_year" in structured_insights:
        current_insights = structured_insights["current_year"].get("insights", {})
        for insight in required_insights:
            if insight not in current_insights or not current_insights[insight]:
                missing_insights.append(insight)

        if missing_insights:
            warnings.append(f"Missing required insights: {', '.join(missing_insights)}")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_trend_claims(
    thesis: str,
    structured_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Verify claims about trends match actual historical data.

    Examples:
    - "Revenue growing rapidly" → Check actual revenue growth rate
    - "Improving margins" → Check margin trend
    - "Consistent ROIC" → Check ROIC volatility

    Args:
        thesis: Full analysis text
        structured_metrics: Metrics with all_years data

    Returns:
        Dictionary with validation results
    """
    errors = []
    warnings = []

    if not structured_metrics or "all_years" not in structured_metrics:
        return {"passed": True, "errors": [], "warnings": ["No historical data for trend validation"]}

    all_years = structured_metrics["all_years"]
    if len(all_years) < 2:
        return {"passed": True, "errors": [], "warnings": ["Need 2+ years for trend validation"]}

    # Sort by year (most recent first)
    all_years = sorted(all_years, key=lambda x: x.get("year", 0), reverse=True)

    # Extract revenue trend
    revenues = [y.get("metrics", {}).get("revenue") for y in all_years if y.get("metrics", {}).get("revenue")]

    if len(revenues) >= 2:
        # Calculate growth rate (most recent vs oldest)
        total_growth = (revenues[0] - revenues[-1]) / revenues[-1] if revenues[-1] != 0 else 0
        years_span = len(revenues) - 1
        cagr = (revenues[0] / revenues[-1]) ** (1 / years_span) - 1 if years_span > 0 and revenues[-1] > 0 else 0

        # Check claims about revenue growth
        thesis_lower = thesis.lower()

        if "revenue growing rapidly" in thesis_lower or "rapid revenue growth" in thesis_lower:
            if cagr < 0.10:  # <10% CAGR
                warnings.append(
                    f"Claims 'rapid revenue growth' but CAGR is only {cagr*100:.1f}% over {years_span} years"
                )

        if "revenue declining" in thesis_lower or "revenue shrinking" in thesis_lower:
            if cagr > 0:
                warnings.append(
                    f"Claims 'revenue declining' but revenue actually grew {cagr*100:.1f}% annually"
                )

        if "stagnant revenue" in thesis_lower or "flat revenue" in thesis_lower:
            if abs(cagr) > 0.05:  # >5% growth or decline
                warnings.append(
                    f"Claims 'stagnant revenue' but revenue changed {cagr*100:.1f}% annually"
                )

    # Extract margin trend
    operating_margins = [
        y.get("metrics", {}).get("operating_margin")
        for y in all_years
        if y.get("metrics", {}).get("operating_margin") is not None
    ]

    if len(operating_margins) >= 2:
        margin_change = operating_margins[0] - operating_margins[-1]

        thesis_lower = thesis.lower()

        if "expanding margins" in thesis_lower or "improving margins" in thesis_lower:
            if margin_change < 0:
                warnings.append(
                    f"Claims 'expanding margins' but operating margin declined "
                    f"{abs(margin_change)*100:.1f}pp over the period"
                )

        if "margin compression" in thesis_lower or "declining margins" in thesis_lower:
            if margin_change > 0:
                warnings.append(
                    f"Claims 'margin compression' but operating margin actually expanded "
                    f"{margin_change*100:.1f}pp"
                )

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def run_all_validations(
    analysis_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run all structured data validations.

    Args:
        analysis_result: Full analysis result with structured_metrics and structured_insights

    Returns:
        Dictionary with all validation results: {
            "quantitative": {...},
            "decision_consistency": {...},
            "completeness": {...},
            "trends": {...},
            "overall_passed": bool,
            "total_errors": int,
            "total_warnings": int
        }
    """
    metadata = analysis_result.get("metadata", {})
    structured_metrics = metadata.get("structured_metrics", {})
    structured_insights = metadata.get("structured_insights", {})
    thesis = analysis_result.get("thesis", "")
    decision = analysis_result.get("decision", "WATCH")
    conviction = analysis_result.get("conviction", "MODERATE")

    # Run all validations
    results = {
        "quantitative": validate_quantitative_claims(structured_metrics),
        "decision_consistency": validate_decision_consistency(
            decision, conviction, structured_metrics, structured_insights
        ),
        "completeness": validate_completeness(structured_metrics, structured_insights),
        "trends": validate_trend_claims(thesis, structured_metrics)
    }

    # Aggregate results
    total_errors = sum(len(r.get("errors", [])) for r in results.values())
    total_warnings = sum(len(r.get("warnings", [])) for r in results.values())
    overall_passed = all(r.get("passed", True) for r in results.values())

    results.update({
        "overall_passed": overall_passed,
        "total_errors": total_errors,
        "total_warnings": total_warnings
    })

    # Log results
    if total_errors > 0:
        logger.warning(f"[VALIDATOR] Structured data validation found {total_errors} errors, {total_warnings} warnings")
    elif total_warnings > 0:
        logger.info(f"[VALIDATOR] Structured data validation found {total_warnings} warnings")
    else:
        logger.info("[VALIDATOR] Structured data validation passed")

    return results
