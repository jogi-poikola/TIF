# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a knowledge management repository containing Teknologiateollisuus (Technology Industries of Finland - TIF) position documents. The repository uses a hierarchical structure to organize policy positions and strategic areas, with automated workflows powered by Claude Code skills to scrape, extract, and classify position statements.

## Repository Structure

### Core Directories

- **`positions/`** - Semantic hierarchical structure containing all finalized position documents (~120+ files)
  - `0000 index.md` - Top-level overview document
  - `Resilienssi/` - Resilience and adaptation
  - `Kriittiset teknologiat/` - Critical technologies (semiconductors, quantum, AI, HPC)
  - `Osaaminen/` - Competence and skills
  - `Investointiympäristö/` - Investment environment
  - `Työelämä/` - Working life
  - `Kestävä kasvu/` - Sustainable growth
  - `Talous- ja veropolitiikka/` - Economic and tax policy
  - `Digitalisaatio ja datatalous/` - Digitalization and data economy
  - `Innovaatiot/` - Innovations

- **`sources/`** - Source materials scraped from TIF website
  - `TIF web/` - Web content organized by URL path structure
    - Contains markdown files with `type: web` frontmatter
    - Files named with format: `YYYY-MM-DD-slug-web.md`
  - `scraped-urls.txt` - Registry tracking all scraped URLs with dates

- **`processed/`** - Processed versions of source files
  - Mirrors folder structure from `sources/`
  - Contains Obsidian transclusions replacing original position bullet points
  - Links back to source files via `up` field

- **`papers/`** - Aggregated paper documents (optional consolidation)
  - Papers that aggregate related positions using Obsidian transclusions

- **`positions-drafts/`** - Draft positions awaiting classification and migration
  - `processed/` - Successfully migrated drafts moved here for archival

### Supporting Files

- `*.zip` files - Packaged Claude Code skills for distribution
  - `tif-web-scraper.zip`
  - `position-migration.zip`
  - `position-extractor.zip`

**Naming convention:**
- **Semantic folder and file names** - No number prefixes, use full descriptive titles
- **Example:** `Digitalisaatio ja datatalous/Tekoälyn hyödyntäminen/Datateollisuus/`
- **Unlimited scalability** - No limits on positions per category
- **Folder = Overview file** - Each category folder contains a matching `.md` file (e.g., `Datateollisuus/Datateollisuus.md`)
- **Root file** - `0000 index.md` serves as the repository root
- **Filenames with spaces** - Obsidian handles spaces natively for full title display

## Document Formats

### Position Documents (`type: position`)

Position documents in `positions/` follow this structure:

```yaml
---
type: position
title: "Document Title"
up: "[[Parent Document]]"
related:
  - "[[Related Document 1]]"
  - "[[Related Document 2]]"
---
```

**Key elements (minimal frontmatter):**
- `type: position` - Identifies this as a position document
- `title` - The position or topic name
- `up` - Parent document link using Obsidian wiki-link format `[[Document Name]]`
- `related` - (Optional) Related documents and source files

**Removed fields:**
- `tags` and `icon` fields have been removed for minimalist design
- Only essential metadata is retained

**Content structure:**
- Documents use Obsidian-style wiki links: `[[Topic Name]]` (no numbers)
- Hierarchical parent documents list child topics as bullet points
- Leaf documents contain position descriptions and details

### Source Documents (`type: web`)

Source files in `sources/` use this format:

```yaml
---
type: web
title: "Web Page Title"
source: "https://teknologiateollisuus.fi/..."
scraped: 2025-11-04
up:
related:
---
```

**Key elements:**
- `type: web` - Identifies this as web-scraped source content
- `source` - Original URL from TIF website
- `scraped` - Date the content was scraped (YYYY-MM-DD)
- Filename format: `YYYY-MM-DD-slug-web.md`

### Processed Documents

Processed files in `processed/` are created by position extraction:

```yaml
---
type: web
title: "Web Page Title"
source: "https://teknologiateollisuus.fi/..."
scraped: 2025-11-04
up: "[[2025-11-04-source-filename]]"
related:
---

> [!todo]+ Position Title
> ![[Position Title#processed-filename]]
```

**Key elements:**
- Contains Obsidian transclusions wrapped in `[!todo]+` callouts
- `up` field links back to original source file
- Transclusions use heading anchors to link to specific sections in position files

### Future: Versioned Positions (Not Yet Implemented)

