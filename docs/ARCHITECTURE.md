# System Architecture: basīrah

## Autonomous AI Investment Agent Using Warren Buffett's Philosophy

**Version:** 1.0  
**Last Updated:** October 29, 2025  
**Agent Core:** Claude 4.5 Sonnet with Extended Thinking  
**Architecture Pattern:** Tool-Based ReAct (Reasoning and Acting)

---

## Document Purpose

This document defines the complete system architecture for basīrah, an autonomous AI investment agent that analyzes publicly traded companies using Warren Buffett's value investing philosophy with Sharia compliance verification. The agent operates autonomously, conducting deep investigations through iterative tool use, reasoning transparently, and producing comprehensive investment theses.

---

## 1. System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│  (Request: "Analyze AAPL for investment potential")        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  AGENT ORCHESTRATOR                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   Claude 4.5 Sonnet with Extended Thinking Mode      │   │
│  │   - System Prompt (Buffett Principles)              │   │
│  │   - Context Window: 200K tokens                      │   │
│  │   - Extended Thinking: Deep reasoning chains         │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              ReAct Reasoning Loop                    │   │
│  │   1. OBSERVATION: Analyze current information        │   │
│  │   2. REASONING: Extended thinking about next steps   │   │
│  │   3. ACTION: Select and execute tool                 │   │
│  │   4. REPEAT until sufficient evidence gathered       │   │
│  │   5. DECISION: Generate investment thesis            │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     TOOL REGISTRY                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  GuruFocus  │  │  SEC Filing  │  │  Calculator  │      │
│  │     Tool    │  │     Tool     │  │     Tool     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐                                           │
│  │  Web Search │                                            │
│  │     Tool    │                                            │
│  └──────────────┘                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL APIS                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  GuruFocus  │  │  SEC EDGAR   │  │Brave Search  │      │
│  │  Premium    │  │   (Free)     │  │   (Free)     │      │
│  │   ~$40/mo   │  │              │  │  2K calls    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 OUTPUT GENERATION                           │
│  - Investment Thesis (Markdown)                             │
│  - Reasoning Chain (Transparent trace)                      │
│  - Recommendation: BUY / WATCH / AVOID                      │
│  - Confidence: High / Medium / Low                          │
└─────────────────────────────────────────────────────────────┘
```

### Component Relationships

**Agent Orchestrator** → Controls investigation flow, makes reasoning decisions  
**Tool Registry** → Provides interface for tool discovery and execution  
**Tools** → Abstract API interactions and computations  
**External APIs** → Data sources for financial information  
**Output Generator** → Formats final investment thesis

### Data Flow Overview

```
User Query → Ticker Symbol
     ↓
Initial Screening (GuruFocus Tool)
     ↓
Business Understanding (SEC Filing Tool + Web Search)
     ↓
Moat Assessment (Web Search + GuruFocus data)
     ↓
Management Evaluation (SEC Filings + Web Search)
     ↓
Financial Analysis (GuruFocus + Calculator Tool)
     ↓
Valuation (Calculator Tool + GuruFocus)
     ↓
Risk Assessment (SEC Filings + Web Search)
     ↓
Sharia Compliance Check (Calculator Tool)
     ↓
Final Decision Synthesis (Extended Thinking)
     ↓
