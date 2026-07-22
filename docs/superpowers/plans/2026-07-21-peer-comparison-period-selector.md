# 同行对比报告期切换实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在同行对比页面中展示所选公司的共同报告期，并支持切换后统一刷新全部指标和图表。

**Architecture:** 服务端复用既有公司报告期查询，在 `getComparison` 内计算倒序共同期间并随响应返回。前端以响应中的 `availablePeriods` 驱动原生选择器，以 `commonPeriod` 作为唯一已确认状态，并同步 URL。

**Tech Stack:** Node.js、Express、SQLite、Vue 3、TypeScript、Vitest、Vue Test Utils。

## Global Constraints

- 只允许选择当前所选公司全部具备数据的共同报告期。
- 不减少样本，不混用期间，不插值或模拟缺失数据。
- 无效旧期间自动回退到最新共同报告期。
- 代码注释和界面文案使用中文。
- 当前工作区包含其他未提交改动，本计划不创建 Git 提交。

---

### Task 1: 服务端共同报告期响应

**Files:**
- Modify: `Web/server/metrics.mjs`
- Modify: `Web/server/metrics.test.mjs`
- Modify: `Web/server/db.mjs`
- Modify: `Web/server/app.test.mjs`

**Interfaces:**
- Produces: `findCommonPeriods(periodsByCompany: string[][]): string[]`
- Produces: `CompareResponse.availablePeriods: string[]`

- [ ] **Step 1: 为共同期间交集、倒序和空输入编写失败测试**
- [ ] **Step 2: 运行 `npm test -- server/metrics.test.mjs`，确认因 `findCommonPeriods` 缺失而失败**
- [ ] **Step 3: 实现 `findCommonPeriods`，并让 `findLatestCommonPeriod` 复用其第一项**
- [ ] **Step 4: 为接口的 `availablePeriods`、有效期间和无效期间回退编写失败测试**
- [ ] **Step 5: 运行 `npm test -- server/app.test.mjs`，确认响应缺少共同期间列表**
- [ ] **Step 6: 修改 `getComparison` 返回共同期间列表，并在指定期间不属于交集时回退最新期间**
- [ ] **Step 7: 运行服务端定向测试，确认全部通过**

### Task 2: 前端报告期选择器

**Files:**
- Modify: `Web/src/types/financial.ts`
- Modify: `Web/src/views/CompareView.vue`
- Modify: `Web/src/views/CompanyDirectoryView.test.ts` 或新增 `Web/src/views/CompareView.test.ts`

**Interfaces:**
- Consumes: `CompareResponse.availablePeriods`、`CompareResponse.commonPeriod`
- Produces: URL 查询参数 `period=YYYY-MM-DD`

- [ ] **Step 1: 编写失败组件测试，断言共同报告期选项、选中值和切换请求参数**
- [ ] **Step 2: 运行该组件测试，确认页面缺少“报告期”选择器**
- [ ] **Step 3: 扩展 `CompareResponse` 类型并在筛选工具栏加入带标签的原生 `select`**
- [ ] **Step 4: 实现报告期格式化、切换立即加载、加载禁用以及响应回退后的 URL 同步**
- [ ] **Step 5: 运行组件定向测试，确认全部通过**

### Task 3: 回归与浏览器验收

**Files:**
- Modify: `Web/README.md`

**Interfaces:**
- Consumes: 完成后的 `/api/compare` 与同行对比页面

- [ ] **Step 1: 在 README 同行分析口径中补充共同报告期选择规则**
- [ ] **Step 2: 运行 `npm test`，确认所有 Web 测试通过**
- [ ] **Step 3: 运行 `npm run build`，确认 TypeScript 和生产构建通过**
- [ ] **Step 4: 使用真实数据库启动临时服务，在浏览器切换两个共同报告期**
- [ ] **Step 5: 核对状态行、URL、图表与指标矩阵期间一致，且控制台无错误**
- [ ] **Step 6: 运行 `git diff --check`，确认无补丁格式错误**
