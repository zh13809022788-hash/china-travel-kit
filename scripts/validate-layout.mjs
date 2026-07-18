// Pre-build validation: ensures BaseLayout.astro has <slot /> in <body>.
// This prevents the "blank page" regression caused by automation removing <slot />.
// Runs automatically via "prebuild" in package.json before every `npm run build`.

import { readFileSync } from 'node:fs';

const LAYOUT_PATH = 'src/layouts/BaseLayout.astro';

try {
  const content = readFileSync(LAYOUT_PATH, 'utf-8');

  // Check for default <slot /> (not <slot name="head" />)
  const hasDefaultSlot = /<slot\s*\/>|<slot\s*>/.test(content) &&
    !/<slot\s+name=/.test(content.replace(/<slot\s+name="head"\s*\/>/g, ''));

  if (!hasDefaultSlot) {
    console.error('\n❌ FATAL: BaseLayout.astro is missing the default <slot /> tag in <body>.');
    console.error('   Without <slot />, ALL page content renders AFTER </html> → blank pages.');
    console.error('   Fix: Add <slot /> inside <body> in src/layouts/BaseLayout.astro\n');
    process.exit(1);
  }

  console.log('✓ Layout validation passed: <slot /> present in BaseLayout.astro');
} catch (err) {
  console.error(`\n❌ Could not read ${LAYOUT_PATH}: ${err.message}\n`);
  process.exit(1);
}
