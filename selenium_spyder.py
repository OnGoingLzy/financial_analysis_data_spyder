from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sqlserver_operation import insert_lrb, insert_xjllb, insert_zcfzb
from utils import generate_custom_id

from selenium.common.exceptions import TimeoutException, NoSuchElementException


INCOME_ROW_LABELS = {
    "total_operating_income": "营业总收入",
    "total_operating_cost": "营业总成本",
    "operating_cost": "营业成本",
}

CASH_FLOW_ROW_LABELS = {
    "net_operating_cash_flow": ("经营活动产生的现金流量净额",),
    "net_investing_cash_flow": ("投资活动产生的现金流量净额",),
    "net_financing_cash_flow": ("筹资活动产生的现金流量净额",),
    "cash_received_from_sales": ("销售商品、提供劳务收到的现金",),
    "capital_expenditure": ("购建固定资产、无形资产和其他长期资产支付的现金",),
    "ending_cash_and_equivalents": ("期末现金及现金等价物余额", "现金及现金等价物净增加额的期末余额"),
}

INCOME_EXTRA_ROW_LABELS = {
    "income_tax_expense": ("所得税费用",),
    "investment_income": ("投资收益", "投资收益（损失以“-”号填列）"),
    "asset_impairment_loss": ("资产减值损失",),
    "credit_impairment_loss": ("信用减值损失",),
}

BALANCE_EXTRA_ROW_LABELS = {
    "monetary_funds": ("货币资金",),
    "inventory": ("存货",),
    "accounts_payable": ("应付账款",),
    "current_assets": ("流动资产合计",),
    "current_liabilities": ("流动负债合计",),
    "short_term_borrowings": ("短期借款",),
    "long_term_borrowings": ("长期借款",),
    "total_equity": ("所有者权益（或股东权益）合计", "所有者权益合计"),
    "equity_attributable_to_parent": ("归属于母公司股东权益合计", "归属于母公司所有者权益合计"),
    "goodwill": ("商誉",),
}


def build_statement_rows(periods, table_rows, field_labels):
    """把任意来源的“指标名-报告期值”矩阵转换成标准字段记录。"""
    normalized_rows = []
    for index, period in enumerate(periods):
        record = {"disclosure_date": period}
        for field, candidates in field_labels.items():
            values = next((table_rows[label] for label in candidates if label in table_rows), None)
            record[field] = values[index] if values is not None and index < len(values) else None
        normalized_rows.append(record)
    return normalized_rows


def extract_statement_rows(table, field_labels, limit=5):
    """从 Selenium 表格读取矩阵；网页标签变化只需调整候选标签映射。"""
    headers = table.find_element(By.CLASS_NAME, "tableHeaderFix").find_elements(By.TAG_NAME, "th")
    periods = [header.text.strip() for header in headers[1:limit + 1]]
    table_rows = {}
    for row in table.find_elements(By.TAG_NAME, "tr"):
        cells = row.find_elements(By.TAG_NAME, "td")
        if not cells:
            continue
        label = cells[0].text.replace("\n", "").strip()
        table_rows[label] = [cell.text.strip() for cell in cells[1:limit + 1]]
    return build_statement_rows(periods, table_rows, field_labels)


def getdata(driver, code):
    try:
        driver.get(
            'https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code=' + code + '&color=b#/cwfx')
        # 若class为checked_Nodata的元素存在，则说明没有数据 return
        try:
            if driver.find_element(By.CLASS_NAME, 'checked_Nodata'):
                return False
        except NoSuchElementException as e:
            print(f"{code}公司信息存在")
        # 等待页面加载完成
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "zcfzb_table")))

        # 尝试获取 zcfzb 表格元素
        try:
            zcfzb = driver.find_elements(By.CLASS_NAME, 'zcfzb_table')[0]

            lrb = driver.find_elements(By.CLASS_NAME, 'lrb_table')[0]
        except IndexError:
            return False

        # 获取 class 为 stockName 的 a 元素的文本
        name = driver.find_element(By.CLASS_NAME, 'stockName').text
        insert_zcfzb(getZcfz(zcfzb, driver, name, code))
        insert_lrb(getlrb(lrb, driver, name, code))
        cash_tables = driver.find_elements(By.CLASS_NAME, 'xjllb_table')
        if cash_tables:
            insert_xjllb(getxjllb(cash_tables[0], driver, name, code))
        return True

    except TimeoutException as e:
        print(f"超时异常: {e}")
        return False


def getxjllb(table, driver, name, code):
    tabs = driver.find_element(By.CLASS_NAME, 'commonTab').find_elements(By.TAG_NAME, 'li')
    if len(tabs) > 2:
        tabs[2].click()
    batch_id = generate_custom_id()
    records = extract_statement_rows(table, CASH_FLOW_ROW_LABELS)
    return [(
        code, name,
        record["net_operating_cash_flow"], record["net_investing_cash_flow"],
        record["net_financing_cash_flow"], record["cash_received_from_sales"],
        record["capital_expenditure"], record["ending_cash_and_equivalents"],
        record["disclosure_date"], batch_id,
    ) for record in records]


