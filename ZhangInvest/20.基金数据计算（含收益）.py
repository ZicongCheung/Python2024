import json
import requests
import re
import sqlite3
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# 数据库路径
db_path = './fundsdb.sqlite'

# 连接数据库
def connect_db():
    return sqlite3.connect(db_path)

# 获取基金列表
def get_funds(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT fund_code, is_domestic FROM funds")
    funds = cursor.fetchall()
    return funds

# 获取基金基础数据
def fetch_fund_data(fund_code):
    url = f'https://fundgz.1234567.com.cn/js/{fund_code}.js'
    try:
        response = requests.get(url, timeout=5)
        data = response.text.replace('jsonpgz(', '').replace(');', '')
        return json.loads(data)
    except Exception as e:
        print(f"请求失败：{e} (基金代码：{fund_code})")
        return None

# 获取基金历史数据
def fetch_fund_history(fund_code):
    url = f'https://fund.eastmoney.com/pingzhongdata/{fund_code}.js'
    try:
        response = requests.get(url, timeout=5)
        pattern = r'var Data_netWorthTrend = (.*?);'
        match = re.search(pattern, response.text)
        if match:
            return json.loads(match.group(1))[-3:]
    except Exception as e:
        print(f"请求失败：{e} (基金代码：{fund_code})")
    return None

# 获取境内基金最近交易日
def get_recent_trade_date(fund_data, last_three):
    try:
        fund_nav_date = fund_data['jzrq']
        fund_nav = float(fund_data['dwjz'])
        last_nav = last_three[-1]['y']
        second_last_nav = last_three[-2]['y']
        if fund_nav == last_nav:
            return datetime.strptime(fund_nav_date, "%Y-%m-%d").strftime("%m-%d")
        elif fund_nav == second_last_nav:
            return (datetime.strptime(fund_nav_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%m-%d")
    except KeyError:
        pass
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

# 查询交易记录
def fetch_confirmed_transactions(conn, fund_code):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT transaction_type, transaction_amount, confirmed_shares
        FROM transactions WHERE fund_code = ? AND confirmed_shares IS NOT NULL
    ''', (fund_code,))
    return cursor.fetchall()

# 计算持有份额和成本价
def calculate_fund_holdings(transactions):
    total_shares = total_amount = 0.0
    for transaction_type, transaction_amount, confirmed_shares in transactions:
        if transaction_type in ["买入", "定投"]:
            total_shares += confirmed_shares
            total_amount += transaction_amount
        elif transaction_type in ["卖出", "转换"]:
            total_shares -= transaction_amount
            total_amount -= confirmed_shares
    return (total_shares, round(total_amount / total_shares, 4)) if total_shares > 0 else (0, 0)

# 主函数
def main():
    conn = connect_db()
    funds = get_funds(conn)
    domestic_trade_date = None

    # 并发请求基金数据
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_fund_data, code): code for code, is_domestic in funds if is_domestic == 'Y'}

        # 处理境内基金
        for future in as_completed(futures):
            fund_code = futures[future]
            fund_data = future.result()
            if not fund_data:
                continue

            history = fetch_fund_history(fund_code)
            if not history:
                continue

            # 获取最近交易日
            recent_trade_date = get_recent_trade_date(fund_data, history)
            if not recent_trade_date:
                continue

            # 缓存第一个境内基金的交易日
            if not domestic_trade_date:
                domestic_trade_date = recent_trade_date

            # 基础数据计算
            recent_nav = history[-1]['y']
            recent_nav_growth_rate = history[-1]['equityReturn']
            estimated_nav = float(fund_data.get('gsz', 0))
            estimated_growth_rate = float(fund_data.get('gszzl', 0))
            estimated_date = fund_data.get('gztime', '--')[5:10]

            # 获取交易记录并计算持有份额
            transactions = fetch_confirmed_transactions(conn, fund_code)
            hold_shares, cost_nav = calculate_fund_holdings(transactions)
            if hold_shares == 0:
                continue

            yesterday_profit, hold_profit = calculate_profits(
                recent_nav, history[-1]['y'], history[-2]['y'], hold_shares, cost_nav, recent_trade_date, 'Y')
            holding_value = recent_nav * hold_shares
            holding_profit_rate = hold_profit / (cost_nav * hold_shares) if cost_nav > 0 else 0.0

            # 打印结果
            print(f"基金代码：{fund_code} (境内)")
            print(f"净值日期：{recent_trade_date}")
            print(f"单位净值：{recent_nav}")
            print(f"净值增长率：{recent_nav_growth_rate}%")
            print(f"估算净值日期：{estimated_date}")
            print(f"单位估值：{estimated_nav}")
            print(f"估算增长率：{estimated_growth_rate}%")
            print(f"昨日收益：{yesterday_profit:.2f} 元")
            print(f"持有收益：{hold_profit:.2f} 元")
            print(f"持有金额：{holding_value:.2f} 元")
            print(f"持有收益率：{holding_profit_rate*100:.2f} %\n")

        # 处理境外基金
        for fund_code in [code for code, is_domestic in funds if is_domestic == 'N']:
            history = fetch_fund_history(fund_code)
            if not history or not domestic_trade_date:
                continue

            recent_nav = history[-1]['y']
            recent_nav_growth_rate = history[-1]['equityReturn']
            foreign_trade_date = (datetime.strptime(domestic_trade_date, "%m-%d") - timedelta(days=1)).strftime("%m-%d")

            transactions = fetch_confirmed_transactions(conn, fund_code)
            hold_shares, cost_nav = calculate_fund_holdings(transactions)
            if hold_shares == 0:
                continue

            yesterday_profit, hold_profit = calculate_profits(
                recent_nav, history[-1]['y'], history[-2]['y'], hold_shares, cost_nav, foreign_trade_date, 'N')
            holding_value = recent_nav * hold_shares
            holding_profit_rate = hold_profit / (cost_nav * hold_shares) if cost_nav > 0 else 0.0

            print(f"基金代码：{fund_code} (境外)")
            print(f"净值日期：{foreign_trade_date}")
            print(f"单位净值：{recent_nav}")
            print(f"净值增长率：{recent_nav_growth_rate}%")
            print(f"估算净值日期：--")
            print(f"单位估值：--")
            print(f"估算增长率：--")
            print(f"昨日收益：{yesterday_profit:.2f} 元")
            print(f"持有收益：{hold_profit:.2f} 元")
            print(f"持有金额：{holding_value:.2f} 元")
            print(f"持有收益率：{holding_profit_rate*100:.2f} %\n")

    conn.close()

if __name__ == "__main__":
    main()