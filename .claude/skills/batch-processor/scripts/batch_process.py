#!/usr/bin/env python3
"""
Batch processor for TIF sources: Process multiple URLs in parallel.

This script reads URLs from scraped-urls.txt and processes them using
the auto-process-source skill, either sequentially or in parallel.
"""

import argparse
import json
import multiprocessing as mp
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
import re


class BatchProcessor:
    def __init__(self, repo_root: Path, max_workers: int = 4, skip_commits: bool = False):
        self.repo_root = repo_root
        self.max_workers = max_workers
        self.skip_commits = skip_commits
        self.skills_dir = repo_root / ".claude" / "skills"
        self.auto_processor = self.skills_dir / "auto-process-source" / "scripts" / "auto_process_source.py"

    def read_registry(self) -> List[Tuple[str, str, str]]:
        """
        Read scraped-urls.txt and return list of (date, url, file_path) tuples.
        """
        registry_path = self.repo_root / "sources" / "scraped-urls.txt"
        if not registry_path.exists():
            print(f"❌ Registry not found: {registry_path}")
            return []

        entries = []
        with open(registry_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split('|')
                if len(parts) >= 3:
                    date = parts[0].strip()
                    url = parts[1].strip()
                    file_path = parts[2].strip()
                    entries.append((date, url, file_path))

        return entries

    def get_unique_urls(self, entries: List[Tuple[str, str, str]]) -> List[str]:
        """Get unique URLs from registry entries (most recent version of each)."""
        url_map = {}
        for date, url, file_path in entries:
            if url not in url_map:
                url_map[url] = (date, file_path)
            else:
                # Keep the most recent
                if date > url_map[url][0]:
                    url_map[url] = (date, file_path)

        return list(url_map.keys())

    def filter_urls(
        self,
        urls: List[str],
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        specific_urls: Optional[List[str]] = None
    ) -> List[str]:
        """
        Filter URLs based on patterns or specific list.
        """
        if specific_urls:
            return specific_urls

        filtered = urls

        # Include patterns
        if include_patterns:
            filtered = [
                url for url in filtered
                if any(re.search(pattern, url) for pattern in include_patterns)
            ]

        # Exclude patterns
        if exclude_patterns:
            filtered = [
                url for url in filtered
                if not any(re.search(pattern, url) for pattern in exclude_patterns)
            ]

        return filtered

    def process_url(self, url: str) -> Tuple[str, bool, str]:
        """
        Process a single URL using auto-process-source.
        Returns (url, success, message).
        """
        print(f"\n{'=' * 70}")
        print(f"Processing: {url}")
        print(f"{'=' * 70}\n")

        cmd = [
            "python3",
            str(self.auto_processor),
            url,
            "--repo-root", str(self.repo_root)
        ]

        if self.skip_commits:
            cmd.append("--skip-commits")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per URL
            )

            success = result.returncode == 0
            message = result.stdout if success else result.stderr

            return url, success, message

        except subprocess.TimeoutExpired:
            return url, False, "Timeout (5 minutes)"
        except Exception as e:
            return url, False, str(e)

    def process_sequential(self, urls: List[str]) -> List[Tuple[str, bool, str]]:
        """Process URLs sequentially."""
        print(f"\n{'=' * 70}")
        print(f"BATCH PROCESSING (Sequential)")
        print(f"{'=' * 70}")
        print(f"URLs to process: {len(urls)}")
        print(f"Mode: Sequential")
        print()

        results = []
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing URL...")
            result = self.process_url(url)
            results.append(result)

        return results

    def process_parallel(self, urls: List[str]) -> List[Tuple[str, bool, str]]:
        """Process URLs in parallel using multiprocessing."""
        print(f"\n{'=' * 70}")
        print(f"BATCH PROCESSING (Parallel)")
        print(f"{'=' * 70}")
        print(f"URLs to process: {len(urls)}")
        print(f"Max workers: {self.max_workers}")
        print()

        with mp.Pool(processes=self.max_workers) as pool:
            results = pool.map(self.process_url, urls)

        return results

    def print_summary(self, results: List[Tuple[str, bool, str]]):
        """Print summary of batch processing results."""
        print(f"\n{'=' * 70}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'=' * 70}\n")

        successful = [r for r in results if r[1]]
        failed = [r for r in results if not r[1]]

        print(f"Total: {len(results)}")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")

        if successful:
            print(f"\n✅ Successfully processed:")
            for url, _, _ in successful:
                print(f"   - {url}")

        if failed:
            print(f"\n❌ Failed to process:")
            for url, _, message in failed:
                print(f"   - {url}")
                # Show first line of error message
                first_line = message.split('\n')[0] if message else "Unknown error"
                print(f"     Error: {first_line}")

    def process(
        self,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        specific_urls: Optional[List[str]] = None,
        parallel: bool = False
    ) -> bool:
        """
        Run batch processing with filters.
        Returns True if all URLs processed successfully.
        """
        # Read registry
        entries = self.read_registry()
        if not entries:
            print("❌ No URLs found in registry")
            return False

        # Get unique URLs
        all_urls = self.get_unique_urls(entries)
        print(f"📋 Found {len(all_urls)} unique URLs in registry")

        # Filter URLs
        urls = self.filter_urls(all_urls, include_patterns, exclude_patterns, specific_urls)

        if not urls:
            print("❌ No URLs match the filters")
            return False

        print(f"🎯 {len(urls)} URLs selected for processing")

        # Process URLs
        if parallel:
            results = self.process_parallel(urls)
        else:
            results = self.process_sequential(urls)

        # Print summary
        self.print_summary(results)

        # Return success if all processed successfully
        return all(success for _, success, _ in results)


def main():
    parser = argparse.ArgumentParser(
        description="Batch process TIF sources in parallel"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory (default: current directory)"
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        help="Specific URLs to process (space-separated)"
    )
    parser.add_argument(
        "--include",
        nargs="+",
        help="Include only URLs matching these regex patterns (space-separated)"
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        help="Exclude URLs matching these regex patterns (space-separated)"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Process URLs in parallel (default: sequential)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of parallel workers (default: 4)"
    )
    parser.add_argument(
        "--skip-commits",
        action="store_true",
        help="Skip git commits (for testing)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all URLs in registry (re-scrape everything)"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.all and not args.urls and not args.include:
        print("❌ Must specify --all, --urls, or --include patterns")
        parser.print_help()
        sys.exit(1)

    # Create processor
    processor = BatchProcessor(
        args.repo_root,
        args.max_workers,
        args.skip_commits
    )

    # Process
    success = processor.process(
        include_patterns=args.include,
        exclude_patterns=args.exclude,
        specific_urls=args.urls,
        parallel=args.parallel
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