Investment Thesis Output
```

---

## 2. Agent Core Design

### LLM: Claude 4.5 Sonnet with Extended Thinking

**Model Selection Rationale:**

1. **Extended Thinking Mode:** Enables deep, multi-step reasoning chains critical for complex investment analysis
2. **200K Context Window:** Accommodates full 10-K filings, multiple data sources, and reasoning history
3. **Tool Use Capability:** Native support for function calling and tool orchestration
4. **Quality Reasoning:** Superior analytical capabilities for evaluating business models and competitive advantages
5. **Cost-Effectiveness:** ~$2-5 per analysis acceptable for quality ($0.003/1K input tokens, $0.015/1K output tokens)

### Why Extended Thinking Mode

Extended thinking is essential for:

- **Complex Financial Analysis:** Multi-step calculations (Owner Earnings, ROIC, DCF) requiring verification
- **Moat Assessment:** Weighing multiple competitive advantage factors across different dimensions
- **Management Evaluation:** Synthesizing evidence from shareholder letters, compensation data, and public statements
- **Risk Analysis:** Identifying subtle warning signs in financial statements and business narratives
- **Investment Thesis Synthesis:** Connecting dots across business understanding, financials, and valuation

**Token Budget Strategy:**
- Initial screening: ~5-10K tokens
- Deep investigation: ~30-50K tokens
- Extended thinking chains: ~10-20K tokens
- Total per analysis: ~50-100K tokens (within 200K limit with margin for tool results)

### System Prompt Structure

The agent operates with a comprehensive system prompt that includes:

```python
system_prompt = f"""
You are an autonomous investment analyst trained in Warren Buffett's value investing philosophy.

Your task: Thoroughly investigate companies to determine if they meet Buffett's strict investment criteria.

CORE PRINCIPLES (from BUFFETT_PRINCIPLES.md):
{load_buffett_principles()}

DECISION FRAMEWORK:
- BUY: Wide moat + Excellent management + ROIC >15% consistently + Margin of Safety >25%
- WATCH: Narrow moat + Good management + ROIC >12% + Margin of Safety 15-25%
- AVOID: No moat OR poor management OR ROIC <12% OR no margin of safety

INVESTIGATION APPROACH:
You have access to tools for gathering evidence. Use them systematically:
1. Start with financial screening (GuruFocus)
2. Understand the business deeply (SEC filings, web search)
3. Assess competitive advantages (web research, financial analysis)
4. Evaluate management quality (SEC filings, web search)
5. Calculate intrinsic value (Calculator tool)
6. Verify Sharia compliance (Calculator tool)
7. Make final decision with full reasoning transparency

CRITICAL RULES:
- Never recommend a stock without thorough investigation
- Always show your reasoning chain (think out loud)
- Admit uncertainty when evidence is insufficient
- Be intellectually honest about risks and weaknesses
- Override BUY if Sharia non-compliant

TOOLS AVAILABLE:
{generate_tool_descriptions()}

Begin investigation when user provides a ticker symbol.
"""
```

**Key Components:**
1. **Identity & Mission:** Establishes agent as autonomous analyst
2. **Buffett Principles:** Complete investment criteria loaded from `docs/BUFFETT_PRINCIPLES.md`
3. **Decision Framework:** BUY/WATCH/AVOID criteria with specific thresholds
4. **Investigation Workflow:** High-level guidance on systematic analysis
5. **Tool Descriptions:** Dynamic loading of available tools with usage guidance
6. **Ethical Guidelines:** Transparency, intellectual honesty, risk disclosure

### Context Management

**Context Window Utilization Strategy:**

```
┌────────────────────────────────────────────────────┐
│ Context Window (200K tokens)                       │
├────────────────────────────────────────────────────┤
│ System Prompt: ~8-10K tokens                       │
│   - Buffett Principles                             │
│   - Tool descriptions                              │
│   - Decision framework                             │
├────────────────────────────────────────────────────┤
│ Investigation History: ~40-60K tokens              │
│   - Tool calls and results                         │
│   - Reasoning chains                               │
│   - Evidence accumulation                          │
├────────────────────────────────────────────────────┤
│ Current Documents: ~60-80K tokens                  │
│   - 10-K excerpts (business description)           │
│   - Shareholder letter sections                    │
│   - Web search results                             │
│   - Financial data tables                          │
├────────────────────────────────────────────────────┤
│ Working Memory: ~30-40K tokens                     │
│   - Extended thinking chains                       │
│   - Intermediate calculations                      │
│   - Synthesis notes                                │
├────────────────────────────────────────────────────┤
│ Response Generation: ~10-20K tokens                │
│   - Final investment thesis                        │
│   - Formatted output                               │
└────────────────────────────────────────────────────┘
```

**Context Overflow Strategy:**
- **Priority 1:** System prompt (always retained)
- **Priority 2:** Key findings summary (updated after each phase)
- **Priority 3:** Recent tool results (last 3-5 calls)
- **Priority 4:** Extended thinking chains (summarized if needed)
- **Priority 5:** Full documents (excerpted to most relevant sections)

**Document Processing:**
- Large documents (10-K) are processed in chunks
- Agent requests specific sections (e.g., "Business" section only)
- Summaries generated and retained instead of full text
- References kept to original documents for verification

### Memory Approach

**Stateless with Conversation History:**
- Each analysis is independent (no persistent memory across companies)
- Within-analysis memory via conversation history (all tool results retained)
- Key findings extracted and summarized at phase transitions

**Evidence Chain Tracking:**
```python
evidence_chain = {
    "business_model": {
        "source": "10-K Business Section",
        "finding": "Apple generates revenue through hardware (iPhone 52%), services (22%), wearables (11%)",
        "confidence": "High"
    },
    "moat_brand_power": {
        "source": "Web search + GuruFocus margins",
        "finding": "Premium pricing sustained, gross margin 42% vs industry 35%, NPS 72",
        "confidence": "High"
    },
    "roic_consistency": {
        "source": "GuruFocus + Calculator",
        "finding": "10-year average ROIC 31%, std dev 4.2%, consistently >25%",
        "confidence": "High"
    }
}
```

This structure allows the agent to:
1. Reference specific evidence when making conclusions
2. Assess confidence based on source quality and consistency
3. Identify gaps requiring additional investigation
4. Provide transparent reasoning in final thesis

---

## 3. ReAct Reasoning Loop

The agent operates through an iterative Reasoning and Acting (ReAct) cycle, making autonomous decisions about investigation direction based on accumulated evidence.

### Core ReAct Cycle

```
┌─────────────────────────────────────────────────────────────┐
│  OBSERVATION                                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Analyze current state:                                 │ │
│  │ - What information do we have?                         │ │
│  │ - What does it tell us?                                │ │
│  │ - What's still missing?                                │ │
│  │ - Do patterns emerge?                                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  REASONING (Extended Thinking)                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Deep analysis of next steps:                           │ │
│  │ - Which investigation path is most valuable?           │ │
│  │ - What tool should we use next?                        │ │
│  │ - What specific question needs answering?              │ │
│  │ - How will this information affect our decision?       │ │
│  │ - Are we ready to conclude or need more evidence?      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  ACTION                                                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Execute tool with specific parameters:                 │ │
│  │ - Tool selection based on reasoning                    │ │
│  │ - Precise query/parameters                             │ │
│  │ - Error handling if tool fails                         │ │
│  │ - Extract key information from results                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  DECISION GATE                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Sufficient evidence to decide?                         │ │
│  │                                                         │ │
│  │ YES → Proceed to final synthesis                       │ │
│  │ NO  → Loop back to OBSERVATION                         │ │
│  │                                                         │ │
│  │ Stopping conditions:                                   │ │
│  │ - All key criteria evaluated                           │ │
│  │ - Clear BUY/WATCH/AVOID signal                         │ │
│  │ - Maximum investigation depth reached (20 tool calls)  │ │
│  │ - Obvious disqualification found (AVOID immediately)   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### How Agent Decides Which Tool to Use

**Decision Process:**

1. **Current Investigation Phase:**
   - Initial screening → GuruFocus Tool
   - Business understanding → SEC Filing Tool
   - Recent news/management → Web Search Tool
   - Calculations → Calculator Tool

2. **Information Gaps:**
   - Missing financial data → GuruFocus Tool
   - Need regulatory details → SEC Filing Tool
   - Need industry context → Web Search Tool
   - Need computed metrics → Calculator Tool

3. **Evidence Quality:**
   - Conflicting information → Additional source (Web Search)
   - Incomplete data → Alternative tool
   - Outdated information → Fresh search (Web Search with recent filter)

**Tool Selection Logic:**

```python
def select_next_tool(investigation_state):
    """
    Agent's internal reasoning for tool selection
    """
    # Check investigation phase
    if investigation_state.phase == "initial_screening":
        if not investigation_state.has("basic_financials"):
            return "gurufocus_tool", {"ticker": ticker, "endpoint": "summary"}
    
    elif investigation_state.phase == "business_understanding":
        if not investigation_state.has("10k_business_section"):
            return "sec_filing_tool", {"ticker": ticker, "filing_type": "10-K", "section": "business"}
        elif not investigation_state.has("recent_business_changes"):
            return "web_search_tool", {"query": f"{company} business model changes", "search_type": "news"}
    
    elif investigation_state.phase == "moat_assessment":
        if not investigation_state.has("competitive_position"):
            return "web_search_tool", {"query": f"{company} competitive advantages market share"}
        if not investigation_state.has("pricing_power_evidence"):
            return "web_search_tool", {"query": f"{company} pricing power premium pricing"}
    
    elif investigation_state.phase == "financial_analysis":
        if investigation_state.has("raw_financials") and not investigation_state.has("owner_earnings"):
            return "calculator_tool", {"calculation": "owner_earnings", "data": financial_data}
        if investigation_state.has("owner_earnings") and not investigation_state.has("roic"):
            return "calculator_tool", {"calculation": "roic", "data": financial_data}
    
    # Continue with next phase or conclude
    return select_next_phase(investigation_state)
```

