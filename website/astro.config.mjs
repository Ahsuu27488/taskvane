import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';

// Scheduled guides (see src/lib/guides.ts): after the build, any link to a guide that isn't
// live yet becomes plain text, on every page, so nothing links to a guide before its day.
const NOW = process.env.GUIDES_NOW ? new Date(process.env.GUIDES_NOW) : new Date();
const guidesDir = new URL('./src/content/guides/', import.meta.url);
const scheduled = readdirSync(guidesDir)
  .filter((f) => f.endsWith('.md'))
  .filter((f) => {
    const m = /^published:\s*(\S+)/m.exec(readFileSync(new URL(f, guidesDir), 'utf8'));
    return m && new Date(m[1]).getTime() > NOW.getTime();
  })
  .map((f) => f.slice(0, -3));

const unlinkScheduledGuides = {
  name: 'unlink-scheduled-guides',
  hooks: {
    'astro:build:done': ({ dir }) => {
      if (!scheduled.length) return;
      const link = new RegExp(`<a href="/guides/(?:${scheduled.join('|')})/"[^>]*>(.*?)</a>`, 'gs');
      const walk = (d) => {
        for (const e of readdirSync(d, { withFileTypes: true })) {
          const p = join(d, e.name);
          if (e.isDirectory()) walk(p);
          else if (e.name.endsWith('.html')) {
            const html = readFileSync(p, 'utf8');
            const out = html.replace(link, '$1');
            if (out !== html) writeFileSync(p, out);
          }
        }
      };
      walk(fileURLToPath(dir));
    },
  },
};

export default defineConfig({
  site: 'https://taskvane.ahsandev.site',
  trailingSlash: 'always',
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/sitemap.xml'),
    }),
    unlinkScheduledGuides,
  ],
  build: { inlineStylesheets: 'always' },
});
