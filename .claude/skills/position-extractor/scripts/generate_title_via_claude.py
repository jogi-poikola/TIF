#!/usr/bin/env python3
"""
Generate position title using Claude Code slash command.
This script is called by extract_positions.py to generate titles.
"""

import sys
import subprocess
import tempfile
from pathlib import Path

def generate_title(position_text: str) -> str:
    """
    Generate a title using Claude Code's generate-position-title slash command.

    Args:
        position_text: The position content

    Returns:
        Generated title (max 7 words)
    """
    try:
        # Create a temporary file with the position text
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(position_text)
            temp_file = f.name

        # Use claude command-line tool to invoke the slash command
        # Note: This assumes 'claude' CLI is available and configured
        result = subprocess.run(
            ['claude', 'code', 'exec', '/generate-position-title', temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Clean up temp file
        Path(temp_file).unlink()

        if result.returncode == 0:
            title = result.stdout.strip()
            # Remove quotes if present
            title = title.strip('"\'')
            return title
        else:
            raise Exception(f"Claude CLI error: {result.stderr}")

    except Exception as e:
        # Fallback to simple algorithm
        print(f"   ⚠️  Could not use Claude slash command ({e})")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_title_via_claude.py <position_text>")
        sys.exit(1)

    position_text = sys.argv[1]
    title = generate_title(position_text)
    print(title)
