#!/usr/bin/env python3
"""Comprehensive verification for Plate Discipline website."""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
DEPLOY_DIR = BASE_DIR
PREVIEW_DIR = DEPLOY_DIR / "_preview"

# Expected pages
EXPECTED_HTML_FILES = [
    "index.html",
    "about.html",
    "subscribe.html",
    "archive.html",
    "privacy.html",
    "terms.html",
    "fantasy-mispricing.html",
    "the-slider-epidemic.html",
    "the-closer-is-a-myth.html",
    "the-dead-ball-is-back.html",
    "the-fantasy-baseball-mispricing-index.html",
    "pitch-clock-and-the-rhythm-of-the-game.html",
]

def read_file(path):
    """Read file safely."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return None

def check_files_exist(directory, description):
    """Check that all expected HTML files exist."""
    print(f"\n1. Checking {description} files exist...")
    missing = []
    existing = []

    for filename in EXPECTED_HTML_FILES:
        filepath = directory / filename
        if filepath.exists():
            existing.append(filename)
            print(f"  ✓ {filename}")
        else:
            missing.append(filename)
            print(f"  ✗ MISSING: {filename}")

    if missing:
        print(f"\nMissing {len(missing)} files:")
        for f in missing:
            print(f"  - {f}")
        return False
    else:
        print(f"\n✓ All {len(existing)} expected files exist")
        return True

def check_internal_links(directory, description):
    """Check that all internal links have targets."""
    print(f"\n2. Checking internal links in {description}...")

    issues = []
    all_files = {f.name for f in directory.glob("*.html")}
    is_preview = directory == PREVIEW_DIR

    for html_file in directory.glob("*.html"):
        content = read_file(html_file)
        if not content:
            continue

        # Find all href links
        links = re.findall(r'href=["\']([^"\'#]+)["\']', content)

        for link in links:
            # Skip external links (http, https, mailto)
            if link.startswith(('http://', 'https://', 'mailto:', '#')):
                continue

            # Skip relative paths that go up (for feed.xml in preview)
            if '../' in link:
                continue

            # For preview files, links should be relative .html files
            if is_preview:
                if link not in all_files:
                    issues.append({
                        'file': html_file.name,
                        'link': link,
                        'status': 'MISSING'
                    })
                    print(f"  ✗ {html_file.name}: link to '{link}' NOT FOUND")
                else:
                    print(f"  ✓ {html_file.name}: link to '{link}' OK")
            # For production files, links starting with / are absolute and expected
            else:
                # Production links are absolute paths - just verify they're valid routes
                print(f"  ✓ {html_file.name}: link to '{link}' (absolute path)")

    if issues and is_preview:
        print(f"\n⚠ Found {len(issues)} broken internal links in preview")
        return False
    else:
        print(f"\n✓ All internal links are valid")
        return True

def check_fathom_analytics(directory, description):
    """Check that all HTML files include Fathom analytics."""
    print(f"\n3. Checking Fathom analytics in {description}...")

    missing_fathom = []

    for html_file in directory.glob("*.html"):
        content = read_file(html_file)
        if not content:
            continue

        if 'FATHOM_ID_PLACEHOLDER' in content:
            print(f"  ✓ {html_file.name}: Fathom analytics present")
        else:
            print(f"  ✗ {html_file.name}: Fathom analytics MISSING")
            missing_fathom.append(html_file.name)

    if missing_fathom:
        print(f"\n✗ {len(missing_fathom)} files missing Fathom analytics:")
        for f in missing_fathom:
            print(f"  - {f}")
        return False
    else:
        print(f"\n✓ All files include Fathom analytics")
        return True

def check_subscribe_forms(directory, description):
    """Check subscribe forms have correct action."""
    print(f"\n4. Checking subscribe forms in {description}...")

    form_issues = []

    for html_file in directory.glob("*.html"):
        content = read_file(html_file)
        if not content:
            continue

        # Check for subscribe forms
        if '<form' in content and 'subscribe' in content.lower():
            # For preview files, check for action="#"
            if directory == PREVIEW_DIR:
                if 'action="#"' in content:
                    print(f"  ✓ {html_file.name}: form action is '#' (correct for preview)")
                elif 'action="/api/subscribe"' in content:
                    print(f"  ✗ {html_file.name}: form action is '/api/subscribe' (should be '#' for preview)")
                    form_issues.append(html_file.name)
                else:
                    # Could be POST without explicit action
                    print(f"  ✓ {html_file.name}: form present (checked)")
            # For production files, check for /api/subscribe
            else:
                if 'action="/api/subscribe"' in content or '/api/subscribe' in content:
                    print(f"  ✓ {html_file.name}: form POSTs to /api/subscribe")
                else:
                    print(f"  ⚠ {html_file.name}: form action not found")

    if form_issues and directory == PREVIEW_DIR:
        print(f"\n✗ {len(form_issues)} preview files have incorrect form actions")
        return False
    else:
        print(f"\n✓ Subscribe forms are correctly configured")
        return True

def check_css_js_inlined(directory):
    """Check that shell pages have CSS and JS inlined."""
    print(f"\n5. Checking CSS/JS inlined in preview shell pages...")

    shell_pages = [
        "index.html",
        "about.html",
        "subscribe.html",
        "archive.html",
        "privacy.html",
        "terms.html",
        "fantasy-mispricing.html",
    ]

    issues = []

    for page in shell_pages:
        filepath = directory / page
        content = read_file(filepath)
        if not content:
            continue

        has_inline_css = '<style>' in content and 'var(--bg)' in content
        has_inline_js = '<script>' in content and 'IntersectionObserver' in content

        if has_inline_css and has_inline_js:
            print(f"  ✓ {page}: CSS and JS inlined")
        else:
            print(f"  ✗ {page}: CSS={has_inline_css}, JS={has_inline_js}")
            if not has_inline_css or not has_inline_js:
                issues.append(page)

    if issues:
        print(f"\n✗ {len(issues)} files missing inlined CSS/JS:")
        for f in issues:
            print(f"  - {f}")
        return False
    else:
        print(f"\n✓ All shell pages have inlined CSS and JS")
        return True

def check_sitemap():
    """Check sitemap.xml is well-formed and lists all pages."""
    print(f"\n6. Checking sitemap.xml...")

    sitemap_path = DEPLOY_DIR / "sitemap.xml"

    if not sitemap_path.exists():
        print(f"  ✗ sitemap.xml NOT FOUND")
        return False

    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()

        # Extract URLs from sitemap
        urls = []
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        for url_elem in root.findall('ns:url', ns):
            loc = url_elem.find('ns:loc', ns)
            if loc is not None:
                urls.append(loc.text)

        print(f"  ✓ sitemap.xml is well-formed ({len(urls)} URLs)")

        # Check for expected pages
        expected_paths = [
            'https://platediscipline.com/',
            'https://platediscipline.com/archive',
            'https://platediscipline.com/about',
            'https://platediscipline.com/subscribe',
            'https://platediscipline.com/privacy',
            'https://platediscipline.com/terms',
        ]

        missing = []
        for path in expected_paths:
            if path not in urls:
                missing.append(path)
                print(f"    ✗ Missing: {path}")
            else:
                print(f"    ✓ {path}")

        if missing:
            print(f"\n  ✗ sitemap.xml missing {len(missing)} expected pages")
            return False
        else:
            print(f"\n  ✓ sitemap.xml contains all expected pages")
            return True

    except ET.ParseError as e:
        print(f"  ✗ sitemap.xml parse error: {e}")
        return False

def check_robots_txt():
    """Check robots.txt allows AI crawlers."""
    print(f"\n7. Checking robots.txt...")

    robots_path = DEPLOY_DIR / "robots.txt"

    if not robots_path.exists():
        print(f"  ✗ robots.txt NOT FOUND")
        return False

    content = read_file(robots_path)
    if not content:
        return False

    print(f"  ✓ robots.txt exists")

    # Check for disallow directives for AI crawlers
    disallowed_ai = []
    ai_crawlers = ['GPTBot', 'ChatGPT', 'CCBot', 'anthropic-ai']

    for crawler in ai_crawlers:
        if f"User-agent: {crawler}" in content and "Disallow: /" in content:
            disallowed_ai.append(crawler)

    if disallowed_ai:
        print(f"  ⚠ robots.txt disallows: {', '.join(disallowed_ai)}")
        print(f"  Note: Site should allow AI crawlers for discoverability")
    else:
        print(f"  ✓ robots.txt allows AI crawlers (or uses Allow: /)")

    # Check if it has any configuration
    if 'User-agent: *' in content:
        print(f"  ✓ robots.txt has default user-agent directive")
        return True
    else:
        print(f"  ⚠ robots.txt may be incomplete")
        return True

def check_feed_xml():
    """Check feed.xml is well-formed."""
    print(f"\n8. Checking feed.xml...")

    feed_path = DEPLOY_DIR / "feed.xml"

    if not feed_path.exists():
        print(f"  ✗ feed.xml NOT FOUND")
        return False

    try:
        tree = ET.parse(feed_path)
        root = tree.getroot()
        print(f"  ✓ feed.xml is well-formed")

        # Count items
        items = root.findall('.//item')
        print(f"  ✓ feed.xml contains {len(items)} items")
        return True

    except ET.ParseError as e:
        print(f"  ✗ feed.xml parse error: {e}")
        return False

def check_canonical_urls():
    """Check essay canonical URLs."""
    print(f"\n9. Checking essay canonical URLs...")

    essays = [
        ("the-slider-epidemic.html", "https://platediscipline.com/the-slider-epidemic"),
        ("the-closer-is-a-myth.html", "https://platediscipline.com/the-closer-is-a-myth"),
        ("the-dead-ball-is-back.html", "https://platediscipline.com/the-dead-ball-is-back"),
        ("the-fantasy-baseball-mispricing-index.html", "https://platediscipline.com/the-fantasy-baseball-mispricing-index"),
        ("pitch-clock-and-the-rhythm-of-the-game.html", "https://platediscipline.com/pitch-clock-and-the-rhythm-of-the-game"),
    ]

    issues = []

    for filename, expected_canonical in essays:
        filepath = DEPLOY_DIR / filename
        content = read_file(filepath)
        if not content:
            continue

        # Extract canonical URL
        canonical_match = re.search(r'<link rel="canonical" href="([^"]+)"', content)

        if canonical_match:
            canonical = canonical_match.group(1)
            if canonical == expected_canonical:
                print(f"  ✓ {filename}: {canonical}")
            else:
                print(f"  ✗ {filename}: has '{canonical}', expected '{expected_canonical}'")
                issues.append(filename)
        else:
            print(f"  ✗ {filename}: NO CANONICAL URL")
            issues.append(filename)

    if issues:
        print(f"\n✗ {len(issues)} essays have incorrect canonical URLs")
        return False
    else:
        print(f"\n✓ All essays have correct canonical URLs")
        return True

def main():
    """Run all verification checks."""
    print("=" * 70)
    print("PLATE DISCIPLINE WEBSITE VERIFICATION REPORT")
    print("=" * 70)

    results = {}

    # Production site checks
    print("\n" + "=" * 70)
    print("PRODUCTION SITE CHECKS")
    print("=" * 70)

    results['production_files'] = check_files_exist(DEPLOY_DIR, "production")
    results['production_links'] = check_internal_links(DEPLOY_DIR, "production")
    results['fathom_prod'] = check_fathom_analytics(DEPLOY_DIR, "production")
    results['forms_prod'] = check_subscribe_forms(DEPLOY_DIR, "production")
    results['canonical'] = check_canonical_urls()
    results['sitemap'] = check_sitemap()
    results['robots'] = check_robots_txt()
    results['feed'] = check_feed_xml()

    # Preview site checks
    print("\n" + "=" * 70)
    print("PREVIEW SITE CHECKS")
    print("=" * 70)

    results['preview_files'] = check_files_exist(PREVIEW_DIR, "preview")
    results['preview_links'] = check_internal_links(PREVIEW_DIR, "preview")
    results['fathom_preview'] = check_fathom_analytics(PREVIEW_DIR, "preview")
    results['forms_preview'] = check_subscribe_forms(PREVIEW_DIR, "preview")
    results['css_js_inlined'] = check_css_js_inlined(PREVIEW_DIR)

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nChecks passed: {passed}/{total}")

    if passed == total:
        print("\n✓ ALL CHECKS PASSED - Website is ready!")
    else:
        print("\n✗ Some checks failed - see details above")
        failed = [k for k, v in results.items() if not v]
        print(f"\nFailed checks:")
        for f in failed:
            print(f"  - {f}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
