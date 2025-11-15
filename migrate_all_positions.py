#!/usr/bin/env python3
"""
Full migration script: Remove numbers from all positions and clean frontmatter

This script:
1. Removes number prefixes from all folders and files
2. Updates all 'up' field references
3. Cleans frontmatter to minimal standard (type, title, up, related only)
4. Removes extra fields like tags, icon, etc.
"""

import re
from pathlib import Path
import shutil
import yaml

# Minimal frontmatter fields allowed
ALLOWED_FIELDS = {'type', 'title', 'up', 'related'}

def remove_number_prefix(name: str) -> str:
    """
    Remove number prefix from folder/file name.

    Examples:
        '8220 Datateollisuus' -> 'Datateollisuus'
        '3000 Osaaminen.md' -> 'Osaaminen.md'
        'Datateollisuus.md' -> 'Datateollisuus.md' (unchanged)
    """
    # Pattern: starts with digits followed by space(s)
    return re.sub(r'^\d+\s+', '', name)

def clean_frontmatter(content: str) -> str:
    """
    Clean frontmatter to keep only allowed fields.
    Removes tags, icon, and any other extra fields.
    """
    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return content

    frontmatter_str = match.group(1)
    body = match.group(2)

    # Parse YAML
    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except:
        # If YAML parsing fails, return original
        return content

    # Filter to allowed fields only
    cleaned = {k: v for k, v in frontmatter.items() if k in ALLOWED_FIELDS}

    # Rebuild frontmatter
    lines = ['---']

    # Always include type first
    if 'type' in cleaned:
        lines.append(f'type: {cleaned["type"]}')

    # Then title
    if 'title' in cleaned:
        title = cleaned['title']
        if isinstance(title, str) and title:
            lines.append(f'title: "{title}"')
        else:
            lines.append(f'title: {title}')

    # Then up
    if 'up' in cleaned:
        up_value = cleaned['up']
        if up_value:  # Only include if not empty
            if isinstance(up_value, str):
                lines.append(f'up: "{up_value}"')
            else:
                lines.append(f'up: {up_value}')
        else:
            lines.append('up:')

    # Then related
    if 'related' in cleaned:
        related = cleaned['related']
        if related:  # Only include if not empty list
            lines.append('related:')
            for item in related:
                lines.append(f'  - "{item}"')

    lines.append('---')

    return '\n'.join(lines) + '\n' + body

def update_wiki_link(content: str, old_name: str, new_name: str) -> str:
    """
    Update wiki link from [[old_name]] to [[new_name]]
    """
    # Escape special regex characters in names
    old_escaped = re.escape(old_name)
    new_escaped = new_name.replace('\\', r'\\')

    # Replace [[old_name]] with [[new_name]]
    pattern = rf'\[\[{old_escaped}\]\]'
    replacement = f'[[{new_escaped}]]'

    return re.sub(pattern, replacement, content)

def build_migration_map(positions_root: Path) -> dict:
    """
    Build a mapping of all folders and files that need renaming.
    Returns: {old_path: new_path}
    """
    import os
    migration_map = {}

    # Walk the directory tree bottom-up (so we process children before parents)
    for dirpath_str, dirnames, filenames in os.walk(str(positions_root), topdown=False):
        dirpath = Path(dirpath_str)
        # Process files
        for filename in filenames:
            if not filename.endswith('.md'):
                continue

            old_file = dirpath / filename
            new_filename = remove_number_prefix(filename)

            if new_filename != filename:
                new_file = dirpath / new_filename
                migration_map[old_file] = new_file

        # Process directories
        for dirname in dirnames:
            old_dir = dirpath / dirname
            new_dirname = remove_number_prefix(dirname)

            if new_dirname != dirname:
                new_dir = dirpath / new_dirname
                migration_map[old_dir] = new_dir

    return migration_map

def extract_wiki_links(content: str) -> list[str]:
    """Extract all wiki links from content"""
    return re.findall(r'\[\[([^\]]+)\]\]', content)

