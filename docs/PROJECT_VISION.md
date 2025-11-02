# basīrah: Autonomous Investment Analysis

## Vision

Build an autonomous AI agent that analyzes companies using Warren Buffett's investment philosophy, with Sharia compliance verification. The agent should investigate, reason, and make investment decisions with the same rigor and skepticism as the Oracle of Omaha.

**basīrah** (بَصِيرَة) - Arabic for "insight" or "perceptiveness"

---

## What This Is

**An autonomous investment analyst** that:
- Reads annual reports (10-Ks) and earnings transcripts
- Investigates business models and competitive moats
- Assesses management quality and capital allocation
- Calculates intrinsic value using Owner Earnings and DCF
- Makes high-conviction BUY/WATCH/AVOID recommendations
- Explains its complete reasoning process
- Adapts its investigation based on what it discovers

**Think of it as:** Warren Buffett as an AI agent with 24/7 access to financial data.

---

## What This Is NOT

❌ **Not a stock screener** - It doesn't just score companies on metrics  
❌ **Not a trading bot** - It doesn't execute trades automatically  
❌ **Not a black box** - Every decision is fully explained  
❌ **Not a rules-based system** - It reasons and adapts, not follows scripts  
❌ **Not for day trading** - It's for long-term value investing  

---

## Core Philosophy

### Buffett's Approach

Warren Buffett's investment process:
1. **Understand the business** - Can I explain how it makes money?
2. **Assess the moat** - Does it have sustainable competitive advantage?
3. **Evaluate management** - Are they competent and honest?
4. **Calculate intrinsic value** - What's it actually worth?
5. **Margin of safety** - Buy only at significant discount
6. **Long-term view** - Think like a business owner, not trader

**This agent replicates that process.**

### Investment Principles (Codified)

**Circle of Competence:**
- Only analyze businesses the agent can understand
- If the business model is too complex → PASS
- Admit uncertainty rather than guess

**Economic Moats:**
- Look for sustainable competitive advantages
- Brand strength, network effects, switching costs
- Patents, economies of scale, regulatory barriers
- Moat must be durable (10+ years)

**Owner Earnings Focus:**
- Ignore accounting tricks
- Focus on real cash generation
- Calculate: Net Income + D&A - CapEx - Working Capital changes
- This is what the business actually produces

**Management Quality:**
- Assess honesty and competence
- Check capital allocation track record
- Review compensation structure (aligned with shareholders?)
- Look for red flags: aggressive accounting, excessive perks

**Margin of Safety:**
- Never pay full price
- Buy at 20-40% discount to intrinsic value
- More uncertainty = bigger discount required
- Protects against mistakes

**Long-term Perspective:**
- 5-10 year holding period mindset
- Ignore short-term price movements
- Focus on business fundamentals
- Compound returns through patience

### Sharia Compliance

In addition to Buffett principles, investments must be Sharia-compliant:
- No interest-based businesses (conventional banks)
- No alcohol, tobacco, gambling, pornography
- Debt/Total Assets < 33%
- Liquid assets/Market cap < 33%
- Accounts receivable/Market cap < 50%

*(Implementation approach TBD in future sprint)*

---

## How It Works

### The Agent's Process

The agent doesn't follow a predetermined script. Instead, it:

**Phase 1: Initial Assessment**
```
Agent: "Let me check if this is even investable..."
→ Quick look at basic metrics
→ Sharia compliance check
→ Circle of competence check
→ Decision: Investigate further or pass?
```

**Phase 2: Business Understanding**
```
Agent: "I need to understand HOW this makes money..."
→ Reads 10-K business description
→ Studies revenue model
→ Maps value chain
→ Identifies key success factors
```

**Phase 3: Moat Assessment**
```
Agent: "What protects this business from competition?"
→ Analyzes competitive position
→ Evaluates switching costs
→ Checks pricing power
→ Compares to competitors
→ Judges moat width (None/Narrow/Wide)
```

**Phase 4: Management Evaluation**
```
Agent: "Can I trust management with capital?"
→ Reads shareholder letters (10 years)
→ Analyzes compensation structure
→ Reviews capital allocation history
→ Looks for red flags
→ Judges management quality
```

**Phase 5: Financial Analysis**
```
Agent: "What are the real economics?"
→ Calculates Owner Earnings
→ Analyzes ROIC trends
→ Checks debt sustainability
→ Evaluates cash generation
→ Builds financial model
```

**Phase 6: Valuation**
```
Agent: "What's this actually worth?"
→ Runs conservative DCF
→ Compares to historical multiples
→ Checks current price vs intrinsic value
→ Calculates margin of safety
```

**Phase 7: Risk Assessment**
```
Agent: "What could go wrong?"
→ Reviews risk factors
→ Checks for litigation
→ Looks for accounting issues
→ Considers worst-case scenarios
```

**Phase 8: Decision**
```
Agent: "Weighing everything, what's my conviction?"
→ Synthesizes all findings
→ Determines confidence level
→ Calculates position size
→ Final recommendation: BUY / WATCH / AVOID
```

**Key:** The agent decides its path based on what it discovers. If it finds red flags in Phase 3, it might skip straight to "AVOID" without doing full financial analysis.

---

## Technical Architecture

