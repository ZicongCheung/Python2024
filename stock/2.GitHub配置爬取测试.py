import requests
import configparser

# GitHub raw链接
url = 'https://raw.githubusercontent.com/username/repository/branch/config.ini'

# 发送HTTP请求获取INI文件内容
response = requests.get(url)
response.raise_for_status()  # 检查请求是否成功

# 将文件内容转换为字符串
ini_content = response.text

# 使用configparser读取INI内容
config = configparser.ConfigParser()
config.read_string(ini_content)

# 打印读取到的内容
for section in config.sections():
    print(f'Section: {section}')
    for key, value in config.items(section):
        print(f'{key} = {value}')
