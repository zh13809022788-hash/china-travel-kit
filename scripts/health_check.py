"""
Chinatripbox 全站健康巡检脚本
每日定时运行：
1. 全站链接扫描 → 发现 404
2. 自动生成缺失的 locale 页面
3. 记录日志

用法: python scripts/health_check.py
输出: .workbuddy/health-reports/YYYY-MM-DD.md
"""

import os, re, sys, json
from datetime import datetime

PROJECT_ROOT = r'D:\独立站\china-travel-kit'
DIST_DIR = os.path.join(PROJECT_ROOT, 'dist')
PAGES_DIR = os.path.join(PROJECT_ROOT, 'src', 'pages')
REPORT_DIR = os.path.join(PROJECT_ROOT, '.workbuddy', 'health-reports')

LOCALES = ['zh-tw', 'ja', 'ko', 'ru', 'fr', 'de', 'es']
LOCALE_MAP = {'zh-tw': 'zh-TW', 'ja': 'ja', 'ko': 'ko', 'ru': 'ru', 'fr': 'fr', 'de': 'de', 'es': 'es'}

os.makedirs(REPORT_DIR, exist_ok=True)


def scan_links():
    """Walk all index.html files, extract links, report 404s."""
    if not os.path.exists(DIST_DIR):
        return {"error": "dist not built yet", "total": 0, "missing": []}

    hub_files = []
    for root, dirs, files in os.walk(DIST_DIR):
        for f in files:
            if f == 'index.html':
                hub_files.append(os.path.join(root, f))

    all_links = set()
    for hf in hub_files:
        with open(hf, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        links = re.findall(r'href="(/[^"]+)"', content)
        for link in links:
            if (link.startswith('http') or link.startswith('#') or 
                link.startswith('/_astro') or link == '/' or
                link.startswith('/rss') or link.startswith('/favicon')):
                continue
            all_links.add(link)

    missing = []
    for link in sorted(all_links):
        path = link.rstrip('/')
        html_path = (path if path.endswith('.html') else path + '/index.html')
        dist_path = os.path.join(DIST_DIR, html_path.lstrip('/')).replace('/', os.sep)
        if not os.path.exists(dist_path):
            missing.append(link)

    return {"total": len(all_links), "total_pages": len(hub_files), "missing": missing}


def classify_links(missing):
    """Classify 404 links into fixable vs non-fixable."""
    fixable = []  # locale hub pages that can be auto-generated
    data_links = []  # /xx/data/... - dynamic content, skip
    query_links = []  # ?q=... query params page
    other = []  # rest

    for link in missing:
        if '/data/' in link:
            data_links.append(link)
        elif '?' in link:
            query_links.append(link)
        else:
            # Check if it's a missing locale hub page
            # Pattern: /xx/some-path/ where xx is a locale
            fixable.append(link)

    return fixable, data_links, query_links, other


def auto_fix(fixable_links):
    """Auto-generate missing locale hub pages."""
    fixed = []
    failed = []

    for link in fixable_links:
        # Parse the link: /fr/some/path/
        parts = link.strip('/').split('/')
        if len(parts) < 2:
            failed.append((link, "too short"))
            continue

        locale_dir = parts[0]
        if locale_dir not in LOCALES:
            failed.append((link, f"unknown locale: {locale_dir}"))
            continue

        # English source path: src/pages/rest
        rest = '/'.join(parts[1:])
        source_path = os.path.join(PAGES_DIR, rest)

        if source_path.endswith('/'):
            source_path = source_path[:-1]

        # Try with .astro, then /index.astro
        source_file = source_path + '.astro'
        source_index = os.path.join(source_path, 'index.astro')

        if os.path.exists(source_file):
            content = read_source(source_file)
            if content is None:
                failed.append((link, "read error"))
                continue
            # Generate locale copy at same depth
            target = os.path.join(PAGES_DIR, locale_dir, rest + '.astro')
            result = write_locale_copy(content, target, locale_dir)
            if result:
                fixed.append(link)
            else:
                failed.append((link, "write error"))

        elif os.path.exists(source_index):
            content = read_source(source_index)
            if content is None:
                failed.append((link, "read error"))
                continue
            # Generate locale copy: fr/rest/index.astro
            target_dir = os.path.join(PAGES_DIR, locale_dir, rest)
            target = os.path.join(target_dir, 'index.astro')
            result = write_locale_copy(content, target, locale_dir)
            if result:
                fixed.append(link)
            else:
                failed.append((link, "write error"))
        else:
            failed.append((link, "source not found"))

    return fixed, failed


def read_source(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None


def write_locale_copy(content, target_path, locale_dir):
    """Adjust imports and add locale props."""
    locale_code = LOCALE_MAP.get(locale_dir, locale_dir)

    # Count depth from pages dir
    rel = os.path.relpath(target_path, PAGES_DIR)
    depth = len(rel.split(os.sep))

    # Adjust imports based on depth
    # pages/X.astro -> depth=1, imports='../' -> need '../../'
    # pages/X/Y.astro -> depth=2, imports='../../' -> need '../../../'
    old_prefix = '../' * (depth - 1)
    new_prefix = '../' * depth

    content = content.replace(
        f"from '{old_prefix}layouts/", f"from '{new_prefix}layouts/"
    ).replace(
        f"from '{old_prefix}components/", f"from '{new_prefix}components/"
    ).replace(
        f"from '{old_prefix}config'", f"from '{new_prefix}config'"
    ).replace(
        f"from '{old_prefix}styles/", f"from '{new_prefix}styles/"
    ).replace(
        f"from '{old_prefix}data/", f"from '{new_prefix}data/"
    ).replace(
        f"from '{old_prefix}assets/", f"from '{new_prefix}assets/"
    )

    # Add locale to BaseLayout / GuideLayout
    def add_locale(match):
        full = match.group(0)
        if 'locale=' in full:
            return full
        if full.endswith('/>'):
            return full[:-2] + f' locale="{locale_code}"/>'
        return full[:-1] + f' locale="{locale_code}">'

    content = re.sub(r'<BaseLayout[^>]*>', add_locale, content)
    content = re.sub(r'<GuideLayout[^>]*>', add_locale, content)
    content = re.sub(r'<Header\s*/>', f'<Header locale="{locale_code}" />', content)

    try:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except:
        return False


def main():
    report_date = datetime.now().strftime('%Y-%m-%d')
    report_time = datetime.now().strftime('%H:%M')
    report = []
    report.append(f"# 站点头健康巡检报告 — {report_date} {report_time}")
    report.append("")

    # Phase 1: Scan
    report.append("## 1. 全站链接扫描")
    result = scan_links()
    if "error" in result:
        report.append(f"❌ {result['error']}")
    else:
        report.append(f"- 扫描页面数: {result['total_pages']}")
        report.append(f"- 总链接数: {result['total']}")
        report.append(f"- 404 数: {len(result['missing'])}")

        if result['missing']:
            fixable, data_links, query_links, other = classify_links(result['missing'])
            report.append(f"  - 可自动修复: {len(fixable)}")
            report.append(f"  - Data 动态页 (跳过): {len(data_links)}")
            report.append(f"  - 查询参数 (跳过): {len(query_links)}")
            report.append(f"  - 其他: {len(other)}")

    report.append("")

    # Phase 2: Auto-fix
    report.append("## 2. 自动修复")
    if "error" not in result and result['missing']:
        fixable, _, _, _ = classify_links(result['missing'])
        if fixable:
            fixed, failed = auto_fix(fixable)
            report.append(f"- 已修复: {len(fixed)}")
            for link in fixed[:10]:
                report.append(f"  ✅ {link}")
            if len(fixed) > 10:
                report.append(f"  ... 还有 {len(fixed)-10} 个")
            if failed:
                report.append(f"- 修复失败: {len(failed)}")
                for link, reason in failed[:5]:
                    report.append(f"  ❌ {link} — {reason}")
        else:
            report.append("- 无需要修复的链接 ✅")
    else:
        report.append("- 无需要修复的链接 ✅")

    report.append("")

    # Write report
    report_path = os.path.join(REPORT_DIR, f"{report_date}.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f"报告已生成: {report_path}")
    print(f"404 链接: {len(result.get('missing', []))}")
    print(f"已修复: {len(fixable) if 'error' not in result and 'fixable' in dir() else 0}")

    # Return result for automation
    return {
        "date": report_date,
        "total_pages": result.get("total_pages", 0),
        "total_links": result.get("total", 0),
        "missing_count": len(result.get("missing", [])),
        "auto_fixed": 0,
        "report_path": report_path
    }


if __name__ == '__main__':
    main()
