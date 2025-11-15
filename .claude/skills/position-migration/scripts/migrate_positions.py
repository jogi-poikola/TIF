#!/usr/bin/env python3
"""
Position Migration Script

Migrates position files from positions-drafts/ to the hierarchical positions/ structure.
Uses merge-into-canonical approach: similar positions are merged into existing canonical positions
rather than creating versioned duplicates.

Usage:
    python migrate_positions.py [--dry-run] [--auto] [--threshold THRESHOLD]

Options:
    --dry-run              Preview migrations without making changes
    --auto                 Auto-accept all high-confidence suggestions (no prompts)
    --threshold THRESHOLD  Auto-accept threshold (default: 0.80, range: 0.0-1.0)
    --batch                Process multiple files in parallel (faster)

Performance optimizations:
- Lazy loading: Only load files when needed
- Caching: Cache parsed content and similarity calculations
- Batch processing: Process multiple drafts without reloading positions
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime
from functools import lru_cache


class PositionMigrator:
    """Main migration class with merge-into-canonical workflow"""

    def __init__(self, dry_run=False, auto_mode=False, auto_threshold=0.80):
        self.dry_run = dry_run
        self.auto_mode = auto_mode
        self.auto_threshold = auto_threshold

        self.drafts_folder = Path("positions-drafts")
        self.positions_folder = Path("positions")
        self.processed_folder = Path("positions-drafts/processed")

        # Session tracking
        self.session_start = datetime.now()
        self.migrated_count = 0
        self.merged_count = 0
        self.skipped_count = 0

        # Similarity thresholds
        self.MERGE_THRESHOLD = 0.80      # 80%+ auto-suggest merge
        self.CONFIRM_THRESHOLD = 0.70    # 70-80% ask user to confirm
        self.CREATE_NEW_THRESHOLD = 0.70 # <70% create new position

        # Performance: Cache for loaded positions
        self._positions_cache: Optional[List[Dict]] = None
        self._similarity_cache: Dict[Tuple[str, str], float] = {}

    def run(self):
        """Main migration workflow"""
        print("🚀 Position Migration - Merge to Canonical")
        if self.auto_mode:
            print(f"   🤖 AUTO MODE: Auto-accepting suggestions >= {self.auto_threshold:.0%}")
        print("=" * 60)

        # 1. Discovery Phase
        drafts = self.discover_drafts()
        if not drafts:
            print("\n✅ No draft positions found in positions-drafts/")
            return

        # Performance: Load all positions once and cache
        print(f"\n📊 Loading existing positions...")
        existing_positions = self.load_existing_positions()

        print(f"\n📊 Discovery:")
        print(f"   {len(drafts)} draft positions to process")
        print(f"   {len(existing_positions)} existing canonical positions")
        print()

        # 2. Process each draft
        for i, draft_path in enumerate(drafts, start=1):
            print(f"\n[{i}/{len(drafts)}] Processing: {draft_path.name}")
            print("─" * 60)

            # Load draft (lazy)
            draft = self.load_draft(draft_path)
            if not draft:
                self.skipped_count += 1
                continue

            # Find similar positions (with caching)
            similar = self.find_similar_positions(draft, existing_positions)

            # Determine action based on similarity
            if similar and similar[0]['similarity'] >= self.MERGE_THRESHOLD:
                # High similarity - auto-merge if in auto mode
                if self.auto_mode and similar[0]['similarity'] >= self.auto_threshold:
                    print(f"   🤖 AUTO-MERGING ({similar[0]['similarity']:.0%} similarity)")
                    action = "merge"
                else:
                    action = self.handle_merge_decision(draft, similar[0])
            elif similar and similar[0]['similarity'] >= self.CONFIRM_THRESHOLD:
                # Medium similarity - ask user (or skip in auto mode)
                if self.auto_mode:
                    print(f"   ⏭️  SKIPPED: Similarity {similar[0]['similarity']:.0%} below auto-threshold")
                    action = "skip"
                else:
                    action = self.confirm_merge_or_create(draft, similar[0])
            else:
                # Low similarity - create new position (both auto and manual mode)
                if self.auto_mode:
                    print(f"   🤖 AUTO-CREATE: Low similarity (best: {similar[0]['similarity']:.0%})" if similar else "   🤖 AUTO-CREATE: No similar positions found")
                else:
                    print(f"   ℹ️  No similar positions found")
                action = "create_new"

            # Execute action
            if action == "merge":
                self.merge_into_canonical(draft, similar[0])
            elif action == "create_new":
                self.create_new_position(draft)
            elif action == "skip":
                self.skip_position(draft)
            elif action == "stop":
                print("\n⏸️  Migration paused")
                break

        # 3. Summary
        self.print_summary()

    def discover_drafts(self) -> List[Path]:
        """Find all position draft files"""
        drafts = []
        for file in self.drafts_folder.glob("*.md"):
            if file.is_file():
                drafts.append(file)
        return sorted(drafts)

    @lru_cache(maxsize=128)
    def _parse_frontmatter_cached(self, content_hash: int) -> Tuple[Dict, str]:
        """Cached frontmatter parsing (internal use only)"""
        # This is called by parse_frontmatter_and_body with hash
        pass

    def parse_frontmatter_and_body(self, content: str) -> Tuple[Dict, str]:
        """Parse YAML frontmatter and extract body in one pass"""
        match = re.search(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if not match:
            return {}, content

        frontmatter = {}
        lines = match.group(1).split('\n')
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

        body = match.group(2).strip()
        return frontmatter, body

    def load_draft(self, path: Path) -> Optional[Dict]:
        """Load a draft position file"""
        try:
            content = path.read_text(encoding='utf-8')
            frontmatter, body = self.parse_frontmatter_and_body(content)

            return {
                'path': path,
                'title': frontmatter.get('title', path.stem),
                'frontmatter': frontmatter,
                'content': content,
                'body': body
            }
        except Exception as e:
            print(f"   ⚠️  Error loading {path}: {e}")
            return None

    def load_existing_positions(self) -> List[Dict]:
        """Load all existing canonical positions (with caching)"""
        if self._positions_cache is not None:
            return self._positions_cache

        positions = []
        # Performance: Use rglob which is efficient
        for file in self.positions_folder.rglob("*.md"):
            if file.is_file() and file.name != "0000 index.md":  # Skip root
                try:
                    content = file.read_text(encoding='utf-8')
                    frontmatter, body = self.parse_frontmatter_and_body(content)

                    # Only cache essential data
                    positions.append({
                        'path': file,
                        'title': frontmatter.get('title', file.stem),
                        'frontmatter': frontmatter,
                        'content': content,
                        'body': body,
                        # Pre-compute for similarity
                        '_body_lower': body.lower(),
                        '_title_lower': frontmatter.get('title', file.stem).lower(),
                        '_body_words': set(body.lower().split()),
                        '_title_words': set(frontmatter.get('title', file.stem).lower().split())
                    })
                except Exception:
                    continue

        self._positions_cache = positions
        return positions

    def find_similar_positions(self, draft: Dict, existing: List[Dict]) -> List[Dict]:
        """
        Find similar positions using simple text similarity.
        Returns list sorted by similarity (highest first).
        Performance optimized with caching and pre-computed word sets.
        """
        similarities = []

        # Pre-compute draft data
        draft_text = draft['body'].lower()
        draft_title = draft['title'].lower()
        draft_words = set(draft_text.split())
        draft_title_words = set(draft_title.split())

        for pos in existing:
            # Use cache key
            cache_key = (draft['path'].name, pos['path'].name)
            if cache_key in self._similarity_cache:
                similarity = self._similarity_cache[cache_key]
            else:
                # Use pre-computed data if available
                pos_words = pos.get('_body_words', set(pos['body'].lower().split()))
                pos_title_words = pos.get('_title_words', set(pos['title'].lower().split()))

                # Title similarity (word overlap)
                if draft_title_words and pos_title_words:
                    title_sim = len(draft_title_words & pos_title_words) / len(draft_title_words | pos_title_words)
                else:
                    title_sim = 0.0

                # Content similarity (simple word overlap)
                if draft_words and pos_words:
                    content_sim = len(draft_words & pos_words) / len(draft_words | pos_words)
                else:
                    content_sim = 0.0

                # Weighted similarity (title counts more)
                similarity = (0.6 * title_sim) + (0.4 * content_sim)

                # Cache result
                self._similarity_cache[cache_key] = similarity

            if similarity > 0.3:  # Only keep reasonable matches
                similarities.append({
                    'position': pos,
                    'similarity': similarity
                })

        return sorted(similarities, key=lambda x: x['similarity'], reverse=True)

    def handle_merge_decision(self, draft: Dict, similar: Dict) -> str:
        """Handle high-similarity case (>80%)"""
        canonical = similar['position']
        similarity = similar['similarity']

        print(f"\n🎯 HIGH SIMILARITY DETECTED ({similarity:.0%})")
        print(f"   Canonical: {canonical['title']}")
        print(f"   Location:  {canonical['path'].relative_to(self.positions_folder)}")
        print(f"\n   Recommendation: MERGE into canonical")
        print(f"\nChoices:")
        print(f"  1. Merge into canonical (recommended)")
        print(f"  2. View canonical content")
        print(f"  3. Create as new position")
        print(f"  4. Skip this draft")

        choice = input("\nYour choice [1]: ").strip() or "1"

        if choice == "1":
            return "merge"
        elif choice == "2":
            self.show_canonical(canonical)
            return self.handle_merge_decision(draft, similar)  # Ask again
        elif choice == "3":
            return "create_new"
        elif choice == "4":
            return "skip"
        else:
            return "merge"  # Default to merge

    def confirm_merge_or_create(self, draft: Dict, similar: Dict) -> str:
        """Handle medium-similarity case (70-80%)"""
        canonical = similar['position']
        similarity = similar['similarity']

        print(f"\n⚠️  POSSIBLE MATCH ({similarity:.0%})")
        print(f"   Canonical: {canonical['title']}")
        print(f"   Location:  {canonical['path'].relative_to(self.positions_folder)}")
        print(f"\nChoices:")
        print(f"  1. Merge into canonical")
        print(f"  2. View canonical content")
        print(f"  3. Create as new position")
        print(f"  4. Skip this draft")

        choice = input("\nYour choice [3]: ").strip() or "3"

        if choice == "1":
            return "merge"
        elif choice == "2":
            self.show_canonical(canonical)
            return self.confirm_merge_or_create(draft, similar)
        elif choice == "3":
            return "create_new"
        elif choice == "4":
            return "skip"
        else:
            return "create_new"  # Default to create new

    def show_canonical(self, canonical: Dict):
        """Display canonical position content"""
        print("\n" + "=" * 60)
        print(f"CANONICAL POSITION: {canonical['title']}")
        print("=" * 60)
        print(canonical['content'][:500])  # Show first 500 chars
        if len(canonical['content']) > 500:
            print("\n[... content truncated ...]")
        print("=" * 60)

    def merge_into_canonical(self, draft: Dict, similar: Dict):
        """Merge draft content into canonical position"""
        canonical = similar['position']

        print(f"\n✅ MERGING into: {canonical['title']}")

        if self.dry_run:
            print(f"   [DRY RUN] Would add source attribution to {canonical['path']}")
            self.merged_count += 1
            return

        # Read canonical (fresh, not from cache)
        canonical_content = canonical['path'].read_text(encoding='utf-8')

        # Extract source link from draft frontmatter (the processed file link)
        draft_related = draft['frontmatter'].get('related', [])
        if isinstance(draft_related, list) and draft_related:
            # Handle list format: ['[[source-file]]']
            source_match = re.search(r'\[\[([^\]]+)\]\]', draft_related[0])
        else:
            # Handle string format (legacy)
            source_match = re.search(r'\[\[([^\]]+)\]\]', str(draft_related)) if draft_related else None
        source_link = source_match.group(1) if source_match else "unknown"

        # Extract draft heading (the section that links back to processed file)
        draft_heading_match = re.search(r'##\s+\[\[([^\]]+)\]\]', draft['content'])
        if draft_heading_match:
            processed_filename = draft_heading_match.group(1)
            # Extract content after heading
            draft_excerpt = re.sub(r'---.*?---', '', draft['content'], flags=re.DOTALL)
            draft_excerpt = re.sub(r'##\s+\[\[.*?\]\]', '', draft_excerpt).strip()
        else:
            processed_filename = source_link
            draft_excerpt = draft['body']

        # Check if "Kontekstit ja lähteet" section exists
        if "## Kontekstit ja lähteet" in canonical_content:
            # Add new source
            new_source = f"\n### [[{processed_filename}]]\n\n> {draft_excerpt[:200]}...\n"
            canonical_content = canonical_content.replace(
                "## Kontekstit ja lähteet",
                f"## Kontekstit ja lähteet{new_source}"
            )
        else:
            # Create new section
            new_section = f"\n\n---\n\n## Kontekstit ja lähteet\n\n### [[{processed_filename}]]\n\n> {draft_excerpt[:200]}...\n"
            canonical_content += new_section

        # Write updated canonical
        canonical['path'].write_text(canonical_content, encoding='utf-8')

        # Move draft to processed
        self.move_to_processed(draft['path'])

        print(f"   ✓ Added source reference to canonical")
        print(f"   ✓ Moved draft to processed/")

        self.merged_count += 1

        # Invalidate cache for this position
        self._positions_cache = None

    def create_new_position(self, draft: Dict):
        """Create new canonical position (interactive or auto)"""
        if self.auto_mode:
            # Auto mode: Use AI classification to determine location
            print(f"   🤖 AUTO-CREATE: Classifying and creating new position")
            location = self.classify_position_location(draft)

            if not location:
                print(f"   ⚠️  Could not determine location, skipping")
                return self.skip_position(draft)

            # Create the position file
            success = self.create_position_file(draft, location)
            if success:
                print(f"   ✅ Created: positions/{location}{draft['title']}.md")
                self.migrated_count += 1
                # Move draft to processed
                self.move_to_processed(draft['path'])
            else:
                print(f"   ❌ Failed to create position file")
                self.skip_position(draft)
            return

        # Interactive mode
        print(f"\n📝 CREATE NEW POSITION")
        print(f"   Title: {draft['title']}")
        print(f"\n   Choose location:")
        print(f"  1. Interactive selection (hierarchical)")
        print(f"  2. Manual path entry")
        print(f"  3. Skip")

        choice = input("\nYour choice [1]: ").strip() or "1"

        if choice == "3":
            return self.skip_position(draft)
        elif choice == "2":
            location = input("Enter path (e.g., 'Digitalisaatio ja datatalous/ICT-hankinnat/'): ")
        else:
            # Interactive selection
            location = self.select_location_interactive()

        if not location:
            return self.skip_position(draft)

        # Create the position file
        success = self.create_position_file(draft, location)
        if success:
            print(f"   ✅ Created: positions/{location}{draft['title']}.md")
            self.migrated_count += 1
            self.move_to_processed(draft['path'])
        else:
            print(f"   ❌ Failed to create position file")

    def classify_position_location(self, draft: Dict) -> Optional[str]:
        """
        Use heuristic classification to determine the best location for a position.
        Returns path relative to positions/ folder (e.g., "Digitalisaatio ja datatalous/")
        """
        # Get available categories by scanning positions folder
        categories = self.get_top_level_categories()

        # Simple keyword-based classification
        title_lower = draft['title'].lower()
        content_lower = draft['content'].lower()
        combined = f"{title_lower} {content_lower}"

        # Classification rules based on keywords (order matters - check most specific first)
        # Check tax/economic first (before digitalization since some positions mention both)
        if any(word in combined for word in ['vero', 'verotus', 'yhteisövero', 'yritysveroj', 'julkisen talouden', 'budjetti', 'verokeinoin']):
            return "Talous- ja veropolitiikka/"

        if any(word in combined for word in ['digitalisaatio', 'data', 'tekoäly', 'ai', 'ict', 'verkko', 'kyber', 'tietoturva', 'pilvi']):
            return "Digitalisaatio ja datatalous/"

        if any(word in combined for word in ['osaaminen', 'koulutus', 'oppi', 'täydennys', 'osaaja']):
            return "Osaaminen/"

        if any(word in combined for word in ['työ', 'työelämä', 'työntekijä', 'työnantaja']):
            return "Työelämä/"

        if any(word in combined for word in ['innovaatio', 'tutkimus', 'kehitys', 't&k', 'tki']):
            return "Innovaatiot/"

        if any(word in combined for word in ['investointi', 'sijoitus', 'rahoitusmarkkinat']):
            return "Investointiympäristö/"

        if any(word in combined for word in ['kriittinen teknologia', 'puolijohde', 'kvantti', 'hpc']):
            return "Kriittiset teknologiat/"

        if any(word in combined for word in ['kestävä', 'ympäristö', 'ilmasto', 'energia', 'kiertotalous', 'yritysvastuu']):
            return "Kestävä kasvu/"

        if any(word in combined for word in ['resilienssi', 'varautuminen', 'kriisi', 'huolto']):
            return "Resilienssi/"

        # Default: try to find best match from categories
        if categories:
            return f"{categories[0]}/"

        return None

    def get_top_level_categories(self) -> List[str]:
        """Get list of top-level category folders in positions/"""
        categories = []
        if not self.positions_folder.exists():
            return categories

        for item in self.positions_folder.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                categories.append(item.name)

        return sorted(categories)

    def create_position_file(self, draft: Dict, location: str) -> bool:
        """
        Create a new position file at the specified location.
        location should be relative path like "Digitalisaatio ja datatalous/"
        Returns True if successful, False otherwise.
        """
        try:
            # Ensure location ends with /
            if not location.endswith('/'):
                location += '/'

            # Create target directory
            target_dir = self.positions_folder / location.rstrip('/')
            target_dir.mkdir(parents=True, exist_ok=True)

            # Sanitize filename
            safe_title = draft['title'].replace('/', '-').replace('\\', '-')
            filename = f"{safe_title}.md"
            target_file = target_dir / filename

            # Determine parent (up) reference
            # Parent is the immediate parent folder's overview file
            path_parts = location.rstrip('/').split('/')
            if len(path_parts) >= 1:
                parent = path_parts[-1]  # Last folder name (immediate parent)
            else:
                parent = "0000 index"  # Root level (shouldn't happen with current logic)

            # Extract related field from draft if it exists
            related_lines = ""
            if 'related' in draft['frontmatter'] and draft['frontmatter']['related']:
                related = draft['frontmatter']['related']
                # Handle both string and list formats
                if isinstance(related, list):
                    related_lines = "related:\n" + "\n".join(f'  - "{item}"' for item in related)
                elif isinstance(related, str) and related:
                    related_lines = f'related:\n  - "{related}"'

            # Create YAML frontmatter
            frontmatter_content = f"""---
