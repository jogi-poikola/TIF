---
description: Process multiple TIF URLs in parallel using separate agents
---

Process multiple TIF website URLs in parallel by launching separate autonomous agents.

## Instructions for Claude

When the user invokes this command, follow these steps:

### Step 1: Determine URLs to Process

**If user specifies URLs directly:**
- Use the URLs provided in the command

**If user specifies --all:**
- Read `sources/scraped-urls.txt`
- Extract unique URLs (skip duplicates, keep most recent)

**If user specifies --include pattern(s):**
- Read `sources/scraped-urls.txt`
- Filter URLs matching the pattern(s)

**Filtering logic:**
```python
# Read registry
urls = []
with open('sources/scraped-urls.txt') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            parts = line.split('|')
            if len(parts) >= 3:
                urls.append(parts[1].strip())

# Get unique URLs
urls = list(dict.fromkeys(urls))

# Filter if needed
if include_patterns:
    urls = [u for u in urls if any(p in u for p in include_patterns)]
if exclude_patterns:
    urls = [u for u in urls if not any(p in u for p in exclude_patterns)]
```

### Step 2: Launch Parallel Agents

**CRITICAL:** Launch ALL agents in a SINGLE response using multiple Task tool calls.

For each URL, create one Task tool invocation:

```
Task(
  subagent_type="general-purpose",
  model="haiku",  # Fast and cost-effective
  description="Auto-process TIF URL",
  prompt="""
Auto-process this TIF source URL end-to-end with automated migration and Claude-generated titles.

**URL:** <INSERT_URL_HERE>

## Task Overview

Process this URL through the complete workflow:
1. Scrape or re-scrape
2. Extract positions with Claude-generated titles (better quality than fallback)
3. Migrate in auto mode
4. Create git commits

## Detailed Steps

### Step 1: Scrape the URL

```bash
python3 .claude/skills/tif-web-scraper/scripts/scrape_tif_web.py "<INSERT_URL_HERE>"
```

This creates/updates the source file in `sources/TIF web/`.

### Step 2: Extract Positions with Claude-Generated Titles

**Use the /extract-positions slash command** which uses Claude Code to generate high-quality titles:

```
/extract-positions <path-to-source-file>
```

The slash command will:
- Read the source file
- Extract all bullet-pointed positions
- Generate maximally descriptive 7-word titles using Claude
- Create position files in `positions-drafts/`

### Step 3: Migrate Positions

```bash
python3 .claude/skills/position-migration/scripts/migrate_positions.py --auto
```

This migrates positions in auto mode (≥80% merge, <70% skip).

### Step 4: Create Git Commits

```bash
git add -A && git commit -m "Auto-process <URL-slug>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Your Job

1. Execute each step in order
2. Monitor for errors
3. Report back CONCISELY:
   - ✅ Success or ❌ Failure
   - Number of positions extracted
   - Number of positions migrated
   - Brief error if failed

**Do NOT include full output** - just parse numbers and report summary.

## Example Report

✅ Successfully processed
   - Extracted: 5 positions (with Claude-generated titles)
   - Migrated: 2 merged, 3 skipped
   - Git commits: Created
"""
)
```

**Important:** Send ALL Task tool calls in ONE message for true parallel execution.

### Step 3: Collect Results

As each agent completes, they will report back. Collect all reports.

### Step 4: Print Summary

After all agents complete, provide a summary:

```
======================================================================
BATCH PROCESSING COMPLETE
======================================================================

Processed: N URLs in parallel
✅ Successful: X
❌ Failed: Y

✅ Successful URLs:
   - URL1 (M positions migrated)
   - URL2 (N positions migrated)

❌ Failed URLs:
   - URL3 (Error: network timeout)

Total positions migrated: Z
Total git commits created: W
```

## Usage Examples

```
# Process all URLs
/batch-process-parallel --all

# Process specific URLs
/batch-process-parallel --urls "https://teknologiateollisuus.fi/tavoitteemme/datakeskukset/" "https://teknologiateollisuus.fi/tavoitteemme/innovaatiot/"

# Filter by pattern
/batch-process-parallel --include "digitalisaatio"
/batch-process-parallel --include "digitalisaatio" "innovaatiot" --exclude "viestimme"
```

## Performance

- Each URL processed in isolated agent (separate context window)
- True parallel execution via Task tool
- Fast model (haiku) for cost-effectiveness
- Typical: 30-90 seconds per URL
- Recommended: Process 4-10 URLs at a time

## Notes

- Main context window stays clean (agents handle details)
- Git commits created independently by each agent
- Failed agents don't block others
- Review git log after completion: `git log --oneline -20`
