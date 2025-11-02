"""
Calculator Tool Tests

Module: tests.test_tools.test_calculator
Purpose: Comprehensive test suite for Calculator Tool
Status: Complete - Sprint 3, Phase 1
Created: 2025-10-29

Tests cover:
- All 5 calculation types
- Valid inputs (all scenarios)
- Missing required fields
- Invalid values
- Edge cases
- Real company data (Coca-Cola, Apple)
"""

import pytest
from src.tools.calculator_tool import CalculatorTool


class TestCalculatorToolInterface:
    """Test Calculator Tool conforms to Tool interface"""

    def test_name(self):
        """Test tool name property"""
        tool = CalculatorTool()
        assert tool.name == "calculator_tool"

    def test_description(self):
        """Test tool description property"""
        tool = CalculatorTool()
        assert "Owner Earnings" in tool.description
        assert "ROIC" in tool.description
        assert "DCF" in tool.description
        assert "Margin of Safety" in tool.description
        assert "Sharia Compliance" in tool.description

    def test_parameters(self):
        """Test tool parameters schema"""
        tool = CalculatorTool()
        params = tool.parameters
        assert params["type"] == "object"
        assert "calculation" in params["properties"]
        assert "data" in params["properties"]


class TestOwnerEarnings:
    """Test Owner Earnings calculation"""

    def test_basic_calculation(self):
        """Test basic Owner Earnings calculation"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="owner_earnings",
            data={
                "net_income": 100_000_000,
                "depreciation_amortization": 10_000_000,
                "capex": 15_000_000,
                "working_capital_change": 5_000_000
            }
        )

        assert result["success"] is True
        assert result["data"]["result"] == 90_000_000
        assert result["data"]["result_formatted"] == "$90.00M"
        assert "breakdown" in result["data"]
        assert result["error"] is None

    def test_negative_working_capital_change(self):
        """Test with negative working capital change (releasing cash)"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="owner_earnings",
            data={
                "net_income": 100_000_000,
                "depreciation_amortization": 10_000_000,
                "capex": 15_000_000,
                "working_capital_change": -5_000_000  # WC decreased, adds to OE
            }
        )

        assert result["success"] is True
        # OE = 100M + 10M - 15M - (-5M) = 100M
        assert result["data"]["result"] == 100_000_000

    def test_apple_realistic_data(self):
        """Test with Apple Inc. approximate data (FY2022)"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="owner_earnings",
            data={
                "net_income": 99_800_000_000,  # ~$99.8B
                "depreciation_amortization": 11_100_000_000,  # ~$11.1B
                "capex": 10_700_000_000,  # ~$10.7B
                "working_capital_change": 3_000_000_000  # ~$3B increase
            }
        )

        assert result["success"] is True
        # OE = 99.8B + 11.1B - 10.7B - 3B = 97.2B
        assert result["data"]["result"] == 97_200_000_000
        assert "$97.20B" in result["data"]["result_formatted"]

    def test_missing_required_field(self):
        """Test missing required field"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="owner_earnings",
            data={
                "net_income": 100_000_000,
                # Missing depreciation_amortization
                "capex": 15_000_000,
                "working_capital_change": 5_000_000
            }
        )

        assert result["success"] is False
        assert "depreciation_amortization" in result["error"]

    def test_negative_capex_error(self):
        """Test that negative capex raises error"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="owner_earnings",
            data={
                "net_income": 100_000_000,
                "depreciation_amortization": 10_000_000,
                "capex": -15_000_000,  # Invalid negative capex
                "working_capital_change": 5_000_000
            }
        )

        assert result["success"] is False
        assert "capex" in result["error"].lower()
        assert "negative" in result["error"].lower() or "non-negative" in result["error"].lower()

    def test_high_capex_warning(self):
        """Test warning for high CapEx relative to D&A"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="owner_earnings",
            data={
                "net_income": 100_000_000,
                "depreciation_amortization": 10_000_000,
                "capex": 30_000_000,  # 3x D&A - should trigger warning
                "working_capital_change": 5_000_000
            }
        )

        assert result["success"] is True
        assert len(result["data"]["warnings"]) > 0
        warning_text = " ".join(result["data"]["warnings"])
        assert "capex" in warning_text.lower()


