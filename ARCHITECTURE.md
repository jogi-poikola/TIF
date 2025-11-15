# TIF Knowledge Management Architecture

## Overview

This repository implements an **automated knowledge management system** for Teknologiateollisuus (TIF) position documents with intelligent classification, semantic organization, and parallel processing capabilities. The system scrapes TIF website content, extracts position statements, and automatically organizes them into a hierarchical structure with full provenance tracking.

## Core Principles

1. **Modularity** - Single responsibility for each component, composable workflows
2. **No Duplication** - Each capability exists in exactly one place
3. **Agent-Based Parallelism** - Isolated context windows for concurrent processing
4. **No External API Dependencies** - Uses Claude Code for AI tasks (no API key required)
5. **One Canonical Position Per Topic** - Each position in `positions/` is the single source of truth
6. **Source Immutability** - Files in `sources/` are immutable snapshots of original content
7. **Provenance Tracking** - All canonical positions track their sources via `## Kontekstit ja lähteet` section
8. **Merge, Don't Version** - Similar positions merge into canonical rather than creating `-a/-b` versions
9. **Minimal Frontmatter** - Only essential metadata in YAML frontmatter
10. **Version Tracking** - Date-based filenames for audit trail

## Folder Structure

```
TIF/
├── sources/                    # Immutable source materials
│   ├── TIF web/               # Published web content (versioned by date)
│   │   ├── tavoitteemme/
│   │   │   ├── digitalisaatio-ja-datatalous/
│   │   │   │   ├── 2025-11-04-datakeskukset-web.md     # V1
│   │   │   │   └── 2025-12-15-datakeskukset-web.md     # V2 (re-scrape)
│   │   └── ...
│   ├── TIF paper/             # Shared PDFs (immutable)
│   ├── TIF internal/          # Internal documents (immutable)
│   └── scraped-urls.txt       # URL registry with scrape dates
│
├── processed/                  # Processed versions with transclusions
│   └── TIF web/               # Mirrors source structure
│       └── tavoitteemme/
│           └── ...
│
├── positions-drafts/           # Temporary staging for new positions
│   ├── Position Title 1.md
│   ├── Position Title 2.md
│   └── processed/             # Successfully migrated drafts
│
├── positions/                  # Canonical hierarchical position structure
│   ├── 0000 index.md          # Root document
│   ├── Resilienssi/           # Semantic folder names (no numbers)
│   ├── Kriittiset teknologiat/
│   ├── Osaaminen/
│   ├── Investointiympäristö/
│   ├── Työelämä/
│   ├── Kestävä kasvu/
│   ├── Talous- ja veropolitiikka/
│   ├── Digitalisaatio ja datatalous/
│   │   ├── Digitalisaatio ja datatalous.md
│   │   ├── Kyberturvallisuus.md
│   │   └── Tekoälyn hyödyntäminen/
│   │       ├── Tekoälyn hyödyntäminen.md
│   │       └── Datateollisuus.md          # Canonical position
│   └── Innovaatiot/
│
└── .claude/                    # Claude Code integration
    ├── skills/                # Python-based capabilities
    │   ├── tif-web-scraper/
    │   ├── source-diff/
    │   ├── position-extractor/
    │   ├── position-migration/
    │   ├── auto-process-source/
    │   └── batch-processor/
    └── commands/              # Slash commands
        ├── extract-positions.md
        ├── auto-process.md
        ├── batch-process-parallel.md
        └── re-scrape.md
```

## Filename Conventions

### Sources & Processed Files
Format: `YYYY-MM-DD-slug-type.md`

**Types:**
- `web` - Published web content
- `paper` - Shared PDF documents
- `internal` - Internal/unpublished docs

**Examples:**
- `2025-11-04-datakeskukset-web.md`
- `2025-09-15-teknologiapoliittiset-linjaukset-paper.md`
- `2025-11-08-procurement-strategy-internal.md`

**Version tracking:**
- First scrape: `2025-11-04-datakeskukset-web.md`
- Re-scrape: `2025-12-15-datakeskukset-web.md`
- Both versions preserved for audit trail

### Position Drafts
Format: `{Position Title}.md`

**Examples:**
- `Kehitetään julkisia ICT-hankintoja.md`
- `Tuetaan datakeskusten kehitystä.md`

