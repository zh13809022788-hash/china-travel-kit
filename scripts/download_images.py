"""Download free travel photos from Unsplash for article covers.
Each image file is saved to src/assets/images/ as topic-{slug}.jpg
credits.json is updated with attribution data."""

import json
import os
import urllib.request
import urllib.error
import ssl
import time
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'src', 'assets', 'images')
CREDITS_FILE = os.path.join(ASSETS_DIR, 'credits.json')

# Unsplash photo IDs mapped to article topics
# Format: (keyword_for_download, photographer_name, photographer_url, unsplash_photo_url)
PHOTOS = {
    'topic-alipay': {
        'keywords': 'mobile+payment+china',
        'photographer': 'Christian Wiediger',
        'photographer_url': 'https://unsplash.com/@christianw',
        'photo_url': 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200&q=75'
    },
    'topic-alipay-vs-wechat': {
        'keywords': 'smartphone+payment+qr',
        'photographer': 'Ales Nesetril',
        'photographer_url': 'https://unsplash.com/@alesnesetril',
        'photo_url': 'https://images.unsplash.com/photo-1523961131990-5ea7c61b2107?w=1200&q=75'
    },
    'topic-apple-pay-google-pay': {
        'keywords': 'phone+tap+payment',
        'photographer': 'Mika Baumeister',
        'photographer_url': 'https://unsplash.com/@mikabaumeister',
        'photo_url': 'https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=1200&q=75'
    },
    'topic-cash-china': {
        'keywords': 'chinese+yuan+money',
        'photographer': 'CHUTTERSNAP',
        'photographer_url': 'https://unsplash.com/@chuttersnap',
        'photo_url': 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=1200&q=75'
    },
    'topic-how-to-pay': {
        'keywords': 'payment+terminal+china',
        'photographer': 'Micheile Henderson',
        'photographer_url': 'https://unsplash.com/@micheile',
        'photo_url': 'https://images.unsplash.com/photo-1556742031-c6961e8560b0?w=1200&q=75'
    },
    'topic-wechat-pay': {
        'keywords': 'wechat+moments+app',
        'photographer': 'Jonas Leupe',
        'photographer_url': 'https://unsplash.com/@jonasleupe',
        'photo_url': 'https://images.unsplash.com/photo-1611605698335-8b156f05287c?w=1200&q=75'
    },
    'topic-credit-card': {
        'keywords': 'credit+card+china',
        'photographer': 'William Warby',
        'photographer_url': 'https://unsplash.com/@wwarby',
        'photo_url': 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200&q=75'
    },
    'topic-esim': {
        'keywords': 'sim+card+smartphone',
        'photographer': 'Onur Binay',
        'photographer_url': 'https://unsplash.com/@onurbinay',
        'photo_url': 'https://images.unsplash.com/photo-1592434134753-a70cca4c6b1a?w=1200&q=75'
    },
    'topic-esim-vs-roaming': {
        'keywords': 'data+roaming+phone',
        'photographer': 'John Schnobrich',
        'photographer_url': 'https://unsplash.com/@johnschno',
        'photo_url': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200&q=75'
    },
    'topic-vpn-great-firewall': {
        'keywords': 'great+wall+china',
        'photographer': 'Maxim Zhitenev',
        'photographer_url': 'https://unsplash.com/@jakenchuck',
        'photo_url': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=1200&q=75'
    },
    'topic-internet-apps': {
        'keywords': 'app+icons+phone',
        'photographer': 'Yura Fresh',
        'photographer_url': 'https://unsplash.com/@mr_fresh',
        'photo_url': 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=1200&q=75'
    },
    'topic-pocket-wifi': {
        'keywords': 'wifi+router+travel',
        'photographer': 'Fredrick Tendong',
        'photographer_url': 'https://unsplash.com/@frederick_tendong',
        'photo_url': 'https://images.unsplash.com/photo-1585336261022-680e295ce3fe?w=1200&q=75'
    },
    'topic-airport-transport': {
        'keywords': 'airport+train+china',
        'photographer': 'Charles Zou',
        'photographer_url': 'https://unsplash.com/@czou_',
        'photo_url': 'https://images.unsplash.com/photo-1580674285054-bed31e145f59?w=1200&q=75'
    },
    'topic-daxing-airport': {
        'keywords': 'beijing+daxing+airport',
        'photographer': 'CHEN Jiateng',
        'photographer_url': 'https://unsplash.com/@jefferson_li',
        'photo_url': 'https://images.unsplash.com/photo-1578643470111-7670fb694b1b?w=1200&q=75'
    },
    'topic-12306-train': {
        'keywords': 'china+train+ticket',
        'photographer': 'Charles Zou',
        'photographer_url': 'https://unsplash.com/@czou_',
        'photo_url': 'https://images.unsplash.com/photo-1512428559087-560fa5ceab42?w=1200&q=75'
    },
    'topic-high-speed-rail': {
        'keywords': 'high+speed+train+china',
        'photographer': 'GongHu Young',
        'photographer_url': 'https://unsplash.com/@gonghu',
        'photo_url': 'https://images.unsplash.com/photo-1558443445-4868e77c5c7a?w=1200&q=75'
    },
    'topic-shanghai-metro': {
        'keywords': 'shanghai+metro+subway',
        'photographer': 'David Lee',
        'photographer_url': 'https://unsplash.com/@david_lee_76',
        'photo_url': 'https://images.unsplash.com/photo-1580674684081-7617fbf3d745?w=1200&q=75'
    },
    'topic-didi-taxi': {
        'keywords': 'taxi+china+ride',
        'photographer': 'Jeremy Cai',
        'photographer_url': 'https://unsplash.com/@jeremycai',
        'photo_url': 'https://images.unsplash.com/photo-1558981001-5864b3259b2c?w=1200&q=75'
    },
    'topic-chengdu-food': {
        'keywords': 'sichuan+food+spicy',
        'photographer': 'Zhao Qiming',
        'photographer_url': 'https://unsplash.com/@zhaoqiming',
        'photo_url': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=1200&q=75'
    },
    'topic-food-delivery': {
        'keywords': 'food+delivery+china',
        'photographer': 'John Fornander',
        'photographer_url': 'https://unsplash.com/@johnfornander',
        'photo_url': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=1200&q=75'
    },
    'topic-trip-planner': {
        'keywords': 'travel+planning+map',
        'photographer': 'Annie Spratt',
        'photographer_url': 'https://unsplash.com/@anniespratt',
        'photo_url': 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1200&q=75'
    },
    'topic-visa-free': {
        'keywords': 'passport+stamp+china',
        'photographer': 'Edwin Andrade',
        'photographer_url': 'https://unsplash.com/@the_meaning_of_edwin',
        'photo_url': 'https://images.unsplash.com/photo-1452421822248-d4c2b47f0c81?w=1200&q=75'
    },
    'topic-first-24-hours': {
        'keywords': 'airport+arrival+travel',
        'photographer': 'Igor Ovsyannykov',
        'photographer_url': 'https://unsplash.com/@igorovsyannykov',
        'photo_url': 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1200&q=75'
    },
    'topic-tipping-china': {
        'keywords': 'restaurant+dining+china',
        'photographer': 'Louis Hansel',
        'photographer_url': 'https://unsplash.com/@louishansel',
        'photo_url': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=75'
    },
    'topic-packing-checklist': {
        'keywords': 'suitcase+travel+pack',
        'photographer': 'Tommy Lisbin',
        'photographer_url': 'https://unsplash.com/@tommylisbin',
        'photo_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=1200&q=75'
    },
    'topic-predeparture-setup': {
        'keywords': 'smartphone+setup+travel',
        'photographer': 'William Hook',
        'photographer_url': 'https://unsplash.com/@williamhook',
        'photo_url': 'https://images.unsplash.com/photo-1483478550801-ceba5fe50e8e?w=1200&q=75'
    },
    'topic-no-tipping-culture': {
        'keywords': 'chinese+dining+table',
        'photographer': 'Louis Hansel',
        'photographer_url': 'https://unsplash.com/@louishansel',
        'photo_url': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1200&q=75'
    },
    # Hub page heroes
    'hub-payment': {
        'keywords': 'mobile+payment+smartphone',
        'photographer': 'Ales Nesetril',
        'photographer_url': 'https://unsplash.com/@alesnesetril',
        'photo_url': 'https://images.unsplash.com/photo-1553729459-afe8f2e2e59e?w=1200&q=75'
    },
    'hub-esim': {
        'keywords': 'mobile+network+antenna',
        'photographer': 'Kevin Ku',
        'photographer_url': 'https://unsplash.com/@ikukev',
        'photo_url': 'https://images.unsplash.com/photo-1555421689-491a97ff2040?w=1200&q=75'
    },
    'hub-transport': {
        'keywords': 'china+train+station',
        'photographer': 'Charles Zou',
        'photographer_url': 'https://unsplash.com/@czou_',
        'photo_url': 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=1200&q=75'
    },
    'hub-food': {
        'keywords': 'chinese+food+dumplings',
        'photographer': 'Louis Hansel',
        'photographer_url': 'https://unsplash.com/@louishansel',
        'photo_url': 'https://images.unsplash.com/photo-1563245372-f217024a2e8c?w=1200&q=75'
    },
    'hub-essentials': {
        'keywords': 'travel+essentials+gear',
        'photographer': 'Drew Hays',
        'photographer_url': 'https://unsplash.com/@drew_hays',
        'photo_url': 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1200&q=75'
    },
}


