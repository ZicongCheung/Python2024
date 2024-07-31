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


def main():
    # 中签规则
    winning_numbers = {
        4: {'3185', '8185', '5592'},
        5: {'24401', '74401'},
        6: {'892672', '767672', '642672', '517672', '392672', '267672', '142672', '017672', '744757'},
        7: {'6748788', '1748788'},
        8: {'36101530'},
        9: {'964174224', '764174224', '564174224', '364174224', '164174224', '880330919', '380330919'},
        10: {'3532550723', '1400801871', '5410860735', '4756764259'}
    }

    # 你的配号起始值和数量
    start_number = 102110022342
    count = 1000

    # 检查配号范围内是否中签
    winning_numbers_in_range = check_winning_range(start_number, count, winning_numbers)

    if winning_numbers_in_range:
        print(f"中签的配号: {winning_numbers_in_range}")
    else:
        print("未中签")


if __name__ == "__main__":
    main()
