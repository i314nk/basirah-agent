# Quick Reference: Phase 7 - Plug-and-Play LLM System

**Phase:** 7 - Multi-LLM Abstraction Layer
**Goal:** Seamlessly switch between ANY LLM via configuration only
**Time:** ~3.5 hours
**Strategic Value:** MASSIVE (90%+ cost savings during testing)

---

## 🎯 **What You're Building**

### **Before Phase 7**
```python
# Locked to Claude only
from anthropic import Anthropic

client = Anthropic(api_key="...")
response = client.messages.create(...)

# Problems:
❌ Can't switch models
❌ Expensive testing ($3 per analysis)
❌ No flexibility
❌ Hard to add new providers
```

### **After Phase 7**
```python
# Use ANY model
from src.llm import LLMClient

llm = LLMClient()  # Uses LLM_MODEL from .env
response = llm.generate(...)

# Benefits:
✅ Switch models: export LLM_MODEL=deepseek-r1-8b
✅ Free testing with Ollama ($0 per analysis)
✅ Keep Claude for realistic tests
✅ Easy to add GPT-5, Gemini, etc.
```

---

## 🏗️ **Architecture**

```
┌─────────────────────────────────┐
│     Your Application Code       │
│  (BuffettAgent, ShariaScreener) │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│        LLMClient                │
│  (Unified Interface)            │
└────────────┬───────────────────┘
             │
             ▼
┌────────────────────────────────┐
│       LLMFactory                │
│  (Provider Selection)           │
└────────────┬───────────────────┘
             │
      ┌──────┴─────┬──────────┐
      ▼            ▼          ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Claude  │  │ Ollama  │  │ Ollama  │
│Provider │  │ Local   │  │ Cloud   │
└─────────┘  └─────────┘  └─────────┘
```

**Key Principle:** Your code talks to `LLMClient`, never to providers directly!

---

## 📊 **Available Models**

### **Production: Claude** (Best Quality)
```bash
LLM_MODEL=claude-sonnet-4.5

Cost: $3-4 per analysis
Quality: 95% (best)
Speed: Fast
Use for: Realistic testing, final checks
```

### **Testing: Ollama Local** (FREE!)
```bash
LLM_MODEL=deepseek-r1-8b

Cost: $0 (runs on your GPU)
Quality: 75% (very good)
Speed: Fast
Use for: Bug fixes, development, iterations
```

### **Testing: Ollama Cloud** (FREE Preview!)
```bash
LLM_MODEL=deepseek-cloud

Cost: $0 (preview, will be paid later)
Quality: 90% (excellent)
Speed: Very fast
Use for: Scale testing without local GPU
```

---

## 💰 **Cost Savings Example**

### **Scenario: Testing Phase**

**Without Phase 7 (Claude only):**
```
Initial testing:    10 analyses × $3 = $30
Bug fixes:          50 tests × $3 = $150
Feature dev:        100 tests × $3 = $300
Final checks:       10 analyses × $3 = $30
────────────────────────────────────────
TOTAL: $510
```

**With Phase 7 (Hybrid):**
```
Initial testing:    10 analyses × $3 = $30   (Claude)
Bug fixes:          50 tests × $0 = $0       (Ollama)
Feature dev:        100 tests × $0 = $0      (Ollama)
Final checks:       10 analyses × $3 = $30   (Claude)
────────────────────────────────────────
TOTAL: $60

SAVINGS: $450 (88%)! 🎉
```

---

## 🔧 **How It Works**

### **1. Configuration (No Code Changes!)**

**File:** `.env`
```bash
# Switch between models by changing this ONE line:
LLM_MODEL=claude-sonnet-4.5        # Production testing
# LLM_MODEL=deepseek-r1-8b         # FREE testing
# LLM_MODEL=deepseek-cloud         # FREE cloud testing

# Provider API Keys
ANTHROPIC_API_KEY=sk-ant-...       # For Claude
OLLAMA_API_KEY=your_key            # For Ollama Cloud (optional)
```

### **2. Unified Interface**

**Before (Direct Anthropic):**
```python
from anthropic import Anthropic

client = Anthropic(api_key="...")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    messages=[{"role": "user", "content": "..."}]
)

content = response.content[0].text
cost = (response.usage.input_tokens * 0.00001) + \
       (response.usage.output_tokens * 0.0003)
```