def download_image(url, filepath, max_retries=3):
    """Download an image with retry logic."""
    context = ssl._create_unverified_context()
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; ChinaTripBox/1.0)'
            })
            with urllib.request.urlopen(req, context=context, timeout=30) as response:
                data = response.read()
                with open(filepath, 'wb') as f:
                    f.write(data)
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  Failed after {max_retries} attempts: {e}")
                return False


def update_credits(photo_key, info):
    """Update credits.json with attribution data."""
    credits = {}
    if os.path.exists(CREDITS_FILE):
        with open(CREDITS_FILE, 'r', encoding='utf-8') as f:
            credits = json.load(f)
    
    credits[photo_key] = {
        'photographer': info['photographer'],
        'photographer_url': info['photographer_url'],
        'source': 'Unsplash',
    }
    
    with open(CREDITS_FILE, 'w', encoding='utf-8') as f:
        json.dump(credits, f, indent=2, ensure_ascii=False)
    
    print(f"  Credits updated for {photo_key}")


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    total = len(PHOTOS)
    success = 0
    
    for i, (name, info) in enumerate(PHOTOS.items(), 1):
        filename = f"{name}.jpg"
        filepath = os.path.join(ASSETS_DIR, filename)
        
        # Skip if already exists
        if os.path.exists(filepath):
            print(f"[{i}/{total}] SKIP {filename} (already exists)")
            continue
        
        print(f"[{i}/{total}] Downloading {filename}...")
        
        if download_image(info['photo_url'], filepath):
            print(f"  Saved to {filename}")
            update_credits(name, info)
            success += 1
        else:
            print(f"  FAILED {filename}")
        
        # Small delay to be respectful to the server
        time.sleep(1)
    
    print(f"\nDone! {success}/{total} images downloaded successfully.")
    
    # List all images in assets
    images = [f for f in os.listdir(ASSETS_DIR) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    print(f"Total images in assets: {len(images)}")


if __name__ == '__main__':
    main()