### Canonical Positions
Format: `{Position Title}.md` (semantic, no number prefixes)

**Examples:**
- `Digitalisaatio ja datatalous.md`
- `Kyberturvallisuus ja digitaalisen infrastruktuurin riippuvuuksien hallinta.md`
- `Datateollisuus.md`

**Folders:**
- Semantic names with spaces: `Digitalisaatio ja datatalous/`
- Unlimited scalability (no numbering constraints)
- Each folder contains matching overview file (e.g., `Datateollisuus/Datateollisuus.md`)

## Frontmatter Schema

### Source Files (`sources/`)
```yaml
---
type: web          # web | paper | internal
title: "Datakeskukset"
source: "https://teknologiateollisuus.fi/..."
scraped: 2025-11-04
up:
related:
---
```

### Processed Files (`processed/`)
```yaml
---
type: web          # Same as source
title: "Datakeskukset"
source: "https://teknologiateollisuus.fi/..."
scraped: 2025-11-04
up:
related:
---
```

### Position Drafts (`positions-drafts/`)
```yaml
---
type: position
title: "Tuetaan datakeskusten kehitystä"
up:
related:
  - "[[2025-11-04-datakeskukset-web]]"
---
```

### Canonical Positions (`positions/`)
```yaml
---
type: position
title: "Kyberturvallisuus ja digitaalisen infrastruktuurin riippuvuuksien hallinta"
up: "[[Digitalisaatio ja datatalous]]"
related:
  - "[[Innovatiiviset julkiset hankinnat]]"
---
```

**Note:** Only 4 fields - minimal by design. No `status`, `granularity`, `last_updated`, or `sources` in frontmatter. Source provenance is in the body under `## Kontekstit ja lähteet`. No number prefixes in wiki links - semantic naming only.

## Canonical Position Format

```markdown
---
type: position
title: "Kyberturvallisuus ja digitaalisen infrastruktuurin riippuvuuksien hallinta"
up: "[[Digitalisaatio ja datatalous]]"
related:
  - "[[Innovatiiviset julkiset hankinnat]]"
---

## [[2025-10-07-tieto-ja-teknologiapoliittiset-linjaukset-web]]

Lujitetaan teknologista turvallisuutta ja resilienssiä:Yritykset nojautuvat laajalti
infrastruktuurissaan Euroopan ulkopuolisten toimittajien digitaalisiin palveluihin.
Geotaloudellisten jännitteiden lisääntyminen on nostanut pintaan tarpeen arvioida ja
hallita näihin riippuvuuksiin liittyviä riskejä...
```

**Structure:**
- Minimal frontmatter (type, title, up, related)
- Source sections with wiki-link headings (e.g., `## [[2025-10-07-...web]]`)
- Position text under each source section
- Provenance via source file links
- No number prefixes in wiki links

## Workflows

This system supports three workflow modes:

### A. Fully Automated Single-URL Workflow (Recommended)

**Command:** `/auto-process <URL>` or direct script invocation

**Tool:** `.claude/skills/auto-process-source/scripts/auto_process_source.py`

**Process:**
```
┌─────────────────┐
│  TIF Website    │
│  URL            │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  auto-process-source                 │
│  ┌──────────────────────────────┐   │
│  │ 1. tif-web-scraper           │   │
│  │    ├─ Detect version         │   │
│  │    └─ Scrape URL             │   │
│  │    └─ Git commit             │   │
│  ├──────────────────────────────┤   │
│  │ 2. source-diff (if re-scrape)│   │
│  │    ├─ Compare versions       │   │
│  │    └─ Generate change report │   │
│  │    └─ Early exit if no changes   │
│  ├──────────────────────────────┤   │
│  │ 3. position-extractor        │   │
│  │    ├─ Extract positions      │   │
│  │    ├─ Only changed (if diff) │   │
│  │    └─ Git commit             │   │
│  ├──────────────────────────────┤   │
│  │ 4. position-migration --auto │   │
│  │    ├─ Classify (≥80% merge)  │   │
│  │    ├─ Skip (70-80%)          │   │
│  │    ├─ Create (<70%)          │   │
│  │    └─ Git commit             │   │
│  └──────────────────────────────┘   │
└──────────────────────────────────────┘
```

**Features:**
- End-to-end automation with one command
- Handles re-scraping intelligently (only processes changes)
- Auto mode migration (≥80% merge, 70-80% skip, <70% create)
- Git commits at meaningful moments
- Early exit if no changes detected

