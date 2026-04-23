import urllib.request
import json
import sys

BASE = 'http://localhost:8000'
API = BASE + '/api/v1'
PASS = '✅'
FAIL = '❌'
results = []

def api_get(url, timeout=15):
    try:
        r = urllib.request.urlopen(url, timeout=timeout)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            return e.code, json.loads(body)
        except:
            return e.code, body
    except Exception as e:
        return 0, str(e)

def api_post(url, data=None, timeout=30):
    body = json.dumps(data).encode() if data else b''
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', 'application/json')
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            return e.code, json.loads(body)
        except:
            return e.code, body
    except Exception as e:
        return 0, str(e)

def test(name, condition, detail=''):
    status = PASS if condition else FAIL
    msg = f'{status} {name}'
    if detail:
        msg += f' — {detail}'
    print(msg)
    results.append((name, condition, detail))

print('=' * 60)
print('HotTrack 全面测试')
print('=' * 60)

# ===== 1. 基础端点 =====
print('\n=== 1. 基础端点 ===')
code, data = api_get(BASE + '/')
test('GET / 根路径', code == 200 and 'name' in data, f'code={code}')

code, data = api_get(BASE + '/health')
test('GET /health 健康检查', code == 200 and data.get('status') == 'healthy', f'code={code}')

code, data = api_get(BASE + '/openapi.json')
test('GET /openapi.json API规范', code == 200 and 'paths' in data, f'code={code}')

# ===== 2. 视频 API =====
print('\n=== 2. 视频 API ===')
code, data = api_get(API + '/videos/top-viewed?limit=10')
test('GET /videos/top-viewed', code == 200 and isinstance(data, list) and len(data) > 0, f'code={code}, count={len(data) if isinstance(data, list) else "N/A"}')

if isinstance(data, list) and len(data) > 0:
    v = data[0]
    has_fields = all(k in v for k in ['id', 'title', 'view_count', 'thumbnail_url', 'video_url', 'platform'])
    test('  视频字段完整', has_fields, f'keys={sorted(v.keys())[:10]}')
    has_thumb = 'i.ytimg.com' in v.get('thumbnail_url', '') or 'picsum.photos' in v.get('thumbnail_url', '')
    test('  缩略图有效', has_thumb, f'thumb={v.get("thumbnail_url", "")[:60]}')
    has_url = 'youtube.com' in v.get('video_url', '') or 'tiktok.com' in v.get('video_url', '')
    test('  视频链接有效', has_url, f'url={v.get("video_url", "")[:60]}')

code, data = api_get(API + '/videos/top-viewed?platform=youtube&limit=5')
test('GET /videos/top-viewed?platform=youtube', code == 200 and isinstance(data, list), f'count={len(data) if isinstance(data, list) else "N/A"}')

code, data = api_get(API + '/videos/top-viewed?platform=tiktok&limit=5')
test('GET /videos/top-viewed?platform=tiktok', code == 200 and isinstance(data, list), f'count={len(data) if isinstance(data, list) else "N/A"}')

code, data = api_get(API + '/videos/top-liked?limit=5')
test('GET /videos/top-liked', code == 200 and isinstance(data, list) and len(data) > 0, f'count={len(data) if isinstance(data, list) else "N/A"}')

code, data = api_get(API + '/videos/trending?hours=168&limit=10')
test('GET /videos/trending', code == 200 and isinstance(data, list) and len(data) > 0, f'count={len(data) if isinstance(data, list) else "N/A"}')

code, data = api_get(API + '/videos/stats')
test('GET /videos/stats', code == 200 and 'youtube' in data and 'tiktok' in data, f'keys={list(data.keys())}')

if code == 200:
    yt = data.get('youtube', {})
    tt = data.get('tiktok', {})
    test('  YouTube统计完整', 'total_videos' in yt and 'total_views' in yt and 'total_estimated_revenue' in yt, f'videos={yt.get("total_videos")}, views={yt.get("total_views")}, revenue={yt.get("total_estimated_revenue")}')
    test('  TikTok统计完整', 'total_videos' in tt and 'total_views' in tt and 'total_estimated_revenue' in tt, f'videos={tt.get("total_videos")}, views={tt.get("total_views")}, revenue={tt.get("total_estimated_revenue")}')

