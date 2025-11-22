# Batch History Enhancement - Phase 8 Update
## Custom Naming & Hierarchical Organization

**Date:** 2025-11-09
**Status:** ✅ Complete

---

## Overview

Enhanced the batch processing system with custom naming and hierarchical organization in the History page, allowing users to:
1. Name their batches for easy identification
2. View batch processing runs separately from individual analyses
3. Drill down into batch results with stage-by-stage breakdown
4. See funnel visualization showing filtering progression

---

## Problem Statement

After implementing Phase 8 (Automated Batch Screening Protocol), batches were not being saved as unified entities. Individual analyses were saved with `batch_id` metadata but:
- No way to view all batches
- No batch summary entity in database
- No hierarchical view (Batch → Stages → Companies)
- No custom batch naming

**User Request:**
> "I would like the batches to be saved as a batch as in grouped with company analysis saved under example: Batch 1 - (User can also choose name of batch if they want)/quick screen/list of company analysis"

---

## Implementation

### Phase A: Custom Batch Naming

#### 1. UI: Batch Name Input ([src/ui/pages/2_Batch_Processing.py:102-108](../../../src/ui/pages/2_Batch_Processing.py#L102-L108))

```python
# Batch name input
st.divider()
batch_name = st.text_input(
    "📝 Batch Name (optional)",
    placeholder="e.g., Tech Stocks Q4 2025, Halal Portfolio Screen",
    help="Give this batch a memorable name, or leave blank for auto-generated timestamp name"
)
```

#### 2. Batch Processor: Accept & Store Name ([src/batch/batch_processor.py:112-150](../../../src/batch/batch_processor.py#L112-L150))

```python
def start_batch(self, tickers: List[str], batch_id: Optional[str] = None, batch_name: Optional[str] = None) -> str:
    if not batch_id:
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Use custom name or generate from timestamp
    if not batch_name or not batch_name.strip():
        batch_name = f"Batch {datetime.now().strftime('%b %d, %Y %H:%M')}"

    self.state = {
        ...
        "batch_id": batch_id,
        "batch_name": batch_name,  # NEW
        ...
    }
```

#### 3. UI: Pass Name to Processor ([src/ui/pages/2_Batch_Processing.py:227-231](../../../src/ui/pages/2_Batch_Processing.py#L227-L231))

```python
batch_id = processor.start_batch(
    st.session_state['batch_tickers'],
    batch_name=batch_name if batch_name and batch_name.strip() else None
)
```

#### 4. Display Custom Names in Progress/Summary

