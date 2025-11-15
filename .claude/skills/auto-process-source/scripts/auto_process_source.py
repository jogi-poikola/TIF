#!/usr/bin/env python3
"""
Auto-process TIF source: Scrape, extract, and migrate positions automatically.

This script orchestrates the entire workflow:
1. Scrape (or re-scrape) TIF website URL
2. Detect changes if re-scraping
3. Extract positions (only changed if re-scrape)
4. Migrate positions in auto mode
5. Git commit at meaningful moments
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple, List
import re


class AutoProcessor:
    def __init__(self, url: str, repo_root: Path, skip_commits: bool = False):
        self.url = url
        self.repo_root = repo_root
        self.skip_commits = skip_commits
        self.skills_dir = repo_root / ".claude" / "skills"

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
        """Run a command and return (exit_code, stdout, stderr)."""
        result = subprocess.run(
            cmd,
            cwd=cwd or self.repo_root,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr

    def git_commit(self, message: str):
        """Create a git commit if not skipping commits."""
        if self.skip_commits:
            print(f"⏭️  Skipping commit: {message}")
            return

        print(f"📝 Committing: {message}")
        # Add all changes
        self.run_command(["git", "add", "."])

        # Create commit with full message
        full_message = f"{message}\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
        self.run_command(["git", "commit", "-m", full_message])

    def scrape_url(self) -> Tuple[Optional[Path], bool]:
        """
        Scrape the URL and return (source_file_path, is_rescrape).
        Returns None, False if scraping failed.
        """
        print(f"\n🔄 Scraping: {self.url}")

        scraper_script = self.skills_dir / "tif-web-scraper" / "scripts" / "scrape_tif_web.py"
        exit_code, stdout, stderr = self.run_command([
            "python3",
            str(scraper_script),
            self.url
        ])

        if exit_code != 0:
            print(f"❌ Scraping failed: {stderr}")
            return None, False

        print(stdout)

        # Parse output to find source file path and check if re-scrape
        is_rescrape = "Previous scrapes found:" in stdout

        # Extract source file path from output
        match = re.search(r"Created source at: (.+\.md)", stdout)
        if not match:
            match = re.search(r"Done! Source created at: (.+\.md)", stdout)

        if not match:
            print("❌ Could not determine source file path")
            return None, False

        source_path = Path(match.group(1).strip())
        return source_path, is_rescrape

    def find_previous_version(self, current_source: Path) -> Optional[Path]:
        """Find the previous version of this source file."""
        # Look in scraped-urls.txt for previous versions
        registry_path = self.repo_root / "sources" / "scraped-urls.txt"
        if not registry_path.exists():
            return None

        previous_files = []
        with open(registry_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('|')
                if len(parts) >= 3:
                    url = parts[1].strip()
                    file_path = parts[2].strip()
                    if url == self.url and file_path != str(current_source):
                        previous_files.append(Path(file_path))

        # Return the most recent previous file
        return previous_files[-1] if previous_files else None

    def run_diff(self, old_source: Path, new_source: Path) -> Tuple[Optional[Path], dict]:
        """
        Run diff between old and new source files.
        Returns (change_report_json_path, change_summary).
        """
        print(f"\n📊 Comparing versions...")
        print(f"   Old: {old_source.name}")
        print(f"   New: {new_source.name}")

        diff_script = self.skills_dir / "source-diff" / "scripts" / "diff_sources.py"

        # Run diff with JSON output
        exit_code, stdout, stderr = self.run_command([
            "python3",
            str(diff_script),
            str(old_source),
            str(new_source),
            "--format", "json"
        ])

        if exit_code != 0:
            print(f"❌ Diff failed: {stderr}")
            return None, {}

        # Parse JSON output to find the change report path
        try:
            # The script outputs the path to the JSON file
            lines = stdout.strip().split('\n')
            json_path = None
            for line in lines:
                if line.endswith('.json'):
                    json_path = Path(line.strip())
                    break

            if not json_path or not json_path.exists():
                print("❌ Could not find change report JSON")
                return None, {}

            # Load the change report
            with open(json_path, 'r') as f:
                change_data = json.load(f)

            # Print summary
            stats = change_data.get('summary', {})
            print(f"\nSummary:")
            print(f"  ✨ New positions:       {stats.get('new', 0)}")
            print(f"  ✏️  Modified positions:  {stats.get('modified', 0)}")
            print(f"  ❌ Removed positions:   {stats.get('removed', 0)}")
            print(f"  ✓ Unchanged positions: {stats.get('unchanged', 0)}")

            return json_path, stats

        except Exception as e:
            print(f"❌ Failed to parse change report: {e}")
            return None, {}

    def extract_positions(self, source_file: Path, change_report: Optional[Path] = None) -> List[Path]:
        """
        Extract positions from source file.
        If change_report provided, only extract changed positions.
        Returns list of created position files.
        """
        print(f"\n📝 Extracting positions...")

        extractor_script = self.skills_dir / "position-extractor" / "scripts" / "extract_positions.py"

        cmd = [
            "python3",
            str(extractor_script),
            str(source_file)
        ]

        if change_report:
            cmd.extend([
                "--change-report", str(change_report),
                "--only-changed"
            ])
            print("   (Only extracting new/modified positions)")

        exit_code, stdout, stderr = self.run_command(cmd)

        if exit_code != 0:
            print(f"❌ Extraction failed: {stderr}")
            return []

        print(stdout)

        # Parse output to find created position files
        position_files = []
        for line in stdout.split('\n'):
            if 'Created position file:' in line:
                match = re.search(r'Created position file: (.+\.md)', line)
                if match:
                    position_files.append(Path(match.group(1).strip()))

        return position_files

    def migrate_positions(self) -> bool:
        """
        Migrate positions from positions-drafts/ using auto mode.
        Returns True if successful.
        """
        # Check if there are any drafts to migrate
        drafts_dir = self.repo_root / "positions-drafts"
        if not drafts_dir.exists():
            print("\n✓ No draft positions to migrate")
            return True

        draft_files = list(drafts_dir.glob("*.md"))
        if not draft_files:
            print("\n✓ No draft positions to migrate")
            return True

        print(f"\n🚀 Migrating {len(draft_files)} positions in auto mode...")

        migration_script = self.skills_dir / "position-migration" / "scripts" / "migrate_positions.py"

        exit_code, stdout, stderr = self.run_command([
            "python3",
            str(migration_script),
            "--auto"
        ])

        if exit_code != 0:
            print(f"❌ Migration failed: {stderr}")
            return False

        print(stdout)
        return True

    def process(self) -> bool:
        """
        Run the full auto-processing workflow.
        Returns True if successful.
        """
        print("=" * 70)
        print("AUTO-PROCESSING TIF SOURCE")
        print("=" * 70)
        print(f"URL: {self.url}")
        print(f"Repo: {self.repo_root}")
        print()

        # Step 1: Scrape
        source_file, is_rescrape = self.scrape_url()
        if not source_file:
            return False

        # Commit after scraping
        if is_rescrape:
            self.git_commit(f"Re-scrape TIF source: {self.url}")
        else:
            self.git_commit(f"Add TIF source: {self.url}")

        # Step 2: Run diff if re-scrape
        change_report = None
        change_stats = {}
        if is_rescrape:
            prev_source = self.find_previous_version(source_file)
            if prev_source and prev_source.exists():
                change_report, change_stats = self.run_diff(prev_source, source_file)

                # Check if there are any changes worth extracting
                total_changes = change_stats.get('new', 0) + change_stats.get('modified', 0)
                if total_changes == 0:
                    print("\n✅ No changes detected - extraction not needed")
                    print("=" * 70)
                    return True
            else:
                print("⚠️  Could not find previous version for comparison")

        # Step 3: Extract positions
        position_files = self.extract_positions(source_file, change_report)

        # Check if there are any drafts created (position_files list might not be populated correctly)
        drafts_dir = self.repo_root / "positions-drafts"
        draft_count = len(list(drafts_dir.glob("*.md"))) if drafts_dir.exists() else 0

        if draft_count == 0:
            print("⚠️  No positions extracted")
            # Still continue - this might be intentional
        else:
            # Commit after extraction
            self.git_commit(f"Extract positions from: {source_file.name}")

        # Step 4: Migrate positions
        if not self.migrate_positions():
            return False

        # Commit after migration
        self.git_commit(f"Migrate positions from: {source_file.name}")

        print("\n✅ Auto-processing complete!")
        print("=" * 70)
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Auto-process TIF source: scrape, extract, and migrate positions"
    )
    parser.add_argument(
        "url",
        help="TIF website URL to process"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory (default: current directory)"
    )
    parser.add_argument(
        "--skip-commits",
        action="store_true",
        help="Skip git commits (for testing)"
    )

    args = parser.parse_args()

    # Validate URL
    if not args.url.startswith("https://teknologiateollisuus.fi/"):
        print(f"❌ Invalid URL: {args.url}")
        print("   URL must start with https://teknologiateollisuus.fi/")
        sys.exit(1)

    # Create processor and run
    processor = AutoProcessor(args.url, args.repo_root, args.skip_commits)
    success = processor.process()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
