#!/usr/bin/env node
/**
 * HEADERS VALIDATION GATE — runs before every build.
 * Blocks deployment if _headers contains dangerous patterns.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const HEADERS_PATH = path.join(__dirname, "..", "public", "_headers");

if (!fs.existsSync(HEADERS_PATH)) {
  console.error("\u274c FATAL: public/_headers is missing!");
  process.exit(1);
}

const content = fs.readFileSync(HEADERS_PATH, "utf8");
const lines = content.split("\n");
let inStarBlock = false;
let errors = [];

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const trimmed = line.trim();

  // Detect /* block start
  if (trimmed === "/*") {
    inStarBlock = true;
    continue;
  }

  // Detect next path pattern (ends /* block)
  if (inStarBlock && /^\/[^*]/.test(trimmed)) {
    inStarBlock = false;
  }

  // DETECT: Content-Type inside /* block
  if (inStarBlock && /^\s*Content-Type\s*:/i.test(trimmed)) {
    errors.push(
      `Line ${i + 1}: Content-Type inside /* block \u2014 THIS BREAKS CSS/JS MIME types. Remove it.`
    );
  }

  // DETECT: bare wildcard Content-Type rules like *.css / *.js
  if (/^\*\.[a-z]+\s*$/.test(trimmed) && !inStarBlock) {
    const nextLine = lines[i + 1] || "";
    if (/^\s*Content-Type\s*:/i.test(nextLine)) {
      errors.push(
        `Line ${i + 1}: Bare wildcard rule "${trimmed}" \u2014 will match root / incorrectly. Use /assets/*.css instead.`
      );
    }
  }
}

if (errors.length > 0) {
  console.error("\u274c _HEADERS VALIDATION FAILED:");
  errors.forEach((e) => console.error("   " + e));
  console.error("");
  console.error("Cloudflare Pages auto-detects MIME types correctly by default.");
  console.error("DO NOT add Content-Type rules to _headers unless you know what you are doing.");
  process.exit(1);
}

console.log("\u2705 _headers validation passed (" + lines.length + " lines)");
