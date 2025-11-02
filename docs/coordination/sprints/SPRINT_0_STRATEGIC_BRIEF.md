# SPRINT 0: Repository Scaffolding & Documentation Structure

**Sprint Type:** Foundation Setup  
**Strategic Planner:** Claude  
**Expected Duration:** 1-2 days  
**Status:** READY FOR TACTICAL PLANNING

---

## Objective

Create the complete repository structure with all directories, placeholder files, and foundational documentation for the basīrah autonomous investment agent project. This sprint establishes the organizational framework that all subsequent development will build upon.

**Why This Sprint:**
Before we can gather documentation (Sprint 2) or build the agent (Sprint 3), we need a clean, well-organized repository structure. This sprint is pure setup - no code, just scaffolding.

---

## Context

**Current State:**
- Fresh repository: https://github.com/i314nk/basirah-agent.git
- Empty (or minimal README)
- Ready for structure

**Project Vision:**
Autonomous AI agent that analyzes companies using Warren Buffett's investment philosophy with Sharia compliance. The agent reasons, investigates, and makes investment decisions autonomously.

**Why Sprint 0:**
Sprint 1 in the old project was misaligned because we didn't have proper architecture from the start. Sprint 0 ensures we have the right structure before building anything.

---

## Architecture Decisions

### Repository Philosophy

**Principles:**
1. **Documentation-first** - Docs are equal to code in importance
2. **Clear separation** - Agent, tools, utils, tests clearly separated
3. **Coordination-aware** - Structure supports three-tier workflow
4. **Professional** - Production-ready organization from day 1

### Directory Structure

The repository will follow agent-first architecture:

```
basirah-agent/
├── README.md                           # Project overview
├── LICENSE                             # TBD
├── .gitignore                          # Python, env, IDE files
├── .env.example                        # API key template
├── requirements.txt                    # Dependencies
│
├── docs/                               # ALL documentation
│   ├── VISION.md                       # Project vision & philosophy
│   ├── ARCHITECTURE.md                 # System architecture
│   ├── BUFFETT_PRINCIPLES.md          # Investment philosophy codified
│   │
│   ├── coordination/                   # Three-tier workflow docs
│   │   ├── three_tier_protocol.md     # Coordination process
│   │   ├── handover_templates/        # Templates for handovers
│   │   │   ├── implementation_plan_template.md
│   │   │   ├── deliverables_template.md
│   │   │   └── technical_review_template.md
│   │   └── sprints/                    # Sprint archives
│   │       ├── sprint_0_brief.md
│   │       └── [future sprints]
│   │
│   ├── api_references/                 # External API documentation
│   │   ├── gurufocus_api.md           # GuruFocus API complete reference
│   │   ├── sec_edgar_api.md           # SEC EDGAR API reference
│   │   └── brave_search_api.md        # Web search API reference
│   │
│   └── tool_specs/                     # Tool specifications
│       ├── gurufocus_tool_spec.md
│       ├── sec_filing_tool_spec.md
│       ├── calculator_tool_spec.md
│       └── web_search_tool_spec.md
│
├── src/                                # Source code
│   ├── __init__.py
│   │
│   ├── agent/                          # Core agent implementation
│   │   ├── __init__.py
│   │   ├── investment_agent.py        # Main agent class
│   │   ├── buffett_prompt.py          # System prompt
│   │   └── reasoning_logger.py        # Trace agent reasoning
│   │
│   ├── tools/                          # Tool implementations
│   │   ├── __init__.py
│   │   ├── base.py                    # Tool interface (ABC)
│   │   ├── tool_registry.py           # Tool management
│   │   ├── gurufocus_tool.py          # GuruFocus API wrapper
│   │   ├── sec_filing_tool.py         # SEC filing reader
│   │   ├── calculator_tool.py         # Financial calculations
│   │   └── web_search_tool.py         # Web search integration
│   │
│   └── utils/                          # Utilities
│       ├── __init__.py
│       ├── config.py                   # Configuration management
│       ├── constants.py                # Constants and enums
│       └── logger.py                   # Logging setup
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest configuration
│   │
│   ├── test_tools/                     # Tool tests
│   │   ├── __init__.py
│   │   ├── test_gurufocus_tool.py
│   │   ├── test_sec_filing_tool.py
│   │   ├── test_calculator_tool.py
│   │   └── test_web_search_tool.py
│   │
│   └── test_agent/                     # Agent tests
│       ├── __init__.py
│       └── test_investment_agent.py
│
└── examples/                           # Usage examples
    ├── __init__.py
    ├── analyze_single_company.py       # Basic usage
    ├── compare_companies.py            # Multi-company analysis
    └── README.md                        # Examples documentation
```

### File Standards

**Python Files:**
- All files include proper docstrings
- All files include `__init__.py` in directories
- Follow PEP 8 style guide

**Documentation:**
- All .md files use proper markdown headers
- All docs include table of contents for long files
- All specs follow consistent template

---

## Deliverables

### Deliverable 1: Complete Directory Structure

**Acceptance Criteria:**
- [ ] All directories created as specified above
- [ ] All `__init__.py` files present
- [ ] Directory structure matches exactly

**Evidence Required:**
- Tree output or directory listing
- Confirmation all directories exist

