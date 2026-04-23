<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">🏆 播放排行</h1>
      <p class="page-subtitle">YouTube & TikTok 播放量最高的视频排名，含收入估算明细</p>
    </div>

    <div class="filter-bar">
      <select v-model="platform">
        <option value="">全部平台</option>
        <option value="youtube">YouTube</option>
        <option value="tiktok">TikTok</option>
      </select>
      <select v-model="limit">
        <option value="20">Top 20</option>
        <option value="50">Top 50</option>
        <option value="100">Top 100</option>
      </select>
      <button class="btn btn-primary" @click="loadData" :disabled="loading">🔄 刷新数据</button>
    </div>

    <div class="card">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="videos.length === 0" class="empty-state">
        <div class="empty-icon">🏆</div>
        <p>暂无数据，请先到数据采集页面抓取</p>
      </div>
      <div v-else class="table-wrapper topviewed-table-wrapper">
        <table class="video-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>平台</th>
              <th>视频</th>
              <th>播放量</th>
              <th>点赞</th>
              <th>发布时间</th>
              <th>收入明细</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="v in videos" :key="v.id">
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
              <td class="data-value">{{ formatNumber(v.view_count) }}</td>
              <td class="data-value">{{ formatNumber(v.like_count) }}</td>
              <td class="data-value">{{ formatTimeAgo(v.published_at) }}</td>
              <td class="revenue-cell">
                <span class="revenue-main">${{ formatRevenue(v.estimated_revenue_mid) }}</span>
                <span class="revenue-range">${{ formatRevenue(v.estimated_revenue_low) }} ~ ${{ formatRevenue(v.estimated_revenue_high) }}</span>
                <span class="revenue-detail">广告 ${{ formatRevenue(v.ad_revenue) }} · 分成 ${{ formatRevenue(v.creator_share_amount) }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { videosApi } from '../api'

export default {
  name: 'TopViewed',
  data() {
    return {
      videos: [],
      platform: '',
      limit: '50',
      loading: false,
    }
  },
  mounted() {
    console.log('[TopViewed] Component mounted, calling loadData...')
    this.loadData()
  },
  watch: {
    platform(newVal, oldVal) {
      if (oldVal !== undefined) {
        this.loadData()
      }
    },
    limit(newVal, oldVal) {
      if (oldVal !== undefined) {
        this.loadData()
      }
    },
  },
  methods: {
    async loadData() {
      console.log('[TopViewed] loadData called, platform:', this.platform, 'limit:', this.limit)
      this.loading = true
      try {
        const params = { limit: parseInt(this.limit) }
        if (this.platform) params.platform = this.platform
        console.log('[TopViewed] API params:', params)
        console.log('[TopViewed] Calling API...')
        const res = await videosApi.getTopViewed(params)
        console.log('[TopViewed] API response status:', res.status)
        console.log('[TopViewed] API response data:', res.data)
        console.log('[TopViewed] API response length:', res.data?.length)
        this.videos = res.data || []
        console.log('[TopViewed] videos set to:', this.videos.length, 'items')
      } catch (e) {
        console.error('[TopViewed] 加载失败:', e)
        console.error('[TopViewed] Error details:', e.message, e.stack)
      } finally {
        this.loading = false
        console.log('[TopViewed] Loading complete, videos:', this.videos.length)
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
.topviewed-table-wrapper table {
  min-width: 1200px;
}

.revenue-cell {
  white-space: nowrap;
}
.revenue-main {
  color: #059669;
  font-weight: 700;
}
.revenue-range {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}
.revenue-detail {
  display: block;
  font-size: 10px;
  color: #94a3b8;
  margin-top: 1px;
}
</style>
