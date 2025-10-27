#!/usr/bin/env python3
"""
Position Extractor Script
Extracts bullet-pointed positions from TIF source markdown files and creates:
1. Individual position files in positions-drafts/
2. A paper file with Obsidian transclusions in papers/
"""

import sys
import re
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
    Generate a descriptive title from position text (max 7 words).
    Takes the first sentence up to the first period.
    """
    # Get first sentence (up to first period)
    first_sentence = position_text.split('.')[0].strip()

    # Remove markdown links but keep the link text
    first_sentence = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', first_sentence)

    # Split into words and limit to max_words
    words = first_sentence.split()
    if len(words) > max_words:
        title = ' '.join(words[:max_words])
    else:
        title = first_sentence

    return title


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


def create_position_file(
    position_text: str,
    position_number: int,
    source_url: str,
    paper_filename: str,
    output_dir: Path
) -> str:
    """
    Create a position file with YAML frontmatter.
    Returns the filename.
    """
    # Generate title
    title = generate_title(position_text)

    # Create filename using title with spaces
    filename = f"{title}.md"

    # Remove .md extension from paper filename for Obsidian link
    paper_name = paper_filename[:-3] if paper_filename.endswith('.md') else paper_filename

    # Create YAML frontmatter with linked heading
    frontmatter = f"""---
type: position
title: "{title}"
source: "{source_url}"
up:
related:
  - "[[{paper_name}]]"
---

## [[{paper_name}]]

{position_text}
"""

    # Write file
    output_path = output_dir / filename
    output_path.write_text(frontmatter, encoding='utf-8')

    return filename


def create_paper_file(
    source_content: str,
    position_filenames: List[str],
    output_path: Path
) -> None:
    """
    Create a paper file with Obsidian transclusions replacing position text.
    """
    # Extract paper name from output path (without .md extension)
    paper_name = output_path.stem

    lines = source_content.split('\n')
    output_lines = []
    position_index = 0
    skip_until_empty = False

    for line in lines:
        # Check if line starts a new position (bullet point)
        if line.strip().startswith('- ') and position_index < len(position_filenames):
            # Replace with transclusion in callout format with heading anchor
            position_file = position_filenames[position_index]
            # Remove .md extension for Obsidian link
            position_name = position_file[:-3]
            # Use the filename as the title (it already is the title)
            position_title = position_name
            output_lines.append(f"> [!todo]+ {position_title}")
            output_lines.append(f"> ![[{position_name}#{paper_name}]]")
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

    # Write paper file
    output_path.write_text('\n'.join(output_lines), encoding='utf-8')


def main():
    """Command-line interface"""
    if len(sys.argv) < 2:
        print("Usage: python extract_positions.py <source-file-path>")
        print("\nExample:")
        print("  python extract_positions.py sources/TIF\\ web/tavoitteemme/web-digitalisaatio-ja-datatalous.md")
        sys.exit(1)

    source_path = Path(sys.argv[1])

    if not source_path.exists():
        print(f"Error: Source file not found: {source_path}")
        sys.exit(1)

    # Read source file
    print(f"📖 Reading source file: {source_path}")
    content = source_path.read_text(encoding='utf-8')

    # Extract source URL from frontmatter
    source_url_match = re.search(r'source:\s*"([^"]+)"', content)
    if not source_url_match:
        print("Error: Could not find source URL in frontmatter")
        sys.exit(1)
    source_url = source_url_match.group(1)

    # Extract positions
    positions = extract_positions(content)
    print(f"✅ Found {len(positions)} positions")

    if not positions:
        print("No positions found in file")
        sys.exit(0)

    # Create output directories
    positions_dir = Path("positions-drafts")
    papers_dir = Path("papers")
    positions_dir.mkdir(exist_ok=True)
    papers_dir.mkdir(exist_ok=True)

    # Determine paper filename
    paper_filename = f"paper-{source_path.name}"

    # Create position files
    print(f"\n📝 Creating position files in {positions_dir}/")
    position_filenames = []
    for i, position in enumerate(positions, start=1):
        filename = create_position_file(position, i, source_url, paper_filename, positions_dir)
        position_filenames.append(filename)
        print(f"  {i}. {filename}")

    # Create paper file
    paper_path = papers_dir / paper_filename
    print(f"\n📄 Creating paper file: {paper_path}")
    create_paper_file(content, position_filenames, paper_path)

    print(f"\n✅ Done!")
    print(f"   Created {len(position_filenames)} position files in {positions_dir}/")
    print(f"   Created paper file: {paper_path}")


if __name__ == "__main__":
    main()