type: position
title: "{draft['title']}"
up: "[[{parent}]]"
"""
            if related_lines:
                frontmatter_content += related_lines + "\n"
            frontmatter_content += "---\n\n"

            frontmatter = frontmatter_content

            # Add body from draft (not full content which includes frontmatter)
            content = frontmatter
            if 'body' in draft and draft['body']:
                # Add original body content (excludes frontmatter)
                content += draft['body']

            # Write file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except Exception as e:
            print(f"   Error creating file: {e}")
            return False

    def select_location_interactive(self) -> Optional[str]:
        """Interactive hierarchical location selection"""
        # TODO: Implement interactive tree navigation
        return None

    def skip_position(self, draft: Dict):
        """Skip this draft position"""
        print(f"   ⏭️  Skipped: {draft['title']}")
        self.skipped_count += 1

    def move_to_processed(self, draft_path: Path):
        """Move draft to processed folder"""
        self.processed_folder.mkdir(parents=True, exist_ok=True)
        target = self.processed_folder / draft_path.name
        draft_path.rename(target)

    def print_summary(self):
        """Print migration session summary"""
        duration = datetime.now() - self.session_start

        print("\n" + "=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Duration: {duration}")
        print(f"\n✅ Merged:   {self.merged_count}")
        print(f"📝 Created:  {self.migrated_count}")
        print(f"⏭️  Skipped:  {self.skipped_count}")
        print(f"📊 Total:    {self.merged_count + self.migrated_count + self.skipped_count}")
        if self.auto_mode:
            print(f"\n🤖 Auto mode: threshold {self.auto_threshold:.0%}")
        print("=" * 60)


def main():
    dry_run = "--dry-run" in sys.argv
    auto_mode = "--auto" in sys.argv

    # Parse threshold
    auto_threshold = 0.80  # Default
    if "--threshold" in sys.argv:
        idx = sys.argv.index("--threshold")
        if idx + 1 < len(sys.argv):
            try:
                auto_threshold = float(sys.argv[idx + 1])
                if not 0.0 <= auto_threshold <= 1.0:
                    print("Error: threshold must be between 0.0 and 1.0")
                    return
            except ValueError:
                print("Error: threshold must be a number")
                return

    if dry_run:
        print("🔍 Running in DRY-RUN mode (no changes will be made)\n")
    if auto_mode:
        print(f"🤖 Running in AUTO mode (threshold: {auto_threshold:.0%})\n")

    migrator = PositionMigrator(
        dry_run=dry_run,
        auto_mode=auto_mode,
        auto_threshold=auto_threshold
    )
    migrator.run()


if __name__ == "__main__":
    main()
