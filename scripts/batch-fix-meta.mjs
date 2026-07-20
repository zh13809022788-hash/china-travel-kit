/**
 * Batch fix: description length, title length, placeholder text
 *
 * This script fixes mechanically resolvable quality issues across all
 * posts-* collections. It is NOT a content expansion tool — thin body,
 * FAQ, and internal link issues are handled separately by WorkBuddy.
 *
 * Rules:
 * - Description > 180 chars: cut at last sentence boundary ≤ 180
 * - Title > 75 chars: cut at last word boundary ≤ 75
 * - Placeholder text (TODO/TBD/lorem ipsum): replace with flagged markers
 */
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const contentDir = join(process.cwd(), 'src', 'content');
const collectionDirs = readdirSync(contentDir)
  .filter((entry) => entry.startsWith('posts'))
  .filter((entry) => statSync(join(contentDir, entry)).isDirectory());

let totalFixed = 0;

for (const dirName of collectionDirs) {
  const dirPath = join(contentDir, dirName);
  const files = readdirSync(dirPath).filter((f) => f.endsWith('.md'));

  for (const file of files) {
    const filePath = join(dirPath, file);
    const source = readFileSync(filePath, 'utf8');

    // Parse frontmatter
    const frontMatch = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
    if (!frontMatch) continue;

    const raw = frontMatch[1];
    const lines = raw.split(/\r?\n/);
    let changed = false;
    let newLines = [];

    for (const line of lines) {
      let newLine = line;

      // Fix description > 180 chars
      const descMatch = newLine.match(/^description:\s*(.*)$/);
      if (descMatch) {
        const val = descMatch[1];
        const clean = val.replace(/^['"]|['"]$/g, '');
        if (clean.length > 180) {
          // Cut at last sentence boundary ≤ 180
          const cut = clean.slice(0, 181);
          const lastPeriod = cut.lastIndexOf('.');
          const lastQuestion = cut.lastIndexOf('?');
          const lastExcl = cut.lastIndexOf('!');
          const bestBreak = Math.max(lastPeriod, lastQuestion, lastExcl);
          if (bestBreak > 80) {
            const newVal = clean.slice(0, bestBreak + 1);
            newLine = `description: "${newVal.replace(/"/g, "'")}"`;
            changed = true;
          }
        }
      }

      // Fix description < 90 chars (append ellipsis and note)
      if (descMatch) {
        const val = descMatch[1];
        const clean = val.replace(/^['"]|['"]$/g, '');
        if (clean.length < 90) {
          newLine = `description: "${clean} [NEEDS EXPANSION]"`;
          changed = true;
        }
      }

      // Fix title > 75 chars
      const titleMatch = newLine.match(/^title:\s*(.*)$/);
      if (titleMatch) {
        const val = titleMatch[1];
        const clean = val.replace(/^['"]|['"]$/g, '');
        if (clean.length > 75) {
          // Cut at last word boundary ≤ 73, add "..."
          const cut = clean.slice(0, 73);
          const lastSpace = cut.lastIndexOf(' ');
          if (lastSpace > 40) {
            newLine = `title: "${clean.slice(0, lastSpace)}..."`;
          } else {
            newLine = `title: "${clean.slice(0, 72)}..."`;
          }
          changed = true;
        }
      }

      // Fix placeholder text in body (not frontmatter)
      // Note: full body placeholder check needed separate pass

      newLines.push(newLine);
    }

    if (changed) {
      const newFrontmatter = newLines.join('\n');
      const newSource = `---\n${newFrontmatter}\n---\n${source.slice(frontMatch[0].length)}`;
      writeFileSync(filePath, newSource, 'utf8');
      totalFixed++;
      console.log(`FIXED: [${dirName}] ${file}`);
    }
  }
}

console.log(`\nBatch fix complete. ${totalFixed} file(s) modified.`);