def getlrb(lrb, driver, name, code):
    lrbData = []
    insertId = generate_custom_id()
    driver.find_element(By.CLASS_NAME, 'commonTab').find_elements(By.TAG_NAME, 'li')[1].click()
    extra_records = extract_statement_rows(lrb, INCOME_EXTRA_ROW_LABELS)
    zyzb_table = driver.find_elements(By.CLASS_NAME, 'zcfzb_table')[0]
    for i in range(5):
        # 披露日期
        date = lrb.find_element(By.CLASS_NAME, 'tableHeaderFix').find_elements(By.TAG_NAME, 'th')[i + 1].text

        #
        yyzsr_span_element = lrb.find_element(By.XPATH, f"//span[text()='{INCOME_ROW_LABELS['total_operating_income']}']")
        yyzsr_element = yyzsr_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        yyzsr = yyzsr_element.find_elements(By.TAG_NAME, 'td')[i + 1].text
        # 营业总成本
        yysr_span_element = lrb.find_element(By.XPATH, f"//span[text()='{INCOME_ROW_LABELS['total_operating_cost']}']")
        yysr_element = yysr_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        yysr = yysr_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        # 营业成本
        yycb_span_element = lrb.find_element(By.XPATH, f"//span[text()='{INCOME_ROW_LABELS['operating_cost']}']")
        yycb_element = yycb_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        yycb = yycb_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        # 营业利润
        lrze_span_element = lrb.find_element(By.XPATH, "//span[text()='营业利润']")
        lrze_element = lrze_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        lrze = lrze_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        # 营业利润
        yylr_span_element = lrb.find_element(By.XPATH, "//span[text()='营业利润']")
        yylr_element = yylr_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        yylr = yylr_element.find_elements(By.TAG_NAME, 'td')[i + 1].text
        # 销售费用
        xsx_span_element = lrb.find_element(By.XPATH, "//span[text()='销售费用']")
        xsx_element = xsx_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        xsx = xsx_element.find_elements(By.TAG_NAME, 'td')[i + 1].text
        # 管理费用
        glx_span_element = lrb.find_element(By.XPATH, "//span[text()='管理费用']")
        glx_element = glx_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        glx = glx_element.find_elements(By.TAG_NAME, 'td')[i + 1].text
        # 财务费用
        cwf_span_element = lrb.find_element(By.XPATH, "//span[text()='财务费用']")
        cwf_element = cwf_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        cwf = cwf_element.find_elements(By.TAG_NAME, 'td')[i + 1].text
        # 营业税金及附加
        yysj_span_element = lrb.find_element(By.XPATH, "//span[text()='营业税金及附加']")
        yysj_element = yysj_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        yysj = yysj_element.find_elements(By.TAG_NAME, 'td')[i + 1].text
        # 研发费用
        sxf_span_element = lrb.find_element(By.XPATH, "//span[text()='研发费用']")
        sxf_element = sxf_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        sxf = sxf_element.find_elements(By.TAG_NAME, 'td')[i + 1].text
        # 其中:利息费用
        lrz_span_element = lrb.find_element(By.XPATH, "//span[text()='其中:利息费用']")
        lrz_element = lrz_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        lrz = lrz_element.find_elements(By.TAG_NAME, 'td')[i + 1].text
        # 其中:利息收入
        lxsr_span_element = lrb.find_element(By.XPATH, "//span[text()='其中:利息收入']")
        lxsr_element = lxsr_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        lxsr = lxsr_element.find_elements(By.TAG_NAME, 'td')[i + 1].text
        # 净利润
        pnj_span_element = lrb.find_element(By.XPATH, "//span[text()='净利润']")
        pnj_element = pnj_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        pnj = pnj_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        # 毛利润
        mlr_span_element = driver.find_element(By.XPATH, "//td[text()='毛利润(元)']")
        mlr_element = mlr_span_element.find_element(By.XPATH, "./ancestor::tr")
        mlr = mlr_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        # 毛利率(%)
        mll_span_element = driver.find_element(By.XPATH, "//td[text()='毛利率(%)']")
        mll_element = mll_span_element.find_element(By.XPATH, "./ancestor::tr")
        mll = mll_element.find_elements(By.TAG_NAME, 'td')[i + 1].text


        # 持续经营净利润
        cxjyjlr_span_element = driver.find_element(By.XPATH, "//span[text()='持续经营净利润']")
        cxjyjlr_element = cxjyjlr_span_element.find_element(By.XPATH, "./ancestor::tr")
        cxjyjlr = cxjyjlr_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        # 归属于母公司股东的净利润
        bmbjlr_span_element = driver.find_element(By.XPATH, "//span[text()='归属于母公司股东的净利润']")
        bmbjlr_element = bmbjlr_span_element.find_element(By.XPATH, "./ancestor::tr")
        bmbjlr = bmbjlr_element.find_elements(By.TAG_NAME, 'td')[i + 1].text
        # 扣除非经常性损益后的净利润
        dkjylr_span_element = driver.find_element(By.XPATH, "//span[text()='扣除非经常性损益后的净利润']")
        dkjylr_element = dkjylr_span_element.find_element(By.XPATH, "./ancestor::tr")
        dkjylr = dkjylr_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        #营业总收入同比增长
        yyzsrtb_span_element = zyzb_table.find_element(By.XPATH, "//td[text()='营业总收入同比增长(%)']")
        yyzsrtb_element = yyzsrtb_span_element.find_element(By.XPATH, "./ancestor::tr")
        yyzsrtb = yyzsrtb_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        extra = extra_records[i]
        lrbData.append(
            (code, name, pnj, yyzsr, yysr, xsx, glx, cwf, yycb, yylr, lrze, date, sxf, yysj,
             insertId, lrz, lxsr, mlr, mll, cxjyjlr, bmbjlr, dkjylr, yyzsrtb,
             extra["income_tax_expense"], extra["investment_income"],
             extra["asset_impairment_loss"], extra["credit_impairment_loss"]))

    return lrbData


