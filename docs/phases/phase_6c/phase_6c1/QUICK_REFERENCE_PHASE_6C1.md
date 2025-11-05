# Quick Reference: Phase 6C.1 - Analysis History with Docker Database

**Phase:** 6C.1 - Storage, Search & History
**Database:** PostgreSQL in Docker
**Time Needed:** ~7 hours
**Strategic Value:** CRITICAL (Foundation for everything else)

---

## 🎯 What You're Building

### **The Complete History System**

```
Before Phase 6C.1:
├─ Run analysis
├─ See results
└─ Results disappear when you close browser

After Phase 6C.1:
├─ Run analysis
├─ Auto-saved to database + files
├─ Search any past analysis instantly
├─ Filter by type, decision, date, metrics
├─ View complete history
├─ Track portfolio candidates
└─ Re-analyze anytime
```

---

## 🏗️ Architecture Overview

### **Why Hybrid Storage?**

```
PostgreSQL Database (Docker)
├─ Fast search (milliseconds)
├─ Complex queries
├─ Relationships
├─ Statistics
└─ Indexes for speed

File System (JSON)
├─ Complete analysis content
├─ Easy to backup
├─ Human-readable
└─ Portable

Together = Best of Both Worlds!
```

---

## 📁 Directory Structure You'll Get

```
basīrah_analyses/
├── deep_dive/
│   ├── buy/
│   │   ├── AAPL_2025-11-04_buy_10y.json
│   │   ├── MSFT_2025-11-04_buy_5y.json
│   │   └── V_2025-11-03_buy_10y.json
│   ├── watch/
│   │   └── GOOG_2025-11-04_watch_3y.json
│   └── avoid/
│       └── F_2025-11-02_avoid_5y.json
│
├── quick_screen/
│   ├── investigate/
│   │   ├── AAPL_2025-11-02_investigate.json
│   │   └── COST_2025-11-01_investigate.json
│   └── pass/
│       └── F_2025-11-02_pass.json
│
└── sharia_screen/
    ├── compliant/
    │   ├── MSFT_2025-11-03_compliant.json
    │   └── V_2025-11-01_compliant.json
    ├── doubtful/
    │   └── AAPL_2025-11-03_doubtful.json
    └── non_compliant/
        └── JPM_2025-11-01_non_compliant.json
```

---

## 🔍 Search Capabilities

### **Basic Search**

```python
# Quick ticker search
Search: "AAPL"
→ Shows all analyses of Apple
→ Across all types (Quick, Deep, Sharia)
→ Sorted by date

# Date filters
"Last 7 days"
"Last 30 days"
"Last 90 days"
"Custom range"

# Type filters
☑ Quick Screen
☑ Deep Dive
☑ Sharia Compliance

# Decision filters
☑ BUY ☑ WATCH ☑ AVOID
☑ INVESTIGATE ☑ PASS
☑ COMPLIANT ☑ DOUBTFUL ☑ NON-COMPLIANT
```

### **Advanced Search**

```python
# Multi-criteria search
Example: "High-conviction BUY decisions from last month"
→ Type: Deep Dive
→ Decision: BUY
→ Conviction: HIGH
→ Date: Last 30 days
→ Result: 3 analyses

# Financial metrics search
Example: "Companies with ROIC > 30%"
→ Min ROIC: 30%
→ Result: 12 analyses

Example: "Undervalued companies (MoS > 20%)"
→ Min Margin of Safety: 20%
→ Decision: BUY
→ Result: 5 analyses
```

### **Sort Options**

```python
Sort by:
- Date (newest/oldest)
- Ticker (A-Z)
- Cost (high/low)
- ROIC (high/low)
- Margin of Safety (high/low)
- Decision
```

---

## 🐘 Database Schema (PostgreSQL)

### **Main Tables**

```sql
companies
├─ ticker, company_name
├─ sector, industry
├─ total_analyses
└─ first/last analyzed

analyses (main storage)
├─ ticker, company_name
├─ analysis_type (quick/deep_dive/sharia)
├─ decision, conviction
├─ intrinsic_value, current_price, margin_of_safety
├─ roic, sharia_status, purification_rate
├─ cost, duration, token_usage
├─ thesis_preview, thesis_full
└─ file_path

tags
├─ Portfolio, Watchlist, High Priority
├─ Halal, Re-screen, Archived
└─ Custom tags

saved_searches
├─ Save frequent searches
└─ One-click filtering
```

### **Indexes for Speed**

```sql
Fast queries on:
├─ ticker
├─ analysis_date
├─ analysis_type
├─ decision
├─ conviction
├─ sharia_status
└─ Full-text search on thesis
```

---

## 🎨 UI Mockup

### **History Page**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Analysis History
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Overview
┌────────────┬────────────┬────────────┬────────────┐
│   Total    │  Unique    │   Total    │   Total    │
│ Analyses   │ Companies  │    Cost    │    Time    │
│    86      │     67     │  $285.50   │   12.3h    │
└────────────┴────────────┴────────────┴────────────┘

