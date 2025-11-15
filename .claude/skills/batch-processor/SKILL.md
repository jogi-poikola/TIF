# batch-processor

Process multiple TIF sources in parallel using autonomous agents (recommended) or Python multiprocessing (legacy).

## Overview

This skill enables batch processing of TIF website URLs using two approaches:

### Approach 1: Agent-Based Parallel Processing (Recommended)

Uses Claude Code's Task tool to launch separate autonomous agents:
- Each URL processed in isolated agent with own context window
- True parallel execution via Task tool
- Main context stays clean (agents handle details)
- Uses `/batch-process-parallel` command

### Approach 2: Python Multiprocessing (Legacy)

Uses Python's multiprocessing for parallel execution:
- All processing in same Python process
- Requires more system resources
- Direct script invocation
- Kept for backwards compatibility

**Recommendation:** Use Approach 1 (agent-based) for better isolation and cleaner execution.

## When to Use

Use this skill when you want to:
- **Re-scrape all sources** to check for updates across the entire TIF website
- **Process multiple URLs** without manual intervention for each
- **Speed up processing** by running multiple URLs in parallel
- **Filter and process** specific subsets of sources (e.g., only digitalization topics)

## Usage - Agent-Based (Recommended)

### Process All URLs

```
/batch-process-parallel --all
```

Claude will:
1. Read all unique URLs from `sources/scraped-urls.txt`
2. Launch one autonomous agent per URL (in a single message)
3. Each agent runs `auto-process-source` workflow
4. Collect results and report summary

### Process Specific URLs

```
/batch-process-parallel --urls "URL1" "URL2" "URL3"
```

### Filter by Pattern

```
# Include only URLs matching pattern
/batch-process-parallel --include "digitalisaatio"

# Multiple patterns
/batch-process-parallel --include "digitalisaatio" "innovaatiot"

# With exclusions
/batch-process-parallel --include "tavoitteemme" --exclude "viestimme"
```

### How It Works

1. **Determine URLs**: Read registry and apply filters
2. **Launch agents**: Use Task tool to launch N agents in parallel (one message)
3. **Isolated execution**: Each agent has own context, runs auto-process-source
4. **Collect results**: Wait for all agents to complete
5. **Report summary**: Show success/failure stats

