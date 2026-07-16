"""
Chinatripbox 一键健康巡检主控
同时运行：全站爬虫 + Clarity 分析（如果有 Token）

用法: python scripts/run_health_check.py
      python scripts/run_health_check.py --clarity-token YOUR_TOKEN --clarity-project YOUR_PROJECT_ID
"""

import os, sys, subprocess, json
from datetime import datetime

SCRIPT_DIR = r'D:\独立站\china-travel-kit\scripts'
PROJECT_DIR = r'D:\独立站\china-travel-kit'
REPORT_DIR = os.path.join(PROJECT_DIR, '.workbuddy', 'health-reports')
os.makedirs(REPORT_DIR, exist_ok=True)


def run_python(script_name):
    """Run a Python script and return its stdout + stderr."""
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, script_name)],
            capture_output=True, text=True, timeout=300,
            cwd=PROJECT_DIR
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1
    except Exception as e:
        return "", str(e), -1


def main():
    today = datetime.now().strftime('%Y-%m-%d')
    report = []
    report.append(f"# ⚡ Chinatripbox 健康巡检 — {today}")
    report.append("")

    # Phase 1: Crawler scan
    print("▶ 全站爬虫扫描...")
    stdout, stderr, code = run_python('health_check.py')
    if code == 0:
        report.append("## 1. 全站链接扫描 ✅")
        report.append(stdout.strip())
    else:
        report.append("## 1. 全站链接扫描 ❌")
        report.append(f"错误: {stderr[:200]}")
    report.append("")

    # Phase 2: Clarity (if token available)
    clarity_token = os.environ.get('CLARITY_API_TOKEN')
    clarity_project = os.environ.get('CLARITY_PROJECT_ID')

    # Also check CLI args
    for i, arg in enumerate(sys.argv):
        if arg == '--clarity-token' and i + 1 < len(sys.argv):
            clarity_token = sys.argv[i + 1]
        elif arg == '--clarity-project' and i + 1 < len(sys.argv):
            clarity_project = sys.argv[i + 1]

    if clarity_token and clarity_project:
        print("▶ Clarity 数据分析...")
        cmd = f'{sys.executable} scripts/clarity_monitor.py --token {clarity_token} --project {clarity_project}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              timeout=60, cwd=PROJECT_DIR)
        if result.returncode == 0:
            report.append(result.stdout)
        else:
            report.append(f"## 2. Clarity 分析 ❌")
            report.append(f"错误: {result.stderr[:200]}")
    else:
        report.append("## 2. Clarity 行为数据")
        report.append("⚠️ 未设置 Clarity API Token，跳过行为分析")
        report.append("")
        report.append("如需启用 Clarity 监控，请提供 Token：")
        report.append("1. 打开 https://clarity.microsoft.com/")
        report.append("2. 进入 chinatripbox 项目 → Settings → Data Export")
        report.append("3. 点 Generate API Token，复制")
        report.append("4. 告诉我 Token 和 Project ID")
        report.append("")

    report.append("---")
    report.append(f"_报告自动生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")

    # Write report
    report_path = os.path.join(REPORT_DIR, f"{today}_full.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f"\n✅ 完整报告: {report_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
