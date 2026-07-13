"""文章生成: 调 Claude API 独立原创英文文章, 组装合法 frontmatter + 唯一 slug。

首要策略: 防止 AI 内容降权。宁可少发、慢发, 也不能发布像批量 AI 生成的泛泛旅游文章。

差异化策略(降低批量 AI 痕迹, 提升海外搜索引擎友好度):
  - 从多套正文骨架模板中随机选一套, 使 H2 结构不雷同;
  - 每篇要求独立信息增量、变化切入角度(angle);
  - description 控制在 150-160 字符;
  - 5-6 条 FAQ;
  - 按 category 在正文中插入对应联盟占位符。

严格约束(否则 astro build 会失败):
  - frontmatter 允许 8 个字段: title, description, pubDate, category, tags, featured, faqs, series(可选)
  - category 必须是允许枚举之一
  - series 可选, 值为 food-of-china|history-of-china|modern-china|nature-of-china|culture-of-china
  - pubDate 为裸 YYYY-MM-DD
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from slugify import slugify

from .config import Config
from .topics import Topic

# 多套正文骨架模板 —— 生成器按索引轮换/随机, 让结构差异化
SKELETONS = [
    [
        "## Introduction",
        "## Before You Start",
        "## Step-by-Step",
        "## Common Mistakes to Avoid",
        "## Summary",
    ],
    [
        "## Why This Matters",
        "## What You Need to Know First",
        "## How It Works in Practice",
        "## Troubleshooting",
        "## Final Tips",
    ],
    [
        "## The Short Answer",
        "## Full Breakdown",
        "## What to Watch Out For",
        "## Real-World Example",
        "## Wrapping Up",
    ],
    [
        "## Overview",
        "## Options Compared",
        "## Our Recommendation",
        "## Setup Walkthrough",
        "## Key Takeaways",
    ],
]

# 系列文章专属骨架模板 —— 灵感/故事型内容结构, 与工具型 SKELETONS 区分
# 每个 series 有多套模板, 生成器按 seed_index 轮换
SERIES_SKELETONS: dict[str, list[list[str]]] = {
    "food-of-china": [
        [
            "## What Makes This Cuisine Distinct",
            "## The Flavors You'll Encounter",
            "## Where to Try It Like a Local",
            "## What to Order First",
            "## Practical Tips for Foreign Visitors",
        ],
        [
            "## The Story Behind the Dish",
            "## Regional Variations",
            "## How to Eat It Properly",
            "## What to Pair It With",
            "## Worth Seeking Out",
        ],
        [
            "## A First Taste",
            "## Decoding the Menu",
            "## What Surprises Foreigners",
            "## How to Find the Real Thing",
            "## Takeaways for Your Trip",
        ],
    ],
    "history-of-china": [
        [
            "## The Story Behind This Place",
            "## What You're Actually Looking At",
            "## How to Visit Without the Crowds",
            "## What Most Tourists Miss",
            "## Practical Visit Tips",
        ],
        [
            "## A Brief History",
            "## Walking the Site",
            "## Decoding What You See",
            "## Nearby Sites Worth Combining",
            "## Planning Your Visit",
        ],
        [
            "## Why This Place Matters",
            "## The Scale of What's Here",
            "## What to Look For",
            "## Logistics and Timing",
            "## Making the Most of Your Visit",
        ],
    ],
    "modern-china": [
        [
            "## The Experience",
            "## Why It's Different Here",
            "## What Surprises Foreigners Most",
            "## How to Navigate It",
            "## Practical Takeaways",
        ],
        [
            "## First Impressions",
            "## How It Actually Works",
            "## What You Need to Prepare",
            "## Common Points of Confusion",
            "## Worth Trying Yourself",
        ],
        [
            "## The Setup",
            "## What's Happening Around You",
            "## How to Participate",
            "## What to Watch Out For",
            "## Final Tips",
        ],
    ],
    "nature-of-china": [
        [
            "## What Makes This Place Special",
            "## The Landscape Explained",
            "## Planning Your Visit",
            "## Best Routes and Viewpoints",
            "## Practical Tips for Foreign Visitors",
        ],
        [
            "## First Impressions",
            "## What You'll See",
            "## How to Get There",
            "## Where to Stay",
            "## Making the Most of Your Time",
        ],
        [
            "## Why This Place Is Worth the Trip",
            "## The Natural Features",
            "## Timing and Seasons",
            "## Navigating the Park",
            "## Essentials to Know Before You Go",
        ],
    ],
    "culture-of-china": [
        [
            "## The Tradition Explained",
            "## Where It Comes From",
            "## How to Experience It as a Visitor",
            "## What to Try or Buy",
            "## Practical Tips",
        ],
        [
            "## A Cultural Deep Dive",
            "## What It Means in Daily Life",
            "## Where Visitors Can Engage",
            "## Common Misunderstandings",
            "## Takeaways for Travelers",
        ],
        [
            "## The Background",
            "## What You're Seeing",
            "## How Locals Experience It",
            "## Where to Participate",
            "## Worth Exploring Further",
        ],
    ],
}

# 系列专属事实核查红线 —— 历史/文化高风险, 美食/自然/现代中风险
SERIES_PROMPT_RULES: dict[str, str] = {
    "history-of-china": (
        "SERIES-SPECIFIC RULES (History — high fact-risk):\n"
        "- Do not invent historical dates, dynasty names, quotes, or architectural facts.\n"
        "- If a fact is uncertain or historically debated, state that explicitly rather than presenting it as certain.\n"
        "- Cross-check dynasty names and dates against the standard Chinese dynasty timeline.\n"
        "- When describing sites, use only verifiable facts about location, size, and history."
    ),
    "culture-of-china": (
        "SERIES-SPECIFIC RULES (Culture — high fact-risk):\n"
        "- Do not invent historical dates, dynasty names, quotes, or architectural facts.\n"
        "- If a fact is uncertain or historically debated, state that explicitly rather than presenting it as certain.\n"
        "- Attribute cultural practices to the correct region or tradition."
    ),
    "food-of-china": (
        "SERIES-SPECIFIC RULES (Food — medium fact-risk):\n"
        "- Do not invent specific restaurant names, prices, or opening hours.\n"
        "- When describing regional dishes, attribute them to the correct region."
    ),
    "nature-of-china": (
        "SERIES-SPECIFIC RULES (Nature — medium fact-risk):\n"
        "- Do not invent specific prices, permit requirements, or access policies.\n"
        "- When describing natural features, use only verifiable geological and geographical facts.\n"
        "- Note that permit and access rules for foreign visitors can change."
    ),
    "modern-china": (
        "SERIES-SPECIFIC RULES (Modern China — medium fact-risk):\n"
        "- Do not fabricate statistics about China's economy, population, or infrastructure.\n"
        "- When describing experiences (trains, payments, apps), keep claims verifiable and current."
    ),
}


@dataclass
class GeneratedPost:
    title: str
    description: str
    category: str
    tags: list[str]
    featured: bool
    faqs: list[dict[str, str]]
    body: str
    slug: str
    series: str = ""

    def to_markdown(self, pub_date: str) -> str:
        """组装完整 .md 文件内容(YAML frontmatter + 正文)。"""
        fm: list[str] = ["---"]
        fm.append(f"title: {_yaml_str(self.title)}")
        fm.append(f"description: {_yaml_str(self.description)}")
        fm.append(f"pubDate: {pub_date}")  # 裸 YYYY-MM-DD
        fm.append(f"category: {self.category}")
        if self.series:
            fm.append(f"series: {self.series}")
        fm.append("tags: [" + ", ".join(_yaml_str(t) for t in self.tags) + "]")
        fm.append(f"featured: {'true' if self.featured else 'false'}")
        if self.faqs:
            fm.append("faqs:")
            for qa in self.faqs:
                fm.append(f"  - question: {_yaml_str(qa['question'])}")
                fm.append(f"    answer: {_yaml_str(qa['answer'])}")
        else:
            fm.append("faqs: []")
        fm.append("---")
        return "\n".join(fm) + "\n\n" + self.body.strip() + "\n"


def _yaml_str(s: str) -> str:
    """安全地把字符串写成双引号 YAML 标量(转义内部双引号与反斜杠)。"""
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def _existing_slugs(posts_dir: Path) -> set[str]:
    if not posts_dir.exists():
        return set()
    return {p.stem for p in posts_dir.glob("*.md")}


def _unique_slug(title: str, taken: set[str]) -> str:
    base = slugify(title, max_length=70) or "post"
    slug = base
    n = 2
    while slug in taken:
        slug = f"{base}-{n}"
        n += 1
    return slug


class Generator:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._client = None  # 延迟初始化, dry-run 不强制建连

    def _client_lazy(self):
        if self._client is None:
            import anthropic  # 延迟导入, 便于无密钥时的 import 阶段

            kwargs = {"api_key": self.cfg.secrets.anthropic_api_key}
            # 第三方代理 key(非 sk-ant-) 需指定 base_url; 官方 key 留空即可
            if self.cfg.anthropic_base_url:
                kwargs["base_url"] = self.cfg.anthropic_base_url
            self._client = anthropic.Anthropic(**kwargs)
        return self._client

    def _build_prompt(self, topic: Topic, skeleton: list[str]) -> str:
        affiliate = self.cfg.affiliate_map.get(topic.category, "")
        affiliate_line = (
            f"- Insert the exact literal HTML comment {affiliate} on its own line at a natural "
            f"point in the body (e.g. after a relevant recommendation). Do not alter its text.\n"
            if affiliate
            else ""
        )
        angle_line = f"- Angle / unique take for this article: {topic.angle}\n" if topic.angle else ""
        series_rules = SERIES_PROMPT_RULES.get(topic.series, "")
        series_block = f"\n{series_rules}\n" if series_rules else ""
        skeleton_str = "\n".join(skeleton)
        return f"""You are an expert travel writer producing an ORIGINAL English article for chinatripbox.com, a guide site for foreigners traveling in China.

