import requests
import configparser
import tkinter as tk
from tkinter import ttk,  messagebox
import threading


class GetBonds(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GetBonds")
        self.geometry(f'320x200+{(self.winfo_screenwidth() - 200) // 2}+{(self.winfo_screenheight() - 320) // 2}')
        self.resizable(width=False, height=False)

        # GitHub INI文件的raw链接
        self.url = 'https://github.com/ZicongCheung/Python2024/blob/main/stock/bond/GetBonds/bond_winning_numbers.ini?raw=true'

        # 初始中签规则为空
        self.winning_numbers = {}

        # 启动线程加载中签规则
        threading.Thread(target=self.load_winning_numbers_from_github, args=(self.url,)).start()

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="债券简称", anchor="center").place(x=10, y=8, width=56, height=30)

        self.bonds_choose = ttk.Combobox(self, state="readonly")
        self.bonds_choose.set("请选择")
        self.bonds_choose.place(x=10, y=42, width=100, height=30)

        ttk.Label(self, text="发行量", anchor="center").place(x=110, y=8, width=42, height=30)
        self.circulation = ttk.Entry(self)
        self.circulation.place(x=110, y=42, width=100, height=30)

        ttk.Label(self, text="中签率", anchor="center").place(x=210, y=8, width=42, height=30)
        self.success_rate = ttk.Entry(self)
        self.success_rate.place(x=210, y=42, width=100, height=30)

        ttk.Label(self, text="预估价格", anchor="center").place(x=10, y=80, width=56, height=30)
        self.estimated_price = ttk.Entry(self)
        self.estimated_price.place(x=10, y=114, width=100, height=30)

        ttk.Label(self, text="初始配售号码", anchor="center").place(x=110, y=80, width=78, height=30)

        self.entry_start_number = ttk.Entry(self)
        self.entry_start_number.place(x=110, y=114, width=200, height=30)


        ttk.Button(self, text="查询", command=self.query).place(x=130, y=158, width=60, height=30)

    def query(self):
        bond_name = self.bonds_choose.get()
        start_number = self.entry_start_number.get()

        if bond_name == "请选择" or not start_number.isdigit():
            messagebox.showerror("错误", "请输入有效的可转债名称和初始配售号码")
            return

        bond_winning_numbers = self.winning_numbers.get(bond_name, {})
        start_number = int(start_number)
        count = 1000

        # 检查配号范围内是否中签
        winning_numbers_in_range = self.check_winning_range(start_number, count, bond_winning_numbers)

        if winning_numbers_in_range:
            messagebox.showinfo("查询结果", f"中签的配号: {winning_numbers_in_range}")
        else:
            messagebox.showinfo("查询结果", "未中签")

    def load_winning_numbers_from_github(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()

            config = configparser.ConfigParser()
            config.read_string(response.text)

            winning_numbers = {
                section: {int(key): set(value.split(',')) for key, value in config.items(section)}
                for section in config.sections()
            }

            self.winning_numbers = winning_numbers

            self.after(0, self.update_bonds_choose)
        except Exception as e:
            messagebox.showerror("错误", f"加载中签规则时出错: {e}")

    def update_bonds_choose(self):
        self.bonds_choose['values'] = list(self.winning_numbers.keys())

    def winning_number(self, winning_numbers, num):
        num_str = str(num)
        return any(num_str[-digits:] in winning_list for digits, winning_list in winning_numbers.items())

    def check_winning_range(self, start_number, count, winning_numbers):
        return [start_number + i for i in range(count) if self.winning_number(winning_numbers, start_number + i)]


if __name__ == "__main__":
    app = GetBonds()
    app.mainloop()
