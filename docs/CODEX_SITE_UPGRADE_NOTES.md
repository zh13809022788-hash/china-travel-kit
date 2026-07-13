# ChinaTripBox Site Upgrade Notes

Date: 2026-07-12

## Decisions Made

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
