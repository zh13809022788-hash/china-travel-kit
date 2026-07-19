/**
 * build-search-index.mjs
 *
 * Scans all 8 language content directories, extracts frontmatter from each markdown file,
 * and generates a structured search index at public/search-index.json.
 *
 * The search index is used by the ContextAiBubble (floating assistant) to answer
 * visitor questions locally — no API tokens consumed for the common case.
 *
 * Runs automatically via "prebuild" in package.json before every `npm run build`.
 */

import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { resolve, basename, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, '..');

// Language → content directory mapping
const LANG_DIRS = {
  en:     'src/content/posts',
  'zh-tw': 'src/content/posts-zh-tw',
  ja:     'src/content/posts-ja',
  ko:     'src/content/posts-ko',
  ru:     'src/content/posts-ru',
  fr:     'src/content/posts-fr',
  de:     'src/content/posts-de',
  es:     'src/content/posts-es',
};

// Fallback category keywords for matching
const CATEGORY_KEYWORDS = {
  payment:    ['payment', '支付宝', 'alipay', 'wechat', '微信', '支付', 'cash', '现金', 'credit card', '信用卡'],
  esim:       ['esim', 'eSIM', 'sim', '手机卡', '手机号', '联通', '移动', '电信', 'data', 'internet', '网络', 'roaming', 'wifi'],
  transport:  ['transport', 'transit', 'train', '高铁', 'metro', '地铁', 'didi', '滴滴', 'airport', 'taxi', 'bus'],
  essentials: ['essentials', 'visa', '签证', 'insurance', '保险', 'passport', '护照', 'packing', 'tipping', 'first day', 'checklist'],
  food:       ['food', '餐厅', 'restaurant', 'cooking', 'dining', 'street food', 'delivery'],
};

/**
 * Simple frontmatter parser — no dependencies needed.
 */
function parseFrontmatter(filePath) {
  const raw = readFileSync(filePath, 'utf-8');
  const fm = {};
  const lines = raw.split('\n');

  // Find frontmatter boundaries
  if (lines[0]?.trim() !== '---') return fm;

  let endIdx = -1;
  for (let i = 1; i < Math.min(lines.length, 120); i++) {
    if (lines[i].trim() === '---') { endIdx = i; break; }
  }
  if (endIdx === -1) return fm;

  // Parse key-value pairs (simple, no nested YAML)
  for (let i = 1; i < endIdx; i++) {
    const line = lines[i].trim();
    const colonIdx = line.indexOf(':');
    if (colonIdx === -1) continue;

    const key = line.slice(0, colonIdx).trim();
    let value = line.slice(colonIdx + 1).trim();

    // Remove surrounding quotes
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }

    // Handle array values like tags: ["a", "b"]
    if (value.startsWith('[') && value.endsWith(']')) {
      try {
        value = JSON.parse(value);
      } catch { /* keep as string */ }
    }

    fm[key] = value;
  }

  return fm;
}

/**
 * Build a searchable index entry from a markdown file.
 */
function buildEntry(lang, slug, dir) {
  const filePath = resolve(PROJECT_ROOT, dir, `${slug}.md`);
  if (!existsSync(filePath)) return null;

  const fm = parseFrontmatter(filePath);

  // URL per language convention
  const url = lang === 'en'
    ? `/posts/${slug}/`
    : `/${lang}/posts/${slug}/`;

  const tags = Array.isArray(fm.tags) ? fm.tags
    : typeof fm.tags === 'string' ? fm.tags.split(',').map(t => t.trim().replace(/^\[|\]$/g, '').replace(/^"|"$/g, ''))
    : [];

  const category = fm.category || '';

  return {
    slug,
    url,
    title: fm.title || slug,
    description: fm.description || '',
    category: typeof category === 'string' ? category : '',
    tags: tags.filter(Boolean),
    pubDate: fm.pubDate ? String(fm.pubDate).split('T')[0] : '',
  };
}

function main() {
  const index = {};

  for (const [lang, dir] of Object.entries(LANG_DIRS)) {
    const fullDir = resolve(PROJECT_ROOT, dir);
    if (!existsSync(fullDir)) {
      console.warn(`  ⚠  Directory not found: ${dir}`);
      continue;
    }

    const files = readdirSync(fullDir).filter(f => f.endsWith('.md'));
    const entries = files
      .map(f => buildEntry(lang, basename(f, '.md'), dir))
      .filter(Boolean)
      .sort((a, b) => (a.pubDate > b.pubDate ? -1 : 1));

    index[lang] = entries;
    console.log(`  ${lang.padEnd(6)} ${entries.length} articles`);
  }

  const total = Object.values(index).reduce((sum, arr) => sum + arr.length, 0);
  const outputPath = resolve(PROJECT_ROOT, 'public', 'search-index.json');
  writeFileSync(outputPath, JSON.stringify(index, null, 0), 'utf-8');
  console.log(`\n✓ search-index.json written (${total} entries across ${Object.keys(index).length} languages)`);
}

main();
