# ChinaTripBox 30-Day Traffic Growth Plan

Date: 2026-07-14

## Goal

Grow qualified organic traffic by publishing high-intent China travel content around the problems foreign visitors search before departure: payments, eSIM/internet, visa-free entry, trains, arrival day, and essential apps.

## Publishing Rules

- Publish 3-5 strong pages per week, not bulk thin pages.
- Each post should include a clear answer near the top, one table or checklist, at least 3 internal links, and 3+ FAQ entries.
- Every new article should point to one relevant tool page and one hub page.
- Update older pages when a new post fills a related search intent.
- Review Search Console weekly for impressions without clicks, then rewrite titles/descriptions before writing more content.

## 30-Day Content Queue

| Day | Page | Primary intent | Internal targets |
| --- | --- | --- | --- |
| 1 | Alipay vs WeChat Pay for Foreigners | Compare payment apps before setup | `/payment/`, `/tools/payment-checker/` |
| 1 | First 24 Hours in China Arrival Checklist | Arrival-day practical checklist | `/resources/`, `/trip-planner/` |
| 1 | Do You Need a VPN in China in 2026? | Internet/app access planning | `/esim/`, `/tools/app-availability-checker/` |
| 2 | China Apps Checklist for Tourists | App setup before travel | `/tools/app-availability-checker/`, `/resources/` |
| 3 | China Visa-Free Transit 240-Hour Rule Explained | Transit eligibility | `/tools/visa-free-checker/`, visa guide |
| 4 | Best China eSIM for iPhone Users | Device-specific eSIM search | `/tools/esim-comparison/`, `/esim/` |
| 5 | China Airport Arrival Checklist | Airport-to-city first steps | airport transport guide, `/tools/show-to-driver/` |
| 6 | Alipay Passport Verification Problems | Payment troubleshooting | Alipay guide, payment checker |
| 7 | WeChat Pay Foreign Card Problems | Payment troubleshooting | WeChat Pay guide, payment checker |
| 8 | China Train Station Guide for Foreigners | Station entry and boarding | high-speed rail guide, 12306 guide |
| 9 | China Metro QR Codes for Tourists | City transport | Shanghai metro guide, `/transport/` |
| 10 | China SIM vs eSIM vs Roaming by Trip Length | Connectivity decision | eSIM comparison, pocket WiFi guide |
| 11 | China Travel Budget by City Tier | Money planning | cash estimator, cash guide |
| 12 | What To Do If Alipay Fails in China | Emergency payment fallback | payment checker, cash guide |
| 13 | Can Tourists Use DiDi Without Chinese? | Ride-hailing search intent | DiDi guide, show-to-driver tool |
| 14 | China Travel During Golden Week | Timing/crowd planning | best-time tool, train guide |
| 15 | Beijing Arrival Checklist | City-specific arrival intent | Beijing guide, Daxing guide |
| 16 | Shanghai Arrival Checklist | City-specific arrival intent | Shanghai guide, metro guide |
| 17 | Chengdu Arrival Checklist | City-specific arrival intent | Chengdu guide, food guide |
| 18 | What Works Without a Chinese Phone Number | Account setup friction | payment, eSIM, app checker |
| 19 | China Hotel Check-In for Foreigners | Practical accommodation setup | city guides, passport caveats |
| 20 | China Translation Apps for Tourists | App planning | app checker, essential phrases |
| 21 | China Food Delivery Without Chinese | Dining conversion | food hub, delivery guide |
| 22 | Can You Use Google Maps in China? | Navigation/internet intent | VPN article, app checker |
| 23 | China Cash Withdrawal Guide | ATM and cash backup | cash guide, budget estimator |
| 24 | China Travel Safety Basics for First-Timers | Practical risk reduction | resources, city hubs |
| 25 | China Layover Guide Without Visa | Stopover search intent | visa-free checker, airport guide |
| 26 | China WeChat Mini Programs for Tourists | App ecosystem education | WeChat Pay, food delivery |
| 27 | How To Buy Attraction Tickets in China | Booking friction | payment, apps, city guides |
| 28 | China Travel Checklist for Families | Segment-specific planning | resources, packing guide |
| 29 | China Travel Checklist for Business Travelers | Segment-specific planning | payment, eSIM, transport |
| 30 | China Trip Mistakes First-Timers Make | Broad internal-link hub | resources, tools, core guides |

## Weekly Measurement

- Search Console: pages with impressions but CTR below 2%.
- Clarity: homepage clicks on search, three-page pathway, tool cards, and resource hub cards.
- Content quality: run `npm.cmd run check:content`.
- Build health: run `npm.cmd run build`.

## Execution Log

### 2026-07-14

Completed Day 1 and related site improvements:

- Published `Alipay vs WeChat Pay for Foreigners`.
- Published `First 24 Hours in China: Arrival Checklist for Foreign Visitors`.
- Published `Do You Need a VPN in China in 2026? Tourist Internet Guide`.
- Added homepage `If you only read three pages` pathway.
- Added `/resources/` `If you only have 30 minutes` pathway.
- Added `/affiliate-disclosure/` and footer/llms links.
- Expanded `/tools/payment-checker/` and `/tools/visa-free-checker/`.
- Verification passed: `npm.cmd run check:content` for 34 posts and `npm.cmd run build` with 70 generated pages.

Next planned batch:

- `China Apps Checklist for Tourists`
- `China Visa-Free Transit 240-Hour Rule Explained`
- `Best China eSIM for iPhone Users`

### 2026-07-14 Survival Kit Module Pass

Completed the first modular Survival Kit pass:

- Added JSON-driven survival-kit content in `src/data/survival-kits.json`.
- Added reusable full-screen translation card component.
- Added checklist component with localStorage persistence and completion state.
- Added context-aware AI entry bubble that opens `/travel-help/` with topic-aware prompts.
- Added `/tools/survival-kit/` and surfaced it in the Tool Center and resource hub.
- Initial themes live: arrival setup and food exploration.

Deferred into follow-up tasks:

- Expand to the remaining six themes: payment, transport, hotel check-in, medical/allergy, shopping/refunds, emergency help.
- Add the AI bubble to `/food/`, `/payment/`, `/transport/`, and `/trip-planner/` only after mobile layout review.
- Add survival-kit links from related article bodies.
- Review Clarity heatmaps for translation card clicks, custom card usage, and checklist completion.
- Review persistent duplicate content-id build warnings for the three new growth posts after a clean environment build.
