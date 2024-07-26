import requests
import time

# 存在限制访问频率问题
url = "https://d.10jqka.com.cn/v4/time/zs_1A0001/last.js"
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}

while True:
    response = requests.get(url, headers=headers)
    print(response.text)
    time.sleep(5)  # 暂停5秒
