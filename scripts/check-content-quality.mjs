import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const contentDir = join(process.cwd(), 'src', 'content');
const strict = process.argv.includes('--strict');
const requiredFields = ['title', 'description', 'pubDate', 'category', 'tags'];
const allowedCategories = new Set(['payment', 'esim', 'transport', 'essentials', 'food']);

// Discover every posts-* collection directory (en, zh-tw, ja, ko, ru, fr, de, es, th, ms, vi).
const collectionDirs = readdirSync(contentDir)
  .filter((entry) => entry.startsWith('posts'))
  .filter((entry) => statSync(join(contentDir, entry)).isDirectory())
  .sort();

if (collectionDirs.length === 0) {
  console.error('No posts-* collections found in', contentDir);
  process.exit(1);
}

const localeLabel = (dirName) => (dirName === 'posts' ? 'en' : dirName.replace(/^posts-/, ''));

const issues = [];

function parseFrontmatter(source, file) {
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) {
    issues.push(`${file}: missing frontmatter block`);
    return { data: {}, body: source };
  }

  const data = {};
  const lines = match[1].split(/\r?\n/);
  let inFaqs = false;
  let faqCount = 0;

  for (const line of lines) {
    if (/^faqs:\s*$/.test(line)) {
      inFaqs = true;
      continue;
    }
    if (inFaqs && /^\s*-\s+question:/.test(line)) faqCount += 1;
    if (!line.startsWith(' ') && /^\w+:/.test(line)) inFaqs = false;

    const field = line.match(/^([A-Za-z][A-Za-z0-9_]*):\s*(.*)$/);
    if (field) data[field[1]] = field[2].replace(/^['"]|['"]$/g, '').trim();
  }

  data.faqCount = faqCount;
  return { data, body: source.slice(match[0].length) };
}

function wordCount(markdown) {
  // Word boundary that also matches CJK characters as individual "words".
  const cjk = markdown.match(/[\u3400-\u9fff\uf900-\ufaff]/g) || [];
  const latin = (markdown.match(/\b[A-Za-z][A-Za-z0-9'-]*\b/g) || []).length;
  return cjk.length + latin;
}

let totalFiles = 0;
let filesByLocale = {};

for (const dirName of collectionDirs) {
  const dirPath = join(contentDir, dirName);
  const files = readdirSync(dirPath).filter((file) => file.endsWith('.md'));
  const locale = localeLabel(dirName);
  filesByLocale[locale] = files.length;
  totalFiles += files.length;

  for (const file of files) {
    const source = readFileSync(join(dirPath, file), 'utf8');
    const tag = `[${locale}] ${file}`;
    const { data, body } = parseFrontmatter(source, tag);
    const words = wordCount(body);
    const mdLinks = (body.match(/\]\(\/(?!\/)/g) || []).length;
    const htmlLinks = (body.match(/href="\/(?!\/)/g) || []).length;
    const internalLinks = mdLinks + htmlLinks;
    const externalLinks = (body.match(/\]\(https?:\/\//g) || []).length;
    const headings = (body.match(/^##\s+/gm) || []).length;

    for (const field of requiredFields) {
      if (!data[field]) issues.push(`${tag}: missing ${field}`);
    }

    if (data.title && data.title.length > 75) issues.push(`${tag}: title is long (${data.title.length} chars)`);
    if (data.description && (data.description.length < 90 || data.description.length > 180)) {
      issues.push(`${tag}: description should be 90-180 chars (${data.description.length})`);
    }
    if (data.category && !allowedCategories.has(data.category)) issues.push(`${tag}: invalid category ${data.category}`);
    if (words < 900) issues.push(`${tag}: thin body (${words} words)`);
    if (headings < 4) issues.push(`${tag}: add more section headings (${headings})`);
    if (internalLinks < 3) issues.push(`${tag}: add internal links (${internalLinks})`);
    if (data.faqCount < 3) issues.push(`${tag}: add at least 3 FAQ entries (${data.faqCount})`);
    if (/TODO|TBD|lorem ipsum|placeholder/i.test(source)) issues.push(`${tag}: contains placeholder text`);
    if (externalLinks > 8) issues.push(`${tag}: unusually many external links (${externalLinks})`);
  }
}

const summary = collectionDirs.map((d) => `${localeLabel(d)}=${filesByLocale[localeLabel(d)] ?? 0}`).join(' ');

if (issues.length) {
  const method = strict ? 'error' : 'warn';
  console[method](`Content quality check found ${issues.length} issue(s) across ${totalFiles} post(s) [${summary}]:`);
  for (const issue of issues) console[method](`- ${issue}`);
  if (strict) process.exit(1);
  console.warn('Report mode only. Use `npm run check:content -- --strict` to fail on these issues.');
  process.exit(0);
}

console.log(`Content quality check passed for ${totalFiles} post(s) across ${collectionDirs.length} locale(s) [${summary}].`);
