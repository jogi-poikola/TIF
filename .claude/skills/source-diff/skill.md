---
name: source-diff
description: Compare two versions of a TIF source file and detect changes at the position/bullet-point level. Generates a structured change report showing new, modified, and removed positions. Use when re-scraping a URL to identify what content changed.
---

# Source Diff

## Overview

Compare two versions of a source markdown file (scraped at different times) and detect changes at the bullet-point level (position statements). This skill generates a structured change report that classifies positions as:

- **NEW**: Positions that appear in the new version but not in the old
- **MODIFIED**: Positions that exist in both but have changed content
- **REMOVED**: Positions that appear in the old version but not in the new
- **UNCHANGED**: Positions that are identical in both versions

## Use Cases

1. **Re-scraping workflow**: After re-scraping a URL, compare old vs new versions
2. **Change tracking**: Understand how TIF positions evolve over time
3. **Selective processing**: Only extract and migrate changed positions
4. **Audit trail**: Document what changed between scrape versions

## Workflow

### 1. Input

Two source markdown files:
- **Old version**: Previous scrape (e.g., `2025-11-04-datakeskukset-web.md`)
- **New version**: Latest scrape (e.g., `2025-12-15-datakeskukset-web.md`)

### 2. Detection Method

**Section-level change detection** (as specified by user preference):

- Extracts bullet-pointed position statements from both files
- Uses fuzzy text similarity to match positions between versions
- Classifies each position based on similarity:
  - **≥90% similarity**: UNCHANGED
  - **70-89% similarity**: MODIFIED (same position, different wording)
  - **<70% similarity**: NEW or REMOVED (depending on which file it appears in)

### 3. Output

**Change report** in markdown format:

```markdown
# Source Change Report

**Old Version:** 2025-11-04-datakeskukset-web.md
**New Version:** 2025-12-15-datakeskukset-web.md
**Compared:** 2025-12-15

## Summary
- ✨ New positions: 3
- ✏️ Modified positions: 2
- ❌ Removed positions: 1
- ✓ Unchanged positions: 8

## New Positions

1. **[Line 45]** Kehitetään datakeskusten energiatehokkuutta...
2. **[Line 67]** Tuetaan kvanttilaskennan infrastruktuuria...
3. **[Line 89]** Varmistetään datakeskusten kyberturvallisuus...

## Modified Positions

1. **[Line 23]**
   - **Before:** Nopeutetaan lupaprosesseja...
   - **After:** Nopeutetaan datakeskusten ja uusiutuvan energian lupaprosesseja EU-direktiivin mukaisesti...
   - **Similarity:** 82%
   - **Change:** Added specifics about EU directive

2. **[Line 56]**
   - **Before:** Datakeskukset tukevat sähköverkkoa...
   - **After:** Datakeskukset osallistuvat sähköjärjestelmän tasapainoon ja hukkalämmön hyödyntämiseen...
   - **Similarity:** 78%
   - **Change:** Added waste heat utilization

## Removed Positions

1. **[Line 78]** Pilotointi-ohjelma datakeskuksille... (no longer in new version)

## Unchanged Positions

1. **[Line 12]** Nopeutetaan datakeskusten lupaprosesseja
2. **[Line 34]** Suomi vaikuttamaan EU-tason datakeskussääntelyyn
   ...
```

**JSON output** (for programmatic use):

```json
{
  "old_file": "sources/TIF web/2025-11-04-datakeskukset-web.md",
  "new_file": "sources/TIF web/2025-12-15-datakeskukset-web.md",
  "compared_date": "2025-12-15",
  "summary": {
    "new": 3,
    "modified": 2,
    "removed": 1,
    "unchanged": 8
  },
  "changes": {
    "new": [
      {"line": 45, "text": "Kehitetään datakeskusten..."}
    ],
    "modified": [
      {
        "old_line": 23,
        "new_line": 23,
        "old_text": "Nopeutetaan lupaprosesseja...",
        "new_text": "Nopeutetaan datakeskusten...",
        "similarity": 0.82
      }
    ],
    "removed": [
      {"line": 78, "text": "Pilotointi-ohjelma..."}
    ],
    "unchanged": [
      {"line": 12, "text": "Nopeutetaan datakeskusten lupaprosesseja"}
    ]
  }
}
```

## Usage

### Command Line

```bash
# Generate change report
python .claude/skills/source-diff/scripts/diff_sources.py \
  sources/TIF\ web/2025-11-04-datakeskukset-web.md \
  sources/TIF\ web/2025-12-15-datakeskukset-web.md

# Output to specific file
python .claude/skills/source-diff/scripts/diff_sources.py \
  OLD_FILE NEW_FILE \
  --output change-reports/2025-12-15-datakeskukset-changes.md

# JSON output for programmatic use
python .claude/skills/source-diff/scripts/diff_sources.py \
  OLD_FILE NEW_FILE \
  --format json \
  --output changes.json
```

### From Python

```python
from diff_sources import SourceDiffer

differ = SourceDiffer()
changes = differ.compare_versions(old_file, new_file)

# Access results
print(f"New positions: {len(changes['new'])}")
print(f"Modified: {len(changes['modified'])}")

# Generate report
differ.generate_markdown_report(changes, "change-report.md")
```

## Integration with Other Skills

### With position-extractor

```python
# Extract only changed positions
extract_positions(
    new_source_file,
    change_report=changes,
    only_changed=True  # Skip unchanged positions
)
```

### With position-migration

```python
# Migrate with change awareness
migrate_positions(
    mode='auto',
    handle_modified=True  # Auto-append to canonical
)
```

## Configuration

### Similarity Thresholds

Adjust in `scripts/diff_sources.py`:

```python
UNCHANGED_THRESHOLD = 0.90  # ≥90% = unchanged
MODIFIED_THRESHOLD = 0.70   # 70-89% = modified
# <70% = new/removed
```

### Extraction Patterns

Customize what counts as a "position statement":

```python
# Default: bullet points starting with - or *
# Can be extended to match other patterns
```

## Best Practices

1. **Always compare consecutive versions**: Compare the latest previous scrape with the new scrape
2. **Review modified positions**: Check that similarity matching correctly identified changes
3. **Keep change reports**: Store in `processed/change-reports/` for audit trail
4. **Use JSON for automation**: Programmatic workflows should use JSON output

## Resources

### scripts/

**diff_sources.py** - Main diff script with:
- Bullet-point extraction from markdown
- Fuzzy text similarity matching
- Change classification logic
- Markdown and JSON report generation
- Command-line and Python API interfaces
