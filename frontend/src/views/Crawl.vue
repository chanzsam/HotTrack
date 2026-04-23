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
import { tasksApi } from '../api'

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