class TestROIC:
    """Test Return on Invested Capital calculation"""

    def test_basic_calculation(self):
        """Test basic ROIC calculation"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="roic",
            data={
                "operating_income": 50_000_000,
                "total_assets": 400_000_000,
                "current_liabilities": 50_000_000,
                "cash_equivalents": 75_000_000
            }
        )

        assert result["success"] is True
        # Invested Capital = 400M - 50M - 75M = 275M
        # ROIC = 50M / 275M = 0.1818 (18.18%)
        assert abs(result["data"]["result"] - 0.1818) < 0.001
        assert "18" in result["data"]["result_formatted"]

    def test_world_class_roic(self):
        """Test ROIC > 25% (world-class)"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="roic",
            data={
                "operating_income": 100_000_000,
                "total_assets": 300_000_000,
                "current_liabilities": 50_000_000,
                "cash_equivalents": 50_000_000
            }
        )

        assert result["success"] is True
        # Invested Capital = 300M - 50M - 50M = 200M
        # ROIC = 100M / 200M = 0.50 (50%)
        assert result["data"]["result"] == 0.50
        assert "WORLD-CLASS" in result["data"]["interpretation"]

    def test_coca_cola_realistic_data(self):
        """Test with Coca-Cola approximate data"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="roic",
            data={
                "operating_income": 10_300_000_000,  # ~$10.3B
                "total_assets": 92_000_000_000,  # ~$92B
                "current_liabilities": 23_000_000_000,  # ~$23B
                "cash_equivalents": 9_000_000_000  # ~$9B
            }
        )

        assert result["success"] is True
        # Invested Capital = 92B - 23B - 9B = 60B
        # ROIC = 10.3B / 60B = 0.1717 (17.17%)
        roic = result["data"]["result"]
        assert 0.15 < roic < 0.20  # Should be in the "GOOD" range
        assert "GOOD" in result["data"]["interpretation"] or "EXCELLENT" in result["data"]["interpretation"]

    def test_zero_invested_capital_error(self):
        """Test error when invested capital is zero"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="roic",
            data={
                "operating_income": 50_000_000,
                "total_assets": 100_000_000,
                "current_liabilities": 50_000_000,
                "cash_equivalents": 50_000_000  # Total = Assets
            }
        )

        assert result["success"] is False
        assert "invested capital" in result["error"].lower()
        assert ("zero" in result["error"].lower() or "is 0" in result["error"].lower())

    def test_low_roic_interpretation(self):
        """Test interpretation for low ROIC < 12%"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="roic",
            data={
                "operating_income": 10_000_000,
                "total_assets": 200_000_000,
                "current_liabilities": 10_000_000,
                "cash_equivalents": 10_000_000
            }
        )

        assert result["success"] is True
        # Invested Capital = 200M - 10M - 10M = 180M
        # ROIC = 10M / 180M = 0.0556 (5.56%)
        roic = result["data"]["result"]
        assert roic < 0.12
        assert "BELOW" in result["data"]["interpretation"]
        assert "AVOID" in result["data"]["interpretation"]


class TestDCF:
    """Test Discounted Cash Flow calculation"""

    def test_basic_dcf(self):
        """Test basic DCF calculation"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="dcf",
            data={
                "owner_earnings": 90_000_000,
                "growth_rate": 0.05,  # 5%
                "discount_rate": 0.10,  # 10%
                "terminal_growth": 0.03,  # 3%
                "years": 10
            }
        )

        assert result["success"] is True
        assert result["data"]["result"] > 0
        assert "breakdown" in result["data"]
        assert "dcf_period_value" in result["data"]["breakdown"]
        assert "terminal_value_present" in result["data"]["breakdown"]

    def test_conservative_buffett_assumptions(self):
        """Test with Buffett's conservative assumptions"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="dcf",
            data={
                "owner_earnings": 100_000_000,
                "growth_rate": 0.07,  # 7% growth
                "discount_rate": 0.10,  # 10% required return
                "terminal_growth": 0.025,  # 2.5% perpetual
                "years": 10
            }
        )

        assert result["success"] is True
        intrinsic_value = result["data"]["result"]
        # Rough sanity check: should be multiple of owner earnings
        assert 500_000_000 < intrinsic_value < 2_000_000_000

    def test_aggressive_growth_warning(self):
        """Test warning for aggressive growth rate"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="dcf",
            data={
                "owner_earnings": 100_000_000,
                "growth_rate": 0.25,  # 25% - very aggressive!
                "discount_rate": 0.10,
                "terminal_growth": 0.03,
                "years": 10
            }
        )

        assert result["success"] is True
        assert len(result["data"]["warnings"]) > 0
        warning_text = " ".join(result["data"]["warnings"])
        assert "aggressive" in warning_text.lower()

    def test_low_discount_rate_warning(self):
        """Test warning for low discount rate"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="dcf",
            data={
                "owner_earnings": 100_000_000,
                "growth_rate": 0.05,
                "discount_rate": 0.06,  # 6% - too low for safety
                "terminal_growth": 0.03,
                "years": 10
            }
        )

        assert result["success"] is True
        assert len(result["data"]["warnings"]) > 0
        warning_text = " ".join(result["data"]["warnings"])
        assert "discount rate" in warning_text.lower()

    def test_terminal_growth_exceeds_discount_rate_error(self):
        """Test error when terminal growth >= discount rate"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="dcf",
            data={
                "owner_earnings": 100_000_000,
                "growth_rate": 0.05,
                "discount_rate": 0.08,
                "terminal_growth": 0.09,  # ERROR: exceeds discount rate
                "years": 10
            }
        )

        assert result["success"] is False
        assert "terminal growth" in result["error"].lower()
        assert "discount rate" in result["error"].lower()

    def test_five_year_projection(self):
        """Test shorter 5-year projection period"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="dcf",
            data={
                "owner_earnings": 100_000_000,
                "growth_rate": 0.07,
                "discount_rate": 0.10,
                "terminal_growth": 0.03,
                "years": 5
            }
        )

        assert result["success"] is True
        assert "years 1-5" in result["data"]["breakdown"]["dcf_period_description"]


class TestMarginOfSafety:
    """Test Margin of Safety calculation"""

    def test_positive_margin(self):
        """Test positive margin (undervalued)"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="margin_of_safety",
            data={
                "intrinsic_value": 150.00,
                "current_price": 100.00
            }
        )

        assert result["success"] is True
        # MoS = (150 - 100) / 150 = 0.3333 (33.33%)
        assert abs(result["data"]["result"] - 0.3333) < 0.001
        assert "33" in result["data"]["result_formatted"]
        assert "GOOD" in result["data"]["interpretation"] or "BUY" in result["data"]["interpretation"]

    def test_negative_margin(self):
        """Test negative margin (overvalued)"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="margin_of_safety",
            data={
                "intrinsic_value": 100.00,
                "current_price": 150.00
            }
        )

        assert result["success"] is True
        # MoS = (100 - 150) / 100 = -0.50 (-50%)
        assert result["data"]["result"] == -0.50
        assert "OVERVALUED" in result["data"]["interpretation"]
        assert "AVOID" in result["data"]["interpretation"]

    def test_excellent_margin(self):
        """Test excellent margin > 40%"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="margin_of_safety",
            data={
                "intrinsic_value": 200.00,
                "current_price": 100.00
            }
        )

        assert result["success"] is True
        # MoS = (200 - 100) / 200 = 0.50 (50%)
        assert result["data"]["result"] == 0.50
        assert "EXCELLENT" in result["data"]["interpretation"]
        assert "STRONG BUY" in result["data"]["interpretation"]

    def test_insufficient_margin(self):
        """Test insufficient margin < 15%"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="margin_of_safety",
            data={
                "intrinsic_value": 110.00,
                "current_price": 100.00
            }
        )

        assert result["success"] is True
        # MoS = (110 - 100) / 110 = 0.0909 (9.09%)
        margin = result["data"]["result"]
        assert 0.08 < margin < 0.10
        assert "INSUFFICIENT" in result["data"]["interpretation"]

    def test_zero_intrinsic_value_error(self):
        """Test error for zero intrinsic value"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="margin_of_safety",
            data={
                "intrinsic_value": 0,
                "current_price": 100.00
            }
        )

        assert result["success"] is False
        assert "intrinsic_value" in result["error"].lower()
        assert "positive" in result["error"].lower()


