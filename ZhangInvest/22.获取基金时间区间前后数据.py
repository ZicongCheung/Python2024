import json
import requests
import re
import sqlite3
from datetime import datetime, timedelta

# 数据库路径
db_path = './fundsdb.sqlite'

# 连接数据库
def connect_db():
    return sqlite3.connect(db_path)

# 获取基金历史数据
def fetch_fund_history(fund_code):
    url = f'https://fund.eastmoney.com/pingzhongdata/{fund_code}.js'
    try:
        response = requests.get(url, timeout=5)
        pattern = r'var Data_netWorthTrend = (.*?);'
        match = re.search(pattern, response.text)
        if match:
            return json.loads(match.group(1))
    except Exception as e:
        print(f"请求失败：{e} (基金代码：{fund_code})")
    return None

# 获取输入时间区间之前的最后一个交易日
def get_last_nav_before_date(fund_history, end_date, is_domestic):
    end_timestamp = int(end_date.timestamp() * 1000)  # 转换为毫秒时间戳
    # 确保筛选的是 "严格小于" 结束日期的记录
    filtered_data = [item for item in fund_history if item['x'] < end_timestamp]

    if not filtered_data:
        return None, None  # 无法获取指定时间区间之前的交易数据

    if is_domestic == "Y":
        # 境内基金取最后一个交易日
        last_record = filtered_data[-1]
    else:
        # 境外基金取倒数第二个交易日
        if len(filtered_data) < 2:
            return None, None  # 数据不足以取倒数第二个交易日
        last_record = filtered_data[-2]

    last_nav = last_record['y']
    last_date = datetime.fromtimestamp(last_record['x'] / 1000).strftime('%Y-%m-%d')
    return last_nav, last_date

# 获取时间区间的结束日期
def get_end_date(interval):
    today = datetime.today()
    if interval == "本年":
        return datetime(today.year, 1, 1)
    elif interval == "本季":
        month = ((today.month - 1) // 3) * 3 + 1
        return datetime(today.year, month, 1)
    elif interval == "本月":
        return datetime(today.year, today.month, 1)
    elif interval == "本周":
        # 本周第一天减去一天，即上周最后一个交易日的结束日期
        monday = today - timedelta(days=today.weekday())
        return monday - timedelta(days=1)
    else:
        raise ValueError("无效的时间区间")

# 计算时间区间的金额数据
def calculate_fund_data(conn, fund_code, start_date, end_date, last_nav, current_nav):
    cursor = conn.cursor()

    # 调整 end_date 格式，确保时间精度
    end_date += " 23:59:59"

    # 时间区间前持有的基金份额
    cursor.execute("""
        SELECT SUM(confirmed_shares)
        FROM transactions
        WHERE fund_code = ? AND transaction_type IN ('买入', '定投') AND confirmed_date < ?
    """, (fund_code, start_date))
    transaction_shares = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(confirmed_shares)
        FROM conversion_details
        WHERE fund_code = ? AND confirmed_date < ?
    """, (fund_code, start_date))
    conversion_shares = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(transaction_amount)
        FROM transactions
        WHERE fund_code = ? AND transaction_type IN ('卖出', '转换') AND confirmed_date < ?
    """, (fund_code, start_date))
    sold_shares = cursor.fetchone()[0] or 0

    shares_before_interval = transaction_shares + conversion_shares - sold_shares

    # 时间区间内购入的基金份额收益
    cursor.execute("""
        SELECT confirmed_shares, confirmed_nav, transaction_fee
        FROM transactions
        WHERE fund_code = ? AND transaction_type IN ('买入', '定投') AND confirmed_date BETWEEN ? AND ?
    """, (fund_code, start_date, end_date))
    transactions = cursor.fetchall()

    cursor.execute("""
        SELECT confirmed_shares, confirmed_nav, transaction_fee
        FROM conversion_details
        WHERE fund_code = ? AND confirmed_date BETWEEN ? AND ?
    """, (fund_code, start_date, end_date))
    conversions = cursor.fetchall()

    purchase_profit = sum(confirmed_shares * (current_nav - confirmed_nav)
                          for confirmed_shares, confirmed_nav, _ in transactions + conversions)

    purchase_fees = sum(transaction_fee for _, _, transaction_fee in transactions + conversions)

    # 时间区间内卖出/转换的基金份额收益
    cursor.execute("""
        SELECT transaction_amount, confirmed_shares
        FROM transactions
        WHERE fund_code = ? AND transaction_type IN ('卖出', '转换') AND confirmed_date BETWEEN ? AND ?
    """, (fund_code, start_date, end_date))
    redemptions = cursor.fetchall()

    redemption_profit = sum(transaction_amount * (current_nav - last_nav)
                            for transaction_amount, confirmed_shares in redemptions)

    return shares_before_interval, purchase_profit, redemption_profit, purchase_fees

# 主流程
def main(interval):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT fund_code, is_domestic FROM funds")
        fund_records = cursor.fetchall()

        end_date = get_end_date(interval)
        start_date = end_date.strftime('%Y-%m-%d')
        end_date_str = datetime.today().strftime('%Y-%m-%d')

        for fund_code, is_domestic in fund_records:
            fund_history = fetch_fund_history(fund_code)
            if fund_history:
                last_nav, last_date = get_last_nav_before_date(fund_history, end_date, is_domestic)
                if last_nav is not None:
                    current_nav = fund_history[-1]['y']  # 当前基金最新净值

                    shares_before_interval, purchase_profit, redemption_profit, purchase_fees = calculate_fund_data(
                        conn, fund_code, start_date, end_date_str, last_nav, current_nav)

                    interval_profit = shares_before_interval * (current_nav - last_nav) + purchase_profit + redemption_profit - purchase_fees

                    print(f"基金代码: {fund_code}, "
                          f"时间区间前持有基金份额: {shares_before_interval}, "
                          f"时间区间前最后交易日日期: {last_date}, "
                          f"时间区间前最后交易日净值: {last_nav}, "
                          f"当前基金最新净值: {current_nav}, "
                          f"时间区间内购入份额收益: {purchase_profit}, "
                          f"时间区间内赎回/转换份额收益: {redemption_profit}, "
                          f"时间区间内购入手续费: {purchase_fees}, "
                          f"时间区间内收益: {interval_profit}")
                else:
                    print(f"基金代码: {fund_code}, 无法获取指定时间区间之前的净值")
            else:
                print(f"基金代码: {fund_code}, 无法获取历史数据")
    except Exception as e:
        print(f"运行时出错：{e}")
    finally:
        conn.close()

if __name__ == "__main__":
    user_interval = input("请输入时间区间（本年、本季、本月、本周）：")
    main(user_interval)
