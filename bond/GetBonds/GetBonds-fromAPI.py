import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox
from io import BytesIO
from PIL import Image, ImageTk
import threading
import configparser

class GetBonds(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GetBonds")
        self.geometry(f'320x200+{(self.winfo_screenwidth() - 200) // 2}+{(self.winfo_screenheight() - 320) // 2}')
        self.resizable(width=False, height=False)
        self.load_icon()
        # 当前软件版本
        self.software_version = "1.0.0"

        # 初始可转债数据为空
        self.ths_bonds_data = {}
        self.bonds_premium_rate = {}
        self.df_bonds_data = {}
        # 启动线程加载配置文件和可转债数据
        threading.Thread(target=self.load_config_and_bonds_data).start()

        self.create_widgets()

    def load_icon(self):
        # GiteeIconURL
        icon_url = "https://gitee.com/ZicongCheung/Python2024/raw/main/bond/GetBonds/GetBondsLogo.ico"
        response = requests.get(icon_url)
        if response.status_code == 200:
            image_data = response.content
            image = Image.open(BytesIO(image_data))
            icon = ImageTk.PhotoImage(image)
            self.iconphoto(False, icon)

    def create_widgets(self):
        ttk.Label(self, text="债券简称", anchor="center").place(x=10, y=8, width=56, height=30)

        self.bonds_choose = ttk.Combobox(self, state="readonly")
        self.bonds_choose.set("数据加载中…")
        self.bonds_choose.place(x=10, y=42, width=100, height=30)
        self.bonds_choose.bind("<<ComboboxSelected>>", self.update_bond_details)

        ttk.Label(self, text="发行量", anchor="center").place(x=110, y=8, width=42, height=30)
        self.circulation = ttk.Entry(self, state='disabled')
        self.circulation.place(x=110, y=42, width=100, height=30)

        ttk.Label(self, text="中签率", anchor="center").place(x=210, y=8, width=42, height=30)
        self.success_rate = ttk.Entry(self, state='disabled')
        self.success_rate.place(x=210, y=42, width=100, height=30)

        ttk.Label(self, text="上市首日估价", anchor="center").place(x=10, y=80, width=78, height=30)
        self.estimated_price = ttk.Entry(self, state='disabled')
        self.estimated_price.place(x=10, y=114, width=100, height=30)

        ttk.Label(self, text="初始配售号码", anchor="center").place(x=110, y=80, width=78, height=30)
        self.entry_start_number = ttk.Entry(self)
        self.entry_start_number.place(x=110, y=114, width=200, height=30)

        ttk.Button(self, text="查询", command=self.query).place(x=130, y=158, width=60, height=30)

    def query(self):
        bond_name = self.bonds_choose.get()
        start_number = self.entry_start_number.get()

        if bond_name == "请选择":
            messagebox.showerror("错误", "请选择债券")
            return

        if not start_number.isdigit():
            messagebox.showerror("错误", "请输入初始配售号码")
            return

        ths_bonds_data = self.ths_bonds_data.get(bond_name, {})
        bond_winning_numbers = ths_bonds_data.get('winning_numbers', {})

        # 检查是否有中签号码
        if not bond_winning_numbers:
            messagebox.showinfo("提示", "当前中签结果未公布")
            return

        start_number = int(start_number)
        count = 1000

        # 检查配号范围内是否中签
        winning_numbers_in_range = self.check_winning_range(start_number, count, bond_winning_numbers)

        if winning_numbers_in_range:
            messagebox.showinfo("查询结果", f"中签啦！中签配号为: {winning_numbers_in_range}")
        else:
            messagebox.showinfo("查询结果", "未中签")

    def load_config_and_bonds_data(self):
        self.load_config()
        self.load_bonds_data_from_thsapi()
        self.load_github_bonds_data()
        # self.load_bonds_data_from_dfapi()

    def load_config(self):
        try:
            # Gitee配置URL
            config_url = 'https://gitee.com/ZicongCheung/Python2024/raw/main/bond/GetBonds/config.ini'
            response = requests.get(config_url)
            config_content = response.text

            config = configparser.ConfigParser()
            config.read_string(config_content)

            maintenance_status = config.get('GetBondsConfig', 'maintenance_status', fallback='off')
            software_version = config.get('GetBondsConfig', 'software_version', fallback='1.0.0')
            self.bond_count = int(config.get('GetBondsConfig', 'bond_count', fallback='10'))

            if maintenance_status.lower() == 'on':
                messagebox.showinfo("维护状态", "GetBonds处于维护状态中，具体恢复时间请咨询小张")
                self.quit()
                return

            if software_version != self.software_version:
                messagebox.showinfo("版本过低", "当前版本过低，请升级")
                self.quit()
                return

        except Exception as e:
            messagebox.showerror("错误", f"加载配置文件时出错: {e}")
            self.quit()

    def get_latest_bonds(self):
        # 同花顺债券API接口
        ths_bonds_data_api = 'https://data.10jqka.com.cn/ipo/kzz/'
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}
        response = requests.get(ths_bonds_data_api, headers=headers)
        data = json.loads(response.text)
        bond_list = data['list']
        latest_bonds = bond_list[:self.bond_count]
        return latest_bonds

    def load_bonds_data_from_thsapi(self):
        try:
            # 获取最新的可转债数据
            latest_bonds = self.get_latest_bonds()

            ths_bonds_data = {}

            # 提取债券名称、规模、中签率、中签配号末*位
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
                            bond_winning_numbers[length] = set(parts)
                ths_bonds_data[bond_name] = {
                    'plan_total': plan_total,
                    'success_rate': success_rate,
                    'winning_numbers': bond_winning_numbers
                }

            self.ths_bonds_data = ths_bonds_data

            self.after(0, self.update_bonds_choose)
        except Exception as e:
            messagebox.showerror("错误", f"加载债券信息时出错: {e}")

    def load_github_bonds_data(self):
        try:
            # Gitee债券数据URL
            bonds_data_url = 'https://gitee.com/ZicongCheung/Python2024/raw/main/bond/GetBonds/bonds_data.ini'
            response = requests.get(bonds_data_url)
            bonds_data_content = response.text

            config = configparser.ConfigParser()
            config.read_string(bonds_data_content)

            # 解析bonds_data.ini文件中的数据
            self.bonds_estimated_price = {}
            for section in config.sections():
                estimated_price = config.get(section, 'bonds_estimated_price', fallback='0')
                self.bonds_estimated_price[section] = estimated_price

        except Exception as e:
            messagebox.showerror("错误", f"加载债券数据时出错: {e}")

    # def load_bonds_data_from_dfapi(self):
    #     try:
    #         # 东方财富债券API接口
    #         df_bonds_data_api = f'https://datacenter-web.eastmoney.com/api/data/v1/get?&sortColumns=PUBLIC_START_DATE,SECURITY_CODE&sortTypes=-1,-1&pageSize={self.bond_count}&pageNumber=1&reportName=RPT_BOND_CB_LIST&columns=ALL&quoteColumns=f236~10~SECURITY_CODE~TRANSFER_VALUE'
    #         response = requests.get(df_bonds_data_api)
    #         data = response.json()
    #         self.df_bonds_data = data['result']['data']
    #     except Exception as e:
    #         messagebox.showerror("错误", f"加载债券数据时出错: {e}")

    def update_bonds_choose(self):
        self.bonds_choose.set("请选择")
        self.bonds_choose['values'] = list(self.ths_bonds_data.keys())

    def update_bond_details(self, event):
        bond_name = self.bonds_choose.get()
        if bond_name in self.ths_bonds_data:
            ths_bond_detail = self.ths_bonds_data[bond_name]

            # 显示发行量，保留两位小数并加上“亿”
            plan_total = float(ths_bond_detail['plan_total'])
            self.circulation.config(state='normal')
            self.circulation.delete(0, tk.END)
            self.circulation.insert(0, f"{plan_total:.2f}亿")
            self.circulation.config(state='disabled')

            # 显示中签率，保留两位小数并加上“%”
            success_rate = float(ths_bond_detail['success_rate'])
            self.success_rate.config(state='normal')
            self.success_rate.delete(0, tk.END)
            if success_rate == 0.0:
                self.success_rate.insert(0, "中签结果未公布")
            else:
                per_100 = success_rate * 1000
                self.success_rate.insert(0, f"{per_100:.2f}%")
            self.success_rate.config(state='disabled')

        if bond_name in self.bonds_estimated_price:
            estimated_price = self.bonds_estimated_price[bond_name]
            self.estimated_price.config(state='normal')
            self.estimated_price.delete(0, tk.END)
            self.estimated_price.insert(0, f"{estimated_price}元")
        else:
            self.estimated_price.config(state='normal')
            self.estimated_price.delete(0, tk.END)
            self.estimated_price.insert(0, "数据暂无…")
        self.estimated_price.config(state='disabled')

    def winning_number(self, winning_numbers, num):
        num_str = str(num)
        return any(num_str[-digits:] in winning_list for digits, winning_list in winning_numbers.items())

    def check_winning_range(self, start_number, count, winning_numbers):
        return [start_number + i for i in range(count) if self.winning_number(winning_numbers, start_number + i)]

if __name__ == "__main__":
    app = GetBonds()
    app.mainloop()