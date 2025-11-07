# Phase 7: Plug-and-Play LLM System

**Status:** ✅ Complete
**Date:** 2025-11-06
**Priority:** HIGH (Flexibility & Cost Control)

---

## Overview

Phase 7 implements a plug-and-play LLM abstraction layer that allows seamless switching between different language models (Claude, Ollama local, Ollama cloud, OpenAI future) via configuration only - **no code changes required**.

### Key Benefits

1. **Cost Savings:** 92% cost reduction during development (use FREE Ollama for iteration, Claude for final testing)
2. **Flexibility:** Switch models via environment variable
3. **Future-Proof:** Easy to add new providers (GPT-5, Gemini, etc.)
4. **Unified API:** Same interface for all LLM providers
5. **User Choice:** Eventually allow users to select their preferred LLM

---

## Architecture

```
Application Layer (Agents)
         ↓
   LLMClient (Unified Interface)
         ↓
    LLMFactory (Provider Selection)
         ↓
   BaseLLMProvider (Abstract Interface)
         ↓
    ┌────┴────┬──────────┬──────────┐
    ↓         ↓          ↓          ↓
  Claude   Ollama    Ollama     OpenAI
          Local     Cloud      (Future)
```

---

## Files Created

### Core LLM System

```
src/llm/
├── __init__.py                 # Package exports
├── base.py                     # Base provider interface
├── config.py                   # Model configurations
├── factory.py                  # Provider factory & client
└── providers/
    ├── __init__.py
    ├── claude.py               # Claude provider
    ├── ollama_local.py         # Ollama local
    └── ollama_cloud.py         # Ollama cloud
```

### Documentation

```
docs/phases/phase_7/
└── PHASE_7_LLM_ABSTRACTION.md  # This file
```

### Tests

```
test_llm_providers.py           # Test script for LLM abstraction
```

---

## Available Models

### Production Models (Claude)
- **claude-sonnet-4.5**: Best quality, $3-4 per analysis
- **claude-3.5-sonnet**: Previous gen, $3-4 per analysis

### Local Models (Ollama - FREE)
- **deepseek-r1-8b**: Best for reasoning, FREE ⭐ Recommended
- **qwen2.5-7b**: General purpose, FREE
- **llama3.1-8b**: Reliable alternative, FREE

### Cloud Models (Ollama - FREE Preview)
- **deepseek-cloud**: 671B model, excellent quality
- **gpt-oss-cloud**: OpenAI's open model

---

## Usage

### 1. Configuration (via Environment Variable)

```bash
# .env file
LLM_MODEL=claude-sonnet-4.5  # or deepseek-r1-8b, qwen2.5-7b, etc.
ANTHROPIC_API_KEY=your_key_here
```

### 2. Basic Usage

```python
from src.llm import LLMClient

# Create client (reads LLM_MODEL from environment)
llm = LLMClient()

# Generate response
response = llm.generate(
    messages=[
        {"role": "system", "content": "You are a financial analyst"},
        {"role": "user", "content": "Analyze Apple Inc."}
    ],
    max_tokens=4000
)

print(response.content)
print(f"Cost: ${response.cost:.2f}")
```

### 3. Specific Model

```python
# Override environment and use specific model
llm = LLMClient(model_key="deepseek-r1-8b")
```

### 4. Provider Info

```python
info = llm.get_provider_info()
print(f"Using: {info['model_key']}")
print(f"Provider: {info['provider']}")
print(f"Cost: {info['cost']}")
```

---

## Integration with Existing Code

### BuffettAgent & ShariaScreener

Both agents now support the LLM abstraction layer:

```python
# Both agents have two interfaces:

# 1. self.llm - LLM abstraction layer (simple generation)
#    - Supports any configured model
#    - Use for simple generation tasks

# 2. self.client - Direct Claude access (extended thinking + tools)
#    - Required for ReAct loop with tool use
#    - Required for Extended Thinking feature
```

**Why Both Interfaces?**

Claude has unique features (Extended Thinking + Tool Use) that aren't supported by other LLMs yet. The abstraction layer provides flexibility while maintaining access to Claude's advanced features.

---

## Testing

### Test Script

```bash
# Activate venv
source venv/Scripts/activate

# Test with current model
python test_llm_providers.py
```

### Switch Models

```bash
# Use Claude (best quality)
export LLM_MODEL=claude-sonnet-4.5
python test_llm_providers.py

# Use Ollama local (FREE)
export LLM_MODEL=deepseek-r1-8b
ollama serve  # In separate terminal
ollama pull deepseek-r1:8b-0528-qwen3
python test_llm_providers.py

# Use Ollama cloud (FREE preview)
export LLM_MODEL=deepseek-cloud
export OLLAMA_API_KEY=your_key
python test_llm_providers.py
```

---

## Cost Savings Example

### Current (Claude Only)
```
Testing 100 companies:
- 100 analyses × $3 = $300
- Bug fixes (50 iterations) × $3 = $150
- Feature testing (100 tests) × $3 = $300
TOTAL: $750
```