**Benefits:**
- ✅ Main context window stays clean
- ✅ True parallel execution
- ✅ Isolated failures (one URL failure doesn't affect others)
- ✅ Cost-effective (uses haiku model for agents)

## Usage - Python Multiprocessing (Legacy)

### Process All URLs (Re-scrape Everything)

```bash
python3 .claude/skills/batch-processor/scripts/batch_process.py --all
```

### Process Specific URLs

```bash
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --urls \
    "https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/" \
    "https://teknologiateollisuus.fi/tavoitteemme/innovaatiot/" \
    "https://teknologiateollisuus.fi/tavoitteemme/datakeskukset/"
```

### Process with Pattern Filtering

```bash
# Include only URLs matching pattern
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --include "digitalisaatio" --all

# Exclude URLs matching pattern
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --include "tavoitteemme" --exclude "viestimme" --all

# Combine multiple patterns
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --include "digitalisaatio" "innovaatiot" "datakeskukset" --all
```

### Parallel Processing

```bash
# Process in parallel with 4 workers (default)
python3 .claude/skills/batch-processor/scripts/batch_process.py --all --parallel

# Process in parallel with custom worker count
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --all --parallel --max-workers 8
```

### Testing Mode (Skip Commits)

```bash
# Test without creating git commits
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --urls "https://..." --skip-commits
```

## Command Options

| Option | Description |
|--------|-------------|
| `--all` | Process all URLs in registry (required if no --urls or --include) |
| `--urls URL [URL ...]` | Specific URLs to process (space-separated) |
| `--include PATTERN [PATTERN ...]` | Include only URLs matching regex patterns |
| `--exclude PATTERN [PATTERN ...]` | Exclude URLs matching regex patterns |
| `--parallel` | Process URLs in parallel (default: sequential) |
| `--max-workers N` | Maximum parallel workers (default: 4) |
| `--skip-commits` | Skip git commits (for testing) |
| `--repo-root PATH` | Repository root (default: current directory) |

## Processing Modes

### Sequential Mode (Default)

Processes URLs one at a time in order:
- **Pros:** Easier to debug, cleaner git history, less resource intensive
- **Cons:** Slower for large batches
- **Use when:** You want to carefully review each URL's processing

### Parallel Mode (`--parallel`)

Processes multiple URLs simultaneously using multiprocessing:
- **Pros:** Much faster for large batches, efficient use of system resources
- **Cons:** Harder to debug, git commits may be interleaved
- **Use when:** You have many URLs and want fast processing
- **Recommended workers:** 4-8 (depends on your system and network)

## Workflow Per URL

For each URL, the batch processor invokes `auto-process-source` which:

1. **Scrapes** (or re-scrapes) the URL
2. **Detects changes** if re-scraping
3. **Extracts positions** (only changed if re-scrape)
4. **Migrates positions** in auto mode
5. **Creates git commits** at each stage

See `auto-process-source` skill documentation for details.

## Output Example

```
======================================================================
BATCH PROCESSING (Parallel)
======================================================================
URLs to process: 5
Max workers: 4

[1/5] Processing URL...
======================================================================
Processing: https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/
======================================================================

🔄 Scraping: https://...
📋 Previous scrapes found: 1
✅ Created source at: sources/TIF web/.../2025-11-10-digitalisaatio-ja-datatalous-web.md

📊 Comparing versions...
Summary:
  ✨ New positions:       2
  ✏️  Modified positions:  1
  ❌ Removed positions:   0
  ✓ Unchanged positions: 12

📝 Extracting positions...
Created 3 position files in positions-drafts/

🚀 Migrating 3 positions in auto mode...
✓ Migrated: ...

✅ Auto-processing complete!

[2/5] Processing URL...
...

======================================================================
BATCH PROCESSING SUMMARY
======================================================================

Total: 5
✅ Successful: 4
❌ Failed: 1

✅ Successfully processed:
   - https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/
   - https://teknologiateollisuus.fi/tavoitteemme/innovaatiot/
   - https://teknologiateollisuus.fi/tavoitteemme/datakeskukset/
   - https://teknologiateollisuus.fi/tavoitteemme/osaaminen/

❌ Failed to process:
   - https://teknologiateollisuus.fi/tavoitteemme/tyoelama/
     Error: Network timeout
```

## Use Cases

### 1. Weekly Update Check

Check all sources for updates once per week:

```bash
python3 .claude/skills/batch-processor/scripts/batch_process.py --all --parallel
```

### 2. Topic-Specific Update

Re-scrape only digitalization-related pages:

```bash
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --include "digitalisaatio" --all --parallel
```

### 3. Targeted Re-processing

Re-process specific URLs that were recently updated:

```bash
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --urls \
    "https://teknologiateollisuus.fi/tavoitteemme/datakeskukset/" \
    "https://teknologiateollisuus.fi/tavoitteemme/tekoaly/"
```

### 4. Test New Features

Test batch processing without committing:

```bash
python3 .claude/skills/batch-processor/scripts/batch_process.py \
  --urls "https://..." \
  --skip-commits
```

## Performance Considerations

### Parallel Processing

- **Recommended workers:** 4-8 for most systems
- **Network bottleneck:** TIF website may rate-limit aggressive scraping
- **CPU/Memory:** Each worker needs ~100-200MB RAM
- **Timeouts:** Each URL has 5-minute timeout

### Sequential Processing

- **Time estimate:** ~30-60 seconds per URL (depends on changes)
- **Network:** Less aggressive, respectful to TIF servers
- **Debugging:** Easier to identify which URL caused issues

## Error Handling

The batch processor handles errors gracefully:

- **Network errors:** Captured and reported, other URLs continue
- **Timeouts:** 5-minute timeout per URL, then marks as failed
- **Script errors:** Captured and reported with error message
- **Git conflicts:** Reported, may cause commit failures

Even if some URLs fail, the processor continues with remaining URLs.

## Dependencies

This skill requires:
- **auto-process-source** - Orchestrates the full workflow per URL
- All dependencies of auto-process-source:
  - tif-web-scraper
  - source-diff
  - position-extractor
  - position-migration

## Best Practices

1. **Start small** - Test with a few URLs before processing all
2. **Use --skip-commits** during testing to avoid polluting git history
3. **Check git status** before batch processing (ensure clean working tree)
4. **Review commits** after batch processing for quality assurance
5. **Use sequential mode** first, then parallel for large batches
6. **Monitor the first few** URLs in parallel mode to ensure stability
7. **Don't overload** TIF servers - use reasonable worker counts (4-8)

## Troubleshooting

### "No URLs found in registry"
- Ensure `sources/scraped-urls.txt` exists and has entries

### "No URLs match the filters"
- Check your --include/--exclude patterns
- Use --urls to specify explicit URLs

### Git commit failures
- Ensure working directory is clean before starting
- Check for merge conflicts from previous operations

### Timeout errors
- Increase timeout in script (default: 5 minutes)
- Check network connectivity
- TIF website may be slow or unavailable

### Parallel processing hangs
- Reduce --max-workers count
- Use sequential mode instead
- Check for deadlocks in auto-process-source script
