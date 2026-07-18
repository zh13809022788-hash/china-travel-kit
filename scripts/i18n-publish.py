#!/usr/bin/env python3
"""
i18n Publish — One English article → 7 native-quality translations.

Usage:
  python3 scripts/i18n-publish.py posts/my-new-guide.astro

Steps:
  1. Read the English .astro file from src/pages/
  2. Copy to 7 locale directories (zh-TW, ja, ko, ru, fr, de, es)
  3. Run Codex CLI for native-language rewrite per locale
  4. Validate output (strip code blocks, check quality)
  5. Push all 7 files to GitHub
  6. Print summary
"""

import sys, os, re, json, base64, urllib.request, urllib.error, urllib.parse, subprocess, time
from pathlib import Path

# ─── Config ────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
FIXES_DIR = BASE / 'i18n_publish_tmp'
KEY_FILE = BASE / '.codex_key'
CODX_LOG = BASE / 'i18n_publish_log.txt'
# Read GitHub PAT from .codex_key (shared secret file) or env var
_GITHUB_PAT = os.environ.get('GH_PAT') or (BASE / '.codex_key').read_text().strip()
PAT = _GITHUB_PAT
REPO = 'zh13809022788-hash/china-travel-kit'
GITHUB_HEADERS = {'Authorization': f'token {PAT}', 'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}

LOCALES = ['zh-TW', 'ja', 'ko', 'ru', 'fr', 'de', 'es']
LOCALE_PREFIX = {'zh-TW': 'zh-tw', 'ja': 'ja', 'ko': 'ko', 'ru': 'ru', 'fr': 'fr', 'de': 'de', 'es': 'es'}

# Codex prompts per locale
CODEX_PROMPTS = {
    'zh-TW': 'You are a native Traditional Chinese writer from Taiwan. Rewrite (not translate) ALL English text in this file to natural Taiwanese Traditional Chinese (繁體中文). PRESERVE all JS/Python code, imports, HTML tags, CSS classes, URLs, JSON-LD, brand names, and technical terms. REWRITE: title, description, visible HTML text, data field values, alt text, button text, Tip sections, FAQ entries, table content. Output the COMPLETE file with no markdown formatting.',
    'ja': 'You are a native Japanese content writer. Rewrite (not translate) ALL English text in this file to natural Japanese (丁寧語/ですます調). PRESERVE all JS/Python code, imports, HTML tags, CSS classes, URLs, JSON-LD, brand names. REWRITE: title, description, visible HTML text, data fields, alt text, button text, Tip sections, FAQ entries, table content. Output the COMPLETE file.',
    'ko': 'You are a native Korean content writer. Rewrite (not translate) ALL English text in this file to natural Korean (존댓말/해요체). PRESERVE all JS/Python code, imports, HTML tags, CSS classes, URLs, JSON-LD, brand names. REWRITE: title, description, visible HTML text, data fields, alt text, button text, Tip sections, FAQ entries, table content. Output the COMPLETE file.',
    'ru': 'You are a native Russian content writer. Rewrite (not translate) ALL English text in this file to natural Russian (use polite you-form). PRESERVE all JS/Python code, imports, HTML tags, CSS classes, URLs, JSON-LD, brand names. REWRITE: title, description, visible HTML text, data fields, alt text, button text, Tip sections, FAQ entries, table content. Output the COMPLETE file.',
    'fr': 'You are a native French content writer. Rewrite (not translate) ALL English text in this file to natural French (utilisez le vouvoiement). PRESERVE all JS/Python code, imports, HTML tags, CSS classes, URLs, JSON-LD, brand names. REWRITE: title, description, visible HTML text, data fields, alt text, button text, Tip sections, FAQ entries, table content. Output the COMPLETE file.',
    'de': 'You are a native German content writer. Rewrite (not translate) ALL English text in this file to natural German (Sie-Form). PRESERVE all JS/Python code, imports, HTML tags, CSS classes, URLs, JSON-LD, brand names. REWRITE: title, description, visible HTML text, data fields, alt text, button text, Tip sections, FAQ entries, table content. Output the COMPLETE file.',
    'es': 'You are a native Spanish content writer. Rewrite (not translate) ALL English text in this file to natural Spanish (use usted form). PRESERVE all JS/Python code, imports, HTML tags, CSS classes, URLs, JSON-LD, brand names. REWRITE: title, description, visible HTML text, data fields, alt text, button text, Tip sections, FAQ entries, table content. Output the COMPLETE file.',
}

# Language validation patterns
LANG_PATTERNS = {
    'zh-TW': re.compile(r'[\u4e00-\u9fff]'),
    'ja': re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]'),
    'ko': re.compile(r'[\uac00-\ud7af]'),
    'ru': re.compile(r'[\u0400-\u04ff]'),
    'fr': re.compile(r'[àâäéèêëïîôöùûüçœ]', re.I),
    'de': re.compile(r'[äöüß]', re.I),
    'es': re.compile(r'[áéíóúñü¿¡]', re.I),
}

