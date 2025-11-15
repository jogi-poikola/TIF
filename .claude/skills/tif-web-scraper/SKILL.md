---
name: tif-web-scraper
description: Scrape content from Teknologiateollisuus (TIF) website URLs and convert them to markdown source files with proper frontmatter. Use this skill when the user requests to scrape a TIF website URL (e.g., teknologiateollisuus.fi), extract web content for documentation, or convert TIF web pages to markdown format.
---

# TIF Web Scraper

## Overview

This skill enables scraping content from Teknologiateollisuus (Technology Industries of Finland - TIF) website and converting it into properly formatted markdown source files. The skill:
- Extracts the main content from TIF web pages
- Excludes sidebar elements and navigation
- Stops at "Lisätiedot:" sections
- Extracts publication date from "Päivitetty DD.MM.YYYY" format
- Generates date-prefixed filenames: `YYYY-MM-DD-slug-web.md`
- Creates files in `sources/TIF web/` with folder structure matching URL path
- Sets `type: web` and `scraped: YYYY-MM-DD` in frontmatter
- Tracks scrapes in `sources/scraped-urls.txt` registry for version management
- Detects and warns about similar/duplicate URLs

## When to Use This Skill

Use this skill when:
- User provides a TIF website URL (teknologiateollisuus.fi) and requests to scrape it
- User asks to "scrape", "extract", or "convert" content from TIF website
- User wants to create source files from TIF web content
- User mentions scraping TIF positions or policy pages

## How to Use

### Workflow

1. **Receive URL**: User provides a TIF website URL (e.g., `https://teknologiateollisuus.fi/tavoitteemme/osaava-tyovoima/`)

2. **Determine output location**: Default is `sources/TIF web/`, but user may specify a different location

3. **Identify parent document** (optional): Ask user if this paper should reference a parent document in the `up` field

4. **Run the scraping script**: Execute `scripts/scrape_tif_web.py` with appropriate parameters

5. **Verify output**: Check the created markdown file and show the user the path

### Script Usage

The `scrape_tif_web.py` script handles all scraping and markdown generation:

```bash
python scripts/scrape_tif_web.py <url> [output_dir] [parent_doc]
```

**Parameters:**
- `url` (required): The TIF website URL to scrape
- `output_dir` (optional): Output directory path, defaults to `sources/TIF web/`
- `parent_doc` (optional): Parent document name for the `up` field (e.g., `3000 Osaaminen`)

**Examples:**

Basic usage:
```bash
python scripts/scrape_tif_web.py https://teknologiateollisuus.fi/tavoitteemme/osaava-tyovoima/
```

With custom output directory:
```bash
python scripts/scrape_tif_web.py <url> "sources/TIF web"
```

With parent document:
```bash
python scripts/scrape_tif_web.py <url> "sources/TIF web" "3000 Osaaminen"
```

### Output Format

The script generates markdown files with this frontmatter structure:

```yaml
---
type: web
title: "Page Title from Website"
source: "https://teknologiateollisuus.fi/..."
scraped: 2025-11-04
up: "[[Parent Document]]"  # Optional
related:
---
```

Followed by the cleaned main content in markdown format.

**Filename format:** `YYYY-MM-DD-slug-web.md`
- Date extracted from "Päivitetty DD.MM.YYYY" in content
- Falls back to current date if not found
- Example: `2025-11-04-datakeskukset-web.md`

### Content Extraction

The script:
- Extracts main content area (excluding sidebars and navigation)
- Converts HTML headings to markdown headings (h1-h4 → #, ##, ###, ####)
- Converts paragraphs and lists to markdown format
- Stops extraction when encountering "Lisätiedot:" (Additional information)
- Removes excessive whitespace and cleans formatting

### Folder Structure

The script automatically replicates the **complete URL path structure**:

**Example:**
- URL: `https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/datakeskukset/`
- Creates: `sources/TIF web/tavoitteemme/digitalisaatio-ja-datatalous/2025-11-04-datakeskukset-web.md`

**How it works:**
- Last path segment (`datakeskukset`) becomes the filename slug
- All other segments (`tavoitteemme/digitalisaatio-ja-datatalous`) become folder hierarchy
- Date prefix added to filename: `YYYY-MM-DD-slug-web.md`

**IMPORTANT**: Always use the full URL path to maintain consistent organization.

### URL Registry and Version Tracking

The script automatically logs all scraped URLs to `sources/scraped-urls.txt`:

```
# Format: YYYY-MM-DD | URL | Output File
2025-11-04 | https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/datakeskukset/ | sources/TIF web/tavoitteemme/digitalisaatio-ja-datatalous/2025-11-04-datakeskukset-web.md
```

**Features:**
- Tracks all scraped URLs with dates and file paths
- Detects when URL was previously scraped
- Warns about similar URLs with different paths (duplicate detection)
- Enables version tracking for re-scraping workflow
- Maintains complete audit trail

**Re-scraping behavior:**
- When scraping an already-registered URL, scraper detects previous versions
- Creates new file with current date (e.g., `2025-12-15-datakeskukset-web.md`)
- Suggests running diff command to compare versions
- Use `/re-scrape` command for complete update workflow with diff

**URL validation:**
If you provide a shortened URL like `/tavoitteemme/datakeskukset/` when the full URL `/tavoitteemme/digitalisaatio-ja-datatalous/datakeskukset/` was already scraped, the scraper will:
- Detect the similar URL in registry
- Warn about potential duplicate with different folder structure
- Ask for confirmation before proceeding
```

This will re-scrape all URLs in the registry and you can use `git diff` to see what changed.

### Dependencies

The script requires:
- `requests` - for HTTP requests
- `beautifulsoup4` - for HTML parsing

If not installed, run:
```bash
pip install requests beautifulsoup4
```

The script will display a helpful error message if these packages are missing.

## Example Usage Scenarios

**Scenario 1: Basic scraping**
```
User: "Scrape https://teknologiateollisuus.fi/tavoitteemme/digitalisaatio-ja-datatalous/datakeskukset/"

Actions:
1. Run: python3 .claude/skills/tif-web-scraper/scripts/scrape_tif_web.py <url>
2. Verify the created file in sources/TIF web/
3. Output: sources/TIF web/tavoitteemme/digitalisaatio-ja-datatalous/2025-11-04-datakeskukset-web.md
```

**Scenario 2: With parent document**
```
User: "Scrape <url> and link it to the '8000 Digitalisaatio ja datatalous' position"

Actions:
1. Run: python3 .claude/skills/tif-web-scraper/scripts/scrape_tif_web.py <url> "sources/TIF web" "8000 Digitalisaatio ja datatalous"
2. Verify the frontmatter includes: up: "[[8000 Digitalisaatio ja datatalous]]"
3. Show user the output
```

**Scenario 3: Batch processing**
```
User: "Scrape these three URLs: <url1>, <url2>, <url3>"

Actions:
1. Run the script three times with each URL
2. Report all created file paths with dates
3. Summarize the batch operation
```

## Troubleshooting

**If scraping fails:**
1. Verify the URL is accessible and from teknologiateollisuus.fi
2. Check network connectivity
3. Examine the HTML structure if the selectors don't match

**If content extraction is incomplete:**
1. The script may need adjustment for specific page layouts
2. Check if "Lisätiedot:" appears early in the content
3. Verify the main content selector matches the page structure

**If dependencies are missing:**
1. The script will display installation instructions
2. Run: `pip install requests beautifulsoup4`
