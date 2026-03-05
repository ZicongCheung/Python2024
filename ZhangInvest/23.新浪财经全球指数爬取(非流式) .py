import requests
import time

# 新浪财经获取指数数据的接口
# 指数代码说明：
# - 上证指数：s_sh000001
# - 深证成指：s_sz399001
# - 创业板指：s_sz399006
# - 道琼斯指数：int_dji  (或尝试 gb_dji，根据实际返回调整)
# - 标普500指数：gb_inx
# - 纳斯达克指数：gb_ixic
# 注：国际指数前缀可能因新浪接口更新而变化，若返回数据为空请尝试调整前缀
index_codes = [
    's_sh000001',   # 上证指数
    's_sz399001',   # 深证成指
    's_sz399006',   # 创业板指
    'gb_dji',      # 道琼斯指数（备用：int_dji）
    'gb_inx',      # 标普500指数
    'gb_ixic'      # 纳斯达克指数
]
# 构造请求URL，将代码用逗号连接
url = f"http://hq.sinajs.cn/list={','.join(index_codes)}"

# 自定义请求头，模拟浏览器，避免被拒绝
headers = {
    'Referer': 'https://finance.sina.com.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_index_data():
    """获取新浪财经指数数据，返回全部原始文本"""
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'gbk'  # 新浪返回的编码为GBK
        response.raise_for_status()
        return response.text   # 返回全部原始数据（多行文本）
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None

def main():
    while True:
        raw_data = fetch_index_data()
        if raw_data:
            print("获取到的全部原始数据如下：\n")
            print(raw_data)
            break
        else:
            print("数据为空，10秒后重试...")
            time.sleep(10)

if __name__ == "__main__":
    main()