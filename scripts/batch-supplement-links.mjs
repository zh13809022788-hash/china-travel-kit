/**
 * Supplement: add one more universal internal link to articles
 * that had < 3 internal links after batch-add-internal-links.mjs.
 *
 * Adds a "tool center" link before the last block or at end.
 */
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const contentDir = join(process.cwd(), 'src', 'content');
const collectionDirs = readdirSync(contentDir)
  .filter((entry) => entry.startsWith('posts'))
  .filter((entry) => statSync(join(contentDir, entry)).isDirectory());

function countInternalLinks(body) {
  const mdLinks = (body.match(/\]\(\/(?!\/)/g) || []).length;
  const htmlLinks = (body.match(/href="\/(?!\/)/g) || []).length;
  return mdLinks + htmlLinks;
}

function parseFrontmatter(source) {
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) return null;
  return { frontmatter: match[0], body: source.slice(match[0].length) };
}

const EXTRA_LINK = '\n\n<div class="my-4"><a href="/tools/" class="text-brand-600 underline">Explore all China travel tools</a> — trip planner, visa checker, currency converter and more.</div>\n';

let totalFixed = 0;

for (const dirName of collectionDirs) {
  const dirPath = join(contentDir, dirName);
  const files = readdirSync(dirPath).filter((f) => f.endsWith('.md'));

  for (const file of files) {
    const filePath = join(dirPath, file);
    const source = readFileSync(filePath, 'utf8');
    const parsed = parseFrontmatter(source);
    if (!parsed) continue;

    const links = countInternalLinks(parsed.body);
    if (links >= 3) continue;

    // Append the extra link
    const newBody = parsed.body.trimEnd() + EXTRA_LINK;
    const newSource = parsed.frontmatter + newBody;
    writeFileSync(filePath, newSource, 'utf8');
    totalFixed++;
    console.log(`SUPP: [${dirName}/${file}] links=${links}->${countInternalLinks(newBody)}`);
  }
}

console.log(`\nDone. ${totalFixed} file(s) supplemented.`);
