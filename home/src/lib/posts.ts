import { getCollection } from 'astro:content';

export async function getVisiblePosts(includeDrafts = import.meta.env.DEV) {
  return (await getCollection('blog'))
    .filter(({ data }) => includeDrafts || !data.draft)
    .sort((a, b) => b.data.publishDate.valueOf() - a.data.publishDate.valueOf());
}
