from flask import Flask, jsonify, request, render_template
import requests
import json
import configparser

app = Flask(__name__)

ths_bonds_data = {}

@app.route('/')
def index():
    return render_template('index.html')

def load_config():
    config_url = 'https://gitee.com/ZicongCheung/WebAPP/raw/main/GetBonds/config_files/config.ini'
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
        ths_bonds_data[bond_name] = {
            'plan_total': plan_total,
            'success_rate': success_rate
        }
    # 返回键值对列表供前端使用
    bonds_data = [{"bond_name": k, **v} for k, v in ths_bonds_data.items()]
    return jsonify(bonds_data)

@app.route('/get_bond_details')
def get_bond_details():
    bond_name = request.args.get('bond_name')
    if bond_name in ths_bonds_data:
        bond_data = ths_bonds_data[bond_name]
        return jsonify({
            'plan_total': bond_data['plan_total'],
            'success_rate': bond_data['success_rate'],
        })
    else:
        return jsonify({'error': 'Bond not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)