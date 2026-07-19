#!/usr/bin/env node
/**
 * HEADERS VALIDATION GATE — runs before every build.
 * Blocks deployment if _headers contains dangerous patterns.
 */

const fs = require("fs");
const path = require("path");

const HEADERS_PATH = path.join(__dirname, "..", "public", "_headers");

if (!fs.existsSync(HEADERS_PATH)) {
  console.error("❌ FATAL: public/_headers is missing!");
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

  // Detect next block start (ends /* block)
  if (inStarBlock && trimmed && !trimmed.startsWith("#") && trimmed.endsWith(":")) {
    // Found a header line inside /* block
  }

  // Detect next path pattern (ends /* block)
  if (inStarBlock && /^\/[^*]/.test(trimmed)) {
    inStarBlock = false;
  }

  // DETECT: Content-Type inside /* block
  if (inStarBlock && /Content-Type/i.test(trimmed)) {
    errors.push(
      `Line ${i + 1}: Content-Type inside /* block — THIS BREAKS CSS/JS MIME types. Remove it.`
    );
  }

  // DETECT: bare wildcard Content-Type rules like *.css / *.js
  if (/^\*\.[a-z]+\s*$/.test(trimmed) && !inStarBlock) {
    const nextLine = lines[i + 1] || "";
    if (/Content-Type/i.test(nextLine)) {
      errors.push(
        `Line ${i + 1}: Bare wildcard rule \"${trimmed}\" — will match root / incorrectly. Use /assets/*.css instead.`
      );
    }
  }

  // DETECT: Global Content-Type on /*
  if (trimmed === "/*" && !inStarBlock) {
    inStarBlock = true;
  }
}

if (errors.length > 0) {
  console.error("❌ _HEADERS VALIDATION FAILED:");
  errors.forEach((e) => console.error("   " + e));
  console.error("");
  console.error("Cloudflare Pages auto-detects MIME types correctly by default.");
  console.error("DO NOT add Content-Type rules to _headers unless you know what you are doing.");
  process.exit(1);
}

console.log("✅ _headers validation passed (" + lines.length + " lines)");