### How Agent Adapts Investigation Based on Findings

**Adaptive Investigation Strategies:**

**Scenario 1: Early Disqualification**
```
Finding: ROIC consistently <10% over past 10 years
Agent Response:
  - Skip detailed moat analysis (clearly no moat if ROIC low)
  - Skip valuation (won't buy anyway)
  - Brief check for turnaround story (web search)
  - Fast path to AVOID decision
  - Tool calls saved: ~8-12 calls
```

**Scenario 2: Promising Initial Signals**
```
Finding: ROIC >20%, growing revenue, low debt
Agent Response:
  - Deep dive into moat sources (multiple web searches)
  - Thorough management evaluation (SEC filings + web search)
  - Detailed valuation work (DCF with multiple scenarios)
  - Conservative assumptions testing
  - Tool calls needed: ~15-20 calls
```

**Scenario 3: Mixed Signals**
```
Finding: Good ROIC but declining margins, recent management change
Agent Response:
  - Focus investigation on competitive threats (web search)
  - Deep dive into new management background (web search)
  - Analyze recent strategic shifts (latest 10-K + 10-Q)
  - Assess probability of margin recovery
  - Decision: Likely WATCH pending more data
```

**Scenario 4: Data Gaps**
```
Finding: GuruFocus returns special values (9999, 10000)
Agent Response:
  - Try SEC EDGAR Company Facts API directly
  - Check recent quarterly filings for missing data
  - Use alternative calculation methods if possible
  - Flag data limitations in final thesis
  - Lower confidence rating if critical data missing
```

### Evidence Chain Tracking

**Evidence Structure:**

```python
class EvidenceChain:
    def __init__(self):
        self.evidence = {
            "circle_of_competence": [],
            "economic_moat": {
                "brand_power": [],
                "network_effects": [],
                "switching_costs": [],
                "cost_advantages": [],
                "intangible_assets": []
            },
            "management_quality": {
                "competence": [],
                "integrity": [],
                "shareholder_alignment": [],
                "capital_allocation": []
            },
            "owner_earnings": [],
            "roic": [],
            "valuation": [],
            "risks": [],
            "sharia_compliance": []
        }
    
    def add_evidence(self, category, subcategory, evidence_item):
        """
        evidence_item = {
            "source": "10-K Risk Factors",
            "finding": "Company faces intense competition from Amazon in cloud services",
            "implication": "Margin pressure risk",
            "confidence": "High",
            "timestamp": "2024-10-29T10:30:00"
        }
        """
        if subcategory:
            self.evidence[category][subcategory].append(evidence_item)
        else:
            self.evidence[category].append(evidence_item)
    
    def get_evidence_quality(self, category):
        """
        Assess evidence sufficiency for a category
        Returns: "Sufficient" | "Partial" | "Insufficient"
        """
        evidence_count = count_evidence(category)
        source_diversity = count_unique_sources(category)
        
        if evidence_count >= 3 and source_diversity >= 2:
            return "Sufficient"
        elif evidence_count >= 2:
            return "Partial"
        else:
            return "Insufficient"
```

**Evidence Quality Assessment:**

- **High Confidence:** Multiple independent sources confirm same finding
- **Medium Confidence:** Single reliable source or multiple sources with minor conflicts
- **Low Confidence:** Limited data, conflicting sources, or reliance on inferences

### When to Stop Investigating

**Stopping Conditions:**

**1. Sufficient Evidence Threshold Reached:**
```python
stopping_criteria = {
    "business_understanding": evidence_chain.get_quality("circle_of_competence") == "Sufficient",
    "moat_assessment": at_least_2_moat_types_evaluated(),
    "management_evaluation": all_4_management_dimensions_assessed(),
    "financial_analysis": owner_earnings_and_roic_calculated(),
    "valuation": intrinsic_value_range_determined(),
    "risk_assessment": top_3_risks_identified(),
    "sharia_compliance": compliance_verified()
}

if all(stopping_criteria.values()):
    proceed_to_final_decision()
```

**2. Clear Disqualification Found:**
```python
early_exit_triggers = [
    "Business model outside circle of competence",
    "ROIC <10% consistently (no moat)",
    "Management integrity issues (SEC violations, accounting scandals)",
    "Overleveraged (Debt/Equity >3, unstable)",
    "Sharia non-compliant (debt >33% assets)",
    "Fatal business risks (bankruptcy risk, obsolete product)"
]

if any_trigger_found(early_exit_triggers):
    issue_avoid_decision_with_reason()
```

**3. Maximum Investigation Depth:**
```python
if tool_call_count >= 20:
    # Prevent infinite investigation loops
    synthesize_available_evidence()
    flag_incomplete_analysis()
    issue_decision_with_caveats()
```

**4. Diminishing Returns:**
```
Agent reasoning: "We've confirmed wide moat through 5 different lenses,
excellent management through 10+ years of track record, ROIC >25% for
a decade, and 40% margin of safety. Additional searches aren't changing
the conclusion. Time to issue BUY recommendation."
```

### Investigation Flow Control

```python
class InvestigationController:
    def __init__(self, ticker):
        self.ticker = ticker
        self.phase = "initial_screening"
        self.evidence_chain = EvidenceChain()
        self.tool_call_count = 0
        self.max_tool_calls = 20
    
    def should_continue(self):
        """Determine if investigation should continue"""
        # Check stopping conditions
        if self.tool_call_count >= self.max_tool_calls:
            return False, "Maximum investigation depth reached"
        
        if self.has_early_disqualification():
            return False, self.get_disqualification_reason()
        
        if self.has_sufficient_evidence():
            return False, "Sufficient evidence collected"
        
        return True, None
    
    def get_next_action(self):
        """Agent decides next action based on current state"""
        if self.phase == "initial_screening":
            return self.initial_screening_actions()
        elif self.phase == "business_understanding":
            return self.business_understanding_actions()
        # ... etc for each phase
    
    def transition_phase(self):
        """Move to next investigation phase"""
        phase_sequence = [
            "initial_screening",
            "business_understanding",
            "moat_assessment",
            "management_evaluation",
            "financial_analysis",
            "valuation",
            "risk_assessment",
            "sharia_compliance",
            "final_synthesis"
        ]
        current_index = phase_sequence.index(self.phase)
        if current_index < len(phase_sequence) - 1:
            self.phase = phase_sequence[current_index + 1]
```

