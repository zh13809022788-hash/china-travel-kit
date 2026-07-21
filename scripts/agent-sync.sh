#!/usr/bin/env bash
# agent-sync — 多电脑多 Agent 协作通信工具
# 用法:
#   ./agent-sync.sh say "消息内容"      # 发消息，所有人可见
#   ./agent-sync.sh claim "任务名"      # 认领任务
#   ./agent-sync.sh done "任务名"       # 完成任务
#   ./agent-sync.sh status             # 查看当前状态
#   ./agent-sync.sh pull               # 拉取最新状态

set -e

# Hermes provider must be openai (uses .env OPENAI_API_KEY + OPENAI_BASE_URL)
# 不加 --provider openai 的话 Hermes 默认走 openrouter，会 401
HERMES="/c/Users/Administrator/bin/hermes"
# === 配置 ===
# 设置环境变量 GIT_TOKEN（或在 ~/.bashrc 里 export）
# Token 需要 repo + workflow 权限
REPO_URL="https://zh13809022788-hash:${GIT_TOKEN:?请设置 GIT_TOKEN 环境变量}@github.com/zh13809022788-hash/china-travel-kit.git"
SYNC_FILE="docs/AGENT_SYNC.md"
AGENT_NAME="${AGENT_NAME:-unknown-agent}"
WORKSPACE="${WORKSPACE:-$(pwd)}"

# === 工具函数 ===
ensure_repo() {
  if [ ! -f "$WORKSPACE/.git/HEAD" ]; then
    echo "⚠️  当前目录不是 git 仓库，尝试 clone..."
    cd /tmp
    git clone --depth 10 "$REPO_URL" china_sync 2>/dev/null || true
    if [ -d /tmp/china_sync ]; then
      WORKSPACE="/tmp/china_sync"
      cd "$WORKSPACE"
    fi
  fi
  cd "$WORKSPACE"
  git pull origin main 2>/dev/null || true
}

timestamp() {
  date '+%Y-%m-%d %H:%M'
}

# === 命令 ===
case "${1:-status}" in
  say)
    shift
    MSG="$*"
    ensure_repo
    echo "" >> "$SYNC_FILE"
    echo "---" >> "$SYNC_FILE"
    echo "**【$(timestamp)】** **$AGENT_NAME**" >> "$SYNC_FILE"
    echo "" >> "$SYNC_FILE"
    echo "$MSG" >> "$SYNC_FILE"
    echo "" >> "$SYNC_FILE"
    git add "$SYNC_FILE"
    git commit -m "sync: $AGENT_NAME - $MSG" --allow-empty
    git push origin main 2>/dev/null || echo "⚠️  push 失败，稍后重试"
    echo "✅ 消息已发送"
    ;;

  claim)
    shift
    TASK="$*"
    ensure_repo
    # 在任务看板里找对应任务，标记为 [进行中]
    # 简单方式：在底部加一条记录
    echo "" >> "$SYNC_FILE"
    echo "**【$(timestamp)】** **$AGENT_NAME** 认领任务: **$TASK**" >> "$SYNC_FILE"
    echo "" >> "$SYNC_FILE"
    git add "$SYNC_FILE"
    git commit -m "sync: $AGENT_NAME claimed '$TASK'"
    git push origin main 2>/dev/null || echo "⚠️  push 失败"
    echo "✅ 已认领: $TASK"
    ;;

  done)
    shift
    TASK="$*"
    ensure_repo
    COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "?")
    echo "" >> "$SYNC_FILE"
    echo "**【$(timestamp)】** **$AGENT_NAME** 完成任务: **$TASK** (HEAD: $COMMIT)" >> "$SYNC_FILE"
    echo "" >> "$SYNC_FILE"
    git add "$SYNC_FILE"
    git commit -m "sync: $AGENT_NAME completed '$TASK'"
    git push origin main 2>/dev/null || echo "⚠️  push 失败"
    echo "✅ 已完成: $TASK"
    ;;

  status)
    ensure_repo
    if [ -f "$SYNC_FILE" ]; then
      echo "=== 最新同步状态 ==="
      tail -30 "$SYNC_FILE"
    else
      echo "⚠️  未找到 $SYNC_FILE"
    fi
    ;;

  pull)
    ensure_repo
    echo "✅ 已同步到最新"
    tail -10 "$SYNC_FILE" 2>/dev/null || true
    ;;

  help|--help|-h)
    echo "agent-sync — 多 Agent 协作通信工具"
    echo ""
    echo "用法:"
    echo "  ./agent-sync.sh say \"消息\"     # 发消息"
    echo "  ./agent-sync.sh claim \"任务\"    # 认领任务"
    echo "  ./agent-sync.sh done \"任务\"     # 完成任务"
    echo "  ./agent-sync.sh status          # 看最新状态"
    echo "  ./agent-sync.sh pull            # 拉取更新"
    echo ""
    echo "环境变量:"
    echo "  AGENT_NAME=my-name    # 设置你的名字（默认: unknown-agent）"
    echo "  WORKSPACE=/path       # 指定仓库目录"
    ;;

  *)
    echo "未知命令: $1"
    echo "用法: ./agent-sync.sh help"
    exit 1
    ;;
esac
