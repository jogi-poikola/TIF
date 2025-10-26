# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a knowledge management repository containing Teknologiateollisuus (Technology Industries of Finland - TIF) position documents. The repository contains approximately 120 markdown files organized in a hierarchical structure representing policy positions and strategic areas.

## Repository Structure

The repository uses a **hierarchical numbering system** for organizing position documents:

- `positions/` - Root directory containing all position documents
  - `0000 Kestävän ja vahvan kasvun ratkaisut.md` - Top-level overview document
  - `1000 Resilienssi/` - Resilience and adaptation
  - `2000 Kriittiset teknologiat/` - Critical technologies (semiconductors, quantum, AI, HPC)
  - `3000 Osaaminen/` - Competence and skills
  - `4000 Investointiympäristö/` - Investment environment
  - `5000 Työelämä/` - Working life
  - `6000 Kestävä kasvu/` - Sustainable growth
  - `7000 Talous- ja veropolitiikka/` - Economic and tax policy
  - `8000 Digitalisaatio ja datatalous/` - Digitalization and data economy
  - `9000 Innovaatiot/` - Innovations

**Numbering convention:**
- Four-digit prefixes (e.g., `1000`, `2000`) indicate main theme areas
- Sub-topics use increments (e.g., `3100`, `3200`, `3300` under `3000 Osaaminen/`)
- Further sub-topics continue the pattern (e.g., `3510`, `3520` under `3500 Osaajatarve/`)
- Directories and files both use this numbering scheme

## Document Format

All position documents follow a consistent structure:

**YAML Frontmatter:**
```yaml
---
type: position
title: "Document Title"
up: "[[Parent Document]]"
related:
tags:
  - position
icon:
---
```

**Key elements:**
- `type: position` - Identifies the document type
- `title` - The position or topic name
- `up` - Parent document link using Obsidian wiki-link format `[[Document Name]]`
- `related` - Related documents (may be empty)
- `tags` - Document categorization (optional)

**Content structure:**
- Documents use Obsidian-style wiki links for cross-references: `[[NNNN Topic Name]]`
- Hierarchical parent documents typically list child topics as bullet points
- Leaf documents contain actual position descriptions and details

## Working with Documents

**When creating new positions:**
1. Determine the appropriate parent category based on the numbering hierarchy
2. Assign the next available number in the sequence (e.g., if `3500` exists, next sibling would be `3600`)
3. Create directory for topics with sub-positions, or standalone `.md` file for leaf positions
4. Include proper YAML frontmatter with correct `up` reference to parent
5. Update parent document to include wiki-link to new position

**When editing existing positions:**
1. Preserve the YAML frontmatter structure
2. Maintain consistent wiki-link format for cross-references
3. Keep numbering system intact (renumbering requires updating multiple references)

## File Organization Notes

- `.gitignore` excludes `.obsidian/` (Obsidian configuration) and `.DS_Store` (macOS metadata)
- `positions/0000.base` contains Obsidian database view configuration
- This is a documentation/content repository with no build, test, or compilation commands
- Content is in Finnish

## Git Workflow

This repository uses a simple main branch workflow:
- Main branch: `main`
- Repository starts with initial commit: "Initial commit: TIF position documents"
- When committing, describe changes to position documents clearly
