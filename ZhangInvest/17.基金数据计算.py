import json
import requests
import re
from datetime import datetime, timedelta

# 获取基金基础数据
fund_code = "011613"
url_fund_data = f'http://fundgz.1234567.com.cn/js/{fund_code}.js'
response_fund_data = requests.get(url_fund_data)
data_fund = response_fund_data.text.replace('jsonpgz(', '').replace(');', '')
fund_data = json.loads(data_fund)

# 解析基金基础数据
fund_nav_date = fund_data['jzrq']  # 基金净值日期
fund_nav = float(fund_data['dwjz'])  # 基金单位净值
fund_estimated_nav = float(fund_data['gsz'])  # 基金估算净值
fund_estimated_growth_rate = float(fund_data['gszzl'])  # 基金估算增长率
hold_shares = 2546.8  # 假设的持有份额
cost_nav = 0.7853  # 假设的持仓成本净值

# 获取基金历史近三天净值
url_history_data = f'http://fund.eastmoney.com/pingzhongdata/{fund_code}.js'
response_history_data = requests.get(url_history_data)
pattern = r'var Data_netWorthTrend = (.*?);'
match = re.search(pattern, response_history_data.text)

if match:
    net_worth_trend_str = match.group(1)
    # 将字符串转换为 JSON 对象
    net_worth_trend = json.loads(net_worth_trend_str)

    # 获取最后三个元素
    last_three = net_worth_trend[-3:]
else:
    print("未找到 Data_netWorthTrend 字段")
    exit()

# 比对基金基础数据的dwjz与基金历史数据的y值
last_nav = last_three[-1]['y']
second_last_nav = last_three[-2]['y']
third_last_nav = last_three[-3]['y']

# 计算最近一个交易日的日期
if fund_nav == last_nav:
    recent_trade_date = fund_nav_date
elif fund_nav == second_last_nav:
    # 基金净值日期加一天
    recent_trade_date = (datetime.strptime(fund_nav_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
else:
    print("无法比对基金基础数据与历史数据")
    exit()

# 获取最近一个交易日的单位净值和净值增长率
recent_nav = last_nav
recent_nav_growth_rate = last_three[-1]['equityReturn']

# 获取最近一个交易日的单位估值和估算增长率
recent_estimated_nav = fund_estimated_nav
recent_estimated_growth_rate = fund_estimated_growth_rate

# 计算昨日收益
# 获取今天的日期和北京时间的前天的日期
today = datetime.now().date()
day_before_yesterday = (today - timedelta(days=2))

# 如果最近一个交易日是北京时间的前天或更早，昨日收益为 0
if recent_trade_date == day_before_yesterday.strftime("%Y-%m-%d"):
    yesterday_profit = 0.0
else:
    # 正常计算昨日收益
    yesterday_nav = second_last_nav
    day_before_yesterday_nav = third_last_nav
    yesterday_profit = (yesterday_nav - day_before_yesterday_nav) * hold_shares

# 计算持有收益
hold_profit = (recent_nav - cost_nav) * hold_shares

# 输出结果
print(f"最近一个交易日的日期：{recent_trade_date}")
print(f"最近一个交易日的单位净值：{recent_nav}")
print(f"最近一个交易日的净值增长率：{recent_nav_growth_rate}%")
print(f"最近一个交易日的单位估值：{recent_estimated_nav}")
print(f"最近一个交易日的估算增长率：{recent_estimated_growth_rate}%")
print(f"昨日收益：{yesterday_profit:.2f} 元")
print(f"持有收益：{hold_profit:.2f} 元")