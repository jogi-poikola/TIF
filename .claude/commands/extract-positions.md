---
description: Extract positions from a TIF source file and create position files with LLM-generated titles
---

You are helping extract positions from a TIF source markdown file and create individual position files with excellent titles.

**IMPORTANT:** YOU (Claude Code) must generate the titles, NOT the Python script. The script will use the titles you provide.

## Workflow

### Step 1: Get Source File
Ask the user for the source file path (or use the file they opened/mentioned)

### Step 2: Read Source and Extract Positions
Read the source file and extract all bullet-pointed positions:
- Look for lines starting with "- "
- Each bullet point is one position
- Multi-line positions continue until empty line

### Step 3: Generate Titles (YOU DO THIS)
For EACH position text, generate ONE maximally descriptive title using these guidelines:

**Title Rules:**
- Maximum 7 words
- No special characters (only: a-z A-Z ä ö å Ä Ö Å 0-9 spaces hyphens)
- Capture the core essence and action of the position
- Prefer noun phrases or gerund forms when more descriptive
- Remove parenthetical content like "(esimerkiksi...)"
- Focus on main action and subject
- Must be in Finnish

**How to generate:**
Process each position text and create its title in ONE batch. Output format:
```
Position 1 title
Position 2 title
Position 3 title
...
```

### Step 4: Call Extraction Script
Once you have ALL titles, call the script with pipe-separated titles:

```bash
python3 .claude/skills/position-extractor/scripts/extract_positions.py \
  "source/file/path.md" \
  --titles="title1|title2|title3|..."
```

**Critical:** Join titles with pipe character "|" with NO spaces around pipes.

## Example Good Titles

These examples show the desired style:
- "Datakeskukset tukemaan sähköjärjestelmän tasapainoa ja hukkalämmön hyödyntämistä"
- "Sähköverkkosuunnittelu kytketään datakeskusklustereiden kehitykseen"
- "Ennakoitava ja investointeja tukeva toimintaympäristö datakeskuksille"
- "Nopeutetaan datakeskusten ja uusiutuvan energian lupaprosesseja"

## Important Notes

- Titles should be in Finnish
- Titles must be maximally descriptive within the 7-word limit
- Join multiple titles with pipe character "|" when passing to script
- The script will create files in `positions-drafts/` and `processed/` directories
