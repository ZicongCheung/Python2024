import requests
import json

# 获取数据
url = 'https://data.10jqka.com.cn/ipo/kzz/'
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}
response = requests.get(url, headers=headers)
data = json.loads(response.text)

# 获取list中前10组数据
bond_list = data['list']
latest_bonds = bond_list[:10]

# 初始化存储每组数据的列表
all_bonds = []

# 提取每组数据中的变量
for bond in latest_bonds:
    bond_data = [
        bond.get('bond_name', ''),
        bond.get('plan_total', ''),
        bond.get('success_rate', ''),
        bond.get('number', '').replace('\r\n', '')
    ]
    all_bonds.append(bond_data)

# 输出结果
for bond in all_bonds:
    print(bond)