🔍 Search & Filter
┌─────────────────────────────────────────────────┐
│ Quick Search: [AAPL_________________] [Clear]   │
└─────────────────────────────────────────────────┘

⚙️ Advanced Filters
┌─ Analysis Type ─┬─ Decision ──┬─ Date Range ──┐
│ ☑ Quick Screen  │ ☑ BUY       │ Last 30 days  │
│ ☑ Deep Dive     │ ☑ WATCH     │ [Custom...]   │
│ ☑ Sharia Screen │ ☑ AVOID     │               │
└─────────────────┴─────────────┴───────────────┘

Sort by: [Date ▼] [Newest First ▼]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Results (8 found)

┌────────────────────────────────────────────────┐
│ AAPL - Apple Inc.              🔍 Deep Dive    │
│ BUY (HIGH conviction)          Nov 4, 2025     │
│ ROIC: 48% | MoS: 18% | IV: $220 | Price: $180 │
│ "Apple represents an exceptional business..."  │
│ [👁️ View] [📥 Download] [🔄 Re-analyze] [🗑️]  │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ AAPL - Apple Inc.              ☪️ Sharia       │
│ DOUBTFUL (2.3% purification)   Nov 3, 2025     │
│ Interest income & entertainment concerns        │
│ [👁️ View] [📥 Download] [🗑️ Delete]            │
└────────────────────────────────────────────────┘

[... more results ...]
```

### **Statistics Dashboard**

```
📈 Detailed Statistics

By Analysis Type:          By Decision:
- Quick Screens: 45        - BUY: 8 ⭐
- Deep Dives: 23           - WATCH: 12
- Sharia Screens: 18       - AVOID: 3
                           - INVESTIGATE: 25
                           - PASS: 20

By Sharia Status:          Date Range:
- Compliant: 10            First: Sept 1, 2025
- Doubtful: 6              Last: Nov 5, 2025
- Non-Compliant: 2

Average Cost: $3.32 per analysis
Total Time: 12.3 hours
```

---

## 🐳 Docker Setup

### **What Gets Installed**

```
Docker Container: basirah_db
├─ PostgreSQL 16 (Alpine - lightweight)
├─ Port: 5432
├─ Database: basirah
├─ User: basirah_user
└─ Volume: postgres_data (persistent storage)
```

### **Setup Commands**

```bash
# 1. Run setup script
./setup_database.sh

# 2. Verify running
docker ps | grep basirah_db

# 3. Check health
docker exec basirah_db pg_isready -U basirah_user

# 4. View logs
docker logs basirah_db

# 5. Connect to database
docker exec -it basirah_db psql -U basirah_user -d basirah
```

### **Management Commands**

```bash
# Start database
docker-compose up -d

# Stop database
docker-compose down

# Restart database
docker-compose restart

# View logs
docker-compose logs -f postgres

# Backup database
docker exec basirah_db pg_dump -U basirah_user basirah > backup.sql

# Restore database
docker exec -i basirah_db psql -U basirah_user basirah < backup.sql

# Remove everything (including data)
docker-compose down -v
```

---

## 💻 Code Structure

### **New Files (9)**

```
docker-compose.yml              # Docker config
db/init/01_create_schema.sql   # Database schema
setup_database.sh               # Setup script

src/storage/
├─ database.py                  # DB connection manager
├─ analysis_storage.py          # Save/load analyses
└─ search_engine.py             # Search & filter

src/ui/
└─ history.py                   # History browser UI

.env.example                    # Config template
requirements.txt                # Add psycopg2-binary
```

### **Modified Files (2)**

```
src/ui/app.py
├─ Initialize storage
├─ Auto-save after analysis
└─ Add history navigation

.env
└─ Add database config
```

---

## 📊 Example Workflows

### **Workflow 1: Portfolio Management**

```
1. Run deep dives on 10 companies
2. 3 get BUY decisions with HIGH conviction
3. Go to History → Filter: BUY + HIGH conviction
4. See your portfolio candidates
5. Export to CSV
6. Track over time
```

### **Workflow 2: Halal Investing**

```
1. Sharia screen 50 companies
2. 30 are COMPLIANT
3. Quick screen these 30
4. 12 say INVESTIGATE
5. Deep dive these 12
6. 4 get BUY decisions
7. Result: Halal high-quality portfolio
8. All saved and searchable
```

### **Workflow 3: Re-screening**

```
1. Search: "analyses from 6 months ago"
2. Find AAPL analysis from May
3. Click "Re-analyze"
4. Compare old vs new thesis
5. Detect changes in business/valuation
6. Update investment decision
```

### **Workflow 4: Sector Research**

```
1. Search: "tech companies"
2. Filter: Deep Dive + BUY
3. Sort by: ROIC (highest first)
4. Compare: AAPL vs MSFT vs GOOG
5. Best risk/reward?
6. Margin of safety?
```

---

## ✅ Testing Checklist

### **Database Setup**
- [ ] Docker installed and running
- [ ] Run `./setup_database.sh`
- [ ] Database container starts
- [ ] Health check passes
- [ ] Can connect via psql
- [ ] Schema created (9 tables)
- [ ] Indexes created

### **Storage System**
- [ ] Run analysis on AAPL
- [ ] "Analysis saved" message shows
- [ ] File created in correct directory
- [ ] Database record created
- [ ] Can load analysis back
- [ ] Can delete analysis

### **Search Functionality**
- [ ] Quick search by ticker works
- [ ] Date filters work
- [ ] Type filters work
- [ ] Decision filters work
- [ ] Financial metric filters work
- [ ] Sort options work
- [ ] Statistics show correct data

### **UI Testing**
- [ ] History page loads
- [ ] Search interface works
- [ ] Results display correctly
- [ ] View full analysis works
- [ ] Download JSON works
- [ ] Re-analyze button works
- [ ] Delete button works
- [ ] No errors in console

---

## 🚀 Implementation Steps

### **Quick Start (7 hours)**

```
Hour 1: Database Setup
├─ Create docker-compose.yml
├─ Create schema.sql
├─ Run setup script
└─ Test connection

