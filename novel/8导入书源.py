import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import io
def import_booksource():
    booksource_file_name = 'BookSource.ini'
    booksource_parser = configparser.ConfigParser()
    with io.open(booksource_file_name, 'r', encoding='utf-8') as file:
        booksource_parser.read_file(file)

    booksource_section = ['------书源列表------'] + booksource_parser.sections()
    booksource_choose['values'] = booksource_section
    if booksource_section:
        booksource_choose.current(0)  # 选择第一个section


def update_entries_from_section(event):
    selected_section = booksource_choose.get()
    if selected_section and selected_section != '------书源列表------':
        try:
            entry_novel_home_url.delete(0, tk.END)
            entry_novel_home_url.insert(0, booksource_parser[selected_section].get('novel_home_url', ''))

            entry_novel_name_xpath.delete(0, tk.END)
            entry_novel_name_xpath.insert(0, booksource_parser[selected_section].get('novel_name_xpath', ''))

            entry_chapter_title_xpath.delete(0, tk.END)
            entry_chapter_title_xpath.insert(0, booksource_parser[selected_section].get('chapter_title_xpath', ''))

            entry_chapter_url_xpath.delete(0, tk.END)
            entry_chapter_url_xpath.insert(0, booksource_parser[selected_section].get('chapter_url_xpath', ''))

            entry_chapter_content_xpath.delete(0, tk.END)
            entry_chapter_content_xpath.insert(0, booksource_parser[selected_section].get('chapter_content_xpath', ''))

            entry_concurrent_requests.delete(0, tk.END)
            entry_concurrent_requests.insert(0, booksource_parser[selected_section].get('concurrent_requests', ''))
        except KeyError as e:
            tk.messagebox.showerror("错误", f"无法找到指定的书源配置项：{e}")

def create_gui():
    global entry_novel_home_url, entry_novel_name_xpath, entry_chapter_title_xpath, entry_chapter_url_xpath, entry_chapter_content_xpath, entry_concurrent_requests, booksource_parser, booksource_choose

    root = tk.Tk()
    root.title("ZickNovel")
    root.geometry("300x380")  # 设置窗口尺寸

    booksource_parser = configparser.ConfigParser()
    booksource_parser.read('BookSource.ini', encoding='utf-8')  # 读取配置文件

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

    # 创建下拉列表
    booksource_choose = ttk.Combobox(root, state="readonly")
    booksource_choose.set("------书源列表------")
    booksource_choose.bind("<<ComboboxSelected>>", update_entries_from_section)
    booksource_choose.pack()

    import_config_button = tk.Button(root, text="导入书源", command=import_booksource)
    import_config_button.pack()

    root.mainloop()
# GUI初始化
create_gui()
