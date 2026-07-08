# chinatripbox.com 自动原创发布流水线

每天由 Claude 独立原创英文旅游文章，分三个时段（09:00 / 15:00 / 20:00）少量、带随机延时地发布，
每批发布后触发站点重建（sitemap 自动更新）并推送百度收录，全程记录日志、失败重试一次。

- **纯自主原创**：不抓取外部网页，规避侵权与爬虫风险。素材来自你维护的选题队列 `topics.json` + 站点五大分类。
- **两套方案**：① GitHub Actions 云端定时（无需本地开机）② 本地 Python 脚本（Windows 任务计划 / Cron）。
- **不改动站点源码**：只向 `src/content/posts/` 写 `.md`，发布沿用现有 CI 构建 + 部署。

---

## 目录结构

```
automation/
├── config.example.toml       # 配置模板 -> 复制为 config.toml
├── config.toml               # 你的实际配置(git 忽略)
├── topics.json               # 选题/关键词队列(你维护)
├── requirements.txt
├── autopublish/              # Python 包
│   ├── config.py  topics.py  generator.py
│   ├── publisher.py  indexing.py  logger.py  run.py
└── logs/                     # 运行日志 & 当天状态(git 忽略)
.github/workflows/scheduled-publish.yml   # 方案① 云端定时任务
```

---

## 快速开始（本地，方案②）

前置：Python 3.11+（本机为 3.14，自带 `tomllib`）、`git`、`node`/`npm`。

```bash
cd D:/独立站/china-travel-kit

# 1) 安装依赖
pip install -r automation/requirements.txt

# 2) 生成配置
cp automation/config.example.toml automation/config.toml
#   按需编辑 automation/config.toml（域名、时段、每日上下限、收录接口等）

# 3) 设置密钥(环境变量, 不写进 toml)
export ANTHROPIC_API_KEY="sk-ant-..."        # 必填
# export ANTHROPIC_BASE_URL="https://your-proxy..."  # 用第三方代理 key(非 sk-ant-)时必填
export BAIDU_TOKEN="你的百度普通收录token"     # baidu_enabled=true 时必填
# export INDEXNOW_KEY="..."                   # 可选(Bing/海外)
# export GIT_PUSH_TOKEN="ghp_..."             # 可选: 本地免交互 push(https remote)

# 4) 先做一次 dry-run(只生成到临时目录, 不 push、不推送收录)
python -m automation.autopublish.run --dry-run

# 5) 校验 frontmatter 是否合法(硬验证)
npm run build

# 6) 真发一篇试水
python -m automation.autopublish.run --count 1
```

Windows PowerShell 里设密钥用 `$env:ANTHROPIC_API_KEY="..."`。

---

## 运行方式

```bash
python -m automation.autopublish.run                 # 按当前时段自动算份额
python -m automation.autopublish.run --count 3       # 强制本次发 3 篇
python -m automation.autopublish.run --slot 15:00    # 指定按哪个时段算份额
python -m automation.autopublish.run --dry-run       # 只生成不发布
python -m automation.autopublish.run --config /path/config.toml
```

**份额分配**：当天目标数在 `daily_min..daily_max` 内按日期确定（同一天三段一致），均分到三段、余数打散。
当天已发数记录在 `logs/state-YYYYMMDD.json`，防止重复发。

---

## 方案① —— GitHub Actions 云端定时任务（推荐）

工作流 `.github/workflows/scheduled-publish.yml` 已就绪，**自包含**：生成 → 提交 → push → `npm run build`（重建 sitemap）→ 部署 Cloudflare Pages。

### 部署步骤
1. 仓库 **Settings → Secrets and variables → Actions** 添加：
   - `ANTHROPIC_API_KEY`（必填）
   - `ANTHROPIC_BASE_URL`（用第三方代理 key 时必填；官方 `sk-ant-` key 不需要）
   - `BAIDU_TOKEN`（启用百度收录时）
   - `INDEXNOW_KEY`（启用 IndexNow 时）
   - `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` / `CLOUDFLARE_PROJECT_NAME`（部署用，与现有 workflow 相同）
2. 确认 **Settings → Actions → General → Workflow permissions** 为 **Read and write**（工作流已声明 `contents: write`，用于 push 文章）。
3. 把 `automation/` 与工作流文件提交到 `main`。
4. **手动验证**：Actions 页选 *Scheduled Auto-Publish* → *Run workflow*，先设 `dry_run=true` 跑一次，再设 `count=1` 真发一篇。
5. 之后按三条 cron 自动运行。日志作为 Artifact 上传（`publish-logs-<run_id>`）。

> ⚠ **CI 下选题去重的限制**：Actions 每次是全新 checkout，脚本只提交生成的 `.md`，不回写 `topics.json`/`state`。
> 因此**云端模式下 `topics.json` 的 `used` 标记不会跨运行保留**。两种应对：
> （a）主要用云端时，把选题设计成“关键词种子”，靠 slug 查重避免重复文件即可（同名文件会被跳过）；
> （b）若要严格去重，改用本地方案②（状态持久），或在工作流末尾追加一步把 `topics.json` 一并 commit（需自行取舍是否让 bot 改动队列文件）。

### Cron 对照表（配置时段为北京时间 Asia/Shanghai, UTC+8）

