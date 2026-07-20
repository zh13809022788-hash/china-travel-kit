/**
 * AI fix for description issues in specific locales only.
 * Targets: zh-tw, ja, ko (remaining 75 description issues)
 */
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const API_KEY = process.env.OPENAI_API_KEY || '';
const API_URL = 'https://sub.llmwc.com/v1/chat/completions';
const MODEL = 'gpt-5.5';
const CONTENT_DIR = join(process.cwd(), 'src', 'content');
const TARGET_LOCALES = ['zh-tw', 'ja', 'ko'];

const collectionDirs = readdirSync(CONTENT_DIR)
  .filter((e) => e.startsWith('posts') && statSync(join(CONTENT_DIR, e)).isDirectory());

async function callAI(prompt) {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${API_KEY}` },
    body: JSON.stringify({ model: MODEL, messages: [{ role: 'user', content: prompt }], max_tokens: 150 }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.choices?.[0]?.message?.content?.trim() || '';
}

let fixed = 0;

for (const dirName of collectionDirs) {
  const locale = dirName === 'posts' ? 'en' : dirName.replace('posts-', '');
  if (!TARGET_LOCALES.includes(locale)) continue;

  const dirPath = join(CONTENT_DIR, dirName);
  const files = readdirSync(dirPath).filter((f) => f.endsWith('.md'));

  for (const file of files) {
    const filePath = join(dirPath, file);
    const source = readFileSync(filePath, 'utf8');
    const m = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
    if (!m) continue;

    const lines = m[1].split(/\r?\n/);
    let title = '', description = '', changed = false;
    for (const l of lines) {
      const t = l.match(/^title:\s*(.*)$/); if (t) title = t[1].replace(/^['"]|['"]$/g, '');
      const d = l.match(/^description:\s*(.*)$/); if (d) description = d[1].replace(/^['"]|['"]$/g, '');
    }
    if (description.length >= 90 && description.length <= 180) continue;

    const langHint = { 'zh-tw': 'Traditional Chinese', ja: 'Japanese', ko: 'Korean' }[locale] || locale;
    const prompt = `Write a meta description (90-180 characters) for a China travel article.
Title: ${title}
Language: ${langHint}
Rules: 90-180 chars, natural, no quotes. Return ONLY the description text.`;

    try {
      const nd = await callAI(prompt);
      if (nd && nd.length >= 80 && nd.length <= 190) {
        const newLines = lines.map((l) => l.match(/^description:/) ? `description: "${nd.replace(/"/g, "'")}"` : l);
        const newContent = '---\n' + newLines.join('\n') + '\n---\n' + source.slice(m[0].length);
        writeFileSync(filePath, newContent, 'utf8');
        fixed++;
        console.log(`DESC: [${locale}] ${file} (${description.length}->${nd.length})`);
      }
    } catch (e) { console.error(`ERR: [${locale}] ${file}: ${e.message}`); }
    await new Promise((r) => setTimeout(r, 800));
  }
}
console.log(`\nDone. ${fixed} description(s) fixed.`);