### B. Batch Parallel Workflow (Agent-Based)

**Command:** `/batch-process-parallel --all` or with filters

**Tool:** `.claude/skills/batch-processor/`

**Process:**
```
┌─────────────────────────────┐
│  scraped-urls.txt registry  │
│  - URL 1 (with date)        │
│  - URL 2 (with date)        │
│  - URL 3 (with date)        │
│  - ...                      │
└───────────┬─────────────────┘
            │
            ▼
┌───────────────────────────────────┐
│  batch-processor                  │
│  - Filter URLs (--include/exclude)│
│  - Launch parallel agents         │
└─────────┬─────────────────────────┘
          │
          ├─────────────┬─────────────┬─────────────┐
          ▼             ▼             ▼             ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
    │ Agent 1 │   │ Agent 2 │   │ Agent 3 │   │ Agent N │
    │  URL 1  │   │  URL 2  │   │  URL 3  │   │  URL N  │
    └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
         │             │             │             │
         ▼             ▼             ▼             ▼
    ┌──────────────────────────────────────────────────┐
    │  Each agent runs:                                │
    │  auto-process-source workflow                    │
    │  (scrape → diff → extract → migrate → commit)    │
    └──────────────────────────────────────────────────┘
```

**Features:**
- True parallel execution via Claude Code Task tool
- Each URL in isolated agent with separate context window
- Pattern filtering (`--include`, `--exclude`)
- Progress tracking and error reporting
- Failed URLs don't stop others

**Use cases:**
- Weekly update checks across all TIF sources
- Topic-specific re-scraping (e.g., only digitalization)
- Bulk re-processing after system changes

### C. Manual Step-by-Step Workflow

For more control, use individual skills separately:

#### 1. tif-web-scraper → sources/

**Tool:** `.claude/skills/tif-web-scraper/scripts/scrape_tif_web.py`

**Input:** TIF website URL

**Output:** Date-prefixed source file in `sources/TIF web/`

**Features:**
- Extracts date from "Päivitetty DD.MM.YYYY"
- Generates `YYYY-MM-DD-slug-web.md`
- Sets `type: web`, `scraped: YYYY-MM-DD`
- Mirrors URL folder structure
- Detects previous scrapes and creates versioned files

**Example:**
```bash
python3 .claude/skills/tif-web-scraper/scripts/scrape_tif_web.py \
  https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/datakeskukset/

# Output: sources/TIF web/tavoitteemme/digitalisaatio-ja-datatalous/2025-11-04-datakeskukset-web.md
```

#### 2. position-extractor → positions-drafts/ + processed/

**Tool:** `.claude/skills/position-extractor/scripts/extract_positions.py`

**Recommended:** Use `/extract-positions` slash command for Claude Code title generation

**Input:** Source file from `sources/`

**Output:**
- Position drafts in `positions-drafts/`
- Processed file in `processed/` (mirrored structure)

**Features:**
- Extracts bullet-pointed positions
- Claude Code generates descriptive 7-word titles (via slash command)
- Python fallback uses improved algorithm (no API key needed)
- Creates drafts with `## [[processed-filename]]` heading
- Processed file has transclusions with anchors
- Bidirectional linking
- Change-aware extraction: `--change-report` and `--only-changed` flags

**Example:**
```bash
# Best quality (via slash command):
/extract-positions sources/TIF web/.../2025-11-04-datakeskukset-web.md

# Or direct script (uses fallback titles):
python3 .claude/skills/position-extractor/scripts/extract_positions.py \
  "sources/TIF web/tavoitteemme/digitalisaatio-ja-datatalous/2025-11-04-datakeskukset-web.md"

# Output:
# positions-drafts/Tuetaan datakeskusten kehitystä.md
# positions-drafts/Varmistetaan energiatehokasta kasvua.md
# processed/TIF web/tavoitteemme/digitalisaatio-ja-datatalous/2025-11-04-datakeskukset-web.md
```

#### 3. position-migration → positions/

**Tool:** `.claude/skills/position-migration/scripts/migrate_positions.py`

**Input:** Drafts from `positions-drafts/`

**Output:** Canonical positions in `positions/` (hierarchical semantic structure)

