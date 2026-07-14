"""Batch add cover and coverAlt frontmatter fields to article markdown files."""

import os
import re

POSTS_DIR = r'D:\独立站\china-travel-kit\src\content\posts'

COVER_MAP = {
    'alipay-foreign-credit-card-step-by-step.md': ('topic-alipay', 'Alipay mobile payment app on a smartphone with Chinese yuan notes'),
    'alipay-vs-wechat-pay-foreigners.md': ('topic-alipay-vs-wechat', 'Two smartphones showing Alipay and WeChat Pay payment QR codes'),
    'apple-pay-google-pay-in-china-what-really-works.md': ('topic-apple-pay-google-pay', 'Contactless payment with a smartphone at a retail terminal'),
    'can-you-still-use-cash-in-china-as-a-foreigner-in-2026.md': ('topic-cash-china', 'Chinese yuan banknotes and coins spread on a surface'),
    'how-much-cash-to-bring-to-china.md': ('topic-cash-china', 'Chinese yuan banknotes and coins spread on a surface'),
    'how-to-pay-in-china-tourist-guide.md': ('topic-how-to-pay', 'Various payment methods including smartphone and cards arranged on a table'),
    'link-a-foreign-visa-or-mastercard-to-wechat-pay-in-china.md': ('topic-credit-card', 'Foreign Visa and Mastercard credit cards arranged on a surface'),
    'use-foreign-credit-card-in-china-directly.md': ('topic-credit-card', 'Foreign credit card being used at a payment terminal'),
    'wechat-pay-foreign-visitors-guide.md': ('topic-alipay-vs-wechat', 'WeChat Pay mobile payment interface on a smartphone'),
    'best-esim-for-china-travel-2026.md': ('topic-esim-vs-roaming', 'eSIM setup screen on a smartphone with data plan options'),
    'china-esim-vs-roaming-2026-the-real-10-day-cost.md': ('topic-esim-vs-roaming', 'Comparison of eSIM and roaming data plans on two smartphones'),
    'do-you-need-a-vpn-in-china-2026.md': ('topic-vpn-great-firewall', 'The Great Wall of China with digital network overlay concept'),
    'internet-access-china-apps-that-work-2026.md': ('topic-internet-apps', 'Smartphone screen with various app icons for internet access'),
    'pocket-wifi-vs-esim-vs-sim-china.md': ('topic-pocket-wifi', 'Pocket WiFi device, eSIM card and local SIM card arranged for comparison'),
    'airport-to-city-transport-beijing-shanghai-guangzhou.md': ('topic-airport-transport', 'Airport express train platform with modern train in station'),
    'book-china-train-tickets-12306-foreigners.md': ('topic-12306-train', 'China train ticket booking app on smartphone with railway station background'),
    'china-high-speed-rail-guide-foreigners.md': None,
    'shanghai-metro-for-foreigners-tickets-qr-codes-transfers.md': ('topic-shanghai-metro', 'Shanghai metro station platform with modern subway train'),
    'beijing-daxing-airport-to-city-center-a-first-timer-s-guide.md': None,
    'didi-china-foreign-tourists-guide.md': None,
    'chengdu-street-food-safety-spice-levels-what-to-order.md': ('topic-chengdu-food', 'Spicy Sichuan street food dishes at a night market stall'),
    'ordering-food-in-china-without-chinese-meituan-ele-me.md': ('topic-food-delivery', 'Food delivery packaging with a smartphone showing ordering app'),
    'china-trip-planner-first-time-visitors-payment-esim-transport-apps.md': ('topic-trip-planner', 'Travel planning setup with map, smartphone, passport and itinerary'),
    'china-visa-free-entry-transit-guide-2026.md': ('topic-visa-free', 'Passport with Chinese visa stamps and boarding pass'),
    'first-24-hours-in-china-arrival-checklist.md': ('topic-first-24-hours', 'International airport arrival hall with luggage and signage'),
    'tipping-in-china-when-it-s-expected-and-when-it-s-not.md': ('topic-tipping-china', 'Restaurant table setting with meal and dining atmosphere'),
    'what-to-pack-for-china-a-season-by-season-checklist.md': ('topic-packing-checklist', 'Open suitcase with travel essentials and clothing for different seasons'),
    'what-to-set-up-before-traveling-to-china-alipay-esim-didi-train-tickets.md': ('topic-predeparture-setup', 'Smartphone setup checklist with travel apps and passport nearby'),
    'why-china-does-not-have-a-tipping-culture.md': ('topic-no-tipping-culture', 'Chinese dining table with dishes in a casual restaurant setting'),
}

def add_cover_to_file(filepath, cover_name, cover_alt):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if cover already exists
    if re.search(r'^cover:', content, re.MULTILINE):
        print(f'  SKIP {os.path.basename(filepath)} (already has cover)')
        return False
    
    # Find the position after tags: line and before faqs: or the first non-frontmatter field after tags
    # We want to insert cover and coverAlt right after the tags line
    pattern = r'^(tags:.*)$'
    match = re.search(pattern, content, re.MULTILINE)
    
    if not match:
        print(f'  ERROR {os.path.basename(filepath)}: no tags field found')
        return False
    
    tags_end = match.end()
    cover_block = f'\ncover: "{cover_name}"\ncoverAlt: "{cover_alt}"'
    
    # Handle indentation: preserve the indentation of the tags line
    frontmatter_end = content.index('---', 3)  # Second ---
    line_after_tags = content[tags_end:].split('\n', 1)
    if len(line_after_tags) > 1:
        rest = line_after_tags[1]
    else:
        rest = ''
    
    new_content = content[:tags_end] + cover_block + '\n' + content[tags_end:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f'  ADDED cover to {os.path.basename(filepath)}')
    return True


def main():
    modified = 0
    skipped = 0
    
    for filename, mapping in COVER_MAP.items():
        filepath = os.path.join(POSTS_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f'  NOT FOUND {filename}')
            continue
        
        if mapping is None:
            print(f'  SKIP {filename} (no image assigned)')
            continue
        
        cover_name, cover_alt = mapping
        
        if add_cover_to_file(filepath, cover_name, cover_alt):
            modified += 1
        else:
            skipped += 1
    
    print(f'\nDone: {modified} modified, {skipped} skipped')
    
    # Verify by checking which files now have cover
    print('\n--- Verification ---')
    for f in sorted(os.listdir(POSTS_DIR)):
        if f.endswith('.md'):
            fp = os.path.join(POSTS_DIR, f)
            with open(fp, 'r', encoding='utf-8') as fh:
                content = fh.read(500)
            has_cover = 'cover:' in content
            has_cover_alt = 'coverAlt:' in content
            print(f'  {f}: cover={has_cover}, coverAlt={has_cover_alt}')


if __name__ == '__main__':
    main()
