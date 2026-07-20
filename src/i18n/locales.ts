/**
 * Shared locale configuration — single source of truth.
 * Import from here instead of hardcoding in BaseLayout.astro.
 */
export type LocaleCode = 'en' | 'zh-TW' | 'ja' | 'ko' | 'ru' | 'fr' | 'de' | 'es' | 'th' | 'vi' | 'ms';

export const ALL_LOCALES: LocaleCode[] = [
  'en', 'zh-TW', 'ja', 'ko', 'ru', 'fr', 'de', 'es', 'th', 'vi', 'ms',
];

export const HTML_LANG_MAP: Record<LocaleCode, string> = {
  en: 'en', 'zh-TW': 'zh-TW', ja: 'ja', ko: 'ko', ru: 'ru',
  fr: 'fr', de: 'de', es: 'es', th: 'th', vi: 'vi', ms: 'ms',
};

export const LOCALE_PREFIXES: Record<LocaleCode, string> = {
  en: '/', 'zh-TW': '/zh-tw/', ja: '/ja/', ko: '/ko/', ru: '/ru/',
  fr: '/fr/', de: '/de/', es: '/es/', th: '/th/', vi: '/vi/', ms: '/ms/',
};

export const NOINDEX_LOCALES: LocaleCode[] = ['zh-TW', 'ja', 'ko', 'ru', 'fr', 'de', 'es', 'th', 'vi', 'ms'];

export const SITEMAP_EXCLUDED_PREFIXES = [
  '/authors/',
  '/zh-tw/', '/ja/', '/ko/', '/ru/',
  '/fr/', '/de/', '/es/', '/th/', '/vi/', '/ms/',
];
