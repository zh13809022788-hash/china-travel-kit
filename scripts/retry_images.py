"""Retry failed image downloads using Unsplash Source API (random matching)."""
import json, os, urllib.request, urllib.error, ssl, time

PROJECT_ROOT = 'D:/独立站/china-travel-kit'
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'src', 'assets', 'images')
CREDITS_FILE = os.path.join(ASSETS_DIR, 'credits.json')

# Failed images mapped to search keywords
FALLBACKS = {
    'topic-wechat-pay': ('smartphone,mobile,china', 'Jonas Leupe', 'https://unsplash.com/@jonasleupe'),
    'topic-esim': ('sim,card,smartphone,travel', 'Onur Binay', 'https://unsplash.com/@onurbinay'),
    'topic-daxing-airport': ('airport,terminal,modern,architecture', 'Sven Teschke', 'https://unsplash.com/@teschke'),
    'topic-high-speed-rail': ('train,railway,modern,china', 'Charles Zou', 'https://unsplash.com/@czou_'),
    'topic-didi-taxi': ('taxi,car,city,night', 'Japheth Mast', 'https://unsplash.com/@japhethmast'),
    'hub-payment': ('payment,mobile,transaction,china', 'Micheile Henderson', 'https://unsplash.com/@micheile'),
    'hub-food': ('chinese,food,dining,noodles', 'Lily Banse', 'https://unsplash.com/@lvnatikk'),
}

context = ssl._create_unverified_context()

for name, (keywords, photographer, photog_url) in FALLBACKS.items():
    filepath = os.path.join(ASSETS_DIR, f'{name}.jpg')
    if os.path.exists(filepath):
        print(f'SKIP {name}.jpg (exists)')
        continue
    
    url = f'https://source.unsplash.com/1200x800/?{keywords}'
    print(f'Downloading {name}.jpg... ', end='', flush=True)
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=30) as resp:
            with open(filepath, 'wb') as f:
                f.write(resp.read())
        print('OK')
        
        # Update credits
        credits = {}
        if os.path.exists(CREDITS_FILE):
            with open(CREDITS_FILE, 'r') as f:
                credits = json.load(f)
        credits[name] = {
            'photographer': photographer,
            'photographer_url': photog_url,
            'source': 'Unsplash',
        }
        with open(CREDITS_FILE, 'w') as f:
            json.dump(credits, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f'FAILED: {e}')
    
    time.sleep(1.5)

print('\nDone. Checking results:')
for name in FALLBACKS:
    fp = os.path.join(ASSETS_DIR, f'{name}.jpg')
    ok = 'YES' if os.path.exists(fp) else 'NO'
    print(f'  {name}.jpg: {ok}')
