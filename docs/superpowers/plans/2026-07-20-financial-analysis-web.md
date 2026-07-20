# 企业财务深度分析 Web 系统实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `Web` 目录中交付 Vue 3 研究终端，并将现有 SQLite 原始文本财务数据迁移为可追溯的标准数值表。

**Architecture:** 根目录 Python 代码负责采集、标准化、正式表写入和一次性迁移；`Web` 内 Node/Express 服务以只读方式访问正式表并提供财务分析 API；Vue 3 前端实现同行对比、单家公司分析和数据质量页面。数据库迁移采用新增表和备份策略，不删除现有表。

**Tech Stack:** Python 3.12、SQLite、pytest、Node 25、npm 11、Node 内置 `node:sqlite`、Vue 3、Vite、TypeScript、Vue Router、Pinia、ECharts、Express、Zod、Vitest、Vue Test Utils、Supertest。

## Global Constraints

- 所有新增文档和代码注释使用中文。
- 禁止删除 Windows 系统文件、现有 HTML 页面、原始数据库表和历史备份表。
- 默认数据库路径必须是 `D:/workbench/python/financial_analysis_data_spyder/financial_analysis.db`。
- 前端不提供数据库上传或切换入口，不包含模拟数据回退。
- 盈利和正增长使用红色；亏损和负增长使用绿色；空值使用中性灰。
- 金额正式存储单位为人民币元，SQLite 类型为 `INTEGER`；比率以百分点存储，例如 `6.36` 表示 `6.36%`。
- 移动端视觉测试优先级最低，基础响应式必须实现，但最终由用户手工确认，不阻断本轮交付。
- 当前目录不是 Git 仓库，因此计划中的阶段提交改为记录变更清单；若执行前已初始化 Git，再按每个任务建议的提交信息提交。

---

## 文件结构

### 根目录 Python 与数据库

- Create: `financial_normalization.py`：金额、比例、日期、报告类型和证券代码标准化。
- Create: `financial_schema.py`：正式表 DDL、模式版本和数据库初始化。
- Create: `migrate_financial_data.py`：备份并迁移现有原始表。
- Create: `requirements-dev.txt`：固定 Python 测试依赖。
- Create: `tests/test_financial_normalization.py`：标准化函数测试。
- Create: `tests/test_financial_schema.py`：DDL、更新和事务测试。
- Create: `tests/test_financial_migration.py`：现有格式迁移和幂等测试。
- Modify: `sqlserver_operation.py`：同一事务写入原始表和正式表。
- Modify: `selenium_spyder.py`：修复营业成本定位并提供标准化入库所需原始值。
- Create: `financial_analysis.before_normalization_20260720.db`：迁移前只读备份。

### `Web` 项目

- Create: `Web/package.json`、`Web/package-lock.json`、`Web/index.html`。
- Create: `Web/vite.config.ts`、`Web/tsconfig.json`、`Web/tsconfig.app.json`、`Web/tsconfig.node.json`。
- Create: `Web/tokens.css`：Hallmark 设计令牌。
- Create: `Web/.hallmark/log.json`：Hallmark 项目记忆。
- Create: `Web/server/index.mjs`、`Web/server/app.mjs`：生产入口和 Express 应用。
- Create: `Web/server/db.mjs`：数据库连接、模式验证和仓储查询。
- Create: `Web/server/metrics.mjs`：单季度、TTM、比率、共同报告期和同行统计。
- Create: `Web/server/errors.mjs`：稳定错误码。
- Create: `Web/server/app.test.mjs`、`Web/server/metrics.test.mjs`。
- Create: `Web/src/main.ts`、`Web/src/App.vue`、`Web/src/env.d.ts`。
- Create: `Web/src/router/index.ts`、`Web/src/stores/analysis.ts`。
- Create: `Web/src/api/client.ts`、`Web/src/types/financial.ts`、`Web/src/utils/format.ts`。
- Create: `Web/src/styles/global.css`。
- Create: `Web/src/layouts/ResearchLayout.vue`。
- Create: `Web/src/components/AppSidebar.vue`、`DataSourceColophon.vue`、`MetricValue.vue`、`ChartPanel.vue`、`DataTable.vue`、`EmptyState.vue`、`ErrorState.vue`、`LoadingState.vue`、`FormulaNote.vue`。
- Create: `Web/src/components/charts/ScaleGrowthChart.vue`、`ProfitabilityChart.vue`、`BalanceChart.vue`、`CompanyTrendChart.vue`。
- Create: `Web/src/views/CompareView.vue`、`CompanyView.vue`、`DataQualityView.vue`。
- Create: `Web/src/**/*.test.ts`：格式、组件和视图行为测试。
- Create: `Web/README.md`：中文运行、迁移和验证说明。

