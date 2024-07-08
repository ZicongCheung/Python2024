import requests
import configparser

def winning_number(winning_numbers, num):
    # 将输入的数字转换为字符串，以便进行尾部子串的检查
    num_str = str(num)
    for digits, winning_list in winning_numbers.items():
        # 提取输入数字的最后digits个字符作为子串
        num_suffix = num_str[-digits:]
        if num_suffix in winning_list:
            return True
    return False


def check_winning_range(start_number, count, winning_numbers):
    winning_numbers_in_range = []
    for i in range(count):
        num = start_number + i
        if winning_number(winning_numbers, num):
            winning_numbers_in_range.append(num)
    return winning_numbers_in_range


def load_winning_numbers_from_github(url):
    # 发送HTTP请求获取INI文件内容
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功

    # 将文件内容转换为字符串
    ini_content = response.text

    # 使用configparser读取INI内容
    config = configparser.ConfigParser()
    config.read_string(ini_content)

    # 转换为所需格式
    winning_numbers = {}
    for section in config.sections():
        winning_numbers[section] = {int(key): set(value.split(',')) for key, value in config.items(section)}

    return winning_numbers


def main():
    # 在 GitHub URL 末尾添加 ?raw=true 以获取原始文件链接
    url = 'https://github.com/ZicongCheung/Python2024/blob/main/stock/bond_winning_numbers.ini?raw=true'

    # 加载中签规则
    winning_numbers = load_winning_numbers_from_github(url)

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