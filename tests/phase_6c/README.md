# Phase 6C.1 Test Suite

This directory contains comprehensive tests for Phase 6C.1: Analysis History with Docker Database & Search.

## Test Files

### 1. test_database_setup.py

**Purpose:** Validates core infrastructure setup

**Tests (9 total):**
- Docker environment validation
- PostgreSQL container health check
- Database connection verification
- Schema creation verification
- Table structure validation
- CRUD operations
- Full-text search functionality
- Index verification
- Trigger functionality

**Run:**
```bash
python tests/phase_6c/test_database_setup.py
```

**Expected Output:**
```
[OK] Docker is installed
[OK] Docker container 'basirah_db' is running
[OK] Can connect to PostgreSQL database
[OK] All required tables exist (7/7)
[OK] Can insert test company
[OK] Can query test company
[OK] Full-text search is working
[OK] Indexes are created (10+ indexes)
[OK] Triggers are working

[RESULTS] 9/9 tests passed
```

---

### 2. test_storage_search.py

**Purpose:** Validates storage and search engine functionality

**Tests (7 total):**
- Save analysis (all types)
- Load analysis from storage
- Search functionality (multi-criteria)
- Quick search (ticker/company)
- Statistics generation
- Company tracking
- Tag management

**Run:**
```bash
python tests/phase_6c/test_storage_search.py
```

**Expected Output:**
```
[OK] Can save deep dive analysis
[OK] Can save quick screen analysis
[OK] Can save Sharia analysis
[OK] Can load saved analysis
[OK] Search with filters works
[OK] Quick search works
[OK] Statistics generation works

[RESULTS] 7/7 tests passed
```

---

### 3. test_delete_functionality.py

**Purpose:** Validates delete functionality and cascade behavior

**Tests (2 test groups):**
- Complete delete workflow
  - Creates test analysis
  - Verifies database record
  - Verifies file exists
  - Deletes analysis
  - Confirms removal from database
  - Confirms file deletion
  - Verifies load returns None

- Cascade delete behavior
  - Creates multiple analyses for same company
  - Deletes one analysis
  - Verifies other analyses remain
  - Confirms proper cascade handling

**Run:**
```bash
python tests/phase_6c/test_delete_functionality.py
```

**Expected Output:**
```
[OK] Test analysis created: DELTEST_2025-11-05_buy_3y
[OK] Analysis found in database
[OK] File exists
[OK] Delete operation successful
[OK] Analysis removed from database
[OK] File successfully deleted
[OK] load_analysis correctly returns None

[SUCCESS] All delete functionality tests passed!

[OK] Created analysis 1
[OK] Created analysis 2
[OK] Found 2 analyses for CASTEST
[OK] Deleted first analysis
[OK] One analysis remains

[RESULTS] 2/2 test groups passed
```

---

### 4. test_sharia_search_fix.py

**Purpose:** Validates Sharia analyses appear in search results

**Tests (4 tests):**
- Search with all decision types (finds Sharia analyses)
- Search with only Sharia decisions (finds Sharia analyses)
- Search without Sharia decisions (correctly excludes them)
- Quick search (finds Sharia analyses)

**Run:**
```bash
python tests/phase_6c/test_sharia_search_fix.py
```

**Expected Output:**
```
Testing Sharia Analysis Search Fix
============================================================

1. Testing search with all decision types...
   [OK] TSLA found in results!

2. Testing search with only Sharia decisions...
   [OK] TSLA found with Sharia filter!

3. Testing search WITHOUT Sharia decisions (old behavior)...
   [OK] TSLA correctly excluded when Sharia decisions not in filter

4. Testing quick search...
   [OK] Quick search finds TSLA (1 result(s))

[SUCCESS] All Sharia search tests passed!
```

---

### 5. test_empty_database.py

**Purpose:** Validates graceful handling of empty database edge case

**Tests (2 test groups):**
- Empty database statistics
  - Verifies all statistics can be safely accessed
  - Tests f-string formatting with None values
  - Checks breakdown dictionaries
  - Validates UI display won't crash

- Search with empty database
  - Quick search returns empty list
  - Advanced search returns empty list
  - Recent analyses returns empty list

**Run:**
```bash
python tests/phase_6c/test_empty_database.py
```

**Expected Output:**
```
Testing Empty Database Statistics
============================================================

1. Getting statistics from database...
   Retrieved statistics: {'total_cost': None, ...}

2. Checking each statistic value...
   Total Analyses: 0
   Total Cost: $0.00

3. Testing f-string formatting (like in UI)...
   [OK] Formatting works correctly

[SUCCESS] Empty database statistics handled correctly!

Testing Search with Empty Database
============================================================

1. Testing quick search...
   [OK] Quick search returns empty list

2. Testing advanced search...
   [OK] Advanced search returns empty list

[SUCCESS] All empty database tests passed!
```

**Note:** This test works best with an empty database. If you have analyses, the test will still pass but won't fully test the edge case.

