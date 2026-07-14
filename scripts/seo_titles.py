"""Batch update SEO titles and meta descriptions for all English articles.
Format: "Keyphrase 2026: Step-by-Step Guide for Foreigners" / "Practical description with year + for foreigners."""

import os
import re

POSTS_DIR = r'D:\独立站\china-travel-kit\src\content\posts'

# (slug, new_title, new_description)
UPDATES = [
    ('alipay-foreign-credit-card-step-by-step.md',
     'Alipay for Foreigners 2026: How to Link a Foreign Credit Card Step by Step',
     'Complete 2026 guide to setting up Alipay as a foreign visitor: download the app, verify your passport, and link a Visa or Mastercard for payments anywhere in China.'),

    ('alipay-vs-wechat-pay-foreigners.md',
     'Alipay vs WeChat Pay for Foreigners 2026: Which Payment App Should You Use?',
     'Compare Alipay and WeChat Pay for your China trip in 2026 — setup difficulty, card support, fees, and which one works best for tourists, with step-by-step setup instructions.'),

    ('apple-pay-google-pay-in-china-what-really-works.md',
     'Apple Pay & Google Pay in China 2026: What Actually Works for Foreigners',
     'Can you use Apple Pay or Google Pay in China in 2026? A practical guide for foreign visitors on contactless payment options, limits, and when to use Alipay or WeChat instead.'),

    ('can-you-still-use-cash-in-china-as-a-foreigner-in-2026.md',
     'Can You Still Use Cash in China in 2026? A Foreign Visitor\'s Guide',
     'China is mostly cashless, but cash still works. This 2026 guide explains when you need cash, where to exchange currency, and how much RMB to carry as a backup payment method.'),

    ('how-much-cash-to-bring-to-china.md',
     'How Much Cash to Bring to China in 2026: Tourist Money Guide',
     'Practical cash advice for China travelers in 2026 — how much RMB to carry, where to exchange foreign currency, ATM fees, and how to balance cash with mobile payments.'),

    ('how-to-pay-in-china-tourist-guide.md',
     'How to Pay in China as a Tourist 2026: Complete Payment Guide',
     'Everything foreign tourists need to know about paying in China in 2026 — Alipay, WeChat Pay, foreign credit cards, cash backup, and step-by-step setup before departure.'),

    ('link-a-foreign-visa-or-mastercard-to-wechat-pay-in-china.md',
     'Link a Foreign Visa or Mastercard to WeChat Pay in China 2026: Step-by-Step',
     'Step-by-step 2026 guide to linking your foreign Visa or Mastercard to WeChat Pay — app setup, identity verification, card binding, and troubleshooting common errors.'),

    ('use-foreign-credit-card-in-china-directly.md',
     'Can You Use a Foreign Credit Card in China 2026? Where It Works',
     'Find out where foreign Visa and Mastercard credit cards are accepted in China in 2026 — hotels, ATMs, international chains — and when you still need Alipay or WeChat Pay.'),

    ('wechat-pay-foreign-visitors-guide.md',
     'WeChat Pay for Foreign Visitors 2026: Complete Setup and Usage Guide',
     'How to set up WeChat Pay as a foreign tourist in 2026 — download, registration, linking a foreign card, and using it for payments, transfers, and mini-programs in China.'),

    ('best-esim-for-china-travel-2026.md',
     'Best eSIM for China Travel 2026: How to Choose and Set Up (Airalo, Holafly, Nomad)',
     'Compare the best eSIM providers for China in 2026 — Airalo, Holafly, Nomad — with pricing, data limits, setup steps, and whether you can bypass the Great Firewall without a VPN.'),

    ('china-esim-vs-roaming-2026-the-real-10-day-cost.md',
     'China eSIM vs Roaming 2026: The Real 10-Day Cost Comparison for Tourists',
     'Should you buy a China eSIM or use your home carrier roaming in 2026? A practical cost and performance comparison for a 10-day trip, with recommendations by traveler type.'),

    ('do-you-need-a-vpn-in-china-2026.md',
     'Do You Need a VPN in China 2026? Tourist Internet Guide',
     'Do tourists still need a VPN in China in 2026? Practical guide to internet access, blocked apps, working VPNs, and eSIM options that bypass censorship for foreign visitors.'),

    ('internet-access-china-apps-that-work-2026.md',
     'Internet Access in China 2026: Which Apps Work for Tourists Without a VPN',
     'A practical 2026 guide to which apps work in China without a VPN, which are blocked, and how to stay connected with messaging, maps, and social media as a foreign tourist.'),

    ('pocket-wifi-vs-esim-vs-sim-china.md',
     'Pocket WiFi vs eSIM vs Local SIM in China 2026: Best Option for Tourists',
     'Compare Pocket WiFi, eSIM, and local SIM cards for China travel in 2026 — coverage, speed, ease of setup, and cost — to find the best internet option for your trip.'),

    ('airport-to-city-transport-beijing-shanghai-guangzhou.md',
     'Airport to City Transport in Beijing, Shanghai and Guangzhou 2026: Complete Guide',
     'How to get from the airport to city center in Beijing, Shanghai, and Guangzhou in 2026 — metro, airport express, taxi, Didi costs, times, and step-by-step instructions for first-time visitors.'),

    ('beijing-daxing-airport-to-city-center-a-first-timer-s-guide.md',
     'Beijing Daxing Airport to City Center 2026: First-Timer\'s Transport Guide',
     'Complete 2026 guide to getting from Beijing Daxing International Airport to the city center — airport express train, taxi costs, Didi, metro options, and tips for first-time visitors.'),

    ('book-china-train-tickets-12306-foreigners.md',
     'How to Book China Train Tickets on 12306 as a Foreigner 2026',
     'Step-by-step guide to booking China train tickets on 12306 with a foreign passport in 2026 — registration, verification, payment options, and alternative booking platforms.'),

    ('china-high-speed-rail-guide-foreigners.md',
     'China High-Speed Rail Guide for Foreigners 2026: Booking, Classes and Tips',
     'Essential 2026 guide to China\'s high-speed rail for foreign travelers — ticket classes, how to book with a passport, station navigation, onboard amenities, and money-saving tips.'),

    ('shanghai-metro-for-foreigners-tickets-qr-codes-transfers.md',
     'Shanghai Metro for Foreigners 2026: Tickets, QR Codes and Transfer Guide',
     'How to use the Shanghai metro as a foreign tourist in 2026 — ticket types, Alipay QR code entry, line transfers, airport connections, and practical tips for navigating the system.'),

    ('didi-china-foreign-tourists-guide.md',
     'Didi for Foreign Tourists 2026: How to Use China\'s Ride-Hailing App',
     'Step-by-step 2026 guide to using DiDi in China as a foreign tourist — English interface setup, adding payment methods, booking rides, and tips for airport and city travel.'),

    ('chengdu-street-food-safety-spice-levels-what-to-order.md',
     'Chengdu Street Food 2026: Safety, Spice Levels and What to Order',
     'Your practical 2026 guide to Chengdu street food — how to handle Sichuan spice levels, food safety tips, must-try dishes, and how to order without speaking Chinese.'),

    ('ordering-food-in-china-without-chinese-meituan-ele-me.md',
     'Ordering Food in China Without Chinese 2026: Meituan, Ele.me and Restaurant Tips',
     'How to order food delivery in China without speaking Chinese in 2026 — using Meituan and Ele.me, H5 web alternatives, Alipay mini-programs, and restaurant ordering tips for foreigners.'),

    ('china-trip-planner-first-time-visitors-payment-esim-transport-apps.md',
     'China Trip Planner 2026: Payment, eSIM, Transport and Apps for First-Time Visitors',
     'Complete China trip planner for first-time visitors in 2026 — what to set up before departure: payments, eSIM, transport apps, packing checklist, and a 24-hour arrival plan.'),

    ('china-visa-free-entry-transit-guide-2026.md',
     'China Visa-Free Entry and Transit 2026: Do You Need a Visa?',
     'Complete 2026 guide to China visa-free entry, 240-hour transit, and visa policies by nationality — eligibility checker, airport processes, required documents, and common questions for foreign travelers.'),

    ('first-24-hours-in-china-arrival-checklist.md',
     'First 24 Hours in China 2026: Complete Arrival Checklist for Foreign Visitors',
     'What to do in your first 24 hours in China as a foreign tourist — airport arrival checklist, getting internet, setting up Alipay, using Didi, and navigating to your hotel without stress.'),

    ('tipping-in-china-when-it-s-expected-and-when-it-s-not.md',
     'Tipping in China 2026: When It\'s Expected and When It\'s Not (Tourist Guide)',
     'Should you tip in China in 2026? Practical guide for foreign visitors — which services expect tips, which do not, how much to tip at hotels and restaurants, and cultural etiquette to avoid awkward moments.'),

    ('what-to-pack-for-china-a-season-by-season-checklist.md',
     'What to Pack for China 2026: Season-by-Season Checklist for Foreign Tourists',
     'Ultimate packing checklist for China travel in 2026 — what to pack by season (spring, summer, autumn, winter), essential apps and documents, luggage tips, and items you should not forget.'),

    ('what-to-set-up-before-traveling-to-china-alipay-esim-didi-train-tickets.md',
     'What to Set Up Before Traveling to China 2026: Apps, Payments and Documents',
     'Essential pre-departure checklist for China 2026 — install Alipay and WeChat Pay, buy an eSIM, set up Didi and 12306, download translation apps, and prepare your documents before you fly.'),

    ('why-china-does-not-have-a-tipping-culture.md',
     'Why China Does Not Have a Tipping Culture: A Foreigner\'s Guide to Service Etiquette',
     'Understand why tipping is not customary in China — cultural differences, when service charges apply, how to show appreciation without tipping, and practical etiquette for foreign visitors.'),

    ('beijing-city-guide-for-foreigners.md',
     'Beijing City Guide for Foreigners 2026: What to Know Before You Go',
     'Complete 2026 guide to Beijing for first-time foreign visitors — top attractions, getting around, food, accommodation areas, Great Wall day trips, and practical travel tips.'),

    ('shanghai-city-guide-for-foreigners.md',
     'Shanghai City Guide for Foreigners 2026: What to Know Before You Go',
     'Complete 2026 guide to Shanghai for foreign tourists — best areas to stay, top attractions, metro tips, food recommendations, day trips, and practical advice for a smooth visit.'),

    ('chengdu-city-guide-for-foreigners.md',
     'Chengdu City Guide for Foreigners 2026: Pandas, Food and Travel Tips',
     'Complete 2026 guide to Chengdu for foreign visitors — panda bases, Sichuan food, teahouses, transport tips, day trips, and practical advice for enjoying this food capital of China.'),

    ('hangzhou-city-guide-for-foreigners.md',
     'Hangzhou City Guide for Foreigners 2026: West Lake and Beyond',
     'Complete 2026 guide to Hangzhou for foreign tourists — West Lake attractions, tea culture, day trips from Shanghai, transport tips, and practical advice for a weekend visit.'),

    ('sanya-city-guide-for-foreigners.md',
     'Sanya City Guide for Foreigners 2026: Beaches, Resorts and Travel Tips',
     'Complete 2026 guide to Sanya for foreign visitors — best beaches, resort areas, water activities, Hainan Island tips, winter sun escape planning, and practical transport advice.'),
]


def update_file(filepath, new_title, new_desc):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_title_match = re.search(r'^title: "(.+)"', content, re.MULTILINE)
    old_desc_match = re.search(r'^description: "(.+)"', content, re.MULTILINE)

    if not old_title_match or not old_desc_match:
        print(f'  SKIP {os.path.basename(filepath)}: title or description not found')
        return False

    # Replace title
    content = content.replace(
        f'title: "{old_title_match.group(1)}"',
        f'title: "{new_title}"'
    )
    # Replace description
    content = content.replace(
        f'description: "{old_desc_match.group(1)}"',
        f'description: "{new_desc}"'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'  UPDATED {os.path.basename(filepath)}')
    print(f'    Title:    {new_title}')
    print(f'    Desc:     {new_desc[:80]}...')
    return True


def main():
    success = 0
    for filename, new_title, new_desc in UPDATES:
        filepath = os.path.join(POSTS_DIR, filename)
        if not os.path.exists(filepath):
            print(f'  NOT FOUND {filename}')
            continue
        if update_file(filepath, new_title, new_desc):
            success += 1

    print(f'\nDone: {success}/{len(UPDATES)} articles updated')


if __name__ == '__main__':
    main()
