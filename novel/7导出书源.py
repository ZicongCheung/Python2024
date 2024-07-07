import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import configparser
import os
import io

booksource_file_name = "BookSource.ini"


def save_booksource_to_file(booksource_name, booksource_data):
    booksource_parser = configparser.ConfigParser()

    # 读取现有配置文件，如果存在的话
    if os.path.exists(booksource_file_name):
        with io.open(booksource_file_name, 'r', encoding='utf-8') as file:
            booksource_parser.read_file(file)

    # 如果节不存在则添加，否则更新
    if not booksource_parser.has_section(booksource_name):
        booksource_parser.add_section(booksource_name)

    # 更新配置项
    for key, value in booksource_data.items():
        booksource_parser.set(booksource_name, key, value)

    # 写入INI文件
    with io.open(booksource_file_name, 'w', encoding='utf-8') as booksourcefile:
        booksource_parser.write(booksourcefile)

def save_booksource():
    if messagebox.askyesno("保存配置", "是否导出当前配置？"):
        if any(entry.get() == "" for entry in
               [entry_novel_home_url, entry_novel_name_xpath, entry_chapter_title_xpath,
                entry_chapter_url_xpath, entry_chapter_content_xpath, entry_concurrent_requests]):
            messagebox.showerror("错误", "配置必填项未输入，请检查！")
            return  # 如果有必填项为空，则不执行保存操作

        # 获取配置文件中的节名称
        booksource_section = simpledialog.askstring("配置节名称", "请输入配置节名称:")
        if not booksource_section:
            messagebox.showerror("错误", "节名称不能为空！")
            return

        # 所有必填项都有值，继续保存配置
        booksource_data = {
            "novel_home_url": entry_novel_home_url.get(),
            "novel_name_xpath": entry_novel_name_xpath.get(),
            "chapter_title_xpath": entry_chapter_title_xpath.get(),
            "chapter_url_xpath": entry_chapter_url_xpath.get(),
            "chapter_content_xpath": entry_chapter_content_xpath.get(),
            "concurrent_requests": entry_concurrent_requests.get()
        }

        # 调用save_booksource_to_file方法保存配置
        try:
            save_booksource_to_file(booksource_section, booksource_data)
            messagebox.showinfo("成功", f"书源已成功导出至{os.getcwd()}/{booksource_file_name}")
        except Exception as e:
            messagebox.showerror("书源失败", f"导出书源文件时发生错误：{e}")


def create_gui():
    global entry_novel_home_url, entry_novel_name_xpath, entry_chapter_title_xpath, entry_chapter_url_xpath, entry_chapter_content_xpath, entry_concurrent_requests

    root = tk.Tk()
    root.title("ZickNovel")
    root.geometry("300x300")  # 设置窗口尺寸

    tk.Label(root, text="小说主页网址:").pack()
    entry_novel_home_url = tk.Entry(root)
    entry_novel_home_url.pack()

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

    save_booksource_button = tk.Button(root, text="导出书源", command=save_booksource)
    save_booksource_button.pack()

    root.mainloop()
# GUI初始化
create_gui()

# 变量初始化
novel_name_xpath = ""
chapter_title_xpath = ""
chapter_url_xpath = ""
chapter_content_xpath = ""