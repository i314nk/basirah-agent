# Lessons Learned

basīrah is archived as an educational prototype and portfolio artifact. This note explains what the project demonstrated, where it became too broad, and how it informed the next iteration.

## What worked

### 1. Real AI-agent integration

The project moved beyond a single prompt and explored an actual tool-using research workflow:

- SEC filing retrieval and section extraction
- financial-data access through a configured provider
- web-search integration
- calculator tools for financial analysis
- LLM-driven synthesis of a structured investment thesis

This made the project valuable as an applied AI-agent experiment rather than just a demo script.

### 2. Finance-domain grounding

The system connected AI tooling to a finance use case:

- business model analysis
- moat/competitive-position review
- management and risk assessment
- conservative valuation concepts
- Sharia-aware screening considerations

That domain grounding made the project more meaningful than a generic chatbot.

### 3. Long-document and context experiments

The project explored practical issues that appear in real AI systems:

- large SEC filings
- context-window limits
- summarization strategies
- multi-year analysis
- cost estimation
- tool failures and external API dependency

These are useful lessons for future AI-infrastructure and AI-operations work.

## What became too broad

The project accumulated several product directions at once:

- investment analyst persona
- SEC filing analysis
- Sharia screening
- Streamlit UI
- PostgreSQL analysis history
- search and storage
- cost tracking
- translation
- portfolio-style tracking

Each feature was individually reasonable, but together they made the project harder to maintain and harder to explain as a clean portfolio artifact.

## Key design lessons

### Keep the core workflow small

The most important capability is:

```text
company input -> evidence gathering -> structured research memo
```

Everything else should support that core workflow or be postponed.

### Avoid overclaiming

The project should be described as an educational prototype, not as a production investment platform. Public-facing language should avoid implying:

- guaranteed analysis quality
- investment advice
- trading recommendations
- production readiness
- Sharia certification

### Prefer transparent local outputs

Markdown reports, local JSON/YAML files, and simple indexes are easier to inspect, demo, and explain than heavy persistence layers. For a portfolio project, clarity is often more valuable than architectural complexity.

### Treat automation as optional

Scheduled tasks, background jobs, and persistent memory add operational complexity. They should only be added after the manual workflow is reliable and easy to test.

## Successor direction

The next iteration should be smaller and cleaner:

```text
ticker/company
  -> business analyst agent
  -> financial analyst agent
  -> risk/Shariah/governance agent
  -> synthesis agent
  -> markdown research memo
```

Recommended scope for a successor project:

- manual company analysis
- simple watchlist and holdings context
- local-first storage
- structured markdown output
- clear architecture diagram
- explicit limitations and disclaimers

Postpone:

- broker integration
- automated trading
- complex database memory
- scheduled monitoring
- portfolio optimization
- production deployment

## Portfolio positioning

A fair description of this repository:

> basīrah is an archived v1 AI investment research prototype exploring SEC filing analysis, LLM tool use, Sharia-aware screening, Streamlit UI, and local research-history storage.

A fair description of the successor direction:

> A cleaner v2 multi-agent investment research workflow focused on specialist analysis agents, synthesis, watchlist/holdings context, and markdown memo generation.
