<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">🕷️ 数据采集</h1>
      <p class="page-subtitle">手动触发 YouTube / TikTok 数据抓取任务</p>
    </div>

    <div class="card config-status-card">
      <h3 class="section-title">🔐 API 配置状态</h3>
      <div class="config-grid">
        <div class="config-item">
          <span class="config-label">YouTube API</span>
          <span class="config-value" :class="configStatus.youtube_api_key_configured ? 'success' : 'error'">
            {{ configStatus.youtube_api_key_configured ? '✓ 已配置' : '✗ 未配置' }}
          </span>
        </div>
        <div class="config-item">
          <span class="config-label">TikHub API</span>
          <span class="config-value" :class="configStatus.tikhub_api_key_configured ? 'success' : 'warning'">
            {{ configStatus.tikhub_api_key_configured ? '✓ 已配置' : '○ 未配置 (可选)' }}
          </span>
        </div>
      </div>
      <button class="btn btn-sm" @click="loadConfigStatus">🔄 刷新状态</button>
    </div>

    <div class="demo-section">
      <button class="btn btn-accent" @click="resetAndCrawl" :disabled="resetting">
        {{ resetting ? '⏳ 采集中...' : '🔄 重置并采集真实数据' }}
      </button>
      <span class="demo-hint">清除现有数据，使用配置的 API Keys 获取真实数据</span>
    </div>

    <div class="demo-section">
      <button class="btn btn-secondary" @click="seedDemo" :disabled="seeding">
        {{ seeding ? '⏳ 生成中...' : '🎲 生成演示数据' }}
      </button>
      <span class="demo-hint">无需 API Key，一键生成模拟数据体验功能</span>
    </div>

    <div class="demo-section">
      <button class="btn btn-primary" @click="calculateRevenue" :disabled="calculating">
        {{ calculating ? '⏳ 计算中...' : '💰 计算收入估算' }}
      </button>
      <span class="demo-hint">为所有视频计算收入估算数据</span>
    </div>

    <div class="demo-section">
      <button class="btn btn-danger" @click="cleanupInvalid" :disabled="cleaning">
        {{ cleaning ? '⏳ 检测中...' : '🗑️ 清理失效视频' }}
      </button>
      <span class="demo-hint">检测并删除链接失效的视频（仅YouTube）</span>
    </div>

    <div v-if="cleanupResult" class="card cleanup-result">
      <h3 class="section-title">📊 清理结果</h3>
      <div class="result-grid">
        <div class="result-item">
          <div class="result-label">检测总数</div>
          <div class="result-value">{{ cleanupResult.total_checked }}</div>
        </div>
        <div class="result-item">
          <div class="result-label">有效视频</div>
          <div class="result-value success">{{ cleanupResult.valid_count }}</div>
        </div>
        <div class="result-item">
          <div class="result-label">失效视频</div>
          <div class="result-value error">{{ cleanupResult.invalid_count }}</div>
        </div>
        <div class="result-item">
          <div class="result-label">状态</div>
          <div class="result-value" :class="cleanupResult.deleted ? 'success' : 'info'">
            {{ cleanupResult.deleted ? '已删除' : '仅检测' }}
          </div>
        </div>
      </div>
      <div v-if="cleanupResult.invalid_videos && cleanupResult.invalid_videos.length > 0" class="invalid-list">
        <h4>失效视频列表：</h4>
        <div v-for="v in cleanupResult.invalid_videos" :key="v.id" class="invalid-item">
          <span class="invalid-platform">{{ v.platform === 'youtube' ? 'YT' : 'TT' }}</span>
          <span class="invalid-title">{{ v.title }}</span>
          <span class="invalid-reason">{{ v.reason }}</span>
        </div>
      </div>
    </div>

    <div class="task-grid">
      <div class="card task-card">
        <div class="task-header">
          <span class="platform-dot youtube-dot"></span>
          <h3 class="section-title">YouTube 采集</h3>
        </div>
        <div class="task-body">
          <div class="form-group">
            <label>采集类型</label>
            <select v-model="ytTask.type">
              <option value="popular">热门视频</option>
              <option value="trending">趋势视频</option>
              <option value="category">分类视频</option>
            </select>
          </div>
          <div class="form-group">
            <label>区域代码</label>
            <input v-model="ytTask.region" placeholder="如 US, JP, KR" />
          </div>
          <div class="form-group">
            <label>最大数量</label>
            <input v-model.number="ytTask.max_results" type="number" placeholder="50" />
          </div>
          <button class="btn btn-primary" @click="startYoutube" :disabled="ytRunning">
            {{ ytRunning ? '⏳ 采集中...' : '▶ 开始采集' }}
          </button>
        </div>
      </div>

      <div class="card task-card">
        <div class="task-header">
          <span class="platform-dot tiktok-dot"></span>
          <h3 class="section-title">TikTok 采集</h3>
        </div>
        <div class="task-body">
          <div class="form-group">
            <label>采集类型</label>
            <select v-model="ttTask.type">
              <option value="trending">热门视频</option>
              <option value="hashtag">话题标签</option>
              <option value="user">用户视频</option>
            </select>
          </div>
          <div class="form-group">
            <label>关键词/标签</label>
            <input v-model="ttTask.keyword" placeholder="如 dance, comedy" />
          </div>
          <div class="form-group">
            <label>最大数量</label>
            <input v-model.number="ttTask.max_results" type="number" placeholder="50" />
          </div>
          <button class="btn btn-primary" @click="startTiktok" :disabled="ttRunning">
            {{ ttRunning ? '⏳ 采集中...' : '▶ 开始采集' }}
          </button>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="section-title">📋 采集日志</h3>
      <div v-if="logs.length === 0" class="empty-state" style="padding: 40px;">
        <div class="empty-icon">📝</div>
        <p>暂无采集记录</p>
      </div>
      <div v-else class="log-list">
        <div v-for="(log, i) in logs" :key="i" class="log-item" :class="log.status">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-badge" :class="log.status">{{ log.status === 'success' ? '✓' : '✗' }}</span>
          <span class="log-msg">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { tasksApi, videosApi } from '../api'

