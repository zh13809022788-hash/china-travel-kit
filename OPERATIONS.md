# ChinaTripBox 运营宪法 v2.0

> 最后更新：2026-07-21
> 治理人：WorkBuddy（首席运营官）
> 定位依据：国家移民管理局 2026上半年数据（年入境外国人3900-4000万人次）

---

## 一、战略定位

**ChinaTripBox = 来华外国人入境服务的入口级平台。**

不是旅行博客，不是内容站——是每年4000万人次来华外国人必须依赖的数字基础设施。

### 1.1 目标市场

2025.7-2026.6 中国入境外国人约 **3908万人次**，且以每年20%增速持续增长。前十大客源国占总入境量的62%。

**客源国梯队（按入境人次）：**
- **第一梯队（400万+）**：韩国（700-780万）、俄罗斯（520-600万）
- **第二梯队（250-400万）**：马来西亚、越南、泰国、新加坡
- **第三梯队（120-240万）**：美国、日本、蒙古国、澳大利亚

### 1.2 北极星指标

成为每年来华4000万外国人解决入境问题的**首选第一站**。

- 用户路径：签证/免签了解 → eSIM购买 → 支付设置 → 交通规划 → 城市游玩 → 离境
- 全链路覆盖，每个节点都有对应的内容 + 工具 + 推荐

### 1.3 商业模式

联盟佣金（eSIM/保险/酒店）> 展示广告（AdSense）> 付费服务（Trip Review/Trip Planner）

联盟不是"变现手段"，而是服务的自然延伸——用户信任我们推荐的eSIM和保险，因为我们真正解决了他入境后的第一个问题。

### 1.4 内容形态

交互工具（核心产品）> 客源国全流程指南 > 城市攻略

内容按**客源国**组织，而非按话题组织：
- 韩国人来中国 → 韩语版全流程（签证/免签 → eSIM → 支付宝 → 交通 → 城市指南）
- 俄罗斯人来中国 → 俄语版全流程
- 马来/越南/泰国人 → 各语言全流程

### 1.5 语言策略（数据驱动）

基于客源国入境人次制定的优先级，每加一种语言即打开数百万人的入口：

| 优先级 | 语言 | 覆盖市场 | 年入境人次 | 策略 |
|--------|------|---------|-----------|------|
| 🔴 P0 | ko | 韩国 | 700-780万 | 全面内容深耕 |
| 🔴 P0 | ru | 俄罗斯 | 520-600万 | 内容质量提升 |
| 🔴 P0 | en | 美国/澳洲/新加坡 | ~600万 | 基础盘，持续扩展 |
| 🟡 P1 | th/ms/vi | 泰国/马来/越南 | 各300万+ | 全量推进（另一台电脑部署中） |
| 🟡 P1 | ja/zh-tw | 日本/台湾/香港 | 各200万+ | 维持更新 |
| 🟢 P2 | fr/de/es | 法/德/西 | 不在前十 | 现有内容维持，不主动扩展 |

---

## 二、指挥链与角色分工（不可变）

### 2.1 指挥链路

```
用户（唯一指令源）
  │
  ▼
WorkBuddy ─── 高级助理 · 首席运营官
  │             ├─ 唯一指令接收人，只对用户负责
  │             ├─ 理解用户意图，制定总体规划与策略
  │             ├─ 将战略指令拆解为可执行任务
  │             ├─ 分配任务给 Codex / Hermes
  │             └─ 审核所有产出，把门
  │
  ├──▶ Codex ── 主执行引擎（最高质量交付）
  │       ├─ 负责：内容生产、多语言翻译、代码开发、编译部署
  │       ├─ 负责：质量修复、SEO优化、技术架构
  │       ├─ 产出质量最高，优先调度
  │       └─ 必须：build 通过，质量门禁全过
  │
  ├──▶ Hermes ── 结构化数据工厂
  │       ├─ 负责：批量数据生产、自动化流水线、JSON结构化输出
  │       ├─ 负责：重复性内容生产（需 Codex 审核质量）
  │       └─ 必须：通过 schema 校验 + WorkBuddy 质量抽查
  │
  └──▶ Claude Code ── 备用引擎
          ├─ 当 Codex sandbox 不可用时顶上
          └─ 处理特殊技术任务
```

### 2.2 角色铁律（不可违反）

**WorkBuddy 不干具体活。**
- WorkBuddy 是战略层、策略层、审核层，不是执行层
- 不写文章、不做翻译、不写代码、不跑脚本
- 只做：理解用户意图、制定策略、拆解任务、分配调度、审核把关
- Codex 和 Hermes 的产出必须经 WorkBuddy 审核后方可进入代码库