---

## Running All Tests

### Quick Run (All Tests)

```bash
# From project root
python tests/phase_6c/test_database_setup.py
python tests/phase_6c/test_storage_search.py
python tests/phase_6c/test_delete_functionality.py
python tests/phase_6c/test_sharia_search_fix.py
python tests/phase_6c/test_empty_database.py
```

### Expected Total Results

```
Infrastructure Tests:     9/9  ✅
Storage & Search Tests:   7/7  ✅
Delete Functionality:     2/2  ✅
Sharia Search Fix:        4/4  ✅
Empty Database Edge Case: 2/2  ✅
------------------------------
Total:                   24/24 ✅
```

---

## Prerequisites

### 1. Docker Running

```bash
# Start database
docker-compose up -d

# Verify container
docker ps | grep basirah_db
```

### 2. Python Dependencies

```bash
# Install requirements
pip install -r requirements.txt
```

### 3. Environment Variables

Ensure `.env` contains:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=basirah
DB_USER=basirah_user
DB_PASSWORD=basirah_secure_password_2025
```

---

## Test Data

Tests create temporary data:
- Test companies: `TEST_CO`, `DELTEST`, `CASTEST`
- Test analyses in: `basīrah_analyses/` directory
- Database records in test tables

**Cleanup:**
- Tests clean up their own data
- Test data is identifiable by ticker prefixes (TEST*, DEL*, CAS*)

---

## Troubleshooting

### Docker Not Running

**Error:**
```
[FAIL] Docker container 'basirah_db' is not running
```

**Solution:**
```bash
docker-compose up -d
# Wait 5 seconds for container to be healthy
docker ps
```

### Database Connection Failed

**Error:**
```
[FAIL] Cannot connect to PostgreSQL database
```

**Solution:**
```bash
# Check container logs
docker logs basirah_db

# Verify credentials in .env
cat .env | grep DB_

# Restart container
docker-compose restart
```

### Schema Not Created

**Error:**
```
[FAIL] Required tables do not exist
```

**Solution:**
```bash
# Recreate database
docker-compose down -v
docker-compose up -d

# Wait for initialization
sleep 10

# Run test again
python tests/phase_6c/test_database_setup.py
```

### Unicode Encoding Errors (Windows)

**Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Note:**
- Tests use ASCII equivalents ([OK], [FAIL]) instead of emojis
- If you see this error, the test file may need updating

---

## Test Architecture

### Test Structure

```python
def test_feature():
    """Test a specific feature."""
    try:
        # Setup
        setup_test_data()

        # Execute
        result = perform_operation()

        # Verify
        assert result == expected
        print("[OK] Test passed")
        return True

    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        cleanup_test_data()
```

### Best Practices

1. **Isolation:** Each test is independent
2. **Cleanup:** Tests clean up after themselves
3. **Clear Output:** Easy to identify failures
4. **Traceback:** Full error details on failure
5. **Return Boolean:** True for pass, False for fail

---

## Coverage

### Database Layer
✅ Connection pooling
✅ Schema creation
✅ CRUD operations
✅ Full-text search
✅ Indexes
✅ Triggers
✅ Views
✅ Cascade deletes

### Storage Layer
✅ Save analyses (all types)
✅ Load analyses
✅ Delete analyses
✅ File system organization
✅ Metadata extraction
✅ Error handling

### Search Layer
✅ Quick search
✅ Advanced search
✅ Multi-criteria filtering
✅ Date range queries
✅ Metric thresholds
✅ Sorting
✅ Limiting
✅ Statistics

### Integration
✅ Hybrid storage (DB + files)
✅ Auto-save flow
✅ Delete with cascade
✅ Company tracking
✅ Tag management

---

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example: GitHub Actions
name: Phase 6C.1 Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: basirah
          POSTGRES_USER: basirah_user
          POSTGRES_PASSWORD: basirah_secure_password_2025
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run Phase 6C.1 Tests
        run: |
          python tests/phase_6c/test_database_setup.py
          python tests/phase_6c/test_storage_search.py
          python tests/phase_6c/test_delete_functionality.py
```

---

## Maintenance

### Updating Tests

When adding new features to Phase 6C.1:

1. **Add new test function** to appropriate test file
2. **Follow naming convention:** `test_<feature_name>()`
3. **Include in main()** function
4. **Update test count** in summary
5. **Document in this README**

### Test Data Management

- Use unique ticker prefixes for test data
- Always clean up in `finally` blocks
- Don't interfere with production data
- Keep test data minimal but representative

---

## Documentation

For complete Phase 6C.1 documentation, see:
- **Completion Summary:** `docs/phases/phase_6c/phase_6c1_completion.md`
- **Database Schema:** `db/init/01_create_schema.sql`
- **Storage API:** `src/storage/analysis_storage.py`
- **Search API:** `src/storage/search_engine.py`

---

**Last Updated:** November 5, 2025
**Status:** All tests passing (24/24) ✅