---

### Task 1: 财务标准化函数

**Files:**
- Create: `financial_normalization.py`
- Create: `requirements-dev.txt`
- Create: `tests/test_financial_normalization.py`

**Interfaces:**
- Produces: `parse_amount_to_yuan(value) -> int | None`
- Produces: `parse_percentage_points(value) -> float | None`
- Produces: `normalize_report_period(value) -> str | None`
- Produces: `infer_report_type(period) -> Literal['Q1','H1','Q3','FY'] | None`
- Produces: `normalize_security_code(value) -> tuple[str, str]`

- [ ] **Step 1: 固定测试依赖并编写金额和比例失败测试**

`requirements-dev.txt`：

```text
pytest>=8.3,<9
```

```python
from financial_normalization import parse_amount_to_yuan, parse_percentage_points


def test_parse_amount_to_yuan_preserves_negative_amount():
    assert parse_amount_to_yuan("-2181万") == -21_810_000


def test_parse_amount_to_yuan_supports_yi_and_commas():
    assert parse_amount_to_yuan("752.60亿") == 75_260_000_000
    assert parse_amount_to_yuan("1,234.5万") == 12_345_000


def test_parse_amount_to_yuan_returns_none_for_missing_or_invalid():
    assert parse_amount_to_yuan("--") is None
    assert parse_amount_to_yuan("") is None
    assert parse_amount_to_yuan("无法解析") is None


def test_parse_percentage_points_keeps_percentage_points():
    assert parse_percentage_points("6.36%") == 6.36
    assert parse_percentage_points(-19.39) == -19.39
```

- [ ] **Step 2: 运行测试并确认因模块不存在而失败**

Run: `python -m pip install -r requirements-dev.txt && python -m pytest tests/test_financial_normalization.py -q`

Expected: FAIL，错误包含 `ModuleNotFoundError: No module named 'financial_normalization'`。

- [ ] **Step 3: 实现金额和比例解析**

```python
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


MISSING_MARKERS = {"", "--", "-", "N/A", "None", "null"}


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).replace(",", "").strip()
    return None if text in MISSING_MARKERS else text


def parse_amount_to_yuan(value: object) -> int | None:
    text = _clean(value)
    if text is None:
        return None
    multiplier = Decimal(1)
    if text.endswith("亿"):
        text, multiplier = text[:-1], Decimal(100_000_000)
    elif text.endswith("万"):
        text, multiplier = text[:-1], Decimal(10_000)
    try:
        amount = Decimal(text) * multiplier
    except InvalidOperation:
        return None
    return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def parse_percentage_points(value: object) -> float | None:
    text = _clean(value)
    if text is None:
        return None
    if text.endswith("%"):
        text = text[:-1]
    try:
        return float(Decimal(text))
    except InvalidOperation:
        return None
```

- [ ] **Step 4: 增加日期和证券代码失败测试**

```python
from financial_normalization import infer_report_type, normalize_report_period, normalize_security_code


def test_normalize_report_period_and_type():
    assert normalize_report_period("2026/03/31") == "2026-03-31"
    assert infer_report_type("2026-03-31") == "Q1"
    assert infer_report_type("2025-12-31") == "FY"


def test_normalize_security_code_corrects_market_prefix():
    assert normalize_security_code("SZ600998") == ("SH600998", "SH")
    assert normalize_security_code("002788") == ("SZ002788", "SZ")
```

