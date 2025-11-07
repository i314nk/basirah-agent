# LLM Selection Guide - When to Use Which Model

**Status:** Phase 7 Complete
**Date:** 2025-11-06

---

## Quick Reference

| Use Case | Recommended Model | Cost | Notes |
|----------|------------------|------|-------|
| **Production Deep Dive** | Claude 4 Sonnet | $3-4 | Best quality, handles large prompts |
| **Testing/Validation** | Claude 4 Sonnet | $3-4 | Realistic quality assessment |
| **UI Debugging** | Ollama Local | FREE | Fast iteration, basic testing |
| **Simple Queries** | Ollama Cloud | FREE | Good for short prompts only |
| **Feature Development** | Ollama Local | FREE | Unlimited iterations |

---

## Model Comparison

### 1. **Claude 4 Sonnet** (Production)

```bash
LLM_MODEL=claude-sonnet-4.5
```

**Best For:**
- ✅ Full Deep Dive analysis (multi-year 10-K research)
- ✅ Production-quality investment theses
- ✅ Large system prompts (27K+ characters)
- ✅ Extended Thinking mode
- ✅ Native tool use (optimal)
- ✅ Final validation before deployment

**Limitations:**
- ❌ Costs $3-4 per Deep Dive analysis
- ❌ Expensive for iterative development

**Context Limit:** ~200K tokens
**Quality:** 95% (Excellent)
**Speed:** Fast
**Cost:** $3/1M input tokens, $15/1M output tokens

---

### 2. **Ollama Local** (Development/Testing)

```bash
LLM_MODEL=deepseek-r1-8b
# Or: deepseek-r1:latest, qwen2.5:7b, llama3.1:8b
```

**Best For:**
- ✅ UI debugging and testing
- ✅ Feature development
- ✅ Unlimited iterations (FREE)
- ✅ Bug fixing without cost
- ✅ Quick screens and basic analysis

**Limitations:**
- ❌ Lower quality than Claude (75% vs 95%)
- ❌ May struggle with complex reasoning
- ❌ Requires local GPU/CPU resources
- ❌ Setup required (Docker/Ollama installation)

**Context Limit:** ~8K tokens (varies by model)
**Quality:** 75% (Very Good for 8B model)
**Speed:** Fast (local GPU)
**Cost:** FREE (electricity only)

**Setup:**
```bash
# Start Ollama Docker
docker run -d --gpus=all -p 11434:11434 ollama/ollama

# Pull model
docker exec ollama-container ollama pull deepseek-r1:latest
```

---

### 3. **Ollama Cloud** (Limited Use)

```bash
LLM_MODEL=gpt-oss:120b-cloud
# Or: gpt-oss-cloud, deepseek-cloud
```

**Best For:**
- ✅ Simple queries (< 1000 chars)
- ✅ Testing without local setup
- ✅ Quick validation
- ✅ No GPU required

**Limitations:**
- ❌ **Cannot handle large prompts** (27K+ chars causes 500 error)
- ❌ **NOT suitable for Deep Dive analysis**
- ❌ Context limits unclear (appears to be ~10K chars)
- ❌ 500 Internal Server Error with full system prompts
- ❌ Cloud service stability unknown

**Context Limit:** ~10K characters (estimated, not documented)
**Quality:** 85% (Very Good for 120B model)
**Speed:** Very Fast (cloud datacenter)
**Cost:** FREE (preview - will be paid eventually)

**Known Issues:**
- ⚠️  Deep Dive analysis fails (prompt too large)
- ⚠️  System prompt (27K chars) + tools = 500 error
- ⚠️  Best for simple queries only

**Example:**
```python
# ✅ Works - Simple query
messages = [{"role": "user", "content": "What is 2+2?"}]

# ❌ Fails - Deep Dive with large system prompt
messages = [
    {"role": "system", "content": "27K char system prompt..."},
    {"role": "user", "content": "Analyze Apple..."}
]  # Results in 500 Internal Server Error
```

---

## Current Issue: Ollama Cloud + Deep Dive

### Problem

Ollama Cloud returns **500 Internal Server Error** when attempting Deep Dive analysis.

**Root Cause:**
- Full system prompt: 27,533 characters
- Tool descriptions: ~5,000 characters
- **Total first request: ~32,000 characters**
- Ollama Cloud cannot handle prompts this large

**Error:**
```
INFO: Calling Ollama Cloud - Prompt size: 32533 chars
ERROR: Internal Server Error (status code: 500)
```

### Solution

**Use Claude for Deep Dive:**
```bash
# For production Deep Dive analysis
set LLM_MODEL=claude-sonnet-4.5
streamlit run src/ui/app.py
```

