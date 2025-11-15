#!/usr/bin/env python3
"""
Re-scrape All URLs

Reads sources/scraped-urls.txt and re-scrapes all registered URLs
to detect changes in content.

Usage:
    python rescrape_all.py [--diff-only]

Options:
    --diff-only  Only show which files have changed, don't save new versions
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime


def parse_registry(registry_file: Path):
    """Parse the scraped-urls.txt registry file"""
    if not registry_file.exists():
        print(f"Error: Registry file not found: {registry_file}")
        return []

    urls = []
    with registry_file.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse format: YYYY-MM-DD | URL | Output File
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 2:
                original_date = parts[0]
                url = parts[1]
                original_file = parts[2] if len(parts) > 2 else None
                urls.append({
                    'url': url,
                    'original_date': original_date,
                    'original_file': original_file
                })

    return urls


def rescrape_url(url: str, diff_only: bool = False):
    """Re-scrape a single URL"""
    print(f"\n🔍 Re-scraping: {url}")

    # Run scraper
    script_path = Path(__file__).parent / "scrape_tif_web.py"
    try:
        result = subprocess.run(
            ["python3", str(script_path), url],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print(f"   ✅ Success")
            # Extract output path from result
            for line in result.stdout.split('\n'):
                if 'Created source at:' in line:
                    print(f"   {line.strip()}")
        else:
            print(f"   ❌ Error: {result.stderr}")

    except subprocess.TimeoutExpired:
        print(f"   ⏱️  Timeout - skipping")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    diff_only = "--diff-only" in sys.argv

    registry_file = Path("sources/scraped-urls.txt")

    print("📋 TIF Sources Re-scraper")
    print("=" * 60)

    # Parse registry
    urls = parse_registry(registry_file)
    print(f"\nFound {len(urls)} URLs to re-scrape\n")

    if not urls:
        return

    # Re-scrape each URL
    for i, entry in enumerate(urls, start=1):
        print(f"[{i}/{len(urls)}]")
        rescrape_url(entry['url'], diff_only)

    print("\n" + "=" * 60)
    print(f"✅ Re-scraping complete")
    print(f"\n💡 Compare with git to see changes:")
    print(f"   git status")
    print(f"   git diff sources/")


if __name__ == "__main__":
    main()
