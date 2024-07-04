import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import configparser
import os


def save_config_to_file(config_name, config_data, file_path):
    config_parser = configparser.ConfigParser()
    # 添加节
    config_parser.add_section('ZickNovelConfig')
    # 写入配置项
    for key, value in config_data.items():
        config_parser.set('ZickNovelConfig', key, value)

    # 写入INI文件，直接使用用户选择的file_path
    with open(file_path, 'w', encoding='utf-8') as configfile:
        config_parser.write(configfile)


def save_config():
    if messagebox.askyesno("保存配置", "是否导出当前配置？"):
        if any(entry.get() == "" for entry in
               [entry_novel_home_url, entry_novel_name_xpath, entry_chapter_title_xpath,
                entry_chapter_url_xpath, entry_chapter_content_xpath, entry_concurrent_requests]):
            messagebox.showerror("错误", "配置必填项未输入，请检查！")
            return  # 如果有必填项为空，则不执行保存操作

        # 所有必填项都有值，继续保存配置
        config_data = {
            "novel_home_url": entry_novel_home_url.get(),
            "novel_name_xpath": entry_novel_name_xpath.get(),
            "chapter_title_xpath": entry_chapter_title_xpath.get(),
            "chapter_url_xpath": entry_chapter_url_xpath.get(),
            "chapter_content_xpath": entry_chapter_content_xpath.get(),
            "concurrent_requests": entry_concurrent_requests.get()
        }

        # 弹出保存文件对话框让用户选择保存路径并命名INI文件
        file_path = filedialog.asksaveasfilename(title="保存配置文件",
                                                 defaultextension=".ini",  # 默认文件扩展名为.ini
                                                 filetypes=[("INI Files", "*.ini")])  # 限制文件类型为INI

        if file_path:  # 用户选择了路径并输入了文件名
            save_config_to_file(os.path.splitext(os.path.basename(file_path))[0], config_data, file_path)
            messagebox.showinfo("成功", "配置已保存至：{}".format(file_path))
        else:  # 用户取消了保存操作
            return
def create_gui():
    global entry_novel_home_url, entry_novel_name_xpath, entry_chapter_title_xpath, entry_chapter_url_xpath, entry_chapter_content_xpath, entry_config_file_path, entry_concurrent_requests

    root = tk.Tk()
    root.title("ZickNovel")
    root.geometry("300x380")  # 设置窗口尺寸

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

    tk.Label(root, text="配置保存路径:").pack()
    entry_config_file_path = tk.Entry(root)
    entry_config_file_path.pack()

    save_config_button = tk.Button(root, text="导出配置", command=save_config)
    save_config_button.pack()

    root.mainloop()
# GUI初始化
create_gui()

# 变量初始化
novel_name_xpath = ""
chapter_title_xpath = ""
chapter_url_xpath = ""
chapter_content_xpath = ""