- [ ] **Step 5: 运行测试并确认新行为失败**

Run: `python -m pytest tests/test_financial_normalization.py -q`

Expected: FAIL，错误指出三个函数尚未定义。

- [ ] **Step 6: 实现日期、报告类型和代码标准化**

```python
from datetime import datetime


def normalize_report_period(value: object) -> str | None:
    text = _clean(value)
    if text is None:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def infer_report_type(period: str | None) -> str | None:
    if not period:
        return None
    return {"03-31": "Q1", "06-30": "H1", "09-30": "Q3", "12-31": "FY"}.get(period[5:])


def normalize_security_code(value: object) -> tuple[str, str]:
    digits = "".join(character for character in str(value) if character.isdigit())[-6:]
    if len(digits) != 6:
        raise ValueError("证券代码必须包含六位数字")
    market = "SH" if digits[0] in {"5", "6", "9"} else "SZ"
    return f"{market}{digits}", market
```

- [ ] **Step 7: 运行完整测试**

Run: `python -m pytest tests/test_financial_normalization.py -q`

Expected: PASS，全部测试通过。

---

### Task 2: 正式数据库表与迁移

**Files:**
- Create: `financial_schema.py`
- Create: `migrate_financial_data.py`
- Create: `tests/test_financial_schema.py`
- Create: `tests/test_financial_migration.py`

**Interfaces:**
- Consumes: Task 1 的五个标准化函数。
- Produces: `ensure_normalized_schema(connection) -> None`
- Produces: `upsert_income_statement(connection, raw_row, batch_id) -> None`
- Produces: `upsert_balance_sheet(connection, raw_row, batch_id) -> None`
- Produces: `migrate_database(database_path, backup_path=None) -> MigrationResult`

- [ ] **Step 1: 编写 DDL 与幂等失败测试**

```python
import sqlite3

from financial_schema import ensure_normalized_schema


def test_schema_creation_is_idempotent():
    connection = sqlite3.connect(":memory:")
    ensure_normalized_schema(connection)
    ensure_normalized_schema(connection)
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"companies", "income_statements", "balance_sheets", "import_batches", "data_quality_issues"} <= tables
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m pytest tests/test_financial_schema.py -q`

Expected: FAIL，模块或函数不存在。

- [ ] **Step 3: 实现模式版本和五张正式表**

实现 `SCHEMA_VERSION = 1`，使用 `CREATE TABLE IF NOT EXISTS` 创建设计规格中的字段、外键和唯一键；在同一事务内写入 `PRAGMA user_version = 1`。金额字段必须是 `INTEGER`，比率字段必须是 `REAL`。

- [ ] **Step 4: 编写迁移幂等与负数保持测试**

```python
def test_migration_keeps_negative_values_and_is_idempotent(tmp_path):
    database_path = build_raw_fixture_database(tmp_path)
    first = migrate_database(database_path)
    second = migrate_database(database_path)
    assert first.income_rows == 2
    assert second.income_rows == 2
    with sqlite3.connect(database_path) as connection:
        value = connection.execute(
            "SELECT net_profit FROM income_statements WHERE code=? AND report_period=?",
            ("SZ000705", "2026-03-31"),
        ).fetchone()[0]
    assert value == -21_810_000
```

- [ ] **Step 5: 运行迁移测试并确认失败**

Run: `python -m pytest tests/test_financial_migration.py -q`

Expected: FAIL，迁移接口尚未实现。

- [ ] **Step 6: 实现迁移、问题记录和冲突更新**

迁移程序执行以下固定顺序：

1. 使用 `sqlite3.Connection.backup` 创建备份。
2. 创建批次记录。
3. 读取两张原始表。
4. 标准化公司、日期、金额和比率。
5. 使用 `ON CONFLICT(code, report_period) DO UPDATE` 写入正式表。
6. 无效字段写入 `data_quality_issues`。
7. 更新批次状态和统计后提交。
8. 异常时回滚正式数据事务并将异常重新抛出。

- [ ] **Step 7: 运行模式与迁移测试**