ENGLISH_WORDS = re.compile(r'\b(the|and|for|with|from|this|that|your|our|their|Check|Guide|Start|Need|Best|Setup|Tips?|before|after|Read|Learn|More|About|App Store|Google Play|Download|Open|Web Version|View|Edit|Delete|Save|Cancel|Submit|Search|Filter|Sort)\b', re.I)


def log(msg):
    print(msg)
    with open(str(CODX_LOG), 'a', encoding='utf-8') as f:
        f.write(msg + '\n')


def fetch_english_file(rel_path):
    """Fetch English file from GitHub."""
    url = f'https://api.github.com/repos/{REPO}/contents/src/pages/{rel_path}?ref=main'
    req = urllib.request.Request(url, headers=GITHUB_HEADERS)
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read())
    content = base64.b64decode(data['content']).decode('utf-8')
    return content, data['sha']


def locale_github_path(locale, rel_path):
    """Convert English rel_path like 'posts/my-guide.astro' to locale path."""
    prefix = LOCALE_PREFIX[locale]
    return f'src/pages/{prefix}/{rel_path}'


def fetch_current_sha(github_path):
    """Fetch current SHA of a file on GitHub (None if not exists)."""
    url = f'https://api.github.com/repos/{REPO}/contents/{urllib.parse.quote(github_path, safe="/")}?ref=main'
    req = urllib.request.Request(url, headers=GITHUB_HEADERS)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read()).get('sha')
    except:
        return None


def push_file(github_path, content, message):
    """Push a single file to GitHub via API. Creates file if new."""
    sha = fetch_current_sha(github_path)
    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    payload = {'message': message, 'content': encoded, 'branch': 'main'}
    if sha:
        payload['sha'] = sha
    
    url = f'https://api.github.com/repos/{REPO}/contents/{urllib.parse.quote(github_path, safe="/")}'
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='PUT', headers=GITHUB_HEADERS)
    
    for attempt in range(3):
        try:
            resp = urllib.request.urlopen(req, timeout=60)
            r = json.loads(resp.read())
            return r.get('commit', {}).get('sha', '')[:8]
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')[:200]
            if e.code == 409:
                sha = fetch_current_sha(github_path)
                payload['sha'] = sha
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(url, data=data, method='PUT', headers=GITHUB_HEADERS)
                continue
            raise
    return None


def strip_code_block(content):
    """Remove ```astro code block markers if present."""
    content = re.sub(r'^\s*```(astro)?\s*\n?', '', content)
    content = re.sub(r'\n?\s*```\s*$', '', content)
    return content