### Agent Core
- **LLM:** Claude 3.5 Sonnet with extended thinking
- **Reasoning:** ReAct-style autonomous loop
- **Budget:** ~$2-5 per company analysis
- **Quality:** Deep thinking, not quick answers

### Tool Ecosystem

**Data Access Tools:**
- GuruFocus API - Pre-calculated financial metrics
- SEC Filing Reader - 10-K/10-Q full text access
- Web Search - Recent news and analysis

**Analysis Tools:**
- Financial Calculator - Owner Earnings, DCF, ROIC
- Accounting Analyzer - Detect earnings manipulation
- Management Tracker - Track CEO/CFO history

**Compliance Tools:**
- Sharia Checker - Islamic finance verification

### System Prompt

The agent's "personality" and knowledge comes from:
- Buffett's actual investment principles
- Specific criteria for quality assessment
- Red flags and warning signs
- Valuation methodologies
- Risk assessment frameworks

This is encoded in a detailed system prompt that guides the agent's thinking.

---

## Success Criteria

**The agent is successful when it can:**

✅ **Differentiate quality** - Tell excellent businesses from mediocre ones  
✅ **Catch red flags** - Identify accounting tricks, bad management  
✅ **Explain reasoning** - Show complete thought process  
✅ **Admit uncertainty** - Say "I don't know" when appropriate  
✅ **Value conservatively** - Prefer errors of omission over commission  
✅ **Think long-term** - Focus on 5-10 year perspective  
✅ **Stay in circle** - Avoid complex businesses it can't understand  

**Success is NOT:**
- ❌ Always being "right" (even Buffett isn't always right)
- ❌ Finding lots of BUY recommendations (most companies fail Buffett's test)
- ❌ Beating the market short-term
- ❌ Having high confidence on everything

**Better to make money on a few high-conviction ideas than lose money on many mediocre ones.**

---

## Development Philosophy

### Build for Quality, Not Speed
- Deep analysis > quick screening
- Thoughtful investigation > predetermined checklists
- Few great investments > many okay investments

### Transparency Over Opacity
- Show all reasoning
- Explain every conclusion
- Make assumptions explicit
- Allow verification

### Continuous Learning
- Compare agent decisions to outcomes
- Refine based on what works
- Update Buffett principles as needed
- Improve over time

---

## Future Vision

**Phase 1 (MVP):** Single-company deep analysis
- Analyze one company at a time
- Output: Detailed investment thesis
- Manual trade execution

**Phase 2:** Portfolio construction
- Compare multiple companies
- Position sizing based on conviction
- Portfolio-level risk management

**Phase 3:** Continuous monitoring
- Track existing holdings
- Alert on material changes
- Re-evaluate investment theses

**Phase 4:** Multi-strategy
- Value investing (current)
- Special situations (spinoffs, mergers)
- Distressed opportunities

---

## Principles We Follow

**From Warren Buffett:**
> "Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1."

> "It's far better to buy a wonderful company at a fair price than a fair company at a wonderful price."

> "Risk comes from not knowing what you're doing."

**Our Interpretation:**
- Margin of safety is paramount
- Quality > cheapness
- Deep understanding required
- When uncertain, pass

---

## What Makes This Different

**Most AI investing tools:**
- Sentiment analysis on news
- Technical trading signals
- Quick screening based on metrics
- Black-box predictions

**basīrah:**
- Fundamental business analysis
- Qualitative + quantitative synthesis
- Transparent reasoning process
- Long-term value investing
- Thinks like a human analyst, not an algorithm

---

## Who This Is For

**Target User:**
- Value investor
- Follows Buffett/Munger philosophy
- Seeks Sharia-compliant investments
- Wants deep analysis, not quick picks
- Comfortable with concentration (few high-conviction ideas)
- Patient, long-term oriented

**NOT for:**
- Day traders
- Technical analysis focus
- Diversification-above-all approach
- Quick-profit seeking
- High-frequency trading

---

## Current Status

**Phase:** Foundation (Sprint 2)  
**Status:** Setting up architecture and gathering documentation  
**Next:** Build the agent (Sprint 3)  
**Timeline:** 6 weeks to working MVP

---

## Repository Structure

```
basirah-agent/
├── docs/           # Architecture, philosophy, tool specs
├── src/
│   ├── agent/      # Core agent implementation
│   ├── tools/      # Data access and analysis tools
│   └── utils/      # Configuration and helpers
├── tests/          # Verification and testing
└── examples/       # Usage examples
```

---

## Contributing Philosophy

**This is a focused project with a clear vision.**

We welcome contributions that:
- ✅ Improve analysis quality
- ✅ Add useful tools for investigation
- ✅ Enhance transparency and explainability
- ✅ Stay true to Buffett's principles

We generally don't want:
- ❌ Features that encourage short-term trading
- ❌ Technical analysis capabilities
- ❌ Automatic trade execution (for now)
- ❌ Anything that reduces transparency

---

## License & Disclaimer

**License:** TBD

**Disclaimer:**  
This is an investment research tool, NOT investment advice. Past performance doesn't guarantee future results. You are responsible for your own investment decisions. The agent can make mistakes - verify its reasoning before investing real money. 

Never invest money you can't afford to lose.

---

**Let's build something remarkable.**