**Modes:**
- **Interactive (default):** User confirms each decision
- **Auto (`--auto` flag):** Fully automated based on similarity thresholds

**Decision Logic:**
- **≥80% similarity:** Auto-merge into existing canonical
- **70-80% similarity:** Skip (needs manual review)
- **<70% similarity:** Auto-create new position with keyword-based classification

**Auto Mode Classification:**
Uses keyword-based heuristics to determine semantic folder:
- Tax/economic keywords → `Talous- ja veropolitiikka/`
- Digitalization keywords → `Digitalisaatio ja datatalous/`
- Skills keywords → `Osaaminen/`
- Work-life keywords → `Työelämä/`
- Innovation keywords → `Innovaatiot/`
- Investment keywords → `Investointiympäristö/`
- Critical tech keywords → `Kriittiset teknologiat/`
- Sustainability keywords → `Kestävä kasvu/`
- Resilience keywords → `Resilienssi/`

**Merge Action:**
- Adds source excerpt to canonical's source section
- Updates processed file transclusion to point to canonical
- Moves draft to `positions-drafts/processed/`

**Create Action (Auto Mode):**
- Classifies location using keyword matching
- Creates directory structure if needed
- Generates frontmatter with proper `up` reference
- Creates position file with content
- Moves draft to `positions-drafts/processed/`

**Example:**
```bash
# Interactive mode:
python3 .claude/skills/position-migration/scripts/migrate_positions.py

# Auto mode (used by automated workflows):
python3 .claude/skills/position-migration/scripts/migrate_positions.py --auto

# Interactive process:
# [1/5] Processing: Kehitetään julkisia ICT-hankintoja.md
# 🎯 HIGH SIMILARITY DETECTED (87%)
#    Canonical: Kyberturvallisuus ja digitaalisen infrastruktuurin...
#    Location:  Digitalisaatio ja datatalous/Kyberturvallisuus...
#
# Your choice [1]: 1
# ✅ MERGING into: Kyberturvallisuus ja digitaalisen infrastruktuurin...
```

## Timestamps

### Source Files
- **`scraped` date** in frontmatter (when scraped from web/PDF)
- Immutable - represents snapshot date

### Canonical Positions
- **File `mtime`** tracked by git/filesystem
- Updates automatically when file modified
- Query with: `git log --follow positions/8000.../8300.md`

### No Manual Timestamps
- No `last_updated` field to maintain
- No risk of forgetting to update dates

## Querying

### Find positions linking to a source
```dataview
TABLE file.mtime as "Last Modified"
FROM "positions"
WHERE contains(file.outlinks, [[2025-11-04-datakeskukset-web]])
SORT file.mtime DESC
```

### Recent position updates
```dataview
TABLE file.mtime as "Modified"
FROM "positions"
SORT file.mtime DESC
LIMIT 10
```

### Positions by type
```dataview
TABLE title, up
FROM "positions"
WHERE type = "position"
SORT file.path
```

## Key System Features

### Automated Workflows
1. **Single-URL auto-processing** - End-to-end automation with one command
2. **Batch parallel processing** - Agent-based concurrent URL processing
3. **Intelligent re-scraping** - Version detection and change-based processing
4. **Auto mode migration** - Keyword-based classification and file creation
5. **No API key required** - Uses Claude Code for AI tasks

### Intelligent Classification
- **Similarity-based** - Uses text matching for duplicate detection
- **Keyword-based** - Automatic semantic folder assignment
- **Three-tier logic** - ≥80% merge, 70-80% skip, <70% create

### Title Generation
- **Claude Code integration** - Best quality via slash commands
- **Fallback algorithm** - Natural language break points, no API needed
- **7-word limit** - Concise, descriptive titles

### Version Management
- **Date-based filenames** - `YYYY-MM-DD-slug-web.md`
- **Multiple versions** - All scrape versions preserved
- **Change detection** - Position-level diff reports
- **Provenance tracking** - Source attribution in position files

### Key Differences from Numbered System

| Aspect | Numbered System | Current Semantic System |
|--------|-----------------|-------------------------|
| Position naming | `8300 Position.md` | `Position Title.md` (no numbers) |
| Folder naming | `8000 Category/` | `Category Name/` (semantic) |
| Scalability | Limited by numbering | Unlimited (no constraints) |
| Wiki links | `[[8300 Position]]` | `[[Position Title]]` |
| Reorganization | Renumber cascades | Move files, update `up` field |
| Similar positions | Versioned (-a, -b) + umbrella | Merged into canonical |
| Source tracking | In frontmatter | In body (source sections) |
| Timestamps | Manual `last_updated` | Git/filesystem `mtime` |
| Automation | Manual workflows | Fully automated with agents |

