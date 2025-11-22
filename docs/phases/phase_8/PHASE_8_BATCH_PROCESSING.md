# Phase 8: Automated Batch Screening Protocol

**Status:** ✅ Complete
**Date:** November 8, 2025
**Priority:** HIGH (Killer Feature)

---

## Overview

Phase 8 transforms basīrah from a single-company analysis tool into a **portfolio-building engine** by implementing automated batch screening that can analyze hundreds of companies in a single run.

### Key Features

1. **CSV Upload** - Simple ticker list input
2. **Protocol Engine** - Configurable multi-stage screening
3. **Progress Dashboard** - Real-time status updates
4. **Stop/Resume** - Pause and continue batch runs
5. **Cost Management** - Estimation and budget controls
6. **Summary Reports** - Detailed results breakdown
7. **Database Integration** - All analyses auto-saved

---

## Architecture

```
Batch Processing Flow

CSV Upload (test_batch_companies.csv)
    ↓
Protocol Selection
├─ Halal Value: Sharia → Quick → Deep
├─ Value Only: Quick → Deep
├─ Sharia Only: Sharia screening
└─ Quick Filter: Quick screening only
    ↓
Batch Processor
├─ Stage 1: Screen all companies
├─ Stage 2: Filter & screen survivors
├─ Stage 3: Deep dive finalists
├─ Progress tracking (real-time)
└─ Auto-save to database
    ↓
Summary Report
├─ Funnel visualization
├─ Top recommendations
├─ Cost breakdown
└─ Navigation to History
```

---

## Files Created

### 1. Protocol System
**File:** [src/batch/protocols.py](../../src/batch/protocols.py) (267 lines)

Defines screening protocols and stages:
- `AnalysisType` enum (SHARIA, QUICK, DEEP_DIVE)
- `Decision` enum (COMPLIANT, INVESTIGATE, BUY, etc.)
- `ProtocolStage` dataclass (single stage definition)
- `BatchProtocol` dataclass (complete protocol)
- 4 predefined protocols:
  - **Halal Value**: Sharia → Quick → Deep (10 years)
  - **Value Only**: Quick → Deep (5 years)
  - **Sharia Only**: Sharia compliance check
  - **Quick Filter**: Quick screening only

**Key Functions:**
```python
get_protocol(protocol_id: str) -> BatchProtocol
list_protocols() -> List[BatchProtocol]
protocol.estimate_cost(num_companies: int) -> Dict
```

### 2. Batch Processing Engine
**File:** [src/batch/batch_processor.py](../../src/batch/batch_processor.py) (378 lines)

Core batch processing logic:
- CSV loading and validation
- Multi-stage processing
- Progress tracking
- Stop/Resume functionality
- Error handling
- Summary generation

**Key Methods:**
```python
BatchProcessor.load_tickers_from_csv(csv_path) -> List[str]
BatchProcessor.start_batch(tickers) -> str  # Returns batch_id
BatchProcessor.process_batch() -> Dict
BatchProcessor.stop()
BatchProcessor.resume()
BatchProcessor.get_summary() -> Dict
```

### 3. Streamlit UI
**File:** [src/ui/pages/2_Batch_Processing.py](../../src/ui/pages/2_Batch_Processing.py) (403 lines)

Complete batch processing interface:
- CSV upload widget
- Protocol selector
- Cost estimator
- Real-time progress dashboard
- Stage statistics
- Stop/Resume controls
- Summary report with funnel visualization

### 4. Navigation Update
**File:** [src/ui/components.py](../../src/ui/components.py) (modified)

Added navigation buttons to sidebar:
- 🏠 Home
- 📜 History
- 🔄 Batch Processing

---

## CSV Format

### Input Format

```csv
ticker
AAPL
MSFT
GOOG
JPM
KO
```

**Requirements:**
- Column header: `ticker`
- One ticker per row
- No additional columns needed
- Case insensitive
- Duplicates automatically removed

---

## Protocol Details

### 1. Halal Value Investing

**Best for:** Muslim investors seeking Sharia-compliant value stocks

**Stages:**
1. **Sharia Compliance Screen** (~$0.98 per company)
   - Filters for COMPLIANT or DOUBTFUL status
   - Non-compliant companies stop here
2. **Quick Screen** (~$1.14 per company)
   - Filters for INVESTIGATE recommendation
   - PASS companies stop here
3. **Deep Dive Analysis** (~$3.71 per company, 10 years)
   - Complete analysis on survivors
   - BUY/WATCH/AVOID decisions

**Cost Estimate (100 companies):**
- Stage 1: 100 companies × $0.98 = $98
- Stage 2: 70 companies × $1.14 = $80 (assume 70% pass)
- Stage 3: 35 companies × $3.71 = $130 (assume 50% pass)
- **Total: ~$308** (actual may be lower due to filtering)

