import requests

# 获取东方财富股票数据&secid=0.股票代码&fields=取值字段,无法爬取主板
url = 'https://push2.eastmoney.com/api/qt/stock/get?fltt=2&invt=2&secid=0.600001&fields=f43'
response = requests.get(url)

# 提取数据中的股票实时价格
stock_price = response.json()['data']['f43']
print(stock_price)