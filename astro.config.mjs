import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  // Production site URL used for sitemap and canonical/SEO absolute links.
  site: 'https://www.chinatripbox.com',
  output: 'static',
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
        // Allow specific zh-tw pages with proven traffic into sitemap
        const allowedZhTw = ['/zh-tw/', '/zh-tw/apps/', '/zh-tw/resources/', '/zh-tw/e-sim/'];
        if (path.startsWith('/zh-tw/')) {
          if (allowedZhTw.includes(path)) return true;
          return false;
        }
        // Keep only released non-English pages; exclude unreleased non-English locales and low-value paths
        const excludedPrefixes = ['/ja/', '/ko/', '/ru/', '/es/', '/authors/'];
        // de-DE, fr-FR released for Google indexing
        if (excludedPrefixes.some((prefix) => path.startsWith(prefix))) return false;
        if (path === '/404' || path === '/404/') return false;
        return true;
      },
    }),
    mdx(),
  ],
});