def migrate_all_positions(dry_run=True):
    """
    Main migration function.

    Args:
        dry_run: If True, only print what would happen. If False, execute migration.
    """
    positions_root = Path("positions")

    if not positions_root.exists():
        print(f"❌ Positions folder not found: {positions_root}")
        return False

    print("=" * 70)
    print(f"{'[DRY RUN] ' if dry_run else ''}FULL POSITIONS MIGRATION")
    print("=" * 70)
    print()

    # Step 1: Build migration map
    print("Step 1: Scanning directory structure...")
    migration_map = build_migration_map(positions_root)

    files_to_migrate = {k: v for k, v in migration_map.items() if k.is_file()}
    dirs_to_migrate = {k: v for k, v in migration_map.items() if k.is_dir()}

    print(f"  Found {len(files_to_migrate)} files to rename")
    print(f"  Found {len(dirs_to_migrate)} directories to rename")
    print()

    # Step 2: Create name mapping for wiki link updates
    print("Step 2: Building wiki link mapping...")
    name_mapping = {}
    for old_path, new_path in migration_map.items():
        old_name = old_path.stem if old_path.is_file() else old_path.name
        new_name = new_path.stem if new_path.is_file() else new_path.name
        if old_name != new_name:
            name_mapping[old_name] = new_name

    print(f"  {len(name_mapping)} wiki link patterns to update")
    print()

    # Step 3: Update all file contents
    print("Step 3: Processing files...")
    processed_count = 0

    for md_file in positions_root.rglob("*.md"):
        if not md_file.is_file():
            continue

        content = md_file.read_text(encoding='utf-8')
        original_content = content

        # Clean frontmatter
        content = clean_frontmatter(content)

        # Update all wiki links
        for old_name, new_name in name_mapping.items():
            content = update_wiki_link(content, old_name, new_name)

        if content != original_content:
            if not dry_run:
                md_file.write_text(content, encoding='utf-8')
            processed_count += 1

            if dry_run and processed_count <= 5:
                print(f"  Would update: {md_file.relative_to(positions_root)}")

    if processed_count > 5 and dry_run:
        print(f"  ... and {processed_count - 5} more files")
    print(f"  Total files to update: {processed_count}")
    print()

    # Step 4: Rename files (process all files first, then directories)
    if files_to_migrate:
        print("Step 4: Renaming files...")
        for old_file, new_file in sorted(files_to_migrate.items()):
            if dry_run:
                print(f"  {old_file.name} → {new_file.name}")
            else:
                if old_file.exists():
                    old_file.rename(new_file)
        print(f"  {len(files_to_migrate)} files renamed")
        print()

    # Step 5: Rename directories (bottom-up)
    if dirs_to_migrate:
        print("Step 5: Renaming directories...")
        # Sort by depth (deepest first)
        sorted_dirs = sorted(dirs_to_migrate.items(), key=lambda x: len(x[0].parts), reverse=True)

        for old_dir, new_dir in sorted_dirs:
            if dry_run:
                print(f"  {old_dir.name} → {new_dir.name}")
            else:
                if old_dir.exists():
                    old_dir.rename(new_dir)
        print(f"  {len(dirs_to_migrate)} directories renamed")
        print()

    # Summary
    print("=" * 70)
    print(f"{'[DRY RUN COMPLETE]' if dry_run else '✅ MIGRATION COMPLETE'}")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  Files updated: {processed_count}")
    print(f"  Files renamed: {len(files_to_migrate)}")
    print(f"  Directories renamed: {len(dirs_to_migrate)}")
    print(f"  Wiki links updated: {len(name_mapping)} patterns")
    print()

    if dry_run:
        print("To execute migration, run:")
        print("  python3 migrate_all_positions.py --execute")
    else:
        print("Next steps:")
        print("  1. Review migrated structure in Obsidian")
        print("  2. Test wiki links work correctly")
        print("  3. Commit changes to git")

    return True

if __name__ == "__main__":
    import sys

    # Check for --execute flag
    execute = "--execute" in sys.argv

    if not execute:
        print("=" * 70)
        print("DRY RUN MODE - No files will be changed")
        print("=" * 70)
        print()

    migrate_all_positions(dry_run=not execute)