Run: `python -m pytest tests/test_financial_schema.py tests/test_financial_migration.py -q`

Expected: PASS。

- [ ] **Step 8: 备份并迁移真实数据库**

Run: `python migrate_financial_data.py --database financial_analysis.db --backup financial_analysis.before_normalization_20260720.db`

Expected: 输出包含 `companies=24`、`income_statements=168`、`balance_sheets=168`，且备份文件存在。

- [ ] **Step 9: 只读验证真实数据**

Run: `python migrate_financial_data.py --database financial_analysis.db --verify-only`

Expected: 负财务费用记录为 28 条；浙江震元 2026-03-31 净利润小于 0；正式表无重复公司报告期。

---

### Task 3: Python 双写入与采集字段修复

**Files:**
- Modify: `sqlserver_operation.py`
- Modify: `selenium_spyder.py`
- Create: `tests/test_storage_upsert.py`

**Interfaces:**
- Consumes: Task 2 的正式表初始化和 upsert 函数。
- Preserves: `insert_zcfzb(data)`、`insert_lrb(data)` 公共函数名。

- [ ] **Step 1: 编写双写入和更新失败测试**

使用临时 SQLite 文件创建原始表，调用 `insert_lrb` 两次写入同一公司报告期的不同净利润，断言原始表保持唯一记录，正式表更新为第二次值。

- [ ] **Step 2: 运行测试并确认正式表无记录**

Run: `python -m pytest tests/test_storage_upsert.py -q`

Expected: FAIL，正式表记录不存在。

- [ ] **Step 3: 重构连接和同事务双写入**

- `get_connection(database_path=None)` 优先使用显式参数，其次使用 `FINANCIAL_DB_PATH`，最后使用脚本目录下的 `financial_analysis.db`。
- `insert_lrb` 和 `insert_zcfzb` 在一个连接中初始化模式、写入原始表并 upsert 正式表。
- 关闭连接前判断游标和连接是否成功创建，避免异常路径再次抛错。
- 不再吞掉写入异常；记录日志后重新抛出，使采集调用者能感知失败。

- [ ] **Step 4: 修复营业成本定位失败测试**

在测试中读取 `selenium_spyder.getlrb` 使用的标签映射，断言 `total_operating_cost` 对应“营业总成本”，`operating_cost` 对应“营业成本”。

- [ ] **Step 5: 将利润表标签集中为中文映射并修复定位**

```python
INCOME_ROW_LABELS = {
    "total_operating_income": "营业总收入",
    "total_operating_cost": "营业总成本",
    "operating_cost": "营业成本",
}
```

`getlrb` 通过映射分别查找三行，禁止复用“营业总成本”结果。

- [ ] **Step 6: 运行 Python 全部测试**

Run: `python -m pytest tests -q`

Expected: PASS，且测试不修改真实数据库。

---

### Task 4: `Web` 工程与数据库健康 API

**Files:**
- Create: `Web/package.json`、TypeScript/Vite 配置、`Web/index.html`
- Create: `Web/server/errors.mjs`、`db.mjs`、`app.mjs`、`index.mjs`
- Create: `Web/server/app.test.mjs`

**Interfaces:**
- Produces: `createApp({ databasePath }) -> Express`
- Produces: `openDatabase(databasePath) -> Database`
- Produces: `GET /api/health`、`GET /api/meta`

- [ ] **Step 1: 创建 package 配置和失败测试**

`package.json` 脚本固定为：

```json
{
  "name": "financial-analysis-web",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "concurrently \"vite\" \"node --watch server/index.mjs\"",
    "build": "vue-tsc -b && vite build",
    "start": "node server/index.mjs",
    "test": "vitest run"
  },
  "dependencies": {
    "echarts": "^5.6.0",
    "express": "^5.1.0",
    "pinia": "^3.0.3",
    "vue": "^3.5.18",
    "vue-router": "^4.5.1",
    "zod": "^4.0.5"
  },
  "devDependencies": {
    "@types/express": "^5.0.3",
    "@types/node": "^24.0.15",
    "@types/supertest": "^6.0.3",
    "@vitejs/plugin-vue": "^6.0.1",
    "@vue/test-utils": "^2.4.6",
    "concurrently": "^9.2.0",
    "jsdom": "^26.1.0",
    "supertest": "^7.1.4",
    "typescript": "~5.8.3",
    "vite": "^7.0.6",
    "vitest": "^3.2.4",
    "vue-tsc": "^3.0.3"
  }
}
```

