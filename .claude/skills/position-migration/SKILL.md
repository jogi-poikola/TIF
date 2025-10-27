---
name: position-migration
description: Migrate position files from positions-drafts/ folder to the hierarchical 4-digit positions/ structure through an interactive, consultative process. Use this skill when the user wants to classify, deduplicate, and integrate new position statements into the existing taxonomy with AI-assisted semantic analysis and similarity detection.
---

# Position Migration

## Overview

Migrate position files from `positions-drafts/` folder to the correct location in the hierarchical 4-digit `positions/` folder structure. This is a consultative, interactive process that helps classify, deduplicate, and properly integrate new position statements into the existing taxonomy using semantic similarity analysis and AI-powered suggestions.

## Core Workflow

### 1. Discovery Phase

Scan and analyze the current state:

1. Scan `positions-drafts/` folder for .md files with valid frontmatter
2. Load existing `positions/` folder structure and all position files
3. Generate embeddings for draft positions and existing positions (for similarity matching)
4. Present summary: "Found X draft positions ready for migration"

### 2. Position-by-Position Migration (Interactive)

Process each draft position through the following steps:

#### Step A: Display Draft

Present the current draft clearly:

```
[Processing 3/15]
─────────────────────────────────────────
Draft: "Edistetään julkisen sektorin digitalisaatiota"
Source: https://teknologiateollisuus.fi/...
Related: [[paper-web-digitalisaatio-ja-datatalous]]

Content preview:
[First 200 characters of content...]
─────────────────────────────────────────
```

#### Step B: Semantic Analysis

Perform similarity checking:
- Calculate similarity scores against all existing positions
- If similarity > 70%: Flag as potential duplicate/related
- If similarity > 85%: Flag as likely duplicate
- Use embeddings to compare content semantically

#### Step C: Classification Suggestion

Present AI recommendation with confidence level:

```
🎯 SUGGESTED CLASSIFICATION

Primary suggestion (85% confidence):
  8400 Julkisen sektorin digitalisoituminen
    → New: 8490 Edistetään julkisen sektorin digitalisaatiota

Reasoning: Content focuses on public sector digitalization and data sharing,
strongly aligns with existing 8400 category.

Alternative suggestions:
  2. 8000 > 8700 Digitaalinen yhteiskunta > New: 8750 (45%)
  3. 7000 > 7100 Julkinen talous > New: 7130 (30%)

⚠️ DUPLICATE CHECK
Found similar position:
  8410 Digitaalinen toimintaympäristö (72% similar)
  Preview: "Julkisen sektorin digitaalinen..."
```

#### Step D: User Decision

Present clear choices:

```
Choose action:
  1. Accept suggested classification (8490 under 8400)
  2. View/modify classification details
  3. View similar position content (8410)
  4. Skip this position (leave in drafts)
  5. Stop migration session

Your choice: _
```

#### Step E: Handle User Response

**If user selects option 2 (Modify):**

Guide through hierarchical selection:

```
Choose theme (X000 level):
  [List all themes with numbers]
  Or: 'new' to create new theme

Your choice: 8000

Choose sub-theme under 8000:
  8100 Teollisuuden digitalisoituminen
  8200 Tekoälyn hyödyntäminen
  8300 Julkiset ICT-hankinnat
  8400 Julkisen sektorin digitalisoituminen ← AI suggested
  8500 Digitaalinen turvallisuus
  ... [show all]
  Or: 'new' to create new sub-theme

Your choice: 8400

Position number options under 8400:
  Next available: 8490
  Custom number: [User can specify]

Your choice: 8490

Final location:
  positions/8000 Digitalisaatio ja datatalous/
           8400 Julkisen sektorin digitalisoituminen/
           8490 Edistetään julkisen sektorin digitalisaatiota.md

Confirm? [yes/no/modify]: _
```

**If user selects option 3 (View similar):**

Show full similar position:

```
═══════════════════════════════════════════════════════
SIMILAR POSITION FOUND (72% similarity)

Existing: 8410 Digitaalinen toimintaympäristö
─────────────────────────────────────────
---
type: position
title: "Digitaalinen toimintaympäristö"
up: "[[8400 Julkisen sektorin digitalisoituminen]]"
related:
  - "[[paper-example]]"
---

[Full content shown here...]
═══════════════════════════════════════════════════════

Actions:
  1. Append new content to 8410 (merge)
  2. Continue with new position (keep separate)
  3. Mark as related (add cross-reference)
  4. View diff comparison

Your choice: _
```

**If user chooses to merge (Append to existing):**

Preview the merge:

```
📝 MERGING CONTENT

Will append to: 8410 Digitaalinen toimintaympäristö

New content will be added as:
─────────────────────────────────────────
## Lisäys: Edistetään julkisen sektorin digitalisaatiota

Source: https://teknologiateollisuus.fi/...

[Draft content here...]
─────────────────────────────────────────

Will also add to 8410's related field:
  - "[[paper-web-digitalisaatio-ja-datatalous]]"

Confirm merge? [yes/no]: _
```

