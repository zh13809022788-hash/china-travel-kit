import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  // Production site URL used for sitemap and canonical/SEO absolute links.
  site: 'https://www.chinatripbox.com',
  output: 'static',
  integrations: [
    tailwind({
      // We provide our own base styles in src/styles/global.css
      applyBaseStyles: false,
    }),
    sitemap(),
    mdx(),
  ],
});
