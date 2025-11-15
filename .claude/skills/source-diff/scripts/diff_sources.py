#!/usr/bin/env python3
"""
Source Diff Script

Compares two versions of a source markdown file and detects changes
at the bullet-point level (position statements).

Usage:
    python diff_sources.py OLD_FILE NEW_FILE [--output REPORT_FILE] [--format {markdown,json}]

Output: Change report with new/modified/removed/unchanged positions
"""

import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from difflib import SequenceMatcher


class SourceDiffer:
    """Compare two versions of a source file and detect changes"""

    # Similarity thresholds
    UNCHANGED_THRESHOLD = 0.90  # ≥90% = unchanged
    MODIFIED_THRESHOLD = 0.70   # 70-89% = modified
    # <70% = new/removed

    def extract_positions(self, file_path: Path) -> List[Dict]:
        """
        Extract bullet-pointed positions from markdown file.

        Returns:
            List of dicts with 'line', 'text', and 'hash' keys
        """
        content = file_path.read_text(encoding='utf-8')
        positions = []

        # Skip frontmatter
        content_without_frontmatter = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

        lines = content_without_frontmatter.split('\n')
        for i, line in enumerate(lines, start=1):
            # Match bullet points (- or *)
            match = re.match(r'^[\s]*[-*]\s+(.+)$', line)
            if match:
                text = match.group(1).strip()
                if text:  # Skip empty bullets
                    positions.append({
                        'line': i,
                        'text': text,
                        'normalized': self._normalize_text(text)
                    })

        return positions

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison (lowercase, remove extra whitespace)"""
        text = text.lower()
        text = ' '.join(text.split())  # Remove extra whitespace
        return text

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (0.0-1.0) using SequenceMatcher"""
        return SequenceMatcher(None, text1, text2).ratio()

    def _find_best_match(self, position: Dict, candidates: List[Dict], used_indices: set) -> Tuple[Dict, float]:
        """
        Find best matching position from candidates.

        Returns:
            (best_match, similarity) or (None, 0.0) if no good match
        """
        best_match = None
        best_similarity = 0.0

        for i, candidate in enumerate(candidates):
            if i in used_indices:
                continue

            similarity = self._calculate_similarity(
                position['normalized'],
                candidate['normalized']
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = (i, candidate)

        if best_match and best_similarity >= self.MODIFIED_THRESHOLD:
            return best_match, best_similarity
        return (None, None), 0.0

    def compare_versions(self, old_file: Path, new_file: Path) -> Dict:
        """
        Compare two source versions and classify changes.

        Returns:
            Dict with 'new', 'modified', 'removed', 'unchanged' lists
        """
        old_positions = self.extract_positions(old_file)
        new_positions = self.extract_positions(new_file)

        changes = {
            'new': [],
            'modified': [],
            'removed': [],
            'unchanged': [],
            'metadata': {
                'old_file': str(old_file),
                'new_file': str(new_file),
                'compared_date': datetime.now().strftime("%Y-%m-%d"),
                'old_count': len(old_positions),
                'new_count': len(new_positions)
            }
        }

        # Track which new positions have been matched
        matched_new_indices = set()

        # Process old positions - find matches in new positions
        for old_pos in old_positions:
            (match_idx, new_pos), similarity = self._find_best_match(
                old_pos, new_positions, matched_new_indices
            )

            if new_pos:
                matched_new_indices.add(match_idx)

                if similarity >= self.UNCHANGED_THRESHOLD:
                    # Unchanged
                    changes['unchanged'].append({
                        'line': new_pos['line'],
                        'text': new_pos['text'],
                        'similarity': similarity
                    })
                else:
                    # Modified (70-89% similarity)
                    changes['modified'].append({
                        'old_line': old_pos['line'],
                        'new_line': new_pos['line'],
                        'old_text': old_pos['text'],
                        'new_text': new_pos['text'],
                        'similarity': similarity
                    })
            else:
                # Removed (no match found in new)
                changes['removed'].append({
                    'line': old_pos['line'],
                    'text': old_pos['text']
                })

        # Process unmatched new positions - these are NEW
        for i, new_pos in enumerate(new_positions):
            if i not in matched_new_indices:
                changes['new'].append({
                    'line': new_pos['line'],
                    'text': new_pos['text']
                })

        return changes

    def generate_markdown_report(self, changes: Dict, output_file: Path = None) -> str:
        """
        Generate markdown change report.

        Args:
            changes: Result from compare_versions()
            output_file: Optional path to write report to

        Returns:
            Markdown report as string
        """
        metadata = changes['metadata']

        lines = [
            "# Source Change Report",
            "",
            f"**Old Version:** {Path(metadata['old_file']).name}",
            f"**New Version:** {Path(metadata['new_file']).name}",
            f"**Compared:** {metadata['compared_date']}",
            "",
            "## Summary",
            f"- ✨ New positions: {len(changes['new'])}",
            f"- ✏️  Modified positions: {len(changes['modified'])}",
            f"- ❌ Removed positions: {len(changes['removed'])}",
            f"- ✓ Unchanged positions: {len(changes['unchanged'])}",
            "",
        ]

        # New positions
        if changes['new']:
            lines.append("## New Positions")
            lines.append("")
            for i, pos in enumerate(changes['new'], start=1):
                text_preview = pos['text'][:100] + "..." if len(pos['text']) > 100 else pos['text']
                lines.append(f"{i}. **[Line {pos['line']}]** {text_preview}")
            lines.append("")

        # Modified positions
        if changes['modified']:
            lines.append("## Modified Positions")
            lines.append("")
            for i, pos in enumerate(changes['modified'], start=1):
                lines.append(f"{i}. **[Line {pos['old_line']} → {pos['new_line']}]**")
                old_preview = pos['old_text'][:80] + "..." if len(pos['old_text']) > 80 else pos['old_text']
                new_preview = pos['new_text'][:80] + "..." if len(pos['new_text']) > 80 else pos['new_text']
                lines.append(f"   - **Before:** {old_preview}")
                lines.append(f"   - **After:** {new_preview}")
                lines.append(f"   - **Similarity:** {pos['similarity']:.0%}")
                lines.append("")

        # Removed positions
        if changes['removed']:
            lines.append("## Removed Positions")
            lines.append("")
            for i, pos in enumerate(changes['removed'], start=1):
                text_preview = pos['text'][:100] + "..." if len(pos['text']) > 100 else pos['text']
                lines.append(f"{i}. **[Line {pos['line']}]** {text_preview}")
            lines.append("")

        # Unchanged positions (summary only, not full list)
        if changes['unchanged']:
            lines.append("## Unchanged Positions")
            lines.append("")
            lines.append(f"Total unchanged: {len(changes['unchanged'])} positions")
            lines.append("")

        report = '\n'.join(lines)

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(report, encoding='utf-8')
            print(f"✅ Change report written to: {output_file}")

        return report

    def generate_json_report(self, changes: Dict, output_file: Path = None) -> str:
        """
        Generate JSON change report.

        Args:
            changes: Result from compare_versions()
            output_file: Optional path to write JSON to

        Returns:
            JSON report as string
        """
        # Add summary to metadata
        changes['metadata']['summary'] = {
            'new': len(changes['new']),
            'modified': len(changes['modified']),
            'removed': len(changes['removed']),
            'unchanged': len(changes['unchanged'])
        }

        json_output = json.dumps(changes, indent=2, ensure_ascii=False)

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(json_output, encoding='utf-8')
            print(f"✅ JSON report written to: {output_file}")

        return json_output


def main():
    """Command-line interface"""
    if len(sys.argv) < 3:
        print("Usage: python diff_sources.py OLD_FILE NEW_FILE [--output REPORT_FILE] [--format {markdown,json}]")
        print("\nExample:")
        print("  python diff_sources.py sources/TIF\\ web/2025-11-04-datakeskukset-web.md \\")
        print("                         sources/TIF\\ web/2025-12-15-datakeskukset-web.md")
        print("\n  python diff_sources.py OLD_FILE NEW_FILE --format json --output changes.json")
        sys.exit(1)

    old_file = Path(sys.argv[1])
    new_file = Path(sys.argv[2])

    # Parse optional arguments
    output_file = None
    output_format = 'markdown'

    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_file = Path(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--format' and i + 1 < len(sys.argv):
            output_format = sys.argv[i + 1]
            if output_format not in ['markdown', 'json']:
                print(f"Error: Invalid format '{output_format}'. Use 'markdown' or 'json'")
                sys.exit(1)
            i += 2
        else:
            i += 1

    # Validate files exist
    if not old_file.exists():
        print(f"Error: Old file not found: {old_file}")
        sys.exit(1)
    if not new_file.exists():
        print(f"Error: New file not found: {new_file}")
        sys.exit(1)

    # Run comparison
    print(f"📊 Comparing versions...")
    print(f"   Old: {old_file.name}")
    print(f"   New: {new_file.name}")
    print()

    differ = SourceDiffer()
    changes = differ.compare_versions(old_file, new_file)

    # Print summary
    print("Summary:")
    print(f"  ✨ New positions:       {len(changes['new'])}")
    print(f"  ✏️  Modified positions:  {len(changes['modified'])}")
    print(f"  ❌ Removed positions:   {len(changes['removed'])}")
    print(f"  ✓ Unchanged positions: {len(changes['unchanged'])}")
    print()

    # Generate report
    if output_format == 'json':
        report = differ.generate_json_report(changes, output_file)
        if not output_file:
            print(report)
    else:
        report = differ.generate_markdown_report(changes, output_file)
        if not output_file:
            print(report)


if __name__ == "__main__":
    main()