---

## 4. Tool Ecosystem

### Tool Interface

**Base Tool Class** (defined in `src/tools/base.py`):

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class Tool(ABC):
    """
    Abstract base class for all tools in the basīrah system.
    Each tool provides a specific capability (data retrieval, computation, etc.)
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique identifier for the tool.
        Used by agent to reference tool in decision making.
        
        Returns:
            str: Tool name (e.g., "gurufocus_tool")
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Human-readable description of tool capabilities.
        Used by agent to understand when to use this tool.
        
        Returns:
            str: Description including use cases and capabilities
        """
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        JSON schema defining tool input parameters.
        Used for validation and agent understanding of required inputs.
        
        Returns:
            dict: JSON schema with parameter definitions
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.
        
        Args:
            **kwargs: Parameters matching the tool's parameter schema
        
        Returns:
            dict: Standardized response format:
                {
                    "success": bool,
                    "data": Any,  # Tool-specific output
                    "error": str | None  # Error message if success=False
                }
        """
        pass
```

### Tool Registry Pattern

**Registry Implementation:**

```python
class ToolRegistry:
    """
    Central registry for all available tools.
    Provides tool discovery and access for the agent.
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool in the registry"""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Tool:
        """Retrieve a specific tool by name"""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        return self._tools[name]
    
    def list_tools(self) -> list[str]:
        """Get list of all registered tool names"""
        return list(self._tools.keys())
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all tools for agent context"""
        return {
            name: tool.description
            for name, tool in self._tools.items()
        }
    
    def get_tool_schemas(self) -> Dict[str, Dict]:
        """Get parameter schemas for all tools"""
        return {
            name: {
                "description": tool.description,
                "parameters": tool.parameters
            }
            for name, tool in self._tools.items()
        }
```

**Tool Registration at Startup:**

```python
# src/tools/__init__.py
from .gurufocus_tool import GuruFocusTool
from .sec_filing_tool import SECFilingTool
from .calculator_tool import CalculatorTool
from .web_search_tool import WebSearchTool
from .base import ToolRegistry

def initialize_tools() -> ToolRegistry:
    """Initialize and register all tools"""
    registry = ToolRegistry()
    
    # Register all tools
    registry.register(GuruFocusTool())
    registry.register(SECFilingTool())
    registry.register(CalculatorTool())
    registry.register(WebSearchTool())
    
    return registry
```

### How Agent Discovers Available Tools

**At Agent Initialization:**

```python
def create_agent_system_prompt(tool_registry: ToolRegistry) -> str:
    """
    Generate system prompt including tool descriptions
    """
    buffett_principles = load_file("docs/BUFFETT_PRINCIPLES.md")
    tool_descriptions = tool_registry.get_tool_schemas()
    
    system_prompt = f"""
    You are an autonomous investment analyst using Warren Buffett's principles.
    
    {buffett_principles}
    
    AVAILABLE TOOLS:
    
    {format_tool_descriptions(tool_descriptions)}
    
    When you need information, select the appropriate tool and call it with
    the required parameters. Analyze results and continue investigation.
    """
    
    return system_prompt

def format_tool_descriptions(tool_schemas: Dict) -> str:
    """Format tool descriptions for system prompt"""
    formatted = []
    for name, schema in tool_schemas.items():
        formatted.append(f"""
        Tool: {name}
        Description: {schema['description']}
        Parameters: {json.dumps(schema['parameters'], indent=2)}
        """)
    return "\n".join(formatted)
```

**Tool Discovery During Investigation:**

The agent has access to tool descriptions in its system prompt and can reason about which tool to use based on:

1. **Current investigation needs**
2. **Tool capabilities described in schema**
3. **Previous successful tool usage patterns**
4. **Parameter requirements**

### Tool Calling Mechanism

**Claude Function Calling Format:**

```python
# Agent generates function call in this format
tool_call = {
    "name": "gurufocus_tool",
    "parameters": {
        "ticker": "AAPL",
        "endpoint": "financials"
    }
}

# Orchestrator processes the call
def process_tool_call(tool_call: Dict, tool_registry: ToolRegistry) -> Dict:
    """
    Execute tool call and return results
    """
    tool_name = tool_call["name"]
    parameters = tool_call["parameters"]
    
    # Get tool from registry
    tool = tool_registry.get_tool(tool_name)
    
    # Execute with parameters
    result = tool.execute(**parameters)
    
    # Return result to agent
    return result
```

**Execution Flow:**

```
1. Agent (Claude 4.5 Sonnet) generates function call:
   {
     "name": "gurufocus_tool",
     "parameters": {"ticker": "AAPL", "endpoint": "summary"}
   }

2. Orchestrator receives call and validates parameters

3. Orchestrator retrieves tool from registry

4. Tool executes:
   - Makes API call to GuruFocus
   - Handles errors (retry logic, etc.)
   - Formats response in standard format

5. Result returned to agent:
   {
     "success": true,
     "data": {
       "company": "Apple Inc",
       "roic": 0.32,
       "financial_strength_score": 8,
       ...
     },
     "error": null
   }

6. Agent analyzes result and decides next action
```

### Result Handling

**Standard Response Format:**

All tools return responses in this format:

```python
{
    "success": bool,       # True if tool executed successfully
    "data": Any,          # Tool-specific data (dict, list, float, etc.)
    "error": str | None   # Error message if success=False
}
```

**Agent Result Processing:**

```python
# Agent receives tool result
result = execute_tool("gurufocus_tool", {"ticker": "AAPL", "endpoint": "summary"})

# Agent reasoning about result
if result["success"]:
    data = result["data"]
    # Extract relevant information
    roic = data["profitability"]["roic"]
    
    # Agent internal reasoning:
    # "ROIC is 32%, which exceeds the 15% threshold for quality businesses.
    #  This is a positive signal for economic moat. I should investigate
    #  what drives this high ROIC - is it brand power, network effects, or
    #  cost advantages? Next action: web search for competitive advantages."
    
    evidence_chain.add_evidence(
        category="roic",
        subcategory=None,
        evidence={
            "source": "GuruFocus Summary",
            "finding": f"ROIC: {roic}%",
            "implication": "Significantly above 15% threshold, suggests strong moat",
            "confidence": "High"
        }
    )
