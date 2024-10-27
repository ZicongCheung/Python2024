import requests
import re
import json

fund_code = "011613"
url = f'http://fund.eastmoney.com/pingzhongdata/{fund_code}.js'
response = requests.get(url)
pattern = r'var Data_netWorthTrend = (.*?);'
match = re.search(pattern, response.text)

if match:
    net_worth_trend_str = match.group(1)
    # 将字符串转换为 JSON 对象
    net_worth_trend = json.loads(net_worth_trend_str)

    # 获取最后三个元素
    last_three = net_worth_trend[-3:]
    print(last_three)
else:
    print("未找到 Data_netWorthTrend 字段")