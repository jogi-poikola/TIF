# Session Close Command

This command wraps up a Claude Code session by:
1. Verifying all documentation is up-to-date
2. Creating/appending a dated changelog entry
3. Committing and pushing all changes
4. Clearing the context window

## Your Task

Execute the following steps in sequence:

### Step 1: Verify Documentation

Check that key documentation files are consistent and up-to-date:

1. **Read and verify:**
   - `CLAUDE.md` - User guide with current features
   - `ARCHITECTURE.md` - System design documentation
   - `README.md` - Project overview

2. **Check for inconsistencies:**
   - Are all skills documented? (6 skills: tif-web-scraper, source-diff, position-extractor, position-migration, auto-process-source, batch-processor)
   - Are all commands documented? (5 commands: extract-positions, auto-process, batch-process-parallel, re-scrape, generate-position-title)
   - Does CLAUDE.md match current implementation?
   - Does ARCHITECTURE.md describe the semantic naming system (not numbered)?

3. **If issues found:**
   - Report issues to user
   - Ask if they want to fix now or proceed with close

### Step 2: Create Changelog Entry

1. **Analyze the current session:**
   - Review git diff to see what changed
   - Review conversation history to understand what was done
   - Identify key accomplishments and changes

2. **Read existing CHANGELOG.md** (if it exists)

3. **Create/append changelog entry at the TOP:**

```markdown
## YYYY-MM-DD - Session Summary

### Accomplishments
- Bullet point of major accomplishment 1
- Bullet point of major accomplishment 2
- ...

### Changes
- **Documentation:** What docs were updated
- **Skills:** What skills were added/modified
- **Commands:** What commands were created/modified
- **Positions:** How many positions created/updated
- **Automation:** What automation was improved

### Files Modified
- `path/to/file1.md` - Brief description
- `path/to/file2.py` - Brief description
- ...

### Commits
- `commit-hash` - Commit message
- ...

---

[Previous entries below...]
```

**Guidelines:**
- Keep it compact (5-15 lines typically)
- Focus on meaningful changes, not minutiae
- Use bullet points for readability
- Date format: YYYY-MM-DD (ISO 8601)
- New entries at TOP (reverse chronological)

### Step 3: Git Status Check

Run `git status` to see what files have changed.

**Expected files:**
- Documentation files (CLAUDE.md, ARCHITECTURE.md, CHANGELOG.md, etc.)
- Position files (if any created/updated)
- Source files (if any scraped)
- Skill files (if any modified)
- Command files (if any created/modified)

### Step 4: Git Commit and Push

1. **Stage all changes:**
   ```bash
   git add -A
   ```

2. **Create commit with descriptive message:**
   ```bash
   git commit -m "$(cat <<'EOF'
   Session close: [Brief summary of session]

   [2-3 bullet points of key changes]

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
   ```

3. **Push to remote:**
   ```bash
   git push
   ```

4. **Verify push succeeded:**
   ```bash
   git status
   ```

### Step 5: Report to User

Provide a final summary:

```
✅ Session closed successfully!

📝 Documentation verified and up-to-date
📋 Changelog updated (YYYY-MM-DD entry)
💾 All changes committed: <commit-hash>
🚀 Pushed to remote: origin/main
🧹 Ready to clear context

Summary of session:
- [Key accomplishment 1]
- [Key accomplishment 2]
- [Key accomplishment 3]

Files changed: N files
Positions created/updated: N positions
Git commits: N commits

Context window can now be safely cleared.
```

### Step 6: Clear Context (User Action)

**NOTE:** You (Claude Code) CANNOT clear the context window directly. Inform the user:

```
To clear the context window and start fresh:
1. Type /clear in the chat
2. Or start a new conversation
```

## Error Handling

**If documentation issues found:**
- Report specific issues
- Ask user if they want to fix before closing
- If "proceed anyway", note issues in changelog

**If git push fails:**
- Report error to user
- Provide troubleshooting steps
- Do NOT proceed with context clear until resolved

**If uncommitted changes:**
- Stage and commit everything
- Never leave repository in dirty state

## Notes

- This command should be run at the end of each significant work session
- It creates an audit trail of what was accomplished
- It ensures all work is saved and pushed to remote
- It prepares for a clean start in next session

## Example Usage

```
User: /session-close

Claude: Executing session close procedure...

[Step 1] Verifying documentation...
✓ CLAUDE.md up-to-date
✓ ARCHITECTURE.md up-to-date
✓ README.md up-to-date
✓ All 6 skills documented
✓ All 5 commands documented

[Step 2] Creating changelog entry...
✓ CHANGELOG.md updated with 2025-11-12 entry

[Step 3] Checking git status...
Found 3 modified files:
- CLAUDE.md
- ARCHITECTURE.md
- CHANGELOG.md

[Step 4] Committing and pushing...
✓ Changes staged
✓ Commit created: a1b2c3d
✓ Pushed to origin/main

✅ Session closed successfully!
...
```
