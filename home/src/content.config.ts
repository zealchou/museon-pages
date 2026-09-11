import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ base: './src/content/blog', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(), description: z.string(), publishDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    category: z.object({ name: z.string(), slug: z.string().regex(/^[a-z0-9-]+$/) }),
    draft: z.boolean().default(true),
    hero: z.object({ src: z.string(), alt: z.string().min(1) }).optional()
  }).refine(({ publishDate, updatedDate }) => !updatedDate || updatedDate >= publishDate)
});

export const collections = { blog };
