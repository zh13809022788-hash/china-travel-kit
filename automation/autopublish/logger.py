"""日志与当天状态。

- 结构化运行日志: logs/publish-YYYYMMDD.jsonl, 每篇一行
  {title, slug, url, category, publish_time, status, attempts, error}
- 当天配额状态: logs/state-YYYYMMDD.json, 记录 target 与 published, 防重复发。
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import Config


@dataclass
class PublishRecord:
    title: str
    slug: str
    url: str
    category: str
    publish_time: str
    status: str  # "published" | "failed" | "dry-run"
    attempts: int = 1
    error: str = ""


class RunLogger:
    def __init__(self, cfg: Config, date_str: str):
        self.cfg = cfg
        self.date_str = date_str
        self.log_path = cfg.logs_dir / f"publish-{date_str}.jsonl"

    def record(self, rec: PublishRecord) -> None:
        line = json.dumps(asdict(rec), ensure_ascii=False)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(f"  [log] {rec.status.upper()}: {rec.title} ({rec.slug})")

    def index_result(self, engine: str, ok: bool, detail: str, urls: int) -> None:
        entry = {
            "type": "indexing",
            "engine": engine,
            "ok": ok,
            "detail": detail,
            "urls": urls,
            "time": _now_iso(self.cfg),
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class DailyState:
    """当天配额状态, 跨时段共享(同一天三段累加)。"""

    def __init__(self, cfg: Config, date_str: str):
        self.path = cfg.logs_dir / f"state-{date_str}.json"
        self._data: dict[str, Any] = {"date": date_str, "target": None, "published": 0}
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                pass

    @property
    def target(self) -> int | None:
        return self._data.get("target")

    @target.setter
    def target(self, value: int) -> None:
        self._data["target"] = int(value)
        self._flush()

    @property
    def published(self) -> int:
        return int(self._data.get("published", 0))

    def add_published(self, n: int) -> None:
        self._data["published"] = self.published + n
        self._flush()

    def remaining(self) -> int:
        if self.target is None:
            return 0
        return max(0, self.target - self.published)

    def _flush(self) -> None:
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)


def _now_iso(cfg: Config) -> str:
    return now_local(cfg).isoformat(timespec="seconds")


def now_local(cfg: Config) -> datetime:
    """当前本地(配置时区)时间。"""
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo(cfg.timezone))
    except Exception:
        return datetime.now()