**After (LLMClient):**
```python
from src.llm import LLMClient

llm = LLMClient()  # Auto-selects from env
response = llm.generate(
    messages=[{"role": "user", "content": "..."}],
    max_tokens=16000
)

content = response.content
cost = response.cost  # Already calculated!
```

### **3. Seamless Switching**

```bash
# Morning: Test with realistic Claude
export LLM_MODEL=claude-sonnet-4.5
streamlit run src/ui/app.py
# Cost: $3 per analysis

# Afternoon: Fix bugs with free Ollama
export LLM_MODEL=deepseek-r1-8b
streamlit run src/ui/app.py
# Cost: $0 per analysis

# Evening: Final check with Claude
export LLM_MODEL=claude-sonnet-4.5
streamlit run src/ui/app.py
# Cost: $3 per analysis
```

**NO CODE CHANGES NEEDED!** 🎉

---

## 📁 **New Files (8)**

```
src/llm/
├── __init__.py                    # Package init
├── base.py                        # Base interface
├── config.py                      # Model configurations
├── factory.py                     # Provider factory
└── providers/
    ├── __init__.py
    ├── claude.py                  # Claude provider
    ├── ollama_local.py            # Ollama local
    └── ollama_cloud.py            # Ollama cloud

docs/architecture/
└── llm_system.md                  # Architecture docs (NEW)
```

---

## 🔄 **Migration Steps**

### **For BuffettAgent**

**Before:**
```python
from anthropic import Anthropic

class BuffettAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def analyze(self, ticker):
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            messages=[...]
        )
        return response.content[0].text
```

**After:**
```python
from src.llm import LLMClient

class BuffettAgent:
    def __init__(self, model_key=None):
        self.llm = LLMClient(model_key=model_key)
    
    def analyze(self, ticker):
        response = self.llm.generate(
            messages=[...]
        )
        return response.content
```

**Changes:**
1. ✅ Import `LLMClient` instead of `Anthropic`
2. ✅ Initialize `LLMClient()` instead of `Anthropic()`
3. ✅ Call `llm.generate()` instead of `client.messages.create()`
4. ✅ Access `response.content` instead of `response.content[0].text`

**That's it!** Same for ShariaScreener.

---

## 🎨 **UI Integration**

### **Model Selector in Sidebar**

```python
# In app.py sidebar
st.sidebar.markdown("### 🤖 LLM Configuration")

# Get available models
available = LLMFactory.get_available_providers()

# Model selector
selected = st.sidebar.selectbox(
    "Select Model",
    options=available,
    format_func=lambda x: LLMConfig.get_model_config(x)["description"]
)

# Update environment
os.environ["LLM_MODEL"] = selected

# Show info
info = LLMConfig.get_model_config(selected)
st.sidebar.caption(f"Provider: {info['provider']}")
st.sidebar.caption(f"Cost: {info['cost']}")
st.sidebar.caption(f"Quality: {info['quality']}")
```

**Result:**
```
┌────────────────────────────┐
│ 🤖 LLM Configuration       │
│                            │
│ Select Model:              │
│ ┌────────────────────────┐ │
│ │ Claude 4 Sonnet        │ │
│ │ DeepSeek R1 8B (FREE) ▼│ │
│ └────────────────────────┘ │
│                            │
│ Provider: ollama_local     │
│ Cost: FREE                 │
│ Quality: Very Good (75%)   │
└────────────────────────────┘
```

---

## ✅ **Testing Checklist**

### **Provider Tests**
- [ ] Claude provider works
- [ ] Ollama local works (if installed)
- [ ] Ollama cloud works (if API key set)
- [ ] Cost tracking accurate
- [ ] Error handling works

### **Integration Tests**
- [ ] BuffettAgent uses LLMClient
- [ ] ShariaScreener uses LLMClient
- [ ] Deep dive analysis works
- [ ] Quick screen works
- [ ] Sharia screen works

### **UI Tests**
- [ ] Model selector appears in sidebar
- [ ] Switching models works
- [ ] Provider info displays correctly
- [ ] No errors in console
- [ ] Analysis completes successfully

### **Workflow Tests**
- [ ] Can switch from Claude to Ollama
- [ ] Results quality acceptable
- [ ] Cost tracking shows $0 for Ollama
- [ ] Cost tracking shows $3-4 for Claude

---

## 🚀 **Quick Start**

