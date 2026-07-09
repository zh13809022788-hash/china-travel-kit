"""选题队列管理: 取题、去重、标记已用。

topics.json 结构:
    { "queue": [ {"keyword": ..., "category": ..., "angle": ..., "used": false}, ... ] }

取题时按 used=false 顺序返回若干条; 发布成功后调用 mark_used 回写。
去重: 已用选题不再取; slug 唯一性由 generator/publisher 侧对文件系统查重保证。
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Topic:
    keyword: str
    category: str
    angle: str = ""
    used: bool = False
    _index: int = -1  # 在 queue 中的原始下标, 用于回写

    def to_dict(self) -> dict[str, Any]:
        d = {"keyword": self.keyword, "category": self.category, "used": self.used}
        if self.angle:
            d["angle"] = self.angle
        return d


class TopicQueue:
    def __init__(self, path: Path):
        self.path = path
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(f"选题队列不存在: {self.path}")
        with open(self.path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
        if "queue" not in self._data or not isinstance(self._data["queue"], list):
            raise ValueError("topics.json 缺少 'queue' 数组")

    def available_count(self) -> int:
        return sum(1 for t in self._data["queue"] if not t.get("used", False))

    def total_count(self) -> int:
        return len(self._data["queue"])

    def all_keywords(self) -> set[str]:
        """队列里全部关键词(含已用), 小写归一, 用于去重。"""
        return {str(t.get("keyword", "")).strip().lower() for t in self._data["queue"]}

    def append(self, items: list[dict[str, Any]]) -> int:
        """追加新选题(去重: 关键词不区分大小写); 返回实际新增条数。"""
        existing = self.all_keywords()
        added = 0
        for it in items:
            kw = str(it.get("keyword", "")).strip()
            if not kw or kw.lower() in existing:
                continue
            self._data["queue"].append(
                {
                    "keyword": kw,
                    "category": it.get("category", ""),
                    "angle": it.get("angle", ""),
                    "used": False,
                }
            )
            existing.add(kw.lower())
            added += 1
        if added:
            self._flush()
        return added

    def take(self, n: int, allowed_categories: list[str] | None = None) -> list[Topic]:
        """取最多 n 条未使用选题(不改动 used, 由 mark_used 在发布成功后置位)。"""
        picked: list[Topic] = []
        for i, item in enumerate(self._data["queue"]):
            if len(picked) >= n:
                break
            if item.get("used", False):
                continue
            category = item.get("category", "")
            if allowed_categories and category not in allowed_categories:
                # 非法分类的选题跳过, 避免生成后构建失败
                continue
            picked.append(
                Topic(
                    keyword=item.get("keyword", "").strip(),
                    category=category,
                    angle=item.get("angle", ""),
                    used=False,
                    _index=i,
                )
            )
        return picked

    def mark_used(self, topic: Topic) -> None:
        """标记某选题为已用并立即回写(逐篇回写, 避免中途崩溃丢状态)。"""
        if 0 <= topic._index < len(self._data["queue"]):
            self._data["queue"][topic._index]["used"] = True
            self._flush()

    def _flush(self) -> None:
        tmp = self.path.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
        tmp.replace(self.path)
