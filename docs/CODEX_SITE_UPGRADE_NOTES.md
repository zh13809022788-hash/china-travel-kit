# ChinaTripBox Site Upgrade Notes

Date: 2026-07-12

## Decisions Made

- Added an Astro content-layer collection for `data_pipeline/pages/**/*.json`, so pipeline output can become static pages without first being converted to Markdown.
- Kept ChinaTripBox focused on practical China travel logistics: payments, internet, transport, cities, food/dining, tools, and longer-stay planning.
- Treated `/resources/` as the main "start here" index rather than creating a marketing landing page.
- Added dedicated crawlable hubs for `/cities/` and `/food/` because city guides and food/etiquette content were high-value but previously depended on article discovery.
- Updated primary navigation to expose the main topic clusters: Start Here, Essentials, Payments, Internet, Transport, Cities, Food, and Tools.
- Set the canonical production site in Astro and robots sitemap reference to `https://www.chinatripbox.com`, matching the briefed domain.
- Added contextual Baijiu365 links only where dining culture makes them useful: baijiu basics, polite drinking, and banquet/toast context. No sitewide/footer links were added.

## Implementation Summary

- Homepage now points users toward the resource hub, topic clusters, city guides, food/dining guides, and practical tools.
- Resource hub now groups links by user intent: first-trip setup, payments, internet/apps, transport/cities, food/etiquette, and longer stays.
- Article pages now render automatic "Recommended next steps" links based on shared category, tags, and city context.
- JSON records in `data_pipeline/pages/` now build to static `/data/<slug>/` pages through the `dataPipelinePages` collection and `src/pages/data/[...slug].astro`.
- Transport hub now has clearer paths for trains, airport transfers, ride-hailing, and metro usage.
- Food hub includes practical dining pathways and a small, contextual culture-companion box.
- City hub groups Beijing, Shanghai, Chengdu, Hangzhou, and Sanya guides with local next-step links.
- Base schema now includes a site search action for the homepage search experience.

## Remaining Work

- Consider adding a dedicated `/visa/` or `/entry/` hub if visa-free/transit content expands beyond the current guide and tool.
- Add unique city landing pages if each city grows beyond one guide plus local transport/food articles.
- Review GSC after deployment for canonical consolidation between non-www and www.
- Add last-updated metadata distinct from publish date when articles receive substantive updates.
- Consider hand-curated related links for the top 10 traffic pages after search data is available.

## 2026-07-14 Update

- Kept today's work scoped to ChinaTripBox only.
- Added a homepage "If you only read three pages" pathway to push new visitors toward the highest-intent setup, payment, and train guides.
- Added an "If you only have 30 minutes" group to `/resources/` for users who need a fast pre-departure reading path.
- Added a dedicated `/affiliate-disclosure/` page and linked it from the footer and `llms.txt`.
- Verification passed: `npm.cmd run check:content` and `npm.cmd run build`; Astro generated 67 pages.
- Added `docs/GROWTH_PLAN_30_DAYS.md` with a 30-day publishing queue, measurement routine, and internal-link targets.
- Published three high-intent posts:
  - `/posts/alipay-vs-wechat-pay-foreigners/`
  - `/posts/first-24-hours-in-china-arrival-checklist/`
  - `/posts/do-you-need-a-vpn-in-china-2026/`
- Expanded `/tools/payment-checker/` and `/tools/visa-free-checker/` with SEO support copy, risk tables/checklists, and next-step links.
- Verification passed again after content expansion: `npm.cmd run check:content` passed for 34 posts and `npm.cmd run build` generated 70 pages.
- Added first Survival Kit module pass:
  - `src/data/survival-kits.json`
  - `ShowToLocal`, `SurvivalChecklist`, and `ContextAiBubble` components
  - `/tools/survival-kit/`
  - shared Tool Center and resource hub links
- Survival Kit verification passed: `npm.cmd run check:content` passed for 34 posts and `npm.cmd run build` generated 71 pages.
- Follow-up tasks are recorded in `PRODUCT_MONETIZATION_PLAN.md` and `docs/GROWTH_PLAN_30_DAYS.md`, including expansion to 8 themes and selective AI bubble rollout.
