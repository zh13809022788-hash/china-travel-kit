"""Generate locale-prefixed hub pages that render English content with locale's Header/Footer."""

import os, shutil

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

            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(modified)

            count += 1
            print(f'  {locale_dir}/{hub}/')

    print(f'\nDone: {count} locale hub pages created')

if __name__ == '__main__':
    generate_locale_hubs()
