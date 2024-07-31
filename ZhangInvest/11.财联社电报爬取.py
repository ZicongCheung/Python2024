import requests
import json
import time
from requests.adapters import HTTPAdapter

referer_url = "https://www.cls.cn/telegraph"
# cookie = ""
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    # "Cookie": cookie,
    "Host": "www.cls.cn",
    "Referer": referer_url,
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
}

base_url = "https://www.cls.cn/v1/roll/get_roll_list?app=CailianpressWeb&category=&os=web&rn=30"


def get_json_data(base_url, headers):
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))

    response = requests.get(base_url, timeout=5, headers=headers)
    html = response.text
    false = False
    true = True
    null = None
    html_json = eval(html)
    json_str = json.dumps(html_json)
    results = json.loads(json_str)
    # print(results)
    data = results['data']['roll_data']
    all_list = []
    for i in data:
        time_tuple_1 = time.localtime(i['ctime'])
        bj_time = time.strftime("%Y/%m/%d %H:%M:%S", time_tuple_1)
        # print(bj_time)
        # print(i['content'])
        all_list.append([bj_time, i['content']])
    # print(data)
    return all_list


def get_all_list():
    all_list = get_json_data(base_url, headers)
    return all_list


print(get_all_list())