#!/usr/bin/env node
/**
 * One-time fix: correct all locale .astro files with wrong import depths.
 *
 * Problem: Auto-generated locale pages (zh-tw/vi/*, de/ms/*, etc.) were created
 * with import depths that are off by 1 (missing i18n/ from replacement list).
 *
 * This script scans ALL locale-page .astro files, validates each file's import
 * depths against its directory depth, and fixes mismatches in-place.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PAGES_DIR = path.join(__dirname, "..", "src", "pages");

const LOCALES = new Set(["zh-tw", "ja", "ko", "ru", "fr", "de", "es", "vi", "th", "ms"]);

let fixed = 0;
let skipped = 0;
let errors = [];

// Known import root prefixes (any relative import under these will be checked)
const IMPORT_ROOTS = [
  "layouts/", "components/", "i18n/", "styles/", "data/", "assets/", "images/",
  "config",
];

function getExpectedDepth(relPath) {
  // relPath is relative to project root, e.g. "src/pages/zh-tw/vi/payment/index.astro"
  const parts = relPath.split("/");
  // Directory depth from src/pages/: parts = ["src","pages","zh-tw","vi","payment","index.astro"]
  // File is at directory depth (parts.length - 3): zh-tw/vi/payment = 3 dirs deep
  const dirDepth = parts.length - 3; // subtract "src", "pages", and the filename
  // To reach src/ from the file's directory: need to go up dirDepth+1 levels
  // Example: zh-tw/vi/payment (dirDepth=3) → ../../../../ (4 levels) to reach src/
  return dirDepth + 1;
}

function fixFile(filePath, relPath) {
  const content = fs.readFileSync(filePath, "utf8");
  const expectedDepth = getExpectedDepth(relPath);

  let modified = false;
  const lines = content.split("\n");
  const newLines = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Only process import lines with relative paths (single or double quotes)
    if (!trimmed.startsWith("import ") || (!trimmed.includes("from '../") && !trimmed.includes('from "../'))) {
      newLines.push(line);
      continue;
    }

    const match = trimmed.match(/from\s+['"]((\.\.\/)+)([^'"]+)['"]/);
    if (!match) {
      newLines.push(line);
      continue;
    }

    const fullImport = match[1] + match[3]; // e.g. "../../../../layouts/BaseLayout.astro"
    const upCount = match[1].split("../").length - 1;
    const importPath = match[3];

    // Only fix imports under our known roots
    const isKnownRoot = IMPORT_ROOTS.some((root) => importPath.startsWith(root));
    if (!isKnownRoot) {
      newLines.push(line);
      continue;
    }

    if (upCount === expectedDepth) {
      newLines.push(line); // already correct
      continue;
    }

    // Fix the depth
    const correctPrefix = "../".repeat(expectedDepth);
    const fixedLine = line.replace(match[1], correctPrefix);
    newLines.push(fixedLine);
    modified = true;
    console.error(`  FIX ${relPath}:${i + 1} — ${upCount}→${expectedDepth}: ${importPath}`);
  }

  if (modified) {
    fs.writeFileSync(filePath, newLines.join("\n"), "utf8");
    return true;
  }
  return false;
}

function walkDir(dir, relBase = "") {
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const relPath = relBase ? `${relBase}/${entry.name}` : entry.name;

    if (entry.isDirectory()) {
      walkDir(fullPath, relPath);
    } else if (entry.isFile() && entry.name.endsWith(".astro")) {
      // Only check locale files (inside a locale subdirectory)
      const isLocaleFile = [...LOCALES].some((loc) => relPath.startsWith(`src/pages/${loc}/`));
      if (!isLocaleFile) continue;

      try {
        const wasFixed = fixFile(fullPath, relPath);
        if (wasFixed) fixed++;
        else skipped++;
      } catch (e) {
        errors.push({ file: relPath, error: e.message });
      }
    }
  }
}

console.log("🔍 Scanning and fixing locale .astro import depths...\n");
console.error = (msg) => { process.stderr.write(msg + "\n"); };
walkDir(path.join(__dirname, ".."));

console.log(`\n📊 Results: ${fixed} fixed, ${skipped} already correct`);
if (errors.length > 0) {
  console.log(`❌ ${errors.length} error(s):`);
  errors.forEach((e) => console.log(`  ${e.file}: ${e.error}`));
  process.exit(1);
} else {
  console.log("✅ All locale imports corrected.");
}
