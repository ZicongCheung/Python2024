import concurrent.futures
import os
import requests
from lxml import etree
import re
import random
import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
import configparser
import queue
import threading
import io
class ZickNovel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ZickNovel")
        width = 260
        height = 291
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = f'{width}x{height}+{(screenwidth - width) // 2}+{(screenheight - height) // 2}'
        self.geometry(geometry)
        self.resizable(width=False, height=False)
        self.widget()
        self.progress_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(self, variable=self.progress_var)
        self.progressbar.place(x=2, y=258, width=256, height=30)
        self.completed_tasks = 0  # 追踪完成的任务数
        self.update_queue = queue.Queue()  # 创建队列用于跨线程通信
        self.queue_monitor_id = None  # 用于存储after的返回ID以便取消
        self.booksource_file_name = "BookSource.ini"
        self.booksource_parser = configparser.ConfigParser()

    def widget(self):
        self.label = ttk.Label(self, text="小说主页链接:", anchor="center", )
        self.label.place(x=0, y=2, width=94, height=30)
        self.entry_novel_home_url = ttk.Entry(self)
        self.entry_novel_home_url.place(x=96, y=2, width=162, height=30)

        self.label = ttk.Label(self, text="小说列表页链接:", anchor="center", )
        self.label.place(x=0, y=34, width=94, height=30)
        self.entry_novel_list_url = ttk.Entry(self)
        self.entry_novel_list_url.place(x=96, y=34, width=162, height=30)

        self.label = ttk.Label(self, text="小说名称XPath:", anchor="center", )
        self.label.place(x=0, y=66, width=94, height=30)
        self.entry_novel_name_xpath = ttk.Entry(self)
        self.entry_novel_name_xpath.place(x=96, y=66, width=162, height=30)

        self.label = ttk.Label(self, text="章节标题XPath:", anchor="center", )
        self.label.place(x=0, y=98, width=94, height=30)
        self.entry_chapter_title_xpath = ttk.Entry(self)
        self.entry_chapter_title_xpath.place(x=96, y=98, width=162, height=30)

        self.label = ttk.Label(self, text="章节网址XPath:", anchor="center", )
        self.label.place(x=0, y=130, width=94, height=30)
        self.entry_chapter_url_xpath = ttk.Entry(self)
        self.entry_chapter_url_xpath.place(x=96, y=130, width=162, height=30)

        self.label = ttk.Label(self, text="章节内容XPath:", anchor="center", )
        self.label.place(x=0, y=162, width=94, height=30)
        self.entry_chapter_content_xpath = ttk.Entry(self)
        self.entry_chapter_content_xpath.place(x=96, y=162, width=162, height=30)

        self.label = ttk.Label(self, text="下载线程数:", anchor="center", )
        self.label.place(x=0, y=194, width=94, height=30)
        self.entry_concurrent_requests = ttk.Entry(self)
        self.entry_concurrent_requests.place(x=96, y=194, width=102, height=30)

        self.download_button = ttk.Button(self, text="开始下载", command=self.start_download_thread)
        self.download_button.place(x=199, y=194, width=60, height=30)

        self.save_booksource_button = ttk.Button(self, text="导出书源", command=self.save_booksource)
        self.save_booksource_button.place(x=0, y=226, width=60, height=30)

        self.import_booksource_button = ttk.Button(self, text="导入书源", command=self.import_booksource)
        self.import_booksource_button.place(x=60, y=226, width=60, height=30)

        self.booksource_choose = ttk.Combobox(self, state="readonly")
        self.booksource_choose.set("------书源列表------")
        self.booksource_choose.bind("<<ComboboxSelected>>", self.update_entries_from_section)
        self.booksource_choose.place(x=121, y=227, width=137, height=28)


    def monitor_queue_for_updates(self):
        """监控队列并在主线程更新进度条"""
        while True:
            if self.update_queue.empty() and self.completed_tasks == self.total_tasks:
                break  # 所有章节下载完成且队列为空，退出循环
            elif not self.update_queue.empty():
                self.update_queue.get()  # 从队列获取完成信号
                self.completed_tasks += 1
                progress = min(self.completed_tasks / self.total_tasks * 100, 100)  # 计算进度百分比
                self.progress_var.set(progress)  # 更新进度条变量
                self.update_idletasks()  # 刷新界面
            else:
                self.after(100, self.monitor_queue_for_updates)  # 没有新任务时等待并检查
                break  # 增加此行以避免无限循环

    def start_download_thread(self):
        """启动下载线程"""
        threading.Thread(target=self.download_novel).start()

    def download_novel(self):
        # 获取用户输入的值
        novel_home_url = self.entry_novel_home_url.get()  # 小说主页变量
        novel_list_url = self.entry_novel_list_url.get()  # 小说列表页变量
        novel_name_xpath = self.entry_novel_name_xpath.get()  # 小说名称变量
        chapter_title_xpath = self.entry_chapter_title_xpath.get()  # 小说章节名称变量
        chapter_url_xpath = self.entry_chapter_url_xpath.get()  # 小说章节网址名称变量
        chapter_content_xpath = self.entry_chapter_content_xpath.get()  # 小说章节内容变量
        try:
            CONCURRENT_REQUESTS = int(self.entry_concurrent_requests.get())
            if CONCURRENT_REQUESTS <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "并发请求数量必须是正整数")
            return
        # 确保提供的URL以http或https开头
        if not novel_home_url.startswith(('http://', 'https://')):
            messagebox.showerror("错误", "小说主页URL必须以http://或https://开头")
            return
        if not novel_list_url.startswith(('http://', 'https://')):
            messagebox.showerror("错误", "小说列表页URL必须以http://或https://开头")
            return
        url = novel_list_url
        headers_list = [
            {
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/87.0.4280.77 Mobile/15E148 Safari/604.1'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.109 Safari/537.36 CrKey/1.54.248666'
            }, {
                'user-agent': 'Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320'
            }, {
                'user-agent': 'Mozilla/5.0 (BB10; Touch) AppleWebKit/537.10+ (KHTML, like Gecko) Version/10.0.9.2372 Mobile Safari/537.10+'
            }, {
                'user-agent': 'Mozilla/5.0 (PlayBook; U; RIM Tablet OS 2.1.0; en-US) AppleWebKit/536.2+ (KHTML like Gecko) Version/7.2.1.0 Safari/536.2+'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; U; Android 4.3; en-us; SM-N900T Build/JSS15J) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; U; Android 4.1; en-us; GT-N7100 Build/JRO03C) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; U; Android 4.0; en-us; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G950U Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; SM-G965U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.111 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; SM-T837A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.80 Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; U; en-us; KFAPWI Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Silk/3.13 Safari/535.19 Silk-Accelerated=true'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; U; Android 4.4.2; en-us; LGMS323 Build/KOT49I.MS32310c) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 550) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Mobile Safari/537.36 Edge/14.14263'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 10 Build/MOB31T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Nexus 5X Build/OPR4.170623.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 7.1.1; Nexus 6 Build/N6F26U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Nexus 6P Build/OPP3.170518.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 7 Build/MOB30X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch; NOKIA; Lumia 520)'
            }, {
                'user-agent': 'Mozilla/5.0 (MeeGo; NokiaN9) AppleWebKit/534.13 (KHTML, like Gecko) NokiaBrowser/8.5.0 Mobile Safari/534.13'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 9; Pixel 3 Build/PQ1A.181105.017.A1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'
            }, {
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
            }, {
                'user-agent': 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1'
            }
        ]
        headers = random.choice(headers_list)
        # 章节页解析
        response = requests.get(url=url, headers=headers).text
        tree = etree.HTML(response)
        # 获取小说名称并去除符号
        novel_name = tree.xpath(novel_name_xpath)[0].strip()

        # 弹出保存文件对话框让用户选择保存位置和文件名
        novel_file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",  # 设置默认文件扩展名为.txt
            filetypes=[("Text Files", "*.txt")],  # 限制文件类型为txt
            initialfile=f"{novel_name}.txt",  # 设置默认文件名为novel_name
            title="选择保存位置"
        )
        if not novel_file_path:  # 如果用户取消了选择
            return

        # 在开始下载前，更改按钮状态和文本
        self.download_button.config(state=tk.DISABLED, text="正在下载")
        self.download_button.update_idletasks()

        # 获取章节名称和章节网址
        chapter_title = [chapter_title for chapter_title in tree.xpath(chapter_title_xpath)]  # 为了后续每个章节名称对应正确的网址，新建列表
        chapter_url = [novel_home_url + chapter_url for chapter_url in tree.xpath(chapter_url_xpath)]
        dic1 = dict(zip(chapter_title, chapter_url))

        self.total_tasks = len(chapter_title)  # 设定任务总数
        self.completed_tasks = 0  # 重置已完成任务数
        self.progress_var.set(0)  # 初始化进度条

        # 定义下载章节内容的函数
        def download_chapter(chapter_info):
            title, url = chapter_info
            try:
                response = requests.get(url=url, headers=headers).text
                tree = etree.HTML(response)
                contents = tree.xpath(chapter_content_xpath)
                contents = [content.strip() for content in contents if content.strip()]
                return title, contents, url
            except Exception as e:
                print(f"下载章节《{title}》时出错：{e}")
                return title, None, url

        # 使用线程池进行并发下载，并收集结果
        chapters_content = []

        # 开始监控队列
        self.queue_monitor_id = self.after(100, self.monitor_queue_for_updates)
        with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
            futures = {executor.submit(download_chapter, (title, url)) for title, url in dic1.items()}
            for future in concurrent.futures.as_completed(futures):
                title, contents, url = future.result()
                if contents:
                    self.update_queue.put(1)  # 下载完成，向队列发送信号
                    chapters_content.append((title, contents, url))

        # 检查更新队列
        self.monitor_queue_for_updates()

        # 按URL尾部数字大小进行排序，确保章节顺序正确
        chapters_content.sort(key=lambda x: int(re.search(r'\d+', x[2].split('/')[-1]).group()))

        # 将排序后的章节内容写入文件
        with open(novel_file_path, "w", encoding="utf-8") as novel_file:
            for title, contents, url in chapters_content:
                novel_file.write(f"{title}\n")
                for content in contents:
                    novel_file.write(content + "\n")
                novel_file.write("-" * 50 + "\n")

        self.download_button.config(state=tk.NORMAL, text="开始下载")  # 下载完成后，恢复按钮状态和文本
        self.download_button.update_idletasks()
        self.after(3000, lambda: self.progress_var.set(0))  # 延迟3秒后重置进度条
        self.completed_tasks = 0
        print(f"小说《{novel_name}》的所有章节内容已成功保存至 {novel_file_path}")

    def save_booksource_to_file(self, booksource_section, booksource_data):
        """保存书源配置到指定的INI文件中"""
        # 读取现有配置文件，如果存在的话
        if os.path.exists(self.booksource_file_name):
            with io.open(self.booksource_file_name, 'r', encoding='utf-8') as file:
                self.booksource_parser.read_file(file)

        # 如果节不存在则添加，否则更新
        if not self.booksource_parser.has_section(booksource_section):
            self.booksource_parser.add_section(booksource_section)

        # 更新配置项
        for key, value in booksource_data.items():
            self.booksource_parser.set(booksource_section, key, value)

        # 写入INI文件
        with io.open(self.booksource_file_name, 'w', encoding='utf-8') as booksourcefile:
            self.booksource_parser.write(booksourcefile)

    def save_booksource(self):
        if messagebox.askyesno("导出书源", "是否导出当前书源？"):
            if any(entry.get() == "" for entry in
                   [self.entry_novel_home_url, self.entry_novel_name_xpath, self.entry_chapter_title_xpath,
                    self.entry_chapter_url_xpath, self.entry_chapter_content_xpath, self.entry_concurrent_requests]):
                messagebox.showerror("错误", "书源必填项未输入，请检查！")
                return  # 如果有必填项为空，则不执行保存操作

            # 获取配置文件中的节名称
            booksource_section = simpledialog.askstring("小说网站名称", "请输入该小说网站名称:")
            if not booksource_section:
                messagebox.showerror("错误", "小说网站名称不能为空！")
                return

            # 所有必填项都有值，继续保存配置
            booksource_data = {
                "novel_home_url": self.entry_novel_home_url.get(),
                "novel_name_xpath": self.entry_novel_name_xpath.get(),
                "chapter_title_xpath": self.entry_chapter_title_xpath.get(),
                "chapter_url_xpath": self.entry_chapter_url_xpath.get(),
                "chapter_content_xpath": self.entry_chapter_content_xpath.get(),
                "concurrent_requests": self.entry_concurrent_requests.get()
            }

            # 调用save_booksource_to_file方法保存配置
            try:
                self.save_booksource_to_file(booksource_section, booksource_data)
                messagebox.showinfo("成功", f"书源已成功导出至{os.getcwd()}/{self.booksource_file_name}")
            except Exception as e:
                messagebox.showerror("书源失败", f"导出书源文件时发生错误：{e}")

    def import_booksource(self):
        # 读取现有配置文件
        self.booksource_parser = configparser.ConfigParser()
        with io.open(self.booksource_file_name, 'r', encoding='utf-8') as file:
            self.booksource_parser.read_file(file)

        # 获取所有section，然后在前面添加默认文本
        self.booksource_section = ['------书源列表------'] + self.booksource_parser.sections()
        self.booksource_choose['values'] = self.booksource_section
        if self.booksource_section:
            self.booksource_choose.current(0)  # 选择第一个section

    def update_entries_from_section(self, event):
        selected_section = self.booksource_choose.get()
        if selected_section and selected_section != '------书源列表------':
            try:
                self.entry_novel_home_url.delete(0, tk.END)
                self.entry_novel_home_url.insert(0, self.booksource_parser[selected_section].get('novel_home_url', ''))

                self.entry_novel_name_xpath.delete(0, tk.END)
                self.entry_novel_name_xpath.insert(0, self.booksource_parser[selected_section].get('novel_name_xpath', ''))

                self.entry_chapter_title_xpath.delete(0, tk.END)
                self.entry_chapter_title_xpath.insert(0, self.booksource_parser[selected_section].get('chapter_title_xpath', ''))

                self.entry_chapter_url_xpath.delete(0, tk.END)
                self.entry_chapter_url_xpath.insert(0, self.booksource_parser[selected_section].get('chapter_url_xpath', ''))

                self.entry_chapter_content_xpath.delete(0, tk.END)
                self.entry_chapter_content_xpath.insert(0, self.booksource_parser[selected_section].get('chapter_content_xpath', ''))

                self.entry_concurrent_requests.delete(0, tk.END)
                self.entry_concurrent_requests.insert(0, self.booksource_parser[selected_section].get('concurrent_requests', ''))
            except KeyError as e:
                messagebox.showerror("错误", f"无法找到指定的书源配置项：{e}")

if __name__ == "__main__":
    app = ZickNovel()
    app.mainloop()