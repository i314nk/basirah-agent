# Changelog

All notable changes to basīrah will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Real-time progress reporting for multi-year analyses with year-by-year updates
- Progress bar showing 0-100% completion during Deep Dive analyses
- Missing 10-K filing tracking and reporting in UI and metadata
- Dynamic fiscal year calculation (automatically adjusts each year)
- Warning display in UI when requested years are unavailable
- Context management metadata fields: `years_requested`, `years_skipped`, `years_skipped_count`

### Fixed
- **Critical:** Extended Thinking format violation causing 400 errors during context pruning
- **Critical:** Context window overflow (202K tokens > 200K limit) in 10-year analyses
- **Critical:** Inverted margin of safety requirements (wide moat required 40%, now correctly 15-20%)
- Hardcoded fiscal year 2024 (now dynamically calculated as `current_year - 1`)
- Inefficient handling of missing 10-K filings (pre-check now implemented)
- UI stuck on "Stage 1" during long analyses (now updates in real-time)

### Changed
- Context pruning threshold reduced from 150K to 100K tokens (more conservative)
- Minimum recent messages kept reduced from 8 to 4 (more aggressive pruning)
- Context pruning no longer inserts summary messages (Extended Thinking compatibility)
- Missing years are now skipped immediately instead of retrying multiple times
- UI shows "Most recent fiscal year" instead of "Current year" for clarity

### Performance
- 95% reduction in context token usage (202K → 10K for 10-year analyses)
- ~40% faster analysis time (no wasted iterations on missing filings)
- More reliable completion of 10-year Deep Dive analyses

### Documentation
- Added comprehensive bug fix documentation: [docs/bug_fixes/2025-11-06_multi_year_analysis_fixes.md](docs/bug_fixes/2025-11-06_multi_year_analysis_fixes.md)
- Added bug fixes summary: [docs/bug_fixes/SUMMARY.md](docs/bug_fixes/SUMMARY.md)
- Updated main README with bug fixes section

## [Phase 6C.1] - 2025-11-01

### Added
- PostgreSQL database integration running in Docker
- Analysis History Browser with multi-criteria search
- Auto-save for all analyses (Deep Dive, Quick Screen, Sharia)
- Hybrid storage system (metadata in DB, full content in files)
- Full-text search across analysis thesis
- Filter by ticker, decision, date range, analysis type
- Financial metrics range filtering (intrinsic value, margin of safety)
- Company-level analytics (track companies over time)
- Delete company feature (removes all analyses for a company)
- Stale company filter (only show companies with recent analyses)

### Fixed
- Quick Screen decision detection (investigate vs pass)
- Storage system incorrectly classifying Quick Screens as Deep Dives
- Duplicate key constraint violations in analysis IDs
- Confidence level extraction from Quick Screen results
- Key metrics hiding for Quick Screen analyses

## [Phase 6B.2] - 2025-10-28

### Added
- Sharia Compliance screening with AAOIFI standards
- Interest-bearing debt analysis
- Impermissible income detection and quantification
- Illiquid assets assessment
- Three-tier decision system: COMPLIANT / DOUBTFUL / NON_COMPLIANT
- Islamic financial principles integration
- Purification calculation for doubtful investments

## [Phase 6B.1] - 2025-10-27

### Added
- Enhanced Quick Screen with INVESTIGATE/PASS recommendations
- Confidence level extraction (High/Medium/Low)
- Smart decision logic for quick business assessment
- 2-3 minute screening before expensive Deep Dive
- Cost-effective initial filtering ($0.75-$1.50 per screen)

## [Phase 6A.2] - 2025-10-25

### Added
- Real-time token usage tracking and cost display
- Session-level cost aggregation across multiple analyses
- Arabic translation with one-click conversion
- Proper RTL (right-to-left) formatting for Arabic text
- Cost breakdown by analysis vs translation
- Session totals with analysis counter

