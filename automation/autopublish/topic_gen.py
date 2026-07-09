"""大模型自主生成选题。

当队列可用选题不足时, 调 Claude 基于站点五大分类(payment/esim/transport/
essentials/food)自动构思一批新选题(关键词 + 分类 + 差异化角度), 去重后入队。

去重两层:
  1. 与现有队列全部关键词(含已用)对比;
  2. 与已发文章标题/主题对比(通过传入的 avoid 列表)。
最终由 TopicQueue.append 再做一次关键词去重, 双保险。
"""
from __future__ import annotations

import json
import re
from typing import Any

from .config import Config
from .generator import _extract_json  # 复用稳健 JSON 抽取


def _build_prompt(cfg: Config, n: int, avoid: list[str]) -> str:
    cats = ", ".join(cfg.allowed_categories)
    avoid_block = ""
    if avoid:
        # 只带最近若干条, 控制 prompt 体积
        sample = avoid[-80:]
        avoid_block = (
            "AVOID these topics — we already have articles or queued items on them; "
            "produce genuinely different angles or subtopics, do NOT rephrase these:\n"
            + "\n".join(f"- {t}" for t in sample)
            + "\n\n"
        )
    return f"""You are the content strategist for chinatripbox.com, an English guide site helping foreign visitors travel in China.

Propose {n} NEW, specific, high-search-intent article topics a real traveler would Google. Each must map to exactly one of these categories: {cats}.

{avoid_block}Requirements per topic:
- "keyword": a concrete, natural-language topic/search phrase (not a single word). Specific beats broad — e.g. "how to refill a transit card in Guangzhou" beats "China transport tips".
- "category": exactly one of: {cats}
- "angle": a short differentiating angle so the article won't feel generic (e.g. "for first-time arrivals", "budget vs comfort", "2026 rule changes").
- Spread topics across DIFFERENT categories and DIFFERENT cities/scenarios. Avoid near-duplicates within your own list.

Return ONLY a JSON object (no markdown fence, no commentary):
{{"topics": [{{"keyword": "...", "category": "...", "angle": "..."}}, ...]}}"""


def generate_topics(cfg: Config, n: int, avoid: list[str]) -> list[dict[str, Any]]:
    """调 Claude 生成 n 个候选选题。返回过滤掉非法分类后的列表(可能少于 n)。"""
    import anthropic

    kwargs: dict[str, Any] = {"api_key": cfg.secrets.anthropic_api_key}
    if cfg.anthropic_base_url:
        kwargs["base_url"] = cfg.anthropic_base_url
    client = anthropic.Anthropic(**kwargs)

    resp = client.messages.create(
        model=cfg.model_id,
        max_tokens=2000,
        messages=[{"role": "user", "content": _build_prompt(cfg, n, avoid)}],
    )
    text = "".join(
        b.text for b in resp.content if getattr(b, "type", "") == "text"
    )
    data = _extract_json(text)
    raw = data.get("topics", []) if isinstance(data, dict) else []

    out: list[dict[str, Any]] = []
    for it in raw:
        kw = str(it.get("keyword", "")).strip()
        cat = str(it.get("category", "")).strip()
        if not kw or cat not in cfg.allowed_categories:
            continue  # 丢弃非法分类, 避免后续构建失败
        out.append({"keyword": kw, "category": cat, "angle": str(it.get("angle", "")).strip()})
    return out
