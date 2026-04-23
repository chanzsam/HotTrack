<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">💰 收入估算</h1>
      <p class="page-subtitle">基于播放量和平台 CPM 估算视频广告收入</p>
    </div>

    <div class="info-box">
      <p>💡 收入估算基于平台平均 CPM（每千次展示费用）。YouTube CPM $1.5~$15，创作者分成 55%；TikTok CPM $0.5~$6，创作者分成 50%。实际收入受内容类别、地区、观众群体等因素影响，仅供参考。</p>
    </div>

    <div class="card">
      <h3 class="section-title">快速估算</h3>
      <div class="calc-form">
        <div class="form-group">
          <label>平台</label>
          <select v-model="calcForm.platform">
            <option value="youtube">YouTube</option>
            <option value="tiktok">TikTok</option>
          </select>
        </div>
        <div class="form-group">
          <label>播放量</label>
          <input v-model.number="calcForm.views" type="number" placeholder="输入播放量" />
        </div>
        <div class="form-group">
          <label>CPM (USD)</label>
          <input v-model.number="calcForm.cpm" type="number" step="0.5" placeholder="每千次展示费用" />
        </div>
        <button class="btn btn-primary" @click="calculate" :disabled="!calcForm.views">计算收入</button>
      </div>
      <div v-if="calcResult" class="result-box">
        <div class="result-grid">
          <div class="result-item">
            <div class="result-label">变现播放量</div>
            <div class="result-value">{{ formatNumber(calcResult.monetized_views) }}</div>
          </div>
          <div class="result-item">
            <div class="result-label">广告总收入</div>
            <div class="result-value">${{ formatRevenue(calcResult.total_ad_revenue) }}</div>
          </div>
          <div class="result-item">
            <div class="result-label">创作者分成 ({{ (calcResult.creator_share_rate * 100).toFixed(0) }}%)</div>
            <div class="result-value highlight">${{ formatRevenue(calcResult.creator_share) }}</div>
          </div>
          <div class="result-item">
            <div class="result-label">收入范围</div>
            <div class="result-value">${{ formatRevenue(calcResult.low) }} ~ ${{ formatRevenue(calcResult.high) }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="section-title">视频收入排行</h3>
      <div class="filter-bar" style="margin-bottom: 16px;">
        <select v-model="platform">
          <option value="">全部平台</option>
          <option value="youtube">YouTube</option>
          <option value="tiktok">TikTok</option>
        </select>
        <button class="btn btn-secondary" @click="loadRanking" :disabled="loadingRanking">🔄 刷新</button>
      </div>
      <div v-if="loadingRanking" class="loading">加载中...</div>
      <div v-else-if="revenueRanking.length === 0" class="empty-state">
        <div class="empty-icon">💰</div>
        <p>暂无收入数据，请先采集视频数据</p>
      </div>
      <div v-else class="table-wrapper revenue-table-wrapper">
        <table class="video-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>平台</th>
              <th>视频</th>
              <th>播放量</th>
              <th>CPM</th>
              <th>发布时间</th>
              <th>广告收入</th>
              <th>创作者分成</th>
              <th>预估收入</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="v in revenueRanking" :key="v.id">
              <td><span class="rank-number data-value">{{ v.rank }}</span></td>
              <td>
                <span class="platform-badge" :class="v.platform">{{ v.platform === 'youtube' ? 'YT' : 'TT' }}</span>
              </td>
              <td>
                <div class="video-info">
                  <img :src="v.thumbnail_url" class="video-thumb" @error="handleImgError" />
                  <div>
                    <a :href="v.video_url" target="_blank" class="video-title" :title="v.title">{{ v.title }}</a>
                    <div class="video-channel">{{ v.channel_title }}</div>
                  </div>
                </div>
              </td>
              <td class="data-value">
                {{ formatNumber(v.view_count) }}
                <span class="revenue-detail">变现 {{ formatNumber(v.monetized_views) }}</span>
              </td>
              <td class="data-value">${{ v.estimated_cpm?.toFixed(2) }}</td>
              <td class="data-value">{{ formatTimeAgo(v.published_at) }}</td>
              <td class="data-value">${{ formatRevenue(v.ad_revenue) }}</td>
              <td class="data-value">${{ formatRevenue(v.creator_share_amount) }}</td>
              <td class="revenue-cell">
                <span class="revenue-main">${{ formatRevenue(v.estimated_revenue_mid) }}</span>
                <span class="revenue-range">${{ formatRevenue(v.estimated_revenue_low) }} ~ ${{ formatRevenue(v.estimated_revenue_high) }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { analyticsApi } from '../api'

export default {
  name: 'Revenue',
  data() {
    return {
      calcForm: {
        platform: 'youtube',
        views: null,
        cpm: null,
      },
      calcResult: null,
      revenueRanking: [],
      platform: '',
      loadingRanking: false,
    }
  },
  mounted() {
    this.loadRanking()
  },
  watch: {
    platform(newVal, oldVal) {
      if (oldVal !== undefined) {
        this.loadRanking()
      }
    },
  },
  methods: {
    calculate() {
      if (!this.calcForm.views) return
      const isYoutube = this.calcForm.platform === 'youtube'
      const cpm = this.calcForm.cpm || (isYoutube ? 7.5 : 2.0)
      const monetizationRate = isYoutube ? 0.55 : 0.30
      const creatorShareRate = isYoutube ? 0.55 : 0.50

      const monetizedViews = Math.floor(this.calcForm.views * monetizationRate)
      const totalAdRevenue = (monetizedViews / 1000) * cpm
      const creatorShare = totalAdRevenue * creatorShareRate

      this.calcResult = {
        monetized_views: monetizedViews,
        total_ad_revenue: totalAdRevenue,
        creator_share: creatorShare,
        creator_share_rate: creatorShareRate,
        low: totalAdRevenue * creatorShareRate * 0.4,
        high: totalAdRevenue * creatorShareRate * 1.8,
      }
    },
    async loadRanking() {
      console.log('[Revenue] loadRanking called, platform:', this.platform)
      this.loadingRanking = true
      try {
        const params = { limit: 50 }
        if (this.platform) params.platform = this.platform
        console.log('[Revenue] API params:', params)
        const res = await analyticsApi.getRevenueRanking(params)
        console.log('[Revenue] API response:', res.data.length, 'videos')
        this.revenueRanking = res.data
      } catch (e) {
        console.error('[Revenue] 加载失败:', e)
      } finally {
        this.loadingRanking = false
      }
    },
    formatNumber(num) {
      if (!num) return '0'
      if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B'
      if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M'
      if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K'
      return num.toString()
    },
    formatRevenue(num) {
      if (!num) return '0'
      if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M'
      if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K'
      return num.toFixed(2)
    },
    formatTimeAgo(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      if (diffMs < 0) return '刚刚'
      const diffSeconds = Math.floor(diffMs / 1000)
      const diffMinutes = Math.floor(diffSeconds / 60)
      const diffHours = Math.floor(diffMinutes / 60)
      if (diffMinutes < 1) return '刚刚'
      if (diffHours < 1) return diffMinutes + '分钟前'
      if (diffHours < 24) return diffHours + '小时前'
      const diffDays = Math.floor(diffHours / 24)
      if (diffDays < 30) return diffDays + '天前'
      const diffMonths = Math.floor(diffDays / 30)
      if (diffMonths < 12) return diffMonths + '个月前'
      return Math.floor(diffMonths / 12) + '年前'
    },
    handleImgError(e) {
      e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="96" height="54"><rect fill="%23f1f5f9" width="96" height="54" rx="8"/></svg>'
    },
  },
}
</script>

<style scoped>
.calc-form {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
  margin-bottom: 4px;
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
  min-width: 140px;
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

.result-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.result-item {
  text-align: center;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.result-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.result-value {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
}

.result-value.highlight {
  color: #059669;
}

.revenue-cell {
  white-space: nowrap;
  text-align: right;
}

.revenue-main {
  color: #059669;
  font-weight: 700;
  font-size: 13px;
}

.revenue-range {
  display: none;
}

.revenue-detail {
  display: none;
}

@media (max-width: 768px) {
  .result-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