测试使用临时数据库，调用 `/api/health` 并期望 `status: ok`；使用不存在路径时期望 HTTP 503 和错误码 `DATABASE_NOT_FOUND`。

- [ ] **Step 2: 安装依赖并运行失败测试**

Run: `cd Web && npm install && npm test -- server/app.test.mjs`

Expected: FAIL，`server/app.mjs` 不存在。

- [ ] **Step 3: 实现数据库连接、模式验证和统一错误结构**

默认路径通过 `fileURLToPath(import.meta.url)` 向上两级定位根目录数据库，不依赖当前工作目录。使用 Node 25 内置 `node:sqlite` 的 `DatabaseSync(databasePath, { readOnly: true })` 打开数据库，避免 Windows 原生扩展编译依赖；验证 `PRAGMA user_version >= 1` 和正式表存在。

错误响应结构：

```json
{
  "error": {
    "code": "DATABASE_NOT_FOUND",
    "message": "未找到财务数据库",
    "retryable": true,
    "scope": "application"
  }
}
```

- [ ] **Step 4: 实现 health 和 meta API**

`/api/meta` 返回数据库路径、修改时间、公司数、期间范围、两张正式表记录数和数据质量问题数。

- [ ] **Step 5: 运行 API 测试**

Run: `cd Web && npm test -- server/app.test.mjs`

Expected: PASS。

---

### Task 5: 指标引擎与分析 API

**Files:**
- Create: `Web/server/metrics.mjs`
- Create: `Web/server/metrics.test.mjs`
- Modify: `Web/server/db.mjs`、`Web/server/app.mjs`

**Interfaces:**
- Produces: `deriveSingleQuarters(records, field) -> Array`
- Produces: `calculateTtm(records, field) -> number | null`
- Produces: `findLatestCommonPeriod(companyPeriods) -> string | null`
- Produces: `calculateRatios(income, balance, previousBalance) -> object`
- Produces: `/api/periods`、`/api/companies`、`/api/compare`、`/api/companies/:code`、`/api/companies/:code/analysis`、`/api/data-quality`

- [ ] **Step 1: 编写单季度、TTM 和共同报告期失败测试**

```javascript
it('从累计值推导单季度并计算 TTM', () => {
  const records = [
    { reportPeriod: '2025-03-31', reportType: 'Q1', revenue: 10 },
    { reportPeriod: '2025-06-30', reportType: 'H1', revenue: 25 },
    { reportPeriod: '2025-09-30', reportType: 'Q3', revenue: 45 },
    { reportPeriod: '2025-12-31', reportType: 'FY', revenue: 70 },
  ]
  expect(deriveSingleQuarters(records, 'revenue').map(item => item.value)).toEqual([10, 15, 20, 25])
  expect(calculateTtm(records, 'revenue')).toBe(70)
})
```

共同报告期测试必须证明某公司缺少最新期时会回退到所有公司均存在的上一个期间。

- [ ] **Step 2: 运行指标测试并确认失败**

Run: `cd Web && npm test -- server/metrics.test.mjs`

Expected: FAIL，指标函数不存在。

- [ ] **Step 3: 实现纯函数指标引擎**

- 缺失相邻期间返回 `null`。
- TTM 要求四个连续季度。
- 比率分母为 0 或空时返回 `null`。
- 平均净资产缺少期初值时 ROE 返回 `null`。
- 年化因子按 Q1=4、H1=2、Q3=4/3、FY=1。

- [ ] **Step 4: 编写分析 API 失败测试**

使用临时正式表插入三家公司，其中一家缺少最新期；请求 `/api/compare?codes=SH600998,SZ002788&mode=index`，断言使用共同期间、中位数指数为 100 且空值不转成 0。

