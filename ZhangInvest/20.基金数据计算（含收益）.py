import json
import requests
import re
import sqlite3
from datetime import datetime, timedelta

# 数据库路径
db_path = './fundsdb.sqlite'

# 连接数据库并获取funds表中的fund_code和is_domestic字段
def get_funds():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT fund_code, is_domestic FROM funds")
    funds = cursor.fetchall()
    conn.close()
    return funds

# 获取基金基础数据
def fetch_fund_data(fund_code):
    url_fund_data = f'https://fundgz.1234567.com.cn/js/{fund_code}.js'
    response_fund_data = requests.get(url_fund_data)
    data_fund = response_fund_data.text.replace('jsonpgz(', '').replace(');', '')
    return json.loads(data_fund)

# 获取基金历史近三天净值
def fetch_fund_history(fund_code):
    url_history_data = f'https://fund.eastmoney.com/pingzhongdata/{fund_code}.js'
    response_history_data = requests.get(url_history_data)
    pattern = r'var Data_netWorthTrend = (.*?);'
    match = re.search(pattern, response_history_data.text)
    if match:
        net_worth_trend_str = match.group(1)
        return json.loads(net_worth_trend_str)[-3:]  # 最后三天的数据
    else:
        print("未找到 Data_netWorthTrend 字段")
        return None

