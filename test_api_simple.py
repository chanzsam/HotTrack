import requests
import os

API_KEY = os.environ.get("YOUTUBE_API_KEY", "AIzaSyAbZqqEl_XNjKT1V_G0Vp172iE9OoZA_Dc")

print(f"=== YouTube API Key 测试 ===")
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

print("\n=== 测试 YouTube API ===")
try:
    resp = requests.get(url, params=params, timeout=10)
    print(f"状态码: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"✓ 成功! 获取到 {len(data.get('items', []))} 条视频")
        for item in data.get('items', [])[:3]:
            print(f"  - {item['snippet']['title'][:60]}")
    else:
        print(f"✗ 失败!")
        try:
            error_data = resp.json()
            print(f"错误代码: {error_data.get('error', {}).get('code')}")
            print(f"错误信息: {error_data.get('error', {}).get('message')}")
            print(f"错误原因: {error_data.get('error', {}).get('errors', [{}])[0].get('reason')}")
        except:
            print(f"响应内容: {resp.text[:500]}")
except Exception as e:
    print(f"✗ 请求失败: {e}")
