import requests
from bs4 import BeautifulSoup

stock_code = '600000'
url = f"http://basic.10jqka.com.cn/{stock_code}/"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    # "Cookie": cookie,
    "Host": "basic.10jqka.com.cn",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0"
}

response = requests.get(url, headers=headers)
response.encoding = 'gbk'  # 手动设置响应编码为 GBK

# 使用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(response.text, 'html.parser')

# 查找包含“公司亮点”和“主营业务”信息的元素
company_highlight = soup.find('span', {'class': 'tip f14 fl core-view-text'})
main_business = soup.find('span', {'class': 'tip f14 fl main-bussiness-text'})

# 提取并打印所需文本
if company_highlight:
    print(company_highlight.get_text(strip=True))

if main_business:
    print(main_business.get_text(strip=True))