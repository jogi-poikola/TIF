# TIF Position Management System - Changelog

This file tracks significant changes and improvements to the TIF position management system.

---

## 2025-11-13 - Provenance Tracking Fix

### Accomplishments
- Fixed position migration to preserve source provenance in `related:` field
- Retroactively added provenance to 16 existing positions
- Enhanced YAML parser to handle multi-line list fields

### Changes
- **Migration Script:** Enhanced `migrate_positions.py` to preserve `related:` field from drafts
- **YAML Parser:** Now correctly parses multi-line YAML lists (e.g., `related:` with `-` items)
- **Backfill Tool:** Created `backfill_related_fields.py` to retroactively add missing provenance
- **Position Files:** Updated 16 positions with missing `related:` fields

### Files Modified
- `.claude/skills/position-migration/scripts/migrate_positions.py` - Enhanced parser and frontmatter generation
- `.claude/skills/position-migration/scripts/backfill_related_fields.py` - New utility (217 lines)
- `position-migration.zip` - Rebuilt with fixes
- 16 position files in `positions/` - Added `related:` field with source links

### Technical Details
- **Parser Enhancement:** Lines 146-178 now handle YAML list parsing correctly
- **Frontmatter Generation:** Lines 544-565 preserve `related:` field from drafts
- **Backfill Logic:** Extracts source links from `## [[source-file]]` headings and adds to frontmatter

### Impact
- All future position migrations automatically preserve provenance
- Existing positions now have proper Obsidian-navigable source links
- Improved traceability from canonical positions back to source files

---

## 2025-11-12 - URL Discovery and Website Crawling

### Accomplishments
- Created comprehensive URL list for entire `/tavoitteemme/` section of TIF website
- Crawled website to discover all hierarchical URLs under main objectives section

### Changes
- **Documentation:** Created `tavoitteemme-urls.md` with 61 discovered URLs
- **Discovery:** Mapped complete URL structure across 10 main categories and 50 sub-pages

### Files Created
- `tavoitteemme-urls.md` - Hierarchical list of all TIF objectives URLs

### Summary
- **61 unique URLs** discovered and catalogued
- **10 main categories** (Viestimme päättäjille, Osaava työvoima, Työelämä, Energia ja ilmasto, etc.)
- **50 sub-pages** across all categories
- **Hierarchical structure** organized for easy navigation

---

## 2025-11-12 - Documentation Update and Session Management

### Accomplishments
- Comprehensive documentation overhaul for all automation features
- Created session management workflow for clean session closes
- Updated architecture documentation to reflect semantic naming system

### Changes
- **Documentation:** Updated CLAUDE.md and ARCHITECTURE.md with complete automation details
- **Commands:** Created `/session-close` command for session management
- **Architecture:** Documented semantic naming system (no number prefixes), agent-based parallelism, and auto mode
- **Workflow:** Documented three workflow modes (automated, batch parallel, manual)

### Files Modified
- `CLAUDE.md` - Added comprehensive commands section, updated automation workflows
- `ARCHITECTURE.md` - Complete rewrite for semantic system, added workflows, skills, and algorithms
- `.claude/commands/session-close.md` - New session closing command

### Key Features Documented
- **Auto mode migration:** ≥80% merge, 70-80% skip, <70% create with keyword classification
- **Title generation:** Claude Code integration (no API key needed)
- **Agent-based parallelism:** True parallel processing via Task tool
- **Version tracking:** Date-based filenames for all sources
- **Three-tier workflow:** Automated, batch parallel, and manual modes

### System Status
- **6 skills:** All documented (tif-web-scraper, source-diff, position-extractor, position-migration, auto-process-source, batch-processor)
- **6 commands:** All documented (extract-positions, auto-process, batch-process-parallel, re-scrape, generate-position-title, session-close)
- **~130 positions:** In semantic hierarchical structure
- **Fully automated:** End-to-end processing with one command

---