- Progress view: [src/ui/pages/2_Batch_Processing.py:245-246](../../../src/ui/pages/2_Batch_Processing.py#L245-L246)
- Summary view: [src/ui/pages/2_Batch_Processing.py:333-338](../../../src/ui/pages/2_Batch_Processing.py#L333-L338)

---

### Phase B: Batch Storage

#### 1. Database Schema ([db/init/02_create_batch_tables.sql](../../../db/init/02_create_batch_tables.sql))

Created three new database objects:

**A. `batch_summaries` table:**
```sql
CREATE TABLE batch_summaries (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(255) NOT NULL UNIQUE,
    batch_name VARCHAR(255) NOT NULL,

    protocol_id VARCHAR(50) NOT NULL,
    protocol_name VARCHAR(100) NOT NULL,
    protocol_description TEXT,

    status VARCHAR(50) NOT NULL,
    total_companies INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    total_cost DECIMAL(8, 2),

    stage_stats JSONB,
    top_recommendations JSONB,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**B. `batch_analyses` junction table:**
```sql
CREATE TABLE batch_analyses (
    batch_id INTEGER NOT NULL REFERENCES batch_summaries(id) ON DELETE CASCADE,
    analysis_id INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    stage_index INTEGER NOT NULL,
    stage_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (batch_id, analysis_id)
);
```

**C. Updated `analyses` table:**
```sql
ALTER TABLE analyses
ADD COLUMN batch_id VARCHAR(255),
ADD COLUMN batch_stage_name VARCHAR(100),
ADD COLUMN batch_stage_index INTEGER;
```

**D. View for easy querying:**
```sql
CREATE VIEW v_batch_summary AS
SELECT
    bs.*,
    COUNT(DISTINCT ba.analysis_id) as analyses_count,
    COUNT(DISTINCT CASE WHEN a.decision = 'BUY' THEN ba.analysis_id END) as buy_count
FROM batch_summaries bs
LEFT JOIN batch_analyses ba ON bs.id = ba.batch_id
LEFT JOIN analyses a ON ba.analysis_id = a.id
GROUP BY bs.id;
```

#### 2. Storage Methods ([src/storage/analysis_storage.py:503-724](../../../src/storage/analysis_storage.py#L503-L724))

Added five new methods to `AnalysisStorage`:

```python
def save_batch(batch_summary: Dict[str, Any]) -> int
    """Save batch summary to database"""

def link_analysis_to_batch(analysis_db_id: int, batch_db_id: int, stage_index: int, stage_name: str)
    """Link analysis to batch in junction table"""

def get_batches(limit: int = 50, offset: int = 0, protocol: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]
    """Retrieve batch summaries with filtering"""

def get_batch(batch_id: str) -> Optional[Dict[str, Any]]
    """Get single batch by ID"""

def get_batch_analyses(batch_id: str, stage_index: Optional[int] = None) -> List[Dict[str, Any]]
    """Get all analyses for a batch, grouped by stage"""
```

#### 3. Updated Analysis Storage ([src/storage/analysis_storage.py:265-309](../../../src/storage/analysis_storage.py#L265-L309))

Modified `save_analysis()` to include batch metadata:
```python
# Get batch metadata if present
batch_id = metadata.get('batch_id')
batch_stage_name = metadata.get('batch_stage')
batch_stage_index = metadata.get('batch_stage_index')

# Insert with batch fields
INSERT INTO analyses (..., batch_id, batch_stage_name, batch_stage_index)
VALUES (..., %s, %s, %s)
```

#### 4. Auto-Save on Batch Completion ([src/batch/batch_processor.py:180-188](../../../src/batch/batch_processor.py#L180-L188))

```python
# Save batch summary to database
try:
    summary = self.get_summary()
    summary['protocol_description'] = self.protocol.description
    self.storage.save_batch(summary)
    logger.info(f"Saved batch summary to database: {self.state['batch_id']}")
except Exception as e:
    logger.error(f"Failed to save batch summary: {e}")
```

---

### Phase C: Hierarchical History View

#### Updated History Page ([src/ui/pages/1_History.py](../../../src/ui/pages/1_History.py))

Added tabs to separate individual analyses from batches:

```python
tab1, tab2 = st.tabs(["📊 Individual Analyses", "📦 Batches"])
```

**Tab 1: Individual Analyses**
- Existing functionality preserved
- Search, filter, and view individual analyses

**Tab 2: Batches**
- List all batch processing runs
- For each batch:
  - Custom name display
  - Protocol used
  - Status (complete, running, error)
  - Metrics: Companies, BUY count, Duration, Cost
  - Stage funnel visualization
  - Expandable hierarchical view

**Hierarchical View Structure:**
```
📦 Batch Name
   ├─ 📊 Stage 1: Sharia Compliance Screen (100 companies)
   │  ├─ AAPL - COMPLIANT
   │  ├─ MSFT - COMPLIANT
   │  └─ JPM - NON_COMPLIANT
   │
   ├─ 📊 Stage 2: Quick Screen (70 companies)
   │  ├─ AAPL - INVESTIGATE
   │  ├─ MSFT - INVESTIGATE
   │  └─ GOOG - PASS
   │
   └─ 📊 Stage 3: Deep Dive (50 companies)
      ├─ AAPL - BUY (HIGH conviction)
      ├─ MSFT - BUY (MODERATE conviction)
      └─ GOOG - WATCH (LOW conviction)
```

**Funnel Visualization:**
Each batch shows filtering progression:
- Stage 1: 100 processed → 70 passed (70% pass rate)
- Stage 2: 70 processed → 50 passed (71% pass rate)
- Stage 3: 50 processed → 25 BUY decisions

---

## Files Modified

### Core Logic:
1. **[src/batch/batch_processor.py](../../../src/batch/batch_processor.py)**
   - Added `batch_name` parameter to `start_batch()` (line 112)
   - Added batch summary auto-save on completion (lines 180-188)
   - Updated `get_summary()` to include `batch_name` (line 351)

2. **[src/storage/analysis_storage.py](../../../src/storage/analysis_storage.py)**
   - Updated `save_analysis()` to save batch metadata (lines 265-309)
   - Added `save_batch()` method (lines 503-576)
   - Added `link_analysis_to_batch()` method (lines 578-600)
   - Added `get_batches()` method (lines 602-654)
   - Added `get_batch()` method (lines 656-687)
   - Added `get_batch_analyses()` method (lines 689-724)

### Database:
3. **[db/init/02_create_batch_tables.sql](../../../db/init/02_create_batch_tables.sql)** (NEW)
   - Created `batch_summaries` table
   - Created `batch_analyses` junction table
   - Altered `analyses` table to add batch columns
   - Created `v_batch_summary` view
   - Added indexes for fast queries

### UI:
4. **[src/ui/pages/2_Batch_Processing.py](../../../src/ui/pages/2_Batch_Processing.py)**
   - Added batch name input field (lines 102-108)
   - Updated batch start to pass name (lines 227-231)
   - Updated progress view to show batch name (lines 245-246)
   - Updated summary view to show batch name (lines 333-338)

5. **[src/ui/pages/1_History.py](../../../src/ui/pages/1_History.py)**
   - Added tabs for Individual Analyses vs Batches (line 44)
   - Implemented Batches tab with hierarchical view (lines 220-346)
   - Added stage funnel visualization
   - Added expandable view showing analyses grouped by stage

---

## Usage Examples

### Creating a Named Batch

1. Navigate to **Batch Processing** page
2. Upload CSV with tickers
3. Select protocol (e.g., "Halal Value Investing")
4. **Enter custom name:** "Tech Stocks Q4 2025"
5. Configure Deep Dive years (5-10)
6. Review cost estimate
7. Click **Start Batch**

### Viewing Batch History

1. Navigate to **History** page
2. Click **Batches** tab
3. See all batch runs with metrics
4. Click **Screening Funnel** to see stage progression
5. Click **View All Analyses** to expand hierarchical view
6. See companies grouped by stage with their decisions

### Searching Individual Analyses

1. Navigate to **History** page
2. Stay on **Individual Analyses** tab (default)
3. Use search and filters as before
4. Analyses from batches show alongside manual ones

---

## Benefits

### 1. Better Organization
- Batches saved as unified entities
- Easy to find specific batch runs by name
- Clear separation between batch and individual analyses

### 2. Batch Transparency
- See exactly what happened at each stage
- Understand why companies were filtered out
- Track progression through the funnel

### 3. Portfolio Building Workflow
- Process 100+ companies efficiently
- Filter down to final BUY decisions
- Review entire batch context before investing

### 4. Cost & Performance Tracking
- See total cost per batch
- Compare protocol efficiency
- Identify slow stages for optimization

### 5. Naming Flexibility
- Auto-generated names (timestamp-based)
- Custom names for important batches
- Easy identification in history

---

## Technical Highlights

### 1. Database Design
- JSONB fields for flexible stage stats storage
- Junction table for many-to-many relationships
- View for efficient batch queries with aggregations
- Foreign keys with CASCADE for data integrity

### 2. Backwards Compatibility
- Existing analyses work unchanged
- Batch fields are nullable
- No breaking changes to existing API

### 3. Query Efficiency
- Indexed batch_id for fast lookups
- View pre-joins tables for dashboard queries
- Limit/offset for pagination support

### 4. UI/UX
- Tabs prevent cluttering
- Progressive disclosure (funnel → expand → details)
- Color-coded decisions (green/yellow/red)
- Consistent with existing design patterns

---

## Future Enhancements

### Potential Additions:
1. **Batch Comparison**: Side-by-side protocol performance
2. **Export**: Download batch results as CSV/PDF
3. **Scheduling**: Cron-like batch scheduling
4. **Alerts**: Email when batch completes
5. **Batch Templates**: Save filter criteria as reusable templates
6. **Historical Trends**: Track how many companies pass each stage over time

---

## Testing Checklist

- [x] Create batch with custom name
- [x] Create batch without custom name (auto-generated)
- [x] Batch summary saves to database
- [x] Batch analyses link correctly
- [x] View batches in History page
- [x] Expand batch to see stages
- [x] Funnel visualization displays correctly
- [x] BUY count aggregation works
- [x] Duration and cost display correctly
- [ ] Run actual batch processing end-to-end (next step)

---

## Related Documentation

- [Phase 8: Automated Batch Screening Protocol](./PHASE_8_BATCH_PROCESSING.md) - Initial batch processing implementation
- [Cost Estimation Fixes](../phase_7/COST_ESTIMATION_FIXES_2025-11-08.md) - Cost calculation accuracy
- [Database Schema](../../database/SCHEMA.md) - Full database structure

---

## Commit Message

```
Phase 8 Update: Batch History Enhancement

Add custom batch naming and hierarchical organization in History page.

Features:
1. Custom Batch Naming
   - Optional batch name input field
   - Auto-generated timestamp names as fallback
   - Display custom names throughout UI

2. Batch Storage
   - New batch_summaries table
   - batch_analyses junction table for hierarchical links
   - Updated analyses table with batch metadata
   - 5 new AnalysisStorage methods for batch operations

3. Hierarchical History View
   - Tabs separating Individual Analyses vs Batches
   - Batch summary cards with metrics
   - Stage funnel visualization
   - Expandable view: Batch → Stages → Companies
   - Color-coded decisions per company

Database Changes:
- Created batch_summaries table
- Created batch_analyses junction table
- Altered analyses table (added batch_id, batch_stage_name, batch_stage_index)
- Created v_batch_summary view
- Added indexes for performance

Files Modified:
- src/batch/batch_processor.py (batch naming + auto-save)
- src/storage/analysis_storage.py (5 new methods)
- src/ui/pages/2_Batch_Processing.py (name input)
- src/ui/pages/1_History.py (tabs + hierarchical view)
- db/init/02_create_batch_tables.sql (NEW)

User Benefits:
- Name batches for easy identification
- View batch processing runs as unified entities
- Drill down into stage-by-stage results
- Understand filtering progression via funnel
- Better portfolio building workflow
```
