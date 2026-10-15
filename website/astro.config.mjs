import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://taskvane.ahsandev.site',
  trailingSlash: 'always',
  integrations: [sitemap()],
  build: { inlineStylesheets: 'always' },
});
