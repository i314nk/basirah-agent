# basīrah - Warren Buffett AI Investment Agent

<div align="center">

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)
![Tests](https://img.shields.io/badge/tests-passing-success.svg)

**An AI-powered investment analysis agent that thinks like Warren Buffett**

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Web UI](#web-ui) • [API](#api-reference)

</div>

---

## Overview

**basīrah** (Arabic: بَصِيرَة, meaning "insight" or "foresight") is an AI investment agent that embodies Warren Buffett's value investing philosophy. It analyzes companies by reading SEC filings, financial data, and market research to generate comprehensive investment theses in Buffett's authentic voice.

### What Makes basīrah Unique

- **📖 Reads Full 10-K Filings** - Analyzes 200+ page annual reports like Warren Buffett does
- **⚡ Smart Quick Screen** - Get INVESTIGATE/PASS guidance before spending on full analysis
- **☪️ Sharia Compliance** - AAOIFI-standard Islamic finance screening for halal investing
- **📊 Multi-Year Analysis** - Configurable 1-10 year trend analysis for deep insights
- **🧠 Adaptive Context Management** - Handles any company size with intelligent summarization
- **💬 Authentic Buffett Voice** - Generates theses that sound like Berkshire Hathaway shareholder letters
- **💰 Real-Time Cost Tracking** - Transparent token usage and cost display for every analysis
- **🌍 Arabic Translation** - One-click translation with proper RTL formatting for global investors
- **🌐 Professional Web UI** - Beautiful Streamlit interface for easy access
- **✅ 100% Coverage** - Successfully analyzes all S&P 500 companies

---

## Features

### 🎯 Core Capabilities

- **Enhanced Quick Screen** - 1-year business snapshot with INVESTIGATE/PASS recommendation (2-3 min, $0.75-$1.50)
- **Deep Dive Analysis** - Comprehensive multi-year investment thesis (5-15 min, $2.50-$7)
- **Sharia Compliance Screening** - AAOIFI-standard Islamic finance analysis (3-5 min, $1.50-$2.50)
- **Configurable Depth** - Choose 1-10 years of historical analysis
- **Economic Moat Detection** - Identifies and analyzes competitive advantages
- **Management Evaluation** - Assesses CEO quality, capital allocation, and integrity
- **Valuation (DCF)** - Conservative discounted cash flow analysis
- **Risk Assessment** - Identifies top 5 risks with detailed analysis

### 🛠️ Technical Features

- **ReAct Agent Architecture** - Reasoning + Acting with extended thinking (8K budget)
- **Progressive Summarization** - 3-stage analysis (current year → prior years → synthesis)
- **Adaptive Strategies** - Automatic routing (standard vs summarization) based on filing size
- **Tool Integration** - SEC EDGAR, GuruFocus, Web Search, Calculator
- **Context Management** - Handles filings up to 552K+ characters
- **Export Options** - JSON, Markdown, Web UI display

### 🌐 Web Interface

- **Streamlit UI** - Professional web application
- **Real-time Progress** - Live updates during 5-7 minute analyses
- **Cost Tracking** - Real-time token usage and cost display with session totals
- **Arabic Translation** - One-click translation with proper RTL formatting
- **Dynamic Estimates** - Cost and time predictions based on configuration
- **Export & Share** - Download results as JSON or Markdown
- **Mobile Responsive** - Works on any device

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- [Anthropic API key](https://console.anthropic.com/) (Claude)
- [GuruFocus API key](https://www.gurufocus.com/api.php) (optional but recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/basira-agent.git
   cd basira-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys:
   # ANTHROPIC_API_KEY=your_key_here
   # GURUFOCUS_API_KEY=your_key_here (optional)
   ```

### Usage

#### Option 1: Web UI (Recommended)

```bash
streamlit run src/ui/app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

#### Option 2: Python API

```python
from src.agent.buffett_agent import WarrenBuffettAgent

# Initialize agent
agent = WarrenBuffettAgent()

# Run deep dive analysis
result = agent.analyze_company(
    ticker="AAPL",
    deep_dive=True,
    years_to_analyze=5  # Analyze 5 years (2024-2020)
)

# Access results
print(result['decision'])         # BUY, WATCH, or AVOID
print(result['conviction'])       # HIGH, MODERATE, or LOW
print(result['thesis'])           # Full investment thesis
print(result['intrinsic_value'])  # Calculated fair value
```

#### Option 3: Command Line

```bash
python -c "
from src.agent.buffett_agent import WarrenBuffettAgent
import json

agent = WarrenBuffettAgent()
result = agent.analyze_company('AAPL', deep_dive=True, years_to_analyze=3)

print(json.dumps(result, indent=2))
"
```

---

## Documentation

### User Guides

- **[Phase 5 User Guide](docs/phases/phase_5/PHASE_5_USER_GUIDE.md)** - Context management and adaptive summarization
- **[UI Guide](docs/phases/phase_6a/UI_README.md)** - Complete Streamlit web interface documentation
- **[Configurable Years](docs/phases/phase_6a/FEATURE_CONFIGURABLE_YEARS.md)** - How to configure analysis depth
- **[Cost Display + Arabic Translation](docs/phases/phase_6a/PHASE_6A2_COMPLETION_SUMMARY.md)** - Token tracking, cost display, and multilingual support

### Technical Documentation

- **[Phase 5 Strategic Review](docs/phases/phase_5/PHASE_5_STRATEGIC_REVIEW.md)** - Progressive summarization architecture
- **[Adaptive Summarization Fix](docs/phases/phase_5/ADAPTIVE_SUMMARIZATION_FIX.md)** - Handling large 10-K filings
- **[Complete Thesis Fix](docs/phases/phase_6a/PHASE_6A1_COMPLETE_THESIS_FIX.md)** - Generating comprehensive analyses

### Development History

- [Phase 1](docs/phases/phase_1/) - Initial implementation and testing
- [Phase 2](docs/phases/phase_2/) - Tool integration and refinement
- [Phase 3](docs/phases/phase_3/) - Advanced features
- [Phase 4](docs/phases/phase_4/) - Production readiness
- [Phase 5](docs/phases/phase_5/) - Context management (100% coverage)
- [Phase 6A](docs/phases/phase_6a/) - Web UI and enhancements
  - Phase 6A.1: Complete thesis fix and configurable years
  - Phase 6A.2: Cost tracking and Arabic translation
- [Phase 6B](docs/phases/phase_6b/) - Advanced screening features
  - Enhanced Quick Screen with INVESTIGATE/PASS recommendations
  - Sharia Compliance screening with AAOIFI standards

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      basīrah Agent                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Quick Screen│  │  Deep Dive   │  │   Synthesis  │    │
│  │   (30-60s)   │  │  (5-7 min)   │  │   (Multi-Yr) │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         Progressive Summarization Engine              │ │
│  │  • Stage 1: Current Year (Standard/Adaptive)         │ │
│  │  • Stage 2: Prior Years (Summarized)                 │ │
│  │  • Stage 3: Multi-Year Synthesis                     │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                 Tool Integrations                     │ │
│  │  • SEC EDGAR (10-K filings)                          │ │
│  │  • GuruFocus (financial data, ratios)                │ │
│  │  • Web Search (news, competitive analysis)           │ │
│  │  • Calculator (DCF, ROIC, owner earnings)            │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input → Validation → Agent Initialization
                             ↓
                    Strategy Selection
                   /                  \
           Standard (95%)        Adaptive (5%)
        (Normal filings)      (Large filings)
                   \                  /
                    ↓                ↓
              Current Year Analysis
                         ↓
               Prior Years Analysis
                  (Summarized)
                         ↓
            Multi-Year Synthesis
         (10-Section Complete Thesis)
                         ↓
          Decision + Thesis + Metadata
                         ↓
              Export (JSON/Markdown)
```

---

## Project Structure

```
basira-agent/
├── src/
│   ├── agent/
│   │   ├── buffett_agent.py       # Main agent implementation
│   │   ├── translator.py          # Arabic translation module
│   │   └── sharia_screener.py     # Sharia compliance screening
│   ├── tools/
│   │   ├── sec_filing_tool.py     # SEC EDGAR integration
│   │   ├── gurufocus_tool.py      # Financial data API
│   │   ├── web_search_tool.py     # Web search capability
│   │   └── calculator_tool.py     # Financial calculations
│   └── ui/
│       ├── app.py                 # Streamlit main app
│       ├── components.py          # UI components
│       └── utils.py               # UI utilities
│
├── tests/
│   ├── test_tools/                # Tool unit tests
│   ├── test_integration/          # Integration tests
│   └── test_company/              # Real company tests
│
├── docs/
│   ├── phases/                    # Development phase documentation
│   │   ├── phase_1/              # Initial implementation
│   │   ├── phase_2/              # Tool integration
│   │   ├── phase_3/              # Advanced features
│   │   ├── phase_4/              # Production readiness
│   │   ├── phase_5/              # Context management
│   │   └── phase_6a/             # Web UI
│   └── sessions/                  # Session summaries
│
├── .streamlit/
│   └── config.toml               # Streamlit theme config
│
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

---

## API Reference

### WarrenBuffettAgent

Main agent class for investment analysis.

#### `analyze_company(ticker, deep_dive=True, years_to_analyze=3)`

Analyze a company and generate investment thesis.

**Parameters:**
- `ticker` (str): Stock ticker symbol (e.g., "AAPL")
- `deep_dive` (bool): If True, comprehensive analysis; if False, quick screen
- `years_to_analyze` (int): Number of years to analyze (1-10, default 3)

**Returns:**
- `dict`: Analysis results containing:
  - `ticker` (str): Company ticker
  - `decision` (str): "BUY", "WATCH", or "AVOID"
  - `conviction` (str): "HIGH", "MODERATE", or "LOW"
  - `thesis` (str): Full investment thesis
  - `intrinsic_value` (float): Calculated fair value per share
  - `current_price` (float): Current market price
  - `margin_of_safety` (float): Percentage discount
  - `metadata` (dict): Analysis metadata

**Example:**

```python
from src.agent.buffett_agent import WarrenBuffettAgent

agent = WarrenBuffettAgent()

# Deep dive with 5 years
result = agent.analyze_company("AAPL", deep_dive=True, years_to_analyze=5)

print(f"Decision: {result['decision']}")
print(f"Conviction: {result['conviction']}")
print(f"Intrinsic Value: ${result['intrinsic_value']:.2f}")
print(f"\n{result['thesis']}")
```

---

## Performance

### Analysis Speed

| Type | Years | Time | Cost |
|------|-------|------|------|
| Quick Screen | 1 | 30-60 sec | ~$0.50 |
| Deep Dive | 1 | 2-3 min | ~$1.50 |
| Deep Dive | 3 | 5-7 min | ~$2.50 |
| Deep Dive | 5 | 10-15 min | ~$4.50 |
| Deep Dive | 10 | 20-30 min | ~$7.00 |

### Test Results

- **100% Success Rate** on S&P 500 companies
- **Adaptive Strategy** handles large 10-K filings (552K+ characters)
- **Standard Strategy** covers 95% of companies

---

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Company-Specific Tests

```bash
# Test Apple (standard strategy)
python tests/test_company/test_deep_dive_apple.py

# Test Coca-Cola (adaptive strategy)
python tests/test_company/test_deep_dive_ko.py

# Test Microsoft
python tests/test_company/test_deep_dive_msft.py
```

---

## Contributing

We welcome contributions! Please see our development guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Disclaimer

**basīrah is a research and educational tool.**

This software is provided for informational purposes only and does not constitute financial advice. Always conduct your own due diligence and consult with qualified financial advisors before making investment decisions.

---

<div align="center">

**Built with ❤️ for value investors**

*"Price is what you pay, value is what you get." - Warren Buffett*

</div>
