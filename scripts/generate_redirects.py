"""Generate language-prefixed redirect pages for hub and static pages.
Each file at /ja/payment/index.html will meta-refresh to /payment/
keeping the user in their language context."""

import os

PROJECT_ROOT = r'D:\独立站\china-travel-kit'
PAGES_DIR = os.path.join(PROJECT_ROOT, 'src', 'pages')

# Locales and their URL prefix directories
LOCALES = {
    'zh-tw': 'zh-TW',
    'ja': 'ja',
    'ko': 'ko',
    'ru': 'ru',
    'fr': 'fr',
    'de': 'de',
    'es': 'es',
}

# Pages that need redirects (hub pages + static pages that are English-only)
REDIRECT_PAGES = [
    'payment',
    'esim',
    'transport',
    'food',
    'essentials',
    'cities',
    'series',
    'tools',
    'apps',
    'resources',
    'trip-planner',
    'travel-help',
    'about',
    'privacy',
    'terms',
    'contact',
    'editorial-policy',
    'affiliate-disclosure',
    'long-stay',
    'digital-nomads',
]

# HTML template with meta refresh redirect
HTML_TEMPLATE = """<!doctype html>
<html lang="{locale_html}">
<head>
  <meta charset="utf-8">
  <title>Redirecting...</title>
  <meta http-equiv="refresh" content="0; url=/">
  <link rel="canonical" href="/">
</head>
<body>
  <p>Redirecting to <a href="/">homepage</a>...</p>
</body>
</html>
"""

def generate_redirects():
    count = 0
    for locale_dir, locale_code in LOCALES.items():
        locale_html = locale_code  # e.g. 'zh-TW'
        
        for page in REDIRECT_PAGES:
            # Create directory: src/pages/{locale}/{page}/
            dir_path = os.path.join(PAGES_DIR, locale_dir, page)
            os.makedirs(dir_path, exist_ok=True)
            
            # Write index.astro file with Astro redirect
            astro_content = f"""---
const target = '/{page}/';
const localeCode = '{locale_code}';
const localeHtml = '{locale_html}';
const pageTitle = '{page}';
---

<!doctype html>
<html lang="{{localeHtml}}">
<head>
  <meta charset="utf-8">
  <title>Chinatripbox</title>
  <meta http-equiv="refresh" content="0; url={{target}}">
  <link rel="canonical" href="{{target}}">
</head>
<body>
  <p>Redirecting to <a href="{{target}}">Chinatripbox</a>...</p>
</body>
</html>
"""
            
            file_path = os.path.join(dir_path, 'index.astro')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(astro_content)
            
            count += 1
            print(f'  {locale_dir}/{page}/ → /{page}/')
    
    print(f'\nTotal: {count} redirect pages created')

if __name__ == '__main__':
    generate_redirects()
