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
def get_last_nav_before_date(fund_history, end_date):
    end_timestamp = int(end_date.timestamp() * 1000)  # 转换为毫秒时间戳
    # 确保筛选的是 "严格小于" 结束日期的记录
    filtered_data = [item for item in fund_history if item['x'] < end_timestamp]
    if not filtered_data:
        return None, None
    last_record = filtered_data[-1]
    last_date = datetime.fromtimestamp(last_record['x'] / 1000).strftime('%Y-%m-%d')
    return last_record['y'], last_date  # 返回净值和对应日期

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
def calculate_fund_data(conn, fund_code, start_date, end_date):
    cursor = conn.cursor()

    # 调整 end_date 格式，确保时间精度
    end_date += " 23:59:59"

    # 时间区间内的投入本金
    cursor.execute("""
        SELECT SUM(transaction_amount + transaction_fee) 
        FROM transactions 
        WHERE fund_code = ? AND transaction_type IN ('买入', '定投') AND transaction_time BETWEEN ? AND ?
    """, (fund_code, start_date, end_date))
    transaction_invest = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(transaction_amount + transaction_fee) 
        FROM conversion_details 
        WHERE fund_code = ? AND transaction_time BETWEEN ? AND ?
    """, (fund_code, start_date, end_date))
    conversion_invest = cursor.fetchone()[0] or 0

    total_invest = transaction_invest + conversion_invest

    # 时间区间内的赎回金额
    cursor.execute("""
        SELECT SUM(confirmed_shares) 
        FROM transactions 
        WHERE fund_code = ? AND transaction_type IN ('卖出', '转换') AND transaction_time BETWEEN ? AND ?
    """, (fund_code, start_date, end_date))
    redemption_amount = cursor.fetchone()[0] or 0

    # 时间区间前的基金持有份额
    cursor.execute("""
        SELECT SUM(confirmed_shares) 
        FROM transactions 
        WHERE fund_code = ? AND transaction_type IN ('买入', '定投') AND transaction_time < ?
    """, (fund_code, start_date))
    transaction_shares = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(confirmed_shares) 
        FROM conversion_details 
        WHERE fund_code = ? AND transaction_time < ?
    """, (fund_code, start_date))
    conversion_shares = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(transaction_amount) 
        FROM transactions 
        WHERE fund_code = ? AND transaction_type IN ('卖出', '转换') AND transaction_time < ?
    """, (fund_code, start_date))
    sold_shares = cursor.fetchone()[0] or 0

    total_shares = transaction_shares + conversion_shares - sold_shares

    return total_invest, redemption_amount, total_shares

# 主流程
def main(interval):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT fund_code FROM funds")
        fund_codes = [row[0] for row in cursor.fetchall()]

        end_date = get_end_date(interval)
        start_date = end_date.strftime('%Y-%m-%d')
        end_date_str = datetime.today().strftime('%Y-%m-%d')

        for fund_code in fund_codes:
            fund_history = fetch_fund_history(fund_code)
            if fund_history:
                last_nav, last_date = get_last_nav_before_date(fund_history, end_date)
                if last_nav is not None:
                    total_invest, redemption_amount, total_shares = calculate_fund_data(conn, fund_code, start_date, end_date_str)
                    holding_value = total_shares * last_nav
                    print(f"基金代码: {fund_code}, "
                          f"时间区间内投入本金: {total_invest}, "
                          f"赎回金额: {redemption_amount}, "
                          f"时间区间前基金持有份额: {total_shares}, "
                          f"时间区间前最后交易日日期: {last_date}, "
                          f"时间区间前最后交易日净值: {last_nav}, "
                          f"时间区间前基金持有价值: {holding_value}")
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
