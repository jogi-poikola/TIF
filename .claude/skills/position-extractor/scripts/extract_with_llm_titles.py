#!/usr/bin/env python3
"""
Wrapper script for extract_positions.py that provides API key from environment.
This script should be called by Claude Code which has access to ANTHROPIC_API_KEY.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_with_llm_titles.py <source-file-path>")
        sys.exit(1)

    source_file = sys.argv[1]

    # Get API key from environment (should be set by Claude Code)
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("Warning: ANTHROPIC_API_KEY not found, will use fallback title generation")
        # Run without API key
        script_path = Path(__file__).parent / "extract_positions.py"
        subprocess.run([sys.executable, str(script_path), source_file])
    else:
        # Run with API key
        script_path = Path(__file__).parent / "extract_positions.py"
        subprocess.run(
            [sys.executable, str(script_path), source_file, f"--api-key={api_key}"]
        )

if __name__ == "__main__":
    main()
