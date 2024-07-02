import requests
from lxml import etree
import re
网址 = "https://www.jkl.com.cn/newsList.aspx?TypeId=10010"
UA伪装 = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}
响应数据 = requests.get(url=网址,headers=UA伪装).text
解析 = etree.HTML(响应数据)
尾页 =解析.xpath('//a[text()="尾页"]/@href')

#尾页为空列表即只有一页
if 尾页 != []:
    正则 = re.search("(\\d+)",尾页[0])
    页数 = 正则.group(0)
else:
    页数 = 1