"""落地与发布: 写 .md 文件, 批内随机延时, git add/commit/push。

发布节奏: 同一时段内逐篇写入, 每篇之间 sleep(随机延时) 模拟人工;
本段全部写完后一次性 commit + push(一段一次构建, 全天 3 次)。
push 触发 CI 构建 -> @astrojs/sitemap 自动重建 sitemap。
"""
from __future__ import annotations

import random
import subprocess
import time
from pathlib import Path

from .config import Config
from .generator import GeneratedPost


class PublishError(RuntimeError):
    pass


def write_post(cfg: Config, post: GeneratedPost, pub_date: str, *, dry_run_dir: Path | None = None) -> Path:
    """把文章写成 .md 文件, 返回文件路径。dry_run_dir 非空时写到该临时目录。"""
    target_dir = dry_run_dir if dry_run_dir is not None else cfg.posts_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{post.slug}.md"
    if path.exists() and dry_run_dir is None:
        raise PublishError(f"目标文件已存在, slug 冲突: {path.name}")
    path.write_text(post.to_markdown(pub_date), encoding="utf-8")
    return path


def sleep_jitter(cfg: Config, *, quiet: bool = False) -> float:
    lo, hi = cfg.jitter_range
    if hi <= 0:
        return 0.0
    secs = random.randint(lo, hi)
    if not quiet:
        print(f"  [jitter] sleeping {secs}s to mimic human pacing...")
    time.sleep(secs)
    return float(secs)


# ----------------------------- git -----------------------------

def _git(cfg: Config, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cfg.repo_path),
        capture_output=True,
        text=True,
        check=check,
    )


def _remote_with_token(cfg: Config) -> str | None:
    """本地免交互 push: 若配置了 GIT_PUSH_TOKEN, 构造带 token 的 https remote url。

    仅在需要时用于单次 push, 不写回 git config, 避免 token 落盘。
    """
    token = cfg.secrets.git_push_token
    if not token:
        return None
    res = _git(cfg, "remote", "get-url", "origin", check=False)
    url = (res.stdout or "").strip()
    if url.startswith("https://") and "@" not in url.split("//", 1)[1].split("/", 1)[0]:
        return url.replace("https://", f"https://x-access-token:{token}@", 1)
    return None


def commit_and_push(cfg: Config, paths: list[Path], message: str) -> None:
    """git add 指定文件 -> commit -> push 到目标分支。失败抛 PublishError。"""
    if not paths:
        return
    rel = [str(p.resolve()) for p in paths]
    add = _git(cfg, "add", *rel, check=False)
    if add.returncode != 0:
        raise PublishError(f"git add 失败: {add.stderr.strip()}")

    commit = _git(cfg, "commit", "-m", message, check=False)
    if commit.returncode != 0:
        # 没有变更时 git commit 返回非 0, 视为无事可做
        if "nothing to commit" in (commit.stdout + commit.stderr).lower():
            print("  [git] nothing to commit.")
            return
        raise PublishError(f"git commit 失败: {commit.stderr.strip() or commit.stdout.strip()}")

    push_url = _remote_with_token(cfg)
    if push_url:
        push = _git(cfg, "push", push_url, f"HEAD:{cfg.git_branch}", check=False)
    else:
        push = _git(cfg, "push", "origin", f"HEAD:{cfg.git_branch}", check=False)
    if push.returncode != 0:
        raise PublishError(f"git push 失败: {push.stderr.strip()}")
    print(f"  [git] pushed {len(paths)} file(s) to {cfg.git_branch}.")
