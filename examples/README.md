# Warren Buffett AI Agent - Examples

**Status:** Complete - Sprint 3, Phase 5

This directory contains real-world examples demonstrating how to use the Warren Buffett AI Agent.

## Prerequisites

Before running examples, ensure you have:

1. **Installed Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Keys:**
   ```bash
   # Required
   export ANTHROPIC_API_KEY='your_key_here'

   # Optional (for full functionality)
   export GURUFOCUS_API_KEY='your_key_here'
   export BRAVE_API_KEY='your_key_here'
   ```

   On Windows:
   ```cmd
   set ANTHROPIC_API_KEY=your_key_here
   set GURUFOCUS_API_KEY=your_key_here
   set BRAVE_API_KEY=your_key_here
   ```

## Examples

### 1. Basic Analysis (`basic_analysis.py`)

**Purpose:** Simplest way to analyze a single company

**Run:**
```bash
python examples/basic_analysis.py
```

**Time:** 2-5 minutes | **Cost:** ~$2-5

---

### 2. Quick Screen (`quick_screen.py`)

**Purpose:** Rapidly screen multiple companies

**Run:**
```bash
python examples/quick_screen.py
```

**Time:** 1-3 minutes | **Cost:** ~$2-3

---

### 3. Compare Competitors (`compare_competitors.py`)

**Purpose:** Side-by-side comparison of competitors

**Run:**
```bash
python examples/compare_competitors.py
```

**Time:** 10-20 minutes | **Cost:** ~$8-15

---

### 4. Outside Circle of Competence (`outside_competence.py`)

**Purpose:** Demonstrates agent passing on opportunities

**Run:**
```bash
python examples/outside_competence.py
```

**Time:** 3-7 minutes | **Cost:** ~$3-5

---

### 5. Error Handling (`error_handling.py`)

**Purpose:** Demonstrates robust error handling

**Run:**
```bash
python examples/error_handling.py
```

**Time:** 2-4 minutes | **Cost:** ~$1-2

## Understanding Results

### Decision Types

**BUY:** Wide moat, excellent management, ROIC >15%, margin of safety ≥25-40%

**WATCH:** Good business but wait for better price

**AVOID:** Outside competence, no moat, poor management, or no margin of safety

### Conviction Levels

**HIGH:** Strong confidence, clear decision

**MODERATE:** Reasonable confidence, some uncertainties

**LOW:** Limited confidence, need more information

## Best Practices

1. **Start with Quick Screens** - Filter before deep diving
2. **Use Deep Dives Selectively** - Only for high-conviction opportunities
3. **Trust AVOID Decisions** - Agent is being selective (like Buffett)
4. **Understand WATCH** - Good businesses worth monitoring

## Troubleshooting

- **API Key Issues:** Verify environment variables are set
- **Tool Failures:** Check API keys for GuruFocus and Brave
- **Slow Analysis:** Use `deep_dive=False` for faster results

## Next Steps

- Read `PHASE_5_USER_GUIDE.md` for complete documentation
- Review `docs/BUFFETT_PRINCIPLES.md` for investment philosophy
- See `docs/ARCHITECTURE.md` for system design

---

**Happy Investing! "The stock market is a device for transferring money from the impatient to the patient." - Warren Buffett**
