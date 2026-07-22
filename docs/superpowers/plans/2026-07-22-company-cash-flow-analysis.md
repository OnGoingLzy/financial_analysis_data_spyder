# 公司现金流分析实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 使用标准现金流量表数据补全公司分析页的现金流质量指标、趋势图和报告期明细。

**Architecture:** 后端公司分析接口继续按报告期合并利润、资产负债和现金流记录，前端口径转换扩展到嵌套现金流字段并重新计算派生比率。新增独立现金流图表组件，公司页根据转换后记录的实际数据展示分析模块或空状态。

**Tech Stack:** Vue 3、TypeScript、ECharts 6、Express、SQLite、Vitest、Vue Test Utils

## Global Constraints

- 所有展示数据来自 `financial_analysis.db` 的标准表，不填充模拟值。
- 亏损或现金净流出为绿色，盈利或现金净流入为红色。
- 移动端测试优先级最低，本次只保证现有响应式布局不退化。
- 代码注释与文档使用中文。

---

### Task 1: 公司分析接口现金流契约

**Files:**
- Modify: `Web/server/app.test.mjs`
- Modify: `Web/src/types/financial.ts`

**Interfaces:**
- Produces: `AnalysisRecord.cashFlow`，字段为 `netOperatingCashFlow`、`netInvestingCashFlow`、`netFinancingCashFlow`、`cashReceivedFromSales`、`capitalExpenditure`、`endingCashAndEquivalents`。

- [ ] **Step 1: 写失败的接口测试**

在公司分析接口断言同报告期现金流和 `cashProfitRatio`、`cashRevenueRatio`、`freeCashFlow` 均返回真实值。

- [ ] **Step 2: 运行测试确认失败**

Run: `npm test -- server/app.test.mjs`
Expected: FAIL，因为当前测试尚未覆盖公司分析现金流契约或类型尚未声明。

- [ ] **Step 3: 补齐前端数据类型**

新增 `CashFlowRecord` 接口，并在 `AnalysisRecord` 中声明 `cashFlow: CashFlowRecord | null`。

- [ ] **Step 4: 运行测试确认通过**

Run: `npm test -- server/app.test.mjs`
Expected: PASS。

### Task 2: 分析口径转换现金流

**Files:**
- Modify: `Web/src/views/viewSemantics.test.ts`
- Modify: `Web/src/views/viewModel.ts`

**Interfaces:**
- Consumes: `AnalysisRecord.cashFlow`
- Produces: `deriveBasisRecords()` 对现金流流量字段执行累计、季度、TTM、年度转换，并重新计算现金含量、现金收入比、自由现金流。

- [ ] **Step 1: 写失败的口径测试**

构造四期累计现金流，断言单季度经营现金流为差额、TTM 为四季度之和、期末现金保持时点值。

- [ ] **Step 2: 运行测试确认失败**

Run: `npm test -- src/views/viewSemantics.test.ts`
Expected: FAIL，当前函数只处理利润表顶层字段。

- [ ] **Step 3: 实现嵌套现金流转换**

对五个现金流流量字段做差分/滚动求和，对 `endingCashAndEquivalents` 保持期末值，并依据转换后的利润和收入重算三个现金流比率。

- [ ] **Step 4: 运行测试确认通过**

Run: `npm test -- src/views/viewSemantics.test.ts`
Expected: PASS。

### Task 3: 现金流趋势图

**Files:**
- Modify: `Web/src/charts/options.test.ts`
- Modify: `Web/src/charts/options.ts`
- Create: `Web/src/components/charts/CompanyCashFlowChart.vue`

**Interfaces:**
- Produces: `createCashFlowTrendOption(records, colors)` 和 `CompanyCashFlowChart`。

- [ ] **Step 1: 写失败的图表测试**

断言经营、投资、筹资三条柱状序列存在，数值进入 tooltip，且 emphasis 不会隐藏图形。

- [ ] **Step 2: 运行测试确认失败**

Run: `npm test -- src/charts/options.test.ts`
Expected: FAIL，因为图表工厂尚不存在。

- [ ] **Step 3: 实现图表工厂和组件**

创建按报告期分组的三序列柱状图，经营现金流按正红负绿着色，投资和筹资使用强调色与中性色，复用稳定 hover 配置。

- [ ] **Step 4: 运行测试确认通过**

Run: `npm test -- src/charts/options.test.ts`
Expected: PASS。

### Task 4: 公司页现金流模块

**Files:**
- Create: `Web/src/views/CompanyView.test.ts`
- Modify: `Web/src/views/CompanyView.vue`

**Interfaces:**
- Consumes: 口径转换后的 `AnalysisRecord[]` 和 `CompanyCashFlowChart`。

- [ ] **Step 1: 写失败的页面测试**

分别挂载有现金流与无现金流的公司页数据，断言前者显示“现金流质量”和明细、后者显示“现金流量分析暂不可用”。

- [ ] **Step 2: 运行测试确认失败**

Run: `npm test -- src/views/CompanyView.test.ts`
Expected: FAIL，因为页面当前无条件显示不可用提示。

- [ ] **Step 3: 实现指标卡、图表和明细表**

以转换后记录的最新现金流期展示四项指标；明细表逐期展示七个标准字段；无有效现金流时保留空状态。

- [ ] **Step 4: 运行测试确认通过**

Run: `npm test -- src/views/CompanyView.test.ts`
Expected: PASS。

### Task 5: 完整验证

**Files:**
- Verify: `Web/`

- [ ] **Step 1: 运行完整测试**

Run: `npm test`
Expected: 全部测试通过，0 failures。

- [ ] **Step 2: 运行生产构建**

Run: `npm run build`
Expected: TypeScript 检查与 Vite 构建退出码 0。

- [ ] **Step 3: 浏览器验证真实数据库**

启动 Web 服务，打开现金流数据完整的公司分析页，切换累计、单季度、TTM、年度，确认模块、tooltip、明细和空字段表现正常，控制台无错误。