- [ ] **Step 5: 实现仓储查询和分析路由**

所有查询使用参数绑定。Zod 校验公司代码、报告期、比较模式和选择数量；API 将数据库 snake_case 字段映射为前端 camelCase 类型。

- [ ] **Step 6: 运行服务端全部测试**

Run: `cd Web && npm test -- server`

Expected: PASS。

---

### Task 6: Hallmark 设计系统与应用壳

**Files:**
- Create: `Web/tokens.css`、`Web/.hallmark/log.json`
- Create: `Web/src/styles/global.css`
- Create: `Web/src/main.ts`、`App.vue`、router、store、API client 和公共类型
- Create: `Web/src/layouts/ResearchLayout.vue`
- Create: 侧栏、数据署名、加载、错误、空状态和指标组件
- Create: 对应组件测试

**Interfaces:**
- Produces: `metricTone(value, kind) -> 'profit' | 'loss' | 'neutral'`
- Produces: 三个路由和统一布局。
- Consumes: Task 4、5 的 API。

- [ ] **Step 1: 编写颜色语义和错误状态失败测试**

```typescript
it('使用中国市场红盈绿亏语义', () => {
  expect(metricTone(1, 'profit')).toBe('profit')
  expect(metricTone(-1, 'profit')).toBe('loss')
  expect(metricTone(null, 'profit')).toBe('neutral')
})
```

组件测试断言错误状态展示稳定错误码对应的中文说明和重试按钮。

- [ ] **Step 2: 运行前端测试并确认失败**

Run: `cd Web && npm test -- src`

Expected: FAIL，前端模块不存在。

- [ ] **Step 3: 建立 Hallmark 令牌和全局样式**

`tokens.css` 第一行必须是：

```css
/* Hallmark · macrostructure: Workbench · tone: technical-austere · anchor hue: cyan · theme: Terminal · nav: N3 · footer: Ft4 */
```

第二行加入预发自评标记。所有颜色使用 OKLCH 令牌；语义令牌包括 `--color-profit`、`--color-loss`、`--color-warning`、`--color-neutral`。全局样式实现 `overflow-x: clip`、可见焦点环、减少动效和表格数字对齐。

- [ ] **Step 4: 实现应用壳、路由和 API 状态**

- `/` 重定向到 `/compare`。
- 侧栏包含同行对比、公司分析和数据质量。
- 底部数据署名展示真实路径、更新时间、公司数和期间范围。
- 960px 以下侧栏收起；移动端只实现基础布局，不进行阻断式视觉验收。

- [ ] **Step 5: 运行公共组件测试**

Run: `cd Web && npm test -- src`

Expected: PASS。

---

### Task 7: 同行对比工作台

**Files:**
- Create: `Web/src/views/CompareView.vue`
- Create: `Web/src/components/charts/ScaleGrowthChart.vue`、`ProfitabilityChart.vue`、`BalanceChart.vue`
- Create: `Web/src/components/DataTable.vue`
- Create: `Web/src/views/CompareView.test.ts`

**Interfaces:**
- Consumes: `GET /api/compare`、公司和期间 API。
- Produces: URL 参数 `period`、`codes`、`dimension`、`mode`。

- [ ] **Step 1: 编写同行工作流失败测试**

测试以下行为：默认选择 API 返回的最新共同期间；切换指数模式会更新 URL；负增长带绿色类和负号；缺失值显示“暂无数据”；公司名称使用真实链接。

- [ ] **Step 2: 运行测试并确认视图不存在**

Run: `cd Web && npm test -- src/views/CompareView.test.ts`

Expected: FAIL。

- [ ] **Step 3: 实现筛选、结论、图表和矩阵**

- 公司搜索和多选支持键盘。
- 结论只使用 API 返回的统计结果。
- ECharts 图表提供 `aria` 描述和等价数据表。
- 绝对值、指数、分位三种模式共用同一选中公司集合。
- 表头可排序且保持当前排序方向提示。

- [ ] **Step 4: 运行同行工作台测试**

