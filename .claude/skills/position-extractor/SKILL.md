---
name: position-extractor
description: Extract bullet-pointed positions from TIF markdown source files and create individual position files with Obsidian transclusions. Use this skill when the user requests to extract positions from a source file, create position files, or generate paper files with transclusions.
---

# Position Extractor

## Overview

This skill extracts individual positions from TIF source markdown files and creates structured position files along with a paper file containing Obsidian transclusions. Each bullet-pointed position in the source file becomes a standalone position file in the `positions-drafts/` folder, and a corresponding paper file is created in `papers/` that references these positions using Obsidian transclusion syntax wrapped in callouts (`[!todo]+`). The system creates bidirectional links: position files include a heading that links back to the paper, and paper transclusions use heading anchors to link to specific sections within position files.

## When to Use This Skill

Use this skill when:
- User requests to extract positions from a source markdown file
- User wants to create individual position files from a source document
- User asks to generate a paper file with Obsidian transclusions
- User mentions processing TIF position documents or creating position drafts

## How It Works

The skill uses a Python script (`scripts/extract_positions.py`) that:

1. **Reads the source file** - Parses the markdown content
2. **Extracts positions** - Identifies bullet-pointed items (lines starting with `- `)
3. **Generates titles** - Creates descriptive titles (max 7 words) from the first sentence of each position
4. **Creates position files** - Generates individual markdown files in `positions-drafts/` with YAML frontmatter
5. **Creates paper file** - Generates a copy of the source in `papers/` with positions replaced by Obsidian transclusions

## Workflow

### Step 1: Identify the Source File

Ask the user for the path to the source markdown file if not provided. The source file should be a TIF web scraped document (e.g., `sources/TIF web/tavoitteemme/web-digitalisaatio-ja-datatalous.md`).

### Step 2: Run the Extraction Script

Execute the script with the source file path:

```bash
python scripts/extract_positions.py "<source-file-path>"
```

Example:
```bash
python scripts/extract_positions.py "sources/TIF web/tavoitteemme/web-digitalisaatio-ja-datatalous.md"
```

The script will:
- Extract all positions marked with bullet points (`- `)
- Create position files with titles as filenames (e.g., `Vauhditetaan teollisuuden digitalisaatiota.md`)
- Generate a paper file with transclusions (e.g., `paper-web-digitalisaatio-ja-datatalous.md`)

### Step 3: Review the Output

Show the user:
- Number of positions extracted
- List of created position files
- Location of the paper file

### Step 4: Optional Adjustments

If the user wants to modify:
- Position titles - Edit the individual position files
- Paper structure - Edit the paper file in `papers/`
- Position numbering - Rename the position files

## Output Structure

### Position Files

Each position file in `positions-drafts/` contains:

```yaml
---
type: position
title: "Descriptive title max 7 words"
source: "Original source URL from input file"
up:
related:
  - "[[paper-web-filename]]"
---

## [[paper-web-filename]]

[Position text with links preserved]
```

**Key features:**
- Filename format: `<title>.md` (e.g., `Vauhditetaan teollisuuden digitalisaatiota.md`)
- Includes heading that links back to the paper file
- Heading serves as an anchor for transclusions from the paper

### Paper File

The paper file in `papers/` is a copy of the source file with positions replaced by Obsidian transclusions wrapped in callouts:

```markdown
> [!todo]+ Vauhditetaan teollisuuden digitalisaatiota
> ![[Vauhditetaan teollisuuden digitalisaatiota#paper-web-digitalisaatio-ja-datatalous]]

> [!todo]+ Tuetaan tekoälyn kehitystä ja käyttöönottoa
> ![[Tuetaan tekoälyn kehitystä ja käyttöönottoa#paper-web-digitalisaatio-ja-datatalous]]

> [!todo]+ Kehitetään julkisia ICT-hankintoja
> ![[Kehitetään julkisia ICT-hankintoja#paper-web-digitalisaatio-ja-datatalous]]
```

**Key features:**
- Transclusions include heading anchors (`#paper-name`)
- Anchors link directly to the specific heading in each position file
- Creates bidirectional linking between paper and positions

## Example Usage

**Input:** `sources/TIF web/tavoitteemme/web-digitalisaatio-ja-datatalous.md`

**Source content includes:**
- Vauhditetaan teollisuuden digitalisaatiota. [description...] [Lue lisää](url)
- Tuetaan tekoälyn kehitystä ja käyttöönottoa. [description...] [Lue lisää](url)
- Kehitetään julkisia ICT-hankintoja. [description...] [Lue lisää](url)

**Output:**

Position files created in `positions-drafts/`:
- `Vauhditetaan teollisuuden digitalisaatiota.md`
- `Tuetaan tekoälyn kehitystä ja käyttöönottoa.md`
- `Kehitetään julkisia ICT-hankintoja.md`

Paper file created in `papers/`:
- `paper-web-digitalisaatio-ja-datatalous.md` (with transclusions)

## Script Details

### extract_positions.py

**Location:** `scripts/extract_positions.py`

**Usage:**
```bash
python scripts/extract_positions.py <source-file-path>
```

**What it does:**
- Parses markdown content to find bullet-pointed positions
- Extracts source URL from YAML frontmatter
- Generates descriptive titles (max 7 words) from first sentence
- Creates filenames using titles with spaces (e.g., `Kehitetään julkisia ICT-hankintoja.md`)
- Generates position files with:
  - Proper YAML frontmatter including link to paper in `related` field
  - Heading that links back to the paper file (`## [[paper-name]]`)
- Creates paper file with:
  - Obsidian transclusion syntax wrapped in callouts (`> [!todo]+ title`)
  - Heading anchors for direct linking (`> ![[filename#paper-name]]`)

**Requirements:**
- Python 3.6+
- Standard library only (no external dependencies)

## Troubleshooting

**No positions found:**
- Check that the source file contains bullet points starting with `- `
- Verify the markdown formatting is correct

**Source URL not found:**
- Ensure the source file has YAML frontmatter with a `source:` field
- Check the frontmatter format matches: `source: "URL"`

**Position titles too long:**
- The script automatically limits titles to 7 words
- If needed, manually edit the position files after creation

**Directories don't exist:**
- The script automatically creates `positions-drafts/` and `papers/` directories
- Ensure write permissions in the current directory
