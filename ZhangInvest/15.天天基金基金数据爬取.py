import json
import requests

fund_code = "011613"
url = f'http://fundgz.1234567.com.cn/js/{fund_code}.js'
response = requests.get(url)
data = response.text.replace('jsonpgz(', '').replace(');', '')
fund_data = json.loads(data)

fund_name = fund_data['name']
fund_nav_date = fund_data['jzrq']
fund_nav = fund_data['dwjz']
fund_estimated_nav = fund_data['gsz']
fund_estimated_growth_rate = fund_data['gszzl']
fund_estimated_nav_date = fund_data['gztime']
print(f'基金名称：{fund_name}，净值日期：{fund_nav_date}，单位净值：{fund_nav}，估算净值：{fund_estimated_nav}，估算增长率：{fund_estimated_growth_rate}，估算净值日期：{fund_estimated_nav_date}')
