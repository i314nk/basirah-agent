"""
Data structures for Phase 7.7 hybrid architecture with Pydantic validation.

Module: src.agent.data_structures
Purpose: Define structured data formats for quantitative/qualitative/hybrid analysis
Status: Phase 7.7 - Pydantic Integration (2025-11-18)
Created: 2025-11-16
Updated: 2025-11-18 - Converted to Pydantic for validation

This module defines the data structures used in the hybrid architecture:
- AnalysisMetrics: Quantitative financial metrics (ROIC, revenue, margins, etc.)
- AnalysisInsights: Qualitative assessments (moat, management, risks)
- YearAnalysis: Combined structure for a single year's analysis
- ToolCache: Cached tool outputs to avoid redundant API calls
"""

from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class AnalysisMetrics(BaseModel):
    """
    Quantitative metrics extracted from financial data.

    These are structured, numerical values that can be used for:
    - Trend analysis across years
    - Building financial tables
    - Programmatic validation
    - Calculations (CAGR, averages, etc.)

    Corresponds to:
    - Phase 1: Initial Screen (ROIC, debt, consistency)
    - Phase 5: Financial Strength (Owner Earnings, ratios)
    - Phase 3/7: Moat/Valuation quantitative components
    """
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        extra='forbid',
        str_strip_whitespace=True
    )

    # Phase 1: Initial Screen
    roic: Optional[float] = Field(
        None,
        ge=0.0,
        le=5.0,
        description="Return on Invested Capital (0.0-5.0 = 0%-500%)"
    )
    debt_equity: Optional[float] = Field(
        None,
        ge=0.0,
        description="Debt to Equity ratio (non-negative)"
    )
    earnings_consistent: Optional[bool] = Field(
        None,
        description="Are earnings consistent?"
    )

    # Phase 5: Financial Strength - Income Statement
    revenue: Optional[float] = Field(
        None,
        description="Total revenue in millions USD"
    )
    operating_income: Optional[float] = Field(
        None,
        description="Operating income in millions USD"
    )
    net_income: Optional[float] = Field(
        None,
        description="Net income in millions USD"
    )

    # Phase 5: Financial Strength - Cash Flow
    operating_cash_flow: Optional[float] = Field(
        None,
        description="Operating cash flow in millions USD"
    )
    capex: Optional[float] = Field(
        None,
        description="Capital expenditures in millions USD (usually negative)"
    )
    owner_earnings: Optional[float] = Field(
        None,
        description="Owner Earnings (OCF - CapEx) in millions USD"
    )
    free_cash_flow: Optional[float] = Field(
        None,
        description="Free cash flow in millions USD"
    )

    # Phase 5: Financial Strength - Balance Sheet
    total_assets: Optional[float] = Field(
        None,
        gt=0,
        description="Total assets in millions USD (must be positive)"
    )
    total_debt: Optional[float] = Field(
        None,
        ge=0,
        description="Total debt in millions USD (non-negative)"
    )
    cash_and_equivalents: Optional[float] = Field(
        None,
        ge=0,
        description="Cash and equivalents in millions USD (non-negative)"
    )
    shareholders_equity: Optional[float] = Field(
        None,
        description="Shareholders' equity in millions USD"
    )

    # Phase 5: Financial Strength - Margins
    gross_margin: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Gross margin as decimal (0.0-1.0 = 0%-100%)"
    )
    operating_margin: Optional[float] = Field(
        None,
        ge=-1.0,
        le=1.0,
        description="Operating margin as decimal (-1.0 to 1.0)"
    )
    net_margin: Optional[float] = Field(
        None,
        ge=-1.0,
        le=1.0,
        description="Net margin as decimal (-1.0 to 1.0)"
    )

    # Phase 5: Financial Strength - Returns & Efficiency
    roic_10yr: Optional[List[float]] = Field(
        None,
        max_length=10,
        description="10-year ROIC history [current, -1yr, -2yr, ...]"
    )
    roic_avg: Optional[float] = Field(
        None,
        ge=0.0,
        le=5.0,
        description="Average ROIC over 10 years (0.0-5.0)"
    )
    roic_stddev: Optional[float] = Field(
        None,
        ge=0.0,
        description="Standard deviation of ROIC (non-negative)"
    )
    roe: Optional[float] = Field(
        None,
        ge=-5.0,
        le=10.0,
        description="Return on Equity (-5.0 to 10.0)"
    )
    roa: Optional[float] = Field(
        None,
        ge=-5.0,
        le=10.0,
        description="Return on Assets (-5.0 to 10.0)"
    )

    # Phase 5: Financial Strength - Debt Coverage
    interest_coverage: Optional[float] = Field(
        None,
        description="EBIT / Interest Expense"
    )
    cash_to_debt: Optional[float] = Field(
        None,
        ge=0.0,
        description="Cash / Total Debt ratio (non-negative)"
    )

    # Phase 3: Economic Moat - Quantitative Components
    market_share: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Market share as decimal (0.0-1.0 = 0%-100%)"
    )
    customer_retention: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Customer retention rate as decimal (0.0-1.0)"
    )
    nps_score: Optional[int] = Field(
        None,
        ge=-100,
        le=100,
        description="Net Promoter Score (-100 to 100)"
    )

    # Phase 7: Valuation - Quantitative Components
    owner_earnings_normalized: Optional[float] = Field(
        None,
        description="5-year average Owner Earnings in millions USD"
    )
    growth_rate: Optional[float] = Field(
        None,
        ge=-0.5,
        le=1.0,
        description="Conservative growth assumption as decimal (-0.5 to 1.0 = -50% to 100%)"
    )
    discount_rate: Optional[float] = Field(
        None,
        ge=0.05,
        le=0.30,
        description="Discount rate used in DCF as decimal (0.05-0.30 = 5%-30%)"
    )
    terminal_growth: Optional[float] = Field(
        None,
        ge=0.0,
        le=0.05,
        description="Terminal growth rate as decimal (0.0-0.05 = 0%-5%)"
    )
    dcf_intrinsic_value: Optional[float] = Field(
        None,
        gt=0,
        description="DCF intrinsic value per share in USD (must be positive)"
    )
    current_price: Optional[float] = Field(
        None,
        gt=0,
        description="Current market price per share in USD (must be positive)"
    )
    margin_of_safety: Optional[float] = Field(
        None,
        ge=-1.0,
        le=1.0,
        description="(IV - Price) / IV as decimal (-1.0 to 1.0 = -100% to 100%)"
    )
    shares_outstanding: Optional[float] = Field(
        None,
        gt=0,
        description="Shares outstanding in millions (must be positive)"
    )

    # Additional metrics
    pe_ratio: Optional[float] = Field(
        None,
        description="Price to Earnings ratio"
    )
    pb_ratio: Optional[float] = Field(
        None,
        description="Price to Book ratio"
    )
    ev_ebitda: Optional[float] = Field(
        None,
        description="Enterprise Value to EBITDA"
    )

    @field_validator('roic', 'roic_avg')
    @classmethod
    def validate_roic_reasonable(cls, v):
        """Ensure ROIC is in reasonable range."""
        if v is not None and not (0.0 <= v <= 2.0):
            raise ValueError(f"ROIC {v*100:.1f}% outside reasonable range (0-200%)")
        return v

    @field_validator('debt_equity')
    @classmethod
    def validate_leverage_reasonable(cls, v):
        """Ensure debt/equity is reasonable."""
        if v is not None and v > 10:
            raise ValueError(f"Debt/Equity {v:.2f} seems unrealistic (>10)")
        return v

    @field_validator('operating_margin', 'net_margin')
    @classmethod
    def validate_margin_logic(cls, v):
        """Warn about unusual margins."""
        if v is not None and abs(v) > 0.5:
            # Allow but log - some companies have extreme margins
            pass
        return v

    def model_post_init(self, __context):
        """Post-initialization validation for cross-field logic."""
        # Validate net margin <= operating margin
        if (self.net_margin is not None and
            self.operating_margin is not None and
            self.net_margin > self.operating_margin):
            # This can happen due to one-time gains, so just warn
            pass

        # Validate gross margin >= operating margin
        if (self.gross_margin is not None and
            self.operating_margin is not None and
            self.operating_margin > self.gross_margin):
            raise ValueError(
                f"Operating margin ({self.operating_margin*100:.1f}%) cannot exceed "
                f"gross margin ({self.gross_margin*100:.1f}%)"
            )


