from pathlib import Path
import re
from deep_translator import GoogleTranslator

paths = [
    r'D:/独立站/china-travel-kit/src/pages/es/digital-nomads/ai-opc/index.astro',
    r'D:/独立站/china-travel-kit/src/pages/es/long-stay/index.astro',
    r'D:/独立站/china-travel-kit/src/pages/es/digital-nomads/index.astro',
    r'D:/独立站/china-travel-kit/src/pages/es/digital-nomads/payment.astro',
    r'D:/独立站/china-travel-kit/src/pages/es/digital-nomads/visa.astro',
    r'D:/独立站/china-travel-kit/src/pages/es/travel-help.astro',
    r'D:/独立站/china-travel-kit/src/pages/es/privacy.astro',
    r'D:/独立站/china-travel-kit/src/pages/es/trip-planner.astro',
    r'D:/独立站/china-travel-kit/src/pages/es/tools/visa-free-checker.astro',
    r'D:/独立站/china-travel-kit/src/pages/es/tools/payment-checker.astro',
    r'D:/独立站/china-travel-kit/src/pages/es/tools/show-to-driver.astro',
    r'D:/独立站/china-travel-kit/src/pages/es/terms.astro',
]

translator = GoogleTranslator(source='auto', target='es')
cache = {}

brand_replacements = {
    'Alipay': 'Alipay',
    'WeChat Pay': 'WeChat Pay',
    'WeChat': 'WeChat',
    'DiDi': 'DiDi',
    'Apple Pay': 'Apple Pay',
    'Google Translate': 'Google Translate',
    'Google Play': 'Google Play',
    'Google': 'Google',
    'Baidu': 'Baidu',
    'Amap': 'Amap',
    'Meituan': 'Meituan',
    'Ele.me': 'Ele.me',
    'Trip.com': 'Trip.com',
    'ExpressVPN': 'ExpressVPN',
    'NordVPN': 'NordVPN',
    'ChinaTripBox': 'ChinaTripBox',
    'App Store': 'App Store',
    '12306': '12306',
    'AI': 'AI',
    'eSIM': 'eSIM',
    'RMB': 'RMB',
    'QR': 'QR',
    'SaaS': 'SaaS',
}

skip_exact = {
    'GuideLayout', 'BaseLayout', 'Header', 'Footer', 'AdSlot', 'AffiliateCta', 'FaqSection',
    'banner', 'cover-ai-opc', 'cover-long-stay', 'cover-digital-nomads', 'cover-payment', 'cover-visa',
    'POST', 'content-type', 'application/json', 'hidden', 'smooth', 'start', 'polite',
    'Visa', 'Mastercard', 'Amex', 'Discover', 'UnionPay', 'American Express',
    'good', 'warn', 'info', 'tourism', 'business', 'transit', 'payment', 'esim', 'transport',
    'hotel', 'apps', 'cash', 'visa', 'food', 'route', 'pickup', 'stop', 'receipt',
}

def should_skip_text(s: str) -> bool:
    t = s.strip()
    if not t or not re.search(r'[A-Za-z]', t):
        return True
    if t in skip_exact:
        return True
    if t.startswith(('/', 'http', 'mailto:', '#', '.', 'api/')):
        return True
    if re.fullmatch(r'[A-Za-z0-9_./:#?=&%{}${}\-\[\](),| ]+', t):
        # Skip obvious code, selectors, routes, IDs, class lists, and paths.
        if any(x in t for x in ['/', '#', '${', '=>', 'input[', 'rounded-', 'text-', 'bg-', 'border-', 'grid ', 'flex ', 'mt-', 'px-', 'py-', 'md:', 'lg:', 'sm:', 'hover:', 'focus:', 'http']):
            return True
        if re.fullmatch(r'[A-Za-z0-9_-]+', t):
            return True
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', t):
        return True
    return False

def translate(s: str) -> str:
    if should_skip_text(s):
        return s
    lead = s[:len(s) - len(s.lstrip())]
    trail = s[len(s.rstrip()):]
    core = s.strip()
    if core in cache:
        out = cache[core]
    else:
        protected = core
        placeholders = {}
        for i, brand in enumerate(sorted(brand_replacements, key=len, reverse=True)):
            token = f'__BRAND_{i}__'
            protected = protected.replace(brand, token)
            placeholders[token] = brand_replacements[brand]
        try:
            out = translator.translate(protected)
        except Exception:
            out = core
        for token, brand in placeholders.items():
            out = out.replace(token, brand)
            out = out.replace(token.lower(), brand)
        out = out.replace('Porcelana', 'China').replace('Chino', 'China').replace('china continental', 'China continental')
        out = out.replace('Ai', 'AI').replace('E SIM', 'eSIM').replace('Esim', 'eSIM')
        cache[core] = out
    return lead + out + trail

string_re = re.compile(r"(?P<q>['\"])(?P<body>(?:\\.|(?!\1).)*?[A-Za-z](?:\\.|(?!\1).)*?)(?P=q)", re.S)

def translate_strings(text: str) -> str:
    def repl(m):
        body = m.group('body')
        # Import specifiers, routes, URLs, CSS-ish strings, and obvious keys stay intact.
        if should_skip_text(body):
            return m.group(0)
        return m.group('q') + translate(body) + m.group('q')
    return string_re.sub(repl, text)

def translate_text_nodes(text: str) -> str:
    def repl(m):
        inner = m.group(1)
        if should_skip_text(inner):
            return '>' + inner + '<'
        return '>' + translate(inner) + '<'
    return re.sub(r'>([^<>{}]+)<', repl, text)

def translate_attrs(text: str) -> str:
    attrs = {'placeholder', 'aria-label', 'title', 'description', 'buttonText', 'coverAlt', 'data-prompt'}
    pattern = re.compile(r'\b(' + '|'.join(attrs) + r')=(["\'])(.*?[A-Za-z].*?)\2', re.S)
    def repl(m):
        return f'{m.group(1)}={m.group(2)}{translate(m.group(3))}{m.group(2)}'
    return pattern.sub(repl, text)

for path in paths:
    with open(r'' + path, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = content.split('---', 2)
    if len(parts) == 3:
        before, fm, rest = parts
        fm = translate_strings(fm)
        content = before + '---' + fm + '---' + rest

    # Translate non-style parts first, then script string literals conservatively.
    blocks = re.split(r'(<style[\s\S]*?</style>)', content)
    out_blocks = []
    for block in blocks:
        if block.startswith('<style'):
            out_blocks.append(block)
            continue
        script_parts = re.split(r'(<script[\s\S]*?</script>)', block)
        for part in script_parts:
            if part.startswith('<script'):
                out_blocks.append(translate_strings(part))
            else:
                part = translate_attrs(part)
                part = translate_text_nodes(part)
                out_blocks.append(part)
    content = ''.join(out_blocks)

    with open(r'' + path, 'w', encoding='utf-8') as f:
        f.write(content)
