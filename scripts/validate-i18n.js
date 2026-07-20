#!/usr/bin/env node
/**
 * I18N QUALITY GATE — runs before every build.
 * Catches systematic bugs introduced by the i18n translation pipeline:
 *
 * 1. Wrong relative import paths (always one "../" level too few)
 * 2. Unescaped apostrophes in JavaScript single-quoted strings (e.g. d'hôtel)
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PAGES_DIR = path.join(__dirname, "..", "src", "pages");

const LOCALES = ["zh-tw", "ja", "ko", "ru", "fr", "de", "es"];

let totalErrors = 0;

// ─── Check 1: Import path depth ──────────────────────────────────────
function checkImportPaths(filePath, relPath) {
  const content = fs.readFileSync(filePath, "utf8");
  const lines = content.split("\n");
  const errors = [];

  // Expected number of "../" levels to reach src/ from this file's directory
  // src/pages/$locale/file.astro -> 3 slashes -> need 2 levels up (to src/)
  // src/pages/$locale/subdir/file.astro -> 4 slashes -> need 3 levels up
  const depth = relPath.split("/").length; // e.g. ["src","pages","fr","contact.astro"] = 4
  const expectedUp = depth - 2; // file dir depth from pages: e.g. 4-2=2 for contact.astro, 5-2=3 for subdir/index.astro

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line.startsWith("import ")) continue;

    // Extract the import path
    const match = line.match(/from\s+['"]([^'"]+)['"]/);
    if (!match) continue;

    const importPath = match[1];
    if (!importPath.startsWith("../")) continue;

    // Count "../" levels
    const parts = importPath.split("/");
    let upCount = 0;
    for (const p of parts) {
      if (p === "..") upCount++;
      else break;
    }

    if (upCount !== expectedUp) {
      errors.push(
        `  Line ${i + 1}: wrong import depth (${upCount} "../" instead of ${expectedUp}): ${importPath}`
      );
    }
  }

  return errors;
}

// ─── Check 2: Unescaped apostrophes in JS strings ────────────────────
function checkApostrophes(filePath, relPath) {
  const content = fs.readFileSync(filePath, "utf8");
  const lines = content.split("\n");
  const errors = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Only check lines inside frontmatter (between --- markers)
    // HTML template content can safely contain apostrophes
    let inFrontmatter = false;
    // Re-scan from top to determine if this line is inside frontmatter
    for (let k = 0; k < i; k++) {
      if (lines[k].trim() === "---") {
        inFrontmatter = !inFrontmatter;
      }
    }
    if (!inFrontmatter) continue;

    // Skip import lines (already checked by import path validator)
    if (trimmed.startsWith("import ")) continue;

    // Skip lines that are only HTML or comments
    if (trimmed.startsWith("<") || trimmed.startsWith("{/*") || trimmed.startsWith("//")) continue;

    // Look for unescaped ' inside single-quoted JS strings
    // First, determine if we're in a backtick string (template literal)
    const inBacktick = (trimmed.match(/`/g) || []).length % 2 === 1;

    for (let j = 0; j < trimmed.length - 2; j++) {
      const c = trimmed[j];
      if (/[a-zA-Z]/.test(c) && trimmed[j + 1] === "'" && /[a-zA-Z]/.test(trimmed[j + 2])) {
        // Check if this ' is preceded by a backslash (escaped)
        if (j > 0 && trimmed[j - 1] === "\\") continue; // already escaped — OK

        // Now verify we're inside a single-quoted JS string
        const beforeQuote = trimmed.substring(0, j + 1);
        const singleQuotes = (beforeQuote.match(/'/g) || []).length;
        const doubleQuotes = (beforeQuote.match(/"/g) || []).length;
        const escapedSingle = (beforeQuote.match(/\\'/g) || []).length;
        const effectiveSingle = singleQuotes - escapedSingle;

        // We're inside a single-quoted string if: odd single quotes AND
        // either even double quotes OR we're before the first double-quote
        // (handles: const x = 'text d'word'; vs const x = "text d'word";)
        const inSingleQuotes = effectiveSingle % 2 === 1;
        const inDoubleQuotes = doubleQuotes % 2 === 1;

        // Skip if we're in a backtick or double-quoted string (safe)
        if (inBacktick || inDoubleQuotes) continue;

        if (inSingleQuotes) {
          // We're inside a single-quoted JS string — this is an unescaped apostrophe!
          const context = trimmed.substring(Math.max(0, j - 15), j + 15);
          errors.push(
            `  Line ${i + 1}: unescaped apostrophe in JS string: ...${context}...`
          );
          break; // one error per line is enough
        }
      }
    }
  }

  return errors;
}

// ─── Walk all locale .astro files ────────────────────────────────────
function walkDir(dir, relBase = "") {
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const relPath = relBase ? `${relBase}/${entry.name}` : entry.name;

    if (entry.isDirectory()) {
      walkDir(fullPath, relPath);
    } else if (entry.isFile() && entry.name.endsWith(".astro")) {
      // Only check locale files (inside a locale subdirectory)
      const isLocaleFile = LOCALES.some((loc) => relPath.startsWith(`src/pages/${loc}/`));
      if (!isLocaleFile) continue;

      // Check 1: Import paths
      const importErrors = checkImportPaths(fullPath, relPath);
      if (importErrors.length > 0) {
        console.log(`\n❌ ${relPath}`);
        importErrors.forEach((e) => console.log(e));
        totalErrors += importErrors.length;
      }

      // Check 2: Apostrophes
      const apostropheErrors = checkApostrophes(fullPath, relPath);
      if (apostropheErrors.length > 0) {
        if (importErrors.length === 0) console.log(`\n❌ ${relPath}`);
        apostropheErrors.forEach((e) => console.log(e));
        totalErrors += apostropheErrors.length;
      }
    }
  }
}

console.log("🔍 Scanning locale .astro files for i18n quality issues...\n");
walkDir(path.join(__dirname, ".."));

if (totalErrors > 0) {
  console.log(`\n❌ I18N VALIDATION FAILED — ${totalErrors} issue(s) found.`);
  console.log(
    "These are systematic bugs from the i18n translation pipeline. Fix them before deploying."
  );
  process.exit(1);
} else {
  console.log("\n✅ I18N validation passed — all locale files look clean.");
}
