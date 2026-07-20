#!/usr/bin/env python3
"""Add Thai, Vietnamese, Malay language support to ChinaTripBox"""
import os, re, shutil

NEW = ['th', 'vi', 'ms']
# Config load
cfg_path = 'astro.config.mjs'
bl_path = 'src/layouts/BaseLayout.astro'
cat_path = 'src/i18n/categories.ts'

# --- astro.config.mjs ---
print("=== 1. astro.config.mjs ===")
with open(cfg_path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    "['en', 'zh-TW', 'ja', 'ko', 'ru', 'fr', 'de', 'es']",
    "['en', 'zh-TW', 'ja', 'ko', 'ru', 'fr', 'de', 'es', 'th', 'vi', 'ms']"
)

# Sitemap: find the last locale entry and add new ones
for code in NEW:
    c = c.replace(
        "es: 'es-ES',",
        "es: 'es-ES',\n          {}: '{}',".format(code, code)
    )

with open(cfg_path, 'w', encoding='utf-8') as f:
    f.write(c)
print("  OK")

# --- BaseLayout.astro ---
print("=== 2. BaseLayout.astro ===")
with open(bl_path, 'r', encoding='utf-8') as f:
    b = f.read()

locales_str = "'en' | 'zh-TW' | 'ja' | 'ko' | 'ru' | 'fr' | 'de' | 'es'"
new_locales_str = "'en' | 'zh-TW' | 'ja' | 'ko' | 'ru' | 'fr' | 'de' | 'es' | 'th' | 'vi' | 'ms'"
b = b.replace(locales_str, new_locales_str)

# hreflangCodes
b = b.replace(
    "const hreflangCodes: LocaleCode[] = ['en', 'zh-TW', 'ja', 'ko', 'ru', 'fr', 'de', 'es'];",
    "const hreflangCodes: LocaleCode[] = ['en', 'zh-TW', 'ja', 'ko', 'ru', 'fr', 'de', 'es', 'th', 'vi', 'ms'];"
)
# localePrefixes
b = b.replace(
    "en: '/', 'zh-TW': '/zh-tw/', ja: '/ja/', ko: '/ko/', ru: '/ru/', fr: '/fr/', de: '/de/', es: '/es/'",
    "en: '/', 'zh-TW': '/zh-tw/', ja: '/ja/', ko: '/ko/', ru: '/ru/', fr: '/fr/', de: '/de/', es: '/es/', th: '/th/', vi: '/vi/', ms: '/ms/'"
)
# htmlLangMap
b = b.replace(
    "en: 'en', 'zh-TW': 'zh-TW', ja: 'ja', ko: 'ko', ru: 'ru', fr: 'fr', de: 'de', es: 'es'",
    "en: 'en', 'zh-TW': 'zh-TW', ja: 'ja', ko: 'ko', ru: 'ru', fr: 'fr', de: 'de', es: 'es', th: 'th', vi: 'vi', ms: 'ms'"
)
# Language preference script: LOCALE_PREFIXES
b = b.replace(
    "var LOCALE_PREFIXES=['zh-tw','ja','ko','ru','fr','de','es'];",
    "var LOCALE_PREFIXES=['zh-tw','ja','ko','ru','fr','de','es','th','vi','ms'];"
)

with open(bl_path, 'w', encoding='utf-8') as f:
    f.write(b)
print("  OK")

# --- categories.ts ---
print("=== 3. categories.ts ===")
with open(cat_path, 'r', encoding='utf-8') as f:
    ca = f.read()

ca = ca.replace(
    "export type LocaleCode = 'en' | 'zh-tw' | 'ja' | 'ko' | 'ru' | 'fr' | 'de' | 'es';",
    "export type LocaleCode = 'en' | 'zh-tw' | 'ja' | 'ko' | 'ru' | 'fr' | 'de' | 'es' | 'th' | 'vi' | 'ms';"
)

# Add placeholder entries. The user needs to fill in actual translations later.
for lang in ['th', 'vi', 'ms']:
    for cat_name in ['payment', 'esim', 'transport', 'essentials', 'food']:
        # Find the closing brace for this category
        search = "{}: {{".format(cat_name)
        pos = ca.find(search)
        if pos < 0:
            continue
        end_brace = ca.find('}', pos)
        if end_brace < 0:
            continue
        # Insert before closing }
        old = ca[end_brace:end_brace+1]
        new = ",  {}: '{}'".format(lang, cat_name) + old
        ca = ca[:end_brace] + new + ca[end_brace+1:]

with open(cat_path, 'w', encoding='utf-8') as f:
    f.write(ca)
print("  OK (stub entries)")

# --- Create page directories ---
print("=== 4. Create page dirs ===")
REF = 'zh-tw'
for code in NEW:
    dst = 'src/pages/{}'.format(code)
    if os.path.exists(dst):
        print("  {} exists".format(code))
        continue
    os.makedirs(dst, exist_ok=True)
    src_dir = 'src/pages/{}'.format(REF)
    for item in os.listdir(src_dir):
        item_path = os.path.join(src_dir, item)
        if os.path.isdir(item_path):
            shutil.copytree(item_path, os.path.join(dst, item), dirs_exist_ok=True)
    print("  {} created".format(code))

print("\n=== DONE ===")
