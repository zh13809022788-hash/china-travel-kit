"""Generate locale-prefixed hub pages.

Generated locale pages must use the matching translated post collection and
locale-prefixed internal links.
"""

import os, re
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
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

LOCALE_META = {
    'zh-tw': {'collection': 'posts-zh-tw', 'date': 'zh-TW'},
    'ja': {'collection': 'posts-ja', 'date': 'ja-JP'},
    'ko': {'collection': 'posts-ko', 'date': 'ko-KR'},
    'ru': {'collection': 'posts-ru', 'date': 'ru-RU'},
    'fr': {'collection': 'posts-fr', 'date': 'fr-FR'},
    'de': {'collection': 'posts-de', 'date': 'de-DE'},
    'es': {'collection': 'posts-es', 'date': 'es-ES'},
}

INTERNAL_ROOTS = (
    'posts', 'tools', 'cities', 'payment', 'esim', 'transport', 'food',
    'trip-planner', 'resources', 'apps', 'essentials', 'long-stay',
    'digital-nomads', 'travel-help', 'about', 'contact', 'privacy', 'terms',
    'editorial-policy', 'affiliate-disclosure', 'series',
)

LOCALE_DIR_RE = r'(?:zh-tw|ja|ko|ru|fr|de|es)'

# Hub pages to duplicate across locales
# Each entry: (source_dir, import_path_prefix)
# The import_path_prefix is adjusted based on nesting depth
HUBS = [
    'payment',
    'esim',
    'transport',
    'food',
    'essentials',
    'cities',
]


def localize_generated_content(content, locale_dir):
    meta = LOCALE_META[locale_dir]
    collection = meta['collection']
    date_locale = meta['date']
    roots = '|'.join(re.escape(root) for root in INTERNAL_ROOTS)

    content = content.replace("getCollection('posts')", f"getCollection('{collection}')")
    content = content.replace("toLocaleDateString('en-US'", f"toLocaleDateString('{date_locale}'")
    content = content.replace('href={`/posts/', f'href={{`/{locale_dir}/posts/')
    content = content.replace('href={`/tools/', f'href={{`/{locale_dir}/tools/')
    content = content.replace('href={`/digital-nomads/', f'href={{`/{locale_dir}/digital-nomads/')
    content = re.sub(
        rf'href="/(?!{LOCALE_DIR_RE}/)({roots})/',
        rf'href="/{locale_dir}/\1/',
        content,
    )
    content = re.sub(
        rf"(href|next|guide): '/(?!{LOCALE_DIR_RE}/)({roots})/",
        rf"\1: '/{locale_dir}/\2/",
        content,
    )
    return content

def generate_locale_hubs():
    count = 0
    for locale_dir, locale_code in LOCALES:
        for hub in HUBS:
            source = os.path.join(PAGES_DIR, hub, 'index.astro')
            if not os.path.exists(source):
                print(f'  SKIP {hub} — source not found')
                continue

            # Read source file
            with open(source, 'r', encoding='utf-8') as f:
                src_content = f.read()

            # Create target directory
            target_dir = os.path.join(PAGES_DIR, locale_dir, hub)
            os.makedirs(target_dir, exist_ok=True)
            target_file = os.path.join(target_dir, 'index.astro')

            # Modify imports: from '../../' → '../../../' (one more level deep)
            modified = src_content.replace(
                "from '../../layouts/", "from '../../../layouts/"
            ).replace(
                "from '../../components/", "from '../../../components/"
            ).replace(
                "from '../../content/", "from '../../../content/"
            ).replace(
                "from '../../config'", "from '../../../config'"
            ).replace(
                "from '../../styles/", "from '../../../styles/"
            ).replace(
                "from '../../data/", "from '../../../data/"
            )

            # Add locale prop to BaseLayout
            modified = modified.replace(
                '<BaseLayout title={`${title} | ChinaTripBox`} description={description}>',
                f'<BaseLayout title={{`${{title}} | ChinaTripBox`}} description={{description}} locale="{locale_code}">'
            )
            
            # Add locale prop to Header
            modified = modified.replace(
                '<Header />',
                f'<Header locale="{locale_code}" />'
            )
            modified = localize_generated_content(modified, locale_dir)

            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(modified)

            count += 1
            print(f'  {locale_dir}/{hub}/')

    print(f'\nDone: {count} locale hub pages created')

if __name__ == '__main__':
    generate_locale_hubs()
