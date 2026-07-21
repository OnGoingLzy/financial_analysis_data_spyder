# 同行财务分析平台升级 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立来源可替换的三张标准财务报表与五区同行经营诊断界面。

**Architecture:** Python 采集适配器只输出标准字段字典，SQLite 标准表保存事实数据，Node 指标引擎统一计算派生指标，Vue 只负责筛选和可视化。旧数据库通过幂等 schema 升级兼容，缺失字段保持 NULL。

**Tech Stack:** Python 3、Selenium、SQLite、Node.js、Express、Vue 3、TypeScript、ECharts、Pytest、Vitest

## Global Constraints

- 文档和代码注释使用中文。
- 盈利/正向值为红色，亏损/负向值为绿色。
- 所有采集时间使用北京时间 `+08:00`。
- 禁止用模拟值补齐真实数据库缺失字段。
- 移动端只保证结构可用，不作为本轮优先验收项。

---

### Task 1: 标准表扩展与现金流写入

**Files:**
- Modify: `financial_schema.py`
- Modify: `sqlserver_operation.py`
- Modify: `tests/test_financial_schema.py`
- Modify: `tests/test_storage_upsert.py`

**Interfaces:**
- Produces: `upsert_cash_flow_statement(connection, raw_row, batch_id)` 与 `insert_xjllb(data)`。

- [ ] 编写旧数据库幂等升级和现金流写入失败测试。
- [ ] 运行定向 Pytest，确认缺表、缺列或函数不存在导致失败。
- [ ] 实现标准表加列、现金流标准化和批次完成状态。
- [ ] 重跑定向测试并确认通过。

### Task 2: 来源可替换的采集适配器

**Files:**
- Modify: `selenium_spyder.py`
- Create: `tests/test_statement_adapter.py`

**Interfaces:**
- Produces: `extract_statement_rows(table, field_labels, periods)`，返回标准字段字典列表。

- [ ] 使用伪表格对象编写候选标签、缺失行与多报告期测试。
- [ ] 运行测试并确认旧实现失败。
- [ ] 实现通用行提取和现金流、资产负债、利润字段映射。
- [ ] 保留 `getdata(driver, code)` 外部入口并接入三张报表写入。

### Task 3: 同行指标引擎与 API

**Files:**
- Modify: `Web/server/metrics.mjs`
- Modify: `Web/server/metrics.test.mjs`
- Modify: `Web/server/db.mjs`
- Modify: `Web/server/app.test.mjs`
- Modify: `Web/src/types/financial.ts`

**Interfaces:**
- Produces: 同行 API 每家公司返回 `metrics`、`incomeStructure`、`workingCapital`、`cashQuality` 和 `completeness`。

- [ ] 编写费用率、自由现金流、现金转换周期、杜邦和 NULL 传播测试。
- [ ] 运行 Vitest 确认指标缺失。
- [ ] 实现统一公式并扩展数据库映射和接口响应。
- [ ] 重跑服务端测试并确认通过。

### Task 4: 五区同行分析界面

**Files:**
- Create: `Web/src/components/charts/PeerHeatmapChart.vue`
- Create: `Web/src/components/charts/GrowthProfitChart.vue`
- Create: `Web/src/components/charts/IncomeStructureChart.vue`
- Create: `Web/src/components/charts/WorkingCapitalChart.vue`
- Create: `Web/src/components/charts/CashRiskChart.vue`
- Modify: `Web/src/charts/echarts.ts`
- Modify: `Web/src/charts/options.ts`
- Modify: `Web/src/charts/options.test.ts`
- Modify: `Web/src/views/CompareView.vue`

**Interfaces:**
- Consumes: 扩展后的 `CompareResponse.rows`。
- Produces: 五个支持 Tooltip、空状态和无隐藏 hover 的分析区。

- [ ] 先编写五类图表配置与空数据测试。
- [ ] 运行 Vitest 确认配置函数不存在。
- [ ] 实现图表配置和 Vue 组件。
- [ ] 重组同行分析页并保留原有筛选和指标矩阵。
- [ ] 重跑前端测试并确认通过。

### Task 5: 真实数据库升级与交付验证

**Files:**
- Modify: `migrate_financial_data.py`
- Modify: `Web/README.md`
- Modify: `.hallmark/log.json`

**Interfaces:**
- Produces: 可重复执行的 schema 升级命令和新数据采集说明。

- [ ] 对真实数据库创建备份并执行幂等 schema 升级。
- [ ] 运行全部 Python 和前端测试。
- [ ] 运行 Vue 生产构建。
- [ ] 通过真实浏览器验证五区页面、Tooltip、空状态和控制台日志。