### Deliverable 2: Placeholder Files

**Acceptance Criteria:**
- [ ] All Python files created with docstring headers
- [ ] All markdown files created with basic structure
- [ ] No file is completely empty

**Required Content for Placeholders:**

**Python files:**
```python
"""
Module: [name]
Purpose: [brief description]
Status: Placeholder - To be implemented in Sprint N
"""

# TODO: Implement in Sprint N
```

**Markdown files:**
```markdown
# [Title]

**Status:** To be completed in Sprint N

## Overview

[Brief description of what this doc will contain]

## Contents

- TBD

---

*This document will be completed during Sprint N*
```

### Deliverable 3: Core Documentation Files

**Files to Create:**

**README.md** - Project overview
- Project name and tagline
- Quick description
- Current status
- Links to key docs
- Setup instructions (placeholder)
- License info

**.gitignore** - Ignore patterns
- Python cache files
- Virtual environment
- `.env` files
- IDE files
- OS files

**.env.example** - Environment template
- `GURUFOCUS_API_KEY=your_key_here`
- `ANTHROPIC_API_KEY=your_key_here`
- `BRAVE_SEARCH_API_KEY=your_key_here`

**requirements.txt** - Dependencies
- anthropic>=0.40.0
- requests>=2.31.0
- python-dotenv>=1.0.0
- pydantic>=2.0.0
- pytest>=7.4.0

### Deliverable 4: Coordination Documents

**Files to Place:**

- `docs/coordination/three_tier_protocol.md` (provided)
- `docs/VISION.md` (provided)
- `docs/coordination/sprints/sprint_0_brief.md` (this file)

**Files to Create:**

- `docs/coordination/handover_templates/implementation_plan_template.md`
- `docs/coordination/handover_templates/deliverables_template.md`
- `docs/coordination/handover_templates/technical_review_template.md`

### Deliverable 5: Tool Specification Templates

**Create template file:**
`docs/tool_specs/_TEMPLATE.md`

**Content:**
```markdown
# [Tool Name] Specification

**Status:** [Draft/Complete/In Progress]  
**Sprint:** [When this will be implemented]

## Purpose

[What this tool does and why it's needed]

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| param1    | str  | Yes      | Description |

## Outputs

```python
{
    "success": bool,
    "data": {...},
    "error": str or null
}
```

## Implementation Requirements

- [ ] Requirement 1
- [ ] Requirement 2

## Example Usage

```python
tool = ToolName()
result = tool.execute(param1="value")
```

## Error Handling

[How errors should be handled]

## Dependencies

- External API or library needed

## Testing Requirements

- [ ] Test case 1
- [ ] Test case 2
```

---

## Success Criteria

**Sprint 0 is successful when:**
- [ ] Complete directory structure exists
- [ ] All placeholder files present with minimal content
- [ ] Core documentation files complete
- [ ] Coordination documents in place
- [ ] Repository is clean and organized
- [ ] No broken links or missing references
- [ ] Ready for documentation gathering (Sprint 2)

**Quality Check:**
- Someone unfamiliar with the project can navigate the repo
- Purpose of each directory is clear
- Coordination workflow is documented
- Nothing looks "incomplete" or "messy"

---

## Constraints

**Time:** 1-2 days maximum (this is quick setup)

**Budget:** $0 (no LLM API calls needed)

**Technical:**
- Python 3.9+
- Git repository
- Markdown for all docs

---

## Out of Scope

**NOT in this sprint:**
- ❌ Any actual code implementation
- ❌ GuruFocus API integration
- ❌ Writing complete documentation
- ❌ Tool specifications (just templates)
- ❌ Agent implementation
- ❌ Testing

**These come in later sprints.**

---

## Dependencies

**Provided Documents:**
- three_tier_protocol.md (already created)
- VISION.md (already created)
- This sprint brief

**No external dependencies.**

---

## Risk Factors

**Risk 1: Over-engineering the structure**
- Mitigation: Keep it simple, follow the exact structure provided
- Don't add extra directories "just in case"

**Risk 2: Forgetting placeholder content**
- Mitigation: Every file must have at least a docstring/header
- Use templates provided

---

## Handoff to Tactical Planner

**ChatGPT, you are receiving this Sprint 0 brief.**

**Your Tasks:**
1. Create detailed task list for every directory and file
2. Specify exact content for each placeholder
3. Provide file-by-file creation instructions
4. Create templates for handover documents
5. Organize tasks in logical order

**Priority:**
- Core structure first (directories, __init__.py)
- Documentation files second
- Placeholder code files last
- Verification checklist at end

**Expected Output:**
Implementation plan with:
- Exact file paths
- Exact content for each file
- Clear acceptance criteria
- Verification steps

**The Builder should be able to execute this sprint in 1-2 hours of focused work.**

---

## Notes for Strategic Review

**What I'll verify:**
- Structure matches specification exactly
- All files have appropriate placeholder content
- Documentation organization is clean
- Coordination process is properly documented
- Repository looks professional

**Definition of DONE:**
- Can run `tree` command and see complete structure
- Can navigate docs/ and understand organization
- Sprint 2 can start immediately after this

---

**SPRINT 0 BRIEF COMPLETE**  
**READY FOR HANDOFF TO TACTICAL PLANNER**
