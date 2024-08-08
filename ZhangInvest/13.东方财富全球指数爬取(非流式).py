import requests
import time

# 获取东方财富股指信息
url = 'https://push2.eastmoney.com/api/qt/ulist/get?fltt=1&invt=2&fields=f2,f4,f3,f14&secids=1.000001,0.399001,0.399006,100.DJIA,100.SPX,100.NDX&pn=1&np=1&pz=20&dect=1'

def fetch_index_data():
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get('data')
        if data:
            return data.get('diff')
        else:
            return None
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def print_index_data(index_data):
    for index in index_data:
        name = index.get('f14')
        value = index.get('f2') / 100
        change_value = index.get('f4') / 100
        change_percentage = index.get('f3') / 100
        print(f"{name}: 当前指数数值 = {value}, 当前指数涨跌数值 = {change_value}, 当前指数涨跌幅数值 = {change_percentage}%")

def main():
    while True:
        index_data = fetch_index_data()
        if index_data:
            print_index_data(index_data)
            break
        else:
            print("数据为null，10秒后重试...")
            time.sleep(10)

if __name__ == "__main__":
    main()