class AnalysisInsights(BaseModel):
    """
    Qualitative insights from investment analysis.

    Text-based assessments requiring judgment:
    - Business model understanding
    - Moat assessment narratives
    - Management quality evaluation
    - Risk assessment

    Corresponds to:
    - Phase 2: Business Understanding
    - Phase 4: Management Quality
    - Phase 6: Risk Assessment
    - Phase 3/7: Moat/Valuation qualitative components
    """
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        extra='forbid',
        str_strip_whitespace=True
    )

    # Phase 2: Business Understanding
    business_model: str = Field(
        "",
        max_length=1000,
        description="How the business makes money (max 1000 chars)"
    )
    circle_of_competence: str = Field(
        "",
        max_length=500,
        description="PASS/FAIL with reasoning"
    )
    key_products: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Main products/services (max 10)"
    )
    revenue_sources: str = Field(
        "",
        max_length=500,
        description="Revenue breakdown and sources"
    )

    # Phase 3: Economic Moat - Qualitative Components
    moat_rating: Literal["DOMINANT", "STRONG", "MODERATE", "WEAK"] = Field(
        "MODERATE",
        description="Economic moat strength assessment"
    )
    brand_power: str = Field(
        "",
        max_length=500,
        description="Brand strength narrative"
    )
    network_effects: str = Field(
        "",
        max_length=500,
        description="Network effects narrative"
    )
    switching_costs: str = Field(
        "",
        max_length=500,
        description="Switching costs narrative"
    )
    cost_advantages: str = Field(
        "",
        max_length=500,
        description="Cost advantages narrative"
    )
    intangible_assets: str = Field(
        "",
        max_length=500,
        description="Patents, licenses, etc."
    )
    moat_durability: str = Field(
        "",
        max_length=500,
        description="Will moat last 10+ years?"
    )
    moat_sources: List[str] = Field(
        default_factory=list,
        max_length=6,
        description="List of moat types (max 6)"
    )

    # Phase 4: Management Quality
    management_assessment: str = Field(
        "",
        max_length=1000,
        description="Overall management evaluation"
    )
    integrity_evidence: List[str] = Field(
        default_factory=list,
        max_length=8,
        description="Evidence of integrity (max 8)"
    )
    red_flags: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Management concerns (max 5)"
    )
    insider_ownership: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Insider ownership as decimal (0.0-1.0)"
    )

    # Phase 6: Risk Assessment
    risk_rating: Literal["LOW", "MODERATE", "HIGH"] = Field(
        "MODERATE",
        description="Overall risk level assessment"
    )
    primary_risks: List[str] = Field(
        default_factory=list,
        max_length=8,
        description="Key risks identified (max 8)"
    )
    risk_mitigation: str = Field(
        "",
        max_length=1000,
        description="How risks are mitigated"
    )

    # Phase 7: Valuation - Qualitative Components
    discount_rate_reasoning: str = Field(
        "",
        max_length=500,
        description="Why 9% vs 10% vs 12%?"
    )
    growth_reasoning: str = Field(
        "",
        max_length=500,
        description="Why this growth rate?"
    )
    assumption_sensitivity: str = Field(
        "",
        max_length=500,
        description="How sensitive is valuation to assumptions?"
    )

    # Phase 7: Final Decision
    decision: Literal["BUY", "WATCH", "AVOID"] = Field(
        "WATCH",
        description="Investment recommendation"
    )
    conviction: Literal["HIGH", "MODERATE", "LOW"] = Field(
        "MODERATE",
        description="Confidence level in decision"
    )
    decision_reasoning: str = Field(
        "",
        max_length=1000,
        description="Why BUY/WATCH/AVOID?"
    )
    watch_price: Optional[float] = Field(
        None,
        gt=0,
        description="Price target if WATCH in USD per share"
    )

    # Prior years specific
    moat_changes: str = Field(
        "",
        max_length=500,
        description="How moat changed this year"
    )
    management_actions: str = Field(
        "",
        max_length=500,
        description="Key management actions this year"
    )
    one_time_events: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="One-time events this year (max 5)"
    )
    year_summary: str = Field(
        "",
        max_length=1000,
        description="Summary of this year"
    )

    @field_validator('primary_risks', 'moat_sources', 'key_products')
    @classmethod
    def validate_list_items_not_empty(cls, v, info):
        """Ensure list items are meaningful."""
        if v:
            for item in v:
                if not item or (isinstance(item, str) and len(item.strip()) < 3):
                    raise ValueError(f"{info.field_name} item too short: '{item}'")
        return v

    @field_validator('business_model', 'management_assessment', 'decision_reasoning')
    @classmethod
    def validate_text_meaningful(cls, v, info):
        """Ensure important text fields are meaningful if provided."""
        if v and len(v.strip()) > 0 and len(v.strip()) < 10:
            raise ValueError(f"{info.field_name} too short (min 10 chars if provided): '{v}'")
        return v


