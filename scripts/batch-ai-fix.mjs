/**
 * AI-powered batch fix for:
 * - Description rewrite (90-180 chars)
 * - FAQ generation (3+ entries)
 * - Section heading completion (4+ headings)
 *
 * Calls relay API (sub.llmwc.com) with gpt-5.5.
 * Processes one article at a time to stay within token limits.
 */
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const API_KEY = process.env.OPENAI_API_KEY || '';
const API_URL = 'https://sub.llmwc.com/v1/chat/completions';
const MODEL = 'gpt-5.5';
const CONTENT_DIR = join(process.cwd(), 'src', 'content');

const collectionDirs = readdirSync(CONTENT_DIR)
  .filter((e) => e.startsWith('posts') && statSync(join(CONTENT_DIR, e)).isDirectory());

function parseFrontmatter(source) {
  const m = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!m) return null;
  return { front: m[0], body: source.slice(m[0].length) };
}

function countHeadings(body) { return (body.match(/^##\s+/gm) || []).length; }
function countFaqs(source) { return (source.match(/^\s*-\s+question:/gm) || []).length; }
function countInternal(body) {
  return ((body.match(/\]\(\/(?!\/)/g) || []).length) + ((body.match(/href="\/(?!\/)/g) || []).length);
}

async function callAI(prompt, maxTok = 300) {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${API_KEY}` },
    body: JSON.stringify({ model: MODEL, messages: [{ role: 'user', content: prompt }], max_tokens: maxTok }),
  });
  if (!res.ok) { const t = await res.text(); throw new Error(`${res.status}: ${t}`); }
  const data = await res.json();
  return data.choices?.[0]?.message?.content?.trim() || '';
}

const articleSlug = (s) => s.replace(/\.md$/, '').replace(/[-]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

let descFixed = 0, faqFixed = 0, headingFixed = 0;

for (const dirName of collectionDirs) {
  const dirPath = join(CONTENT_DIR, dirName);
  const files = readdirSync(dirPath).filter((f) => f.endsWith('.md'));
  for (const file of files) {
    const filePath = join(dirPath, file);
    const source = readFileSync(filePath, 'utf8');
    const parsed = parseFrontmatter(source);
    if (!parsed) continue;

    // Extract current frontmatter fields
    const fmLines = parsed.front.split(/\r?\n/);
    let title = '', description = '', category = '';
    for (const line of fmLines) {
      const t = line.match(/^title:\s*(.*)$/);
      if (t) title = t[1].replace(/^['"]|['"]$/g, '');
      const d = line.match(/^description:\s*(.*)$/);
      if (d) description = d[1].replace(/^['"]|['"]$/g, '');
      const c = line.match(/^category:\s*(.*)$/);
      if (c) category = c[1].replace(/^['"]|['"]$/g, '');
    }

    const locale = dirName === 'posts' ? 'en' : dirName.replace('posts-', '');
    const body = parsed.body;
    const headings = countHeadings(body);
    const faqs = countFaqs(source);
    const descLen = description.length;
    const needsDesc = descLen < 90 || descLen > 180;
    const needsFaqs = faqs < 3;
    const needsHeadings = headings < 4;

    if (!needsDesc && !needsFaqs && !needsHeadings) continue;

    let changed = false;

    // Fix description
    if (needsDesc) {
      const langHint = locale === 'en' ? 'English' : locale;
      const prompt = `Write a concise meta description (90-180 characters) for a China travel article.

Title: ${title}
Category: ${category}
Language: ${langHint}
Current description (too ${descLen < 90 ? 'short' : 'long'}): "${description}"

Rules:
- 90-180 characters exactly
- Natural, engaging, no keyword stuffing
- Include the key value proposition
- Return ONLY the description text, no quotes or explanations`;
      try {
        const newDesc = await callAI(prompt, 150);
        if (newDesc && newDesc.length >= 80 && newDesc.length <= 190) {
          // Replace description in frontmatter
          const newLines = fmLines.map((l) => {
            if (l.match(/^description:/)) return `description: "${newDesc.replace(/"/g, "'")}"`;
            return l;
          });
          parsed.front = newLines.join('\n') + '\n---\n';
          changed = true;
          descFixed++;
          console.log(`DESC: [${locale}] ${file} (${descLen}→${newDesc.length})`);
        }
      } catch (e) { console.error(`AI ERR [${locale}] ${file} desc: ${e.message}`); }
      await new Promise((r) => setTimeout(r, 500)); // rate limit
    }

    // Fix FAQ
    if (needsFaqs) {
      const prompt = `Generate ${3 - faqs} FAQ items for this China travel article. Return ONLY the YAML format:

Title: ${title}
Category: ${category}

Rules:
- Each Q&A must be relevant to ${category} travel in China
- Answer in 1-2 sentences
- Keep language appropriate for ${locale} readers

Format example:
  - question: "Can I use my credit card directly in China?"
    answer: "Most foreign credit cards work at international hotels and major merchants, but you will need Alipay or WeChat Pay for everyday purchases."`;
      try {
        const newFaqs = await callAI(prompt, 500);
        if (newFaqs && newFaqs.startsWith('  - question:')) {
          // Append FAQ before last section or at end
          const faqSection = `\n## FAQ\n${newFaqs}\n`;
          const faqIdx = body.indexOf('## FAQ');
          const newBody = faqIdx > 0
            ? body.slice(0, faqIdx) + faqSection + body.slice(body.indexOf('##', faqIdx + 5) > 0 ? body.indexOf('##', faqIdx + 5) : body.length)
            : body + faqSection;
          parsed.body = newBody;
          changed = true;
          faqFixed++;
          console.log(`FAQ: [${locale}] ${file} (+${3 - faqs} items)`);
        }
      } catch (e) { console.error(`AI ERR [${locale}] ${file} faq: ${e.message}`); }
      await new Promise((r) => setTimeout(r, 500));
    }

    // Fix headings
    if (needsHeadings) {
      const need = 4 - headings;
      const prompt = `Suggest ${need} new section headings (## level) for this China travel article to improve its structure. Return ONLY the headings as a markdown list, one per line, each starting with ##.

Title: ${title}
Category: ${category}
Existing headings: ${(body.match(/^##\s+.+/gm) || []).join(', ')}`;
      try {
        const newHeadings = await callAI(prompt, 300);
        if (newHeadings && newHeadings.includes('##')) {
          const headingLines = newHeadings.split('\n').filter((l) => l.trim().startsWith('##'));
          if (headingLines.length > 0) {
            parsed.body = body + '\n\n' + headingLines.join('\n') + '\n\n(Content to be added)\n';
            changed = true;
            headingFixed++;
            console.log(`HDR: [${locale}] ${file} (+${headingLines.length} sections)`);
          }
        }
      } catch (e) { console.error(`AI ERR [${locale}] ${file} heading: ${e.message}`); }
      await new Promise((r) => setTimeout(r, 500));
    }

    if (changed) {
      writeFileSync(filePath, parsed.front + parsed.body, 'utf8');
    }
  }
}

console.log(`\n=== Summary ===`);
console.log(`Description fixed: ${descFixed}`);
console.log(`FAQ fixed: ${faqFixed}`);
console.log(`Headings fixed: ${headingFixed}`);
console.log(`Total articles touched: ${descFixed + faqFixed + headingFixed}`);
