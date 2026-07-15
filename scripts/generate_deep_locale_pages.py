"""Generate locale hub copies for deep sub-pages (tools/*, series/*, digital-nomads/*)."""
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

# Source pages (relative to PAGES_DIR)
SOURCES = [
    # Tools sub-pages
    'tools/app-availability-checker.astro',
    'tools/best-time-to-visit.astro',
    'tools/budget-cash-estimator.astro',
    'tools/clothing-size-converter.astro',
    'tools/currency-converter.astro',
    'tools/esim-comparison.astro',
    'tools/essential-phrases.astro',
    'tools/payment-checker.astro',
    'tools/power-plug-checker.astro',
    'tools/show-to-driver.astro',
    'tools/survival-kit.astro',
    'tools/visa-free-checker.astro',
    # Series sub-pages
    'series/culture-of-china.astro',
    'series/food-of-china.astro',
    'series/history-of-china.astro',
    'series/modern-china.astro',
    'series/nature-of-china.astro',
    # Digital nomad sub-pages
    'digital-nomads/payment.astro',
    'digital-nomads/visa.astro',
    # Author page
    'authors/chinatripbox-editorial-team.astro',
]


def process_file(content, locale_code):
    """Adjust imports and add locale props."""
    # Adjust imports: '../../' → '../../../'
    content = content.replace("from '../../layouts/", "from '../../../layouts/")
    content = content.replace("from '../../components/", "from '../../../components/")
    content = content.replace("from '../../config'", "from '../../../config'")
    content = content.replace("from '../../styles/", "from '../../../styles/")
    content = content.replace("from '../../data/", "from '../../../data/")
    content = content.replace("from '../../assets/", "from '../../../assets/")
    content = content.replace("from '../../images/", "from '../../../images/")

    # Add locale to BaseLayout
    def add_to_tag(match):
        full = match.group(0)
        if 'locale=' in full:
            return full
        if full.endswith('/>'):
            return full[:-2] + f' locale="{locale_code}"/>'
        return full[:-1] + f' locale="{locale_code}">'

    content = re.sub(r'<BaseLayout[^>]*>', add_to_tag, content)
    content = re.sub(r'<GuideLayout[^>]*>', add_to_tag, content)

    # Add locale to Header
    content = re.sub(r'<Header\s*/>', f'<Header locale="{locale_code}" />', content)
    content = re.sub(r'<Header(?!\s+locale)(\s+[^>]*)?>', f'<Header locale="{locale_code}"\\1>', content)

    return content


def generate():
    count = 0
    for locale_dir, locale_code in LOCALES:
        locale_root = os.path.join(PAGES_DIR, locale_dir)
        
        for rel_path in SOURCES:
            src = os.path.join(PAGES_DIR, rel_path)
            if not os.path.exists(src):
                print(f'  SKIP {rel_path} — source not found')
                continue

            with open(src, 'r', encoding='utf-8') as f:
                content = f.read()

            content = process_file(content, locale_code)

            dst = os.path.join(locale_root, rel_path)
            dst_dir = os.path.dirname(dst)
            os.makedirs(dst_dir, exist_ok=True)
            with open(dst, 'w', encoding='utf-8') as f:
                f.write(content)

            count += 1
            print(f'  {locale_dir}/{rel_path}')

    print(f'\nDone: {count} deep locale pages generated')


if __name__ == '__main__':
    generate()
