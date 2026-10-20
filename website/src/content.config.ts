import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const guides = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/guides' }),
  schema: z.object({
    title: z.string(),
    seoTitle: z.string().max(65),
    description: z.string().min(120).max(160),
    targetQuery: z.string(),
    published: z.coerce.date(),
    updated: z.coerce.date(),
    promise: z.string(),
    related: z.array(z.string()).default([]),
    compare: z.enum(['task-manager', 'hwinfo', 'librehardwaremonitor']).optional(),
    faq: z.array(
      z.object({
        q: z.string(),
        a: z.string(),
      })
    ),
  }),
});

export const collections = { guides };