After confirmation:

```
✅ Merged successfully
   Updated: 8410 Digitaalinen toimintaympäristö.md
   Added related link: paper-web-digitalisaatio-ja-datatalous
   Moved draft to: positions-drafts/processed/[original-name].md

Continue to next draft? [yes/stop]: _
```

#### Step F: Execute Migration (Non-merge case)

Preview and confirm migration:

```
✅ MIGRATING POSITION

Creating file: 8490 Edistetään julkisen sektorin digitalisaatiota.md
Location: positions/8000 Digitalisaatio ja datatalous/
                   8400 Julkisen sektorin digitalisoituminen/

Frontmatter will be updated to:
─────────────────────────────────────────
---
type: position
title: "Edistetään julkisen sektorin digitalisaatiota"
up: "[[8400 Julkisen sektorin digitalisoituminen]]"
related:
  - "[[paper-web-digitalisaatio-ja-datatalous]]"
---
─────────────────────────────────────────

Confirm migration? [yes/no/modify]: _
```

After confirmation:

```
✅ Migration complete
   Created: 8490 Edistetään julkisen sektorin digitalisaatiota.md
   Updated frontmatter: up link added
   Moved draft to: positions-drafts/processed/[original-name].md

Progress: 3/15 positions processed

Continue to next draft? [yes/pause/stop]: _
```

### 3. Structural Change Handling

When classification requires new structure:

```
⚠️ STRUCTURAL CHANGE REQUIRED

The suggested classification requires creating new structure:
  New sub-theme: 8900 [Suggested name based on content]
  Under: 8000 Digitalisaatio ja datatalous

This requires approval. Recording suggestion...

📝 Writing to: change-suggestions.md

Change suggestion recorded as:
─────────────────────────────────────────
## Suggestion #1 - [timestamp]

**Type:** New sub-theme creation
**Trigger position:** [Draft title]
**Proposed:** 8900 [Name]
**Parent:** 8000 Digitalisaatio ja datatalous
**Reason:** [AI reasoning]

**Affected positions:**
- Draft: [Title]
- Related existing: [If any]

**Implementation:**
1. Create folder: 8000.../8900 [Name]/
2. Create file: 8900 [Name].md with appropriate frontmatter
3. Migrate draft as: 8910 [Title]

**Status:** PENDING_REVIEW
─────────────────────────────────────────

✅ Suggestion saved to change-suggestions.md

This position will remain in positions-drafts/ until structural
change is approved and implemented via the structure management skill.

Moving to next draft...
```

### 4. Session Summary

After all drafts processed or user stops:

```
═══════════════════════════════════════════════════════
MIGRATION SESSION COMPLETE
═══════════════════════════════════════════════════════

Summary:
  ✅ Migrated: 8 positions
  🔀 Merged: 2 positions (into existing)
  ⏸️  Skipped: 3 positions (left in drafts)
  🔧 Structural changes needed: 2 positions (see change-suggestions.md)
  ❌ Errors: 0

Migrated positions:
  1. 8490 Edistetään julkisen sektorin digitalisaatiota
  2. 3550 Tekoälyn osaaminen koulutuksessa
  ... [list all]

Merged into existing:
  1. Merged into 8410 Digitaalinen toimintaympäristö
  2. Merged into 6140 Ilmastotavoitteet

Still in drafts (skipped):
  1. [filename] - User skipped
  2. [filename] - User skipped
  3. [filename] - Requires structural change (see change-suggestions.md)

Requiring structural changes (pending):
  1. [filename] - Needs new 8900 sub-theme
  2. [filename] - Needs new 10000 theme

📄 Detailed log saved to: migration-log-[timestamp].md
📋 Change suggestions saved to: change-suggestions.md

Next steps:
  1. Review change-suggestions.md
  2. Use structure management skill to implement approved changes
  3. Re-run migration for positions requiring structural changes
  4. Review positions-drafts/processed/ folder

═══════════════════════════════════════════════════════
```

## Edge Cases

### Multiple Similar Positions

When multiple similar positions are found:

```
Found 3 similar positions:
  1. 8410 (85% similar) - Most similar
  2. 8420 (78% similar)
  3. 8450 (72% similar)

Actions:
  1. View all three and choose
  2. Merge into most similar (8410)
  3. Create new position and mark all as related
  4. Skip this draft
```

### Ambiguous Classification

When confidence is low:

```
Confidence is low (< 70%) for all suggestions:
  1. 8400 sub-theme (45%)
  2. 7100 sub-theme (40%)
  3. New structure needed (30%)

Recommendation: Manual classification required

Please specify:
  1. Choose from existing themes [show list]
  2. Describe where this should go (AI will help)
  3. Skip for now
```

### Position Spans Multiple Themes