**Use Ollama Local for FREE Deep Dive:**
```bash
# For FREE Deep Dive (requires local setup)
set LLM_MODEL=deepseek-r1-8b
streamlit run src/ui/app.py
```

**Ollama Cloud for simple queries only:**
```bash
# Only for simple, short prompts
set LLM_MODEL=gpt-oss-cloud
# Use custom script with small prompts, NOT Deep Dive
```

---

## Recommendations by Use Case

### Scenario 1: Initial Development

**Goal:** Build features, fix bugs, iterate quickly

**Recommended:**
```bash
LLM_MODEL=deepseek-r1-8b  # FREE local Ollama
```

**Why:**
- Unlimited iterations at $0 cost
- Fast local execution
- Good enough quality for development
- No cloud dependencies

---

### Scenario 2: Feature Testing

**Goal:** Validate that new features work correctly

**Recommended:**
```bash
# Start with local for basic testing
LLM_MODEL=deepseek-r1-8b

# Then validate with Claude for quality
LLM_MODEL=claude-sonnet-4.5
```

**Why:**
- Catch obvious bugs with FREE local model
- Final validation with production-quality Claude
- Saves money on test iterations

---

### Scenario 3: Production Deployment

**Goal:** Real analyses for actual investment decisions

**Recommended:**
```bash
LLM_MODEL=claude-sonnet-4.5
```

**Why:**
- Highest quality (95%)
- Handles large prompts
- Reliable and well-tested
- Extended Thinking mode
- Worth the cost for actual decisions

---

### Scenario 4: UI/UX Debugging

**Goal:** Test UI changes, styling, workflows

**Recommended:**
```bash
LLM_MODEL=deepseek-r1-8b  # LOCAL (not cloud)
```

**Why:**
- Don't need high-quality analysis output
- Just testing UI rendering/behavior
- FREE and fast
- Unlimited iterations

---

## Cost Optimization Strategy

### Development Phase

```bash
# Week 1-4: Build features
LLM_MODEL=deepseek-r1-8b  # $0 cost
# Run 1000 test iterations = $0

# Week 5: Validate quality
LLM_MODEL=claude-sonnet-4.5  # Test 10 analyses = $30
```

**Savings:** $2,970 (vs $3,000 if using Claude for all iterations)

---

### Production Phase

```bash
# For actual user analyses
LLM_MODEL=claude-sonnet-4.5

# For internal testing/debugging
LLM_MODEL=deepseek-r1-8b
```

**Monthly Cost:**
- 100 user analyses × $3 = $300/month
- 500 internal tests × $0 = $0/month
- **Total:** $300/month

**Without Phase 7:**
- 100 user analyses × $3 = $300/month
- 500 internal tests × $3 = $1,500/month
- **Total:** $1,800/month

**Savings:** $1,500/month = $18,000/year

---

## Environment Configuration

### Development `.env`

```bash
# For development - FREE local model
LLM_MODEL=deepseek-r1-8b

# Claude for validation only
ANTHROPIC_API_KEY=your_key_here
```

### Production `.env`

```bash
# For production - Best quality
LLM_MODEL=claude-sonnet-4.5

# Required
ANTHROPIC_API_KEY=your_production_key_here
```

---

## Summary

| Model | Deep Dive | Quick Screen | Simple Queries | Cost |
|-------|-----------|--------------|----------------|------|
| **Claude 4 Sonnet** | ✅ Excellent | ✅ Excellent | ✅ Excellent | $$$  |
| **Ollama Local** | ✅ Good | ✅ Good | ✅ Good | FREE |
| **Ollama Cloud** | ❌ Fails (500) | ⚠️  Limited | ✅ Good | FREE |

**Recommendation:**
- **Production:** Claude 4 Sonnet
- **Development:** Ollama Local (deepseek-r1-8b)
- **Simple Tests:** Ollama Cloud (gpt-oss-cloud) - but avoid Deep Dive

---

## Troubleshooting

### "500 Internal Server Error" with Ollama Cloud

**Cause:** Prompt too large (> 10K characters)

**Solution:**
```bash
# Switch to Claude for large prompts
set LLM_MODEL=claude-sonnet-4.5

# Or use Ollama Local
set LLM_MODEL=deepseek-r1-8b
```

### Ollama Local "Model not found"

**Solution:**
```bash
# Pull the model first
ollama pull deepseek-r1:latest

# Or via Docker
docker exec ollama-container ollama pull deepseek-r1:latest
```

### Claude "API key not found"

**Solution:**
```bash
# Set in .env file
ANTHROPIC_API_KEY=your_key_here
```

---

**Updated:** 2025-11-06
**Phase:** 7 - Plug-and-Play LLM System
