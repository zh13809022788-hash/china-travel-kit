"""Generate ALL missing locale hub pages for every nav-relevant route.

Handles two source patterns:
1. Single-file pages: src/pages/X.astro  ->  src/pages/{locale}/X.astro
2. Directory-index:   src/pages/X/index.astro  ->  src/pages/{locale}/X/index.astro
"""

import os, re

PROJECT_ROOT = r'D:\独立站\china-travel-kit'
PAGES_DIR = os.path.join(PROJECT_ROOT, 'src', 'pages')

LOCALES = [
    ('zh-tw', 'zh-TW'),
    ('ja', 'ja'),
    ('ko', 'ko'),
    ('ru', 'ru'),
    ('fr', 'fr'),
    ('de', 'de'),
    ('es', 'es'),
]

# Single-file pages: (filename)
SINGLE_FILE_PAGES = [
    'about.astro',
    'privacy.astro',
    'terms.astro',
    'contact.astro',
    'travel-help.astro',
    'resources.astro',
    'trip-planner.astro',
]

# Directory-index pages: (dirname)
DIR_INDEX_PAGES = [
    'apps',
    'tools',
    'series',
    'long-stay',
    'digital-nomads',
]


def adjust_imports_single(content):
    """Adjust import paths for single-file pages (one level deeper)."""
    return (content
        .replace("from '../layouts/", "from '../../layouts/")
        .replace("from '../components/", "from '../../components/")
        .replace("from '../config'", "from '../../config'")
        .replace("from '../styles/", "from '../../styles/")
        .replace("from '../data/", "from '../../data/")
        .replace("from '../assets/", "from '../../assets/")
    )


def adjust_imports_dir(content):
    """Adjust import paths for directory-index pages (one level deeper)."""
    return (content
        .replace("from '../../layouts/", "from '../../../layouts/")
        .replace("from '../../components/", "from '../../../components/")
        .replace("from '../../config'", "from '../../../config'")
        .replace("from '../../styles/", "from '../../../styles/")
        .replace("from '../../data/", "from '../../../data/")
        .replace("from '../../assets/", "from '../../../assets/")
    )


def add_locale_props(content, locale_code):
    """Add locale prop to BaseLayout, GuideLayout, and Header."""
    # BaseLayout: add locale before closing >
    # Handle: <BaseLayout title="..." description="...">  or  <BaseLayout title={`...`} description={...}>
    # Also handle: <BaseLayout title="..." description="..." noindex={false}>
    # Strategy: find <BaseLayout ...> and add locale="xx" before the closing >

    def add_to_tag(match):
        full = match.group(0)
        # Already has locale?
        if 'locale=' in full:
            return full
        # Add before closing > or />
        if full.endswith('/>'):
            return full[:-2] + f' locale="{locale_code}"/>'
        else:
            return full[:-1] + f' locale="{locale_code}">'

    content = re.sub(r'<BaseLayout[^>]*>', add_to_tag, content)
    content = re.sub(r'<GuideLayout[^>]*>', add_to_tag, content)

    # Header: <Header /> -> <Header locale="xx" />
    content = re.sub(
        r'<Header\s*/>',
        f'<Header locale="{locale_code}" />',
        content
    )
    # Also handle <Header> without self-closing
    content = re.sub(
        r'<Header(?!\s+locale)(\s+[^>]*)?>',
        f'<Header locale="{locale_code}"\\1>',
        content
    )

    return content


def generate():
    count = 0
    for locale_dir, locale_code in LOCALES:
        locale_pages_dir = os.path.join(PAGES_DIR, locale_dir)
        os.makedirs(locale_pages_dir, exist_ok=True)

        # Single-file pages
        for fname in SINGLE_FILE_PAGES:
            src = os.path.join(PAGES_DIR, fname)
            if not os.path.exists(src):
                print(f'  SKIP {fname} — not found')
                continue

            with open(src, 'r', encoding='utf-8') as f:
                content = f.read()

            content = adjust_imports_single(content)
            content = add_locale_props(content, locale_code)

            dst = os.path.join(locale_pages_dir, fname)
            with open(dst, 'w', encoding='utf-8') as f:
                f.write(content)

            count += 1
            print(f'  {locale_dir}/{fname}')

        # Directory-index pages
        for dirname in DIR_INDEX_PAGES:
            src = os.path.join(PAGES_DIR, dirname, 'index.astro')
            if not os.path.exists(src):
                print(f'  SKIP {dirname}/index.astro — not found')
                continue

            with open(src, 'r', encoding='utf-8') as f:
                content = f.read()

            content = adjust_imports_dir(content)
            content = add_locale_props(content, locale_code)

            dst_dir = os.path.join(locale_pages_dir, dirname)
            os.makedirs(dst_dir, exist_ok=True)
            dst = os.path.join(dst_dir, 'index.astro')
            with open(dst, 'w', encoding='utf-8') as f:
                f.write(content)

            count += 1
            print(f'  {locale_dir}/{dirname}/index.astro')

    print(f'\nDone: {count} locale hub pages generated')


if __name__ == '__main__':
    generate()