else:
    # Handle error
    error_message = result["error"]
    # Agent decides: retry, use alternative tool, or note limitation
```

**Error Handling Strategy:**

```python
def handle_tool_error(tool_name: str, error: str, attempt: int) -> str:
    """
    Agent's strategy for handling tool errors
    """
    if "rate limit" in error.lower():
        # Rate limit: wait and retry
        return "wait_and_retry"
    
    elif "not found" in error.lower() or "invalid ticker" in error.lower():
        # Invalid input: don't retry, note in analysis
        return "skip_and_continue"
    
    elif "timeout" in error.lower() or "network" in error.lower():
        # Network issue: retry with exponential backoff
        if attempt < 3:
            return "retry_with_backoff"
        else:
            return "skip_and_continue"
    
    elif "special value" in error.lower():
        # Data not available (9999, 10000 codes)
        return "try_alternative_source"
    
    else:
        # Unknown error: try once more, then skip
        if attempt < 2:
            return "retry_once"
        else:
            return "skip_and_continue"
```

---

## 5. Investigation Workflow

### Complete 8-Phase Investigation Process

The agent follows a systematic investigation workflow that adapts based on findings at each phase.

**Phase Sequence:**

1. Initial Assessment → Quick screening
2. Business Understanding → Deep dive into business model
3. Moat Assessment → Identify competitive advantages
4. Management Evaluation → Assess leadership quality
5. Financial Analysis → Calculate Owner Earnings & ROIC
6. Valuation → Determine intrinsic value & margin of safety
7. Risk Assessment → Identify top risks
8. Sharia Compliance → Verify Islamic finance compliance
9. Final Synthesis → Generate investment thesis

**Estimated Total Duration:** 40-70 minutes (15-20 tool calls)

**See Section 3 (ReAct Reasoning Loop) for detailed phase breakdowns with specific tool usage patterns, decision gates, and evidence requirements for each investigation phase.**

---

## 6. Extended Thinking Strategy

### When to Use Extended Thinking

Extended thinking mode is activated for:

**1. Complex Multi-Factor Decisions:**
```python
extended_thinking_triggers = [
    "Initial moat assessment (weighing 5 moat types)",
    "Management quality synthesis (4 dimensions)",
    "Valuation scenario analysis (conservative, base, optimistic)",
    "Final investment decision (synthesizing all evidence)",
    "Risk-reward tradeoff evaluation",
    "Conflicting evidence resolution"
]
```

**2. Deep Calculations:**
```python
calculation_triggers = [
    "DCF valuation with multiple scenarios",
    "ROIC consistency analysis (10-year trend + std dev)",
    "Working capital change interpretation",
    "Margin of safety calculations across scenarios"
]
```

**3. Ambiguous Situations:**
```python
ambiguity_triggers = [
    "Mixed signals (high ROIC but declining margins)",
    "Conflicting sources (different ROIC calculations)",
    "Recent major changes (new CEO, business pivot)",
    "Industry disruption assessment"
]
```

### Token Budget Management

**Total Analysis Budget:** 50-100K tokens

**Breakdown:**

```
System Prompt:                    8-10K tokens (fixed)
Tool Calls & Results:            30-50K tokens (variable by investigation depth)
Extended Thinking:               10-20K tokens (critical reasoning points)
Response Generation:             10-20K tokens (final thesis)
────────────────────────────────────────────────────────────
TOTAL:                           58-100K tokens (well within 200K limit)
```

**Extended Thinking Allocation:**

```python
extended_thinking_budget = {
    "moat_assessment": "3-5K tokens (weighing evidence across 5 moat types)",
    "management_synthesis": "2-3K tokens (4-dimension assessment)",
    "valuation_scenarios": "3-5K tokens (DCF with sensitivities)",
    "final_decision": "5-10K tokens (comprehensive synthesis)",
    "contingent_reasoning": "2-5K tokens (if/when needed for conflicts)"
}
```

**Budget Management Strategy:**

```python
def manage_token_budget(current_usage, remaining_budget):
    """
    Dynamically adjust investigation depth based on budget
    """
    if remaining_budget < 30_000:
        # Low budget: focus on essentials
        return "prioritize_critical_findings_only"
    
    elif remaining_budget < 60_000:
        # Medium budget: standard investigation
        return "standard_depth"
    
    else:
        # High budget: can do deep dives
        return "deep_investigation_allowed"
```

### Quality vs Cost Tradeoff

**Cost Structure:**

```
Input tokens:  $0.003 per 1K tokens
Output tokens: $0.015 per 1K tokens

Typical analysis:
  Input:  60K tokens × $0.003 = $0.18
  Output: 30K tokens × $0.015 = $0.45
  ──────────────────────────────────
  Total:  ~$0.60 per analysis

Extended thinking-heavy analysis:
  Input:  80K tokens × $0.003 = $0.24
  Output: 50K tokens × $0.015 = $0.75
  ──────────────────────────────────
  Total:  ~$1.00 per analysis

With retry/error handling:
  ~$2-5 per complete analysis (acceptable target)
```

**Quality Benefits:**

```
WITHOUT extended thinking:
  - Faster but shallower analysis
  - May miss subtle red flags
  - Less nuanced moat assessment
  - Weaker thesis reasoning
  - Cost: $0.50-1.00 per analysis

WITH extended thinking:
  - Deeper reasoning chains
  - Better evidence synthesis
  - Stronger thesis quality
  - Catches subtle warning signs
  - Cost: $2-5 per analysis
  
DECISION: Use extended thinking (quality > speed for investment decisions)
```

**When to Economize:**

```python
def should_use_extended_thinking(investigation_phase, evidence_clarity):
    """
    Decide whether to invoke extended thinking
    """
    if investigation_phase == "initial_screening" and evidence_clarity == "clear_avoid":
        # Don't waste tokens on obvious AVOID
        return False
    
    elif investigation_phase in ["moat_assessment", "final_decision"]:
        # Always use extended thinking for critical decisions
        return True
    
    elif evidence_clarity == "highly_ambiguous":
        # Use extended thinking to resolve ambiguity
        return True
    
    else:
        # Standard reasoning sufficient
        return False
```

---

## 7. Error Handling & Logging

### API Failure Recovery

**Retry Logic with Exponential Backoff:**

```python
import time
from typing import Dict, Any, Optional