export default {
  name: 'Crawl',
  data() {
    return {
      configStatus: {
        youtube_api_key_configured: false,
        youtube_api_key_length: 0,
        youtube_api_enabled: false,
        tikhub_api_key_configured: false,
        tikhub_api_key_length: 0,
        tikhub_enabled: false,
      },
      ytTask: {
        type: 'popular',
        region: 'US',
        max_results: 50,
      },
      ttTask: {
        type: 'trending',
        keyword: '',
        max_results: 50,
      },
      ytRunning: false,
      ttRunning: false,
      seeding: false,
      resetting: false,
      calculating: false,
      cleaning: false,
      cleanupResult: null,
      logs: [],
    }
  },
  mounted() {
    this.loadConfigStatus()
  },
  methods: {
    async loadConfigStatus() {
      try {
        const res = await tasksApi.getConfigStatus()
        this.configStatus = res.data
      } catch (e) {
        console.error('加载配置状态失败:', e)
      }
    },
    async calculateRevenue() {
      this.calculating = true
      const startTime = new Date().toLocaleTimeString()
      try {
        const res = await tasksApi.calculateRevenue()
        this.logs.unshift({
          time: startTime,
          status: 'success',
          message: res.data.message || `收入估算完成`,
        })
      } catch (e) {
        this.logs.unshift({
          time: startTime,
          status: 'error',
          message: `收入估算失败: ${e.response?.data?.detail || e.message}`,
        })
      } finally {
        this.calculating = false
      }
    },
    async startYoutube() {
      this.ytRunning = true
      const startTime = new Date().toLocaleTimeString()
      try {
        const res = await tasksApi.startCrawl('youtube', this.ytTask)
        this.logs.unshift({
          time: startTime,
          status: 'success',
          message: res.data.message || `YouTube ${this.ytTask.type} 采集完成`,
        })
      } catch (e) {
        this.logs.unshift({
          time: startTime,
          status: 'error',
          message: `YouTube 采集失败: ${e.response?.data?.detail || e.message}`,
        })
      } finally {
        this.ytRunning = false
      }
    },
    async startTiktok() {
      this.ttRunning = true
      const startTime = new Date().toLocaleTimeString()
      try {
        const res = await tasksApi.startCrawl('tiktok', this.ttTask)
        this.logs.unshift({
          time: startTime,
          status: 'success',
          message: res.data.message || `TikTok ${this.ttTask.type} 采集完成`,
        })
      } catch (e) {
        this.logs.unshift({
          time: startTime,
          status: 'error',
          message: `TikTok 采集失败: ${e.response?.data?.detail || e.message}`,
        })
      } finally {
        this.ttRunning = false
      }
    },
    async seedDemo() {
      this.seeding = true
      const startTime = new Date().toLocaleTimeString()
      try {
        const res = await tasksApi.seedDemo()
        this.logs.unshift({
          time: startTime,
          status: 'success',
          message: res.data.message || '演示数据生成完成',
        })
      } catch (e) {
        this.logs.unshift({
          time: startTime,
          status: 'error',
          message: `演示数据生成失败: ${e.response?.data?.detail || e.message}`,
        })
      } finally {
        this.seeding = false
      }
    },
    async resetAndCrawl() {
      this.resetting = true
      const startTime = new Date().toLocaleTimeString()
      try {
        const res = await tasksApi.resetAndCrawl()
        const data = res.data
        let msg = data.message
        if (data.results) {
          msg += ` (YouTube: ${data.results.youtube}条, TikTok: ${data.results.tiktok}条)`
        }
        if (data.results?.errors?.length > 0) {
          msg += ` 错误: ${data.results.errors.join(', ')}`
        }
        this.logs.unshift({
          time: startTime,
          status: data.results?.youtube > 0 || data.results?.tiktok > 0 ? 'success' : 'error',
          message: msg,
        })
      } catch (e) {
        this.logs.unshift({
          time: startTime,
          status: 'error',
          message: `重置采集失败: ${e.response?.data?.detail || e.message}`,
        })
      } finally {
        this.resetting = false
      }
    },
    async cleanupInvalid() {
      this.cleaning = true
      this.cleanupResult = null
      const startTime = new Date().toLocaleTimeString()
      try {
        const res = await videosApi.cleanupInvalid({ dry_run: false })
        this.cleanupResult = res.data
        this.logs.unshift({
          time: startTime,
          status: res.data.invalid_count > 0 ? 'warning' : 'success',
          message: `清理完成: 检测${res.data.total_checked}个视频，发现${res.data.invalid_count}个失效`,
        })
      } catch (e) {
        this.logs.unshift({
          time: startTime,
          status: 'error',
          message: `清理失败: ${e.response?.data?.detail || e.message}`,
        })
      } finally {
        this.cleaning = false
      }
    },
  },
}
</script>

