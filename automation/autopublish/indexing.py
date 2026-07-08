"""收录推送: 百度普通收录 (+ 可选 IndexNow/Bing)。失败自动重试 1 次。

百度普通收录 API: POST 纯文本, 每行一个 URL, Content-Type: text/plain。
    成功返回 JSON 含 success / remain 字段。
IndexNow: POST JSON {host, key, urlList}, 面向 Bing 及支持 IndexNow 的引擎。

注意: Google 无通用 URL 提交 API —— Google 侧依赖构建时自动重建的 sitemap
       (@astrojs/sitemap) + Search Console。见 README。
"""
from __future__ import annotations

from dataclasses import dataclass, field

import requests

from .config import Config


@dataclass
class PushResult:
    engine: str
    ok: bool
    detail: str = ""
    submitted: int = 0


def _post_with_retry(retry_once: bool, fn) -> tuple[bool, str]:
    """执行一次推送; 失败则(可选)重试 1 次。fn 返回 (ok, detail)。"""
    ok, detail = fn()
    if ok or not retry_once:
        return ok, detail
    print(f"  [indexing] first attempt failed ({detail}); retrying once...")
    return fn()


def push_baidu(cfg: Config, urls: list[str]) -> PushResult:
    if not urls:
        return PushResult("baidu", True, "no urls", 0)
    endpoint = cfg.baidu_endpoint.format(site=cfg.domain, token=cfg.secrets.baidu_token)
    payload = "\n".join(urls).encode("utf-8")

    def attempt() -> tuple[bool, str]:
        try:
            r = requests.post(
                endpoint,
                data=payload,
                headers={"Content-Type": "text/plain"},
                timeout=20,
            )
        except requests.RequestException as e:
            return False, f"network error: {e}"
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}: {r.text[:300]}"
        try:
            body = r.json()
        except ValueError:
            return False, f"non-JSON response: {r.text[:300]}"
        if "error" in body:
            return False, f"baidu error {body.get('error')}: {body.get('message')}"
        return True, f"success={body.get('success')} remain={body.get('remain')}"

    ok, detail = _post_with_retry(cfg.retry_once, attempt)
    return PushResult("baidu", ok, detail, submitted=len(urls) if ok else 0)


def push_indexnow(cfg: Config, urls: list[str]) -> PushResult:
    if not urls:
        return PushResult("indexnow", True, "no urls", 0)
    body = {
        "host": cfg.domain,
        "key": cfg.secrets.indexnow_key,
        "urlList": urls,
    }

    def attempt() -> tuple[bool, str]:
        try:
            r = requests.post(cfg.indexnow_endpoint, json=body, timeout=20)
        except requests.RequestException as e:
            return False, f"network error: {e}"
        # IndexNow: 200/202 视为成功
        if r.status_code in (200, 202):
            return True, f"HTTP {r.status_code}"
        return False, f"HTTP {r.status_code}: {r.text[:300]}"

    ok, detail = _post_with_retry(cfg.retry_once, attempt)
    return PushResult("indexnow", ok, detail, submitted=len(urls) if ok else 0)


def push_all(cfg: Config, urls: list[str]) -> list[PushResult]:
    results: list[PushResult] = []
    if cfg.baidu_enabled:
        results.append(push_baidu(cfg, urls))
    if cfg.indexnow_enabled:
        results.append(push_indexnow(cfg, urls))
    for res in results:
        status = "OK" if res.ok else "FAIL"
        print(f"  [indexing] {res.engine}: {status} — {res.detail}")
    return results