### 2. Value Investing Only

**Best for:** Non-Muslim investors or broader screening

**Stages:**
1. **Quick Screen** (~$1.14 per company)
2. **Deep Dive Analysis** (~$2.81 per company, 5 years)

**Cost Estimate (100 companies):**
- Stage 1: 100 × $1.14 = $114
- Stage 2: 50 × $2.81 = $141
- **Total: ~$255**

### 3. Sharia Screening Only

**Best for:** Quick Sharia compliance check on large universe

**Stages:**
1. **Sharia Compliance Screen** (~$0.98 per company)

**Cost Estimate (500 companies):**
- Stage 1: 500 × $0.98 = $490
- **Total: ~$490**

### 4. Quick Filter Only

**Best for:** Building watchlist from large universe

**Stages:**
1. **Quick Screen** (~$1.14 per company)

**Cost Estimate (200 companies):**
- Stage 1: 200 × $1.14 = $228
- **Total: ~$228**

---

## Usage Guide

### Step 1: Prepare CSV

Create a CSV file with tickers:
```csv
ticker
AAPL
MSFT
GOOG
```

### Step 2: Upload & Select Protocol

1. Navigate to **Batch Processing** page
2. Upload CSV file
3. Preview tickers
4. Select screening protocol
5. Review cost estimate

### Step 3: Start Batch

1. Click "🚀 Start Batch"
2. Monitor progress in real-time
3. View stage-by-stage statistics

### Step 4: Review Results

After completion:
- View funnel visualization
- See top BUY recommendations
- Check total cost
- Navigate to History for details

---

## Progress Tracking

### Real-Time Updates

The UI displays:
- **Status**: Running / Paused / Complete
- **Current Stage**: e.g., "Stage 2/3"
- **Elapsed Time**: Minutes elapsed
- **Current Progress**: Companies processed in current stage
- **Stage Statistics**: Passed/Failed counts

### Stage Statistics

For each completed stage:
- Companies processed
- Passed (continue to next stage)
- Failed (stopped)
- Errors (if any)
- Duration

---

## Stop/Resume Functionality

### Stop Batch
- Click "⏸️ Stop Batch"
- Completes current company analysis
- Saves all completed analyses
- Status changes to "Paused"

### Resume Batch
- Click "▶️ Resume Batch"
- Continues from where it left off
- Processes remaining companies

---

## Summary Report

### Metrics Displayed

1. **Overall Stats**
   - Total companies processed
   - Duration (hours)
   - Total cost
   - BUY decisions count

2. **Screening Funnel**
   - Stage-by-stage progression
   - Pass rates
   - Visual progress bars

3. **Top Recommendations**
   - BUY decisions from final stage
   - Ticker + conviction level
   - Sorted by quality

4. **Actions**
   - View all results in History
   - Start new batch

---

## Database Integration

All analyses are automatically saved to the database (Phase 6C.1):

- **Searchable**: Find by ticker, date, batch_id
- **Filterable**: Filter by decision, conviction, batch
- **Exportable**: Download analysis details
- **Metadata**: Includes batch_id, batch_stage, batch_stage_index

**Example metadata:**
```python
{
    "batch_id": "batch_20251108_143022",
    "batch_stage": "Deep Dive Analysis",
    "batch_stage_index": 2,
    "analysis_type": "deep_dive",
    "years_analyzed": 10
}
```

---

## Cost Management

### Cost Estimation

Before starting, the system estimates:
- **Best case**: Heavy filtering (50% of max)
- **Worst case**: Light filtering (100%)
- **Time estimate**: Based on analysis types
- **Stage breakdown**: Per-stage costs

### Actual Cost Tracking

During and after processing:
- Real-time cost accumulation
- Token usage from each analysis
- Final total cost in summary

---

## Error Handling

### CSV Validation

- Checks for `ticker` column
- Validates ticker format (1-5 characters)
- Removes duplicates
- Reports invalid tickers

### Analysis Errors

- Logged with ticker and stage
- Doesn't stop batch processing
- Reported in summary
- Continues with next company

### Recovery

- Stop/Resume allows pausing
- All completed analyses saved
- Can restart from checkpoint

---

## Testing

### Test CSV Included

**File:** [test_batch_companies.csv](../../test_batch_companies.csv)

```csv
ticker
AAPL
MSFT
GOOG
JPM
KO
```

### Test Procedure

1. **Quick Test** (Sharia Only):
   - Upload test CSV (5 companies)
   - Select "Sharia Screening Only"
   - Estimated cost: ~$5
   - Estimated time: ~20 minutes
   - Run and verify all complete