When similar positions exist with different perspectives, versioning may be used in the future. The current system uses the `related` field to cross-reference similar positions without creating formal version structures.

## Fully Automated Processing (New!)

The repository now includes **fully automated** workflows for processing TIF sources with minimal manual intervention:

### Single URL Auto-Processing

Process any TIF URL end-to-end with one command:

```bash
python3 .claude/skills/auto-process-source/scripts/auto_process_source.py \
  "https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/"
```

Or use the slash command:
```
/auto-process https://teknologiateollisuus.fi/tavoitteemme/datakeskukset/
```

**What it does:**
1. Scrapes (or re-scrapes) the URL with version detection
2. Compares with previous version and detects changes
3. Extracts positions (only changed positions if re-scraping)
4. Migrates positions to semantic hierarchy in **auto mode**
5. Creates git commits at each stage for audit trail

**Auto mode behavior (fully implemented):**
- Positions with ≥80% similarity → Auto-merge into existing canonical position ✅
- Positions with 70-80% similarity → Skipped (needs manual review) ✅
- Positions with <70% similarity → Auto-create in classified location ✅

**Automatic classification:** Uses keyword-based classification to determine location:
- Tax/economic keywords → `Talous- ja veropolitiikka/`
- Digitalization keywords → `Digitalisaatio ja datatalous/`
- Skills keywords → `Osaaminen/`
- Work-life keywords → `Työelämä/`
- Innovation keywords → `Innovaatiot/`
- Investment keywords → `Investointiympäristö/`
- Critical tech keywords → `Kriittiset teknologiat/`
- Sustainability keywords → `Kestävä kasvu/`
- Resilience keywords → `Resilienssi/`

**Title generation:** No API key required!
- Slash commands use Claude Code for best quality titles
- Python scripts use improved fallback algorithm
- Both produce clean, descriptive 7-word titles

### Batch Processing Multiple URLs

Process multiple URLs in parallel using autonomous agents (recommended):

```
# Re-scrape all URLs
/batch-process-parallel --all

# Process specific URLs
/batch-process-parallel --urls "URL1" "URL2" "URL3"

# Filter by topic pattern
/batch-process-parallel --include "digitalisaatio"
/batch-process-parallel --include "digitalisaatio" "innovaatiot" --exclude "viestimme"
```

**How it works:**
1. Reads URLs from `sources/scraped-urls.txt` registry
2. Launches separate autonomous agents in parallel (one per URL)
3. Each agent runs the auto-process-source workflow independently
4. Reports summary when all complete

**Features:**
- True parallel execution via Claude Code Task tool
- Each URL processed in isolated agent (separate context window)
- Main context stays clean
- Pattern filtering with `--include` and `--exclude`
- Automatic git commits for each URL
- Comprehensive error handling and reporting

**Use cases:**
- Weekly update checks across all TIF sources
- Topic-specific re-scraping (e.g., only digitalization)
- Bulk re-processing after system changes

## Step-by-Step Workflow (Alternative)

If you prefer more control, you can use the individual skills separately:

The repository includes Claude Code skills that automate the position management workflow:

### 1. Scrape TIF Website Content

Use the `tif-web-scraper` skill to extract content from TIF website:

```
User: "Scrape https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/"
```

This creates a markdown file in `sources/TIF web/` with proper frontmatter and clean content.

**Version tracking:** The scraper automatically detects if a URL was previously scraped and creates versioned files:
- First scrape: `2025-11-04-datakeskukset-web.md`
- Re-scrape: `2025-12-15-datakeskukset-web.md`
- Both versions preserved for audit trail
- Registry updated in `sources/scraped-urls.txt`

### 2. Extract Position Statements (Optional)

The `position-extractor` skill extracts individual position bullet points from source documents into separate position files in `positions-drafts/` with LLM-generated titles.

**Recommended method:** Use the `/extract-positions` slash command:
```
User: /extract-positions
```

This will:
- Read the source file and extract all bullet-pointed positions
- Generate maximally descriptive titles (max 7 words) using LLM
- Create individual position files in `positions-drafts/`
- Create a processed file in `processed/` with Obsidian transclusions

### 3. Migrate Draft Positions

Use the `position-migration` skill for interactive classification:

```
User: "Migrate the draft positions"
```

The skill provides:
- AI-powered classification suggestions based on semantic similarity
- Duplicate detection (>70% similarity threshold)
- Interactive hierarchy navigation
- Semantic folder/file placement (no numbering constraints)
- Moves processed drafts to `positions-drafts/processed/`

