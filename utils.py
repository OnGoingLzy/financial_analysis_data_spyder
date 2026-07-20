import datetime
import random
import json
import requests

from sqlserver_operation import Log


# 获取随机id
def generate_custom_id():
    # 获取当前时间并格式化
    now = datetime.datetime.now()
    formatted_time = now.strftime('%Y%m%d%H%M%S%f')[:-3]  # 去掉最后三位微秒以保留毫秒

    # 生成6位随机数字
    random_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    # 组合时间和随机数字生成ID
    custom_id = f"{formatted_time}{random_digits}"

    return custom_id