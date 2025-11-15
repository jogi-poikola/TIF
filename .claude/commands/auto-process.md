---
description: Automatically process a TIF URL end-to-end (scrape, extract, migrate in auto mode)
---

Automatically process a TIF website URL through the complete workflow with minimal intervention.

## Workflow

When the user provides a URL, execute:

```bash
python3 .claude/skills/auto-process-source/scripts/auto_process_source.py "<URL>"
```

This will:
1. Scrape (or re-scrape) the URL with version tracking
2. Detect changes if re-scraping (using source-diff)
3. Extract positions (only changed if re-scrape)
4. Migrate positions to semantic hierarchy in auto mode
5. Create git commits at meaningful moments:
   - After scraping
   - After extraction
   - After migration

## Exit Conditions

The script will exit successfully without error if:
- No changes detected (re-scrape with identical content)
- No positions to extract
- No drafts to migrate

The script will exit with error only if:
- Scraping fails (network error, invalid URL)
- Extraction fails (script error)
- Migration fails (script error, conflicts)

## Usage

```
/auto-process https://teknologiateollisuus.fi/tavoitteemme/datakeskukset/
```

## Important Notes

- Uses **auto mode** for position migration (no user prompts)
- Creates **git commits** automatically at each stage
- Handles **re-scrapes** intelligently (only processes changes)
- May take 30-60 seconds per URL depending on content
- **Title generation:** Uses improved fallback algorithm (no API key needed, good quality)
  - For best titles, use `/batch-process-parallel` which uses Claude Code in agents

## Testing Mode

To test without git commits:

```bash
python3 .claude/skills/auto-process-source/scripts/auto_process_source.py \
  "<URL>" \
  --skip-commits
```

## Expected Output

```
======================================================================
AUTO-PROCESSING TIF SOURCE
======================================================================
URL: https://teknologiateollisuus.fi/tavoitteemme/datakeskukset/

🔄 Scraping: https://...
📋 Previous scrapes found: 1
✅ Created source at: sources/TIF web/.../2025-11-10-datakeskukset-web.md

📝 Committing: Re-scrape TIF source: https://...

📊 Comparing versions...
Summary:
  ✨ New positions:       2
  ✏️  Modified positions:  1

📝 Extracting positions...
Created 3 position files

📝 Committing: Extract positions from: 2025-11-10-datakeskukset-web.md

🚀 Migrating 3 positions in auto mode...
✓ Migrated: ...

📝 Committing: Migrate positions from: 2025-11-10-datakeskukset-web.md

✅ Auto-processing complete!
======================================================================
```
