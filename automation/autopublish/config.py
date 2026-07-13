"""配置加载: 读取 config.toml (非密钥) + 环境变量 (密钥)。

密钥永远不进 toml, 避免入库泄露。缺失必填项时给出清晰报错。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fallback for 3.10-
    import tomli as tomllib  # type: ignore

# automation/ 目录 (本文件的上两级: autopublish/config.py -> autopublish -> automation)
AUTOMATION_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = AUTOMATION_DIR / "config.toml"
EXAMPLE_CONFIG_PATH = AUTOMATION_DIR / "config.example.toml"


class ConfigError(RuntimeError):
    """配置缺失或非法。"""


@dataclass
class Secrets:
    anthropic_api_key: str | None = None
    baidu_token: str | None = None
    indexnow_key: str | None = None
    git_push_token: str | None = None

    @classmethod
    def from_env(cls) -> "Secrets":
        return cls(
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
            baidu_token=os.environ.get("BAIDU_TOKEN"),
            indexnow_key=os.environ.get("INDEXNOW_KEY"),
            git_push_token=os.environ.get("GIT_PUSH_TOKEN"),
        )


@dataclass
class Config:
    raw: dict[str, Any]
    secrets: Secrets
    automation_dir: Path

    # ---- site ----
    @property
    def domain(self) -> str:
        return self._site["domain"]

    @property
    def repo_path(self) -> Path:
        # repo_path 相对 automation/ 的父目录(仓库根)解析
        p = Path(self._site.get("repo_path", "."))
        if not p.is_absolute():
            p = (self.automation_dir.parent / p).resolve()
        return p

    @property
    def posts_dir(self) -> Path:
        return (self.repo_path / self._site.get("posts_dir", "src/content/posts")).resolve()

    @property
    def git_branch(self) -> str:
        return self._site.get("git_branch", "main")

    @property
    def post_url_tmpl(self) -> str:
        return self._site.get("post_url_tmpl", "https://{domain}/posts/{slug}/")

    def post_url(self, slug: str) -> str:
        return self.post_url_tmpl.format(domain=self.domain, slug=slug)

    # ---- schedule ----
    @property
    def slots(self) -> list[str]:
        return list(self._schedule.get("slots", ["09:00", "15:00", "20:00"]))

    @property
    def timezone(self) -> str:
        return self._schedule.get("timezone", "Asia/Shanghai")

    @property
    def daily_min(self) -> int:
        return int(self._schedule.get("daily_min", 8))

    @property
    def daily_max(self) -> int:
        return int(self._schedule.get("daily_max", 10))

    @property
    def jitter_range(self) -> tuple[int, int]:
        lo, hi = self._schedule.get("per_slot_jitter_sec", [30, 180])
        return int(lo), int(hi)

    @property
    def featured_ratio(self) -> float:
        return float(self._schedule.get("featured_ratio", 0.0))

    @property
    def autogen_topics(self) -> bool:
        """队列不足时是否让大模型自动补题(默认开启)。"""
        return bool(self._schedule.get("autogen_topics", True))

    @property
    def autogen_batch(self) -> int:
        """每次自动补题生成的数量(缓冲, 减少调用频率)。"""
        return int(self._schedule.get("autogen_batch", 10))

    # ---- model ----
    @property
    def provider(self) -> str:
        return self._model.get("provider", "anthropic")

    @property
    def model_id(self) -> str:
        return self._model.get("model_id", "claude-opus-4-8")

    @property
    def max_tokens(self) -> int:
        return int(self._model.get("max_tokens", 8000))

    @property
    def anthropic_base_url(self) -> str | None:
        """第三方代理的 API 地址。优先取环境变量 ANTHROPIC_BASE_URL,
        其次取 config.toml 的 [model].base_url; 官方 key 时留空。"""
        return os.environ.get("ANTHROPIC_BASE_URL") or self._model.get("base_url") or None

    # ---- indexing ----
    @property
    def baidu_enabled(self) -> bool:
        return bool(self._indexing.get("baidu_enabled", False))

    @property
    def baidu_endpoint(self) -> str:
        return self._indexing.get(
            "baidu_endpoint", "http://data.zz.baidu.com/urls?site={site}&token={token}"
        )

    @property
    def indexnow_enabled(self) -> bool:
        return bool(self._indexing.get("indexnow_enabled", False))

    @property
    def indexnow_endpoint(self) -> str:
        return self._indexing.get("indexnow_endpoint", "https://api.indexnow.org/indexnow")

    @property
    def retry_once(self) -> bool:
        return bool(self._indexing.get("retry_once", True))

    # ---- categories ----
    @property
    def allowed_categories(self) -> list[str]:
        return list(
            self._categories.get(
                "allowed", ["payment", "esim", "transport", "essentials", "food"]
            )
        )

    @property
    def affiliate_map(self) -> dict[str, str]:
        return dict(self._categories.get("affiliate", {}))

    # ---- paths ----
    @property
    def logs_dir(self) -> Path:
        d = self.automation_dir / "logs"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def topics_path(self) -> Path:
        return self.automation_dir / "topics.json"

    # ---- section shortcuts ----
    @property
    def _site(self) -> dict[str, Any]:
        return self.raw.get("site", {})

    @property
    def _schedule(self) -> dict[str, Any]:
        return self.raw.get("schedule", {})

    @property
    def _model(self) -> dict[str, Any]:
        return self.raw.get("model", {})

    @property
    def _indexing(self) -> dict[str, Any]:
        return self.raw.get("indexing", {})

    @property
    def _categories(self) -> dict[str, Any]:
        return self.raw.get("categories", {})

    # ---- validation ----
    def validate(self, *, require_generation: bool = True, require_indexing: bool = True) -> None:
        """校验关键项。dry-run 下 require_generation=True 仍需 API key 才能生成,
        但 require_indexing=False 可跳过收录密钥校验(dry-run 不推收录)。"""
        if not self.domain:
            raise ConfigError("site.domain 未配置")
        if require_generation and not self.secrets.anthropic_api_key:
            raise ConfigError(
                "缺少环境变量 ANTHROPIC_API_KEY —— 生成文章需要 Claude API 密钥"
            )
        if require_indexing and self.baidu_enabled and not self.secrets.baidu_token:
            raise ConfigError(
                "indexing.baidu_enabled=true 但缺少环境变量 BAIDU_TOKEN"
            )
        if require_indexing and self.indexnow_enabled and not self.secrets.indexnow_key:
            raise ConfigError(
                "indexing.indexnow_enabled=true 但缺少环境变量 INDEXNOW_KEY"
            )
        if self.daily_min > self.daily_max:
            raise ConfigError(
                f"daily_min({self.daily_min}) 不能大于 daily_max({self.daily_max})"
            )


def load_config(path: str | os.PathLike[str] | None = None) -> Config:
    """加载配置。未找到 config.toml 时回退到 config.example.toml 并提示。"""
    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not cfg_path.exists():
        if EXAMPLE_CONFIG_PATH.exists():
            raise ConfigError(
                f"未找到 {cfg_path.name}。请先复制模板:\n"
                f"  cp {EXAMPLE_CONFIG_PATH} {DEFAULT_CONFIG_PATH}\n"
                f"然后按需修改。"
            )
        raise ConfigError(f"配置文件不存在: {cfg_path}")

    with open(cfg_path, "rb") as f:
        raw = tomllib.load(f)

    return Config(raw=raw, secrets=Secrets.from_env(), automation_dir=AUTOMATION_DIR)
