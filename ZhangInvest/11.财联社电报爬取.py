import requests
import json
import time
import hashlib
from requests.adapters import HTTPAdapter

referer_url = "https://www.cls.cn/telegraph"
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Host": "www.cls.cn",
    "Referer": referer_url,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def generate_sign(params):
    """生成财联社API签名
    
    财联社签名算法：
    1. 将参数按key排序后拼接成 key=value 格式（不含sign参数）
    2. 对拼接字符串进行 SHA1 加密
    3. 对 SHA1 结果进行 MD5 加密
    """
    # 过滤掉sign参数并排序
    filtered_params = {k: v for k, v in params.items() if k != 'sign'}
    sorted_params = sorted(filtered_params.items())
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    
    # 先SHA1，再MD5
    sha1_result = hashlib.sha1(sign_str.encode('utf-8')).hexdigest()
    md5_result = hashlib.md5(sha1_result.encode('utf-8')).hexdigest()
    
    return md5_result

def get_json_data(telegraph_count=30):
    # 构建请求参数
    timestamp = int(time.time() * 1000)
    params = {
        "app": "CailianpressWeb",
        "os": "web",
        "rn": telegraph_count,
        "sv": "8.4.6",
        "ts": timestamp
    }
    
    # 生成签名
    params["sign"] = generate_sign(params)
    
    # 构建URL
    base_url = "https://www.cls.cn/v1/roll/get_roll_list"
    
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))

    try:
        response = s.get(base_url, params=params, timeout=10, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # 注意：errno可能是整数0或字符串"0"
        errno = result.get('errno')
        if errno != 0 and errno != '0':
            print(f"API错误: {result.get('msg', '未知错误')}")
            return []
        
        data = result.get('data', {}).get('roll_data', [])
        all_list = []
        for item in data:
            time_tuple = time.localtime(item.get('ctime', 0))
            bj_time = time.strftime("%Y/%m/%d %H:%M:%S", time_tuple)
            all_list.append([bj_time, item.get('content', '')])
        return all_list
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return []
    except Exception as e:
        print(f"未知错误: {e}")
        return []

def get_all_list():
    return get_json_data(30)

if __name__ == "__main__":
    result = get_all_list()
    for item in result:
        print(f"{item[0]} | {item[1]}")
