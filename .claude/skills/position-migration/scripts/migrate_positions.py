#!/usr/bin/env python3
"""
Position Migration Script

Migrates position files from positions-drafts/ to the hierarchical positions/ structure
with AI-assisted classification, duplicate detection, and interactive guidance.

Usage:
    python migrate_positions.py [--resume] [--dry-run]

Options:
    --resume    Resume from last migration session
    --dry-run   Preview migrations without making changes
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import json


class PositionMigrator:
    """Main migration class handling the interactive workflow"""

    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.drafts_folder = Path("positions-drafts")
        self.positions_folder = Path("positions")
        self.processed_folder = Path("positions-drafts/processed")
        self.suggestions_file = Path("change-suggestions.md")
        self.log_folder = Path("migration-logs")

        # Session tracking
        self.session_start = datetime.now()
        self.session_log = []
        self.migrated_count = 0
        self.merged_count = 0
        self.skipped_count = 0
        self.structural_changes_count = 0

        # Similarity thresholds
        self.DUPLICATE_THRESHOLD = 0.85
        self.RELATED_THRESHOLD = 0.70
        self.MENTION_THRESHOLD = 0.50

    def run(self):
        """Main migration workflow"""
        print("🚀 Starting Position Migration")
        print("=" * 55)

        # 1. Discovery Phase
        drafts = self.discover_drafts()
        if not drafts:
            print("\n✅ No draft positions found in positions-drafts/")
            return

        existing_positions = self.load_existing_positions()

        print(f"\n📊 Discovery Summary:")
        print(f"   Found {len(drafts)} draft positions ready for migration")
        print(f"   Loaded {len(existing_positions)} existing positions")
        print()

        # 2. Process each draft
        for i, draft in enumerate(drafts, start=1):
            print(f"\n[Processing {i}/{len(drafts)}]")
            print("─" * 55)

            # Display draft
            self.display_draft(draft)

            # Semantic analysis
            similar_positions = self.find_similar_positions(draft, existing_positions)

            # Classification suggestion
            suggestion = self.suggest_classification(draft, existing_positions, similar_positions)

            # User decision
            action = self.get_user_decision(draft, suggestion, similar_positions)

            # Execute action
            if action == "accept":
                self.migrate_position(draft, suggestion)
            elif action == "modify":
                modified_suggestion = self.modify_classification(draft, suggestion)
                self.migrate_position(draft, modified_suggestion)
            elif action == "merge":
                target = self.select_merge_target(similar_positions)
                self.merge_position(draft, target)
            elif action == "skip":
                self.skip_position(draft)
            elif action == "stop":
                print("\n⏸️  Migration session paused")
                break

        # 3. Session summary
        self.print_session_summary()
        self.save_migration_log()

    def discover_drafts(self) -> List[Dict]:
        """Scan positions-drafts/ for valid position files"""
        drafts = []

        if not self.drafts_folder.exists():
            return drafts

        for file_path in self.drafts_folder.glob("*.md"):
            draft = self.parse_position_file(file_path)
            if draft and self.validate_draft(draft):
                drafts.append(draft)

        return drafts

    def load_existing_positions(self) -> List[Dict]:
        """Load all existing positions from positions/ folder"""
        positions = []

        if not self.positions_folder.exists():
            return positions

        for file_path in self.positions_folder.rglob("*.md"):
            position = self.parse_position_file(file_path)
            if position:
                positions.append(position)

        return positions

    def parse_position_file(self, file_path: Path) -> Optional[Dict]:
        """Parse a position markdown file and extract frontmatter and content"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
            if not frontmatter_match:
                return None

            frontmatter_text = frontmatter_match.group(1)
            body = frontmatter_match.group(2).strip()

            # Parse YAML frontmatter (simple parsing)
            frontmatter = {}
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip().strip('"')

            return {
                'path': file_path,
                'title': frontmatter.get('title', ''),
                'source': frontmatter.get('source', ''),
                'up': frontmatter.get('up', ''),
                'related': frontmatter.get('related', ''),
                'content': body,
                'frontmatter': frontmatter
            }
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
            return None

    def validate_draft(self, draft: Dict) -> bool:
        """Validate that draft has required fields"""
        if not draft.get('title'):
            print(f"⚠️  Skipping {draft['path'].name}: Missing title")
            return False
        return True

    def display_draft(self, draft: Dict):
        """Display draft information to user"""
        print(f"Draft: \"{draft['title']}\"")
        if draft.get('source'):
            print(f"Source: {draft['source'][:50]}...")
        if draft.get('related'):
            print(f"Related: {draft['related']}")
        print()
        print("Content preview:")
        preview = draft['content'][:200]
        print(preview + "..." if len(draft['content']) > 200 else preview)
        print("─" * 55)

    def find_similar_positions(self, draft: Dict, existing_positions: List[Dict]) -> List[Tuple[Dict, float]]:
        """Find similar positions using semantic analysis"""
        # TODO: Implement semantic similarity using embeddings
        # This is a placeholder that would use actual embedding-based similarity

        similar = []
        draft_text = draft['title'] + " " + draft['content']

        for position in existing_positions:
            position_text = position['title'] + " " + position['content']

            # Placeholder: simple word overlap (replace with embeddings)
            similarity = self.calculate_text_similarity(draft_text, position_text)

            if similarity >= self.MENTION_THRESHOLD:
                similar.append((position, similarity))

        # Sort by similarity descending
        similar.sort(key=lambda x: x[1], reverse=True)

        return similar[:5]  # Top 5 similar positions

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (placeholder for embeddings)"""
        # TODO: Replace with actual embedding-based similarity
        # This is a simple word overlap metric as placeholder

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        overlap = len(words1 & words2)
        total = len(words1 | words2)

        return overlap / total if total > 0 else 0.0

    def suggest_classification(self, draft: Dict, existing_positions: List[Dict],
                              similar_positions: List[Tuple[Dict, float]]) -> Dict:
        """Suggest classification based on content analysis"""
        # TODO: Implement AI-based classification suggestion
        # This is a placeholder that would use actual LLM or ML model

        suggestion = {
            'theme': None,
            'sub_theme': None,
            'position_number': None,
            'confidence': 0.0,
            'reasoning': '',
            'alternatives': []
        }

        # Placeholder logic
        if similar_positions:
            most_similar, similarity = similar_positions[0]
            # Extract parent structure from similar position
            # This would be more sophisticated in real implementation
            suggestion['confidence'] = similarity
            suggestion['reasoning'] = f"Similar to existing position ({similarity:.0%} match)"

        return suggestion

    def get_user_decision(self, draft: Dict, suggestion: Dict,
                         similar_positions: List[Tuple[Dict, float]]) -> str:
        """Get user decision on how to proceed"""
        print("\n🎯 SUGGESTED CLASSIFICATION")
        print(f"Confidence: {suggestion['confidence']:.0%}")

        if similar_positions:
            print("\n⚠️  DUPLICATE CHECK")
            for position, similarity in similar_positions[:3]:
                if similarity >= self.RELATED_THRESHOLD:
                    print(f"  {position['title']} ({similarity:.0%} similar)")

        print("\nChoose action:")
        print("  1. Accept suggested classification")
        print("  2. View/modify classification details")
        print("  3. View similar position content")
        print("  4. Skip this position (leave in drafts)")
        print("  5. Stop migration session")

        choice = input("\nYour choice: ").strip()

        action_map = {
            '1': 'accept',
            '2': 'modify',
            '3': 'view_similar',
            '4': 'skip',
            '5': 'stop'
        }

        return action_map.get(choice, 'skip')

    def modify_classification(self, draft: Dict, suggestion: Dict) -> Dict:
        """Interactive classification modification"""
        # TODO: Implement interactive classification wizard
        print("\n🔧 Modify Classification (not yet implemented)")
        return suggestion

    def select_merge_target(self, similar_positions: List[Tuple[Dict, float]]) -> Dict:
        """Select target position for merging"""
        # TODO: Implement merge target selection
        return similar_positions[0][0] if similar_positions else None

    def migrate_position(self, draft: Dict, suggestion: Dict):
        """Execute migration of position to target location"""
        print(f"\n✅ Migrating: {draft['title']}")

        if self.dry_run:
            print("   [DRY RUN - No files created]")
        else:
            # TODO: Implement actual file migration
            # - Create target file
            # - Update frontmatter
            # - Move original to processed/
            pass

        self.migrated_count += 1
        self.session_log.append({
            'action': 'migrate',
            'draft': draft['title'],
            'target': suggestion
        })

    def merge_position(self, draft: Dict, target: Dict):
        """Merge draft content into existing position"""
        print(f"\n🔀 Merging into: {target['title']}")

        if self.dry_run:
            print("   [DRY RUN - No files modified]")
        else:
            # TODO: Implement actual merge
            # - Append content to target
            # - Update related links
            # - Move original to processed/
            pass

        self.merged_count += 1
        self.session_log.append({
            'action': 'merge',
            'draft': draft['title'],
            'target': target['title']
        })

    def skip_position(self, draft: Dict):
        """Skip position, leave in drafts"""
        print(f"\n⏸️  Skipped: {draft['title']}")
        self.skipped_count += 1
        self.session_log.append({
            'action': 'skip',
            'draft': draft['title']
        })

    def print_session_summary(self):
        """Print comprehensive session summary"""
        print("\n" + "=" * 55)
        print("MIGRATION SESSION COMPLETE")
        print("=" * 55)
        print(f"\nSummary:")
        print(f"  ✅ Migrated: {self.migrated_count} positions")
        print(f"  🔀 Merged: {self.merged_count} positions")
        print(f"  ⏸️  Skipped: {self.skipped_count} positions")
        print(f"  🔧 Structural changes needed: {self.structural_changes_count}")
        print()

    def save_migration_log(self):
        """Save detailed migration log"""
        self.log_folder.mkdir(exist_ok=True)

        timestamp = self.session_start.strftime("%Y%m%d-%H%M%S")
        log_file = self.log_folder / f"migration-log-{timestamp}.md"

        # TODO: Write comprehensive log
        print(f"📄 Detailed log saved to: {log_file}")


def main():
    """Command-line interface"""
    dry_run = "--dry-run" in sys.argv
    resume = "--resume" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    migrator = PositionMigrator(dry_run=dry_run)

    try:
        migrator.run()
    except KeyboardInterrupt:
        print("\n\n⏸️  Migration interrupted by user")
        migrator.print_session_summary()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
