import re
import requests
from lxml import etree

网址 = "https://www.jkl.com.cn/shop.aspx"
UA伪装 = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}
响应数据 = requests.get(url=网址,headers=UA伪装).text
解析 = etree.HTML(响应数据)
城区名称 = 解析.xpath('//div[@class="infoLis"]//a/text()')
城区链接 = 解析.xpath('//div[@class="infoLis"]//@href')
for i in range(1,13):
    名称 = 城区名称[i-1].strip()
    链接 = 'https://www.jkl.com.cn/' + 城区链接[i-1]
    响应数据1 = requests.get(url=链接,headers=UA伪装).text
    解析1 = etree.HTML(响应数据1)
    尾页 = 解析1.xpath('//a[text()="尾页"]/@href')
    if 尾页 != []:
        正则 = re.search("(\\d+)",尾页[0])
        页数 = 正则.group(0)
    else:
        页数 = 1
    print(f'{名称},{链接},总页数{页数}')