# 获取境内基金的最近交易日
def get_recent_trade_date(fund_data, last_three):
    fund_nav_date = fund_data['jzrq']
    fund_nav = float(fund_data['dwjz'])
    last_nav = last_three[-1]['y']
    second_last_nav = last_three[-2]['y']

    # 比对基金净值
    if fund_nav == last_nav:
        return datetime.strptime(fund_nav_date, "%Y-%m-%d").strftime("%m-%d")
    elif fund_nav == second_last_nav:
        return (datetime.strptime(fund_nav_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%m-%d")
    else:
        return None

# 计算昨日收益和持有收益
def calculate_profits(recent_nav, second_last_nav, third_last_nav, hold_shares, cost_nav, recent_trade_date, is_domestic):
    today = datetime.now().date()
    day_before_yesterday = (today - timedelta(days=2))
    three_days_ago = (today - timedelta(days=3))

    # 根据基金类型判断最近交易日的收益计算
    if is_domestic == 'Y':  # 境内基金
        # 如果最近一个交易日日期为北京时间前天或更早，那昨日收益应该为0
        if recent_trade_date == day_before_yesterday.strftime("%m-%d"):
            yesterday_profit = 0.0
        else:
            yesterday_profit = (second_last_nav - third_last_nav) * hold_shares
    else:  # 境外基金
        # 如果最近一个交易日日期为北京时间大前天或更早，那昨日收益应该为0
        if recent_trade_date == three_days_ago.strftime("%m-%d"):
            yesterday_profit = 0.0
        else:
            yesterday_profit = (second_last_nav - third_last_nav) * hold_shares

    hold_profit = (recent_nav - cost_nav) * hold_shares
    return yesterday_profit, hold_profit

# 连接数据库
def connect_db():
    return sqlite3.connect('fundsdb.sqlite')

# 查询某个基金的所有已成交交易记录
def fetch_confirmed_transactions(fund_code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT transaction_type, transaction_amount, confirmed_shares
        FROM transactions
        WHERE fund_code =? AND confirmed_shares IS NOT NULL
    ''', (fund_code,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# 计算基金的持有份额和持仓成本价
def calculate_fund_holdings(fund_code):
    transactions = fetch_confirmed_transactions(fund_code)

    if not transactions:
        print(f"基金 {fund_code} 没有已成交的交易记录。")
        return

    total_shares = 0.0  # 持有份额
    total_amount = 0.0  # 购入金额

    for transaction_type, transaction_amount, confirmed_shares in transactions:
        if transaction_type in ["买入", "定投"]:  # 买入或定投
            total_shares += confirmed_shares
            total_amount += transaction_amount
        elif transaction_type in ["卖出", "转换"]:  # 卖出或转换
            total_shares -= transaction_amount
            total_amount -= confirmed_shares

    # 计算持仓成本价
    if total_shares > 0:
        cost_price = total_amount / total_shares  # 保留小数点后四位
        cost_price = round(cost_price, 4)
        return total_shares, cost_price
    else:
        print(f"基金 {fund_code} 当前没有持有份额，无法计算持仓成本价。")
        return 0, 0

# 主函数
def main():
    funds = get_funds()
    domestic_trade_date = None
    foreign_funds = []

    # 第一步：处理境内基金
    for fund_code, is_domestic in funds:
        if is_domestic == 'Y':
            fund_data = fetch_fund_data(fund_code)
            last_three = fetch_fund_history(fund_code)

            if not last_three:
                continue

            # 计算境内基金的最近交易日
            recent_trade_date = get_recent_trade_date(fund_data, last_three)
            if not recent_trade_date:
                print(f"无法比对基金基础数据与历史数据, fund_code: {fund_code}")
                continue

            recent_nav = last_three[-1]['y']
            recent_nav_growth_rate = last_three[-1]['equityReturn']
            recent_estimated_nav = float(fund_data['gsz'])
            recent_estimated_growth_rate = float(fund_data['gszzl'])
            fund_estimated_nav_date = fund_data['gztime'][5:10]

            # 获取基金持有份额和成本价
            hold_shares, cost_nav = calculate_fund_holdings(fund_code)
            if hold_shares == 0:
                continue

            # 计算收益
            yesterday_profit, hold_profit = calculate_profits(recent_nav, last_three[-1]['y'], last_three[-2]['y'],
                                                              hold_shares, cost_nav, recent_trade_date, is_domestic)

            # 输出结果
            print(f"基金代码：{fund_code} (境内)")
            print(f"净值日期：{recent_trade_date}")
            print(f"单位净值：{recent_nav}")
            print(f"净值增长率：{recent_nav_growth_rate}%")
            print(f"估算净值日期：{fund_estimated_nav_date}")
            print(f"单位估值：{recent_estimated_nav}")
            print(f"估算增长率：{recent_estimated_growth_rate}%")
            print(f"昨日收益：{yesterday_profit:.2f} 元")
            print(f"持有收益：{hold_profit:.2f} 元\n")

            # 记录境内基金的交易日
            if not domestic_trade_date:
                domestic_trade_date = recent_trade_date

        elif is_domestic == 'N':
            # 暂存境外基金信息
            foreign_funds.append(fund_code)

    # 第二步：处理境外基金
    if domestic_trade_date:
        for fund_code in foreign_funds:
            last_three = fetch_fund_history(fund_code)
            if not last_three:
                continue

            # 境外基金的最近交易日比境内早一天
            foreign_trade_date = (datetime.strptime(domestic_trade_date, "%m-%d") - timedelta(days=1)).strftime("%m-%d")

            recent_nav = last_three[-1]['y']
            recent_nav_growth_rate = last_three[-1]['equityReturn']

            # 获取基金持有份额和成本价
            hold_shares, cost_nav = calculate_fund_holdings(fund_code)
            if hold_shares == 0:
                continue

            # 计算收益
            yesterday_profit, hold_profit = calculate_profits(recent_nav, last_three[-1]['y'], last_three[-2]['y'],
                                                              hold_shares, cost_nav, foreign_trade_date, 'N')

            # 输出结果
            print(f"基金代码：{fund_code} (境外)")
            print(f"净值日期：{foreign_trade_date}")
            print(f"单位净值：{recent_nav}")
            print(f"净值增长率：{recent_nav_growth_rate}%")
            print(f"估算净值日期：--")
            print(f"单位估值：--")
            print(f"估算增长率：--")
            print(f"昨日收益：{yesterday_profit:.2f} 元")
            print(f"持有收益：{hold_profit:.2f} 元\n")


if __name__ == "__main__":
    main()