The migration process is consultative and interactive, requiring user confirmation at each step.

## Re-Scraping and Update Management

When TIF website content is updated, use the `/re-scrape` workflow to detect changes and update positions:

### Re-Scrape Workflow

```
User: /re-scrape https://teknologiateollisuus.fi/tavoitteemme/datakeskukset/
```

**Automated steps:**
1. **Version detection** - Checks if URL was previously scraped
2. **Re-scrape** - Creates new version with current date (e.g., `2025-12-15-datakeskukset-web.md`)
3. **Diff detection** - Compares old vs new using `source-diff` skill:
   - NEW positions (added to source)
   - MODIFIED positions (content changed)
   - REMOVED positions (no longer present)
   - UNCHANGED positions (same content)
4. **Selective extraction** - Extracts only new/modified positions
5. **Smart migration**:
   - NEW positions → Normal migration workflow
   - MODIFIED positions → Auto-append to existing canonical positions in "## Kontekstit ja lähteet" section
6. **Provenance tracking** - Maintains clear audit trail of which source version contributed what

### Source Version Management

**File structure after re-scrape:**
```
sources/TIF web/
├── 2025-11-04-datakeskukset-web.md          # V1
├── 2025-12-15-datakeskukset-web.md          # V2 (new)
└── scraped-urls.txt                         # Registry tracking all scrapes

processed/
├── 2025-11-04-datakeskukset-web.md          # V1 processed
├── 2025-12-15-datakeskukset-web.md          # V2 processed
└── change-reports/
    └── 2025-12-15-datakeskukset-changes.md  # Diff report

positions/
└── .../Datateollisuus/
    └── Datakeskukset tukemaan sähköjärjestelmän tasapainoa.md
        (now has TWO sources in "Kontekstit ja lähteet")
```

**Canonical position with version history:**
```markdown
## Kontekstit ja lähteet

### [[2025-11-04-datakeskukset-web]]
> Datakeskukset tukevat sähköverkkoa...
**Scraped:** 2025-11-04

### [[2025-12-15-datakeskukset-web]]
> Datakeskukset osallistuvat sähköjärjestelmän tasapainoon...
**Scraped:** 2025-12-15
**Change:** Added specifics about district heating
```

## Manual Position Management

**When manually creating new positions:**
1. Determine the appropriate parent category in the semantic hierarchy
2. Use full descriptive title for the filename (e.g., `Nopeutetaan datakeskusten lupaprosesseja.md`)
3. Create directory for categories with sub-positions, or standalone `.md` file for leaf positions
4. Include minimal YAML frontmatter with correct `up` reference to parent
5. Optionally update parent document to include wiki-link to new position

**When organizing positions:**
1. Categories with children = folders containing an overview `.md` file
2. Leaf positions = standalone `.md` files in their parent folder
3. No numbering limits - add as many positions as needed
4. Easy reorganization - just move folders and update `up` fields

**When editing existing positions:**
1. Preserve minimal YAML frontmatter (type, title, up, related only)
2. Maintain consistent wiki-link format for cross-references `[[Position Name]]`
3. Reorganizing is simple - move files/folders and update `up` field
4. Use search/replace to update wiki links when renaming positions

## Claude Code Commands

This repository includes several slash commands for common workflows:

### /extract-positions
Extract position statements from a source file with Claude-generated titles.
- Reads source file and extracts bullet-pointed positions
- Generates maximally descriptive 7-word titles using Claude
- Creates individual position files in `positions-drafts/`
- Creates processed file with Obsidian transclusions

### /auto-process
Fully automated end-to-end processing of a single TIF URL.
- Scrapes (or re-scrapes) with version detection
- Compares with previous version if re-scraping
- Extracts positions (only changed if re-scrape)
- Migrates to hierarchy in auto mode
- Creates git commits at each stage

### /batch-process-parallel
Process multiple TIF URLs in parallel using autonomous agents.
- `--all` - Re-scrape all URLs from registry
- `--urls "URL1" "URL2"` - Process specific URLs
- `--include "pattern"` - Filter URLs by pattern
- `--exclude "pattern"` - Exclude URLs by pattern
- Each URL processed in separate agent with isolated context

### /re-scrape
Re-scrape a TIF URL with intelligent change detection.
- Detects previous version
- Scrapes new version
- Compares and generates change report
- Extracts only new/modified positions
- Guides through migration workflow

