# 企业财务深度分析 Web

面向公司内部财务分析人员的 Vue 3 研究工作台，支持同行横向对比、单家公司深度分析和数据质量追溯。界面默认读取项目根目录的真实 SQLite 数据库，不提供文件上传入口，也不使用模拟数据回退。

## 环境要求

- Python 3.12
- Node.js 22.5 或更高版本；当前开发环境为 Node.js 25
- npm 11

项目使用 Node 自带的 `node:sqlite` 只读访问数据库，因此无需安装 SQLite 原生扩展编译工具。Node 可能输出 SQLite 实验性 API 提示，不影响当前运行。

## 默认数据库

默认路径：

```text
D:\workbench\python\financial_analysis_data_spyder\financial_analysis.db
```

服务端通过脚本绝对位置定位数据库，不依赖启动时的工作目录。若确需在其他机器验证副本，可临时设置 `FINANCIAL_DB_PATH`；正常使用无需设置。

```powershell
$env:FINANCIAL_DB_PATH = 'D:\data\financial_analysis.db'
```

数据库不存在、不可读或未完成标准化迁移时，接口会返回稳定错误码，界面停止展示业务数据，不会切换到模拟数据。

## 首次迁移

在项目根目录执行：

```powershell
python -m pip install -r requirements-dev.txt
python migrate_financial_data.py --database financial_analysis.db --backup financial_analysis.before_normalization_20260720.db
python migrate_financial_data.py --database financial_analysis.db --verify-only
```

迁移只新增 `companies`、`income_statements`、`balance_sheets`、`import_batches` 和 `data_quality_issues`，不会删除原始表。迁移程序可重复运行，同一公司同一报告期使用冲突更新，不产生重复正式记录。

若数据库来自旧版本，需要修复 UTC 时间或遗留的 `running` 批次，可先备份并执行：

```powershell
python migrate_financial_data.py --database financial_analysis.db --backup financial_analysis.before_metadata_repair.db --repair-metadata
```

修复程序会把标准表时间转换为 `Asia/Shanghai` 的 `+08:00` ISO 时间，并根据原始表和正式表核对遗留 Selenium 批次后写入完成状态与行数。

## 安装与开发

```powershell
cd Web
npm install
npm run dev
```

- Vue 开发服务器默认为 `http://127.0.0.1:5173`
- 本地只读 API 默认为 `http://127.0.0.1:5174`
- Vite 自动将 `/api` 转发到本地 API

## 测试与构建

```powershell
# 项目根目录：Python 标准化、迁移和双写入测试
python -m pytest tests -q

# Web 目录：Node API 与 Vue 组件测试
npm test

# Web 目录：TypeScript 检查与生产构建
npm run build
```

## 生产方式启动

```powershell
cd Web
npm run build
npm start
```

打开 `http://127.0.0.1:5174`。生产服务同时提供 Vue 静态资源和只读 API。

## 分析口径

- 累计：直接使用披露报表累计值。
- 单季度：Q1 直接使用；H1 减 Q1；Q3 减 H1；FY 减 Q3。相邻期间缺失时显示“暂无数据”。
- TTM：最近四个连续单季度之和；期间不足时显示“暂无数据”。
- 年度：只显示 FY 年报。
- ROE：累计归母净利润除以年初与期末平均归母净资产，并按 Q1、H1、Q3、FY 分别使用 4、2、4/3、1 的年化因子。缺少上年末净资产时不估算。

当前数据库没有现金流量表，界面明确显示范围说明，不虚构现金流指标。

## 数值与颜色约定

- 金额正式存储单位为人民币元，类型为 `INTEGER`。
- 比率保存为百分点，例如 `6.36` 表示 `6.36%`。
- 盈利和正增长显示红色；亏损和负增长显示绿色。
- 正负号和文字说明与颜色同时使用，颜色不是唯一信号。
- `NULL` 显示为“暂无数据”，绝不替换为 0。
- 负财务费用显示为“财务净收益”。
- 标准表的采集、更新时间和批次时间统一使用北京时间（`Asia/Shanghai`，`+08:00`）。

## 常见错误码

- `DATABASE_NOT_FOUND`：未找到默认数据库文件。
- `DATABASE_UNAVAILABLE`：数据库被占用、损坏或暂时不可读。
- `DATABASE_SCHEMA_INVALID`：尚未运行标准化迁移或模式版本不匹配。
- `INVALID_PARAMETERS`：公司代码、期间或比较模式不合法。
- `NO_COMMON_PERIOD`：所选公司没有共同报告期。
- `COMPANY_NOT_FOUND`：标准化公司表中不存在该代码。

## 移动端说明

项目包含 960px、760px 和 640px 等基础响应式规则，表格在窄屏内进行局部横向滚动，页面本身保持无横向溢出。按约定，移动端视觉验收优先级最低，最终手机显示效果由使用方手工确认。
