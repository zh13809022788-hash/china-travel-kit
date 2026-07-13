"""一次性取图工具：按 image-map.json 的关键词，从 Unsplash 官方 API 搜索并下载
高相关度图片到 src/assets/images/，同时按 Unsplash 许可记录作者署名并触发下载追踪。

这是独立工具，不属于每日自动发布流水线。

用法:
    export UNSPLASH_ACCESS_KEY=你的key      # Windows: setx 或 $env:
    python automation/fetch_images.py                 # 取所有缺失的图
    python automation/fetch_images.py --force         # 重新下载(覆盖已存在)
    python automation/fetch_images.py --only city-shanghai cover-visa

合规(Unsplash API 许可强制):
  - 每张图记录 photographer + Unsplash 链接(带 utm), 供页面署名。
  - 下载时触发 download_location 端点(Unsplash 要求的下载事件)。
  - 图片本地化存储, 不热链 CDN。

免费 Demo 版限速约 50 次/小时, 本表仅 ~10 张, 远低于限额。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import requests

AUTOMATION_DIR = Path(__file__).resolve().parent
REPO_ROOT = AUTOMATION_DIR.parent
MAP_PATH = AUTOMATION_DIR / "image-map.json"
API_BASE = "https://api.unsplash.com"
UTM = "?utm_source=chinatripbox&utm_medium=referral"


def _key() -> str:
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        print("缺少环境变量 UNSPLASH_ACCESS_KEY —— 去 https://unsplash.com/developers 免费申请",
              file=sys.stderr)
        sys.exit(2)
    return key


def _headers(key: str) -> dict:
    # Unsplash 推荐用 Client-ID 授权头
    return {"Authorization": f"Client-ID {key}", "Accept-Version": "v1"}


def search_one(key: str, query: str, orientation: str) -> dict | None:
    """搜索并返回相关度最高的一张图的元数据(含下载与署名信息)。"""
    params = {"query": query, "orientation": orientation, "per_page": 1, "content_filter": "high"}
    r = requests.get(f"{API_BASE}/search/photos?{urlencode(params)}", headers=_headers(key), timeout=20)
    if r.status_code != 200:
        print(f"  搜索失败 HTTP {r.status_code}: {r.text[:200]}")
        return None
    results = r.json().get("results", [])
    if not results:
        print(f"  无结果: {query!r}")
        return None
    return results[0]


def trigger_download(key: str, photo: dict) -> None:
    """触发 Unsplash 要求的下载事件(许可合规)。"""
    loc = photo.get("links", {}).get("download_location")
    if not loc:
        return
    try:
        requests.get(loc, headers=_headers(key), timeout=15)
    except requests.RequestException:
        pass  # 追踪失败不阻断下载


def download_raw(photo: dict, dest: Path) -> bool:
    """下载图片本体到 dest。用 regular 尺寸(~1080px 宽, 适合头图)。"""
    url = photo.get("urls", {}).get("regular") or photo.get("urls", {}).get("full")
    if not url:
        return False
    for attempt in (1, 2):  # 失败重试一次
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200 and r.content:
                dest.write_bytes(r.content)
                return True
            print(f"  下载 HTTP {r.status_code} (尝试 {attempt})")
        except requests.RequestException as e:
            print(f"  下载异常 (尝试 {attempt}): {e}")
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="从 Unsplash 取封面图")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的图")
    parser.add_argument("--only", nargs="*", default=None, help="只取指定 name")
    args = parser.parse_args(argv)

    key = _key()
    spec = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    out_dir = (REPO_ROOT / spec.get("output_dir", "src/assets/images")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    credits_path = out_dir / "credits.json"
    credits = {}
    if credits_path.exists():
        try:
            credits = json.loads(credits_path.read_text(encoding="utf-8"))
        except ValueError:
            credits = {}

    items = spec["images"]
    if args.only:
        items = [i for i in items if i["name"] in set(args.only)]

    ok, skipped, failed = 0, 0, 0
    for item in items:
        name = item["name"]
        dest = out_dir / f"{name}.jpg"
        if dest.exists() and not args.force:
            print(f"[skip] {name} 已存在")
            skipped += 1
            continue

        print(f"[fetch] {name}  <-  {item['query']!r}")
        photo = search_one(key, item["query"], item.get("orientation", "landscape"))
        if not photo:
            failed += 1
            continue

        trigger_download(key, photo)
        if not download_raw(photo, dest):
            failed += 1
            continue

        user = photo.get("user", {})
        credits[name] = {
            "photographer": user.get("name", ""),
            "photographer_url": (user.get("links", {}).get("html", "") + UTM),
            "unsplash_url": (photo.get("links", {}).get("html", "") + UTM),
            "query": item["query"],
            "description": photo.get("description") or photo.get("alt_description") or "",
            "width": photo.get("width"),
            "height": photo.get("height"),
        }
        print(f"    ✓ by {credits[name]['photographer']}  ({credits[name]['description'][:60]})")
        ok += 1
        time.sleep(1)  # 温柔限速

    credits_path.write_text(json.dumps(credits, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n完成: 下载 {ok}, 跳过 {skipped}, 失败 {failed}。署名写入 {credits_path.name}")
    print("下一步: npm run build 验证; 抽查 credits.json 的 query/description 是否贴题。")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
