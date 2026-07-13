import { getCollection } from 'astro:content';
import { TOOLS } from '../config';

const site = 'https://www.chinatripbox.com';

const corePages = [
  ['Home', '/'],
  ['Resources', '/resources/'],
  ['Trip Planner', '/trip-planner/'],
  ['Travel Help', '/travel-help/'],
  ['Payment Hub', '/payment/'],
  ['eSIM Hub', '/esim/'],
  ['Transport Hub', '/transport/'],
  ['Tools', '/tools/'],
  ['Cities', '/cities/'],
  ['Food', '/food/'],
  ['Affiliate Disclosure', '/affiliate-disclosure/'],
];

export async function GET() {
  const posts = await getCollection('posts');
  const sortedPosts = posts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
  const featuredPosts = sortedPosts.filter((post) => post.data.featured).slice(0, 12);
  const latestPosts = sortedPosts.slice(0, 12);

  const lines = [
    '# ChinaTripBox',
    '',
    '> Practical China travel planning guides and tools for foreign visitors, focused on payments, eSIMs, transport, apps, first-day setup, city planning, and everyday travel logistics.',
    '',
    '## Core Pages',
    ...corePages.map(([title, path]) => `- [${title}](${site}${path})`),
    '',
    '## Featured Guides',
    ...featuredPosts.map((post) => `- [${post.data.title}](${site}/posts/${post.slug}/): ${post.data.description}`),
    '',
    '## Latest Guides',
    ...latestPosts.map((post) => `- [${post.data.title}](${site}/posts/${post.slug}/): ${post.data.description}`),
    '',
    '## Interactive Tools',
    ...TOOLS.map((tool) => `- [${tool.title}](${site}${tool.href}): ${tool.desc}`),
    '',
    '## Editorial Scope',
    '- General travel information only, not legal, immigration, medical, banking, emergency, or official government advice.',
    '- Content is written for foreign visitors who need practical setup help before and during a China trip.',
  ];

  return new Response(`${lines.join('\n')}\n`, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
}
