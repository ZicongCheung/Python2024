import requests
import json

# 获取数据的函数
def get_latest_bonds(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    bond_list = data['list']
    latest_bonds = bond_list[:10]
    return latest_bonds

# 检查是否中签的函数
def winning_number(winning_numbers, num):
    num_str = str(num)
    for digits, winning_list in winning_numbers.items():
        num_suffix = num_str[-digits:]
        if num_suffix in winning_list:
            return True
    return False

# 检查配号范围是否中签的函数
def check_winning_range(start_number, count, winning_numbers):
    winning_numbers_in_range = []
    for i in range(count):
        num = start_number + i
        if winning_number(winning_numbers, num):
            winning_numbers_in_range.append(num)
    return winning_numbers_in_range

# 主函数
def main():
    # 获取最新的可转债数据
    url = 'https://data.10jqka.com.cn/ipo/kzz/'
    latest_bonds = get_latest_bonds(url)

    # 将最新的可转债数据转化为中签规则格式
    winning_numbers = {}
    for bond in latest_bonds:
        bond_name = bond.get('bond_name', '')
        numbers = bond.get('number', '').replace('\r\n', '')
        if numbers:
            # 按长度分组
            number_groups = numbers.split('；')
            bond_winning_numbers = {}
            for group in number_groups:
                group = group.strip()
                if group:
                    parts = group.split('、')
                    length = len(parts[0])
                    bond_winning_numbers[length] = set(parts)
            winning_numbers[bond_name] = bond_winning_numbers

    # 获取用户输入的可转债名称和配号范围
    bond_name = input("请输入可转债名称: ")
    start_number = int(input("请输入配号起始值: "))
    count = int(input("请输入配号数量: "))

    if bond_name in winning_numbers:
        bond_winning_numbers = winning_numbers[bond_name]
    else:
        print(f"未找到名为{bond_name}的中签规则")
        return

    # 检查配号范围内是否中签
    winning_numbers_in_range = check_winning_range(start_number, count, bond_winning_numbers)

    if winning_numbers_in_range:
        print(f"中签的配号: {winning_numbers_in_range}")
    else:
        print("未中签")

if __name__ == "__main__":
    main()
