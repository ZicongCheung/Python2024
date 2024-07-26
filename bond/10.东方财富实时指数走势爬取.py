import requests

# 仅实时指数价格为https://40.push2.eastmoney.com/api/qt/stock/trends2/sse?fields1=f5&fields2=f53&secid=1.000001
url = "https://40.push2.eastmoney.com/api/qt/stock/trends2/sse?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f17&fields2=f51,f52,f53,f54,f55,f56,f57,f58&secid=1.000001"

try:
    with requests.get(url, stream=True) as response:
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")