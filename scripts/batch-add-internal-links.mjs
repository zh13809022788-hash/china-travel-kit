/**
 * Batch add internal links to all posts based on category.
 *
 * Rule: for each article, append a "Related tools" section with
 * category-appropriate links before the FAQ section or at end of body.
 *
 * Category → Tool mapping:
 * - esim  → /tools/esim-comparison/
 * - payment → /tools/payment-checker/
 * - transport → /tools/show-to-driver/ + transport-guide link
 * - essentials → /tools/survival-kit/ + /tools/best-time-to-visit/
 * - food → /tools/essential-phrases/ + food guide
 */
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const contentDir = join(process.cwd(), 'src', 'content');
const collectionDirs = readdirSync(contentDir)
  .filter((entry) => entry.startsWith('posts'))
  .filter((entry) => statSync(join(contentDir, entry)).isDirectory());

const TOOL_LINKS = {
  esim: {
    label: 'eSIM plan comparator',
    url: '/tools/esim-comparison/',
    desc: 'Compare data plans across different China eSIM providers.',
  },
  payment: {
    label: 'payment compatibility checker',
    url: '/tools/payment-checker/',
    desc: 'Check if your card works with Alipay and WeChat Pay in China.',
  },
  transport: [
    { label: 'show to driver tool', url: '/tools/show-to-driver/', desc: 'Show Chinese addresses to taxi drivers.' },
    { label: 'budget & cash estimator', url: '/tools/budget-cash-estimator/', desc: 'Plan your trip budget and how much cash to bring.' },
  ],
  essentials: [
    { label: 'china survival kit', url: '/tools/survival-kit/', desc: 'Full-screen translation cards and checklists for your trip.' },
    { label: 'best time to visit china', url: '/tools/best-time-to-visit/', desc: 'Check weather and crowds by city and month.' },
  ],
  food: [
    { label: 'essential chinese phrases', url: '/tools/essential-phrases/', desc: 'Must-know Mandarin phrases for restaurants.' },
    { label: 'clothing & shoe size converter', url: '/tools/clothing-size-converter/', desc: 'Convert your sizes to Chinese sizes.' },
  ],
};

const ALL_TOOL_LINKS = [
  { label: 'visa-free & transit checker', url: '/tools/visa-free-checker/', desc: 'Check if you need a visa for China.' },
  { label: 'currency converter', url: '/tools/currency-converter/', desc: 'Convert your currency to RMB.' },
  { label: 'power plug & voltage checker', url: '/tools/power-plug-checker/', desc: 'Check if you need a plug adapter.' },
  { label: 'will my apps work in china?', url: '/tools/app-availability-checker/', desc: 'Check which apps work without a VPN.' },
];

function parseFrontmatter(source) {
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) return null;
  const lines = match[1].split(/\r?\n/);
  const data = {};
  let inFaqs = false;
  for (const line of lines) {
    if (/^faqs:\s*$/.test(line)) { inFaqs = true; continue; }
    if (inFaqs && !line.startsWith(' ')) inFaqs = false;
    const field = line.match(/^([A-Za-z][A-Za-z0-9_]*):\s*(.*)$/);
    if (field) data[field[1]] = field[2].replace(/^['"]|['"]$/g, '').trim();
  }
  return { data, frontmatter: match[0], body: source.slice(match[0].length) };
}

const RELATED_HTML = `
<div class="related-tools">
  <h3>Related tools for your China trip</h3>
  <p>TOOL_HTML</p>
</div>`;

let totalFixed = 0;

for (const dirName of collectionDirs) {
  const dirPath = join(contentDir, dirName);
  const files = readdirSync(dirPath).filter((f) => f.endsWith('.md'));

  for (const file of files) {
    const filePath = join(dirPath, file);
    const source = readFileSync(filePath, 'utf8');
    const parsed = parseFrontmatter(source);
    if (!parsed) continue;
    const { data, body } = parsed;
    const category = data.category;

    if (!category) continue;

    // Count existing internal links
    const existingLinks = (body.match(/\]\(\/(?!\/)/g) || []).length;
    if (existingLinks >= 3) continue; // skip if already 3+

    // Build related tool links HTML
    const links = TOOL_LINKS[category];
    if (!links) continue;

    const linkArray = Array.isArray(links) ? links : [links];
    const linkHtml = linkArray.map((l) =>
      `<a href="${l.url}" rel="nofollow">${l.label}</a> — ${l.desc}`
    ).join('<br>');

    const htmlBlock = `
<div class="my-6 rounded-lg border border-gray-200 bg-gray-50 p-4">
  <p class="text-sm text-gray-700">
    <strong>Planning your trip?</strong><br>
    ${linkHtml}
  </p>
</div>`;

    // Insert before the FAQ section or append at end
    const faqIndex = body.indexOf('## FAQ');
    const insertIndex = faqIndex > 100 ? faqIndex : body.length;

    const newBody = body.slice(0, insertIndex) + '\n' + htmlBlock + '\n' + body.slice(insertIndex);

    const newSource = parsed.frontmatter + newBody;
    writeFileSync(filePath, newSource, 'utf8');
    totalFixed++;
    console.log(`FIXED: [${dirName}/${file}] category=${category} links=${linkArray.length}`);
  }
}

console.log(`\nDone. ${totalFixed} file(s) updated with internal links.`);
