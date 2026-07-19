# China Travel Kit

**Project**: China Travel Kit — static English guides for foreign visitors (payments, eSIM, transport) built with Astro.

## Project Overview
A small static site containing practical guides, interactive front-end tools, and affiliate placeholders to help foreign visitors travel in China. This repository is set up for local development and static deployment (Cloudflare Pages recommended).

## Environment & Dependencies
- Node.js >= 18
- npm (or pnpm/yarn)
- Git
- Local AI runtime: GPT-5 mini (project notes and content generation / workflow assume availability of GPT-5 mini)

> Note: This project was scaffolded and verified to build locally with `npm run build`. README explicitly documents GPT-5 mini as the primary model used for content generation and automation.

## Install & Run
Install dependencies:

```bash
npm install
```

Run dev server:

```bash
npm run dev
```

Build production static files:

```bash
npm run build
```

Preview built site:

```bash
npm run preview
```

## Directory Structure
- `src/` — Astro source files (pages, components, layouts, content)
  - `src/content/posts/` — Markdown guides
  - `src/pages/` — routes and tool pages
  - `src/components/` — UI components (AdSlot, AffiliateCta, FaqSection)
  - `src/layouts/` — base and post layouts
  - `src/styles/` — global CSS
- `public/` — static assets (og images, robots.txt)
- `dist/` — generated static site (after `npm run build`)
- `package.json` — scripts and dependencies

## Usage Example
Open development site and visit tool pages:

```bash
npm run dev
# then open http://localhost:3000 (or the port shown by Astro)
```

## Affiliate Placeholders
Replace these placeholders in Markdown content with your real affiliate links before publishing:
- `<!-- AFFILIATE_ESIM -->`
- `<!-- AFFILIATE_PAYMENT -->`
- `<!-- AFFILIATE_TRAVEL -->`

## Open Source & License
This repository is provided as-is. Add your preferred license file (e.g., MIT) in the repository root if you intend to open-source.

## Contact
For automation or content regeneration notes related to GPT-5 mini, update the `auto-setup.md.txt` instructions.

