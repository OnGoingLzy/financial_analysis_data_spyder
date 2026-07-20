# 公司查询入口与图表悬停修复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立公司查询到详情分析的明确路径，并让所有财务图表悬停稳定显示对应数值。

**Architecture:** 将 ECharts 配置提取为可测试的纯函数，图表组件仅负责传入数据；新增独立公司查询视图，复用全局公司目录与既有详情 API。侧栏和路由只负责导航，不再隐式选择第一家公司。

**Tech Stack:** Vue 3、Vue Router、Pinia、TypeScript、ECharts 6、Vitest、Python、SQLite

## Global Constraints

- 界面和代码注释使用中文。
- 视觉保持专业克制的研究终端风。
- 盈利/正值为红色，亏损/负值为绿色。
- 移动端只保证结构可用，不作为本轮优先验收项。

---

### Task 1: 可测试的图表交互配置

**Files:**
- Create: `Web/src/charts/options.ts`
- Create: `Web/src/charts/options.test.ts`
- Modify: `Web/src/components/charts/ScaleGrowthChart.vue`
- Modify: `Web/src/components/charts/CompanyTrendChart.vue`

**Interfaces:**
- Produces: `createBarOption(rows, metricName, colors)` 与 `createTrendOption(records, colors)`。

- [ ] 编写失败测试，断言柱状图存在 Tooltip formatter，且所有系列的 `emphasis.disabled` 与 `blur` 可见性配置不会隐藏图形。
- [ ] 运行 `npm test -- --run src/charts/options.test.ts`，确认测试因配置函数不存在而失败。
- [ ] 实现配置函数，金额使用中文分组格式并显示人民币元，空值显示“暂无数据”。
- [ ] 修改两个图表组件使用配置函数。
- [ ] 重跑定向测试并确认通过。

### Task 2: 公司查询主页

**Files:**
- Create: `Web/src/views/CompanyDirectoryView.vue`
- Create: `Web/src/views/CompanyDirectoryView.test.ts`
- Modify: `Web/src/router/index.ts`
- Modify: `Web/src/components/AppSidebar.vue`

**Interfaces:**
- Consumes: `useAnalysisStore().companies: Company[]`。
- Produces: `/companies` 路由与 `/company/:code` 详情链接。

- [ ] 编写失败组件测试，断言关键词搜索、市场筛选与公司详情链接。
- [ ] 运行定向 Vitest，确认新视图尚不存在时失败。
- [ ] 实现查询工具栏、结果统计、公司表格及空状态。
- [ ] 将侧栏入口固定为 `/companies`，保留详情页直接访问能力。
- [ ] 重跑定向测试并确认通过。

### Task 3: 时间命名收尾与全量回归

**Files:**
- Modify: `financial_schema.py`
- Modify: `sqlserver_operation.py`
- Modify: `migrate_financial_data.py`
- Modify: `tests/test_financial_schema.py`

**Interfaces:**
- Produces: `beijing_now() -> str`，统一生成带 `+08:00` 的 ISO 时间。

- [ ] 将误导性的 `utc_now` 重命名为 `beijing_now` 并更新引用。
- [ ] 运行 `python -m pytest tests -q`，确认 Python 测试全部通过。
- [ ] 运行 `npm test` 与 `npm run build`，确认前端测试和生产构建通过。
- [ ] 查询真实数据库，确认 running 批次为 0，标准表时间均为 `+08:00`。
