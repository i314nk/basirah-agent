"""
Financial Calculator Tool

Module: src.tools.calculator_tool
Purpose: Pure computation tool for financial calculations (Owner Earnings, ROIC, DCF, Margin of Safety, Sharia Compliance)
Status: Complete - Sprint 3, Phase 1
Created: 2025-10-29

This tool implements Warren Buffett's quantitative investment criteria and AAOIFI Sharia compliance standards.
All calculations are based on formulas from:
- Buffett's 1986 Berkshire Hathaway Shareholder Letter (Owner Earnings)
- BUFFETT_PRINCIPLES.md (Sections 4, 5, 6)
- calculator_tool_spec.md (Complete specification)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from src.tools.base import Tool


class CalculatorTool(Tool):
    """
    Financial calculator implementing Buffett metrics and Sharia compliance.

    Provides 5 core calculations:
    1. Owner Earnings - True economic cash flow (Buffett, 1986)
    2. ROIC - Return on Invested Capital (capital efficiency)
    3. DCF - Discounted Cash Flow valuation (intrinsic value)
    4. Margin of Safety - Undervaluation percentage
    5. Sharia Compliance - AAOIFI standards checking

    All calculations are deterministic (no external APIs), transparent (step-by-step breakdown),
    and reference-based (formulas from authoritative sources).
    """

    # Sharia compliance: prohibited business activities per AAOIFI standards
    PROHIBITED_ACTIVITIES = [
        "alcohol_production",
        "gambling",
        "pork_products",
        "conventional_banking",
        "conventional_insurance",
        "adult_entertainment",
        "tobacco",
        "weapons_munitions"
    ]

    # ROIC thresholds from BUFFETT_PRINCIPLES.md Section 5
    ROIC_WORLD_CLASS = 0.25  # 25%+
    ROIC_EXCELLENT = 0.20    # 20-25%
    ROIC_GOOD = 0.15         # 15-20%
    ROIC_THRESHOLD = 0.12    # 12%+ acceptable

    # Margin of Safety thresholds from BUFFETT_PRINCIPLES.md Section 6
    MARGIN_EXCELLENT = 0.40   # 40%+
    MARGIN_GOOD = 0.25        # 25-40%
    MARGIN_ACCEPTABLE = 0.15  # 15-25%

    # Sharia compliance thresholds from calculator_tool_spec.md
    SHARIA_DEBT_THRESHOLD = 0.33        # Debt/Assets < 33%
    SHARIA_LIQUID_THRESHOLD = 0.33      # Liquid/Market Cap < 33%
    SHARIA_RECEIVABLES_THRESHOLD = 0.50 # Receivables/Market Cap < 50%

    def __init__(self):
        """Initialize Calculator Tool"""
        pass

    @property
    def name(self) -> str:
        """Tool name for agent to reference"""
        return "calculator_tool"

    @property
    def description(self) -> str:
        """What this tool does (for agent decision-making)"""
        return (
            "Performs financial calculations for investment analysis: "
            "Owner Earnings (Buffett's cash flow metric), "
            "ROIC (return on invested capital), "
            "DCF (discounted cash flow valuation), "
            "Margin of Safety (undervaluation %), "
            "Sharia Compliance (AAOIFI standards check). "
            "IMPORTANT: For sharia_compliance_check, you MUST gather ALL required fields first: "
            "total_debt, total_assets, cash_and_liquid_assets, market_cap, accounts_receivable, business_activities. "
            "Tool will reject requests with missing fields."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        """JSON schema for tool parameters"""
        return {
            "type": "object",
            "properties": {
                "calculation": {
                    "type": "string",
                    "enum": [
                        "owner_earnings",
                        "roic",
                        "dcf",
                        "margin_of_safety",
                        "sharia_compliance_check"
                    ],
                    "description": "Type of calculation to perform"
                },
                "data": {
                    "type": "object",
                    "description": "Input data for calculation (schema varies by type)"
                }
            },
            "required": ["calculation", "data"]
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute financial calculation.

        Args:
            calculation: Type of calculation (owner_earnings, roic, dcf, margin_of_safety, sharia_compliance_check)
            data: Input data dictionary (schema depends on calculation type)

        Returns:
            Dict containing:
                - success: bool (whether calculation succeeded)
                - data: dict with result, breakdown, interpretation, warnings, metadata
                - error: str or None
        """
        calculation = kwargs.get("calculation")
        data = kwargs.get("data")

        # Validate required parameters
        if not calculation:
            return self._error("Missing required parameter: 'calculation'")
        if data is None:
            return self._error("Missing required parameter: 'data'")

        # Route to specific calculation
        calculators = {
            "owner_earnings": self._calculate_owner_earnings,
            "roic": self._calculate_roic,
            "dcf": self._calculate_dcf,
            "margin_of_safety": self._calculate_margin_of_safety,
            "sharia_compliance_check": self._check_sharia_compliance
        }

        if calculation not in calculators:
            valid = ", ".join(calculators.keys())
            return self._error(
                f"Unknown calculation: '{calculation}'. Must be one of: {valid}"
            )

        # Execute calculation with error handling
        try:
            return calculators[calculation](data)
        except KeyError as e:
            return self._error(f"Missing required field: {str(e)}")
        except ValueError as e:
            return self._error(f"Validation error: {str(e)}")
        except ZeroDivisionError as e:
            return self._error(f"Division by zero: {str(e)}")
        except Exception as e:
            return self._error(f"Calculation error: {str(e)}")

    # =====================================================================
    # CALCULATION 1: OWNER EARNINGS
    # =====================================================================

    def _calculate_owner_earnings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Owner Earnings per Buffett's 1986 formula.

        Formula: OE = Net Income + D&A - CapEx - ΔWorking Capital

        Reference:
            Warren Buffett, 1986 Berkshire Hathaway Shareholder Letter
            BUFFETT_PRINCIPLES.md Section 4

        Args:
            data: Dict with keys:
                - net_income: Net income from operations
                - depreciation_amortization: D&A expense (non-cash)
                - capex: Capital expenditures
                - working_capital_change: Change in working capital (positive = increase)

        Returns:
            Standard response with result, breakdown, interpretation
        """
        # Extract and validate inputs
        net_income = data["net_income"]
        da = data["depreciation_amortization"]
        capex = data["capex"]
        wc_change = data["working_capital_change"]

        # Validate: CapEx must be positive (it's an outflow)
        if capex < 0:
            raise ValueError("capex must be non-negative (it's a cash outflow)")

        # Calculate Owner Earnings
        # OE = NI + D&A - CapEx - ΔWC
        owner_earnings = net_income + da - capex - wc_change

        # Build step-by-step breakdown
        breakdown = {
            "step1": f"Net Income: {self._format_currency(net_income)}",
            "step2": f"Add D&A (non-cash): {self._format_currency(da)}",
            "step3": f"Subtotal: {self._format_currency(net_income + da)}",
            "step4": f"Subtract CapEx: {self._format_currency(capex)}",
            "step5": f"Subtract ΔWorking Capital: {self._format_currency(wc_change)}",
            "final": f"Owner Earnings: {self._format_currency(owner_earnings)}"
        }

        # Generate interpretation
        interpretation = self._interpret_owner_earnings(owner_earnings, net_income, capex, da)

        # Check for warnings
        warnings = self._check_owner_earnings_warnings(owner_earnings, capex, da, net_income)

        return {
            "success": True,
            "data": {
                "calculation": "owner_earnings",
                "result": owner_earnings,
                "result_formatted": self._format_currency(owner_earnings),
                "inputs": data,
                "breakdown": breakdown,
                "interpretation": interpretation,
                "warnings": warnings,
                "metadata": {
                    "formula": "OE = Net Income + D&A - CapEx - ΔWorking Capital",
                    "reference": "Buffett, 1986 Berkshire Hathaway Shareholder Letter",
                    "timestamp": datetime.now().isoformat()
                }
            },
            "error": None
        }

    # =====================================================================
    # CALCULATION 2: ROIC (Return on Invested Capital)
    # =====================================================================

    def _calculate_roic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Return on Invested Capital.

        Formula:
            Invested Capital = Total Assets - Current Liabilities - Cash
            ROIC = Operating Income / Invested Capital

        Reference:
            BUFFETT_PRINCIPLES.md Section 5
            calculator_tool_spec.md Section 2

        Args:
            data: Dict with keys:
                - operating_income: Operating income (or NOPAT)
                - total_assets: Total assets
                - current_liabilities: Current liabilities
                - cash_equivalents: Cash and cash equivalents

        Returns:
            Standard response with ROIC as decimal (e.g., 0.18 = 18%)
        """
        # Extract inputs
        operating_income = data["operating_income"]
        total_assets = data["total_assets"]
        current_liabilities = data["current_liabilities"]
        cash = data["cash_equivalents"]

        # Validate positive values where required
        if total_assets < 0:
            raise ValueError("total_assets cannot be negative")
        if current_liabilities < 0:
            raise ValueError("current_liabilities cannot be negative")
        if cash < 0:
            raise ValueError("cash_equivalents cannot be negative")

        # Calculate invested capital
        invested_capital = total_assets - current_liabilities - cash

        # Check for zero or negative invested capital
        if invested_capital <= 0:
            raise ValueError(
                f"Cannot calculate ROIC: invested capital is {invested_capital:,.0f} "
                f"(Total Assets {total_assets:,.0f} - Current Liabilities {current_liabilities:,.0f} "
                f"- Cash {cash:,.0f}). This suggests balance sheet issues."
            )

        # Calculate ROIC
        roic = operating_income / invested_capital

        # Build breakdown
        breakdown = {
            "invested_capital_calc": "Total Assets - Current Liabilities - Cash",
            "invested_capital_numbers": (
                f"{self._format_currency(total_assets)} - "
                f"{self._format_currency(current_liabilities)} - "
                f"{self._format_currency(cash)}"
            ),
            "invested_capital": invested_capital,
            "invested_capital_formatted": self._format_currency(invested_capital),
            "roic_calc": "Operating Income / Invested Capital",
            "roic_numbers": (
                f"{self._format_currency(operating_income)} / "
                f"{self._format_currency(invested_capital)}"
            ),
            "roic": roic,
            "roic_formatted": self._format_percentage(roic)
        }

        # Interpretation
        interpretation = self._interpret_roic(roic)

        return {
            "success": True,
            "data": {
                "calculation": "roic",
                "result": roic,
                "result_formatted": self._format_percentage(roic),
                "inputs": data,
                "breakdown": breakdown,
                "interpretation": interpretation,
                "warnings": [],
                "metadata": {
                    "formula": "ROIC = Operating Income / (Total Assets - Current Liabilities - Cash)",
                    "reference": "BUFFETT_PRINCIPLES.md Section 5 - ROIC thresholds",
                    "timestamp": datetime.now().isoformat()
                }
            },
            "error": None
        }

    # =====================================================================
    # CALCULATION 3: DCF (Discounted Cash Flow)
    # =====================================================================

    def _calculate_dcf(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Discounted Cash Flow valuation.

        Formula:
            DCF Value = Σ[OE × (1+g)^t / (1+r)^t] for t=1 to years
            Terminal Value = OE(year N) × (1+tg) / (r - tg) / (1+r)^years
            Intrinsic Value = DCF Value + Terminal Value

        Reference:
            BUFFETT_PRINCIPLES.md Section 6
            calculator_tool_spec.md Section 2.3

        Args:
            data: Dict with keys:
                - owner_earnings: Current or average owner earnings
                - growth_rate: Conservative growth rate (decimal, e.g., 0.05 = 5%)
                - discount_rate: Required return rate (decimal, e.g., 0.10 = 10%)
                - terminal_growth: Terminal growth rate (decimal, e.g., 0.03 = 3%)
                - years: Projection period (default: 10)

        Returns:
            Standard response with intrinsic value
        """
        # Extract inputs
        oe = data["owner_earnings"]
        g = data["growth_rate"]
        r = data["discount_rate"]
        tg = data["terminal_growth"]
        years = data.get("years", 10)

        # Validate ranges
        if g < -0.5 or g > 0.5:
            raise ValueError(f"growth_rate must be between -50% and 50%, got {g*100:.1f}%")
        if r < 0.01 or r > 0.30:
            raise ValueError(f"discount_rate must be between 1% and 30%, got {r*100:.1f}%")
        if tg < 0 or tg > 0.10:
            raise ValueError(f"terminal_growth must be between 0% and 10%, got {tg*100:.1f}%")
        if years < 5 or years > 20:
            raise ValueError(f"years must be between 5 and 20, got {years}")

        # Critical validation: terminal growth must be less than discount rate
        if tg >= r:
            raise ValueError(
                f"Terminal growth ({tg*100:.1f}%) cannot equal or exceed "
                f"discount rate ({r*100:.1f}%). This violates perpetuity formula."
            )

        # Collect warnings
        warnings = []
        if g > 0.20:
            warnings.append(
                f"Growth rate of {g*100:.1f}% is very aggressive. "
                f"Buffett typically uses 5-10% for conservative estimates."
            )
        if r < 0.08:
            warnings.append(
                f"Discount rate of {r*100:.1f}% is low. Buffett uses 10-12% "
                f"to ensure adequate margin of safety."
            )
        if tg > 0.04:
            warnings.append(
                f"Terminal growth of {tg*100:.1f}% exceeds long-term GDP growth (~3%). "
                f"Consider more conservative perpetuity assumption."
            )

        # Calculate DCF value (present value of explicit forecast period)
        dcf_value = 0
        for t in range(1, years + 1):
            cash_flow = oe * ((1 + g) ** t)
            present_value = cash_flow / ((1 + r) ** t)
            dcf_value += present_value

        # Calculate terminal value
        # Terminal CF = OE(year N) × (1 + terminal growth)
        # Terminal Value = Terminal CF / (r - tg)
        # PV of Terminal Value = Terminal Value / (1 + r)^years
        terminal_cash_flow = oe * ((1 + g) ** years) * (1 + tg)
        terminal_value = terminal_cash_flow / (r - tg)
        terminal_value_present = terminal_value / ((1 + r) ** years)

        # Total intrinsic value
        intrinsic_value = dcf_value + terminal_value_present

        # Build breakdown
        breakdown = {
            "dcf_period_value": self._format_currency(dcf_value),
            "dcf_period_description": f"Present value of years 1-{years} cash flows",
            "terminal_value_nominal": self._format_currency(terminal_value),
            "terminal_value_present": self._format_currency(terminal_value_present),
            "terminal_value_description": f"Present value of perpetuity beyond year {years}",
            "intrinsic_value": self._format_currency(intrinsic_value),
            "note": "Divide by shares outstanding for per-share intrinsic value"
        }

        # Interpretation
        interpretation = (
            f"Conservative DCF valuation yielding {self._format_currency(intrinsic_value)} "
            f"intrinsic value. Based on {g*100:.1f}% growth for {years} years, "
            f"{r*100:.1f}% discount rate, and {tg*100:.1f}% terminal growth. "
            f"Terminal value represents {terminal_value_present/intrinsic_value*100:.1f}% of total."
        )

        return {
            "success": True,
            "data": {
                "calculation": "dcf",
                "result": intrinsic_value,
                "result_formatted": self._format_currency(intrinsic_value),
                "inputs": data,
                "breakdown": breakdown,
                "interpretation": interpretation,
                "warnings": warnings,
                "metadata": {
                    "formula": "DCF = Σ[CF/(1+r)^t] + Terminal Value",
                    "reference": "BUFFETT_PRINCIPLES.md Section 6 - DCF Methodology",
                    "timestamp": datetime.now().isoformat()
                }
            },
            "error": None
        }

    # =====================================================================
    # CALCULATION 4: MARGIN OF SAFETY
    # =====================================================================

    def _calculate_margin_of_safety(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Margin of Safety.

        Formula: MoS = (Intrinsic Value - Current Price) / Intrinsic Value

        Reference:
            Benjamin Graham & Warren Buffett
            BUFFETT_PRINCIPLES.md Section 6

        Args:
            data: Dict with keys:
                - intrinsic_value: Calculated intrinsic value per share
                - current_price: Current market price per share

        Returns:
            Standard response with margin as decimal (e.g., 0.28 = 28%)
        """
        # Extract inputs
        intrinsic_value = data["intrinsic_value"]
        current_price = data["current_price"]

        # Validate positive values
        if intrinsic_value <= 0:
            raise ValueError("intrinsic_value must be positive")
        if current_price <= 0:
            raise ValueError("current_price must be positive")

        # Calculate margin of safety
        margin = (intrinsic_value - current_price) / intrinsic_value

        # Build breakdown
        difference = intrinsic_value - current_price
        breakdown = {
            "intrinsic_value": self._format_currency(intrinsic_value),
            "current_price": self._format_currency(current_price),
            "difference": self._format_currency(difference),
            "calculation": (
                f"({self._format_currency(intrinsic_value)} - "
                f"{self._format_currency(current_price)}) / "
                f"{self._format_currency(intrinsic_value)}"
            ),
            "result": f"{margin:.4f} = {margin*100:.1f}%"
        }

        # Interpretation
        interpretation = self._interpret_margin(margin)

        return {
            "success": True,
            "data": {
                "calculation": "margin_of_safety",
                "result": margin,
                "result_formatted": self._format_percentage(margin),
                "inputs": data,
                "breakdown": breakdown,
                "interpretation": interpretation,
                "warnings": [],
                "metadata": {
                    "formula": "MoS = (Intrinsic Value - Price) / Intrinsic Value",
                    "reference": "Benjamin Graham & Warren Buffett",
                    "timestamp": datetime.now().isoformat()
                }
            },
            "error": None
        }

    # =====================================================================
    # CALCULATION 5: SHARIA COMPLIANCE CHECK
    # =====================================================================

    def _check_sharia_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check Sharia compliance per AAOIFI standards.

        Screening Criteria:
        1. Debt/Assets < 33%
        2. Liquid Assets/Market Cap < 33%
        3. Receivables/Market Cap < 50%
        4. No prohibited business activities

        Reference:
            AAOIFI Sharia Standards
            calculator_tool_spec.md Section 2.5
            BUFFETT_PRINCIPLES.md Section 12

        Args:
            data: Dict with keys:
                - total_debt: Total interest-bearing debt
                - total_assets: Total assets
                - cash_and_liquid_assets: Cash + marketable securities + receivables
                - market_cap: Current market capitalization
                - accounts_receivable: Accounts receivable
                - business_activities: List of business activity codes

        Returns:
            Standard response with 1 (compliant) or 0 (non-compliant)
        """
        # Extract inputs
        total_debt = data["total_debt"]
        total_assets = data["total_assets"]
        liquid_assets = data["cash_and_liquid_assets"]
        market_cap = data["market_cap"]
        receivables = data["accounts_receivable"]
        activities = data["business_activities"]

        # Validate non-negative values
        if total_debt < 0:
            raise ValueError("total_debt cannot be negative")
        if total_assets <= 0:
            raise ValueError("total_assets must be positive")
        if liquid_assets < 0:
            raise ValueError("cash_and_liquid_assets cannot be negative")
        if market_cap <= 0:
            raise ValueError("market_cap must be positive")
        if receivables < 0:
            raise ValueError("accounts_receivable cannot be negative")

        # Calculate ratios
        debt_to_assets = total_debt / total_assets
        liquid_to_market = liquid_assets / market_cap
        receivables_to_market = receivables / market_cap

        # Check against thresholds
        debt_pass = debt_to_assets < self.SHARIA_DEBT_THRESHOLD
        liquid_pass = liquid_to_market < self.SHARIA_LIQUID_THRESHOLD
        receivables_pass = receivables_to_market < self.SHARIA_RECEIVABLES_THRESHOLD

        # Check business activities
        prohibited_found = [act for act in activities if act in self.PROHIBITED_ACTIVITIES]
        business_pass = len(prohibited_found) == 0

        # Overall compliance
        all_pass = debt_pass and liquid_pass and receivables_pass and business_pass

        # Build detailed breakdown
        breakdown = {
            "debt_to_assets": {
                "value": debt_to_assets,
                "formatted": self._format_percentage(debt_to_assets),
                "threshold": f"{self.SHARIA_DEBT_THRESHOLD*100:.0f}%",
                "status": "PASS" if debt_pass else "FAIL",
                "description": "Total Debt / Total Assets"
            },
            "liquid_to_market_cap": {
                "value": liquid_to_market,
                "formatted": self._format_percentage(liquid_to_market),
                "threshold": f"{self.SHARIA_LIQUID_THRESHOLD*100:.0f}%",
                "status": "PASS" if liquid_pass else "FAIL",
                "description": "(Cash + Liquid Assets) / Market Cap"
            },
            "receivables_to_market_cap": {
                "value": receivables_to_market,
                "formatted": self._format_percentage(receivables_to_market),
                "threshold": f"{self.SHARIA_RECEIVABLES_THRESHOLD*100:.0f}%",
                "status": "PASS" if receivables_pass else "FAIL",
                "description": "Accounts Receivable / Market Cap"
            },
            "business_screening": {
                "activities_checked": activities,
                "prohibited_found": prohibited_found,
                "status": "PASS" if business_pass else "FAIL",
                "description": "Screening for prohibited business activities"
            }
        }

        # Interpretation
        interpretation = self._interpret_sharia_compliance(
            all_pass, debt_pass, liquid_pass, receivables_pass, business_pass, prohibited_found
        )

        return {
            "success": True,
            "data": {
                "calculation": "sharia_compliance_check",
                "result": 1 if all_pass else 0,
                "result_formatted": "COMPLIANT" if all_pass else "NON-COMPLIANT",
                "inputs": data,
                "breakdown": breakdown,
                "interpretation": interpretation,
                "warnings": [],
                "metadata": {
                    "formula": "AAOIFI Screening Standards",
                    "reference": "Accounting and Auditing Organization for Islamic Financial Institutions",
                    "timestamp": datetime.now().isoformat()
                }
            },
            "error": None
        }

    # =====================================================================
    # HELPER METHODS: FORMATTING
    # =====================================================================

    def _format_currency(self, value: float) -> str:
        """
        Format value as currency with B/M/K suffixes.

        Args:
            value: Numeric value

        Returns:
            Formatted string (e.g., "$1.25B", "$90.5M", "$15.3K", "$150.00")
        """
        abs_value = abs(value)
        sign = "-" if value < 0 else ""

        if abs_value >= 1_000_000_000:
            return f"{sign}${abs_value/1_000_000_000:.2f}B"
        elif abs_value >= 1_000_000:
            return f"{sign}${abs_value/1_000_000:.2f}M"
        elif abs_value >= 1_000:
            return f"{sign}${abs_value/1_000:.2f}K"
        else:
            return f"{sign}${abs_value:.2f}"

    def _format_percentage(self, value: float) -> str:
        """
        Format decimal as percentage.

        Args:
            value: Decimal value (e.g., 0.18)

        Returns:
            Formatted string (e.g., "18.0%")
        """
        return f"{value * 100:.1f}%"

    # =====================================================================
    # HELPER METHODS: ERROR HANDLING
    # =====================================================================

    def _error(self, message: str) -> Dict[str, Any]:
        """
        Return standardized error response.

        Args:
            message: Error message

        Returns:
            Dict with success=False and error message
        """
        return {
            "success": False,
            "data": None,
            "error": message
        }

    # =====================================================================
    # HELPER METHODS: INTERPRETATION
    # =====================================================================

    def _interpret_owner_earnings(self, oe: float, net_income: float,
                                   capex: float, da: float) -> str:
        """
        Interpret Owner Earnings result based on Buffett criteria.

        Reference: BUFFETT_PRINCIPLES.md Section 4 (Quality Thresholds)
        """
        oe_to_ni_ratio = oe / net_income if net_income != 0 else 0

        if oe < 0:
            return (
                "CONCERNING: Negative Owner Earnings indicates company is consuming cash "
                "rather than generating it. Major red flag per Buffett criteria."
            )
        elif oe < net_income * 0.50:
            return (
                f"CONCERNING: Owner Earnings ({self._format_currency(oe)}) is only "
                f"{oe_to_ni_ratio*100:.0f}% of Net Income. High capital intensity suggests "
                "company must reinvest heavily just to maintain position."
            )
        elif oe > net_income * 1.20:
            return (
                f"UNUSUAL: Owner Earnings ({self._format_currency(oe)}) exceeds Net Income by "
                f"{(oe_to_ni_ratio-1)*100:.0f}%. Verify working capital calculation - this pattern "
                "is uncommon and may indicate declining working capital needs."
            )
        else:
            capex_to_da = capex / da if da > 0 else 0
            if capex <= da:
                quality = "EXCELLENT (asset-light business model)"
            elif capex <= da * 1.5:
                quality = "GOOD (moderate capital needs)"
            else:
                quality = "ACCEPTABLE (capital-intensive)"

            return (
                f"Company generated {self._format_currency(oe)} in true owner earnings "
                f"({oe_to_ni_ratio*100:.0f}% of Net Income). Quality: {quality}. "
                f"CapEx is {capex_to_da*100:.0f}% of D&A."
            )

    def _check_owner_earnings_warnings(self, oe: float, capex: float,
                                       da: float, net_income: float) -> List[str]:
        """
        Check for Owner Earnings warning signs.

        Reference: BUFFETT_PRINCIPLES.md Section 4 (Red Flags)
        """
        warnings = []

        if oe < 0:
            warnings.append(
                "Negative Owner Earnings - company is not generating free cash flow. "
                "Cannot sustain operations without external capital."
            )

        if capex > da * 2:
            warnings.append(
                f"CapEx ({self._format_currency(capex)}) is {capex/da:.1f}x D&A "
                f"({self._format_currency(da)}), suggesting significant growth capex "
                "or asset expansion. Verify if sustainable."
            )

        if oe < net_income * 0.70 and oe >= 0:
            warnings.append(
                f"Owner Earnings is only {oe/net_income*100:.0f}% of Net Income. "
                "High capital requirements reduce cash available to owners."
            )

        return warnings

    def _interpret_roic(self, roic: float) -> str:
        """
        Interpret ROIC result based on Buffett thresholds.

        Reference: BUFFETT_PRINCIPLES.md Section 5 (ROIC Thresholds)
        """
        if roic >= self.ROIC_WORLD_CLASS:
            return (
                f"ROIC of {self._format_percentage(roic)} is WORLD-CLASS. "
                f"Far exceeds Buffett's 15% threshold. Indicates strong moat and "
                "exceptional capital efficiency. Quality score: 100/100."
            )
        elif roic >= self.ROIC_EXCELLENT:
            return (
                f"ROIC of {self._format_percentage(roic)} is EXCELLENT. "
                f"Well above Buffett's 15% threshold. Demonstrates strong competitive "
                "advantages and efficient capital deployment. Quality score: 85/100."
            )
        elif roic >= self.ROIC_GOOD:
            return (
                f"ROIC of {self._format_percentage(roic)} is GOOD. "
                f"Meets Buffett's 15% threshold. Indicates solid business quality "
                "with adequate returns on invested capital. Quality score: 70/100."
            )
        elif roic >= self.ROIC_THRESHOLD:
            return (
                f"ROIC of {self._format_percentage(roic)} is ACCEPTABLE for narrow moat companies. "
                f"Below Buffett's preferred 15% but above minimum 12%. Proceed with caution. "
                "Quality score: 50/100."
            )
        else:
            return (
                f"ROIC of {self._format_percentage(roic)} is BELOW threshold. "
                f"Poor capital efficiency - returns below 12% indicate weak competitive position "
                "or commoditized business. Quality score: 25/100. AVOID per Buffett criteria."
            )

    def _interpret_margin(self, margin: float) -> str:
        """
        Interpret Margin of Safety based on Buffett criteria.

        Reference: BUFFETT_PRINCIPLES.md Section 6 (Margin of Safety)
        """
        if margin >= self.MARGIN_EXCELLENT:
            return (
                f"{self._format_percentage(margin)} margin is EXCELLENT. "
                f"Wide margin of safety provides strong downside protection. "
                "Buffett's minimum is 30%, this exceeds it significantly. STRONG BUY signal."
            )
        elif margin >= self.MARGIN_GOOD:
            return (
                f"{self._format_percentage(margin)} margin is GOOD. "
                f"Meets Buffett's preferred 20-40% range for quality companies with wide moats. "
                "Adequate protection against valuation errors. BUY signal."
            )
        elif margin >= self.MARGIN_ACCEPTABLE:
            return (
                f"{self._format_percentage(margin)} margin is ACCEPTABLE for exceptional companies only. "
                f"Below Buffett's typical 30% threshold but acceptable for highest-quality businesses "
                "with fortress balance sheets and wide moats. Conditional BUY."
            )
        elif margin > 0:
            return (
                f"{self._format_percentage(margin)} margin is INSUFFICIENT. "
                f"Below Buffett's 15% minimum. Not enough safety cushion against "
                "valuation errors or adverse events. WATCH or AVOID."
            )
        else:
            overvalued_by = abs(margin)
            return (
                f"NEGATIVE margin - stock is OVERVALUED by {self._format_percentage(overvalued_by)}. "
                f"Current price exceeds intrinsic value. Clear AVOID signal per Buffett criteria."
            )

    def _interpret_sharia_compliance(self, all_pass: bool, debt: bool, liquid: bool,
                                     receivables: bool, business: bool,
                                     prohibited: List[str]) -> str:
        """
        Interpret Sharia compliance result.

        Reference: AAOIFI Standards, calculator_tool_spec.md Section 2.5
        """
        if all_pass:
            return (
                "Company is Sharia COMPLIANT. All financial ratios within AAOIFI thresholds "
                "(Debt/Assets <33%, Liquid/Market Cap <33%, Receivables/Market Cap <50%) "
                "and no prohibited business activities detected."
            )

        # Build failure message
        failures = []
        if not debt:
            failures.append("Debt/Assets ratio exceeds 33% threshold")
        if not liquid:
            failures.append("Liquid Assets/Market Cap exceeds 33% threshold")
        if not receivables:
            failures.append("Receivables/Market Cap exceeds 50% threshold")
        if not business:
            failures.append(f"Prohibited activities found: {', '.join(prohibited)}")

        return (
            f"Company is Sharia NON-COMPLIANT per AAOIFI standards. "
            f"Failures: {'; '.join(failures)}. "
            "Investment NOT permissible under Sharia law."
        )


# Make tool available for import
__all__ = ["CalculatorTool"]
