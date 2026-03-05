import requests
import time
import json

def create_session_with_cookie():
    """
    访问雪球首页，自动获取并保存Cookie，返回配置好的Session对象。
    如果获取失败，返回None。
    """
    session = requests.Session()
    # 设置常见浏览器请求头，模拟真实访问
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    try:
        # 先访问雪球首页，服务器会返回必要的Cookie（如xq_a_token等）
        home_url = 'https://xueqiu.com/'
        response = session.get(home_url, timeout=10)
        response.raise_for_status()
        # Session会自动保存响应中的Cookie，无需额外处理
        return session
    except requests.RequestException as e:
        print(f"获取Cookie失败: {e}")
        return None

def fetch_index_data(session):
    """
    使用给定的Session（已包含有效Cookie）请求雪球指数接口。
    成功时返回解析后的JSON数据（字典形式），失败返回None。
    """
    url = 'https://stock.xueqiu.com/v5/stock/realtime/quotec.json'
    params = {
        'symbol': 'SH000001,SZ399001,SZ399006,.DJI,.SPX,.IXIC'   # 上证、深成指、创业板、道指、标普500、纳指
    }
    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        # 雪球接口返回的error_code为0表示成功，否则说明Cookie可能失效或其它错误
        if data.get('error_code') == 0:
            return data
        else:
            print(f"接口返回错误: {data.get('error_description')}")
            return None
    except requests.RequestException as e:
        print(f"请求数据失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return None

def main():
    """
    主循环：自动管理Cookie的生命周期，成功获取数据后打印全部内容并退出。
    """
    session = None
    while True:
        # 若无有效Session或上次请求失败（Cookie可能过期），则重新获取
        if session is None:
            session = create_session_with_cookie()
            if session is None:
                print("无法获取Cookie，10秒后重试...")
                time.sleep(10)
                continue

        # 尝试获取指数数据
        data = fetch_index_data(session)
        if data:
            print("获取到的全部数据如下：")
            # 以格式化的JSON字符串打印全部数据
            print(json.dumps(data, ensure_ascii=False, indent=2))
            break   # 成功后退出循环
        else:
            # 数据获取失败，很可能是Cookie过期或无效，置空Session以便下次重新获取
            print("数据获取失败，可能Cookie失效，10秒后重新获取Cookie并重试...")
            session = None
            time.sleep(10)

if __name__ == "__main__":
    main()