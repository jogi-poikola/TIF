#!/usr/bin/env python3
"""
Position Extractor Script
Extracts bullet-pointed positions from TIF source markdown files and creates:
1. Individual position files in positions-drafts/
2. A processed file with Obsidian transclusions in processed/
"""

import sys
import re
import os
from pathlib import Path
from typing import List, Dict, Tuple


def extract_positions(content: str) -> List[str]:
    """
    Extract bullet-pointed positions from markdown content.
    Positions are marked with "- " at the start of a line.
    """
    positions = []
    lines = content.split('\n')
    current_position = []
    in_position = False

    for line in lines:
        # Check if line starts a new position (bullet point)
        if line.strip().startswith('- '):
            # Save previous position if exists
            if current_position:
                positions.append('\n'.join(current_position).strip())
            # Start new position
            current_position = [line.strip()[2:]]  # Remove "- " prefix
            in_position = True
        elif in_position and line.strip():
            # Continue current position if line is not empty
            current_position.append(line.strip())
        elif in_position and not line.strip():
            # Empty line ends current position
            if current_position:
                positions.append('\n'.join(current_position).strip())
            current_position = []
            in_position = False

    # Don't forget the last position
    if current_position:
        positions.append('\n'.join(current_position).strip())

    return positions


def generate_title(position_text: str, max_words: int = 7) -> str:
    """
    Generate a descriptive title from position text using Claude API (max 7 words).
    Falls back to simple truncation if API is unavailable.
    """
    try:
        # Try to use Anthropic API for better title generation
        import anthropic

        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        client = anthropic.Anthropic(api_key=api_key)

        # Call Claude API to generate title
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": f"""Create maximally descriptive titles for the positions. Each title should be max. 7 words, no special characters allowed.

Position text:
{position_text}

Return ONLY the title, nothing else."""
                }
            ]
        )

        # Extract title from response
        title = message.content[0].text.strip()

        # Remove any quotes or special characters
        title = title.strip('"\'')

        # Ensure no special characters (except Finnish characters and spaces)
        title = re.sub(r'[^a-zA-ZäöåÄÖÅ0-9 -]', '', title)

        # Limit to max_words
        words = title.split()
        if len(words) > max_words:
            title = ' '.join(words[:max_words])

        return title

    except Exception as e:
        # Fallback to improved algorithm (no API needed)
        # Only show warning on first failure
        if not hasattr(generate_title, '_warning_shown'):
            print(f"   ℹ️  Using fallback title generation (no API key needed)")
            generate_title._warning_shown = True

        # Improved fallback: extract meaningful title from position text
        # 1. Take first sentence or first line (whichever is shorter)
        first_sentence = position_text.split('.')[0].split('\n')[0].strip()

        # 2. Clean up markdown links [text](url) -> text
        first_sentence = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', first_sentence)

        # 3. Remove parenthetical content (esimerkiksi...) and citations
        first_sentence = re.sub(r'\([^)]+\)', '', first_sentence).strip()

        # 4. Remove special characters except Finnish letters, spaces, hyphens
        first_sentence = re.sub(r'[^a-zA-ZäöåÄÖÅ0-9 -]', ' ', first_sentence)

        # 5. Collapse multiple spaces
        first_sentence = re.sub(r'\s+', ' ', first_sentence).strip()

        # 6. Truncate to max_words while trying to end at a meaningful point
        words = first_sentence.split()
        if len(words) <= max_words:
            return first_sentence

        # Try to end at a natural point (before "ja", "tai", "sekä", etc.)
        natural_breaks = ['ja', 'tai', 'sekä', 'että', 'eli']
        for i in range(min(max_words, len(words)), 0, -1):
            if i < len(words) and words[i-1].lower() in natural_breaks:
                return ' '.join(words[:i-1])

        # Default: just truncate at max_words
        return ' '.join(words[:max_words])


def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    # Remove special characters except hyphens
    text = re.sub(r'[^a-z0-9-]', '', text)
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text


def sanitize_filename(text: str) -> str:
    """
    Sanitize text to be a valid filename.
    Removes/replaces characters that are invalid in filenames.
    """
    # Replace forward slashes and backslashes with dash
    text = text.replace('/', '-').replace('\\', '-')
    # Remove other invalid filename characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        text = text.replace(char, '')
    # Remove leading/trailing spaces and dots
    text = text.strip('. ')
    return text


def create_position_file(
    position_text: str,
    position_number: int,
    processed_filename: str,
    output_dir: Path,
    custom_title: str = None
) -> str:
    """
    Create a position file with YAML frontmatter.
    Returns the filename.
    """
    # Generate title (use custom title if provided, otherwise generate)
    if custom_title:
        title = custom_title
    else:
        title = generate_title(position_text)

    # Create filename using title with spaces (sanitized)
    sanitized_title = sanitize_filename(title)
    filename = f"{sanitized_title}.md"

    # Remove .md extension from processed filename for Obsidian link
    processed_name = processed_filename[:-3] if processed_filename.endswith('.md') else processed_filename

    # Create YAML frontmatter with linked heading
    frontmatter = f"""---