Run: `cd Web && npm test -- src/views/CompareView.test.ts`

Expected: PASS。

---

### Task 8: 单家公司分析与数据质量

**Files:**
- Create: `Web/src/views/CompanyView.vue`、`DataQualityView.vue`
- Create: `Web/src/components/charts/CompanyTrendChart.vue`
- Create: `Web/src/components/FormulaNote.vue`
- Create: 两个视图测试文件

**Interfaces:**
- Consumes: 公司分析和数据质量 API。
- Produces: URL 参数 `period`、`basis`、`section`。

- [ ] **Step 1: 编写公司分析失败测试**

测试累计、单季度、TTM、年度切换；负净利润绿色；负财务费用显示“财务净收益”；缺少现金流时显示明确说明；ROE 估算带公式标签。

- [ ] **Step 2: 运行测试并确认失败**

Run: `cd Web && npm test -- src/views/CompanyView.test.ts`

Expected: FAIL。

- [ ] **Step 3: 实现单家公司分析**

摘要、盈利、成长、费用、资产负债五组内容共享同一报告期和口径状态。图表标签显示单位；财务费用图允许正负方向；每组包含可展开公式说明和数据表。

- [ ] **Step 4: 编写并实现数据质量测试**

断言路径、模式版本、记录数、批次状态和质量问题均来自 API；无问题时显示“当前未发现标准化异常”，不能显示虚构分数。

- [ ] **Step 5: 运行两个视图测试**

Run: `cd Web && npm test -- src/views/CompanyView.test.ts src/views/DataQualityView.test.ts`

Expected: PASS。

---

### Task 9: 集成验证、Hallmark 审查与运行文档

**Files:**
- Create: `Web/README.md`
- Modify: 仅修复验证中发现的对应文件

**Interfaces:**
- Consumes: 全部前置任务。
- Produces: 可启动、可测试、可构建的本地系统。

- [ ] **Step 1: 运行 Python 全量测试**

Run: `python -m pytest tests -q`

Expected: PASS，真实数据库内容未被测试清理。

- [ ] **Step 2: 运行 Web 全量测试**

Run: `cd Web && npm test`

Expected: PASS，0 个失败。

- [ ] **Step 3: 运行生产构建**

Run: `cd Web && npm run build`

Expected: 退出码 0，生成 `Web/dist`。

- [ ] **Step 4: 启动生产服务并检查健康接口**

Run: `cd Web && npm start`

Expected: 服务打印本地 URL；`/api/health` 返回 `status: ok`；首页自动显示真实数据库元数据。

- [ ] **Step 5: 桌面端浏览器验证**

验证同行对比、公司详情、数据质量、错误状态、键盘焦点和页面级横向溢出。移动端仅确认基础断点代码存在，最终视觉由用户手工确认。

- [ ] **Step 6: 执行 Hallmark 58 项 slop test**

在实现完成后读取 `C:/Users/yygs/.codex/skills/hallmark/references/slop-test.md` 和 `contract.md`。任何失败项必须修复后重新检查；更新 CSS 顶部六项自评分，六个维度不得低于 3。

- [ ] **Step 7: 编写中文 README**

README 包含环境要求、数据库备份和迁移、安装、开发、测试、构建、启动、环境变量、错误处理和用户移动端确认步骤。

- [ ] **Step 8: 最终变更核对**

确认未删除现有 HTML、原始表、历史表和 Windows 系统文件；列出新增与修改文件。若目录仍无 Git，仅报告无法提交；若已有 Git，建议提交信息：`feat: 新增企业财务深度分析 Vue 工作台`。

---

## 计划自检结果

- 规格覆盖：数据库标准化、迁移、双写入、固定路径、同行比较、公司分析、数据质量、红盈绿亏、错误恢复、无障碍和基础响应式均有对应任务。
- 占位符检查：计划不包含待定接口或未定义函数。
- 类型一致性：Python 正式金额为 `int | None`；API 使用 `number | null`；Vue 类型保持 `null`，不将空值转换为 0。
- 范围控制：不新增现金流采集、登录、权限、部署或行业分类数据。