2. **Medium Test** (Quick Filter):
   - Use 10-20 companies
   - Select "Quick Filter Only"
   - Estimated cost: ~$20
   - Verify progress tracking

3. **Full Test** (Value Only):
   - Use 5-10 companies
   - Select "Value Investing Only"
   - Test stop/resume
   - Verify funnel visualization

---

## Performance

### Scalability

- **Small batches** (5-10 companies): 30-60 minutes
- **Medium batches** (20-50 companies): 2-6 hours
- **Large batches** (100+ companies): 8-24 hours

### Optimization

- Sequential processing (one company at a time)
- Automatic filtering reduces later-stage costs
- Database auto-save prevents data loss
- Progress tracking allows monitoring

---

## Limitations & Future Enhancements

### Current Limitations

1. **Sequential Processing**: One company at a time
2. **No Parallel Execution**: Single-threaded
3. **Manual Protocol Selection**: No dynamic adjustment
4. **Fixed Filter Rates**: Assumes 70/50% progression

### Future Enhancements

1. **Parallel Processing**: Analyze multiple companies simultaneously
2. **Dynamic Protocols**: Adjust based on results
3. **Batch Scheduling**: Schedule for off-hours
4. **Email Notifications**: Alert when complete
5. **Export Reports**: PDF/Excel summary generation
6. **Cost Limits**: Stop when budget reached
7. **Custom Protocols**: User-defined screening stages
8. **Batch History**: View past batch runs
9. **Batch Comparison**: Compare results across batches
10. **Smart Filtering**: ML-based pass rate prediction

---

## Integration with Other Phases

### Phase 6C.1 (Database)
- All batch analyses saved automatically
- Searchable by batch_id
- Metadata includes batch context

### Phase 7 (LLM Providers)
- Works with any configured LLM
- Cost tracking adapts to provider
- Token usage accurately recorded

### Phase 8 Enables
- Portfolio construction workflows
- Systematic screening processes
- Research automation
- Large-scale analysis

---

## Success Metrics

### Phase 8 Complete ✅

- [x] CSV upload works
- [x] 4 protocols implemented
- [x] Batch processor handles multi-stage screening
- [x] Progress tracking real-time
- [x] Stop/Resume functional
- [x] Database integration works
- [x] UI complete and functional
- [x] Navigation added
- [x] Documentation complete
- [x] Test CSV provided

---

## Examples

### Example 1: Halal Value Screen

**Input:** 50 Halal-focused companies
**Protocol:** Halal Value Investing
**Expected Flow:**
- Stage 1: 50 companies → 35 pass Sharia (70%)
- Stage 2: 35 companies → 15 pass Quick Screen (43%)
- Stage 3: 15 companies → Deep Dive all
- **Result**: 15 complete analyses, 3-5 BUY decisions
- **Cost**: ~$150-200
- **Time**: ~6-8 hours

### Example 2: S&P 500 Quick Filter

**Input:** All 500 S&P 500 companies
**Protocol:** Quick Filter Only
**Expected Flow:**
- Stage 1: 500 companies → All get quick screened
- **Result**: ~150-200 INVESTIGATE recommendations
- **Cost**: ~$570
- **Time**: ~16-20 hours

### Example 3: Tech Sector Deep Dive

**Input:** 20 tech companies
**Protocol:** Value Investing Only
**Expected Flow:**
- Stage 1: 20 companies → 10 pass Quick Screen
- Stage 2: 10 companies → All get Deep Dive
- **Result**: 10 complete analyses, 2-3 BUY decisions
- **Cost**: ~$50-60
- **Time**: ~3-4 hours

---

## Conclusion

Phase 8 transforms basīrah into a professional-grade research platform capable of systematic portfolio construction through automated batch screening. Combined with Phase 6C.1's database and Phase 7's LLM flexibility, this creates a complete investment analysis system.

**Impact:** Enables users to screen hundreds of companies systematically, build portfolios following specific criteria (Halal, Value, etc.), and make data-driven investment decisions at scale.

---

## Files Summary

### Created (4 files)
1. `src/batch/__init__.py` - Module initialization
2. `src/batch/protocols.py` - Protocol definitions (267 lines)
3. `src/batch/batch_processor.py` - Batch engine (378 lines)
4. `src/ui/pages/2_Batch_Processing.py` - UI (403 lines)
5. `test_batch_companies.csv` - Test data

### Modified (1 file)
1. `src/ui/components.py` - Added navigation buttons

### Total Lines Added: ~1,050 lines

---

*Phase 8: Automated Batch Screening Protocol - Complete*
*November 8, 2025*
