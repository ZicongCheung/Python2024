import concurrent.futures
import requests
from lxml import etree
import re
import random
import tkinter as tk
from tkinter import messagebox, filedialog

def download_novel(download_button):
    global novel_home_url, novel_list_url, novel_name_xpath, chapter_title_xpath, chapter_url_xpath, chapter_content_xpath, novel_file_path, CONCURRENT_REQUESTS

    # 获取用户输入的值
    novel_home_url = entry_novel_home_url.get()  # 小说主页变量
    novel_list_url = entry_novel_list_url.get()  # 小说列表页变量
    novel_name_xpath = entry_novel_name_xpath.get()  # 小说名称变量
    chapter_title_xpath = entry_chapter_title_xpath.get()  # 小说章节名称变量
    chapter_url_xpath = entry_chapter_url_xpath.get()  # 小说章节网址名称变量
    chapter_content_xpath = entry_chapter_content_xpath.get()  # 小说章节内容变量
    try:
        CONCURRENT_REQUESTS = int(entry_concurrent_requests.get())
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
    download_button.config(state=tk.DISABLED, text="正在下载")
    download_button.update_idletasks()  # 更安全地更新UI，避免阻塞主循环

    # 获取章节名称和章节网址
    chapter_title = [chapter_title for chapter_title in tree.xpath(chapter_title_xpath)]  # 为了后续每个章节名称对应正确的网址，新建列表
    chapter_url = [novel_home_url + chapter_url for chapter_url in tree.xpath(chapter_url_xpath)]
    dic1 = dict(zip(chapter_title, chapter_url))

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

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        futures = {executor.submit(download_chapter, (title, url)) for title, url in dic1.items()}
        for future in concurrent.futures.as_completed(futures):
            title, contents, url = future.result()
            if contents:
                chapters_content.append((title, contents, url))

    # 下载完成后，恢复按钮状态和文本
    download_button.config(state=tk.NORMAL, text="开始下载")
    download_button.update_idletasks()  # 更新UI

    # 按URL尾部数字大小进行排序，确保章节顺序正确
    chapters_content.sort(key=lambda x: int(re.search(r'\d+', x[2].split('/')[-1]).group()))

    # 将排序后的章节内容写入文件
    with open(novel_file_path, "w", encoding="utf-8") as novel_file:
        for title, contents, url in chapters_content:
            novel_file.write(f"{title}\n")
            for content in contents:
                novel_file.write(content + "\n")
            novel_file.write("-" * 50 + "\n")

    print(f"小说《{novel_name}》的所有章节内容已成功保存至 {novel_file_path}")

def create_gui():
    global entry_novel_home_url, entry_novel_list_url, entry_novel_name_xpath, entry_chapter_title_xpath, entry_chapter_url_xpath, entry_chapter_content_xpath, entry_concurrent_requests

    root = tk.Tk()
    root.title("ZickNovel")
    root.geometry("260x600")  # 设置窗口尺寸
    tk.Label(root, text="小说主页链接:").pack()
    entry_novel_home_url = tk.Entry(root)
    entry_novel_home_url.pack()

    tk.Label(root, text="小说列表页链接:").pack()
    entry_novel_list_url = tk.Entry(root)
    entry_novel_list_url.pack()

    tk.Label(root, text="小说名称XPath:").pack()
    entry_novel_name_xpath = tk.Entry(root)
    entry_novel_name_xpath.pack()

    tk.Label(root, text="章节标题XPath:").pack()
    entry_chapter_title_xpath = tk.Entry(root)
    entry_chapter_title_xpath.pack()

    tk.Label(root, text="章节网址XPath:").pack()
    entry_chapter_url_xpath = tk.Entry(root)
    entry_chapter_url_xpath.pack()

    tk.Label(root, text="章节内容XPath:").pack()
    entry_chapter_content_xpath = tk.Entry(root)
    entry_chapter_content_xpath.pack()

    tk.Label(root, text="下载线程数:").pack()
    entry_concurrent_requests = tk.Entry(root)
    entry_concurrent_requests.pack()

    download_button = tk.Button(root, text="开始下载")
    download_button.pack()
    download_button.config(command=lambda: download_novel(download_button))  # 传递download_button给download_novel

    root.mainloop()

# GUI初始化
create_gui()

# 变量初始化
novel_home_url = ""
novel_list_url = ""
novel_name_xpath = ""
chapter_title_xpath = ""
chapter_url_xpath = ""
chapter_content_xpath = ""
novel_file_path = ""
CONCURRENT_REQUESTS = 10  # 默认并发请求数量