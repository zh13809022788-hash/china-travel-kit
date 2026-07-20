# ChinaTripBox 运营宪法 v1.0

> 最后更新：2026-07-20
> 治理人：WorkBuddy（首席运营官）

---

## 一、核心使命

为赴华外国旅行者提供实用、准确、最新的旅行信息，构建中国旅行垂直领域最具权威的独立内容站。

- **流量来源**：Google 自然搜索（70%）+ 社交媒体/外链（30%）
- **变现路径**：联盟佣金 > 展示广告 > 付费服务
- **内容形态**：实用指南 + 交互工具 + 城市攻略
- **语言策略**：11语言全覆盖（en, zh-tw, ja, ko, ru, fr, de, es, th, ms, vi）

---

## 二、指挥链（不可变）

```
用户（唯一指令源）
  │
  ▼
WorkBuddy ─── 首席运营官
  │             ├─ 唯一指令接收人
  │             ├─ 翻译战略指令为可执行任务
  │             ├─ 分配 Hermes / Codex / Claude
  │             └─ 审核所有产出
  │
  ├──▶ Hermes（内容工厂）
  │       ├─ 产出：src/content/posts-*/**.md
  │       ├─ 必须：通过 check-content-quality.mjs 校验
  │       └─ 必须：每篇 3+ 内链、3+ FAQ、description 90-180 字符
  │
  ├──▶ Codex（页面工厂）
  │       ├─ 处理：代码修改、内容扩编、编译部署
  │       ├─ 必须：build 通过，无重复 content-id
  │       └─ 必须：hreflang 完整配对
  │
  └──▶ Claude Code（备用引擎）
          ├─ 当 Codex sandbox 不可用时顶上
          └─ 处理特殊技术任务
```

**硬性规则：**
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
