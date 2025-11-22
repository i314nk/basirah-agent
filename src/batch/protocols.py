"""
Batch screening protocols for basīrah.

A protocol defines a multi-stage screening process where companies
progress through stages and are filtered at each step.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AnalysisType(Enum):
    """Types of analysis that can be performed."""
    SHARIA = "sharia"
    QUICK = "quick"
    DEEP_DIVE = "deep_dive"


class Decision(Enum):
    """Possible decisions from analyses."""
    # Sharia decisions
    COMPLIANT = "compliant"
    DOUBTFUL = "doubtful"
    NON_COMPLIANT = "non_compliant"

    # Quick screen decisions
    INVESTIGATE = "investigate"
    PASS = "pass"

    # Deep dive decisions
    BUY = "buy"
    WATCH = "watch"
    AVOID = "avoid"


@dataclass
class ProtocolStage:
    """Single stage in a screening protocol."""

    name: str
    analysis_type: AnalysisType
    pass_decisions: List[Decision]  # Decisions that allow progression
    fail_decisions: List[Decision]  # Decisions that stop progression
    years_to_analyze: Optional[int] = None  # For deep dive
    description: str = ""

    def should_progress(self, decision: str) -> bool:
        """
        Check if a decision allows progression to next stage.

        Args:
            decision: Decision string from analysis

        Returns:
            True if should continue to next stage
        """
        decision_lower = decision.lower()

        # Check if in pass list
        for pass_dec in self.pass_decisions:
            if pass_dec.value in decision_lower:
                return True

        return False


@dataclass
class BatchProtocol:
    """Complete batch screening protocol."""

    id: str
    name: str
    description: str
    stages: List[ProtocolStage]

    def get_stage(self, stage_index: int) -> Optional[ProtocolStage]:
        """Get stage by index."""
        if 0 <= stage_index < len(self.stages):
            return self.stages[stage_index]
        return None

    def total_stages(self) -> int:
        """Get total number of stages."""
        return len(self.stages)

    def estimate_cost(self, num_companies: int) -> Dict[str, Any]:
        """
        Estimate cost for running protocol on N companies.

        Assumes best-case scenario where companies progress through all stages.
        Actual cost will likely be lower due to filtering.

        Args:
            num_companies: Number of companies to screen

        Returns:
            Cost estimate dictionary
        """
        # Cost per analysis type (average)
        cost_map = {
            AnalysisType.SHARIA: 0.98,
            AnalysisType.QUICK: 1.14,
            AnalysisType.DEEP_DIVE: 3.26  # Average of 5-10 years
        }

        # Time per analysis type (minutes)
        time_map = {
            AnalysisType.SHARIA: 4,
            AnalysisType.QUICK: 2,
            AnalysisType.DEEP_DIVE: 15  # Average of 10-20 min
        }

        total_cost = 0
        total_time = 0
        stage_costs = []

        # Assume progressive filtering: 100% → 70% → 50%
        filter_rates = [1.0, 0.7, 0.5]

        for i, stage in enumerate(self.stages):
            filter_rate = filter_rates[min(i, len(filter_rates) - 1)]
            stage_companies = int(num_companies * filter_rate)

            if stage.analysis_type == AnalysisType.DEEP_DIVE and stage.years_to_analyze:
                # Adjust cost for years
                base_cost = 2.09
                per_year_cost = 0.18
                cost_per = base_cost + (stage.years_to_analyze - 1) * per_year_cost
            else:
                cost_per = cost_map.get(stage.analysis_type, 2.0)

            time_per = time_map.get(stage.analysis_type, 5)

            stage_cost = stage_companies * cost_per
            stage_time = stage_companies * time_per

            total_cost += stage_cost
            total_time += stage_time

            stage_costs.append({
                "stage_name": stage.name,
                "companies": stage_companies,
                "cost": round(stage_cost, 2),
                "time_minutes": stage_time
            })

        return {
            "total_companies": num_companies,
            "total_cost_min": round(total_cost * 0.5, 2),  # Best case (heavy filtering)
            "total_cost_max": round(total_cost, 2),  # Worst case (light filtering)
            "total_time_minutes": total_time,
            "total_time_hours": round(total_time / 60, 1),
            "stage_breakdown": stage_costs
        }


# Predefined Protocols

HALAL_VALUE_PROTOCOL = BatchProtocol(
    id="halal_value",
    name="Halal Value Investing",
    description="Complete screening: Sharia compliance → Business quality → Detailed analysis",
    stages=[
        ProtocolStage(
            name="Sharia Compliance Screen",
            analysis_type=AnalysisType.SHARIA,
            pass_decisions=[Decision.COMPLIANT, Decision.DOUBTFUL],
            fail_decisions=[Decision.NON_COMPLIANT],
            description="Filter for Sharia-compliant companies"
        ),
        ProtocolStage(
            name="Quick Screen",
            analysis_type=AnalysisType.QUICK,
            pass_decisions=[Decision.INVESTIGATE],
            fail_decisions=[Decision.PASS],
            description="Identify companies worth deep analysis"
        ),
        ProtocolStage(
            name="Deep Dive Analysis",
            analysis_type=AnalysisType.DEEP_DIVE,
            pass_decisions=[Decision.BUY, Decision.WATCH, Decision.AVOID],
            fail_decisions=[],
            years_to_analyze=10,
            description="Complete Warren Buffett analysis (10 years)"
        )
    ]
)

VALUE_ONLY_PROTOCOL = BatchProtocol(
    id="value_only",
    name="Value Investing Only",
    description="Skip Sharia screening, focus on business quality",
    stages=[
        ProtocolStage(
            name="Quick Screen",
            analysis_type=AnalysisType.QUICK,
            pass_decisions=[Decision.INVESTIGATE],
            fail_decisions=[Decision.PASS],
            description="Filter for quality businesses"
        ),
        ProtocolStage(
            name="Deep Dive Analysis",
            analysis_type=AnalysisType.DEEP_DIVE,
            pass_decisions=[Decision.BUY, Decision.WATCH, Decision.AVOID],
            fail_decisions=[],
            years_to_analyze=5,
            description="Complete Warren Buffett analysis (5 years)"
        )
    ]
)

SHARIA_ONLY_PROTOCOL = BatchProtocol(
    id="sharia_only",
    name="Sharia Screening Only",
    description="Check Islamic compliance for large universe of companies",
    stages=[
        ProtocolStage(
            name="Sharia Compliance Screen",
            analysis_type=AnalysisType.SHARIA,
            pass_decisions=[Decision.COMPLIANT, Decision.DOUBTFUL, Decision.NON_COMPLIANT],
            fail_decisions=[],
            description="Check Sharia compliance status"
        )
    ]
)

QUICK_FILTER_PROTOCOL = BatchProtocol(
    id="quick_filter",
    name="Quick Filter Only",
    description="Fast screening to build watchlist",
    stages=[
        ProtocolStage(
            name="Quick Screen",
            analysis_type=AnalysisType.QUICK,
            pass_decisions=[Decision.INVESTIGATE, Decision.PASS],
            fail_decisions=[],
            description="1-year business snapshot"
        )
    ]
)

# Protocol registry
PROTOCOLS: Dict[str, BatchProtocol] = {
    "halal_value": HALAL_VALUE_PROTOCOL,
    "value_only": VALUE_ONLY_PROTOCOL,
    "sharia_only": SHARIA_ONLY_PROTOCOL,
    "quick_filter": QUICK_FILTER_PROTOCOL
}


def get_protocol(protocol_id: str) -> Optional[BatchProtocol]:
    """Get protocol by ID."""
    return PROTOCOLS.get(protocol_id)


def list_protocols() -> List[BatchProtocol]:
    """Get all available protocols."""
    return list(PROTOCOLS.values())


__all__ = [
    "AnalysisType",
    "Decision",
    "ProtocolStage",
    "BatchProtocol",
    "PROTOCOLS",
    "get_protocol",
    "list_protocols"
]
