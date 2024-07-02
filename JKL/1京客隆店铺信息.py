import requests
from lxml import etree
import pandas as pd

网址 = "https://www.jkl.com.cn/shop.aspx"
UA伪装 = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}

# 拿取每个城区网址
响应数据 = requests.get(url=网址,headers=UA伪装).text
解析 = etree.HTML(响应数据)
城区 = 解析.xpath('//div[@class="infoLis"]//@href')
for 区 in 城区:
    网址1 = 'https://www.jkl.com.cn/' + 区
    响应数据1 = requests.get(url=网址1,headers=UA伪装).text
    解析1 = etree.HTML(响应数据1)
    店铺名称 = 解析1.xpath('//span[@class="con01"]/text()')
    详细地址 = 解析1.xpath('//span[@class="con02"]/text()')
    电话号码 = 解析1.xpath('//span[@class="con03"]/text()')
    营业时间 = 解析1.xpath('//span[@class="con04"]/text()')
    列表 = []
    for 店名 in 店铺名称:
        店铺名称新 = 店名.strip()
        列表.append(店铺名称新)
    数据 = pd.DataFrame({'店名':列表,'地址':详细地址,'电话':电话号码,'时间':营业时间})
    数据.to_csv('C:/Users/zhangzicong/Desktop/店铺信息.csv',index=False,header=0,mode='a',encoding='ANSI')
    if 网址1 == 'https://www.jkl.com.cn/shopLis.aspx?TypeId=10045':
        for 页码 in range(2, 4):
            网址2 = 'https://www.jkl.com.cn/shopLis.aspx?current=' + str(页码) + '&TypeId=10045'
            响应数据2 = requests.get(url=网址2, headers=UA伪装).text
            解析2 = etree.HTML(响应数据2)
            店铺名称 = 解析2.xpath('//span[@class="con01"]/text()')
            详细地址 = 解析2.xpath('//span[@class="con02"]/text()')
            电话号码 = 解析2.xpath('//span[@class="con03"]/text()')
            营业时间 = 解析2.xpath('//span[@class="con04"]/text()')
            列表 = []
            for 店名 in 店铺名称:
                店铺名称新 = 店名.strip()
                列表.append(店铺名称新)
            数据 = pd.DataFrame({'店名': 列表, '地址': 详细地址, '电话': 电话号码, '时间': 营业时间})
            数据.to_csv('C:/Users/zhangzicong/Desktop/店铺信息.csv', index=False, header=0, mode='a', encoding='ANSI')