Hours 2-3: Storage System
├─ Create database.py
├─ Create analysis_storage.py
└─ Test save/load

Hours 3-4: Search Engine
├─ Create search_engine.py
└─ Test queries

Hours 5-6: UI Implementation
├─ Create history.py
├─ Build search interface
└─ Build results display

Hour 7: Integration & Testing
├─ Integrate with main app
├─ Test complete workflow
└─ Fix any bugs
```

---

## 💰 Cost Impact

**Storage Costs:**
- PostgreSQL: FREE (runs locally)
- Disk space: ~1 MB per 100 analyses
- No cloud costs

**Analysis Costs: (unchanged)**
- Quick Screen: $0.75-$1.50
- Deep Dive: $2.50-$7
- Sharia Screen: $1.50-$2.50

**Benefit:**
- Never lose an analysis
- Never pay twice for same company
- Build knowledge base over time

---

## 🎯 Success Metrics

**After Phase 6C.1, you'll have:**

```
✅ Persistent storage for all analyses
✅ Fast search (<100ms for any query)
✅ Organized directory structure
✅ Beautiful history browser
✅ Statistics dashboard
✅ Portfolio candidate tracking
✅ Re-analysis capability
✅ Audit trail for decisions

Foundation for:
→ Phase 6C.2: Batch Processing
→ Phase 6C.3: Portfolio Management
→ Phase 7: Multi-user & API
```

---

## 🔧 Troubleshooting

### **Docker Issues**

```bash
# Docker not running?
sudo systemctl start docker

# Port 5432 already in use?
docker-compose down
# Change port in docker-compose.yml

# Container won't start?
docker-compose logs postgres
# Check error messages

# Permission denied?
sudo chown -R $USER:$USER .
```

### **Database Issues**

```bash
# Can't connect?
# Check .env file has correct credentials

# Schema not created?
docker exec -it basirah_db psql -U basirah_user -d basirah -f /docker-entrypoint-initdb.d/01_create_schema.sql

# Wrong password?
# Update DB_PASSWORD in .env
# Restart: docker-compose restart
```

### **Python Issues**

```bash
# psycopg2 won't install?
pip install psycopg2-binary

# Import errors?
pip install -r requirements.txt

# Connection timeout?
# Check firewall, Docker network
```

---

## 📥 Files to Download

**Main Implementation:**
- [BUILDER_PROMPT_PHASE_6C1.txt](computer:///mnt/user-data/outputs/BUILDER_PROMPT_PHASE_6C1.txt) ⭐

**Reference:**
- QUICK_REFERENCE_PHASE_6C1.md (This file)

---

## 🎊 What's Next: Phase 6C.2

**After Phase 6C.1, you can build:**

```
Phase 6C.2: Batch Processing
├─ Upload CSV with 500 companies
├─ Run: Sharia → Quick → Deep protocol
├─ Automated screening pipeline
├─ Progress tracking
├─ Summary report
└─ Cost savings: 50-70%

All analyses auto-saved to your new database!
```

---

## 💡 Pro Tips

**1. Regular Backups**
```bash
# Daily backup script
docker exec basirah_db pg_dump -U basirah_user basirah > backups/basirah_$(date +%Y%m%d).sql
```

**2. Performance Monitoring**
```sql
-- Check table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables 
WHERE schemaname = 'public';

-- Check slow queries
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

**3. Data Maintenance**
```python
# Clean up old analyses (>1 year)
search.search(date_to="2024-01-01")
# Review and delete as needed
```

---

## 🚀 Ready to Build!

**Phase 6C.1 is the foundation** that transforms basīrah from a one-off analysis tool into a **professional investment research platform**.

**Time Investment:** 7 hours  
**Strategic Value:** CRITICAL  
**Enables:** Batch processing, portfolio management, long-term tracking

**Download the builder prompt and let's create your investment knowledge base!** 🎯

---

*Phase 6C.1: Analysis History with Docker Database & Search*
*The foundation for everything that follows*
*Status: Ready for Implementation*
