import re
from pathlib import Path
import argostranslate.translate as argos

ROOT = Path(r'D:\独立站\china-travel-kit')
FILES = [
  r'src/pages/ko/long-stay/index.astro',
  r'src/pages/ko/digital-nomads/payment.astro',
  r'src/pages/ko/digital-nomads/ai-opc/index.astro',
  r'src/pages/ko/digital-nomads/index.astro',
  r'src/pages/ko/digital-nomads/visa.astro',
  r'src/pages/ko/trip-planner.astro',
  r'src/pages/ko/tools/visa-free-checker.astro',
  r'src/pages/ko/travel-help.astro',
  r'src/pages/ko/privacy.astro',
  r'src/pages/ko/apps/index.astro',
  r'src/pages/ko/tools/payment-checker.astro',
  r'src/pages/ko/terms.astro',
  r'src/pages/ko/resources.astro',
  r'src/pages/ko/about.astro',
  r'src/pages/ko/tools/show-to-driver.astro',
  r'src/pages/ko/editorial-policy.astro',
  r'src/pages/ko/tools/power-plug-checker.astro',
  r'src/pages/ko/series/index.astro',
  r'src/pages/ko/tools/best-time-to-visit.astro',
  r'src/pages/ko/authors/chinatripbox-editorial-team.astro',
  r'src/pages/ko/cities/index.astro',
  r'src/pages/ko/contact.astro',
  r'src/pages/ko/affiliate-disclosure.astro',
  r'src/pages/ko/tools/survival-kit.astro',
  r'src/pages/ko/esim/index.astro',
  r'src/pages/ko/payment/index.astro',
  r'src/pages/ko/tools/budget-cash-estimator.astro',
  r'src/pages/ko/tools/currency-converter.astro',
  r'src/pages/ko/tools/index.astro',
  r'src/pages/ko/series/culture-of-china.astro',
  r'src/pages/ko/tools/clothing-size-converter.astro',
  r'src/pages/ko/tools/esim-comparison.astro',
  r'src/pages/ko/tools/essential-phrases.astro',
]

BRANDS = ['ExpressVPN', 'NordVPN', 'Google Play', 'App Store', 'ChinaTripBox', 'WeChat', 'Alipay', 'Meituan', 'Google', 'Baidu', 'DiDi', 'China']
brand_map = {f'__BRAND{i}__': b for i, b in enumerate(BRANDS)}
cache = {}
translator = argos.get_translation_from_codes('en', 'ko')
if translator is None:
    raise RuntimeError('Argos en->ko model is not installed')

hangul = re.compile(r'[가-힣]')
latin = re.compile(r'[A-Za-z]')

manual = {
    'Home': '홈',
    'Tool': '도구',
    'Tools': '도구',
    'All': '전체',
    'FAQ': '자주 묻는 질문',
    'Contact': '문의',
    'Privacy Policy': '개인정보 처리방침',
    'Terms': '이용약관',
    'Affiliate Disclosure': '제휴 고지',
    'Editorial Policy': '편집 정책',
    'Resources': '자료',
    'Cities': '도시',
    'Series': '시리즈',
    'Payment': '결제',
    'Payments': '결제',
    'Transport': '교통',
    'Internet': '인터넷',
    'Trip Planning': '여행 준비',
    'Digital Nomads': '디지털 노마드',
    'Long Stay': '장기 체류',
    'Travel Help': '여행 도움말',
    'Last updated:': '최종 업데이트:',
    'Last reviewed:': '최종 검토:',
    'Print / Save PDF': '인쇄 / PDF 저장',
    'Start planning': '계획 시작하기',
    'Ask travel help': '여행 도움 요청',
    'Generate plan': '계획 생성',
    'Check My Eligibility': '자격 확인하기',
    'Get Connected': '인터넷 준비하기',
    'See Travel Essentials': '여행 필수 준비 보기',
    'Read first-time guide': '첫 여행 가이드 읽기',
    'Read the full visa-free guide': '무비자 전체 가이드 읽기',
    'Use the arrival checklist': '도착 체크리스트 사용하기',
    'Plan airport transport': '공항 교통 계획하기',
}

def protect(text):
    out = text
    for ph, brand in brand_map.items():
        out = re.sub(re.escape(brand), ph, out)
    return out

def unprotect(text):
    out = text
    for ph, brand in brand_map.items():
        out = out.replace(ph, brand)
    return out

