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
    locales: ['en', 'zh-TW', 'ja', 'ko'],
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
        },
      },
    }),
    mdx(),
  ],
});
