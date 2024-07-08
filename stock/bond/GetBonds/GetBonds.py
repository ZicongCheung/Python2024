import requests
import configparser
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading

class GetBonds(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GetBonds")
        width = 200
        height = 226
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = f'{width}x{height}+{(screenwidth - width) // 2}+{(screenheight - height) // 2}'
        self.geometry(geometry)
        self.resizable(width=False, height=False)

        # GitHub INI文件的raw链接
        self.url = 'https://github.com/ZicongCheung/Python2024/blob/main/stock/bond_winning_numbers.ini?raw=true'

        # 初始值
        self.winning_numbers = {}

        # 启动线程加载中签规则
        threading.Thread(target=self.load_winning_numbers).start()

        self.widget()

    def widget(self):
        self.label = ttk.Label(self, text="可转债简称", anchor="center")
        self.label.place(x=10, y=8, width=65, height=30)

        self.bonds_choose = ttk.Combobox(self, state="readonly")
        self.bonds_choose.set("请选择")
        self.bonds_choose.place(x=10, y=42, width=180, height=30)

        self.label = ttk.Label(self, text="初始配售号码", anchor="center")
        self.label.place(x=10, y=80, width=78, height=30)

        self.entry_start_number = ttk.Entry(self)
        self.entry_start_number.place(x=10, y=114, width=180, height=30)

        self.query_button = ttk.Button(self, text="查询", command=self.query)
        self.query_button.place(x=70, y=158, width=60, height=30)

    def query(self):
        # 在点击查询按钮时重新加载中签规则
        threading.Thread(target=self.load_winning_numbers_and_query).start()

    def load_winning_numbers_and_query(self):
        # 重新加载中签规则
        self.load_winning_numbers()

        # 读取用户输入的可转债名称和初始配售号码
        bond_name = self.bonds_choose.get()
        start_number = self.entry_start_number.get()

        # GUI线程中更新UI
        self.after(0, self.display_result, bond_name, start_number)

    def display_result(self, bond_name, start_number):
        if bond_name == "请选择" or not start_number.isdigit():
            messagebox.showerror("错误", "请输入有效的可转债名称和初始配售号码")
            return

        bond_winning_numbers = self.winning_numbers.get(bond_name)
        if not bond_winning_numbers:
            messagebox.showerror("错误", "未找到该可转债的中签规则")
            return

        start_number = int(start_number)
        count = 1000

        # 检查配号范围内是否中签
        winning_numbers_in_range = self.check_winning_range(start_number, count, bond_winning_numbers)

        if winning_numbers_in_range:
            messagebox.showinfo("查询结果", f"中签的配号: {winning_numbers_in_range}")
        else:
            messagebox.showinfo("查询结果", "未中签")

    def load_winning_numbers(self):
        try:
            # 发送HTTP请求获取INI文件内容
            response = requests.get(self.url)
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

            # 更新中签规则
            self.winning_numbers = winning_numbers

            # 更新可转债名称列表
            self.after(0, self.update_bonds_choose)

        except Exception as e:
            messagebox.showerror("错误", f"加载中签规则时出错: {e}")

    def update_bonds_choose(self):
        self.bonds_choose['values'] = list(self.winning_numbers.keys())

    def winning_number(self, winning_numbers, num):
        # 将输入的数字转换为字符串，以便进行尾部子串的检查
        num_str = str(num)
        for digits, winning_list in winning_numbers.items():
            # 提取输入数字的最后digits个字符作为子串
            num_suffix = num_str[-digits:]
            if num_suffix in winning_list:
                return True
        return False

    def check_winning_range(self, start_number, count, winning_numbers):
        winning_numbers_in_range = []
        for i in range(count):
            num = start_number + i
            if self.winning_number(winning_numbers, num):
                winning_numbers_in_range.append(num)
        return winning_numbers_in_range

if __name__ == "__main__":
    app = GetBonds()
    app.mainloop()
