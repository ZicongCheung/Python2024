import tkinter as tk
from tkinter import filedialog

def remove_text_from_file(file_path, texts_to_remove):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    for text in texts_to_remove:
        content = content.replace(text, '')

    # 删除多余的空行
    new_content = '\n'.join(line for line in content.splitlines() if line.strip())

    new_file_path = file_path.replace('.txt', '_modified.txt')
    with open(new_file_path, 'w', encoding='utf-8') as new_file:
        new_file.write(new_content)
    print(f"生成的新文件: {new_file_path}")


def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="选择要处理的TXT文件", filetypes=[("Text files", "*.txt")])

    if file_path:
        print("输入要删除的文本内容，每行一条，结束输入后按回车两次:")
        texts_to_remove = []
        while True:
            line = input()
            if line == "":
                break
            texts_to_remove.append(line)

        remove_text_from_file(file_path, texts_to_remove)


if __name__ == "__main__":
    main()