# auto-process-source

Automatically process TIF website sources end-to-end with minimal human intervention.

## Overview

This skill orchestrates the complete workflow for processing TIF website content:
1. **Scrape** or re-scrape TIF website URLs with version tracking
2. **Detect changes** if re-scraping (using source-diff)
3. **Extract positions** (only changed positions if re-scraping)
4. **Migrate positions** to semantic hierarchy using auto mode
5. **Git commit** at meaningful moments for audit trail

## When to Use

Use this skill when you want to:
- Fully automate the processing of a TIF website URL from start to finish
- Re-scrape a URL and automatically integrate only the changes
- Process multiple URLs in parallel without manual intervention
- Maintain a clean git history with meaningful commits at each stage

## Usage

### Single URL Processing

```bash
python3 .claude/skills/auto-process-source/scripts/auto_process_source.py \
  "https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/"
```

### With Options

```bash
# Skip git commits (for testing)
python3 .claude/skills/auto-process-source/scripts/auto_process_source.py \
  "https://teknologiateollisuus.fi/tavoitteemme/datakeskukset/" \
  --skip-commits

# Specify repo root (if not in repo directory)
python3 .claude/skills/auto-process-source/scripts/auto_process_source.py \
  "https://teknologiateollisuus.fi/tavoitteemme/innovaatiot/" \
  --repo-root /path/to/TIF
```

## Workflow Details

### 1. Scraping with Version Detection

- Checks `sources/scraped-urls.txt` for previous scrapes
- Creates versioned file if content changed
- Updates registry automatically

**Git commit:** "Add TIF source: {url}" or "Re-scrape TIF source: {url}"

### 2. Change Detection (Re-scrapes Only)

- Compares previous version with new version
- Generates JSON change report
- Identifies: new, modified, removed, unchanged positions
- **Exits early** if no changes detected (all unchanged)

### 3. Position Extraction

**First scrape:**
- Extracts all bullet-pointed positions
- Creates files in `positions-drafts/`
- Generates LLM-powered descriptive titles

**Re-scrape:**
- Extracts ONLY new/modified positions
- Uses change report to filter
- Avoids duplicate extraction

**Git commit:** "Extract positions from: {source_filename}"

### 4. Position Migration (Auto Mode)

- Migrates draft positions to semantic hierarchy
- Uses AI classification with semantic similarity
- Runs in **auto mode** (no user prompts)
- Handles duplicates automatically:
  - High similarity (>90%): Auto-append to existing position
  - Medium similarity (70-90%): Create umbrella position
  - Low similarity (<70%): Create new position
- Moves processed drafts to `positions-drafts/processed/`

**Git commit:** "Migrate positions from: {source_filename}"

## Exit Conditions

The skill will exit successfully (no error) in these cases:
- **No changes detected** during re-scrape → Exits after diff step
- **No positions extracted** → Continues to migration (might be intentional)
- **No drafts to migrate** → Exits successfully

The skill will exit with error if:
- Scraping fails (network error, invalid URL, etc.)
- Diff fails (file not found, parsing error)
- Extraction fails (script error)
- Migration fails (script error, file conflicts)

## Git Commit Strategy

Commits are created at three key moments:

1. **After scraping** - Preserves scraped source content
   - `"Add TIF source: {url}"` (first scrape)
   - `"Re-scrape TIF source: {url}"` (re-scrape)

2. **After extraction** - Preserves extracted position drafts
   - `"Extract positions from: {source_filename}"`

3. **After migration** - Preserves final integrated positions
   - `"Migrate positions from: {source_filename}"`

All commits include:
- Attribution: "🤖 Generated with Claude Code"
- Co-authorship: "Co-Authored-By: Claude <noreply@anthropic.com>"

Use `--skip-commits` flag during testing to prevent commits.

## Example Output

```
======================================================================
AUTO-PROCESSING TIF SOURCE
======================================================================
URL: https://teknologiateollisuus.fi/tavoitteemme/datakeskukset/
Repo: /Users/user/TIF

🔄 Scraping: https://teknologiateollisuus.fi/...

📋 Previous scrapes found: 1
   - 2025-11-04: sources/TIF web/.../2025-11-04-datakeskukset-web.md

✅ Created source at: sources/TIF web/.../2025-11-10-datakeskukset-web.md

📝 Committing: Re-scrape TIF source: https://...

📊 Comparing versions...
   Old: 2025-11-04-datakeskukset-web.md
   New: 2025-11-10-datakeskukset-web.md

Summary:
  ✨ New positions:       2
  ✏️  Modified positions:  1
  ❌ Removed positions:   0
  ✓ Unchanged positions: 5

📝 Extracting positions...
   (Only extracting new/modified positions)

Created 3 position files in positions-drafts/

📝 Committing: Extract positions from: 2025-11-10-datakeskukset-web.md

🚀 Migrating 3 positions in auto mode...

✓ Migrated: Datakeskukset tukemaan sähköjärjestelmän tasapainoa
  → positions/Digitalisaatio ja datatalous/Tekoälyn hyödyntäminen/Datateollisuus/
  → Auto-appended to existing position (similarity: 92%)

✓ Migrated: Kehitetään datakeskusten energiatehokkuutta
  → positions/Kestävä kasvu/Energia/
  → Created new position

✓ Migrated: Tuetaan kvanttilaskennan infrastruktuuria
  → positions/Kriittiset teknologiat/Kvanttiteknologia/
  → Created new position

📝 Committing: Migrate positions from: 2025-11-10-datakeskukset-web.md

✅ Auto-processing complete!
======================================================================
```

## Integration with Parallel Processing

This skill is designed to be used by the batch processor for parallel execution:

```bash
# Process all URLs in registry
python3 .claude/skills/batch-processor/scripts/batch_process.py

# Process specific URLs in parallel
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --urls "url1" "url2" "url3" \
  --parallel
```

## Dependencies

This skill orchestrates the following skills:
- **tif-web-scraper** - Web scraping with version tracking
- **source-diff** - Change detection between versions
- **position-extractor** - Position extraction with LLM titles
- **position-migration** - Semantic hierarchy migration with auto mode

All dependencies must be installed and functional.

## Limitations

- Only works with TIF website URLs (teknologiateollisuus.fi)
- Requires all four dependency skills to be available
- Auto mode migration may make decisions you disagree with (review commits)
- Network errors during scraping will cause failure
- Git conflicts will cause commit failures

## Best Practices

1. **Review commits** after auto-processing to ensure quality
2. **Use --skip-commits** flag when testing to avoid polluting git history
3. **Process one URL first** before batch processing many URLs
4. **Check git status** before running to ensure clean working directory
5. **Pull latest changes** before processing to avoid conflicts
