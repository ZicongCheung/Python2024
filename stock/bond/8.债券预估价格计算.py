import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import configparser

class GetBonds(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GetBonds")
        self.geometry(f'320x200+{(self.winfo_screenwidth() - 200) // 2}+{(self.winfo_screenheight() - 320) // 2}')
        self.resizable(width=False, height=False)
        # 当前软件版本
        self.software_version = "1.0.0"

        # 初始可转债数据为空
        self.ths_bonds_data = {}
        self.bonds_premium_rate = {}
        self.df_bonds_data = {}

        threading.Thread(target=self.load_config_and_bonds_data).start()

        self.create_widgets()

    def load_config_and_bonds_data(self):
        self.load_config()
        self.load_bonds_data_from_thsapi()
        self.load_github_bonds_data()
        self.load_bonds_data_from_dfapi()

    def create_widgets(self):
        ttk.Label(self, text="债券简称", anchor="center").place(x=10, y=8, width=56, height=30)

        self.bonds_choose = ttk.Combobox(self, state="readonly")
        self.bonds_choose.set("数据加载中…")
        self.bonds_choose.place(x=10, y=42, width=100, height=30)
        self.bonds_choose.bind("<<ComboboxSelected>>", self.update_bond_details)

        ttk.Label(self, text="预估价格", anchor="center").place(x=110, y=8, width=42, height=30)
        self.estimated_price = ttk.Entry(self, state='disabled')
        self.estimated_price.place(x=110, y=42, width=100, height=30)

    def load_config(self):
        try:
            # GitHub配置URL
            config_url = 'https://github.com/ZicongCheung/Python2024/blob/main/stock/bond/GetBonds/config.ini?raw=true'
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
            self.destroy()

    def get_latest_bonds(self):
        # 同花顺债券API接口
        ths_bonds_data_api = 'https://data.10jqka.com.cn/ipo/kzz/'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}
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
            # GitHub债券数据URL
            bonds_data_url = 'https://github.com/ZicongCheung/Python2024/blob/main/stock/bond/GetBonds/bonds_data.ini?raw=true'
            response = requests.get(bonds_data_url)
            bonds_data_content = response.text

            config = configparser.ConfigParser()
            config.read_string(bonds_data_content)

            # 解析bonds_data.ini文件中的数据
            self.bonds_premium_rate = {}
            for section in config.sections():
                # 将读取的字符串转换为浮点数
                premium_rate = float(config.get(section, 'bonds_premium_rate', fallback='0'))
                self.bonds_premium_rate[section] = premium_rate

        except Exception as e:
            messagebox.showerror("错误", f"加载GitHub债券数据时出错: {e}")

    def load_bonds_data_from_dfapi(self):
        try:
            # 东方财富债券API接口
            df_bonds_data_api = f'https://datacenter-web.eastmoney.com/api/data/v1/get?&sortColumns=PUBLIC_START_DATE,SECURITY_CODE&sortTypes=-1,-1&pageSize={self.bond_count}&pageNumber=1&reportName=RPT_BOND_CB_LIST&columns=ALL&quoteColumns=f236~10~SECURITY_CODE~TRANSFER_VALUE'
            response = requests.get(df_bonds_data_api)
            data = response.json()
            self.df_bonds_data = data['result']['data']
        except Exception as e:
            messagebox.showerror("错误", f"加载东方财富债券数据时出错: {e}")

    def update_bonds_choose(self):
        self.bonds_choose.set("请选择")
        self.bonds_choose['values'] = list(self.ths_bonds_data.keys())

    def update_bond_details(self, event):
        selected_bond = self.bonds_choose.get()
        if selected_bond in self.bonds_premium_rate:
            premium_rate = self.bonds_premium_rate[selected_bond]
            try:
                transfer_value = next(item['TRANSFER_VALUE'] for item in self.df_bonds_data if
                                      item['SECURITY_NAME_ABBR'] == selected_bond)

                estimated_price = transfer_value * (1 + premium_rate)
                self.estimated_price.config(state='normal')
                self.estimated_price.delete(0, tk.END)
                self.estimated_price.insert(0, str(round(estimated_price, 2)))
                self.estimated_price.config(state='disabled')
            except StopIteration:
                self.estimated_price.config(state='normal')
                self.estimated_price.delete(0, tk.END)
                self.estimated_price.insert(0, "数据暂无")
                self.estimated_price.config(state='disabled')
        else:
            self.estimated_price.config(state='normal')
            self.estimated_price.delete(0, tk.END)
            self.estimated_price.insert(0, "未录入溢价率…")
            self.estimated_price.config(state='disabled')

if __name__ == "__main__":
    app = GetBonds()
    app.mainloop()