class RetryStrategy:
    """
    Implements exponential backoff retry logic for API calls
    """
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def execute_with_retry(self, func, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute function with retry logic
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                
                # Check for rate limit response
                if self.is_rate_limited(result):
                    wait_time = self.calculate_backoff(attempt)
                    logger.warning(f"Rate limited. Waiting {wait_time}s before retry {attempt+1}/{self.max_retries}")
                    time.sleep(wait_time)
                    continue
                
                # Success
                return {
                    "success": True,
                    "data": result,
                    "error": None,
                    "attempts": attempt + 1
                }
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"Attempt {attempt+1}/{self.max_retries} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    wait_time = self.calculate_backoff(attempt)
                    time.sleep(wait_time)
                else:
                    # Final attempt failed
                    return {
                        "success": False,
                        "data": None,
                        "error": f"Failed after {self.max_retries} attempts: {last_error}",
                        "attempts": self.max_retries
                    }
        
        # Should not reach here
        return {
            "success": False,
            "data": None,
            "error": "Unexpected retry loop exit",
            "attempts": self.max_retries
        }
    
    def calculate_backoff(self, attempt: int) -> float:
        """Exponential backoff: 1s, 2s, 4s, 8s, ..."""
        return self.base_delay * (2 ** attempt)
    
    def is_rate_limited(self, result) -> bool:
        """Check if response indicates rate limiting"""
        if isinstance(result, dict):
            if result.get("status_code") == 429:
                return True
            if "rate limit" in str(result.get("error", "")).lower():
                return True
        return False
```

**API-Specific Error Handling:**

```python
class GuruFocusErrorHandler:
    """Handle GuruFocus-specific errors"""
    
    @staticmethod
    def handle_error(error: str, response_data: Dict) -> Dict:
        """
        Parse GuruFocus errors and determine recovery strategy
        """
        # Special numeric codes
        if response_data and isinstance(response_data, dict):
            for key, value in response_data.items():
                if value == 9999:
                    return {
                        "error_type": "data_not_available",
                        "recovery": "try_alternative_source",
                        "message": f"{key} not available (code 9999)"
                    }
                elif value == 10000:
                    return {
                        "error_type": "special_case",
                        "recovery": "interpret_as_zero_or_na",
                        "message": f"{key} special case (code 10000)"
                    }
        
        # Rate limiting
        if "rate limit" in error.lower():
            return {
                "error_type": "rate_limit",
                "recovery": "exponential_backoff",
                "message": "GuruFocus rate limit exceeded"
            }
        
        # Invalid ticker
        if "not found" in error.lower() or "invalid" in error.lower():
            return {
                "error_type": "invalid_input",
                "recovery": "validate_ticker",
                "message": "Ticker not found in GuruFocus"
            }
        
        # Default
        return {
            "error_type": "unknown",
            "recovery": "retry_once",
            "message": f"GuruFocus error: {error}"
        }

class SECEdgarErrorHandler:
    """Handle SEC EDGAR-specific errors"""
    
    @staticmethod
    def handle_error(error: str, response) -> Dict:
        """
        Parse SEC EDGAR errors
        """
        # Missing User-Agent header
        if "403" in error or "forbidden" in error.lower():
            return {
                "error_type": "missing_user_agent",
                "recovery": "add_user_agent_header",
                "message": "SEC EDGAR requires User-Agent header"
            }
        
        # Rate limiting (10 req/sec)
        if "429" in error or "rate limit" in error.lower():
            return {
                "error_type": "rate_limit",
                "recovery": "wait_110ms",  # 9 req/sec safely under limit
                "message": "SEC EDGAR rate limit (10 req/sec)"
            }
        
        # CIK not found
        if "404" in error:
            return {
                "error_type": "not_found",
                "recovery": "verify_cik_format",
                "message": "CIK not found (ensure 10-digit format with leading zeros)"
            }
        
        return {
            "error_type": "unknown",
            "recovery": "retry_once",
            "message": f"SEC EDGAR error: {error}"
        }
```

### Missing Data Handling

**Fallback Calculation Strategies:**

```python
class DataFallbackStrategy:
    """
    Handle missing financial data with fallback approaches
    """
    
    @staticmethod
    def calculate_owner_earnings_fallback(financials: Dict) -> Optional[float]:
        """
        Attempt Owner Earnings calculation with data availability checks
        """
        # Try primary calculation
        if all(k in financials for k in ["net_income", "da", "capex"]):
            oe = financials["net_income"] + financials["da"] - financials["capex"]
            
            # Subtract working capital change if available
            if "wc_change" in financials:
                oe -= financials["wc_change"]
            
            return oe
        
        # Fallback 1: Use Free Cash Flow as proxy
        if "free_cash_flow" in financials:
            logger.warning("Using FCF as Owner Earnings proxy (insufficient data)")
            return financials["free_cash_flow"]
        
        # Fallback 2: Operating Cash Flow - Capex
        if all(k in financials for k in ["operating_cash_flow", "capex"]):
            logger.warning("Using OCF - CapEx as Owner Earnings proxy")
            return financials["operating_cash_flow"] - financials["capex"]
        
        # No viable calculation
        logger.error("Insufficient data to calculate Owner Earnings")
        return None
    
    @staticmethod
    def calculate_roic_fallback(financials: Dict) -> Optional[float]:
        """
        Attempt ROIC calculation with data availability checks
        """
        # Try primary calculation
        if all(k in financials for k in ["operating_income", "tax_rate", "invested_capital"]):
            nopat = financials["operating_income"] * (1 - financials["tax_rate"])
            roic = nopat / financials["invested_capital"]
            return roic
        
        # Fallback 1: Use pre-calculated ROIC from GuruFocus
        if "roic_precalculated" in financials:
            logger.warning("Using GuruFocus pre-calculated ROIC")
            return financials["roic_precalculated"]
        
        # Fallback 2: ROE as rough proxy (less accurate)
        if "roe" in financials:
            logger.warning("Using ROE as ROIC proxy (less accurate)")
            return financials["roe"]
        
        # No viable calculation
        logger.error("Insufficient data to calculate ROIC")
        return None
```

### Tool Error Handling

**Graceful Degradation:**

```python
class ToolExecutor:
    """
    Execute tools with comprehensive error handling
    """
    
    def execute_tool_safe(self, tool_name: str, parameters: Dict) -> Dict:
        """
        Execute tool with error handling and logging
        """
        logger.info(f"Executing {tool_name} with params: {parameters}")
        
        try:
            # Get tool from registry
            tool = self.tool_registry.get_tool(tool_name)
            
            # Validate parameters
            validation_result = self.validate_parameters(tool, parameters)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "data": None,
                    "error": f"Invalid parameters: {validation_result['errors']}"
                }
            
            # Execute with retry logic
            retry_strategy = RetryStrategy(max_retries=3)
            result = retry_strategy.execute_with_retry(
                tool.execute,
                **parameters
            )
            
            # Log result
            if result["success"]:
                logger.info(f"{tool_name} succeeded after {result['attempts']} attempts")
            else:
                logger.error(f"{tool_name} failed: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.exception(f"Unexpected error executing {tool_name}")
            return {
                "success": False,
                "data": None,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    def validate_parameters(self, tool: Tool, parameters: Dict) -> Dict:
        """Validate parameters against tool schema"""
        schema = tool.parameters
        errors = []
        
        # Check required parameters
        required = schema.get("required", [])
        for param in required:
            if param not in parameters:
                errors.append(f"Missing required parameter: {param}")
        
        # Check parameter types
        properties = schema.get("properties", {})
        for param, value in parameters.items():
            if param in properties:
                expected_type = properties[param].get("type")
                if not self.type_matches(value, expected_type):
                    errors.append(f"Parameter {param} has wrong type (expected {expected_type})")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
```

### Investigation Trace Logging

**Comprehensive Logging System:**

```python
import logging
import json
from datetime import datetime
from typing import Dict, Any, List

class InvestigationLogger:
    """
    Logs complete investigation trace for transparency and debugging
    """
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.investigation_id = f"{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.trace = []
        
        # Setup file logger
        self.logger = self.setup_logger()
    
    def setup_logger(self) -> logging.Logger:
        """Setup investigation-specific logger"""
        logger = logging.getLogger(self.investigation_id)
        logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(f"logs/investigations/{self.investigation_id}.log")
        fh.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        return logger
    
    def log_phase_start(self, phase: str):
        """Log investigation phase start"""
        self.logger.info(f"=== PHASE START: {phase} ===")
        self.trace.append({
            "type": "phase_start",
            "phase": phase,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_tool_call(self, tool_name: str, parameters: Dict, result: Dict):
        """Log tool execution"""
        self.logger.info(f"Tool Call: {tool_name}")
        self.logger.debug(f"Parameters: {json.dumps(parameters, indent=2)}")
        self.logger.debug(f"Result: {json.dumps(result, indent=2)}")
        
        self.trace.append({
            "type": "tool_call",
            "tool": tool_name,
            "parameters": parameters,
            "success": result.get("success"),
            "error": result.get("error"),
            "timestamp": datetime.now().isoformat()
        })
    
    def log_reasoning(self, reasoning: str):
        """Log agent's reasoning"""
        self.logger.info(f"Agent Reasoning: {reasoning}")
        self.trace.append({
            "type": "reasoning",
            "content": reasoning,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_evidence(self, category: str, evidence: Dict):
        """Log evidence collection"""
        self.logger.info(f"Evidence [{category}]: {evidence['finding']}")
        self.trace.append({
            "type": "evidence",
            "category": category,
            "evidence": evidence,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_decision(self, decision: str, reasoning: str, confidence: str):
        """Log final investment decision"""
        self.logger.info(f"=== FINAL DECISION: {decision} ({confidence} confidence) ===")
        self.logger.info(f"Reasoning: {reasoning}")
        
        self.trace.append({
            "type": "final_decision",
            "decision": decision,
            "reasoning": reasoning,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        })
    
    def export_trace(self) -> Dict:
        """Export complete investigation trace"""
        return {
            "investigation_id": self.investigation_id,
            "ticker": self.ticker,
            "trace": self.trace,
            "duration": self.calculate_duration(),
            "tool_calls": self.count_tool_calls(),
            "phases_completed": self.list_phases_completed()
        }
    
    def calculate_duration(self) -> float:
        """Calculate total investigation duration in seconds"""
        if len(self.trace) < 2:
            return 0.0
        start_time = datetime.fromisoformat(self.trace[0]["timestamp"])
        end_time = datetime.fromisoformat(self.trace[-1]["timestamp"])
        return (end_time - start_time).total_seconds()
    
    def count_tool_calls(self) -> int:
        """Count total tool calls"""
        return len([t for t in self.trace if t["type"] == "tool_call"])
    
    def list_phases_completed(self) -> List[str]:
        """List all phases completed"""
        return [t["phase"] for t in self.trace if t["type"] == "phase_start"]
```

### Reasoning Transparency

**Exposing Reasoning Chain to User:**

The final investment thesis includes a "Reasoning Chain" section that shows the agent's investigation path:

```markdown
## Investigation Reasoning Chain

### Phase 1: Initial Screening
**Tool Calls:** GuruFocus /summary, /keyratios  
**Key Finding:** ROIC 32% (well above 15% threshold)  
**Reasoning:** High ROIC suggests strong competitive advantage. Proceed with deep investigation.

### Phase 2: Business Understanding
**Tool Calls:** SEC 10-K Business section, Web Search "Apple business model"  
**Key Finding:** Clear business model - hardware ecosystem + services  
**Reasoning:** Business is within circle of competence. Revenue sources are predictable.

[... continues for all phases ...]

### Final Decision: WATCH
**Reasoning:** Company meets all fundamental criteria (wide moat, excellent management, world-class ROIC), but current valuation provides only 10% margin of safety vs. required 20-25% for wide moat companies. Recommend watching for better entry point at $156 or below (20% margin vs. base case intrinsic value of $195/share).
```

---

## 8. Output Generation

The agent generates a comprehensive investment thesis document following a standardized format that provides complete transparency into the analysis process.

**Investment Thesis Template:** See `docs/INVESTMENT_THESIS_TEMPLATE.md` for complete output format specification including:

- Executive Summary with recommendation, confidence, target price
- Business Understanding section
- Economic Moat Analysis with scoring
- Management Quality Assessment
- Financial Analysis (Owner Earnings, ROIC, Debt)
- Valuation Analysis with DCF and margin of safety
- Risk Assessment with top 3 risks
- Sharia Compliance Verification
- Investment Decision with rationale
- Monitoring Plan
- Investigation Summary with tool usage statistics

**Output Format:** Markdown document (~10-20KB)  
**Location:** Saved to user-specified directory  
**Includes:** Full reasoning chain, evidence citations, confidence levels

---

## 9. Sharia Compliance Integration

### When to Check

**Timing in Investigation Flow:**

```
Initial Screening → Business Understanding → Moat → Management → Financial Analysis
→ Valuation → Risk Assessment → **SHARIA COMPLIANCE** → Final Decision
```

Sharia compliance is checked **after fundamental analysis is complete** but **before final decision**, because:

1. No point checking Sharia if business fails fundamental criteria
2. Sharia non-compliance is a **hard override** - even if BUY signal, becomes AVOID
3. Efficient use of tool calls (skip if already AVOIDing)

### How to Check

**Tool Usage:**

```python
# Calculator Tool with sharia_compliance_check calculation
result = calculator_tool.execute(
    calculation="sharia_compliance_check",
    data={
        "total_debt": 107_000_000_000,
        "total_assets": 353_000_000_000,
        "cash_and_liquid_assets": 30_000_000_000,
        "market_cap": 2_750_000_000_000,
        "accounts_receivable": 60_000_000_000,
        "business_activities": [
            "consumer_electronics",
            "software",
            "services",
            "wearables"
        ]
    }
)
```

### Screening Criteria

**Financial Ratios (AAOIFI Standards):**

```python
sharia_ratios = {
    "debt_to_assets": {
        "formula": "Total Debt / Total Assets",
        "threshold": 0.33,  # 33%
        "rationale": "Ensures company not overleveraged with interest-bearing debt"
    },
    
    "liquid_assets_to_market_cap": {
        "formula": "(Cash + Receivables + Interest-bearing Securities) / Market Cap",
        "threshold": 0.33,  # 33%
        "rationale": "Ensures company's value not primarily interest-bearing assets"
    },
    
    "receivables_to_market_cap": {
        "formula": "Accounts Receivable / Market Cap",
        "threshold": 0.50,  # 50%
        "rationale": "Ensures company not primarily a lending operation"
    }
}

# All three ratios must PASS for compliance
```

**Business Activity Screen:**

```python
prohibited_activities = [
    "alcohol_production",         # Alcoholic beverages
    "gambling",                   # Casinos, lotteries, betting
    "pork_products",              # Pork processing
    "conventional_banking",       # Interest-based financial services
    "insurance",                  # Conventional insurance (not takaful)
    "adult_entertainment",        # Pornography, nightclubs
    "tobacco",                    # Tobacco products
    "weapons_munitions"           # Weapons manufacturing (not defense)
]

# Company must have 0% revenue from prohibited activities
# Some scholars allow up to 5% if unavoidable and donated
```

### Impact on Recommendation

**Decision Override Logic:**

```python
def final_investment_decision_with_sharia(analysis: Dict) -> Dict:
    """
    Generate final decision with Sharia compliance override
    """
    # Perform fundamental analysis
    fundamental_decision = analyze_fundamentals(analysis)
    # fundamental_decision could be BUY, WATCH, or AVOID
    
    # Check Sharia compliance
    sharia_result = analysis["sharia_compliance"]
    
    # Hard override: Sharia non-compliance → AVOID
    if sharia_result["status"] == "NON-COMPLIANT":
        return {
            "decision": "AVOID",
            "reason": f"Sharia non-compliant: {sharia_result['reason']}",
            "fundamental_signal": fundamental_decision["decision"],
            "note": "Company may be fundamentally sound but does not meet Islamic finance requirements",
            "confidence": "High"
        }
    
    # If Sharia compliant, proceed with fundamental decision
    return fundamental_decision
```

**Example Scenario:**

```
Company: XYZ Corp
Fundamental Analysis Results:
  - Wide Moat: ✓
  - Excellent Management: ✓
  - ROIC >15%: ✓ (22%)
  - Margin of Safety: ✓ (28%)
  → Fundamental Signal: BUY

Sharia Compliance Check:
  - Debt/Assets: 38% > 33% threshold ✗
  → Sharia Status: NON-COMPLIANT

Final Decision: AVOID
Reason: "Sharia non-compliant (Debt/Assets 38% exceeds 33% threshold). 
         Company is fundamentally strong (would be BUY based on Buffett 
         criteria alone), but does not meet Islamic finance requirements."
```

### Cross-Reference with Zoya App

For validation and confirmation, users can cross-reference agent's Sharia compliance determination with established screening services:

**Zoya App Integration (Manual for MVP):**

```
After agent determines Sharia compliance status, recommend user verify using:

1. Zoya App (zoya.finance)
   - Search company ticker
   - Check "Compliance Status"
   - Compare ratios to agent's calculations
   
2. Musaffa App (musaffa.com)
   - Alternative Islamic screening service
   - Provides detailed ratio breakdown
   
3. AAOIFI Standards
   - Official accounting standards for Islamic finance
   - Reference for edge cases

Note: Agent uses AAOIFI standards, which are most widely accepted.
Some services may use slightly different thresholds or methodologies.
```

**Future Enhancement:** Direct API integration with Zoya for real-time validation.

---

## Conclusion

This architecture document defines a complete autonomous investment analysis system that:

1. **Operates Independently:** Agent makes its own investigation decisions based on evidence
2. **Reasons Transparently:** Extended thinking and logging expose complete reasoning chain
3. **Uses Tools Systematically:** Clear patterns for when and how to use each tool
4. **Handles Errors Gracefully:** Comprehensive retry logic and fallback strategies
5. **Produces Quality Output:** Detailed investment theses with confidence levels
6. **Respects Constraints:** Sharia compliance as hard requirement for Abu Dhabi context

**Key Design Principles:**
- **Quality over Speed:** $2-5 per analysis is acceptable for deep, accurate analysis
- **Transparency First:** All reasoning visible to user
- **Evidence-Based:** Every claim backed by specific sources
- **Intellectually Honest:** Admits limitations and uncertainties
- **Buffett-Faithful:** Strict adherence to value investing principles

**Cost Efficiency:**
- Target: $2-5 per complete analysis
- Early AVOID decisions: $0.50-1.00 (save on unnecessary deep investigation)
- Complex deep dives: $3-5 (justified by quality and decision importance)

**Ready for Sprint 3 Implementation:** This architecture provides complete specification for building the agent core and integrating all tools.

---

**Document Complete**  
**File:** `docs/ARCHITECTURE.md`  
**Size:** ~73KB  
**Sections:** 9 major sections covering all required architecture components  
**Status:** PRODUCTION-READY
