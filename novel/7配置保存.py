import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os


def save_config_to_file(config_name, config_data, file_path):
    """保存配置到指定路径的文件中，优化处理以避免末尾额外的换行符，并替换XPath中的双引号为单引号"""
    # 替换XPath表达式中的双引号为单引号，以避免输出时的转义
    for key in config_data:
        if isinstance(config_data[key], str) and '//' in config_data[key]:  # 简单判断是否可能是XPath
            config_data[key] = config_data[key].replace('"', "'")

    config_file_path = f"{file_path}/{config_name}.json"
    with open(config_file_path, 'w', encoding='utf-8') as file:
        # 使用json.dumps先转化为字符串，以便后续处理末尾的空白字符
        json_str = json.dumps(config_data, ensure_ascii=False, indent=4)
        file.write(json_str)
        # 移除可能的末尾空白字符（包括换行符）
        file.seek(-1, os.SEEK_END)
        while file.read(1).isspace():
            file.seek(-1, os.SEEK_END)
            file.truncate()
    messagebox.showinfo("成功", f"配置已保存至：{config_file_path}")
def config_download():
    if messagebox.askyesno("保存配置", "是否导出当前配置？"):
        config_name = simpledialog.askstring("输入配置名", "请输入配置文件名：")
        if config_name:  # 用户提供了配置名
            config_data = {
                "novel_name_xpath": entry_novel_name_xpath.get(),
                "chapter_title_xpath": entry_chapter_title_xpath.get(),
                "chapter_url_xpath": entry_chapter_url_xpath.get(),
                "chapter_content_xpath": entry_chapter_content_xpath.get(),
                "novel_file_path": entry_novel_file_path.get()
            }
            save_config_to_file(config_name, config_data, entry_novel_file_path.get())
            messagebox.showinfo("成功", "配置已保存。")
def create_gui():
    global entry_novel_name_xpath, entry_chapter_title_xpath, entry_chapter_url_xpath, entry_chapter_content_xpath, entry_novel_file_path

    root = tk.Tk()
    root.title("ZickNovel")
    root.geometry("500x280")  # 设置窗口尺寸

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

    tk.Label(root, text="配置保存路径:").pack()
    entry_novel_file_path = tk.Entry(root)
    entry_novel_file_path.pack()

    download_button = tk.Button(root, text="导出配置", command=config_download)
    download_button.pack()

    root.mainloop()
# GUI初始化
create_gui()

# 变量初始化
novel_name_xpath = ""
chapter_title_xpath = ""
chapter_url_xpath = ""
chapter_content_xpath = ""
novel_file_path_var = ""