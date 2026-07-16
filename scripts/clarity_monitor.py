"""
Chinatripbox Clarity 行为数据分析
需要 Clarity API Token，从 clarity.microsoft.com 获取
设置: Settings → Data Export → Generate API Token

用法: python scripts/clarity_monitor.py --token YOUR_TOKEN --project YOUR_PROJECT_ID
"""

import os, sys, json, requests
from datetime import datetime, timezone

REPORT_DIR = r'D:\独立站\china-travel-kit\.workbuddy\health-reports'
os.makedirs(REPORT_DIR, exist_ok=True)

CLARITY_API = "https://www.clarity.ms/export-data/api/v1/project-live-insights"


def fetch_clarity(token, project_id, days=1):
    """Fetch Clarity data for the last N days."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
        "projectId": project_id,
        "numOfDays": min(days, 3),  # API max 3 days
        "dimension1": "URL"  # Break down by page URL
    }
    try:
        resp = requests.get(CLARITY_API, headers=headers, params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": f"API error: {resp.status_code}", "detail": resp.text}
    except Exception as e:
        return {"error": str(e)}


def analyze_data(data):
    """Analyze Clarity data for red flags."""
    issues = []
    flags = {"dead_clicks": 0, "rage_clicks": 0, "quickbacks": 0, "bad_pages": []}

    if "error" in data:
        return {"error": data["error"]}

    if not data or not isinstance(data, list):
        return {"error": "empty response"}

    for entry in data:
        url = entry.get("URL", "unknown")
        dead = int(entry.get("DeadClickCount", 0))
        rage = int(entry.get("RageClickCount", 0))
        quickback = int(entry.get("QuickbackClick", 0))
        sessions = int(entry.get("totalSessionCount", 0))
        scroll = float(entry.get("ScrollDepth", 0))

        flags["dead_clicks"] += dead
        flags["rage_clicks"] += rage
        flags["quickbacks"] += quickback

        # Per-page issues
        page_issues = []
        if dead > 5:
            page_issues.append(f"死点击 {dead}")
        if rage > 3:
            page_issues.append(f"愤怒点击 {rage}")
        if quickback > 2:
            page_issues.append(f"快速后退 {quickback}")
        if sessions > 5 and scroll < 30:
            page_issues.append(f"滚动深度仅 {scroll}%")

        if page_issues:
            flags["bad_pages"].append({
                "url": url,
                "sessions": sessions,
                "issues": page_issues,
                "dead": dead,
                "rage": rage,
                "quickback": quickback,
                "scroll": scroll
            })

    return flags


def generate_report(clarity_result):
    """Generate a report from Clarity data."""
    report = []
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    report.append(f"## 2. Clarity 行为数据分析 ({today})")
    report.append("")

    if "error" in clarity_result:
        report.append(f"❌ Clarity API 错误: {clarity_result['error']}")
        report.append("")
        report.append("需要你提供 Clarity API Token：")
        report.append("1. 打开 https://clarity.microsoft.com/")
        report.append("2. 进入 chinatripbox 项目 → Settings → Data Export")
        report.append("3. 点 Generate API Token，复制")
        report.append("4. 告诉我 Token，我就能开始自动监控")
        return "\n".join(report)

    total_dead = clarity_result.get("dead_clicks", 0)
    total_rage = clarity_result.get("rage_clicks", 0)
    total_quickback = clarity_result.get("quickbacks", 0)
    bad_pages = clarity_result.get("bad_pages", [])

    report.append(f"- 死点击总数: {total_dead}")
    report.append(f"- 愤怒点击总数: {total_rage}")
    report.append(f"- 快速后退总数: {total_quickback}")
    report.append(f"- 有问题页面: {len(bad_pages)}")
    report.append("")

    if total_dead > 20:
        report.append("⚠️ 死点击超过 20 次，需要排查链接问题")
    if total_rage > 10:
        report.append("⚠️ 愤怒点击超过 10 次，可能页面交互有问题")
    if total_quickback > 5:
        report.append("⚠️ 快速后退超过 5 次，首屏内容可能不达标")

    if bad_pages:
        report.append("### 问题页面详情")
        for page in bad_pages[:10]:
            report.append(f"- {page['url']}")
            for issue in page['issues']:
                report.append(f"  - ❌ {issue}")
            report.append(f"  会话数: {page['sessions']}")

    return "\n".join(report)


def main():
    token = None
    project_id = None

    # Read from args or env
    for i, arg in enumerate(sys.argv):
        if arg == '--token' and i + 1 < len(sys.argv):
            token = sys.argv[i + 1]
        elif arg == '--project' and i + 1 < len(sys.argv):
            project_id = sys.argv[i + 1]

    if not token:
        token = os.environ.get('CLARITY_API_TOKEN')
    if not project_id:
        project_id = os.environ.get('CLARITY_PROJECT_ID')

    if not token or not project_id:
        result = {"error": "no API credentials"}
    else:
        data = fetch_clarity(token, project_id)
        result = analyze_data(data)

    report_md = generate_report(result)
    print(report_md)

    # Append to today's health report
    today = datetime.now().strftime('%Y-%m-%d')
    report_path = os.path.join(REPORT_DIR, f"{today}.md")
    if os.path.exists(report_path):
        with open(report_path, 'a', encoding='utf-8') as f:
            f.write("\n" + report_md)

    return result


if __name__ == '__main__':
    main()