def looks_codeish(s):
    st = s.strip()
    if not st:
        return True
    if '${' in st or '{' in st or '}' in st:
        return True
    if st.startswith(('http://','https://','mailto:','/','#','.', '../','./')):
        return True
    if any(x in st for x in ['.astro', '.com', '@', '://', 'AFFILIATE_LINKS', 'document.', 'window.', 'querySelector']):
        return True
    if re.fullmatch(r'[a-z0-9_-]+', st):
        return True
    if re.fullmatch(r'[A-Z0-9_]+', st):
        return True
    if len(st.split()) >= 2:
        toks = st.split()
        classish = sum(1 for t in toks if re.search(r'[:\[\]/_-]', t) or t in {'flex','grid','hidden','block','inline-flex','container-page','card','btn-primary','btn-outline'})
        if classish >= max(2, len(toks)//2):
            return True
    return False

def should_translate(s):
    st = s.strip()
    if not latin.search(st):
        return False
    if looks_codeish(st):
        return False
    # Skip tiny unit strings that are more likely ids/types than visible copy.
    if len(st) <= 2:
        return False
    return True

def translate_text(s):
    if not should_translate(s):
        return s
    lead = s[:len(s)-len(s.lstrip())]
    trail = s[len(s.rstrip()):]
    core = s.strip()
    if core in manual:
        return lead + manual[core] + trail
    if core in cache:
        return lead + cache[core] + trail
    src = protect(core)
    try:
        res = translator.translate(src)
    except Exception:
        res = core
    res = unprotect(res)
    # Common Argos cleanup and glossary consistency.
    fixes = {
        '중국트립박스': 'ChinaTripBox',
        '중국 여행': 'China 여행',
        '알리페이': 'Alipay',
        '위챗': 'WeChat',
        '위챗 페이': 'WeChat Pay',
        '구글 플레이': 'Google Play',
        '앱 스토어': 'App Store',
        '디디': 'DiDi',
        '바이두': 'Baidu',
        '메이투안': 'Meituan',
        '구글': 'Google',
        'VPN': 'VPN',
    }
    for a,b in fixes.items():
        res = res.replace(a,b)
    # Revert if translation somehow dropped all Hangul and changed little.
    if not hangul.search(res) and latin.search(core):
        res = core
    cache[core] = res
    return lead + res + trail

string_pat = re.compile(r"(?P<q>['\"])(?P<body>(?:\\.|(?!\1).)*?)(?P=q)", re.S)

def translate_strings(seg):
    def repl(m):
        q = m.group('q')
        body = m.group('body')
        if '\\n' in body or len(body) > 5000:
            return m.group(0)
        new = translate_text(body)
        # Escape only the matching quote for code strings.
        if new != body:
            new = new.replace('\\', '\\\\') if False else new
            new = new.replace(q, '\\' + q)
        return q + new + q
    return string_pat.sub(repl, seg)

# Visible text between tags. Preserve multiline indentation, skip template expressions.
text_node_pat = re.compile(r'>([^<>{}]+)<', re.S)
def translate_text_nodes(seg):
    def repl(m):
        body = m.group(1)
        if not latin.search(body):
            return m.group(0)
        # Translate each non-empty line or paragraph-like chunk.
        parts = re.split(r'(\s*\n\s*)', body)
        out = []
        for p in parts:
            if '\n' in p or not p.strip():
                out.append(p)
            else:
                out.append(translate_text(p))
        return '>' + ''.join(out) + '<'
    return text_node_pat.sub(repl, seg)

attr_pat = re.compile(r'\b(aria-label|alt|title|placeholder)=(?P<q>[\"\'])(?P<body>.*?)(?P=q)', re.S)
def translate_attrs(seg):
    def repl(m):
        return f"{m.group(1)}={m.group('q')}{translate_text(m.group('body'))}{m.group('q')}"
    return attr_pat.sub(repl, seg)

def process_body(body):
    # Keep script blocks structurally intact, but translate natural-language JS strings inside them.
    parts = re.split(r'(<script[^>]*>.*?</script>)', body, flags=re.S|re.I)
    out = []
    for part in parts:
        if part.lower().startswith('<script'):
            out.append(translate_strings(part))
        else:
            part = translate_attrs(part)
            part = translate_text_nodes(part)
            # Some component props are quoted visible copy.
            part = re.sub(r'\b(title|description|buttonText|coverAlt)=(?P<q>[\"\'])(?P<body>.*?)(?P=q)',
                          lambda m: f"{m.group(1)}={m.group('q')}{translate_text(m.group('body'))}{m.group('q')}", part, flags=re.S)
            out.append(part)
    return ''.join(out)

for rel in FILES:
    path = ROOT / rel
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if text.startswith('---'):
        m = re.match(r'---\r?\n(.*?)\r?\n---\r?\n(.*)', text, re.S)
        if m:
            fm = translate_strings(m.group(1))
            body = process_body(m.group(2))
            new = '---\n' + fm + '\n---\n\n' + body
        else:
            new = process_body(text)
    else:
        new = process_body(text)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(new)
print(f'updated {len(FILES)} files; translated {len(cache)} unique strings')
