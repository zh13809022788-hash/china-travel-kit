import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  // Production site URL used for sitemap and canonical/SEO absolute links.
  site: 'https://www.chinatripbox.com',
  output: 'static',
  build: {
    assets: 'assets',
  },
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh-TW', 'ja', 'ko', 'ru', 'fr', 'de', 'es'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
  integrations: [
    tailwind({
      applyBaseStyles: false,
    }),
    sitemap({
      i18n: {
        defaultLocale: 'en',
        locales: {
          en: 'en-US',
          'zh-TW': 'zh-TW',
          ja: 'ja-JP',
          ko: 'ko-KR',
          ru: 'ru-RU',
          fr: 'fr-FR',
          de: 'de-DE',
          es: 'es-ES',
        },
      },
      filter: (page) => {
        const url = new URL(page);
        const path = url.pathname;
        // All locales released - only exclude low-value paths
        // Keep only released non-English pages; exclude low-value paths
        const excludedPrefixes = ['/authors/'];
        // All 7 non-English locales confirmed 100% native - released for Google indexing
        if (excludedPrefixes.some((prefix) => path.startsWith(prefix))) return false;
        if (path === '/404' || path === '/404/' || path.endsWith('/404/') || path.endsWith('/404')) return false;
        return true;
      },
    }),
    mdx(),
  ],
});
