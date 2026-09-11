import rss from '@astrojs/rss';
import { getVisiblePosts } from '../../lib/posts';

export async function GET(context) {
  const posts = await getVisiblePosts();
  return rss({
    title: 'Museon AI/OS 部落格', description: '周逸達在 Museon 的文章正本。', site: context.site,
    items: posts.map((post) => ({ title: post.data.title, description: post.data.description, pubDate: post.data.publishDate, link: `/blog/${post.id.replace(/\.md$/, '')}/` }))
  });
}