def validate_content(locale, content):
    """Validate that content has target language and minimal English."""
    pattern = LANG_PATTERNS.get(locale)
    if pattern:
        native_chars = len(pattern.findall(content))
        if native_chars < 20:
            return False, f'Too few native chars ({native_chars})'
    
    visible = ' '.join(re.findall(r'>([^<]+)<', content))
    eng_count = len(ENGLISH_WORDS.findall(visible))
    if eng_count >= 10:
        return False, f'{eng_count} English words in visible text'
    
    return True, 'OK'


def run_codex(locale, content):
    """Run Codex CLI to rewrite content for a locale."""
    prompt = CODEX_PROMPTS[locale]
    api_key = KEY_FILE.read_text().strip()
    
    env = os.environ.copy()
    env['CODEX_API_KEY'] = api_key
    
    result = subprocess.run(
        ['codex', 'exec', '--dangerously-bypass-approvals-and-sandbox', '--skip-git-repo-check', prompt],
        input=content, capture_output=True, text=True, timeout=180,
        cwd=str(BASE), env=env
    )
    
    output = result.stdout.strip()
    
    # Extract from code block if present
    lines = output.split('\n')
    in_block = False
    block_lines = []
    for line in lines:
        if line.strip().startswith('```'):
            in_block = not in_block
            continue
        if in_block:
            block_lines.append(line)
    
    if block_lines:
        output = '\n'.join(block_lines)
    
    return strip_code_block(output)


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/i18n-publish.py posts/my-article.astro')
        sys.exit(1)
    
    rel_path = sys.argv[1].lstrip('/')
    if not rel_path.startswith('posts/') and '/' not in rel_path:
        # Assume it's a post
        rel_path = f'posts/{rel_path}'
    if not rel_path.endswith('.astro'):
        rel_path += '.astro'
    
    FIXES_DIR.mkdir(exist_ok=True)
    CODX_LOG.unlink(missing_ok=True)
    
    log(f'🚀 i18n Publishing: {rel_path}')
    log(f'   Target: 7 locales ({", ".join(LOCALES)})\n')
    
    # Step 1: Fetch English source
    log('📥 Step 1: Fetching English source...')
    try:
        eng_content, eng_sha = fetch_english_file(rel_path)
        log(f'   ✅ src/pages/{rel_path} ({len(eng_content)} bytes, sha: {eng_sha[:12]})\n')
    except Exception as e:
        log(f'   ❌ Failed: {e}')
        sys.exit(1)
    
    # Step 2-4: For each locale, copy, Codex, validate
    results = {}
    for locale in LOCALES:
        log(f'🌐 Step 2-4: Processing {locale}...')
        
        try:
            # Run Codex
            rewritten = run_codex(locale, eng_content)
            
            # Validate
            valid, msg = validate_content(locale, rewritten)
            if not valid:
                log(f'   ⚠️  Quality check: {msg}')
            
            # Push to GitHub
            gpath = locale_github_path(locale, rel_path)
            commit = push_file(gpath, rewritten, f'i18n: {locale} native rewrite - {rel_path}')
            
            if commit:
                results[locale] = (True, commit, len(rewritten))
                log(f'   ✅ {gpath} -> commit {commit} ({len(rewritten)}b)')
            else:
                results[locale] = (False, 'push failed', 0)
                log(f'   ❌ Push failed')
        except Exception as e:
            results[locale] = (False, str(e), 0)
            log(f'   ❌ Error: {str(e)[:100]}')
        
        time.sleep(2)  # Rate limit friendly
    
    # Step 5: Summary
    log('\n' + '=' * 50)
    log('📊 SUMMARY')
    log('=' * 50)
    
    success = sum(1 for v in results.values() if v[0])
    for locale, (ok, msg, size) in results.items():
        status = '✅' if ok else '❌'
        log(f'  {status} {locale}: {msg} ({size}b)' if ok else f'  {status} {locale}: {msg}')
    
    log(f'\n   {success}/{len(LOCALES)} locales published successfully')
    log(f'   Source: src/pages/{rel_path}')


if __name__ == '__main__':
    main()