# 获取资产负债表数据
def getZcfz(zcfzb, driver, name, code):
    ZcfzData = []
    insertId = generate_custom_id()
    driver.find_element(By.CLASS_NAME, 'commonTab').find_elements(By.TAG_NAME, 'li')[0].click()
    extra_records = extract_statement_rows(zcfzb, BALANCE_EXTRA_ROW_LABELS)
    for i in range(5):
        # 披露日期
        date = zcfzb.find_element(By.CLASS_NAME, 'tableHeaderFix').find_elements(By.TAG_NAME, 'th')[i + 1].text
        # 获取span值为"资产总计"的span
        zczj_span_element = driver.find_element(By.XPATH, "//span[text()='资产总计']")
        # 获取上级的上级元素
        zczj_element = zczj_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        # 资产总计
        # 获取span的值

        zczj = zczj_element.find_elements(By.TAG_NAME, 'td')[i + 1].find_element(By.TAG_NAME, "span").text

        # 获取span值为"负债合计"的span
        zclj_span_element = driver.find_element(By.XPATH, "//span[text()='负债合计']")
        # 获取上级的上级元素
        zclj_element = zclj_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        # 负债合计
        zclj = zclj_element.find_elements(By.TAG_NAME, 'td')[i + 1].find_element(By.TAG_NAME, "span").text

        # 实收资本
        sszb_span_element = driver.find_element(By.XPATH, "//span[text()='实收资本（或股本）']")
        sszb_element = sszb_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        sszb = sszb_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        # 资本公积
        zbgj_span_element = driver.find_element(By.XPATH, "//span[text()='资本公积']")
        zbgj_element = zbgj_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        zbgj = zbgj_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        # 其他综合收益
        qtzy_span_element = driver.find_element(By.XPATH, "//span[text()='其他综合收益']")
        qtzy_element = qtzy_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        qtzy = qtzy_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        # 盈余公积
        ybgj_span_element = driver.find_element(By.XPATH, "//span[text()='盈余公积']")
        ybgj_element = ybgj_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        ybgj = ybgj_element.find_elements(By.TAG_NAME, 'td')[i + 1].text
        # 未分配利润
        wdlr_span_element = driver.find_element(By.XPATH, "//span[text()='未分配利润']")
        wdlr_element = wdlr_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        wdlr = wdlr_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        # 少数股东权益
        sswdb_span_element = driver.find_element(By.XPATH, "//span[text()='少数股东权益']")
        sswdb_element = sswdb_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        sswdb = sswdb_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        # 应收账款
        try:
            ysrk_span_element = driver.find_element(By.XPATH, "//span[text()='应收账款']")
        except NoSuchElementException:
            ysrk_span_element = driver.find_element(By.XPATH, "//span[text()='其中:应收账款']")
        # ysrk_span_element = driver.find_element(By.XPATH, "//span[text()='应收账款']")
        ysrk_element = ysrk_span_element.find_element(By.XPATH, "./ancestor::td/ancestor::tr")
        ysrk = ysrk_element.find_elements(By.TAG_NAME, 'td')[i + 1].text

        # print("资产总计：", zczj)
        # print("负债合计：", zclj)
        # print("实收资本（或股本）：", sszb)
        # print("资本公积：", zbgj)
        # print("其他综合收益：", qtzy)
        # print("盈余公积：", ybgj)
        # print("未分配利润：", wdlr)
        # print("少数股东权益：", sswdb)
        # print("披露日期：", date)

        extra = extra_records[i]
        ZcfzData.append((
            code, name, zczj, zclj, sszb, zbgj, qtzy, ybgj, wdlr, sswdb, date, insertId, ysrk,
            extra["monetary_funds"], extra["inventory"], extra["accounts_payable"],
            extra["current_assets"], extra["current_liabilities"],
            extra["short_term_borrowings"], extra["long_term_borrowings"],
            extra["total_equity"], extra["equity_attributable_to_parent"], extra["goodwill"],
        ))

    return ZcfzData