## Migration Path

To convert existing files to new structure, use the migration script (to be created):

```bash
python3 migrate_existing_files.py

# Will:
# 1. Rename papers/ → processed/TIF web/
# 2. Add dates to filenames
# 3. Update frontmatter type fields
# 4. Consolidate -a/-b versions into canonicals
# 5. Create ## Kontekstit ja lähteet sections
```

## Claude Code Skills

The system includes six custom skills for different capabilities:

### 1. tif-web-scraper
- **Single responsibility:** Web scraping only
- **Features:** Version detection, URL registry, date extraction
- **Used by:** All workflows (manual, auto, batch)

### 2. source-diff
- **Single responsibility:** File comparison only
- **Features:** Position-level diff, fuzzy matching, change reports
- **Used by:** Re-scrape workflows

### 3. position-extractor
- **Single responsibility:** Position extraction only
- **Features:** Bullet extraction, transclusions, change-aware processing
- **Title generation:** Via Claude Code (slash command) or fallback algorithm
- **Used by:** All workflows

### 4. position-migration
- **Single responsibility:** Classification and file creation only
- **Features:** Similarity analysis, keyword classification, interactive/auto modes
- **Used by:** All workflows (with `--auto` flag for automation)

### 5. auto-process-source
- **Single responsibility:** Orchestration for single URL
- **Features:** Combines all skills, handles re-scraping, git commits
- **Uses:** Skills 1-4 in sequence

### 6. batch-processor
- **Single responsibility:** Parallelization for multiple URLs
- **Features:** Agent launching, URL filtering, progress tracking
- **Uses:** Skill 5 (auto-process-source) in parallel agents

**Design principle:** Each skill exists once, used by both manual and automated workflows via flags.

## Slash Commands

User-facing commands that orchestrate skills:

1. **/extract-positions** - Extract with Claude-generated titles
2. **/auto-process** - Single-URL automation
3. **/batch-process-parallel** - Agent-based parallel processing
4. **/re-scrape** - Smart re-scrape with diff
5. **/generate-position-title** - Utility for title generation
6. **/session-close** - Wrap up session with changelog, commit, and push

## Maintenance

### Weekly Workflow
1. Run `/batch-process-parallel --all` to check all TIF URLs for updates
2. Review 70-80% similarity positions for manual migration
3. Curate canonical positions (synthesize, refine)

### Regular Tasks
- **Weekly:** Batch re-scrape all URLs
- **Monthly:** Review skipped positions (70-80% similarity)
- **Quarterly:** Verify classification accuracy, adjust keywords if needed
- **Yearly:** Archive old source versions if needed

### Single Maintainer Benefits
- Minimal frontmatter = less maintenance
- Merge workflow = no version explosion
- Git timestamps = automatic tracking
- Clear provenance = easy to trace sources
- Automated workflows = less manual work

## Monitoring

Check these indicators for system health:

1. **Draft backlog** - Growing `positions-drafts/` may indicate classification issues
2. **Git commits** - Regular commits indicate active processing
3. **Error logs** - Failed URLs in batch processing reports
4. **Similarity distribution** - Most positions should be <70% or ≥80%

## Future Extensions

### Potential Improvements
1. **Semantic embeddings** - Better classification than keyword matching
2. **Batch embedding** - Cache embeddings for faster similarity
3. **Multi-language** - English translation support
4. **Web UI** - Browse positions via web interface
5. **Export formats** - PDF, DOCX, HTML export

### Additional Scrapers
- PDF parser for `TIF paper/` sources
- Internal doc importer for `TIF internal/` sources
- Same workflow applies to all source types

### Enhanced Migration
- AI embeddings for better similarity detection
- Automatic synonym detection
- Suggested canonical text synthesis
- Learning from manual classification decisions

### Query Dashboard
- Obsidian canvas showing position graph
- "Orphaned positions" detector
- "Missing parent links" validator

---

**Document version:** 2.0
**Last updated:** 2025-11-12
**Maintainer:** TIF Position Management System