# ===== 3. 分析 API =====
print('\n=== 3. 分析 API ===')
code, data = api_get(API + '/analytics/viral?limit=10')
test('GET /analytics/viral', code == 200 and isinstance(data, list) and len(data) > 0, f'count={len(data) if isinstance(data, list) else "N/A"}')

if isinstance(data, list) and len(data) > 0:
    test('  包含viral_score', 'viral_score' in data[0], f'keys={sorted(data[0].keys())[:8]}')

code, data = api_get(API + '/analytics/revenue?limit=10')
test('GET /analytics/revenue', code == 200 and isinstance(data, list) and len(data) > 0, f'count={len(data) if isinstance(data, list) else "N/A"}')

if isinstance(data, list) and len(data) > 0:
    test('  包含收入数据', 'estimated_revenue_mid' in data[0] or 'estimated_cpm' in data[0], f'keys={sorted(data[0].keys())[:8]}')

code, data = api_get(API + '/analytics/revenue/ranking?limit=5')
test('GET /analytics/revenue/ranking', code == 200 and isinstance(data, list), f'count={len(data) if isinstance(data, list) else "N/A"}')

code, data = api_post(API + '/analytics/viral/calculate')
test('POST /analytics/viral/calculate', code == 200, f'data={str(data)[:80]}')

code, data = api_post(API + '/analytics/revenue/calculate')
test('POST /analytics/revenue/calculate', code == 200, f'data={str(data)[:80]}')

# ===== 4. AI API =====
print('\n=== 4. AI API ===')
code, data = api_post(API + '/ai/analyze-title', {'platform': 'youtube', 'title': 'How I Made $100K in 30 Days!'})
test('POST /ai/analyze-title', code == 200 and 'seo_score' in data, f'code={code}, seo_score={data.get("seo_score", "N/A")}')

if code == 200:
    test('  包含CTR预测', 'ctr_prediction' in data, f'ctr={data.get("ctr_prediction")}')
    test('  包含建议', 'suggestions' in data and isinstance(data['suggestions'], list), f'count={len(data.get("suggestions", []))}')

code, data = api_post(API + '/ai/analyze-niche', {'keyword': 'cooking', 'platform': 'youtube'})
test('POST /ai/analyze-niche', code == 200 and 'recommendations' in data, f'code={code}')

if code == 200 and isinstance(data.get('recommendations'), list) and len(data['recommendations']) > 0:
    test('  赛道推荐有数据', len(data['recommendations']) > 0, f'count={len(data["recommendations"])}')

code, data = api_post(API + '/ai/predict-trend', {'platform': 'youtube'})
test('POST /ai/predict-trend', code == 200 and 'trends' in data, f'code={code}')

if code == 200 and isinstance(data.get('trends'), list) and len(data['trends']) > 0:
    test('  趋势预测有数据', len(data['trends']) > 0, f'count={len(data["trends"])}')
    first = data['trends'][0]
    test('  趋势包含关键词', 'keyword' in first or 'name' in first, f'keys={sorted(first.keys())[:6]}')

code, data = api_post(API + '/ai/calculate-revenue', {'platform': 'youtube', 'views': 1000000, 'category': 'entertainment', 'region': 'us'})
test('POST /ai/calculate-revenue', code == 200 and 'total_ad_revenue' in data, f'code={code}, revenue={data.get("total_ad_revenue", "N/A")}')

if code == 200:
    test('  包含创作者分成', 'creator_share' in data, f'share={data.get("creator_share", "N/A")}')

# ===== 5. 采集 API =====
print('\n=== 5. 采集 API ===')
code, data = api_post(API + '/crawl/seed-demo')
test('POST /crawl/seed-demo', code == 200, f'code={code}, msg={str(data)[:80]}')

code, data = api_post(API + '/crawl/youtube?type=popular&max_results=5')
test('POST /crawl/youtube', code == 200, f'code={code}, msg={str(data)[:80]}')