### With Phase 7 (Hybrid)
```
Initial testing (10 companies, Claude):
- 10 × $3 = $30

Bug fixes (50 iterations, Ollama):
- 50 × $0 = $0

Feature testing (100 tests, Ollama):
- 100 × $0 = $0

Final verification (10 companies, Claude):
- 10 × $3 = $30

TOTAL: $60
Savings: $690 (92%)! 🎉
```

---

## Recommended Workflow

### For Development/Testing

```bash
# 1. Start with Claude for realistic baseline
export LLM_MODEL=claude-sonnet-4.5
# Run analysis, note quality

# 2. Switch to Ollama for iteration
export LLM_MODEL=deepseek-r1-8b
# Test features, fix bugs at $0 cost
# Unlimited iterations!

# 3. Final verification with Claude
export LLM_MODEL=claude-sonnet-4.5
# Ensure production quality before deploy
```

### For Production (Future Options)

**Option 1: Fixed Model**
```bash
LLM_MODEL=claude-sonnet-4.5  # All users
```

**Option 2: User Choice**
```python
# Let users select in UI
selected_model = st.selectbox(
    "Choose LLM",
    ["claude-sonnet-4.5", "deepseek-r1-8b", "qwen2.5-7b"]
)
llm = LLMClient(model_key=selected_model)
```

**Option 3: Tiered Access**
```python
# Free tier: Ollama
# Premium tier: Claude
if user.is_premium:
    model = "claude-sonnet-4.5"
else:
    model = "deepseek-r1-8b"

llm = LLMClient(model_key=model)
```

---

## Installation

### Dependencies

```bash
# Activate venv
source venv/Scripts/activate

# Install ollama package (already in requirements.txt)
pip install ollama
```

### Ollama Local Setup

```bash
# Download from: https://ollama.com/download
# Or:

# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Windows: Download from website

# Start Ollama
ollama serve

# Pull recommended model
ollama pull deepseek-r1:8b-0528-qwen3
```

---

## Adding New Providers

To add a new provider (e.g., OpenAI):

1. **Create provider class:** `src/llm/providers/openai.py`
2. **Inherit from:** `BaseLLMProvider`
3. **Implement methods:**
   - `generate()` - Generate response
   - `is_available()` - Check availability
   - `get_cost_per_token()` - Return costs
4. **Register in factory:** `LLMFactory.PROVIDER_CLASSES`
5. **Add config:** `LLMConfig.MODELS`
6. **Update docs**

---

## Technical Details

### Base Interface

All providers implement `BaseLLMProvider`:

```python
class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        messages: List[LLMMessage],
        max_tokens: int = 16000,
        temperature: float = 1.0,
        **kwargs
    ) -> LLMResponse:
        """Generate response from LLM."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass

    @abstractmethod
    def get_cost_per_token(self) -> Dict[str, float]:
        """Get cost per token."""
        pass
```

### Response Format

All providers return standardized `LLMResponse`:

```python
@dataclass
class LLMResponse:
    content: str          # Generated text
    model: str            # Model ID used
    provider: str         # Provider name
    tokens_input: int     # Input token count
    tokens_output: int    # Output token count
    cost: float          # Total cost in USD
    metadata: Dict       # Provider-specific metadata
```

---

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
**Solution:** Set in `.env` file:
```bash
ANTHROPIC_API_KEY=your_key_here
```

### "Ollama is not running"
**Solution:** Start Ollama:
```bash
ollama serve
```

### "Model not found locally"
**Solution:** Pull the model:
```bash
ollama pull deepseek-r1:8b-0528-qwen3
```

### "ollama package not installed"
**Solution:** Install in venv:
```bash
source venv/Scripts/activate
pip install ollama
```

---

## Success Criteria

✅ **Plug-and-play working** - Switch models via env var only
✅ **All providers functional** - Claude, Ollama local, Ollama cloud
✅ **Existing agents updated** - Both have LLM abstraction access
✅ **Cost tracking accurate** - Costs tracked for all providers
✅ **Easy to add providers** - Clear interface and examples
✅ **Documentation complete** - Usage guide and architecture docs
✅ **Testing verified** - Test script working with all models

---

## Future Enhancements

- [ ] OpenAI provider implementation
- [ ] Google Gemini provider
- [ ] Automatic provider selection based on task
- [ ] Cost-based provider switching
- [ ] Response caching
- [ ] Provider health monitoring
- [ ] Extended Thinking support in abstraction layer
- [ ] Tool use support in abstraction layer

---

## Summary

Phase 7 successfully implements a flexible, plug-and-play LLM system that:
- **Saves 92% on development costs** (use FREE Ollama for iteration)
- **Maintains Claude quality** (use for final testing/production)
- **Future-proofs the codebase** (easy to add new providers)
- **Preserves existing functionality** (agents work as before)
- **Provides user choice** (eventually allow model selection)

The abstraction layer is production-ready and immediately usable for cost-effective development and testing.

---

**Status:** ✅ Complete
**Next Steps:** Use Ollama for development, Claude for production
**Estimated Savings:** $690 per 100 test iterations (92%)
