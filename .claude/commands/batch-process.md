---
description: Process multiple TIF URLs in parallel from the registry
---

Process multiple TIF website URLs in parallel using the batch processor.

## Workflow

The batch processor reads URLs from `sources/scraped-urls.txt` and processes them using the auto-process-source workflow.

### Process All URLs

When the user wants to re-scrape everything:

```bash
python3 .claude/skills/batch-processor/scripts/batch_process.py --all --parallel
```

### Process Specific URLs

When the user provides specific URLs:

```bash
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --urls "URL1" "URL2" "URL3" \
  --parallel
```

### Process with Filtering

When the user wants to filter by topic/pattern:

```bash
# Include only URLs matching pattern
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --include "digitalisaatio" --all --parallel

# Multiple patterns
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --include "digitalisaatio" "innovaatiot" --all --parallel

# Exclude patterns
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --include "tavoitteemme" --exclude "viestimme" --all --parallel
```

## Options

- `--all` - Process all URLs in registry
- `--urls URL [URL ...]` - Specific URLs to process
- `--include PATTERN [PATTERN ...]` - Include only URLs matching patterns
- `--exclude PATTERN [PATTERN ...]` - Exclude URLs matching patterns
- `--parallel` - Process in parallel (recommended)
- `--max-workers N` - Number of parallel workers (default: 4)
- `--skip-commits` - Skip git commits (for testing)

## Usage Examples

### Re-scrape everything in parallel

```
/batch-process --all
```

### Process specific topics

```
/batch-process --include "digitalisaatio" "datakeskukset"
```

### Process specific URLs

```
/batch-process --urls "https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/" "https://teknologiateollisuus.fi/tavoitteemme/innovaatiot/"
```

## Performance

- **Parallel mode:** Processes 4 URLs simultaneously by default
- **Time estimate:** ~30-60 seconds per URL
- **Recommended:** Use parallel mode for 3+ URLs

## Output Example

```
======================================================================
BATCH PROCESSING (Parallel)
======================================================================
URLs to process: 5
Max workers: 4

[Processing each URL in parallel...]

======================================================================
BATCH PROCESSING SUMMARY
======================================================================

Total: 5
✅ Successful: 4
❌ Failed: 1

✅ Successfully processed:
   - URL1
   - URL2
   - URL3
   - URL4

❌ Failed to process:
   - URL5 (Network timeout)
```

## Important Notes

- Each URL is processed using the auto-process-source workflow
- Git commits are created automatically for each URL
- Failed URLs are reported but don't stop other URLs from processing
- Re-scrapes only extract changed positions (efficient)

## Before Running

1. Ensure git working directory is clean
2. Pull latest changes if working with others
3. Consider testing with 1-2 URLs first

## After Running

Review the git commits to ensure quality:

```bash
git log --oneline -20
```