code, data = api_post(API + '/crawl/tiktok?type=trending&max_results=5')
test('POST /crawl/tiktok', code == 200, f'code={code}, msg={str(data)[:80]}')

# ===== 6. 参数验证 =====
print('\n=== 6. 参数验证 ===')
code, data = api_get(API + '/videos/top-viewed?platform=invalid_platform')
test('无效平台参数 → 422', code == 422, f'code={code}')

code, data = api_get(API + '/videos/top-viewed?limit=0')
test('limit=0 → 422', code == 422, f'code={code}')

code, data = api_get(API + '/videos/top-viewed?limit=999')
test('limit=999 → 422', code == 422, f'code={code}')

code, data = api_get(API + '/analytics/viral?min_views=999999999')
test('极高min_views → 空列表', code == 200 and isinstance(data, list) and len(data) == 0, f'count={len(data) if isinstance(data, list) else "N/A"}')

code, data = api_get(API + '/nonexistent')
test('不存在端点 → 404', code == 404, f'code={code}')

# ===== 7. 数据一致性 =====
print('\n=== 7. 数据一致性 ===')
code, top = api_get(API + '/videos/top-viewed?limit=50&platform=youtube')
if isinstance(top, list) and len(top) > 1:
    views = [v.get('view_count', 0) for v in top]
    is_desc = all(a >= b for a, b in zip(views, views[1:]))
    test('YouTube排行降序', is_desc, f'top={views[0]}, bottom={views[-1]}')
else:
    test('YouTube排行降序', False, '数据不足')

code, top = api_get(API + '/videos/top-viewed?limit=50&platform=tiktok')
if isinstance(top, list) and len(top) > 1:
    views = [v.get('view_count', 0) for v in top]
    is_desc = all(a >= b for a, b in zip(views, views[1:]))
    test('TikTok排行降序', is_desc, f'top={views[0]}, bottom={views[-1]}')
else:
    test('TikTok排行降序', False, '数据不足')

code, viral = api_get(API + '/analytics/viral?limit=10')
if isinstance(viral, list) and len(viral) > 1:
    scores = [v.get('viral_score', 0) for v in viral]
    is_desc = all(a >= b for a, b in zip(scores, scores[1:]))
    test('爆红指数降序', is_desc, f'top={scores[0]:.1f}, bottom={scores[-1]:.1f}')
else:
    test('爆红指数降序', False, '数据不足')

code, rev = api_get(API + '/analytics/revenue?limit=10')
if isinstance(rev, list) and len(rev) > 1:
    revenues = [v.get('estimated_revenue_mid', 0) for v in rev]
    is_desc = all(a >= b for a, b in zip(revenues, revenues[1:]))
    test('收入排行降序', is_desc, f'top={revenues[0]:.0f}, bottom={revenues[-1]:.0f}')
else:
    test('收入排行降序', False, '数据不足')

# ===== 8. 前端页面 =====
print('\n=== 8. 前端页面 ===')
frontend_base = 'http://localhost:5175'

try:
    import subprocess
    result = subprocess.run(
        ['powershell', '-Command', '(Invoke-WebRequest -Uri http://localhost:5175/ -UseBasicParsing -TimeoutSec 5).StatusCode'],
        capture_output=True, text=True, timeout=10
    )
    fe_code = int(result.stdout.strip()) if result.stdout.strip() else 0
    test('前端首页加载', fe_code == 200, f'code={fe_code}')
except Exception as e:
    test('前端首页加载', False, f'error={e}')

# ===== 汇总 =====
print('\n' + '=' * 60)
passed = sum(1 for _, c, _ in results if c)
failed = sum(1 for _, c, _ in results if not c)
total = len(results)
print(f'测试结果: {passed}/{total} 通过, {failed} 失败')
if failed > 0:
    print('\n❌ 失败项:')
    for name, cond, detail in results:
        if not cond:
            print(f'  • {name} — {detail}')
print('=' * 60)
sys.exit(0 if failed == 0 else 1)
