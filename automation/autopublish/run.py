"""主流程编排 —— 单个时段执行一次。

流程:
  1. 算配额: 当天目标 = 稳定值(daily_min..daily_max), 均分到三段(余数打散);
             用 state-YYYYMMDD.json 记录当天已发, 防重复。
  2. 取题: 从 topics.json 取本段份额数量的未用选题。
  3. 逐篇生成(失败重试1次) + 逐篇写文件 + 篇间随机延时。
  4. 本段全部写完 -> 一次 git commit + push (触发 CI 构建, sitemap 自动重建)。
  5. 批量推送收录(百度 / 可选 IndexNow), 失败重试1次。
  6. 记录结构化日志, 更新当天已发计数。

用法:
  python -m automation.autopublish.run                 # 自动判断当前时段份额
  python -m automation.autopublish.run --count 3       # 强制本次发 3 篇
  python -m automation.autopublish.run --slot 09:00    # 指定按哪个时段算份额
  python -m automation.autopublish.run --dry-run       # 只生成到临时目录, 不 push 不推送收录
  python -m automation.autopublish.run --config path/to/config.toml
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

# Windows 任务计划/Cron 的默认控制台常是 GBK, 打印中文或符号(如 ✓)会抛
# UnicodeEncodeError 导致进程非零退出、甚至中途崩溃丢文章。这里强制 stdout/stderr
# 走 UTF-8 并对不可编码字符降级替换, 保证无人值守运行稳定。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

from .config import Config, ConfigError, load_config
from .generator import Generator, GeneratedPost
from .indexing import push_all
from . import publisher
from .logger import DailyState, PublishRecord, RunLogger, now_local
from .topics import Topic, TopicQueue
from .topic_gen import generate_topics


def _daily_target(cfg: Config, date_str: str) -> int:
    """当天目标产出数。取 [daily_min, daily_max] 内一个按日期确定的稳定值,
    保证同一天三段调用得到同一目标(不依赖随机源, 便于复现)。"""
    lo, hi = cfg.daily_min, cfg.daily_max
    if hi <= lo:
        return lo
    h = int(hashlib.sha256(date_str.encode()).hexdigest(), 16)
    return lo + (h % (hi - lo + 1))


def _slot_share(target: int, n_slots: int, slot_index: int) -> int:
    """把 target 均分到 n_slots 段, 余数从前面的时段起逐段 +1。"""
    base = target // n_slots
    rem = target % n_slots
    return base + (1 if slot_index < rem else 0)


def _current_slot_index(cfg: Config, slot_arg: str | None) -> int:
    slots = cfg.slots
    if slot_arg:
        if slot_arg in slots:
            return slots.index(slot_arg)
        raise SystemExit(f"--slot {slot_arg} 不在配置的时段 {slots} 中")
    # 按当前本地时间选最接近且已到达的时段; 取 <= now 的最后一个, 否则第 0 段
    now = now_local(cfg)
    now_minutes = now.hour * 60 + now.minute
    chosen = 0
    for i, s in enumerate(slots):
        hh, mm = s.split(":")
        smin = int(hh) * 60 + int(mm)
        if now_minutes >= smin - 30:  # 允许 cron 早触发 30 分钟内归入该段
            chosen = i
    return chosen


def _generate_with_retry(gen: Generator, topic: Topic, seed_index: int,
                         extra_taken: set[str]) -> tuple[GeneratedPost | None, int, str]:
    """生成一篇, 失败重试1次。返回 (post|None, attempts, error)。"""
    last_err = ""
    for attempt in (1, 2):
        try:
            post = gen.generate(topic, seed_index=seed_index, extra_taken=extra_taken)
            return post, attempt, ""
        except Exception as e:  # noqa: BLE001 - 记录并重试
            last_err = f"{type(e).__name__}: {e}"
            print(f"  [gen] attempt {attempt} failed for '{topic.keyword}': {last_err}")
    return None, 2, last_err


def run_slot(cfg: Config, *, count: int | None, slot: str | None, dry_run: bool) -> int:
    date_str = now_local(cfg).strftime("%Y%m%d")
    pub_date = now_local(cfg).strftime("%Y-%m-%d")

    state = DailyState(cfg, date_str)
    if state.target is None:
        state.target = _daily_target(cfg, date_str)
    target = state.target

    # 计算本次份额
    if count is not None:
        share = count
    else:
        slot_idx = _current_slot_index(cfg, slot)
        share = _slot_share(target, len(cfg.slots), slot_idx)
    # 不能超过当天剩余配额(硬上限 clamp)
    share = max(0, min(share, state.remaining()))

    print(f"=== chinatripbox autopublish ===")
    print(f"date={date_str} daily_target={target} already_published={state.published} "
          f"this_run_share={share} dry_run={dry_run}")
    if share == 0:
        print("本时段份额为 0(当天配额已满或已发完), 退出。")
        return 0

    queue = TopicQueue(cfg.topics_path)

    # 队列可用选题不足本次份额时, 让大模型自主补题(可用 config 关闭)
    if cfg.autogen_topics and queue.available_count() < share:
        need = share - queue.available_count()
        # 多生成一些做缓冲, 减少下次调用频率
        want = max(need, cfg.autogen_batch)
        print(f"选题不足({queue.available_count()}<{share}), 调用大模型补题 {want} 个...")
        try:
            avoid = sorted(queue.all_keywords())
            candidates = generate_topics(cfg, want, avoid)
            added = queue.append(candidates)
            print(f"  自动补题: 生成 {len(candidates)} 个, 去重后新增 {added} 个, "
                  f"现可用 {queue.available_count()}。")
        except Exception as e:  # noqa: BLE001 - 补题失败不应中断已有选题的发布
            print(f"  ⚠ 自动补题失败: {type(e).__name__}: {e}(继续用现有选题)")

    if queue.available_count() == 0:
        print("⚠ 选题队列为空且未能自动补题, 无法生成。请补充 topics.json 或检查 API。")
        return 0
    topics = queue.take(share, allowed_categories=cfg.allowed_categories)
    if not topics:
        print("⚠ 没有取到合法选题(分类不匹配或全部已用)。")
        return 0

    gen = Generator(cfg)
    logger = RunLogger(cfg, date_str)

    dry_dir: Path | None = None
    if dry_run:
        dry_dir = Path(tempfile.mkdtemp(prefix="chinatripbox_dryrun_"))
        print(f"[dry-run] 文章将写入临时目录: {dry_dir}")

    written_paths: list[Path] = []
    written_urls: list[str] = []
    batch_taken: set[str] = set()  # 本批内 slug 去重(还未落盘时)
    published_topics: list[Topic] = []

    for i, topic in enumerate(topics):
        print(f"\n[{i+1}/{len(topics)}] topic: {topic.keyword} ({topic.category})")
        post, attempts, err = _generate_with_retry(gen, topic, seed_index=i, extra_taken=batch_taken)
        ts = now_local(cfg).isoformat(timespec="seconds")

        if post is None:
            logger.record(PublishRecord(
                title=topic.keyword, slug="", url="", category=topic.category,
                publish_time=ts, status="failed", attempts=attempts, error=err,
            ))
            continue

        try:
            path = publisher.write_post(cfg, post, pub_date, dry_run_dir=dry_dir)
        except Exception as e:  # noqa: BLE001
            logger.record(PublishRecord(
                title=post.title, slug=post.slug, url="", category=post.category,
                publish_time=ts, status="failed", attempts=attempts,
                error=f"write failed: {e}",
            ))
            continue

        batch_taken.add(post.slug)
        written_paths.append(path)
        url = cfg.post_url(post.slug)
        written_urls.append(url)
        published_topics.append(topic)

        logger.record(PublishRecord(
            title=post.title, slug=post.slug, url=url, category=post.category,
            publish_time=ts, status="dry-run" if dry_run else "published",
            attempts=attempts,
        ))

        # 篇间随机延时(最后一篇后不必等)
        if i < len(topics) - 1:
            publisher.sleep_jitter(cfg, quiet=dry_run)

    if not written_paths:
        print("\n本次没有成功生成任何文章。")
        return 0

    if dry_run:
        print(f"\n[dry-run] 完成, 生成 {len(written_paths)} 篇于 {dry_dir}。未 push、未推送收录、未改动 topics/state。")
        print("[dry-run] 建议接着运行: cd <repo> && npm run build  以校验 frontmatter。")
        return len(written_paths)

    # 真发布: 提交 + push
    msg = f"content: publish {len(written_paths)} article(s) [{date_str}]"
    try:
        publisher.commit_and_push(cfg, written_paths, msg)
    except publisher.PublishError as e:
        print(f"✗ git 发布失败: {e}")
        print("  文件已写入但未推送。修复后可手动 commit/push, 或重跑(slug 已存在会跳过)。")
        return len(written_paths)

    # 发布成功 -> 标记选题已用 + 更新当天计数
    for t in published_topics:
        queue.mark_used(t)
    state.add_published(len(written_paths))

    # 收录推送
    results = push_all(cfg, written_urls)
    for res in results:
        logger.index_result(res.engine, res.ok, res.detail, res.submitted)

    print(f"\n✓ 本时段完成: 发布 {len(written_paths)} 篇, 当天累计 {state.published}/{target}。")
    return len(written_paths)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="chinatripbox.com 自动发布(单时段)")
    parser.add_argument("--config", default=None, help="config.toml 路径(默认 automation/config.toml)")
    parser.add_argument("--count", type=int, default=None, help="强制本次发布篇数(覆盖时段份额)")
    parser.add_argument("--slot", default=None, help="指定时段(如 09:00)以计算份额")
    parser.add_argument("--dry-run", action="store_true", help="只生成到临时目录, 不 push、不推送收录")
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config)
        # dry-run 不推收录, 无需 BAIDU_TOKEN/INDEXNOW_KEY
        cfg.validate(require_generation=True, require_indexing=not args.dry_run)
    except ConfigError as e:
        print(f"配置错误: {e}", file=sys.stderr)
        return 2

    try:
        run_slot(cfg, count=args.count, slot=args.slot, dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n已中断。")
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
