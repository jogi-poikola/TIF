---
name: re-scrape
description: Re-scrape a TIF web URL, detect changes from previous version, extract new/modified positions, and guide through migration with auto-append for updated content
---

Re-scrape the provided TIF website URL and handle updates intelligently.

## Workflow Steps

When the user provides a URL, execute these steps:

### 1. Scrape with version tracking

Run the scraper which will:
- Check `sources/scraped-urls.txt` for previous scrapes of this URL
- Create new version with today's date in correct folder structure
- Display previous versions if any exist

```bash
python3 .claude/skills/tif-web-scraper/scripts/scrape_tif_web.py "<URL>"
```

**IMPORTANT**: The scraper creates folder structure from the FULL URL path. For example:
- `https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/datakeskukset/`
- Creates: `sources/TIF web/tavoitteemme/digitalisaatio-ja-datatalous/YYYY-MM-DD-datakeskukset-web.md`

### 2. Check if this is a re-scrape

Look at the scraper output:
- If it says "📋 Previous scrapes found: N" → This is a RE-SCRAPE, proceed to step 3
- If it says "🔍 First scrape of: ..." → This is FIRST SCRAPE, skip to step 4

### 3. Run diff (only for re-scrapes)

If previous versions exist, compare old vs new:

```bash
python3 .claude/skills/source-diff/scripts/diff_sources.py \
  "<old_file_path>" \
  "<new_file_path>"
```

The diff will show:
- ✨ New positions (extract these)
- ✏️ Modified positions (extract these)
- ❌ Removed positions (informational only)
- ✓ Unchanged positions (skip these)

**Decision point**:
- If changes exist → Proceed to step 4 with `--only-changed` flag
- If NO changes (all unchanged) → STOP HERE, inform user no extraction needed

### 4. Extract positions

**For FIRST SCRAPE** (no previous versions):
```bash
/extract-positions "<source_file_path>"
```

**For RE-SCRAPE with changes**:
```bash
python3 .claude/skills/position-extractor/scripts/extract_positions.py \
  "<new_source_file>" \
  --change-report="<diff_json_file>" \
  --only-changed
```

This creates position files only for new/modified content.

### 5. Migrate positions

Use the position-migration skill:
- NEW positions → Normal interactive migration
- MODIFIED positions → Auto-append to existing canonical positions

### 6. Summary

Report what was done:
- Files created
- Changes detected
- Positions extracted and migrated

## Usage

```
/re-scrape https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/datakeskukset/
```

## Important Notes

- **Always use the FULL URL** including all path segments (e.g., `/tavoitteemme/digitalisaatio-ja-datatalous/datakeskukset/`)
- **Check registry first** to see what URL was originally used
- **Run diff before extraction** on re-scrapes to avoid creating duplicates
- **Only extract changed positions** on re-scrapes

## Expected Output

```
🔄 Re-scraping: https://teknologiateollisuus.fi/tavoitteemme/datakeskukset/

📋 Previous scrapes found: 1
   - 2025-11-04: sources/TIF web/tavoitteemme/datakeskukset/2025-11-04-datakeskukset-web.md

🔍 Scraping new version...
✅ Created: sources/TIF web/tavoitteemme/datakeskukset/2025-12-15-datakeskukset-web.md

📊 Comparing versions...
   Old: 2025-11-04-datakeskukset-web.md
   New: 2025-12-15-datakeskukset-web.md

Summary:
  ✨ New positions:       3
  ✏️  Modified positions:  2
  ❌ Removed positions:   1
  ✓ Unchanged positions: 8

📝 Extracting changed positions...
   Created 3 new position files
   Created 2 modified position files
   Created processed file

🚀 Migrating positions...
   NEW: "Kehitetään datakeskusten energiatehokkuutta"
   NEW: "Tuetaan kvanttilaskennan infrastruktuuria"
   NEW: "Varmistetaan datakeskusten kyberturvallisuus"
   MODIFIED: "Datakeskukset tukemaan sähköjärjestelmän tasapainoa"
   MODIFIED: "Nopeutetaan datakeskusten lupaprosesseja"

✅ Re-scrape complete!
   New source: sources/TIF web/.../2025-12-15-datakeskukset-web.md
   Positions migrated: 5
   Change report: processed/change-reports/2025-12-15-datakeskukset-changes.md
```

The user will provide the URL, and this command will orchestrate the entire re-scraping and update workflow.
