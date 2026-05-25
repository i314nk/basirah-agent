# basīrah - Archived AI Investment Research Agent

<div align="center">

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-archived-red.svg)

**An archived educational prototype for LLM-assisted investment research, SEC filing analysis, and Sharia-aware screening.**

[Overview](#overview) • [What It Demonstrates](#what-it-demonstrates) • [Architecture](#architecture) • [Quick Start](#quick-start) • [Project Status](#project-status)

</div>

---

## Overview

**basīrah** (Arabic: بَصِيرَة, meaning "insight" or "foresight") is an archived AI investment research prototype. It explored whether an LLM-based agent could gather evidence from company filings, financial-data tools, web research, and calculations to produce structured long-form investment research.

The project was built as a hands-on learning system at the intersection of:

- AI agents and tool use
- SEC filing ingestion and long-document analysis
- Value-investing research workflows
- Sharia-aware investment screening
- Streamlit-based research interfaces
- Local storage of generated analyses

This repository is preserved as a portfolio and learning artifact. It is not an active investment product and should not be used as financial advice.

---

## What It Demonstrates

### AI-agent workflow

- ReAct-style investigation loop for tool-assisted analysis
- Agent prompts for business quality, moat, management, valuation, and risk review
- LLM provider abstraction for Claude-based analysis
- Context-management experiments for long SEC filings

### Research tools

- SEC EDGAR filing retrieval and section extraction
- Financial-data integration through GuruFocus where configured
- Web-search tool integration
- Calculator utilities for financial analysis
- Sharia screening module based on common Islamic finance screening concepts

### Application layer

- Streamlit UI for running analyses and viewing results
- Cost-estimation and token-usage tracking experiments
- PostgreSQL-backed analysis history and search experiments
- Export paths for JSON and Markdown research outputs

---

## What This Project Is Not

basīrah is not:

- a registered investment advisor
- a trading bot
- a broker integration
- a production-grade financial platform
- a source of buy/sell instructions
- a substitute for qualified financial or Sharia review

The project is best understood as an educational AI research prototype and an earlier-generation system design experiment.

---

## Project Status

This project is **archived**.

Development concluded after the prototype demonstrated the core research workflow. Newer long-context and deep-research LLM capabilities reduced the need for a standalone single-agent research system, and the next iteration is being explored separately as a cleaner multi-agent workflow.

Current status:

- The repository is kept public as a portfolio artifact.
- The code may require API keys and local setup to run.
- Some modules reflect experimental phases rather than a polished product roadmap.
- The project is not being actively maintained as an investment application.

See also: [`docs/LESSONS_LEARNED.md`](docs/LESSONS_LEARNED.md).

---

## Architecture

High-level flow:

```text
User request / ticker
        |
        v
Agent orchestration
        |
        +--> SEC filing tool
        +--> financial data tool
        +--> web search tool
        +--> calculator tool
        |
        v
Research synthesis
        |
        v
Structured investment memo / exported analysis
```

Main areas:

```text
src/
  agent/      Agent orchestration, prompts, Sharia screener, translation
  tools/      SEC, GuruFocus, web-search, and calculator integrations
  llm/        LLM provider abstraction
  storage/    Analysis history and search experiments
  ui/         Streamlit application

docs/         Architecture, project vision, tool specs, API notes
examples/     Example scripts for running analyses and tools
tests/        Unit/integration-style tests and company-analysis experiments
```

For the original detailed architecture notes, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Quick Start

### Prerequisites

- Python 3.10+
- Anthropic API key for Claude-based analysis
- GuruFocus API key for some financial-data features, optional but useful
- PostgreSQL/Docker only if using the historical analysis database features

### Installation

```bash
git clone https://github.com/i314nk/basirah-agent.git
cd basirah-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add the API keys required for the features you want to run.

### Run the Streamlit UI

```bash
streamlit run src/ui/app.py
```

### Run an analysis from Python

```python
from src.agent.buffett_agent import WarrenBuffettAgent

agent = WarrenBuffettAgent()
result = agent.analyze_company("AAPL", deep_dive=True, years_to_analyze=3)

print(result["decision"])
print(result["thesis"])
```

---

## Documentation

Core docs:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - original detailed architecture notes
- [`docs/PROJECT_VISION.md`](docs/PROJECT_VISION.md) - original project vision and design intent
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) - development/setup notes
- [`docs/LESSONS_LEARNED.md`](docs/LESSONS_LEARNED.md) - retrospective and successor-project notes

Tool/API notes:

- [`docs/tool_specs/sec_filing_tool_spec.md`](docs/tool_specs/sec_filing_tool_spec.md)
- [`docs/tool_specs/gurufocus_tool_spec.md`](docs/tool_specs/gurufocus_tool_spec.md)
- [`docs/tool_specs/web_search_tool_spec.md`](docs/tool_specs/web_search_tool_spec.md)
- [`docs/tool_specs/calculator_tool_spec.md`](docs/tool_specs/calculator_tool_spec.md)
- [`docs/api_references/sec_edgar_api.md`](docs/api_references/sec_edgar_api.md)
- [`docs/api_references/gurufocus_api.md`](docs/api_references/gurufocus_api.md)
- [`docs/api_references/brave_search_api.md`](docs/api_references/brave_search_api.md)

---

## Testing

```bash
pytest tests/ -v
```

Some tests and example analyses depend on external APIs, configured environment variables, or local services. Treat the test suite as part of the archived prototype rather than a maintained CI guarantee.

---

## Successor Direction

basīrah informed a cleaner second-generation direction: a smaller multi-agent research workflow focused on role separation, synthesis, local-first watchlist/holdings context, and markdown memo generation.

The key lesson was scope control: the most useful portfolio version of this idea is not a full investment platform, but a clear and explainable AI research workflow.

---

## Disclaimer

This repository is for educational and research purposes only. It does not provide financial advice, investment recommendations, trading signals, or Sharia rulings. Always conduct independent due diligence and consult qualified professionals before making financial decisions.

---

## License

MIT License - see [`LICENSE`](LICENSE) for details.
