import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const postsDir = join(process.cwd(), 'src', 'content', 'posts');
const strict = process.argv.includes('--strict');
const requiredFields = ['title', 'description', 'pubDate', 'category', 'tags'];
const allowedCategories = new Set(['payment', 'esim', 'transport', 'essentials', 'food']);
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
  return (markdown.match(/\b[A-Za-z][A-Za-z0-9'-]*\b/g) || []).length;
}

const files = readdirSync(postsDir).filter((file) => file.endsWith('.md'));

for (const file of files) {
  const source = readFileSync(join(postsDir, file), 'utf8');
  const { data, body } = parseFrontmatter(source, file);
  const words = wordCount(body);
  const internalLinks = (body.match(/\]\(\/(?!\/)/g) || []).length;
  const externalLinks = (body.match(/\]\(https?:\/\//g) || []).length;
  const headings = (body.match(/^##\s+/gm) || []).length;

  for (const field of requiredFields) {
    if (!data[field]) issues.push(`${file}: missing ${field}`);
  }

  if (data.title && data.title.length > 75) issues.push(`${file}: title is long (${data.title.length} chars)`);
  if (data.description && (data.description.length < 90 || data.description.length > 180)) {
    issues.push(`${file}: description should be 90-180 chars (${data.description.length})`);
  }
  if (data.category && !allowedCategories.has(data.category)) issues.push(`${file}: invalid category ${data.category}`);
  if (words < 900) issues.push(`${file}: thin body (${words} words)`);
  if (headings < 4) issues.push(`${file}: add more section headings (${headings})`);
  if (internalLinks < 3) issues.push(`${file}: add internal links (${internalLinks})`);
  if (data.faqCount < 3) issues.push(`${file}: add at least 3 FAQ entries (${data.faqCount})`);
  if (/TODO|TBD|lorem ipsum|placeholder/i.test(source)) issues.push(`${file}: contains placeholder text`);
  if (externalLinks > 8) issues.push(`${file}: unusually many external links (${externalLinks})`);
}

if (issues.length) {
  const method = strict ? 'error' : 'warn';
  console[method](`Content quality check found ${issues.length} issue(s):`);
  for (const issue of issues) console[method](`- ${issue}`);
  if (strict) process.exit(1);
  console.warn('Report mode only. Use `npm run check:content -- --strict` to fail on these issues.');
  process.exit(0);
}

console.log(`Content quality check passed for ${files.length} post(s).`);
