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
    filtered_data = [item for item in fund_history if item['x'] < end_timestamp]
    if not filtered_data:
        return None
    return filtered_data[-1]['y']  # 返回最后一个交易日的净值

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
        last_friday = today - timedelta(days=today.weekday() + 3) if today.weekday() < 5 else today - timedelta(days=today.weekday() - 4)
        return last_friday
    else:
        raise ValueError("无效的时间区间")

# 主流程
def main(interval):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT fund_code FROM funds")
        fund_codes = [row[0] for row in cursor.fetchall()]

        end_date = get_end_date(interval)

        for fund_code in fund_codes:
            fund_history = fetch_fund_history(fund_code)
            if fund_history:
                last_nav = get_last_nav_before_date(fund_history, end_date)
                if last_nav is not None:
                    print(f"基金代码: {fund_code}, 时间区间之前的最后一个交易日净值: {last_nav}")
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