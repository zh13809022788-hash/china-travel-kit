/**
 * batch-translate.mjs
 * Translates 4 new articles into ja, ko, zh-tw via the relay API.
 * Usage: OPENAI_API_KEY=sk-xxx node batch-translate.mjs
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';

const API_KEY = process.env.OPENAI_API_KEY;
const BASE_URL = 'https://sub.llmwc.com/v1';
const MODEL = 'gpt-5.5';

if (!API_KEY) {
  console.error('ERROR: OPENAI_API_KEY env var required');
  process.exit(1);
}

const ARTICLES = [
  'china-apps-checklist-tourists',
  'china-visa-free-transit-240-hour-guide',
  'best-china-esim-for-iphone-users-2026',
  'china-tourist-visa-application-guide-2026',
];

const LOCALES = [
  { code: 'ja', dir: 'posts-ja', lang: 'Japanese', label: '日本語' },
  { code: 'ko', dir: 'posts-ko', lang: 'Korean', label: '한국어' },
  { code: 'zh-tw', dir: 'posts-zh-tw', lang: 'Traditional Chinese', label: '繁體中文' },
];

const CONTENT_DIR = 'D:/独立站/china-travel-kit/src/content';

function parseFrontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!m) return null;
  const fm = {};
  const lines = m[1].split('\n');
  let currentKey = null;
  let currentValue = [];
  let inFaq = false;
  let faqList = [];
  let currentFaq = {};

  for (const line of lines) {
    const keyMatch = line.match(/^(\w+):\s*(.*)/);
    const arrayMatch = line.match(/^\s+-\s+(.+)/);
    const faqQuestionMatch = line.match(/^\s+-\s+question:\s*"(.*)"/);
    const faqAnswerMatch = line.match(/^\s+answer:\s*"(.*)"/);

    if (faqQuestionMatch) {
      if (currentFaq.question) faqList.push(currentFaq);
      currentFaq = { question: faqQuestionMatch[1] };
      inFaq = true;
    } else if (faqAnswerMatch && inFaq) {
      currentFaq.answer = faqAnswerMatch[1];
      faqList.push(currentFaq);
      currentFaq = {};
    } else if (line.startsWith('tags:')) {
      const rest = line.replace('tags:', '').trim();
      if (rest.startsWith('[')) {
        fm.tags = rest.slice(1, -1).split(',').map(t => t.trim().replace(/"/g, ''));
      } else {
        fm.tags = [];
      }
      inFaq = false;
    } else if (keyMatch && !line.startsWith(' ')) {
      if (currentKey && currentValue.length) {
        fm[currentKey] = currentValue.join('\n');
      }
      currentKey = keyMatch[1];
      currentValue = keyMatch[2] ? [keyMatch[2]] : [];
      inFaq = false;
    } else if (currentKey && !inFaq) {
      currentValue.push(line);
    }
  }
  if (currentKey && currentValue.length) {
    fm[currentKey] = currentValue.join('\n');
  }

  fm.faqs = faqList;
  return { frontmatter: fm, body: text.slice(m[0].length) };
}

async function translate(text, targetLang, targetLabel) {
  const prompt = `Translate the following China travel article from English to ${targetLang} (${targetLabel}). 

Rules:
1. Keep all Markdown formatting, HTML tags, URLs, and internal links (href="/...", ](/...) exactly as-is — DO NOT translate them
2. Translate all visible text: headings, paragraphs, table content, list items
3. Keep the same structure: headings, paragraphs, tables, callout divs
4. Use natural ${targetLang} — not machine-translated gibberish
5. Return ONLY the translated content, no explanations

Article content:
${text}`;

  const res = await fetch(`${BASE_URL}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({
      model: MODEL,
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 8192,
      temperature: 0.3,
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API error ${res.status}: ${err.slice(0, 200)}`);
  }

  const data = await res.json();
  return data.choices[0].message.content;
}

async function translateFaqs(faqs, targetLang, targetLabel) {
  if (!faqs || faqs.length === 0) return [];

  const prompt = `Translate these FAQ items from English to ${targetLang} (${targetLabel}).
Return as a JSON array of objects with "question" and "answer" keys.
Keep any URLs and internal links unchanged.
Only translate the visible text.

FAQs:
${JSON.stringify(faqs, null, 2)}`;

  const res = await fetch(`${BASE_URL}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({
      model: MODEL,
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 4096,
      temperature: 0.2,
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    console.warn(`  FAQ API error ${res.status}, keeping original FAQs`);
    return faqs;
  }

  const data = await res.json();
  try {
    return JSON.parse(data.choices[0].message.content);
  } catch {
    console.warn('  FAQ parse failed, keeping original');
    return faqs;
  }
}

async function processArticle(slug, locale) {
  const sourceFile = `${CONTENT_DIR}/posts/${slug}.md`;
  const targetDir = `${CONTENT_DIR}/${locale.dir}`;
  const targetFile = `${targetDir}/${slug}.md`;

  if (!existsSync(sourceFile)) {
    console.error(`  SKIP: source not found ${sourceFile}`);
    return false;
  }

  if (existsSync(targetFile)) {
    console.log(`  SKIP: already exists ${targetFile}`);
    return false;
  }

  mkdirSync(targetDir, { recursive: true });

  const sourceText = readFileSync(sourceFile, 'utf8');
  const parsed = parseFrontmatter(sourceText);
  if (!parsed) {
    console.error(`  FAIL: cannot parse frontmatter`);
    return false;
  }

  const { frontmatter, body } = parsed;

  console.log(`  Translating title & description...`);
  const titlePrompt = `Translate this title and description from English to ${locale.lang} (${locale.label}). Return as JSON: {"title": "...", "description": "..."}

Title: ${frontmatter.title}
Description: ${frontmatter.description}`;

  const titleRes = await fetch(`${BASE_URL}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({
      model: MODEL,
      messages: [{ role: 'user', content: titlePrompt }],
      max_tokens: 500,
      temperature: 0.2,
    }),
  });

  let translatedTitle = frontmatter.title;
  let translatedDesc = frontmatter.description;
  if (titleRes.ok) {
    const data = await titleRes.json();
    try {
      const parsed = JSON.parse(data.choices[0].message.content);
      if (parsed.title) translatedTitle = parsed.title;
      if (parsed.description) translatedDesc = parsed.description;
    } catch {}
  }

  console.log(`  Translating body...`);
  let translatedBody;
  try {
    translatedBody = await translate(body, locale.lang, locale.label);
  } catch (e) {
    console.error(`  Body translation failed: ${e.message}`);
    // Fallback: write an abbreviated version
    translatedBody = body;
  }

  console.log(`  Translating FAQs...`);
  const translatedFaqs = await translateFaqs(frontmatter.faqs, locale.lang, locale.label);

  // Handle tags - keep original tags, they work across languages
  const tags = Array.isArray(frontmatter.tags) ? frontmatter.tags : [];

  // Build frontmatter YAML
  let output = '---\n';
  output += `title: "${translatedTitle.replace(/"/g, '\\"')}"\n`;
  output += `description: "${translatedDesc.replace(/"/g, '\\"')}"\n`;
  output += `pubDate: ${frontmatter.pubDate || '2026-07-20'}\n`;
  output += `category: ${frontmatter.category || 'essentials'}\n`;

  if (tags.length > 0) {
    output += `tags: [${tags.join(', ')}]\n`;
  } else {
    output += 'tags: []\n';
  }

  if (frontmatter.featured === true || frontmatter.featured === 'true') {
    output += 'featured: true\n';
  } else {
    output += 'featured: false\n';
  }

  if (translatedFaqs.length > 0) {
    output += 'faqs:\n';
    for (const faq of translatedFaqs) {
      if (faq.question && faq.answer) {
        output += `  - question: "${faq.question.replace(/"/g, '\\"')}"\n`;
        output += `    answer: "${faq.answer.replace(/"/g, '\\"')}"\n`;
      }
    }
  } else if (frontmatter.faqs && frontmatter.faqs.length > 0) {
    // Fallback: keep original English FAQs
    output += 'faqs:\n';
    for (const faq of frontmatter.faqs) {
      output += `  - question: "${(faq.question || '').replace(/"/g, '\\"')}"\n`;
      output += `    answer: "${(faq.answer || '').replace(/"/g, '\\"')}"\n`;
    }
  }

  if (frontmatter.cover) {
    output += `cover: ${frontmatter.cover}\n`;
  }
  if (frontmatter.coverAlt) {
    output += `coverAlt: "${frontmatter.coverAlt}"\n`;
  }

  output += '---\n\n';
  output += translatedBody;

  // Ensure the body ends with newline
  if (!output.endsWith('\n')) output += '\n';

  writeFileSync(targetFile, output, 'utf8');
  console.log(`  ✅ Written to ${targetFile}`);
  return true;
}

async function main() {
  let total = 0;
  let success = 0;

  for (const slug of ARTICLES) {
    for (const locale of LOCALES) {
      total++;
      console.log(`\n[${slug}] → ${locale.code} (${locale.lang})`);
      try {
        const ok = await processArticle(slug, locale);
        if (ok) success++;
      } catch (e) {
        console.error(`  ❌ Error: ${e.message}`);
      }
    }
  }

  console.log(`\n========================================`);
  console.log(`Done: ${success}/${total} files translated`);
  console.log(`========================================`);
}

main().catch(console.error);
