#!/usr/bin/env python3
"""Build self-contained preview files for Plate Discipline website."""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent
DEPLOY_DIR = BASE_DIR
PREVIEW_DIR = DEPLOY_DIR / "_preview"
CSS_FILE = DEPLOY_DIR / "css" / "style.css"
JS_FILE = DEPLOY_DIR / "js" / "main.js"

# Shell pages to process
SHELL_PAGES = [
    "index.html",
    "about.html",
    "subscribe.html",
    "archive.html",
    "privacy.html",
    "terms.html",
    "hall-of-fame.html",
]

# Essay pages to process
ESSAY_PAGES = [
    "the-slider-epidemic.html",
    "the-closer-is-a-myth.html",
    "the-dead-ball-is-back.html",
    "pitch-clock-and-the-rhythm-of-the-game.html",
]

def read_file(path):
    """Read file contents."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    """Write file contents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def convert_links_to_relative(content, is_essay=False):
    """Convert absolute links to relative .html links."""

    # Link mappings for conversion
    link_map = {
        'href="/archive"': 'href="archive.html"',
        'href="/about"': 'href="about.html"',
        'href="/subscribe"': 'href="subscribe.html"',
        'href="/privacy"': 'href="privacy.html"',
        'href="/terms"': 'href="terms.html"',
        'href="/hall-of-fame"': 'href="hall-of-fame.html"',
        'href="/"': 'href="index.html"',
        'href="/feed.xml"': 'href="../feed.xml"',

        # Essay links in homepage
        'href="/essays/slider-epidemic"': 'href="the-slider-epidemic.html"',
        'href="/essays/closer-myth"': 'href="the-closer-is-a-myth.html"',
        'href="/essays/dead-ball"': 'href="the-dead-ball-is-back.html"',
        'href="/essays/dead-ball-back"': 'href="the-dead-ball-is-back.html"',
        'href="/essays/pitch-clock-rhythm"': 'href="pitch-clock-and-the-rhythm-of-the-game.html"',

        # Direct essay links in archive
        'href="/the-slider-epidemic"': 'href="the-slider-epidemic.html"',
        'href="/the-closer-is-a-myth"': 'href="the-closer-is-a-myth.html"',
        'href="/the-dead-ball-is-back"': 'href="the-dead-ball-is-back.html"',
        'href="/pitch-clock-and-the-rhythm-of-the-game"': 'href="pitch-clock-and-the-rhythm-of-the-game.html"',
    }

    for old, new in link_map.items():
        content = content.replace(old, new)

    # Fix image paths for local preview
    content = content.replace('src="/images/', 'src="../images/')

    return content

def process_shell_page(filename):
    """Process a shell page (index, about, etc.) - inline CSS and JS."""
    print(f"Processing shell page: {filename}")

    html_path = DEPLOY_DIR / filename
    content = read_file(html_path)

    # Read CSS and JS
    css_content = read_file(CSS_FILE)
    js_content = read_file(JS_FILE)

    # Replace CSS link with inline style
    content = re.sub(
        r'<link rel="stylesheet" href="/css/style\.css">',
        f'<style>{css_content}</style>',
        content
    )

    # Replace JS script src with inline script
    content = re.sub(
        r'<script src="/js/main\.js" defer></script>',
        f'<script>{js_content}</script>',
        content
    )

    # Convert links to relative
    content = convert_links_to_relative(content, is_essay=False)

    # Change form action from /api/subscribe to #
    content = content.replace('action="/api/subscribe"', 'action="#"')

    # Write to preview
    preview_path = PREVIEW_DIR / filename
    write_file(preview_path, content)
    print(f"  ✓ Created {preview_path.name}")

def process_essay_page(filename):
    """Process an essay page - only fix internal links (essays have inline CSS)."""
    print(f"Processing essay page: {filename}")

    html_path = DEPLOY_DIR / filename
    content = read_file(html_path)

    # Convert links to relative
    content = convert_links_to_relative(content, is_essay=True)

    # Change form action from /api/subscribe to #
    content = content.replace('action="/api/subscribe"', 'action="#"')

    # Write to preview
    preview_path = PREVIEW_DIR / filename
    write_file(preview_path, content)
    print(f"  ✓ Created {preview_path.name}")

def main():
    """Main entry point."""
    print("Building Plate Discipline preview files...\n")

    # Create preview directory
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    # Process shell pages
    print("=== Processing Shell Pages ===")
    for page in SHELL_PAGES:
        try:
            process_shell_page(page)
        except Exception as e:
            print(f"  ✗ Error processing {page}: {e}")

    print("\n=== Processing Essay Pages ===")
    # Process essay pages
    for page in ESSAY_PAGES:
        try:
            process_essay_page(page)
        except Exception as e:
            print(f"  ✗ Error processing {page}: {e}")

    print("\n=== Summary ===")
    print(f"Created {len(SHELL_PAGES)} shell page previews")
    print(f"Created {len(ESSAY_PAGES)} essay page previews")
    print(f"Total: {len(SHELL_PAGES) + len(ESSAY_PAGES)} preview files")
    print(f"\nPreview files located at: {PREVIEW_DIR}")

if __name__ == "__main__":
    main()
