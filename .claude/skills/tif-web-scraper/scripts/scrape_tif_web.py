#!/usr/bin/env python3
"""
TIF Website Scraper
Scrapes content from Teknologiateollisuus (TIF) website and converts to markdown.
"""

import sys
import re
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime

def scrape_tif_website(url: str, output_dir: str = None) -> dict:
    """
    Scrape content from a TIF website URL and prepare it for markdown conversion.

    Args:
        url: The TIF website URL to scrape
        output_dir: Optional output directory path (defaults to papers/TIF web/)

    Returns:
        dict with 'title', 'content', 'url', and 'output_path' keys
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("Error: Required packages not installed.")
        print("Please install: pip install requests beautifulsoup4")
        sys.exit(1)

    # Fetch the page
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        sys.exit(1)

    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract title
    title = ""
    h1_tag = soup.find('h1')
    if h1_tag:
        title = h1_tag.get_text(strip=True)

    # Find main content area (adjust selector based on TIF website structure)
    # Common patterns: main, article, .content, #main-content
    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')

    if not main_content:
        print("Warning: Could not find main content area, using body")
        main_content = soup.body

    # Remove navigation, sidebar, and other non-content elements
    for element in main_content.find_all(['nav', 'aside', 'header', 'footer']):
        element.decompose()

    # Remove elements with common navigation/menu classes
    for element in main_content.find_all(class_=['navigation', 'nav', 'menu', 'sidebar', 'breadcrumb']):
        element.decompose()

    # Extract and clean content
    content_parts = []
    title_added = False

    # Look for the "Päivitetty" (updated) date
    updated_date = main_content.find('div', class_='em-block-hero__modified-date')

    # Process content elements
    for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'div']):
        text = element.get_text(strip=True)

        # Stop at "Lisätiedot:"
        if text.startswith("Lisätiedot:"):
            break

        # Skip empty elements
        if not text:
            continue

        # Skip navigation/menu elements based on class or common patterns
        element_classes = element.get('class', [])
        if any(nav_class in str(element_classes).lower() for nav_class in ['nav', 'menu', 'sidebar', 'breadcrumb']):
            continue

        # Format based on element type
        if element.name == 'div':
            # Only include specific divs like the modified date
            if 'em-block-hero__modified-date' in element_classes:
                content_parts.append(f"\n{text}\n")
            continue
        elif element.name == 'h1':
            # Only add the first h1 to avoid duplication
            if not title_added and title:
                content_parts.append(f"# {text}\n")
                title_added = True
        elif element.name == 'h2':
            content_parts.append(f"\n## {text}\n")
        elif element.name == 'h3':
            content_parts.append(f"\n### {text}\n")
        elif element.name == 'h4':
            content_parts.append(f"\n#### {text}\n")
        elif element.name == 'p':
            # Skip paragraphs that are likely navigation (contain multiple links)
            links = element.find_all('a')
            if len(links) > 3:  # Likely a navigation menu
                continue
            # Fix missing spaces after periods
            text = re.sub(r'\.([A-ZÄÖÅ])', r'. \1', text)
            content_parts.append(f"\n{text}\n")
        elif element.name in ['ul', 'ol']:
            # Process list items
            list_items = element.find_all('li', recursive=False)
            for li in list_items:
                li_text = li.get_text(strip=True)
                if li_text:
                    # Clean up extra whitespace
                    li_text = ' '.join(li_text.split())
                    # Fix missing spaces after periods
                    li_text = re.sub(r'\.([A-ZÄÖÅ])', r'. \1', li_text)
                    content_parts.append(f"- {li_text}")

    content = '\n'.join(content_parts)

    # Clean up multiple newlines
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Extract date from content (format: "Päivitetty DD.MM.YYYY klo HH:MM")
    date_match = re.search(r'Päivitetty (\d{2})\.(\d{2})\.(\d{4})', content)
    if date_match:
        day, month, year = date_match.groups()
        scraped_date = f"{year}-{month}-{day}"
    else:
        # Fallback to current date if not found
        scraped_date = datetime.now().strftime("%Y-%m-%d")

    # Determine output path
    if output_dir is None:
        output_dir = "sources/TIF web"

    # Generate filename and folder structure from URL path
    path_parts = urlparse(url).path.strip('/').split('/')

    if path_parts and path_parts[-1]:
        # Last segment becomes the slug
        url_slug = path_parts[-1]
        # Format: YYYY-MM-DD-slug-web.md
        filename = f"{scraped_date}-{url_slug}-web.md"

        # All segments except the last become the folder structure
        if len(path_parts) > 1:
            # Create subdirectories from URL path (excluding last segment)
            subdirs = '/'.join(path_parts[:-1])
            output_path = Path(output_dir) / subdirs / filename
        else:
            output_path = Path(output_dir) / filename
    else:
        filename = f"{scraped_date}-scraped_content-web.md"
        output_path = Path(output_dir) / filename

    return {
        'title': title,
        'content': content,
        'url': url,
        'output_path': str(output_path),
        'scraped_date': scraped_date
    }


def check_previous_scrapes(url: str) -> list:
    """
    Check if URL was previously scraped, return list of previous scrape records.

    Args:
        url: The URL to check

    Returns:
        List of dicts with 'date' and 'file_path' keys, sorted by date (oldest first)
    """
    registry_file = Path("sources/scraped-urls.txt")

    if not registry_file.exists():
        return []

    previous_scrapes = []
    content = registry_file.read_text(encoding='utf-8')

    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 3:
            date, line_url, file_path = parts[0], parts[1], parts[2]
            if line_url == url:
                previous_scrapes.append({
                    'date': date,
                    'file_path': file_path,
                    'url': line_url
                })

    return sorted(previous_scrapes, key=lambda x: x['date'])


def find_similar_url_in_registry(url: str) -> list:
    """
    Find URLs in registry that might be variations of the given URL.
    Helps detect when user provides shortened URL.

    Args:
        url: The URL to check

    Returns:
        List of similar URLs found in registry
    """
    registry_file = Path("sources/scraped-urls.txt")

    if not registry_file.exists():
        return []

    url_path = urlparse(url).path.strip('/')
    url_slug = url_path.split('/')[-1] if url_path else ''

    similar_urls = []
    content = registry_file.read_text(encoding='utf-8')

    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 3:
            date, line_url, file_path = parts[0], parts[1], parts[2]

            # Check if this URL ends with the same slug
            line_path = urlparse(line_url).path.strip('/')
            line_slug = line_path.split('/')[-1] if line_path else ''

            if line_slug == url_slug and line_url != url:
                similar_urls.append({
                    'url': line_url,
                    'file_path': file_path,
                    'date': date
                })

    return similar_urls


def log_scraped_url(url: str, output_path: str, scraped_date: str):
    """
    Log scraped URL to registry file for tracking and re-scraping.

    Args:
        url: The scraped URL
        output_path: Path to the created source file
        scraped_date: Date the content was scraped (YYYY-MM-DD)
    """
    registry_file = Path("sources/scraped-urls.txt")

    # Ensure sources directory exists
    registry_file.parent.mkdir(parents=True, exist_ok=True)

    # Create file with header if it doesn't exist
    if not registry_file.exists():
        header = """# TIF Scraped Sources Registry