**Codex 是主执行引擎。**
- 所有需要高质量交付的工作优先调度 Codex
- 内容生产（文章写作、翻译、扩写）→ Codex
- 代码修改、架构调整、构建部署 → Codex
- 质量修复、SEO优化 → Codex
- 未经 WorkBuddy 审核的 Codex 产出不得 push

**Hermes 是结构化数据工厂。**
- 批量数据生产（JSON、CSV、结构化内容）→ Hermes
- 自动化流水线（GitHub Actions、定时任务）→ Hermes
- 重复性内容生产（需先经 WorkBuddy 审批 + Codex 质量抽检）
- 不适合：高质量内容创作、代码架构决策、翻译
- 用户不与 Hermes 或 Codex 直接对话 — 一切通过 WorkBuddy
- 未通过质量门禁的内容 → 拒绝进入分支
- build 报 warning → 修复后再合并
- 所有产出必须经 WorkBuddy 确认后才 push

---

## 三、质量门禁（不可跳过）

### 3.1 内容质量（check-content-quality.mjs）

| 维度 | 标准 | 触发条件 |
|------|------|----------|
| 正文长度 | ≥ 900 词（英文）/ 等效字数（其他语言） | `thin body` 告警 |
| 内链 | ≥ 3 个指向站内其他页面的链接 | `add internal links` 告警 |
| FAQ | ≥ 3 条 FAQ 条目 | `add at least 3 FAQ` 告警 |
| Description | 90-180 字符 | `description should be` 告警 |
| 标题 | ≤ 75 字符 | `title is long` 告警 |
| 章节标题 | ≥ 4 个二级标题 (##) | `add more section headings` 告警 |
| 占位文本 | 不含 TODO/TBD/lorem ipsum/placeholder | `placeholder` 告警 |

### 3.2 技术质量

| 维度 | 标准 | 检查方式 |
|------|------|----------|
| hreflang | 每个语言版本都有对应的 alternate link | BaseLayout hreflangCodes 覆盖所有11语言 |
| Canonical | 每个页面有正确的 canonical URL | BaseLayout 自动生成 |
| Build | 零报错、零重复 content-id | `npm run build` |
| 结构化数据 | FAQ/Organization/WebSite schema | BaseLayout json-ld |
| 外链 | 每篇文章 ≤ 8 个外链 | check-content-quality.mjs |

### 3.3 本地化标准（非翻译）

| 语言 | 要求 |
|------|------|
| 所有非英文 | 内容针对该语言用户群具体需求定制，非机器翻译 |
| th/ms/vi | 各国家签证政策、出发地信息、当地常用APP |
| zh-tw | 台湾游客来中国的具体问题（支付、证件、交通） |
| ja/ko | 日本/韩国游客高频搜索词和关注点 |

---

## 四、技术架构规范

### 4.1 URL 结构

```
英文：/posts/slug/
中文繁体：/zh-tw/posts/slug/
德/日/韩/法/西/俄/泰/马/越：/{lang}/posts/slug/
工具页：/tools/{tool-name}/
分类页：/{category}/
城市指南：/cities/{city-name}/
```

### 4.2 新增语言流程

1. `src/i18n/categories.ts` — 添加 LocaleCode 类型和分类翻译
2. `src/layouts/BaseLayout.astro` — 添加到 hreflangCodes / localePrefixes / htmlLangMap / 语言检测脚本
3. `src/content/config.ts` — 添加新的 collection 定义和 export
4. 创建 `src/content/posts-{lang}/` 目录
5. 英文文章翻译/本地化后放入对应目录
6. 部署后验证 hreflang 标签和语言切换

### 4.3 代理协作规范

- 日常维护与质量修复 → WorkBuddy 执行
- 大规模内容批量处理 → Codex 分批执行（每批 ≤ 10 篇）
- 本地化内容生产 → Hermes 执行
- 技术架构调整 → WorkBuddy 审核后 Codex 执行

---

## 五、变现策略

### 5.1 联盟变现（即时启动）

| 品类 | 优先级 | 配置位置 |
|------|--------|----------|
| eSIM | P0 | `src/config.ts` → `AFFILIATE_LINKS.esim` |
| 支付/金融 | P1 | `src/config.ts` → `AFFILIATE_LINKS.payment` |
| 交通/酒店 | P2 | `src/config.ts` → `AFFILIATE_LINKS.transport` |

### 5.2 展示广告

等待 AdSense 审核通过后激活，填入 `ADSENSE_SLOTS` 中的广告位 slot ID。

### 5.3 付费服务

流量达到日均 500+ UV 后启动 Trip Review 和高级 Trip Planner。

---

## 六、发布规范

- **英文内容**：按 30天增长计划（docs/GROWTH_PLAN_30_DAYS.md）推进
- **多语言内容**：英文版发布确认质量后，分批本地化至其他语言
- **质量门禁**：所有内容在合并前必须过 `npm run check:content`
- **Build 检查**：部署前必须 `npm run build` 无报错
- **索引监控**：每周检查 Google Search Console 索引覆盖率

---

## 七、宪法分发与更新机制

### 7.1 权威位置

本文件存放在项目 Git 仓库根目录（`OPERATIONS.md`），是**唯一权威版本**。所有 agent（WorkBuddy / Codex / Hermes / Claude Code）和所有任务运行时以 GitHub 仓库中的版本为准。

### 7.2 更新流程

任何对本宪法的修改必须：

1. 由 WorkBuddy（首席运营官）审核并执行修改
2. 修改后 commit 并 push 到 GitHub `main` 分支
3. 各 agent 在每次任务启动时读取 `OPERATIONS.md` 获取最新规则
4. 重大变更需在 commit message 中标注 `[OPS]` 前缀

### 7.3 多设备同步

当多台设备上的 WorkBuddy/Codex 并行工作时：
- 每次开始任务前执行 `git pull` 获取最新宪法
- 如本地修改与远程冲突，以远程版本为准（先 pull 再操作）
- 各设备的批量产出（内容文件、脚本）通过 Git 合并

### 7.4 版本追溯

- `git log -- OPERATIONS.md` 查看所有变更历史
- 每次重大决策变更需在文件中更新"最后更新"日期
- 不删除历史条款，使用 `~~删除线~~` 标记废弃内容

---

## 八、多设备协作协议

### 8.1 语言配置中心（单一事实来源）

语言配置统一在 `src/i18n/locales.ts` 管理，**所有 agent 和设备不得在其他文件中硬编码语言列表**。

- 新增语言：只改 `locales.ts` 一个文件
- `ALL_LOCALES`、`HTML_LANG_MAP`、`LOCALE_PREFIXES`、`NOINDEX_LOCALES`、`SITEMAP_EXCLUDED_PREFIXES` — 五个导出覆盖全部语言相关逻辑
- BaseLayout.astro / categories.ts / astro.config.mjs 均通过 import 引用

### 8.2 并行工作时的冲突避免

当两台设备同时操作仓库时：

1. **开始任务前** → `git pull` 获取远程最新代码
2. **有冲突的文件** → 查看冲突内容，如修改目的一致则接受更完整的版本
3. **新增内容（新文章、新脚本）→ 不会冲突，直接合并**
4. **修改架构文件（BaseLayout, config, locales）→ 只能一边做**，先在 shared-messages.md 通知另一方暂停相关操作
5. **大规模批量修改（如质量修复脚本）→ 执行前确认没有人在改同批文件**

### 8.3 共享消息通道

两台设备通过 `shared-messages.md` 文件（项目根目录或共享位置）通信：

- **启动大任务前** → 在 shared-messages.md 宣告 "正在处理 X"
- **完成任务后** → 写总结 + commit hash
- **发现架构问题** → 写到这里通知另一方，附解决方案
- **需要决策的问题** → 写到这里等老板或对方回复

### 8.4 Git 工作流

- commit 粒度：一个逻辑任务 = 一个 commit，不攒批
- commit message 格式：`[OPS]` 宪法变更 / `[FIX]` 修复 / `[FEAT]` 新功能 / `[CONTENT]` 内容
- push 前先 pull，冲突当场解决
- 不 force push，不 amend 已推送的 commit
- 重大 merge 冲突由 WorkBuddy（首席运营官）裁定

### 8.5 当前设备分工（2026-07-20）

| 设备 | 职责 | 状态 |
|------|------|------|
| **电脑（这台）** | 质量门禁、30天增长计划文章、技术架构、GSC分析 | 活跃 |
| **另一台电脑** | 站点故障修复、Layout全站统一、多语言骨架、GDPR页 | 活跃 |
| **手机 WorkBuddy** | 协调、决策确认、小任务 | 待命 |

### 8.6 已知技术债

以下问题记录在此，供后续修复：

- `ja/about.astro` import 路径问题（每次构建时可能被覆盖）— 修复：改为 `../../layouts/BaseLayout.astro`
- `_headers` 规则：绝对不要加 `Content-Type`
- `lorem` 和 `tryst` 残留文件：确认无引用后删除
