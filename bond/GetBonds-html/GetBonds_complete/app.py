from flask import Flask, jsonify, request, render_template
import requests
import json
import configparser

app = Flask(__name__)

bonds_estimated_price = {}
ths_bonds_data = {}

@app.route('/')
def index():
    return render_template('index.html')

def load_config():
    config_url = 'https://gitee.com/ZicongCheung/Python2024/raw/main/bond/GetBonds/config.ini'
    response = requests.get(config_url)
    config_content = response.text
    config = configparser.ConfigParser()
    config.read_string(config_content)
    bond_count = int(config.get('GetBondsConfig', 'bond_count', fallback='10'))
    return bond_count

def get_latest_bonds():
    bond_count = load_config()
    ths_bonds_data_api = 'https://data.10jqka.com.cn/ipo/kzz/'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}
    response = requests.get(ths_bonds_data_api, headers=headers)
    data = json.loads(response.text)
    bond_list = data['list']
    latest_bonds = bond_list[:bond_count]
    return latest_bonds

@app.route('/load_bonds_data_from_thsapi', methods=['GET'])
def load_bonds_data_from_thsapi():
    latest_bonds = get_latest_bonds()
    for bond in latest_bonds:
        bond_name = bond.get('bond_name', '')
        plan_total = bond.get('plan_total', '')
        success_rate = bond.get('success_rate', '')
        numbers = bond.get('number', '').replace('\r\n', '')
        bond_winning_numbers = {}
        if numbers:
            # 按长度分组
            number_groups = numbers.split('；')
            for group in number_groups:
                group = group.strip()
                if group:
                    parts = group.split('、')
                    length = len(parts[0])
                    bond_winning_numbers[length] = list(set(parts))
        ths_bonds_data[bond_name] = {
            'plan_total': plan_total,
            'success_rate': success_rate,
            'winning_numbers': bond_winning_numbers
        }
    # 返回键值对列表供前端使用
    bonds_data = [{"bond_name": k, "plan_total": v["plan_total"], "success_rate": v["success_rate"], "winning_numbers": v["winning_numbers"]} for k, v in ths_bonds_data.items()]
    return jsonify(bonds_data)

@app.route('/load_github_bonds_data', methods=['GET'])
def load_github_bonds_data():
    # Gitee债券数据URL
    bonds_data_url = 'https://gitee.com/ZicongCheung/Python2024/raw/main/bond/GetBonds/bonds_data.ini'
    response = requests.get(bonds_data_url)
    bonds_data_content = response.text

    config = configparser.ConfigParser()
    config.read_string(bonds_data_content)

    # 解析bonds_data.ini文件中的数据
    global bonds_estimated_price
    bonds_estimated_price.clear()  # 清空旧数据
    for section in config.sections():
        estimated_price = config.get(section, 'bonds_estimated_price')
        bonds_estimated_price[section] = estimated_price
    return jsonify(bonds_estimated_price)

@app.route('/get_bond_details')
def get_bond_details():
    bond_name = request.args.get('bond_name')
    if bond_name in ths_bonds_data:
        bond_data = ths_bonds_data[bond_name]
        response_data = {
            'plan_total': bond_data['plan_total'],
            'success_rate': bond_data['success_rate'],
            'winning_numbers': bond_data['winning_numbers'],
        }
        if bond_name in bonds_estimated_price:
            response_data['estimated_price'] = bonds_estimated_price[bond_name]
        else:
            response_data['estimated_price'] = None
        return jsonify(response_data)
    elif bond_name in bonds_estimated_price:
        estimated_price = bonds_estimated_price[bond_name]
        return jsonify({
            'estimated_price': estimated_price,
        })
    else:
        return jsonify({'error': 'Bond not found'}), 404

def winning_number(winning_numbers, num):
    num_str = str(num)
    return any(num_str[-digits:] in winning_list for digits, winning_list in winning_numbers.items())

def check_winning_range(start_number, count, winning_numbers):
    return [start_number + i for i in range(count) if winning_number(winning_numbers, start_number + i)]

if __name__ == '__main__':
    load_github_bonds_data()  # 加载债券数据
    app.run(debug=True)