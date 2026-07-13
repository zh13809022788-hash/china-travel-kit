import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const categorySchema = z.enum(['payment', 'esim', 'transport', 'essentials', 'food']);
const seriesSchema = z.enum([
  'food-of-china',
  'history-of-china',
  'modern-china',
  'nature-of-china',
  'culture-of-china',
]);
const faqSchema = z.object({ question: z.string(), answer: z.string() });

const posts = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    category: categorySchema,
    series: seriesSchema.optional(),
    tags: z.array(z.string()).default([]),
    featured: z.boolean().default(false),
    faqs: z.array(faqSchema).default([]),
    cover: z.string().optional(),
    coverAlt: z.string().optional(),
  }),
});

const postsZhTw = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    category: categorySchema,
    series: seriesSchema.optional(),
    tags: z.array(z.string()).default([]),
    featured: z.boolean().default(false),
    faqs: z.array(faqSchema).default([]),
    cover: z.string().optional(),
    coverAlt: z.string().optional(),
  }),
});

const dataPipelinePages = defineCollection({
  loader: glob({
    base: './data_pipeline/pages',
    pattern: '**/*.json',
    generateId: ({ data, entry }) => {
      if (typeof data.slug === 'string' && data.slug.trim()) {
        return data.slug.trim().replace(/^\/+|\/+$/g, '');
      }

      return entry.replace(/\.json$/i, '').replace(/\\/g, '/');
    },
  }),
  schema: z.object({
    slug: z.string().optional(),
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    category: categorySchema,
    series: seriesSchema.optional(),
    tags: z.array(z.string()).default([]),
    featured: z.boolean().default(false),
    cover: z.string().optional(),
    coverAlt: z.string().optional(),
    summary: z.array(z.string()).default([]),
    sections: z
      .array(
        z.object({
          heading: z.string(),
          body: z.array(z.string()).default([]),
          bullets: z.array(z.string()).default([]),
        })
      )
      .default([]),
    faqs: z.array(faqSchema).default([]),
  }),
});

export const collections = { posts, 'posts-zh-tw': postsZhTw, dataPipelinePages };
