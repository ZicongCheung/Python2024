import re
from db_operations import *

# 显示基金列表
def display_fund_list():
    funds = fetch_all_funds()
    if not funds:
        print("数据库不存在基金信息，请回车以录入基金信息：")
        input()
        return None
    print("\n当前基金信息列表：")
    for i, (fund_code, fund_name, is_domestic) in enumerate(funds):
        domestic_type = "境内" if is_domestic == 'Y' else "境外"
        print(f"{i + 1}. {fund_code} {fund_name} ({domestic_type})")
    return funds

# 验证基金代码
def is_valid_fund_code(fund_code):
    return fund_code.isdigit() and len(fund_code) == 6

# 录入基金信息
def add_fund():
    while True:
        fund_code = input("请输入6位基金代码并回车：")
        if not is_valid_fund_code(fund_code):
            print("基金代码错误，请重新输入。")
            continue
        fund_name = input("请输入基金名称并回车：")
        is_domestic = input("请输入基金类型（Y: 境内, N: 境外）：").upper()
        if is_domestic not in ['Y', 'N']:
            print("基金类型错误，请输入 'Y' 或 'N'")
            continue
        insert_fund(fund_code, fund_name, is_domestic)
        print(f"基金 {fund_code} - {fund_name} ({'境内' if is_domestic == 'Y' else '境外'}) 已成功录入。")
        break

# 删除基金信息
def remove_fund_action(funds):
    while True:
        try:
            choice = int(input("\n请输入序号以删除基金，或按回车退出删除操作："))
            if choice < 1 or choice > len(funds):
                print("无效选择，请重新输入。")
                continue
            fund_code, fund_name, _ = funds[choice - 1]
            remove_fund(fund_code)
            print(f"基金 {fund_code} - {fund_name} 已成功删除。")
            break
        except ValueError:
            print("输入无效，退出删除操作。")
            break

# 显示基金的交易记录
def display_transactions(fund_code):
    transactions = fetch_transactions_by_fund(fund_code)
    if not transactions:
        print(f"基金 {fund_code} 没有交易记录。")
        return

    print(f"\n基金 {fund_code} 的交易记录如下：")
    for transaction_time, transaction_type, transaction_amount, confirmed_shares, transaction_fee in transactions:
        shares = f", 确认份额: {confirmed_shares}" if confirmed_shares is not None else ""
        fee = f", 交易费用: {transaction_fee}" if transaction_fee is not None else ""
        print(f"{transaction_time} {transaction_type} 金额: {transaction_amount}{shares}{fee}")

# 录入交易记录
def add_transaction(fund_code):
    transaction_info = input("请输入新的交易记录（格式：YYYY-MM-DD HH:MM:SS 买入/卖出/定投/转换 金额）：")
    try:
        # 使用正则表达式匹配输入格式
        match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (买入|卖出|定投|转换) ([+-]?\d*\.\d+|\d+)', transaction_info)
        if not match:
            raise ValueError("输入格式错误")

        transaction_time, transaction_type, transaction_amount_str = match.groups()
        transaction_amount = float(transaction_amount_str)

        confirmed_shares = input("请输入确认份额（可选，直接回车跳过）：")
        confirmed_shares = float(confirmed_shares) if confirmed_shares else None

        transaction_fee = input("请输入交易费用（可选，直接回车跳过）：")
        transaction_fee = float(transaction_fee) if transaction_fee else None

        insert_transaction(fund_code, transaction_type, transaction_time, transaction_amount, confirmed_shares, transaction_fee)
        print("交易记录已成功录入。")
    except ValueError as e:
        print(f"输入格式错误：{e}. 请重新输入。")

# 删除交易记录
def remove_transaction(fund_code):
    transaction_info = input("请输入删除的交易记录（格式：YYYY-MM-DD HH:MM:SS 买入/卖出/定投/转换 金额）：")
    try:
        transaction_time, transaction_type, transaction_amount = transaction_info.split()
        transaction_amount = float(transaction_amount)
        delete_transaction(fund_code, transaction_time, transaction_type, transaction_amount)
        print("交易记录已成功删除。")
    except ValueError:
        print("输入格式错误，请重新输入。")

def main():
    while True:
        funds = display_fund_list()
        if funds is None:
            add_fund()
            continue

        print("\n0. 录入或删除基金信息")
        try:
            choice = int(input("\n请输入序号查看基金交易记录，或输入0进行基金信息录入/删除："))
        except ValueError:
            print("无效输入，请重新输入。")
            continue

        if choice == 0:
            print("\n0. 添加新基金")
            print("1. 删除已有基金")
            sub_choice = input("请选择操作：")
            if sub_choice == "0":
                add_fund()
            elif sub_choice == "1":
                remove_fund_action(funds)
        elif 1 <= choice <= len(funds):
            fund_code, fund_name, _ = funds[choice - 1]
            display_transactions(fund_code)
            transaction_action(fund_code)
        else:
            print("无效选择，请重新选择。")

def transaction_action(fund_code):
    print("\n0：返回；1. 增加交易记录；2. 删除交易记录")
    try:
        action = int(input())
        if action == 1:
            add_transaction(fund_code)
        elif action == 2:
            remove_transaction(fund_code)
    except ValueError:
        print("无效选择。")

if __name__ == "__main__":
    main()