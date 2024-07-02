import concurrent.futures
import requests
from lxml import etree
import re

url = "http://www.23book.org/shu72390/"
headers =  {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0'}

# 章节页解析
response = requests.get(url=url, headers=headers).text
tree = etree.HTML(response)
# 获取小说名称并去除符号
novel_name = tree.xpath('//div[@id="info"]/h1/text()')[0].strip()
novel_file_path = f"C:/Users/张/Desktop/{novel_name}.txt"
# 获取章节名称和章节网址
chapter_title = [chapter_title for chapter_title in tree.xpath('//div[@class="listmain"]//a/text()')]  # 为了后续每个章节名称对应正确的网址，新建列表
chapter_url = ['http://www.23book.org/' + chapter_url for chapter_url in tree.xpath('//div[@class="listmain"]//a/@href')]
dic1 = dict(zip(chapter_title, chapter_url))
# 设置并发数
CONCURRENT_REQUESTS = 100

# 定义下载章节内容的函数
def download_chapter(chapter_info):
    title, url = chapter_info
    try:
        response = requests.get(url=url, headers=headers).text
        tree = etree.HTML(response)
        contents = tree.xpath('//div[@id="content"]/text()')
        contents = [content.strip() for content in contents if content.strip()]
        return title, contents
    except Exception as e:
        print(f"下载章节《{title}》时出错：{e}")
        return title, None

# 使用线程池进行并发下载，并收集结果
chapters_content = []

with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
    futures = {executor.submit(download_chapter, (title, url)) for title, url in dic1.items()}
    for future in concurrent.futures.as_completed(futures):
        title, contents = future.result()
        if contents:
            chapters_content.append((title, contents))

# 提取章节标题中的数字，假设数字位于"第"和"章"之间
def chapter_number(title):
    match = re.search(r'\d+', title)
    return int(match.group()) if match else float('inf')

# 按章节标题中提取的数字大小进行排序，确保章节顺序正确
chapters_content.sort(key=lambda x: chapter_number(x[0]))

# 将排序后的章节内容写入文件
with open(novel_file_path, "w", encoding="utf-8") as novel_file:
    for title, contents in chapters_content:
        novel_file.write(f"{title}\n")
        for content in contents:
            novel_file.write(content + "\n")
        novel_file.write("-"*50 + "\n")

print(f"小说《{novel_name}》的所有章节内容已成功保存至 {novel_file_path}")