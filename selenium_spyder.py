from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sqlserver_operation import insert_zcfzb, insert_lrb
from utils import generate_custom_id

from selenium.common.exceptions import TimeoutException, NoSuchElementException


INCOME_ROW_LABELS = {
    "total_operating_income": "营业总收入",
    "total_operating_cost": "营业总成本",
    "operating_cost": "营业成本",
}


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
        return True

    except TimeoutException as e:
        print(f"超时异常: {e}")
        return False


def getlrb(lrb, driver, name, code):
    lrbData = []
    insertId = generate_custom_id()
    driver.find_element(By.CLASS_NAME, 'commonTab').find_elements(By.TAG_NAME, 'li')[1].click()
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

        lrbData.append(
            (code, name, pnj, yyzsr, yysr, xsx, glx, cwf, yycb, yylr, lrze, date, sxf, yysj, insertId, lrz, lxsr,mlr,mll,cxjyjlr,bmbjlr,dkjylr,yyzsrtb))

    return lrbData


# 获取资产负债表数据
def getZcfz(zcfzb, driver, name, code):
    ZcfzData = []
    insertId = generate_custom_id()
    driver.find_element(By.CLASS_NAME, 'commonTab').find_elements(By.TAG_NAME, 'li')[0].click()
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

        ZcfzData.append((code, name, zczj, zclj, sszb, zbgj, qtzy, ybgj, wdlr, sswdb, date, insertId, ysrk))

    return ZcfzData