Primary quality rule: protect chinatripbox.com from AI-content devaluation. If the draft would read like a generic AI travel article, rewrite it before returning JSON. The article must feel edited, specific, and useful enough that a traveler would save it before a China trip.

Write a completely original, factual, genuinely useful article. Do NOT copy or paraphrase any specific external source — write from general, well-established travel knowledge. Each article must add its own information increment (concrete steps, comparisons, numbers, caveats a real traveler needs).

TOPIC: {topic.keyword}
CATEGORY: {topic.category}
{angle_line}{series_block}
STRUCTURE — use these H2 section headings, in this order (you may add ### subsections and adapt wording naturally, but keep the overall flow):
{skeleton_str}

REQUIREMENTS:
- Natural, human, specific prose. Vary sentence length. Avoid generic filler and obvious AI boilerplate ("In today's fast-paced world", "Whether you're a...").
- Avoid AI-content tells: no generic significance claims, no promotional travel-brochure tone, no vague attributions like "experts say", no "let's dive in", no formulaic "in conclusion", no padded summary, no repetitive rule-of-three phrasing, and no overuse of em dashes.
- Add practical judgment: include real traveler constraints, failure cases, backup plans, thresholds, timing, app/payment/transport friction, or "when not to do this" details where relevant.
- Prefer concrete, checkable statements over broad advice. Do not invent official policy, prices, limits, or app behavior; if details vary, say exactly what varies and what the traveler should verify.
- If the topic is payment, visa, transport, telecom, safety, or health-adjacent, include a concise caution to verify current rules with the relevant official provider or authority.
- Use Markdown: ## / ### headings, **bold**, ordered and unordered lists where helpful. No images.
{affiliate_line}- End with a short summary section (per the structure above).

Return ONLY a single JSON object (no markdown fence, no commentary) with EXACTLY these keys:
{{
  "title": "compelling, specific, <= 65 chars, unique phrasing",
  "description": "meta description, MUST be 150-160 characters",
  "tags": ["3-5 lowercase keyword tags"],
  "faqs": [{{"question": "...", "answer": "full-sentence answer"}}, ...],   // 5 to 6 items
  "body": "the full article body in Markdown, starting at the first H2 heading"
}}

The "body" must NOT contain the frontmatter or the title as an H1. Start directly with the first ## heading."""

    def generate(self, topic: Topic, *, seed_index: int, extra_taken: set[str] | None = None) -> GeneratedPost:
        """生成一篇文章。seed_index 用于确定性地轮换骨架模板(避免依赖随机源)。"""
        if topic.series and topic.series in SERIES_SKELETONS:
            series_skel = SERIES_SKELETONS[topic.series]
            skeleton = series_skel[seed_index % len(series_skel)]
        else:
            skeleton = SKELETONS[seed_index % len(SKELETONS)]
        prompt = self._build_prompt(topic, skeleton)

        client = self._client_lazy()
        resp = client.messages.create(
            model=self.cfg.model_id,
            max_tokens=self.cfg.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", "") == "text"
        )
        data = _extract_json(text)

        title = str(data["title"]).strip()
        description = _clamp_description(str(data["description"]).strip())
        tags = [str(t).strip() for t in data.get("tags", []) if str(t).strip()][:5]
        faqs_raw = data.get("faqs", [])
        faqs = [
            {"question": str(qa["question"]).strip(), "answer": str(qa["answer"]).strip()}
            for qa in faqs_raw
            if qa.get("question") and qa.get("answer")
        ]
        body = str(data["body"]).strip()

        if topic.category not in self.cfg.allowed_categories:
            raise ValueError(
                f"选题分类非法: {topic.category!r} 不在 {self.cfg.allowed_categories}"
            )

        taken = _existing_slugs(self.cfg.posts_dir) | (extra_taken or set())
        slug = _unique_slug(title, taken)

        featured = self._decide_featured(seed_index)

        return GeneratedPost(
            title=title,
            description=description,
            category=topic.category,
            tags=tags,
            featured=featured,
            faqs=faqs,
            body=body,
            slug=slug,
            series=topic.series,
        )

    def _decide_featured(self, seed_index: int) -> bool:
        ratio = self.cfg.featured_ratio
        if ratio <= 0:
            return False
        # 确定性: 每 round(1/ratio) 篇里 1 篇 featured
        step = max(1, round(1 / ratio))
        return seed_index % step == 0


def _extract_json(text: str) -> dict[str, Any]:
    """从模型返回中稳健地抽取 JSON 对象(容忍 ```json 包裹或前后杂字)。"""
    text = text.strip()
    # 去掉可能的 markdown fence
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 回退: 抓第一个 { 到最后一个 }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise ValueError(f"无法从模型返回中解析 JSON: {text[:200]}...")


def _clamp_description(desc: str) -> str:
    """description 目标 150-160 字符; 过长截断到 160(尽量在词边界)。"""
    if len(desc) <= 160:
        return desc
    cut = desc[:159]  # 留 1 位给结尾句号, 保证 <= 160
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(",. ") + "."
