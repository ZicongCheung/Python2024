import requests

# 获取东方财富债券信息
url = 'https://datacenter-web.eastmoney.com/api/data/v1/get?&sortColumns=PUBLIC_START_DATE,SECURITY_CODE&sortTypes=-1,-1&pageSize=2&pageNumber=1&reportName=RPT_BOND_CB_LIST&columns=ALL&quoteColumns=f236~10~SECURITY_CODE~TRANSFER_VALUE'
response = requests.get(url)
data = response.json()

# 提取SECURITY_NAME_ABBR债券名称和TRANSFER_VALUE转股价值
bonds = data['result']['data']


# 初始化存储每组数据的列表
all_bonds = []

# 提取每组数据中的变量
for bond in bonds:
    bond_data = [
        bond.get('SECURITY_NAME_ABBR', ''),
        bond.get('TRANSFER_VALUE', ''),
    ]
    all_bonds.append(bond_data)


for bond in all_bonds:
    print(bond)