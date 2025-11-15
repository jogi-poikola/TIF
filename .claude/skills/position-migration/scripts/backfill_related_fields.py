#!/usr/bin/env python3
"""
Backfill Related Fields Script

Retroactively adds `related:` fields to position files that are missing them.
Extracts source links from section headings like `## [[source-file]]` and adds
them to the frontmatter.

Usage:
    python backfill_related_fields.py [--dry-run]

Options:
    --dry-run    Preview changes without modifying files
"""

import sys
import re
from pathlib import Path
from typing import List, Set


def parse_frontmatter_and_content(content: str) -> tuple:
    """Parse YAML frontmatter and extract body"""
    match = re.search(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return {}, "", content

    frontmatter_text = match.group(1)
    body = match.group(2)

    # Parse frontmatter
    frontmatter = {}
    lines = frontmatter_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if ':' in line and not line.strip().startswith('-'):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"')

            # Check if next lines are list items
            if not value and i + 1 < len(lines) and lines[i + 1].strip().startswith('-'):
                # Parse list items
                list_items = []
                i += 1
                while i < len(lines) and lines[i].strip().startswith('-'):
                    item = lines[i].strip().lstrip('- ').strip('"').strip("'")
                    list_items.append(item)
                    i += 1
                frontmatter[key] = list_items
                continue
            else:
                frontmatter[key] = value
        i += 1

    return frontmatter, frontmatter_text, body


def extract_source_links(body: str) -> List[str]:
    """Extract source file links from section headings like ## [[source-file]]"""
    # Find all ## [[...]] patterns
    pattern = r'##\s+\[\[([^\]]+)\]\]'
    matches = re.findall(pattern, body)
    return list(set(matches))  # Remove duplicates


def build_frontmatter(frontmatter: dict, source_links: List[str]) -> str:
    """Build YAML frontmatter with related field"""
    lines = ["---"]

    # Always include: type, title, up
    for key in ['type', 'title', 'up']:
        if key in frontmatter:
            value = frontmatter[key]
            if value:
                lines.append(f'{key}: "{value}"')
            else:
                lines.append(f'{key}:')

    # Add related field if we have source links
    if source_links:
        lines.append('related:')
        for link in sorted(source_links):
            # Keep wiki-link format if already present
            if link.startswith('[[') and link.endswith(']]'):
                lines.append(f'  - "{link}"')
            else:
                lines.append(f'  - "[[{link}]]"')

    # Add any other fields (preserve order, skip the ones we already added)
    for key, value in frontmatter.items():
        if key not in ['type', 'title', 'up', 'related']:
            if isinstance(value, list):
                lines.append(f'{key}:')
                for item in value:
                    lines.append(f'  - "{item}"')
            elif value:
                lines.append(f'{key}: "{value}"')
            else:
                lines.append(f'{key}:')

    lines.append('---')
    return '\n'.join(lines)


def process_file(file_path: Path, dry_run: bool = False) -> bool:
    """Process a single position file. Returns True if changes were made."""
    try:
        content = file_path.read_text(encoding='utf-8')

        # Parse frontmatter and body
        frontmatter, frontmatter_text, body = parse_frontmatter_and_content(content)

        # Check if it's a position file
        if frontmatter.get('type') != 'position':
            return False

        # Check if related field already exists and has items
        existing_related = frontmatter.get('related', [])
        if isinstance(existing_related, str):
            existing_related = [existing_related] if existing_related else []

        # Extract source links from body
        source_links = extract_source_links(body)

        if not source_links:
            # No source links found in body
            return False

        # Check if all source links are already in related field
        existing_set = set(existing_related)
        source_set = set(source_links)

        # Normalize for comparison (remove [[ ]] if present)
        existing_normalized = set()
        for item in existing_set:
            normalized = item.strip('[]')
            existing_normalized.add(normalized)

        source_normalized = set()
        for item in source_set:
            normalized = item.strip('[]')
            source_normalized.add(normalized)

        if source_normalized.issubset(existing_normalized):
            # All source links already in related field
            return False

        # Merge existing and new source links
        all_links = list(existing_normalized | source_normalized)

        # Build new frontmatter
        new_frontmatter_text = build_frontmatter(frontmatter, all_links)

        # Build new content
        new_content = new_frontmatter_text + '\n\n' + body.strip() + '\n'

        if dry_run:
            print(f"  Would update: {file_path.relative_to(Path('positions'))}")
            print(f"    Current related: {existing_related}")
            print(f"    New related: {all_links}")
            return True
        else:
            # Write updated content
            file_path.write_text(new_content, encoding='utf-8')
            print(f"  ✓ Updated: {file_path.relative_to(Path('positions'))}")
            return True

    except Exception as e:
        print(f"  ⚠️  Error processing {file_path}: {e}")
        return False


def main():
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")

    positions_folder = Path('positions')
    if not positions_folder.exists():
        print("❌ positions/ folder not found")
        return

    print("🔍 Scanning position files...")

    # Find all position files
    position_files = []
    for file in positions_folder.rglob('*.md'):
        if file.is_file() and file.name != '0000 index.md':
            position_files.append(file)

    print(f"   Found {len(position_files)} position files\n")

    # Process each file
    updated_count = 0
    for file in sorted(position_files):
        if process_file(file, dry_run):
            updated_count += 1

    # Summary
    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total files: {len(position_files)}")
    print(f"Files {'that would be ' if dry_run else ''}updated: {updated_count}")
    print(f"Files unchanged: {len(position_files) - updated_count}")

    if dry_run:
        print(f"\n💡 Run without --dry-run to apply changes")

    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
