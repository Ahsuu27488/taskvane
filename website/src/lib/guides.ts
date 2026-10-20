import { getCollection } from 'astro:content';

// Scheduled publishing: a guide goes live on its `published` date. Future-dated guides aren't
// built at all (no page, sitemap entry, llms.txt line or link). website.yml rebuilds the site
// every morning, so a scheduled guide appears on its day without anyone pushing.
// GUIDES_NOW=2026-10-24 builds the site as it will look on that day (for testing).
export const NOW = process.env.GUIDES_NOW ? new Date(process.env.GUIDES_NOW) : new Date();

/** Live guides, newest first. */
export async function liveGuides() {
  return (await getCollection('guides', (g) => g.data.published.getTime() <= NOW.getTime()))
    .sort((a, b) => b.data.published.getTime() - a.data.published.getTime());
}

/** Whether the guide with this slug is live (for hand-written links on other pages). */
export async function isLive(slug: string) {
  return (await liveGuides()).some((g) => g.id === slug);
}
