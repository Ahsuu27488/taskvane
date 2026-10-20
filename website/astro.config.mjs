import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://taskvane.ahsandev.site',
  trailingSlash: 'always',
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/sitemap.xml'),
    }),
  ],
  build: { inlineStylesheets: 'always' },
});