class ToolCache(BaseModel):
    """
    Cache of all tool outputs to avoid redundant API calls.

    Each tool response is stored as-is to enable:
    - Re-extraction if data structure changes
    - Debugging and validation
    - Avoiding duplicate API costs
    """
    model_config = ConfigDict(
        validate_assignment=True,
        extra='allow'  # Allow extra fields for flexibility
    )

    # GuruFocus tool outputs
    gurufocus_summary: Optional[Dict[str, Any]] = Field(
        None,
        description="GuruFocus summary endpoint response"
    )
    gurufocus_financials: Optional[Dict[str, Any]] = Field(
        None,
        description="GuruFocus financials endpoint response"
    )
    gurufocus_keyratios: Optional[Dict[str, Any]] = Field(
        None,
        description="GuruFocus keyratios endpoint response"
    )
    gurufocus_valuation: Optional[Dict[str, Any]] = Field(
        None,
        description="GuruFocus valuation endpoint response"
    )

    # SEC filing tool outputs
    sec_10k_full: Optional[str] = Field(
        None,
        description="Complete 10-K text"
    )
    sec_10k_business: Optional[str] = Field(
        None,
        description="Business section from 10-K"
    )
    sec_10k_mda: Optional[str] = Field(
        None,
        description="MD&A section from 10-K"
    )
    sec_10k_risk_factors: Optional[str] = Field(
        None,
        description="Risk factors section from 10-K"
    )
    sec_10q: Optional[str] = Field(
        None,
        description="Latest 10-Q text"
    )
    sec_proxy: Optional[str] = Field(
        None,
        description="Proxy statement (DEF 14A) text"
    )

    # Web search tool outputs
    web_search_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="All web search results keyed by query"
    )

    # Calculator tool outputs
    calculator_outputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="All calculator results keyed by calculation type"
    )