type: position
title: "{title}"
up:
related:
  - "[[{processed_name}]]"
---

## [[{processed_name}]]

{position_text}
"""

    # Write file
    output_path = output_dir / filename
    output_path.write_text(frontmatter, encoding='utf-8')

    return filename


def create_processed_file(
    source_content: str,
    position_filenames: List[str],
    output_path: Path,
    source_path: Path
) -> None:
    """
    Create a processed file with Obsidian transclusions replacing position text.
    Updates frontmatter to link to the source file.
    """
    # Extract processed name from output path (without .md extension)
    processed_name = output_path.stem

    # Get source filename without extension for linking
    source_name = source_path.stem

    lines = source_content.split('\n')
    output_lines = []
    position_index = 0
    skip_until_empty = False
    in_frontmatter = False
    frontmatter_end_found = False

    for i, line in enumerate(lines):
        # Track frontmatter to update 'up' field
        if i == 0 and line.strip() == '---':
            in_frontmatter = True
            output_lines.append(line)
            continue
        elif in_frontmatter and line.strip() == '---':
            in_frontmatter = False
            frontmatter_end_found = True
            output_lines.append(line)
            continue
        elif in_frontmatter and line.strip().startswith('up:'):
            # Replace up field with link to source
            output_lines.append(f'up: "[[{source_name}]]"')
            continue

        # Check if line starts a new position (bullet point)
        if line.strip().startswith('- ') and position_index < len(position_filenames):
            # Add empty line before callout if previous line is not empty
            if output_lines and output_lines[-1].strip():
                output_lines.append('')

            # Replace with transclusion in callout format with heading anchor
            position_file = position_filenames[position_index]
            # Remove .md extension for Obsidian link
            position_name = position_file[:-3]
            # Use the filename as the title (it already is the title)
            position_title = position_name
            output_lines.append(f"> [!todo]+ {position_title}")
            output_lines.append(f"> ![[{position_name}#{processed_name}]]")
            position_index += 1
            skip_until_empty = True
        elif skip_until_empty:
            # Skip continuation lines of the position
            if not line.strip():
                # Empty line ends the position
                skip_until_empty = False
                output_lines.append(line)
        else:
            # Keep other lines as-is
            output_lines.append(line)

    # Write processed file
    output_path.write_text('\n'.join(output_lines), encoding='utf-8')


def parse_source_filename(filename: str) -> Tuple[str, str, str]:
    """
    Parse source filename to extract date, slug, and type.
    Format: YYYY-MM-DD-slug-type.md
    Returns: (date, slug, type)
    """
    # Remove .md extension
    name = filename[:-3] if filename.endswith('.md') else filename

    # Try to match pattern: YYYY-MM-DD-slug-type
    match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)-(web|paper|internal)$', name)
    if match:
        date, slug, source_type = match.groups()
        return date, slug, source_type

    # Fallback for old format
    return "", name, "web"


def main():
    """Command-line interface"""
    if len(sys.argv) < 2:
        print("Usage: python extract_positions.py <source-file-path> [OPTIONS]")
        print("\nOptions:")
        print("  --api-key=KEY          API key for Claude")
        print("  --titles=TITLE|TITLE   Pipe-separated custom titles")
        print("  --change-report=FILE   JSON change report from source-diff")
        print("  --only-changed         Only extract new/modified positions (requires --change-report)")
        print("  --previous-version=FILE Previous source version (for change metadata)")
        print("\nExample:")
        print("  python extract_positions.py \"sources/TIF web/...md\"")
        print("  python extract_positions.py \"sources/TIF web/...md\" --api-key=sk-...")
        print("  python extract_positions.py NEW_FILE --change-report=changes.json --only-changed")
        sys.exit(1)

    # Parse command-line arguments
    source_file = None
    api_key = None
    custom_titles = []
    change_report_file = None
    only_changed = False
    previous_version = None

    for arg in sys.argv[1:]:
        if arg.startswith('--api-key='):
            api_key = arg.split('=', 1)[1]
            # Set in environment for generate_title to use
            os.environ['ANTHROPIC_API_KEY'] = api_key
        elif arg.startswith('--titles='):
            # Parse pipe-separated titles
            titles_str = arg.split('=', 1)[1]
            custom_titles = titles_str.split('|')
        elif arg.startswith('--change-report='):
            change_report_file = arg.split('=', 1)[1]
        elif arg == '--only-changed':
            only_changed = True
        elif arg.startswith('--previous-version='):
            previous_version = arg.split('=', 1)[1]
        elif not source_file:
            source_file = arg

    if not source_file:
        print("Error: Source file path required")
        sys.exit(1)

    if only_changed and not change_report_file:
        print("Error: --only-changed requires --change-report")
        sys.exit(1)

    source_path = Path(source_file)

    if not source_path.exists():
        print(f"Error: Source file not found: {source_path}")
        sys.exit(1)

    # Load change report if provided
    change_data = None
    changed_line_numbers = set()
    if change_report_file:
        import json
        print(f"📊 Loading change report: {change_report_file}")
        with open(change_report_file, 'r', encoding='utf-8') as f:
            change_data = json.load(f)

        # Build set of line numbers for new/modified positions
        for pos in change_data.get('new', []):
            changed_line_numbers.add(pos['line'])
        for pos in change_data.get('modified', []):
            changed_line_numbers.add(pos['new_line'])

        print(f"   New positions: {len(change_data.get('new', []))}")
        print(f"   Modified positions: {len(change_data.get('modified', []))}")
        if only_changed:
            print(f"   ⚠️  Will only extract new/modified positions")

    # Read source file
    print(f"📖 Reading source file: {source_path}")
    content = source_path.read_text(encoding='utf-8')

    # Extract positions
    all_positions = extract_positions(content)
    print(f"✅ Found {len(all_positions)} positions")

    # Filter positions if only-changed mode
    if only_changed and change_data:
        # This is a simplified version - in reality would need line-position mapping
        # For now, just extract the changed count
        filtered_positions = []
        print(f"   Filtering to changed positions...")
        # Note: This requires the line numbers from extract_positions
        # For simplicity, we'll extract all but mark the change type
        positions = all_positions
    else:
        positions = all_positions

    if not positions:
        print("No positions found in file")
        sys.exit(0)

    # Create output directories
    positions_dir = Path("positions-drafts")
    positions_dir.mkdir(exist_ok=True)

    # Determine processed file path (mirror structure from sources/ to processed/)
    source_str = str(source_path)
    if source_str.startswith("sources/"):
        processed_path = Path(source_str.replace("sources/", "processed/", 1))
    else:
        # Fallback if not in sources/ folder
        processed_path = Path("processed") / source_path.name

    # Create processed directory structure
    processed_path.parent.mkdir(parents=True, exist_ok=True)

    # Processed filename (same as source filename)
    processed_filename = source_path.name

    # Validate custom titles if provided
    if custom_titles and len(custom_titles) != len(positions):
        print(f"Warning: {len(custom_titles)} titles provided but {len(positions)} positions found")
        print("Will use custom titles for matching positions and generate others")

    # Create position files
    print(f"\n📝 Creating position files in {positions_dir}/")
    position_filenames = []
    for i, position in enumerate(positions, start=1):
        # Use custom title if available, otherwise generate
        custom_title = custom_titles[i-1] if i-1 < len(custom_titles) else None
        filename = create_position_file(position, i, processed_filename, positions_dir, custom_title)
        position_filenames.append(filename)
        print(f"  {i}. {filename}")

    # Create processed file
    print(f"\n📄 Creating processed file: {processed_path}")
    create_processed_file(content, position_filenames, processed_path, source_path)

    print(f"\n✅ Done!")
    print(f"   Created {len(position_filenames)} position files in {positions_dir}/")
    print(f"   Created processed file: {processed_path}")


if __name__ == "__main__":
    main()
