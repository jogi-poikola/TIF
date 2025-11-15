# Position Structure Migration Summary

**Date:** 2025-11-09
**Migration Type:** Numbered hierarchy → Semantic hierarchy

## What Changed

### Before: Numbered System
```
positions/
├── 0000 Kestävän ja vahvan kasvun ratkaisut.md
├── 8000 Digitalisaatio ja datatalous/
│   ├── 8200 Tekoälyn hyödyntäminen/
│   │   ├── 8220 Datateollisuus/
│   │   │   ├── 8221 Nopeutetaan datakeskusten...md
│   │   │   └── ... (max 9 positions: 8221-8229)
```

**Problems:**
- **9-item limit** per category (8221-8229, then out of numbers)
- **Rigid numbering** made reorganization difficult
- **Extra frontmatter** (tags, icon fields)
- **Number prefixes** less readable

### After: Semantic System
```
positions/
├── 0000 index.md
├── Digitalisaatio ja datatalous/
│   ├── Digitalisaatio ja datatalous.md
│   ├── Tekoälyn hyödyntäminen/
│   │   ├── Tekoälyn hyödyntäminen.md
│   │   ├── Datateollisuus/
│   │   │   ├── Datateollisuus.md
│   │   │   ├── Nopeutetaan datakeskusten ja uusiutuvan energian lupaprosesseja.md
│   │   │   └── ... (unlimited positions)
```

**Benefits:**
- ✅ **Unlimited scalability** - no position limits
- ✅ **Semantic names** - full descriptive titles
- ✅ **Clean frontmatter** - only essential fields
- ✅ **Easy reorganization** - move folders, update `up` fields
- ✅ **Obsidian-friendly** - native title display

## Migration Statistics

- **Files updated:** 120 (frontmatter cleaned + wiki links updated)
- **Files renamed:** 119 (number prefixes removed)
- **Directories renamed:** 30 (number prefixes removed)
- **Wiki link patterns updated:** 120

## New Frontmatter Standard

### Minimal Required Fields

```yaml
---
type: position
title: "Position Title"
up: "[[Parent Position]]"
related:
  - "[[Related Position 1]]"
  - "[[Source Document]]"
---
```

**Removed fields:**
- `tags` - removed for minimal design
- `icon` - removed for minimal design

## Naming Conventions

1. **Semantic folder names** - Use full descriptive titles
   - Example: `Datateollisuus/` not `8220 Datateollisuus/`

2. **Semantic file names** - Use full descriptive titles with spaces
   - Example: `Nopeutetaan datakeskusten ja uusiutuvan energian lupaprosesseja.md`
   - Obsidian handles spaces natively

3. **Overview files** - Each category folder contains matching overview file
   - Example: `Datateollisuus/Datateollisuus.md`

4. **Root file** - `0000 index.md` serves as repository root

## Reorganization Made Easy

**Moving a category:**
```bash
# Move folder
mv positions/A/B/category positions/A/category

# Update one file
# Edit: category/category.md
# Change: up: "[[B]]" → up: "[[A]]"
```

All positions inside stay unchanged! Only the category overview file needs updating.

## Migration Scripts Created

1. **`migrate_8220_datateollisuus.py`** - Proof of concept for single category
2. **`migrate_all_positions.py`** - Full migration script with:
   - Automatic number prefix removal
   - Wiki link updates
   - Frontmatter cleaning
   - Preserves all content and relationships

## Updated Documentation

- ✅ `CLAUDE.md` - Updated with new semantic structure
- ✅ `.claude/skills/position-migration/skill.md` - Updated skill description
- ✅ `MIGRATION-SUMMARY.md` - This document

## Testing Checklist

- [ ] Open repository in Obsidian
- [ ] Verify wiki links work correctly
- [ ] Check graph view shows proper connections
- [ ] Test search functionality with semantic names
- [ ] Verify frontmatter is clean (no tags/icon)
- [ ] Test reorganizing a category (move folder + update `up`)

## Future Improvements

1. **Automated reorganization tool** - Script to move categories and update references
2. **Frontmatter validator** - Check all files have minimal frontmatter
3. **Orphan detector** - Find positions with broken `up` links
4. **Versioning system** - Implement formal versioning for similar positions (future)

## Rollback Plan

If needed, the old numbered structure can be restored:
1. Revert git commit: `git reset --hard <commit-before-migration>`
2. Or use migration script in reverse (would need modification)

**Recommendation:** Test in Obsidian first before committing to git.
