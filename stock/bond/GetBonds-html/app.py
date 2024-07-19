from flask import Flask, render_template, request, jsonify
import requests
import json
import configparser
from io import BytesIO

app = Flask(__name__)

# 当前软件版本
software_version = "1.0.0"

ths_bonds_data = {}
bonds_premium_rate = {}
df_bonds_data = {}


def load_config():
    config_url = 'https://gitee.com/ZicongCheung/Python2024/raw/main/stock/bond/GetBonds/config.ini'
    response = requests.get(config_url)
    config_content = response.text

    config = configparser.ConfigParser()
    config.read_string(config_content)

    maintenance_status = config.get('GetBondsConfig', 'maintenance_status', fallback='off')
    software_version = config.get('GetBondsConfig', 'software_version', fallback='1.0.0')
    bond_count = int(config.get('GetBondsConfig', 'bond_count', fallback='10'))

    if maintenance_status.lower() == 'on':
        return '维护状态'

    if software_version != software_version:
        return '版本过低'

    return bond_count


def get_latest_bonds():
    ths_bonds_data_api = 'https://data.10jqka.com.cn/ipo/kzz/'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}
    response = requests.get(ths_bonds_data_api, headers=headers)
    data = json.loads(response.text)
    bond_list = data['list']
    return bond_list


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_bonds', methods=['GET'])
def get_bonds():
    bond_count = load_config()
    if isinstance(bond_count, str):
        return jsonify({'error': bond_count})

    latest_bonds = get_latest_bonds()
    return jsonify({'bonds': latest_bonds[:bond_count]})


@app.route('/check_winning', methods=['POST'])
def check_winning():
    data = request.json
    bond_name = data.get('bond_name')
    start_number = data.get('start_number')

    if not bond_name or not start_number.isdigit():
        return jsonify({'error': '无效的请求'})

    start_number = int(start_number)
    ths_bonds_data = {}  # Get the actual bond data here

    bond_winning_numbers = ths_bonds_data.get(bond_name, {}).get('winning_numbers', {})
    if not bond_winning_numbers:
        return jsonify({'message': '当前中签结果未公布'})

    count = 1000
    winning_numbers_in_range = check_winning_range(start_number, count, bond_winning_numbers)
    if winning_numbers_in_range:
        return jsonify({'message': f'中签啦！中签配号为: {winning_numbers_in_range}'})
    else:
        return jsonify({'message': '未中签'})


def check_winning_range(start_number, count, winning_numbers):
    return [start_number + i for i in range(count) if winning_number(winning_numbers, start_number + i)]


def winning_number(winning_numbers, num):
    num_str = str(num)
    return any(num_str[-digits:] in winning_list for digits, winning_list in winning_numbers.items())


if __name__ == '__main__':
    app.run(debug=True)