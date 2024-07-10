# 导入库
import time
import json
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup


headers = {
  'host':'q.10jqka.com.cn',
  'Referer':'http://q.10jqka.com.cn/',
  'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.0 Safari/537.36',
  'X-Requested-With':'XMLHttpRequest'
}
url = 'http://q.10jqka.com.cn/index/index/board/all/field/zdf/order/desc/page/%s/ajax/1/' % page_id
res = requests.get(url,headers=headers)
res.encoding = 'GBK'
soup = BeautifulSoup(res.text, 'lxml')
tr_list = soup.select('tbody tr')
print(tr_list)