## [Phase 6A.1] - 2025-10-24

### Added
- Configurable years selector (1-10 years for Deep Dive)
- Dynamic cost and time estimates based on configuration
- Complete thesis fix ensuring all 10 sections are generated
- Improved synthesis prompt with explicit structure requirements

### Fixed
- Incomplete thesis generation (agent now always produces full analysis)
- Missing sections in multi-year synthesis

## [Phase 6A.0] - 2025-10-23

### Added
- Professional Streamlit web interface
- Real-time progress indicators
- Export functionality (JSON and Markdown)
- Mobile-responsive design
- Analysis metadata display
- Cost tracking in UI

## [Phase 5.0] - 2025-10-30

### Added
- Progressive summarization for multi-year analysis
- Adaptive strategy selection based on filing size
- Three-stage analysis: current year → prior years → synthesis
- Context management for large 10-K filings (up to 552K characters)
- 100% S&P 500 coverage achieved

### Changed
- Switched from single-pass to three-stage analysis
- Introduced 400K character threshold for adaptive summarization
- Enhanced prompt structure for complete thesis generation

## [Phase 4.0] - 2025-10-20

### Added
- Extended Thinking integration (8K token budget)
- ReAct (Reasoning + Acting) agent loop
- Comprehensive error handling
- Production-ready deployment configuration

## [Phase 3.0] - 2025-10-15

### Added
- Web search integration for market research
- Economic moat analysis framework
- Management quality evaluation
- Risk assessment with top 5 risks identification

## [Phase 2.0] - 2025-10-10

### Added
- GuruFocus API integration for financial data
- Calculator tool for DCF valuations
- Owner earnings calculation
- ROIC analysis

## [Phase 1.0] - 2025-10-05

### Added
- Initial Warren Buffett AI agent implementation
- SEC EDGAR integration for 10-K retrieval
- Basic investment thesis generation
- Tool-based architecture foundation

---

## Migration Notes

### Upgrading to Latest Version

**⚠️ Restart Required:**
Streamlit caches the `WarrenBuffettAgent` class. After updating, you must restart the Streamlit server:

```bash
# Stop current server (Ctrl+C)
streamlit run src/ui/app.py
```

**Database Migration:**
Phase 6C.1 introduced PostgreSQL. If upgrading from earlier versions:

```bash
# Start PostgreSQL container
docker-compose up -d

# Initialize database (automatic on first run)
streamlit run src/ui/app.py
```

**No Breaking Changes:**
All updates maintain backward compatibility with existing saved analyses.

---

## Support

For bug reports and feature requests:
- Documentation: [docs/bug_fixes/](docs/bug_fixes/)
- Issues: [GitHub Issues](https://github.com/yourusername/basira-agent/issues)

---

[Unreleased]: https://github.com/yourusername/basira-agent/compare/v6c.1...HEAD
[Phase 6C.1]: https://github.com/yourusername/basira-agent/releases/tag/v6c.1
[Phase 6B.2]: https://github.com/yourusername/basira-agent/releases/tag/v6b.2
[Phase 6B.1]: https://github.com/yourusername/basira-agent/releases/tag/v6b.1
[Phase 6A.2]: https://github.com/yourusername/basira-agent/releases/tag/v6a.2
[Phase 6A.1]: https://github.com/yourusername/basira-agent/releases/tag/v6a.1
[Phase 6A.0]: https://github.com/yourusername/basira-agent/releases/tag/v6a.0
[Phase 5.0]: https://github.com/yourusername/basira-agent/releases/tag/v5.0
[Phase 4.0]: https://github.com/yourusername/basira-agent/releases/tag/v4.0
[Phase 3.0]: https://github.com/yourusername/basira-agent/releases/tag/v3.0
[Phase 2.0]: https://github.com/yourusername/basira-agent/releases/tag/v2.0
[Phase 1.0]: https://github.com/yourusername/basira-agent/releases/tag/v1.0
