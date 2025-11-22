"""
Validator Auto-Correction Module

Uses cached tool data as source of truth to automatically correct errors
in analysis without relying on LLM text editing.

Phase 7.7.5: Validator-Driven Auto-Correction
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ValidatorCorrections:
    """Auto-correct analysis using cached data as source of truth."""

    def __init__(self):
        self.corrections_applied = []

    def auto_correct_analysis(
        self,
        analysis: Dict[str, Any],
        validator_issues: List[Dict[str, Any]],
        tool_cache: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Auto-correct analysis using cached data.

        Args:
            analysis: The analysis to correct
            validator_issues: Issues identified by validator
            tool_cache: Cached tool results (source of truth)

        Returns:
            Corrected analysis with corrections_log
        """
        logger.info("[AUTO-CORRECT] Starting auto-correction using cached data")

        corrected = analysis.copy()
        corrections_log = []

        for issue in validator_issues:
            severity = issue.get('severity', 'unknown')
            category = issue.get('category', 'unknown')

            # Only auto-correct data and calculation issues
            if category in ['data', 'calculations']:
                correction = self._apply_correction(
                    corrected,
                    issue,
                    tool_cache
                )
                if correction:
                    corrections_log.append(correction)
                    logger.info(f"[AUTO-CORRECT] Applied: {correction['description']}")

        # Add corrections metadata
        if 'metadata' not in corrected:
            corrected['metadata'] = {}
        corrected['metadata']['auto_corrections'] = {
            'total_corrections': len(corrections_log),
            'corrections': corrections_log
        }

        logger.info(f"[AUTO-CORRECT] Applied {len(corrections_log)} corrections")
        return corrected

    def _apply_correction(
        self,
        analysis: Dict[str, Any],
        issue: Dict[str, Any],
        tool_cache: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """
        Apply a single correction using cached data.

        Returns:
            Correction log entry if successful, None if no correction possible
        """
        description = issue.get('description', '')

        # Extract metric name from issue description
        if 'ROIC' in description.upper():
            return self._correct_roic(analysis, tool_cache, description)
        elif 'OWNER EARNINGS' in description.upper() or 'OCF' in description.upper():
            return self._correct_owner_earnings(analysis, tool_cache, description)
        elif 'REVENUE' in description.upper():
            return self._correct_revenue(analysis, tool_cache, description)
        elif 'OPERATING MARGIN' in description.upper():
            return self._correct_margin(analysis, tool_cache, description, 'operating_margin')
        elif 'GROSS MARGIN' in description.upper():
            return self._correct_margin(analysis, tool_cache, description, 'gross_margin')
        elif 'DEBT' in description.upper() or 'D/E' in description.upper():
            return self._correct_debt(analysis, tool_cache, description)

        return None

    def _correct_roic(
        self,
        analysis: Dict[str, Any],
        tool_cache: Dict[str, Any],
        issue_description: str
    ) -> Optional[Dict[str, str]]:
        """Correct ROIC using cached GuruFocus data."""
        # Find GuruFocus keyratios in cache
        gf_keyratios = None
        for key, value in tool_cache.items():
            if 'gurufocus' in str(key).lower() and 'keyratios' in str(key).lower():
                gf_keyratios = value
                break

        if not gf_keyratios or not isinstance(gf_keyratios, dict):
            logger.debug("[AUTO-CORRECT] No GuruFocus keyratios in cache")
            return None

        # Extract ROIC from cached data
        data = gf_keyratios.get('data', {})
        metrics = data.get('metrics', {})
        cached_roic = metrics.get('roic')

        if cached_roic is None:
            logger.debug("[AUTO-CORRECT] No ROIC in cached GuruFocus data")
            return None

        # Update analysis
        old_roic = analysis.get('roic', 'unknown')
        analysis['roic'] = cached_roic

        return {
            'field': 'roic',
            'old_value': str(old_roic),
            'new_value': f"{cached_roic:.1%}" if isinstance(cached_roic, float) else str(cached_roic),
            'source': 'GuruFocus (cached)',
            'description': f"Corrected ROIC from {old_roic} to {cached_roic:.1%} using cached GuruFocus data"
        }

    def _correct_owner_earnings(
        self,
        analysis: Dict[str, Any],
        tool_cache: Dict[str, Any],
        issue_description: str
    ) -> Optional[Dict[str, str]]:
        """
        Correct Owner Earnings using GuruFocus verified components.

        Owner Earnings = Net Income + D&A - CapEx - Change in Working Capital

        NOTE: Calculator tool is NOT used because it's LLM-generated and may contain
        extraction/calculation errors. Only verified sources (GuruFocus) are trusted.

        This calculation uses verified GuruFocus data as inputs, so while it involves
        arithmetic, it's much more reliable than LLM-generated calculator results.
        """
        # Find GuruFocus financials in cache
        gf_financials = None
        for key, value in tool_cache.items():
            if 'gurufocus' in str(key).lower() and 'financials' in str(key).lower():
                gf_financials = value
                break

        if not gf_financials:
            logger.debug("[AUTO-CORRECT] No GuruFocus financials available for Owner Earnings")
            return None

        data = gf_financials.get('data', {})
        financials = data.get('financials', {})

        # Extract Owner Earnings components from GuruFocus (verified data)
        # All values should be arrays with most recent value at index -1
        net_income_arr = financials.get('net_income')
        da_arr = financials.get('depreciation_amortization')
        capex_arr = financials.get('capex')

        # Working capital change might not always be available
        # If not available, we'll use the simpler formula: NI + D&A - CapEx
        working_capital_change_arr = financials.get('working_capital_change')

        # Verify we have the essential components
        if not all([net_income_arr, da_arr, capex_arr]):
            logger.debug("[AUTO-CORRECT] Missing essential components for Owner Earnings calculation")

            # Fallback: Try to use FCF if available
            fcf = financials.get('free_cash_flow')
            if fcf and isinstance(fcf, list) and len(fcf) > 0:
                latest_fcf = fcf[-1]
                old_value = analysis.get('owner_earnings', 'unknown')
                analysis['owner_earnings'] = latest_fcf

                return {
                    'field': 'owner_earnings',
                    'old_value': str(old_value),
                    'new_value': f"${latest_fcf/1000:.1f}B",
                    'source': 'GuruFocus FCF (verified)',
                    'description': f"Corrected Owner Earnings using verified GuruFocus FCF (components unavailable)"
                }

            return None

        # Extract most recent values
        try:
            # Handle both list and non-list formats
            net_income = net_income_arr[-1] if isinstance(net_income_arr, list) else net_income_arr
            da = da_arr[-1] if isinstance(da_arr, list) else da_arr
            capex = capex_arr[-1] if isinstance(capex_arr, list) else capex_arr

            # CapEx is usually negative in financials, make it positive for subtraction
            if capex < 0:
                capex = abs(capex)

            # Calculate Owner Earnings using verified GuruFocus components
            if working_capital_change_arr and isinstance(working_capital_change_arr, list) and len(working_capital_change_arr) > 0:
                wc_change = working_capital_change_arr[-1]
                owner_earnings = net_income + da - capex - wc_change
                formula_used = "Net Income + D&A - CapEx - Change in WC"
            else:
                # Simplified formula (working capital not available)
                owner_earnings = net_income + da - capex
                formula_used = "Net Income + D&A - CapEx"
                logger.debug("[AUTO-CORRECT] Working capital change not available, using simplified formula")

            # Update analysis
            old_value = analysis.get('owner_earnings', 'unknown')
            analysis['owner_earnings'] = owner_earnings

            return {
                'field': 'owner_earnings',
                'old_value': str(old_value),
                'new_value': f"${owner_earnings/1000:.1f}B",
                'source': 'GuruFocus (calculated from verified components)',
                'description': f"Corrected Owner Earnings using {formula_used} with GuruFocus verified data"
            }

        except (TypeError, IndexError, KeyError) as e:
            logger.debug(f"[AUTO-CORRECT] Error calculating Owner Earnings from components: {e}")
            return None

    def _correct_revenue(
        self,
        analysis: Dict[str, Any],
        tool_cache: Dict[str, Any],
        issue_description: str
    ) -> Optional[Dict[str, str]]:
        """Correct revenue using cached GuruFocus data."""
        gf_financials = None
        for key, value in tool_cache.items():
            if 'gurufocus' in str(key).lower() and 'financials' in str(key).lower():
                gf_financials = value
                break

        if not gf_financials:
            return None

        data = gf_financials.get('data', {})
        financials = data.get('financials', {})
        revenue = financials.get('revenue')

        if revenue and isinstance(revenue, list) and len(revenue) > 0:
            latest_revenue = revenue[-1]
            old_value = analysis.get('revenue', 'unknown')
            analysis['revenue'] = latest_revenue

            return {
                'field': 'revenue',
                'old_value': str(old_value),
                'new_value': f"${latest_revenue/1000:.1f}B",
                'source': 'GuruFocus (cached)',
                'description': f"Corrected revenue using cached GuruFocus data"
            }

        return None

    def _correct_margin(
        self,
        analysis: Dict[str, Any],
        tool_cache: Dict[str, Any],
        issue_description: str,
        margin_type: str
    ) -> Optional[Dict[str, str]]:
        """Correct margin using cached GuruFocus data."""
        gf_keyratios = None
        for key, value in tool_cache.items():
            if 'gurufocus' in str(key).lower() and 'keyratios' in str(key).lower():
                gf_keyratios = value
                break

        if not gf_keyratios:
            return None

        data = gf_keyratios.get('data', {})
        metrics = data.get('metrics', {})
        cached_margin = metrics.get(margin_type)

        if cached_margin is not None:
            old_value = analysis.get(margin_type, 'unknown')
            analysis[margin_type] = cached_margin

            return {
                'field': margin_type,
                'old_value': str(old_value),
                'new_value': f"{cached_margin:.1%}" if isinstance(cached_margin, float) else str(cached_margin),
                'source': 'GuruFocus (cached)',
                'description': f"Corrected {margin_type.replace('_', ' ')} using cached GuruFocus data"
            }

        return None

    def _correct_debt(
        self,
        analysis: Dict[str, Any],
        tool_cache: Dict[str, Any],
        issue_description: str
    ) -> Optional[Dict[str, str]]:
        """Correct debt/equity using cached GuruFocus data."""
        gf_keyratios = None
        for key, value in tool_cache.items():
            if 'gurufocus' in str(key).lower() and 'keyratios' in str(key).lower():
                gf_keyratios = value
                break

        if not gf_keyratios:
            return None

        data = gf_keyratios.get('data', {})
        metrics = data.get('metrics', {})
        cached_de = metrics.get('debt_equity')

        if cached_de is not None:
            old_value = analysis.get('debt_equity', 'unknown')
            analysis['debt_equity'] = cached_de

            return {
                'field': 'debt_equity',
                'old_value': str(old_value),
                'new_value': f"{cached_de:.2f}" if isinstance(cached_de, float) else str(cached_de),
                'source': 'GuruFocus (cached)',
                'description': f"Corrected debt/equity ratio using cached GuruFocus data"
            }

        return None


def apply_cached_corrections(
    analysis: Dict[str, Any],
    validator_issues: List[Dict[str, Any]],
    tool_cache: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function to apply auto-corrections.

    Args:
        analysis: Analysis to correct
        validator_issues: Issues from validator
        tool_cache: Cached tool results

    Returns:
        Corrected analysis
    """
    corrector = ValidatorCorrections()
    return corrector.auto_correct_analysis(analysis, validator_issues, tool_cache)