### **Step 1: Install Ollama (Optional - for FREE testing)**

```bash
# Download from: https://ollama.com/download

# Pull recommended model
ollama pull deepseek-r1:8b-0528-qwen3

# Verify it works
ollama run deepseek-r1:8b-0528-qwen3
>>> What is 2+2?
4
>>> /bye
```

### **Step 2: Update .env**

```bash
# Add to .env
LLM_MODEL=claude-sonnet-4.5  # Start with Claude

# Optional: Add Ollama Cloud key
OLLAMA_API_KEY=your_key_here
```

### **Step 3: Run basīrah**

```bash
# Use Claude (realistic testing)
export LLM_MODEL=claude-sonnet-4.5
streamlit run src/ui/app.py

# Use Ollama (free testing)
export LLM_MODEL=deepseek-r1-8b
streamlit run src/ui/app.py
```

---

## 💡 **Recommended Workflow**

### **Phase 1: Initial Testing**
```bash
LLM_MODEL=claude-sonnet-4.5
```
- Run 5-10 analyses
- Verify quality meets expectations
- Note baseline cost

### **Phase 2: Development & Bug Fixes**
```bash
LLM_MODEL=deepseek-r1-8b
```
- Fix bugs at $0 cost
- Test new features unlimited
- Iterate freely

### **Phase 3: Final Verification**
```bash
LLM_MODEL=claude-sonnet-4.5
```
- Run final checks
- Ensure production quality
- Deploy with confidence

---

## 📊 **Model Comparison**

| Model | Provider | Cost | Quality | Speed | Use Case |
|-------|----------|------|---------|-------|----------|
| **claude-sonnet-4.5** | Claude | $3-4 | 95% | Fast | Production testing |
| **deepseek-r1-8b** | Ollama Local | FREE | 75% | Fast | Development ⭐ |
| **qwen3-8b** | Ollama Local | FREE | 70% | Fast | Alternative |
| **deepseek-cloud** | Ollama Cloud | FREE* | 90% | Very Fast | Scale testing |

*Preview - will be paid eventually

**Recommendation:** Use `deepseek-r1-8b` for development (best quality/cost ratio)

---

## 🎯 **Success Metrics**

**After Phase 7, you can:**

✅ **Switch models instantly** - One env var change
✅ **Test for free** - $0 with Ollama local
✅ **Keep high quality** - Claude when it matters
✅ **Save 90%+ costs** - During development
✅ **Future-proof** - Easy to add GPT-5, Gemini
✅ **Give users choice** - Let them pick model (future)

---

## 🔮 **Future Possibilities**

### **User Choice**
```python
# Let users pick their model
model = st.selectbox("Choose LLM", [
    "claude-sonnet-4.5",     # Best quality
    "deepseek-r1-8b",        # Free, good quality
    "qwen3-8b"               # Free, decent quality
])
```

### **Tiered Access**
```python
# Free tier: Ollama
# Premium tier: Claude
if user.is_premium:
    model = "claude-sonnet-4.5"
else:
    model = "deepseek-r1-8b"
```

### **Cost-Based Selection**
```python
# Use cheap model first, upgrade if needed
response = llm.generate(messages, model="deepseek-r1-8b")

if response.confidence < 0.8:
    # Retry with better model
    response = llm.generate(messages, model="claude-sonnet-4.5")
```

---

## 📥 **Download**

[View BUILDER_PROMPT_PHASE_7.txt](computer:///mnt/user-data/outputs/BUILDER_PROMPT_PHASE_7.txt) ⭐

**Includes:**
- Complete implementation (8 new files)
- Integration instructions (2 file updates)
- Testing procedures
- Documentation templates
- Architecture updates
- Migration guide

---

## 🎊 **Bottom Line**

**Phase 7 = Professional Infrastructure**

```
Before:
❌ Locked to Claude ($3 per test)
❌ Expensive development
❌ Limited flexibility

After:
✅ Any LLM, one config change
✅ Free testing with Ollama
✅ Claude when quality matters
✅ 90%+ cost savings
✅ Future-proof architecture
```

**This is the infrastructure that transforms basīrah from a prototype into a professional platform!**

Ready to implement the plug-and-play system? 🚀

---

*Phase 7: Plug-and-Play LLM System*
*The infrastructure that pays for itself immediately*
*Status: Ready for Implementation*