class YearAnalysis(BaseModel):
    """
    Complete analysis for a single year.

    Combines:
    - Metadata (year, ticker)
    - Quantitative metrics (structured)
    - Qualitative insights (text)
    - Tool cache (raw outputs)
    - Full analysis text (for context and backward compatibility)
    """
    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid',
        protected_namespaces=()  # Allow 'model_used' field (suppress warning)
    )

    # Metadata
    year: int = Field(
        ...,
        ge=1900,
        le=2100,
        description="Analysis year (1900-2100)"
    )
    ticker: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Stock ticker (1-10 chars)"
    )
    data_version: str = Field(
        "7.7",
        description="Data structure version"
    )

    # Structured data
    metrics: AnalysisMetrics = Field(
        default_factory=AnalysisMetrics,
        description="Quantitative financial metrics"
    )
    insights: AnalysisInsights = Field(
        default_factory=AnalysisInsights,
        description="Qualitative assessments"
    )
    tool_cache: ToolCache = Field(
        default_factory=ToolCache,
        description="Cached tool outputs"
    )

    # Full text analysis (for backward compatibility and context)
    full_analysis: str = Field(
        "",
        description="Complete narrative analysis"
    )

    # Analysis metadata
    analysis_date: Optional[str] = Field(
        None,
        description="When analysis was performed (ISO format)"
    )
    model_used: Optional[str] = Field(
        None,
        description="LLM model used for analysis"
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'YearAnalysis':
        """Create YearAnalysis from dictionary (backward compatibility)."""
        return cls(**data)


class MultiYearAnalysis(BaseModel):
    """
    Complete analysis across multiple years.

    Contains:
    - Current year analysis (most recent)
    - Prior years analyses (historical)
    - Synthesis (final investment thesis)
    """
    model_config = ConfigDict(validate_assignment=True, extra='forbid')

    # Core analysis data
    ticker: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Stock ticker"
    )
    current_year: YearAnalysis = Field(
        ...,
        description="Current year analysis (most recent)"
    )
    prior_years: List[YearAnalysis] = Field(
        default_factory=list,
        max_length=10,
        description="Historical years analyses (max 10)"
    )

    # Synthesis
    synthesis: str = Field(
        "",
        description="Final investment thesis"
    )
    synthesis_decision: Literal["BUY", "WATCH", "AVOID"] = Field(
        "WATCH",
        description="Final investment decision"
    )
    synthesis_conviction: Literal["HIGH", "MODERATE", "LOW"] = Field(
        "MODERATE",
        description="Confidence in final decision"
    )

    # Validation
    validation_score: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Validation score (0-100)"
    )
    validation_iterations: int = Field(
        0,
        ge=0,
        le=10,
        description="Number of refinement iterations (0-10)"
    )

    # Metadata
    total_years_analyzed: int = Field(
        1,
        ge=1,
        le=10,
        description="Total years analyzed (1-10)"
    )
    analysis_type: Literal["quick_screen", "deep_dive"] = Field(
        "quick_screen",
        description="Type of analysis performed"
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MultiYearAnalysis':
        """Create MultiYearAnalysis from dictionary (backward compatibility)."""
        return cls(**data)


# Helper type aliases for clarity
CurrentYear = YearAnalysis
PriorYear = YearAnalysis

__all__ = [
    "AnalysisMetrics",
    "AnalysisInsights",
    "ToolCache",
    "YearAnalysis",
    "MultiYearAnalysis",
    "CurrentYear",
    "PriorYear"
]