#
# This file tracks all URLs that have been scraped from the TIF website.
# Use this to re-scrape and detect changes in source content.
#
# Format: YYYY-MM-DD | URL | Output File
# Lines starting with # are comments
# Multiple entries for the same URL indicate version history (re-scrapes)

"""
        registry_file.write_text(header, encoding='utf-8')

    # Append new entry
    entry = f"{scraped_date} | {url} | {output_path}\n"
    with registry_file.open('a', encoding='utf-8') as f:
        f.write(entry)


def create_markdown_file(scraped_data: dict, parent_doc: str = None):
    """
    Create a markdown file with proper frontmatter.

    Args:
        scraped_data: Dictionary from scrape_tif_website()
        parent_doc: Optional parent document name for 'up' field
    """
    title = scraped_data['title']
    content = scraped_data['content']
    url = scraped_data['url']
    output_path = Path(scraped_data['output_path'])

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build frontmatter
    scraped_date = scraped_data.get('scraped_date', datetime.now().strftime("%Y-%m-%d"))

    frontmatter_parts = [
        "---",
        "type: web",
        f'title: "{title}"',
        f'source: "{url}"',
        f'scraped: {scraped_date}',
    ]

    if parent_doc:
        frontmatter_parts.append(f'up: "[[{parent_doc}]]"')
    else:
        frontmatter_parts.append('up:')

    frontmatter_parts.extend([
        "related:",
        "---",
    ])

    frontmatter = '\n'.join(frontmatter_parts)

    # Combine frontmatter and content
    full_content = f"{frontmatter}\n\n{content}"

    # Write to file
    output_path.write_text(full_content, encoding='utf-8')

    # Log to scraped-urls registry
    log_scraped_url(url, str(output_path), scraped_date)

    print(f"✅ Created source at: {output_path}")
    return str(output_path)


def main():
    """Command-line interface"""
    if len(sys.argv) < 2:
        print("Usage: python scrape_tif_web.py <url> [output_dir] [parent_doc]")
        print("\nExample:")
        print("  python scrape_tif_web.py https://teknologiateollisuus.fi/tavoitteemme/osaava-tyovoima/")
        print("  python scrape_tif_web.py <url> 'sources/TIF web' '3000 Osaaminen'")
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    parent_doc = sys.argv[3] if len(sys.argv) > 3 else None

    # Check for previous scrapes of exact URL
    previous_scrapes = check_previous_scrapes(url)

    # Also check for similar URLs (different path but same slug)
    similar_urls = find_similar_url_in_registry(url)

    if similar_urls and not previous_scrapes:
        print(f"⚠️  Warning: Found similar URL(s) already scraped:")
        for similar in similar_urls:
            print(f"   - {similar['url']}")
            print(f"     File: {similar['file_path']}")
        print(f"\n❓ You provided: {url}")
        print(f"   This may create duplicate content with different folder structure.")
        print(f"   Consider using the full URL from registry instead.\n")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Aborted.")
            sys.exit(0)

    if previous_scrapes:
        print(f"📋 Previous scrapes found: {len(previous_scrapes)}")
        for scrape in previous_scrapes:
            print(f"   - {scrape['date']}: {scrape['file_path']}")
        print(f"\n🔄 Re-scraping to create new version...")
    else:
        print(f"🔍 First scrape of: {url}")

    scraped_data = scrape_tif_website(url, output_dir)

    print(f"📝 Creating markdown file...")
    output_path = create_markdown_file(scraped_data, parent_doc)

    print(f"\n✅ Done! Source created at: {output_path}")

    if previous_scrapes:
        latest_previous = previous_scrapes[-1]
        print(f"\n💡 Tip: Compare versions with:")
        print(f"   python .claude/skills/source-diff/scripts/diff_sources.py \\")
        print(f"     '{latest_previous['file_path']}' \\")
        print(f"     '{output_path}'")


if __name__ == "__main__":
    main()