When position relates to multiple themes:

```
⚠️ This position appears to relate to multiple themes:
  - 60% similarity to 8400 (Digital public sector)
  - 55% similarity to 7100 (Public finance)

Suggestions:
  1. Choose primary theme and add cross-references
  2. Split into separate positions
  3. Create as high-level position with both as parents

Which approach? _
```

## Configuration

### Similarity Thresholds

```yaml
similarity:
  duplicate_threshold: 0.85  # 85%+ likely duplicate
  related_threshold: 0.70    # 70%+ closely related
  mention_threshold: 0.50    # 50%+ somewhat related
```

### Automation Level

```yaml
automation:
  auto_classify_confidence: 0.95  # Only auto-classify if 95%+ confident
  require_merge_confirmation: true  # Always confirm merges
  require_migration_confirmation: true  # Confirm each migration
  batch_mode: false  # Process one-by-one
```

### File Paths

```yaml
paths:
  drafts_folder: "positions-drafts/"
  positions_folder: "positions/"
  processed_folder: "positions-drafts/processed/"
  suggestions_file: "change-suggestions.md"
  log_folder: "migration-logs/"
```

## Output Files

### Migration Log Format

Create detailed log file: `migration-logs/migration-log-[timestamp].md`

```markdown
# Migration Log - [timestamp]

## Session Info
- Start: [timestamp]
- End: [timestamp]
- User: [if available]
- Drafts processed: X/Y

## Migrations

### ✅ 8490 Edistetään julkisen sektorin digitalisaatiota
- **Source draft:** [original filename]
- **Action:** Migrated
- **Location:** positions/8000.../8400.../
- **Similarity check:** No duplicates found (highest: 8410 at 65%)
- **User decision:** Accepted AI suggestion
- **Frontmatter updated:** Added up: [[8400 ...]]

### 🔀 Merged into 8410
- **Source draft:** [original filename]
- **Action:** Merged (appended content)
- **Target:** 8410 Digitaalinen toimintaympäristö
- **Similarity:** 87%
- **Related links added:** [[paper-web-...]]
- **User decision:** Approved merge

[... continue for all positions ...]

## Summary
[Session summary repeated here]
```

### Change Suggestions Format

Create or append to: `change-suggestions.md`

```markdown
# Structural Change Suggestions

## Pending Changes

### Suggestion #1 - [timestamp]
**Status:** 🟡 PENDING_REVIEW
**Type:** New sub-theme creation
**Priority:** Medium

**Trigger Position:**
- Title: [Draft title]
- Content summary: [Brief summary]

**Proposed Structure:**
```
8000 Digitalisaatio ja datatalous/
  └── 8900 [Proposed name]/
      └── 8900 [Proposed name].md
      └── 8910 [Draft title].md
```

**Rationale:**
[AI explanation of why this structure is needed]

**Alternative Considerations:**
1. Could fit under existing 8700? (45% match)
2. Could be merged with 8400 expansion?

**Implementation Steps:**
1. Create folder: `positions/8000.../8900 [Name]/`
2. Create theme file: `8900 [Name].md` with frontmatter
3. Migrate draft as: `8910 [Title].md`
4. Update 8000 parent to include 8900 in children list

**Approval Required By:** [Role/person if known]

---

## Approved Changes
[Implemented changes moved here by structure management skill]

## Rejected Changes
[Rejected suggestions moved here with reason]
```

## Error Handling

### Validation Errors

- Invalid frontmatter → Skip with warning
- Missing title → Skip with warning
- Duplicate number conflict → Suggest next available
- Invalid parent reference → Ask user to clarify

### Recovery

- Save session state after each migration
- Allow resume from last position
- Rollback capability for last N operations
- Backup before any merge operation

## Best Practices

1. **Always show reasoning** - Help user understand why AI suggests specific locations
2. **Provide context** - Show surrounding structure when suggesting placement
3. **Preserve source information** - Keep `source:` field from drafts
4. **Log everything** - Detailed logs help audit and rollback
5. **Safe defaults** - When uncertain, ask rather than assume
6. **Respect user expertise** - They know the domain better than AI
7. **Learn from decisions** - Note user corrections for future suggestions
8. **Clear communication** - Use emojis and formatting to guide user attention

## Success Criteria

A successful migration session means:
- ✅ All processed positions are in correct locations
- ✅ All frontmatter has valid `up:` links
- ✅ No orphaned files
- ✅ Duplicates handled appropriately
- ✅ Structural change needs documented
- ✅ User satisfied with classifications
- ✅ Complete audit trail exists

## Resources

This skill includes a Python script for executing the migration workflow.

### scripts/

**migrate_positions.py** - Main migration script that implements the interactive workflow described above. The script handles:
- Scanning drafts and existing positions
- Semantic similarity analysis using embeddings
- Interactive classification prompts
- Merge and migration operations
- Logging and change suggestion documentation
