import requests
import os

API_KEY = os.environ.get("YOUTUBE_API_KEY", "AIzaSyAbZqqEl_XNjKT1V_G0Vp172iE9OoZA_Dc")

print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
print(f"API Key 长度: {len(API_KEY)}")

url = "https://www.googleapis.com/youtube/v3/videos"
params = {
    "part": "snippet,statistics",
    "chart": "mostPopular",
    "regionCode": "US",
    "maxResults": 5,
    "key": API_KEY
}

print("\n测试 1: 不使用代理")
try:
    resp = requests.get(url, params=params, timeout=30)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"成功! 获取到 {len(data.get('items', []))} 条视频")
        for item in data.get('items', [])[:2]:
            print(f"  - {item['snippet']['title'][:50]}")
    else:
        print(f"错误: {resp.text[:300]}")
except Exception as e:
    print(f"请求失败: {e}")

print("\n测试 2: 使用代理")
proxy = os.environ.get("HTTP_PROXY", "http://127.0.0.1:7890")
proxies = {"http": proxy, "https": proxy}
try:
    resp = requests.get(url, params=params, proxies=proxies, timeout=30)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"成功! 获取到 {len(data.get('items', []))} 条视频")
        for item in data.get('items', [])[:2]:
            print(f"  - {item['snippet']['title'][:50]}")
    else:
        print(f"错误: {resp.text[:300]}")
except Exception as e:
    print(f"请求失败: {e}")
