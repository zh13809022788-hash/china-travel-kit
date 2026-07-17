import re
import time
from pathlib import Path

import translators as ts


ROOT = Path(r"D:\独立站\china-travel-kit")

BRANDS = [
    "Google Play",
    "App Store",
    "WeChat Pay",
    "WeChat",
    "Alipay",
    "DiDi",
    "Google",
    "Baidu",
    "Meituan",
    "ChinaTripBox",
    "China",
]

TEXT_KEYS = {
    "title",
    "description",
    "label",
    "question",
    "answer",
    "coverAlt",
    "alt",
    "placeholder",
    "summary",
    "text",
    "heading",
    "cta",
    "note",
    "warning",
    "buttonText",
    "category",
    "desc",
}

ATTRS = {"alt", "aria-label", "placeholder", "title"}

cache = {}


def protect(text):
    out = text
    placeholders = {}
    for i, brand in enumerate(BRANDS):
        token = f"__BRAND_{i}__"
        out = out.replace(brand, token)
        placeholders[token] = brand
    return out, placeholders


def unprotect(text, placeholders):
    out = text
    for token, brand in placeholders.items():
        out = out.replace(token, brand).replace(token.lower(), brand)
    return out


def should_translate(value):
    stripped = value.strip()
    if not re.search(r"[A-Za-z]", stripped):
        return False
    if stripped.startswith(("/", "./", "../", "#", "http", "mailto:", "tel:", "{")):
        return False
    if re.fullmatch(r"[A-Za-z0-9_./:-]+", stripped):
        return False
    return True


def translate_text(text):
    if not should_translate(text):
        return text
    leading = re.match(r"^\s*", text).group(0)
    trailing = re.search(r"\s*$", text).group(0)
    core = text.strip()
    if core in cache:
        return leading + cache[core] + trailing
    protected, placeholders = protect(core)
    translated = protected
    for attempt in range(4):
        try:
            translated = ts.translate_text(
                protected,
                translator="bing",
                from_language="en",
                to_language="ko",
                if_use_cn_host=True,
            )
            break
        except Exception:
            if attempt < 3:
                time.sleep(1.5 * (attempt + 1))
    translated = unprotect(translated, placeholders)
    cache[core] = translated
    return leading + translated + trailing


def translate_js_like_strings(text):
    key_re = "|".join(re.escape(k) for k in sorted(TEXT_KEYS, key=len, reverse=True))
    pattern = re.compile(
        rf"(?P<prefix>\b(?:{key_re})\b\s*[:=]\s*)(?P<quote>['\"])(?P<value>(?:\\.|(?! (?P=quote)).)*?)(?P=quote)",
        re.S | re.X,
    )

    def repl(match):
        value = match.group("value")
        if should_translate(value):
            value = translate_text(value)
        return f"{match.group('prefix')}{match.group('quote')}{value}{match.group('quote')}"

    return pattern.sub(repl, text)


def translate_tag_attrs(tag):
    for attr in ATTRS:
        pattern = re.compile(rf"(\b{re.escape(attr)}=)(['\"])(.*?)(\2)", re.S)

        def repl(match):
            value = match.group(3)
            if should_translate(value):
                value = translate_text(value)
            return f"{match.group(1)}{match.group(2)}{value}{match.group(4)}"

        tag = pattern.sub(repl, tag)
    return tag


def translate_html(html):
    chunks = re.split(r"(<script\b.*?</script>|<style\b.*?</style>)", html, flags=re.S | re.I)
    for i, chunk in enumerate(chunks):
        if re.match(r"<(?:script|style)\b", chunk, flags=re.I):
            continue
        parts = re.split(r"(<[^>]+>|\{[^{}]*\})", chunk)
        for j, part in enumerate(parts):
            if not part:
                continue
            if part.startswith("<"):
                parts[j] = translate_tag_attrs(part)
            elif part.startswith("{"):
                continue
            else:
                parts[j] = translate_text(part)
        chunks[i] = "".join(parts)
    return "".join(chunks)


def add_ko_links(text):
    def repl(match):
        prefix, quote, href = match.groups()
        if href == "/":
            href = "/ko/"
        elif href.startswith("/") and not href.startswith(("/ko/", "/api/", "/assets/", "//")):
            href = "/ko" + href
        return f"{prefix}{quote}{href}{quote}"

    text = re.sub(r"(\bhref=)(['\"])(/[^'\"]*)\2", repl, text)
    text = re.sub(r"(\bguide:\s*)(['\"])(/[^'\"]*)\2", repl, text)
    return text


def adjust_imports(text):
    def repl(match):
        quote, path = match.groups()
        return f"from {quote}../{path}{quote}"

    return re.sub(r"from\s+(['\"])(\.\./[^'\"]+)\1", repl, text)


def add_locale_props(text):
    text = re.sub(r"<(BaseLayout|GuideLayout)(?![^>]*\slocale=)", r'<\1 locale="ko"', text)
    text = re.sub(r"<Header(?![^>]*\slocale=)", r'<Header locale="ko"', text)
    text = re.sub(r"<Footer(?![^>]*\slocale=)", r'<Footer locale="ko"', text)
    return text


def source_for(target):
    rel = target.relative_to(ROOT / "src" / "pages" / "ko")
    return ROOT / "src" / "pages" / rel


def translate_file(target):
    source = source_for(target)
    if not source.exists():
        return False
    raw = source.read_text(encoding="utf-8-sig")
    if raw.startswith("---"):
        end = raw.find("---", 3)
        frontmatter = raw[: end + 3]
        html = raw[end + 3 :]
    else:
        frontmatter = ""
        html = raw
    out = adjust_imports(translate_js_like_strings(frontmatter)) + translate_js_like_strings(translate_html(html))
    out = add_locale_props(add_ko_links(out))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8", newline="")
    return True


def main():
    targets = sorted((ROOT / "src" / "pages" / "ko").rglob("*.astro"))
    for target in targets:
        if translate_file(target):
            print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