<style scoped>
.config-status-card {
  margin-bottom: 20px;
  padding: 20px;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.config-label {
  font-weight: 600;
  color: #475569;
}

.config-value {
  font-weight: 700;
  font-size: 13px;
}

.config-value.success {
  color: #059669;
}

.config-value.error {
  color: #dc2626;
}

.config-value.warning {
  color: #f59e0b;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-sm:hover {
  background: #e2e8f0;
}

.demo-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 18px 22px;
  background: linear-gradient(135deg, #faf5ff, #eef2ff);
  border: 1px solid #e9d5ff;
  border-radius: 14px;
}

.demo-hint {
  font-size: 13px;
  color: #64748b;
}

.task-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.task-card {
  min-height: 280px;
}

.task-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.platform-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.youtube-dot {
  background: #dc2626;
}

.tiktok-dot {
  background: #0d9488;
}

.task-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: #64748b;
}

.form-group select,
.form-group input {
  padding: 10px 16px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #1e293b;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.2s;
}
.form-group select:focus,
.form-group input:focus {
  outline: none;
  border-color: #818cf8;
  box-shadow: 0 0 0 3px rgba(129,140,248,0.15);
}
.form-group input::placeholder {
  color: #94a3b8;
}

.log-list {
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 4px;
  font-size: 13px;
  transition: background 0.2s;
}
.log-item:hover {
  background: #f8fafc;
}

.log-time {
  color: #94a3b8;
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

.log-badge {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}
.log-badge.success {
  background: #dcfce7;
  color: #059669;
}
.log-badge.error {
  background: #fee2e2;
  color: #dc2626;
}

.log-msg {
  color: #475569;
}

.cleanup-result {
  margin-bottom: 20px;
}

.cleanup-result .result-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.cleanup-result .result-item {
  text-align: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.cleanup-result .result-label {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 8px;
}

.cleanup-result .result-value {
  font-size: 24px;
  font-weight: 800;
  color: #1e293b;
}

.cleanup-result .result-value.success {
  color: #059669;
}

.cleanup-result .result-value.error {
  color: #dc2626;
}

.cleanup-result .result-value.info {
  color: #6366f1;
}

.invalid-list {
  margin-top: 16px;
}

.invalid-list h4 {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 12px;
}

.invalid-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #fef2f2;
  border-radius: 8px;
  margin-bottom: 6px;
}

.invalid-platform {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 700;
  background: #dc2626;
  color: white;
}

.invalid-title {
  flex: 1;
  font-size: 13px;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.invalid-id {
  font-size: 11px;
  color: #94a3b8;
}

.invalid-reason {
  font-size: 11px;
  color: #dc2626;
  font-weight: 600;
  background: #fef2f2;
  padding: 2px 8px;
  border-radius: 4px;
}

.btn-danger {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .task-grid {
    grid-template-columns: 1fr;
  }
  .demo-section {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
