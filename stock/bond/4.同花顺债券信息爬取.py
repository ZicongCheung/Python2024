import requests
import json

url = 'https://data.10jqka.com.cn/ipo/kzz/'
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}
response = requests.get(url, headers=headers)
data = json.loads(response.text)
# 获取list中前10组数据
bond_list = data['list']
latest_bonds = bond_list[:10]
# 提取bond_code, bond_name, plan_total, success_rate, number
for bond in latest_bonds:
    bond_code = bond['bond_code']
    bond_name = bond['bond_name']
    plan_total = bond['plan_total']
    success_rate = bond['success_rate']
    number = bond['number']
    print(f"bond_code: {bond_code}, bond_name: {bond_name}, plan_total: {plan_total}, success_rate: {success_rate}, number: {number}")