### /generate-position-title
Utility command to generate a descriptive title for a position.
- Analyzes position text
- Generates maximally descriptive 7-word title
- Uses natural language and semantic understanding

### /session-close
Wrap up a Claude Code session (NEW!)
- Verifies all documentation is up-to-date
- Creates/appends dated changelog entry
- Commits and pushes all changes
- Prepares for context clear
- Use at end of each work session

## Claude Code Skills

This repository includes six custom skills (available as .zip files):

### tif-web-scraper
- **Purpose:** Scrape TIF website URLs and convert to markdown files with version tracking
- **Input:** TIF website URL (teknologiateollisuus.fi)
- **Output:** Markdown file in `sources/TIF web/` with URL path structure preserved
- **Features:**
  - Excludes sidebars, stops at "Lisätiedot:"
  - Detects previous scrapes and creates versioned files
  - Updates `sources/scraped-urls.txt` registry
  - Suggests using source-diff for re-scrapes

### source-diff
- **Purpose:** Compare two versions of a source file and detect position-level changes
- **Input:** Old and new source markdown files
- **Output:** Change report (markdown or JSON) showing new/modified/removed/unchanged positions
- **Features:**
  - Section-level diff (bullet points)
  - Fuzzy text similarity matching (70-90% thresholds)
  - Markdown and JSON output formats
  - Classification: new, modified, removed, unchanged

### position-extractor
- **Purpose:** Extract bullet-pointed positions from source documents with LLM-generated titles
- **Input:** Source markdown files (from `sources/`)
- **Output:** Individual position files in `positions-drafts/` and processed file in `processed/`
- **Usage:** Use `/extract-positions` slash command for best results
- **Features:**
  - LLM-generated descriptive titles (max 7 words)
  - Obsidian transclusions linking positions to processed files
  - Bidirectional linking between processed files and positions
  - Change-aware extraction: `--change-report` and `--only-changed` flags
  - Alternative: Manual script invocation with `--titles` parameter for custom titles

### position-migration
- **Purpose:** Migrate draft positions to semantic hierarchical structure
- **Input:** Position files in `positions-drafts/`
- **Output:** Organized positions in `positions/` directory tree using semantic naming
- **Features:**
  - Semantic similarity analysis using embeddings
  - AI-powered classification suggestions with confidence levels
  - No numbering constraints - unlimited positions per category
  - Simple reorganization with semantic folder structure
  - Duplicate detection and versioning strategy
  - Interactive consultation at each step (or `--auto` mode)
  - Automatic umbrella position creation for similar content
  - Migration logging and change tracking

### auto-process-source (New!)
- **Purpose:** Fully automated end-to-end processing of TIF URLs
- **Input:** TIF website URL
- **Output:** Scraped source, extracted positions, migrated to hierarchy, git commits
- **Usage:** `/auto-process <URL>` or direct script invocation
- **Features:**
  - Orchestrates full workflow: scrape → diff → extract → migrate → commit
  - Handles re-scrapes intelligently (only processes changes)
  - Auto mode migration (≥80% merge, 70-80% skip, <70% create)
  - Git commits at meaningful moments (scrape, extract, migrate)
  - Early exit if no changes detected
  - Comprehensive error handling

### batch-processor (New!)
- **Purpose:** Process multiple TIF URLs in parallel using autonomous agents
- **Input:** URLs from registry or command line
- **Output:** Processed sources across all URLs with git commits
- **Usage:** `/batch-process-parallel --all` or with filters
- **Features:**
  - Agent-based parallel execution (via Task tool)
  - Each URL in isolated agent with separate context window
  - Pattern filtering (`--include`, `--exclude`)
  - Reads from `sources/scraped-urls.txt` registry
  - Uses auto-process-source for each URL
  - Progress tracking and error reporting
  - Graceful error handling (failed URLs don't stop others)
  - Legacy Python multiprocessing mode also available

## File Organization Notes

- `.gitignore` excludes `.obsidian/` (Obsidian configuration) and `.DS_Store` (macOS metadata)
- `positions/0000.base` contains Obsidian database view configuration
- Content is in Finnish
- This is a documentation/content repository - no build/test commands needed
- Python scripts in Claude skills require: `requests`, `beautifulsoup4` for web scraping

## Git Workflow

This repository uses a simple main branch workflow:
- Main branch: `main`
- When committing, describe changes to position documents clearly
- Claude skills are version-controlled as .zip files for easy distribution
