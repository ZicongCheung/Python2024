import requests
from lxml import etree
import os
if not os.path.exists('C:/Users/zhangzicong/Desktop/财务资料'):
    os.mkdir('C:/Users/zhangzicong/Desktop/财务资料')
UA伪装 = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}

keys = [] #为了后续每个文件名对应正确的文件，新建列表
value = []

for 页码 in range(1,4):
    网址 = 'https://www.jkl.com.cn/newsList.aspx?current=' +str(页码) + '&TypeId=10009'
    响应数据 = requests.get(url=网址, headers=UA伪装).text
    解析 = etree.HTML(响应数据)
    文件链接 = 解析.xpath('//div[@class="newsLis"]//li//@href')
    文件名称 = 解析.xpath('//div[@class="newsLis"]//li/a/text()')
    for 名称 in 文件名称:
        名称 = 名称.strip()
        keys.append(名称) #追加数据至对应列表
    for 链接 in 文件链接:
        链接 = 'https://www.jkl.com.cn' + 链接
        value.append(链接) #追加数据至对应列表
字典 = dict(zip(keys,value))
for 键, 值 in 字典.items():
    文件类型 = 值.split('.')[-1]
    文件数据 = requests.get(url=值, headers=UA伪装).content
    文件路径 = 'C:/Users/zhangzicong/Desktop/财务资料/' + 键 + '.' + 文件类型
    with open(文件路径,'wb') as 变量名:
        变量名.write(文件数据)
        print(键,'下载成功！！！！！')