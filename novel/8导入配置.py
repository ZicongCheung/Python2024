import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import configparser

def import_config():
    ini_file_path = filedialog.askopenfilename(title="选择INI配置文件", filetypes=[("INI Files", "*.ini")])
    if ini_file_path:
        config = configparser.ConfigParser()
        config.read(ini_file_path)

        # 假设配置都在[ZickNovelConfig] section下
        if 'ZickNovelConfig' in config:
            entry_novel_home_url.delete(0, tk.END)
            entry_novel_home_url.insert(0, config['ZickNovelConfig'].get('novel_home_url', ''))

            entry_novel_name_xpath.delete(0, tk.END)
            entry_novel_name_xpath.insert(0, config['ZickNovelConfig'].get('novel_name_xpath', ''))

            entry_chapter_title_xpath.delete(0, tk.END)
            entry_chapter_title_xpath.insert(0, config['ZickNovelConfig'].get('chapter_title_xpath', ''))

            entry_chapter_url_xpath.delete(0, tk.END)
            entry_chapter_url_xpath.insert(0, config['ZickNovelConfig'].get('chapter_url_xpath', ''))

            entry_chapter_content_xpath.delete(0, tk.END)
            entry_chapter_content_xpath.insert(0, config['ZickNovelConfig'].get('chapter_content_xpath', ''))

            entry_novel_file_path.delete(0, tk.END)
            entry_novel_file_path.insert(0, config['ZickNovelConfig'].get('novel_file_path', ''))

            entry_concurrent_requests.delete(0, tk.END)
            entry_concurrent_requests.insert(0, config['ZickNovelConfig'].get('concurrent_requests', ''))

            messagebox.showinfo("成功", "配置已成功导入。")
        else:
            messagebox.showerror("错误", "INI文件中未找到[ZickNovelConfig] section。")
def create_gui():
    global entry_novel_home_url, entry_novel_name_xpath, entry_chapter_title_xpath, entry_chapter_url_xpath, entry_chapter_content_xpath, entry_concurrent_requests, entry_novel_file_path

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

    tk.Label(root, text="小说保存路径:").pack()
    entry_novel_file_path = tk.Entry(root)
    entry_novel_file_path.pack()

    import_config_button = tk.Button(root, text="导入配置", command=import_config)
    import_config_button.pack()

    root.mainloop()
# GUI初始化
create_gui()
