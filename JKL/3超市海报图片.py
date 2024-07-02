import requests
from lxml import etree

# 假如不存在‘海报’文件夹，便新建它
import os
if not os.path.exists('C:/Users/zhangzicong/Desktop/海报'):
    os.mkdir('C:/Users/zhangzicong/Desktop/海报')

网址 = "https://www.jkl.com.cn/phoLis.aspx"
UA伪装 = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}

# 拿取每张海报链接
响应数据 = requests.get(url=网址,headers=UA伪装).text
解析 = etree.HTML(响应数据)
海报链接 = 解析.xpath('//div[@class="proLis"]//@src')
for 链接 in 海报链接:
    网址1 = 'https://www.jkl.com.cn' + 链接
    海报数据 = requests.get(url=网址1,headers=UA伪装).content
    海报名称 = 网址1.split('/')[-1]
    海报路径 = 'C:/Users/zhangzicong/Desktop/海报/' + 海报名称
    with open(海报路径,'wb') as 变量名:
        变量名.write(海报数据)
        print(海报名称,'下载成功！！！！！')