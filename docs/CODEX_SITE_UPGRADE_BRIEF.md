# Codex Brief: ChinaTripBox Comprehensive Upgrade

Owner model: Hermes coordinates, Codex implements, Hermes verifies/deploys.

Goal: Upgrade ChinaTripBox into a stronger China travel authority site with better content architecture, editorial depth, internal linking, Google indexing readiness, and selective contextual linking to Baijiu365.

Non-negotiables:
- Preserve working Astro static build.
- Do not ask the user routine implementation questions; make conservative product/content decisions and document them.
- Avoid generic AI travel content. Content should be practical, specific, source-aware where possible, and useful for foreign visitors.
- Keep ChinaTripBox focused on travel logistics and planning; Baijiu365 is the deeper alcohol/baijiu companion site.
- Do not add spammy footer/sitewide SEO links. Use contextual links only where they help readers.
- Update/create development docs with decisions, changed structure, and remaining work.

Current context:
- Project path: D:\独立站\china-travel-kit
- Domain: https://www.chinatripbox.com
- Existing content includes payments, eSIM, transport, city guides, tools, food ordering, tipping, and practical China travel guides.
- Baijiu365 project path: D:\白酒独立站, domain https://baijiu365.com.

Prioritized work:
1. IA/navigation: improve category paths and topic clusters so users and Google can understand essentials, payments, transport, cities, tools, food, and long-stay topics.
2. Homepage/resources: surface best guides, tools, and topical pathways more clearly.
3. Internal linking: add useful next-step links between related guides, especially payments, eSIM/connectivity, transport, city guides, food, and tipping.
4. SEO/indexing: review metadata, canonical/sitemap/robots, schema, category pages, duplicate/thin pages, and crawlable links.
5. Contextual Baijiu365 links: add 2-4 natural links only in food/etiquette/culture contexts, pointing to specific Baijiu365 pages such as how-to-drink-baijiu, baijiu-101, beginner bottle guide, or Maotai guide.
6. Content quality: strengthen weak pages with practical details, warnings, decision frameworks, FAQs, and concise summaries.

Verification:
- npm run build must pass.
- Inspect generated routes/sitemap for expected URLs.
- Provide a concise change report listing files changed, major decisions, and any follow-up items Hermes should verify/deploy.