| 本地时段 | UTC | Actions cron | 本地 crontab（服务器时区=北京时） |
|---|---|---|---|
| 09:00 | 01:00 | `0 1 * * *` | `0 9 * * *` |
| 15:00 | 07:00 | `0 7 * * *` | `0 15 * * *` |
| 20:00 | 12:00 | `0 12 * * *` | `0 20 * * *` |

> GitHub Actions 定时任务只认 UTC，且高峰期可能延迟数分钟至十几分钟，属正常。

---

## 方案② 定时配置

### Windows 任务计划（3 个触发器）
对 09:00 / 15:00 / 20:00 各建一个任务（示例为 09:00）：

```bat
schtasks /Create /TN "chinatripbox-publish-0900" /SC DAILY /ST 09:00 ^
  /TR "cmd /c cd /d D:\独立站\china-travel-kit && set ANTHROPIC_API_KEY=sk-ant-... && set BAIDU_TOKEN=... && python -m automation.autopublish.run >> automation\logs\task.log 2>&1"
```
把 `/ST` 改成 `15:00`、`20:00` 再建两个（`/TN` 换名）。
> 更安全的做法：密钥用系统环境变量（`控制面板 → 系统 → 高级 → 环境变量`）而非写进命令行，然后 `/TR` 里只保留 `cd ... && python -m ...`。

### Mac / Linux Cron
`crontab -e` 加入（服务器时区设为北京时；否则按上表换算 UTC）：
```cron
CRON_TZ=Asia/Shanghai
0 9,15,20 * * * cd /path/to/china-travel-kit && /usr/bin/python3 -m automation.autopublish.run >> automation/logs/cron.log 2>&1
```
密钥建议写在 `~/.profile` 或专用 env 文件并在命令前 `source`。

---

## 收录异常排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 百度返回 `"error":401` / `not_valid_token` | token 失效或站点未验证 | 到百度搜索资源平台重取 token，确认 `config.toml` 的 domain 与验证站点一致 |
| 返回 `"error":400 not_same_site` | 提交的 URL 域名与 token 站点不符 | 核对 `post_url_tmpl` 生成的 URL 域名 == 百度验证域名（含 www 与否要一致） |
| `remain:0` / 配额用尽 | 当日推送额度耗尽 | 次日恢复；降低每日篇数或分散推送 |
| HTTP 5xx / 网络超时 | 接口临时不可用 | 脚本已自动重试 1 次；仍失败则日志标记，手动补推或等下段 |
| IndexNow 返回 403 | key 文件未部署到站点根 | 在 `public/<INDEXNOW_KEY>.txt` 放置 key 文件并随站点部署 |
| Google 一直不收录 | Google 无 URL 提交 API | 依赖构建自动重建的 `sitemap-index.xml` + 在 Google Search Console 提交 sitemap；耐心等抓取 |
| `git push 失败` | 无凭证 / 无写权限 | 本地设 `GIT_PUSH_TOKEN` 或配置 SSH；Actions 确认 workflow 写权限已开 |
| `npm run build` 报 frontmatter 错 | 生成字段非法 | 见下方“内容质量”；重跑生成，或删除有问题的 `.md` |

> **Google 说明**：本站面向海外，主力是 Google/Bing。Google 没有“主动提交单条 URL”的公开 API，
> 正确做法是保证 sitemap 自动更新（本站构建已做到）并在 GSC 提交 sitemap；IndexNow 覆盖 Bing。
> 百度推送对英文海外站意义有限，如无中文流量可在 `config.toml` 关闭 `baidu_enabled`、改开 `indexnow_enabled`。

---

## 长期安全运营建议

- **起步保守**：先 `daily_min=3, daily_max=5` 稳定跑 2–4 周，观察 GSC 收录率/抓取情况，再逐步上调；
  长期**单日不建议超过 8 篇**，避免被判定为低质批量站。当前模板默认 8–10，请按站点实际收录反馈调整。
- **保持差异化**：generator 已内置多套骨架模板 + 角度(angle) + 变化措辞。选题 `topics.json` 也要持续补充**真实、有信息增量**的题目，不要只堆同义词。
- **节奏拟人**：三时段 + 篇间随机延时已开启，别把 `per_slot_jitter_sec` 调成 0，也别把三段并到一段瞬时上新。
- **质量抽检**：每周人工抽读 2–3 篇，检查事实准确性、是否有 AI 套话、内链/联盟占位是否自然。
- **监控指标**：GSC 的收录数、展示/点击、平均排名；跳出率与停留时长。收录停滞或跳出飙高时先降频、提质。
- **密钥卫生**：密钥只放环境变量 / Secrets，绝不进 `config.toml` 或提交历史；`config.toml` 与 `logs/` 已被 gitignore。
- **合规**：坚持原创、事实准确，不虚构价格/政策等硬信息；联盟披露按目标市场法规在站点固定位置声明。

---

## 日志格式

`logs/publish-YYYYMMDD.jsonl`，每行一条：
```json
{"title":"...","slug":"...","url":"https://chinatripbox.com/posts/...","category":"esim","publish_time":"2026-07-08T09:03:11+08:00","status":"published","attempts":1,"error":""}
```
收录推送结果另起一行（`"type":"indexing"`）。当天配额状态见 `logs/state-YYYYMMDD.json`。
