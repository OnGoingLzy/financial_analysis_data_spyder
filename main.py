import random
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.chrome.service import Service

from selenium_spyder import getdata

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # 配置浏览器驱动路径
    service1 = Service(executable_path='chromedriver.exe')
    # 配置不打开浏览器窗口
    options = webdriver.ChromeOptions()
    # 配置对象添加开启无界面模式的命令
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service1, options=options)
    codes = ["601607", "600998", "000028", "600713", "000963", "600056", "000411", "002589", "000078", "600511",
              "002462", "600829", "603368", "002788", "000705", "600833", "000950", "002727", "605266", "603233",
              "603883", "603939", "301017","000538"]
    # codes = ["000538"]
    # codes = ["601607"]
    for code in codes:
        if not getdata(driver, "SZ" + code):
            getdata(driver, "SH" + code)
            # time.sleep(random.randint(1, 2))
