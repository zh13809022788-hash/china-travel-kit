# 工具开发路线图（4周计划）

**当前状态：7个工具已上线 | 目标：4周内新增2-3个 → 9-10个**

**已上线工具：**
1. ✅ Visa-Free Checker → /tools/visa-free-checker/
2. ✅ Best Time to Visit → /tools/best-time-to-visit/
3. ✅ Budget Cash Estimator → /tools/budget-cash-estimator/
4. ✅ Payment Checker → /tools/payment-checker/
5. ✅ eSIM Comparator → /tools/esim-comparison/
6. ✅ App Availability Checker → /tools/app-availability-checker/
7. ✅ Survival Kit → /tools/survival-kit/
8. ✅ Show to Driver → /tools/show-to-driver/
9. ✅ Currency Converter → /tools/currency-converter/
10. ✅ Essential Phrases → /tools/essential-phrases/

---

## 本周重点：工具增强（非新建）

| 工具 | 增强内容 | 工作量 |
|------|---------|--------|
| Survival Kit | 增加打印功能 | 小（2小时） |
| Essential Phrases | 合并中医短语卡+点餐短语卡 | 中（4小时） |
| eSIM Comparator | 更新2026年价格 | 小（1小时） |

## 第2-4周：新建工具

| 优先级 | 工具 | 描述 | 预估 |
|--------|------|------|------|
| 🔴 高 | **Checklist Generator** | 用户勾选"我有支付/我有eSIM"等，生成个性化PDF checklist | 大（外包或Codex） |
| 🟡 中 | **TCM Phrase Card** | 可打印的中医对话卡，包含症状描述+拼音 | 小（4小时） |
| 🟡 中 | **Food Ordering Card** | 可打印的点餐短语卡+图片点菜法 | 小（4小时） |
| 🟢 低 | **Packing Checklist** | 交互式打包清单（按季节/性别筛选） | 中（1天） |

## 爆款工具潜力评估

| 工具 | 病毒传播潜力 | 技术难度 | 建议 |
|------|-------------|---------|------|
| Checklist Generator | ⭐⭐⭐⭐⭐ | 中 | 最值得做——用户可分享结果 |
| TCM Phrase Card | ⭐⭐⭐ | 低 | 快速产出 |
| Budget Estimator（已存在） | ⭐⭐⭐⭐ | 已上线 | 增强分享功能 |

**工具开发原则：**
- 所有工具浏览器端运行（JS + localStorage），无后端依赖
- 关键功能：打印/下载/分享
- 先做低难度高传播的工具
