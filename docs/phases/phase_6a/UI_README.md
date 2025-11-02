# basīrah Web Interface

Professional web interface for Warren Buffett AI Investment Agent

**Status:** ✅ MVP Complete (Phase 6A)
**Version:** 1.0.0
**Date:** November 1, 2025

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Streamlit (web framework)
- Plotly (visualizations)
- Pandas (data handling)
- All backend dependencies

### 2. Set API Keys

Create or edit `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-...
GURUFOCUS_API_KEY=your_key
BRAVE_API_KEY=your_key
```

### 3. Run the Application

```bash
streamlit run src/ui/app.py
```

The app will open automatically in your browser at: [http://localhost:8501](http://localhost:8501)

---

## Features (MVP)

### ✅ Completed (Phase 6A)

**Core Functionality:**
- Company ticker input with validation
- Analysis type selection (Deep Dive / Quick Screen)
- Real-time progress feedback
- Results display with decision, metrics, and thesis
- Error handling with retry option
- Session state management

**Results Display:**
- Decision badge (BUY/WATCH/AVOID) with emoji
- Key metrics (Intrinsic Value, Current Price, Margin of Safety, Duration)
- Full investment thesis in Warren Buffett's voice
- Context management details (strategy, years analyzed, tokens used)
- Analysis metadata (tool calls, duration, etc.)

**Export Options:**
- Download as JSON
- Download as Markdown
- Copy thesis to clipboard

**UI Polish:**
- Professional color scheme (blue theme)
- Clean, uncluttered layout
- Mobile-responsive design
- Warren Buffett branding (basīrah)
- Helpful tooltips and guidance
- Sidebar with information

---

## User Guide

### Running an Analysis

1. **Enter Ticker Symbol**
   - Type a valid US stock ticker (e.g., AAPL, MSFT, KO)
   - Must be 1-5 uppercase letters

2. **Select Analysis Type**
   - **Deep Dive**: Full 10-K analysis (5-7 min, ~$2-5)
     - Reads complete annual reports
     - Multi-year analysis (3 years)
     - Comprehensive investment thesis
   - **Quick Screen**: Fast screening (30-60 sec, ~$0.50)
     - Key metrics only
     - Basic BUY/WATCH/AVOID decision

3. **Click "Analyze Company"**
   - Progress indicator shows current stage
   - Warren AI reads filings, uses tools, generates thesis
   - Wait for completion (don't close browser)

4. **Review Results**
   - Decision and conviction level
   - Key metrics and valuation
   - Full investment thesis
   - Export or save results

### Understanding Results

**Decision Types:**

🟢 **BUY** (Green)
- High-quality business
- Margin of safety ≥25-40%
- Warren would invest

🟡 **WATCH** (Yellow)
- Good business quality
- Margin of safety 10-25%
- Wait for better price

🔴 **AVOID** (Red)
- Outside circle of competence
- No economic moat
- Poor management or financials
- Overvalued

**Conviction Levels:**
- **HIGH**: Very confident, clear signals
- **MODERATE**: Reasonable confidence, some uncertainties
- **LOW**: Limited confidence, more info needed

### Context Management

The agent automatically handles companies of any size:

**Standard Strategy (95% of companies):**
- Normal-sized 10-K filings (<400K characters)
- Examples: Apple, Lululemon, most companies

**Adaptive Strategy (5% edge cases):**
- Exceptionally large 10-K filings (>400K characters)
- Examples: Coca-Cola, Microsoft (some years)
- Agent still reads FULL 10-K
- Creates comprehensive summary to manage context
- Zero quality sacrifice

Check the "Context Management Details" section in results to see which strategy was used.

---

## Examples

### Example 1: Apple (Standard Strategy)

```
Ticker: AAPL
Analysis Type: Deep Dive
Expected: 5-7 minutes

Results:
- Decision: AVOID (HIGH conviction)
- Strategy: Standard
- Context: 3,911 tokens
- Years: [2024, 2023, 2022]
- Duration: 353 seconds
```

### Example 2: Coca-Cola (Adaptive Strategy)

```
Ticker: KO
Analysis Type: Deep Dive
Expected: 5-7 minutes

Results:
- Decision: AVOID (HIGH conviction)
- Strategy: Adaptive Summarization
- Filing Size: 552,732 characters
- Context: 4,335 tokens (98.2% reduction)
- Years: [2024, 2023, 2022]
- Duration: 408 seconds
```

### Example 3: Quick Screen

```
Ticker: MSFT
Analysis Type: Quick Screen
Expected: 30-60 seconds

Results:
- Decision: WATCH (MODERATE conviction)
- Duration: 45 seconds
- Cost: ~$0.50
```

---

## Troubleshooting

### "Please enter a valid stock ticker"

- Use 1-5 uppercase letters only
- Examples: AAPL, MSFT, KO, BRK.B
- No spaces or special characters (except .)

### "Analysis Failed - API rate limits"

- Wait 30-60 seconds and retry
- Anthropic has rate limits (429 errors)
- Agent will auto-retry with exponential backoff

### "ANTHROPIC_API_KEY not found"

- Create `.env` file in project root
- Add: `ANTHROPIC_API_KEY=sk-ant-...`
- Restart Streamlit app

### Analysis taking too long

- Deep Dive: 5-7 minutes is normal
- Quick Screen: 30-60 seconds is normal
- Don't close browser during analysis
- Progress indicator shows current stage

### Results not displaying

- Check browser console for errors
- Refresh page (Ctrl+R)
- Clear session state: Menu → Settings → Clear cache

---

## File Structure

```
basira-agent/
├── src/
│   ├── agent/
│   │   └── buffett_agent.py       # Backend AI agent
│   ├── tools/                      # 4 production-ready tools
│   └── ui/                         # Web interface (NEW)
│       ├── __init__.py
│       ├── app.py                  # Main Streamlit app
│       ├── components.py           # Reusable UI components
│       └── utils.py                # Helper functions
├── .streamlit/
│   └── config.toml                 # Theme configuration
├── requirements.txt                # Python dependencies
└── UI_README.md                    # This file
```

---

## Configuration

### Theme Customization

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"        # Professional blue
backgroundColor = "#ffffff"      # Clean white
secondaryBackgroundColor = "#f0f2f6"  # Light gray
textColor = "#262730"           # Dark text
```

### Server Settings

```toml
[server]
headless = true
port = 8501                      # Change port if needed
```

---

## Performance

**Expected Metrics:**

| Analysis Type | Time | Cost | Tool Calls | Context |
|---------------|------|------|------------|---------|
| Quick Screen | 30-60s | $0.50 | 1-3 | ~500 tokens |
| Deep Dive (Standard) | 5-7 min | $2.50 | 10-20 | ~4K tokens |
| Deep Dive (Adaptive) | 5-7 min | $4.00 | 10-20 | ~4K tokens |

**Browser Requirements:**
- Modern browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Minimum 1024px width recommended

---

## Deployment (Future)

**Local Development:**
```bash
streamlit run src/ui/app.py
```

**Production Options:**
1. **Streamlit Community Cloud** (Free)
   - Push to GitHub
   - Connect at share.streamlit.io
   - Free hosting with resource limits

2. **Docker Container**
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   CMD ["streamlit", "run", "src/ui/app.py"]
   ```

3. **Cloud Platforms**
   - AWS (EC2, ECS)
   - Google Cloud (Cloud Run)
   - Azure (App Service)
   - Heroku

---

## Known Limitations

1. **Session State**
   - Analysis history not persisted (cleared on refresh)
   - Future: Database integration

2. **Real-Time Logs**
   - Currently shows spinner only
   - Future: Streaming logs display

3. **Multi-User**
   - Single-user app (session-based)
   - Future: User authentication

4. **Export Formats**
   - JSON and Markdown only
   - Future: PDF generation

---

## Next Steps (Phase 6B)

**Enhanced Features (Planned):**
1. Analysis history (persistent)
2. PDF export with charts
3. Multi-company comparison UI
4. Cost tracking dashboard
5. Custom settings (years to analyze, token budget)
6. Batch analysis interface

**Advanced Features (Phase 6C):**
7. Watchlist management
8. Charts & visualizations
9. Email/SMS alerts
10. Portfolio tracking

---

## Support

**Issues & Bug Reports:**
- GitHub Issues: [https://github.com/i314nk/basirah-agent/issues](https://github.com/i314nk/basirah-agent/issues)

**Documentation:**
- User Guide: [PHASE_5_USER_GUIDE.md](PHASE_5_USER_GUIDE.md)
- Strategic Review: [PHASE_5_STRATEGIC_REVIEW.md](PHASE_5_STRATEGIC_REVIEW.md)
- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

**Community:**
- Discord: Coming soon
- Discussions: GitHub Discussions

---

## Changelog

### v1.0.0 (November 1, 2025) - Phase 6A MVP

**Added:**
- ✅ Streamlit web interface
- ✅ Ticker input with validation
- ✅ Analysis type selector (Deep Dive / Quick Screen)
- ✅ Real-time progress feedback
- ✅ Results display (decision, metrics, thesis)
- ✅ Context management details
- ✅ Export (JSON, Markdown)
- ✅ Error handling with retry
- ✅ Professional theme and styling
- ✅ Mobile-responsive layout
- ✅ Sidebar info and guidance

**Backend:**
- ✅ Warren Buffett AI Agent (100% coverage)
- ✅ 4 production-ready tools
- ✅ Adaptive summarization
- ✅ Multi-year analysis

---

## License

MIT License - See LICENSE file for details

---

## Disclaimer

This is an AI-powered analytical tool, not financial advice.
Past performance does not guarantee future results. Always do your own research
and consult with a qualified financial advisor before making investment decisions.

---

**Built with Warren Buffett's investment principles | Powered by Claude 4.5 Sonnet**

**"The stock market is a device for transferring money from the impatient to the patient." - Warren Buffett**