class TestShariaCompliance:
    """Test Sharia Compliance checking"""

    def test_fully_compliant_company(self):
        """Test fully compliant company (all ratios pass)"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="sharia_compliance_check",
            data={
                "total_debt": 50_000_000_000,
                "total_assets": 200_000_000_000,  # Debt/Assets = 25% < 33%
                "cash_and_liquid_assets": 30_000_000_000,
                "market_cap": 2_000_000_000_000,  # Liquid/MC = 1.5% < 33%
                "accounts_receivable": 60_000_000_000,  # Receivables/MC = 3% < 50%
                "business_activities": ["consumer_electronics", "software", "services"]
            }
        )

        assert result["success"] is True
        assert result["data"]["result"] == 1
        assert result["data"]["result_formatted"] == "COMPLIANT"
        assert "COMPLIANT" in result["data"]["interpretation"]

        # Check all individual tests passed
        breakdown = result["data"]["breakdown"]
        assert breakdown["debt_to_assets"]["status"] == "PASS"
        assert breakdown["liquid_to_market_cap"]["status"] == "PASS"
        assert breakdown["receivables_to_market_cap"]["status"] == "PASS"
        assert breakdown["business_screening"]["status"] == "PASS"

    def test_apple_realistic_data_compliant(self):
        """Test with Apple Inc. data (should be compliant)"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="sharia_compliance_check",
            data={
                "total_debt": 111_000_000_000,  # ~$111B
                "total_assets": 353_000_000_000,  # ~$353B (31.4% ratio - PASS)
                "cash_and_liquid_assets": 90_000_000_000,  # ~$90B
                "market_cap": 2_750_000_000_000,  # ~$2.75T (3.3% ratio - PASS)
                "accounts_receivable": 60_000_000_000,  # ~$60B (2.2% ratio - PASS)
                "business_activities": ["consumer_electronics", "software", "services"]
            }
        )

        assert result["success"] is True
        assert result["data"]["result"] == 1
        assert result["data"]["result_formatted"] == "COMPLIANT"

    def test_debt_ratio_violation(self):
        """Test debt ratio violation (Debt/Assets > 33%)"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="sharia_compliance_check",
            data={
                "total_debt": 80_000_000_000,
                "total_assets": 200_000_000_000,  # Debt/Assets = 40% > 33% (FAIL)
                "cash_and_liquid_assets": 30_000_000_000,
                "market_cap": 2_000_000_000_000,
                "accounts_receivable": 60_000_000_000,
                "business_activities": ["consumer_electronics"]
            }
        )

        assert result["success"] is True
        assert result["data"]["result"] == 0
        assert result["data"]["result_formatted"] == "NON-COMPLIANT"
        assert result["data"]["breakdown"]["debt_to_assets"]["status"] == "FAIL"

    def test_prohibited_activity(self):
        """Test prohibited business activity"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="sharia_compliance_check",
            data={
                "total_debt": 50_000_000_000,
                "total_assets": 200_000_000_000,
                "cash_and_liquid_assets": 30_000_000_000,
                "market_cap": 2_000_000_000_000,
                "accounts_receivable": 60_000_000_000,
                "business_activities": ["consumer_goods", "alcohol_production"]  # PROHIBITED
            }
        )

        assert result["success"] is True
        assert result["data"]["result"] == 0
        assert result["data"]["result_formatted"] == "NON-COMPLIANT"
        assert result["data"]["breakdown"]["business_screening"]["status"] == "FAIL"
        assert "alcohol_production" in result["data"]["breakdown"]["business_screening"]["prohibited_found"]

    def test_multiple_violations(self):
        """Test multiple violations"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="sharia_compliance_check",
            data={
                "total_debt": 80_000_000_000,
                "total_assets": 200_000_000_000,  # 40% - FAIL
                "cash_and_liquid_assets": 900_000_000_000,
                "market_cap": 2_000_000_000_000,  # 45% - FAIL
                "accounts_receivable": 60_000_000_000,
                "business_activities": ["gambling", "conventional_banking"]  # FAIL
            }
        )

        assert result["success"] is True
        assert result["data"]["result"] == 0
        # Should have multiple failures
        breakdown = result["data"]["breakdown"]
        assert breakdown["debt_to_assets"]["status"] == "FAIL"
        assert breakdown["liquid_to_market_cap"]["status"] == "FAIL"
        assert breakdown["business_screening"]["status"] == "FAIL"


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_missing_calculation_parameter(self):
        """Test missing calculation parameter"""
        tool = CalculatorTool()
        result = tool.execute(data={"some": "data"})

        assert result["success"] is False
        assert "calculation" in result["error"].lower()

    def test_missing_data_parameter(self):
        """Test missing data parameter"""
        tool = CalculatorTool()
        result = tool.execute(calculation="owner_earnings")

        assert result["success"] is False
        assert "data" in result["error"].lower()

    def test_invalid_calculation_type(self):
        """Test invalid calculation type"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="invalid_calculation",
            data={"some": "data"}
        )

        assert result["success"] is False
        assert "unknown" in result["error"].lower() or "invalid" in result["error"].lower()
        assert "invalid_calculation" in result["error"]

    def test_empty_data_dict(self):
        """Test empty data dictionary"""
        tool = CalculatorTool()
        result = tool.execute(
            calculation="owner_earnings",
            data={}
        )

        assert result["success"] is False
        assert "missing" in result["error"].lower() or "required" in result["error"].lower()


class TestFormattingHelpers:
    """Test formatting helper methods"""

    def test_currency_formatting(self):
        """Test currency formatting with different magnitudes"""
        tool = CalculatorTool()

        # Test billions
        assert "$1.25B" in tool._format_currency(1_250_000_000)

        # Test millions
        assert "$90.50M" in tool._format_currency(90_500_000)

        # Test thousands
        assert "$15.30K" in tool._format_currency(15_300)

        # Test small amounts
        assert "$150.00" in tool._format_currency(150)

        # Test negative
        assert "-$1.00B" in tool._format_currency(-1_000_000_000)

    def test_percentage_formatting(self):
        """Test percentage formatting"""
        tool = CalculatorTool()

        assert tool._format_percentage(0.18) == "18.0%"
        assert tool._format_percentage(0.2547) == "25.5%"
        assert tool._format_percentage(0.05) == "5.0%"
        assert tool._format_percentage(1.0) == "100.0%"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
