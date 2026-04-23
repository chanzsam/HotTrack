<template>
  <div class="dashboard-page page-fullwidth">
    <section class="hero">
      <div class="section-inner hero-inner">
        <div class="hero-content">
          <h1 class="hero-title">YouTube & TikTok 热门视频<span class="gradient-text">智能分析</span></h1>
          <p class="hero-desc">用 AI 驱动你的视频分析。从热门追踪到收入估算，AI 全流程助力数据洞察。一键查看排行榜、趋势分析、爆红追踪，让创作更高效。</p>
          <div class="hero-actions">
            <router-link to="/top-viewed" class="btn btn-primary btn-lg">查看排行榜</router-link>
            <router-link to="/ai-tools" class="btn btn-accent btn-lg">✨ AI 工具箱</router-link>
          </div>
        </div>
        <div class="hero-visual">
          <div class="visual-card">
            <div class="visual-icon">🔥</div>
            <div class="visual-label">实时热门</div>
          </div>
          <div class="visual-card">
            <div class="visual-icon">💰</div>
            <div class="visual-label">收入估算</div>
          </div>
          <div class="visual-card">
            <div class="visual-icon">🚀</div>
            <div class="visual-label">爆红追踪</div>
          </div>
        </div>
      </div>
    </section>

    <section class="steps-section">
      <div class="section-inner">
        <h2 class="section-heading">三步开始分析</h2>
        <div class="steps-grid">
          <div class="step-card">
            <div class="step-num">01</div>
            <h3 class="step-title">数据采集</h3>
            <p class="step-desc">一键抓取 YouTube 和 TikTok 热门视频数据，自动存储播放量、点赞数、评论数等关键指标</p>
          </div>
          <div class="step-arrow">→</div>
          <div class="step-card">
            <div class="step-num">02</div>
            <h3 class="step-title">AI 分析</h3>
            <p class="step-desc">AI 自动计算排行榜、爆红指数、收入估算，生成可执行的数据洞察和优化建议</p>
          </div>
          <div class="step-arrow">→</div>
          <div class="step-card">
            <div class="step-num">03</div>
            <h3 class="step-title">洞察发现</h3>
            <p class="step-desc">查看多维度排行榜、收入明细、趋势变化，发现下一个爆款机会</p>
          </div>
        </div>
      </div>
    </section>

    <section class="tools-section">
      <div class="section-inner">
        <h2 class="section-heading">热门视频分析工具箱</h2>
        <p class="section-desc">数据采集完成后，随时使用这些工具进行深度分析</p>
        <div class="tools-grid">
          <router-link to="/top-viewed" class="tool-card">
            <div class="tool-icon">🏆</div>
            <h3 class="tool-name">播放排行</h3>
            <p class="tool-desc">查看 YouTube & TikTok 播放量最高的视频，含收入估算</p>
          </router-link>
          <router-link to="/trending" class="tool-card">
            <div class="tool-icon">📈</div>
            <h3 class="tool-name">热门趋势</h3>
            <p class="tool-desc">追踪当前最热门的视频趋势和增长速度</p>
          </router-link>
          <router-link to="/viral" class="tool-card">
            <div class="tool-icon">🚀</div>
            <h3 class="tool-name">爆红追踪</h3>
            <p class="tool-desc">发现爆红速度最快的视频，计算爆红指数</p>
          </router-link>
          <router-link to="/revenue" class="tool-card">
            <div class="tool-icon">💰</div>
            <h3 class="tool-name">收入估算</h3>
            <p class="tool-desc">基于 CPM 和播放量估算视频广告收入和创作者分成</p>
          </router-link>
          <router-link to="/ai-tools" class="tool-card tool-card-ai">
            <div class="tool-icon">✨</div>
            <h3 class="tool-name">AI 标题评分</h3>
            <p class="tool-desc">AI 分析视频标题 SEO 得分和点击率预测</p>
          </router-link>
          <router-link to="/ai-tools" class="tool-card tool-card-ai">
            <div class="tool-icon">🎯</div>
            <h3 class="tool-name">赛道推荐</h3>
            <p class="tool-desc">AI 推荐最佳内容赛道和增长机会</p>
          </router-link>
        </div>
      </div>
    </section>

    <section class="stats-section">
      <div class="section-inner">
        <h2 class="section-heading">数据概览</h2>
        <div class="stat-grid">
          <div class="stat-card">
            <div class="stat-value data-value">{{ stats.youtube.total_videos }}</div>
            <div class="stat-label">YouTube 视频数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value data-value">{{ formatNumber(stats.youtube.total_views) }}</div>
            <div class="stat-label">YouTube 总播放量</div>
          </div>
          <div class="stat-card stat-card-revenue">
            <div class="stat-value data-value">${{ formatRevenue(stats.youtube.total_estimated_revenue) }}</div>
            <div class="stat-label">YouTube 预估收入</div>
          </div>
          <div class="stat-card">
            <div class="stat-value data-value">{{ stats.tiktok.total_videos }}</div>
            <div class="stat-label">TikTok 视频数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value data-value">{{ formatNumber(stats.tiktok.total_views) }}</div>
            <div class="stat-label">TikTok 总播放量</div>
          </div>
          <div class="stat-card stat-card-revenue">
            <div class="stat-value data-value">${{ formatRevenue(stats.tiktok.total_estimated_revenue) }}</div>
            <div class="stat-label">TikTok 预估收入</div>
          </div>
        </div>
      </div>
    </section>

    <section class="ranking-section">
      <div class="section-inner">
        <div class="dual-panel">
          <div class="card panel-card">
            <div class="panel-header">
              <span class="platform-dot youtube-dot"></span>
              <h3 class="section-title">YouTube Top 10</h3>
            </div>
            <div v-if="loadingYoutube" class="loading">加载中...</div>
            <div v-else-if="youtubeTop.length === 0" class="empty-state">
              <div class="empty-icon">▶️</div>
              <p>暂无数据，请先到数据采集页面抓取</p>
            </div>
            <div v-else class="table-wrapper">
              <table class="video-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>视频</th>
                    <th>播放量</th>
                    <th>预估收入</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="v in youtubeTop" :key="v.id">
                    <td><span class="rank-number data-value">{{ v.rank }}</span></td>
                    <td>
                      <div class="video-info">
                        <img :src="v.thumbnail_url" class="video-thumb" @error="handleImgError" />
                        <div>
                          <div class="video-title" :title="v.title">{{ v.title }}</div>
                          <div class="video-channel">{{ v.channel_title }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="data-value">{{ formatNumber(v.view_count) }}</td>
                    <td class="revenue-cell">
                      <span class="revenue-main">${{ formatRevenue(v.estimated_revenue_mid) }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="card panel-card">
            <div class="panel-header">
              <span class="platform-dot tiktok-dot"></span>
              <h3 class="section-title">TikTok Top 10</h3>
            </div>
            <div v-if="loadingTiktok" class="loading">加载中...</div>
            <div v-else-if="tiktokTop.length === 0" class="empty-state">
              <div class="empty-icon">🎵</div>
              <p>暂无数据，请先到数据采集页面抓取</p>
            </div>
            <div v-else class="table-wrapper">
              <table class="video-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>视频</th>
                    <th>播放量</th>
                    <th>预估收入</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="v in tiktokTop" :key="v.id">
                    <td><span class="rank-number data-value">{{ v.rank }}</span></td>
                    <td>
                      <div class="video-info">
                        <img :src="v.thumbnail_url" class="video-thumb" @error="handleImgError" />
                        <div>
                          <div class="video-title" :title="v.title">{{ v.title }}</div>
                          <div class="video-channel">{{ v.channel_title }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="data-value">{{ formatNumber(v.view_count) }}</td>
                    <td class="revenue-cell">
                      <span class="revenue-main">${{ formatRevenue(v.estimated_revenue_mid) }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { videosApi } from '../api'

export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {
        youtube: { total_videos: 0, total_views: 0, total_estimated_revenue: 0 },
        tiktok: { total_videos: 0, total_views: 0, total_estimated_revenue: 0 },
      },
      youtubeTop: [],
      tiktokTop: [],
      loadingYoutube: true,
      loadingTiktok: true,
    }
  },
  async mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const [statsRes, ytRes, ttRes] = await Promise.allSettled([
          videosApi.getStats(),
          videosApi.getTopViewed({ platform: 'youtube', limit: 10 }),
          videosApi.getTopViewed({ platform: 'tiktok', limit: 10 }),
        ])
        if (statsRes.status === 'fulfilled') this.stats = statsRes.value.data
        if (ytRes.status === 'fulfilled') this.youtubeTop = ytRes.value.data
        if (ttRes.status === 'fulfilled') this.tiktokTop = ttRes.value.data
      } catch (e) {
        console.error('数据加载失败:', e)
      } finally {
        this.loadingYoutube = false
        this.loadingTiktok = false
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
    handleImgError(e) {
      e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="96" height="54"><rect fill="%23f1f5f9" width="96" height="54" rx="8"/></svg>'
    },
  },
}
</script>

<style scoped>
.dashboard-page {
  width: 100%;
}

.section-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
}

.hero {
  padding: 48px 0;
  margin-bottom: 0;
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #fff 0%, #f8fafc 100%);
}

.hero::before {
  content: '';
  position: absolute;
  top: -40px;
  right: -200px;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 70%);
  pointer-events: none;
}

.hero::after {
  content: '';
  position: absolute;
  bottom: -100px;
  left: -100px;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(168,85,247,0.06) 0%, transparent 70%);
  pointer-events: none;
}

.hero-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 48px;
  position: relative;
  z-index: 1;
}

.hero-content {
  max-width: 560px;
}

.hero-title {
  font-size: 42px;
  font-weight: 900;
  line-height: 1.15;
  color: #0f172a;
  letter-spacing: -1px;
  margin-bottom: 16px;
}

.gradient-text {
  background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  font-size: 16px;
  color: #64748b;
  line-height: 1.7;
  margin-bottom: 28px;
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.btn-lg {
  padding: 14px 28px;
  font-size: 15px;
  border-radius: 12px;
}

.hero-visual {
  display: flex;
  gap: 16px;
}

.visual-card {
  width: 120px;
  height: 140px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.visual-card:nth-child(1) {
  transform: translateY(0);
}
.visual-card:nth-child(2) {
  transform: translateY(-20px);
}
.visual-card:nth-child(3) {
  transform: translateY(-8px);
}
.visual-card:hover {
  box-shadow: 0 8px 24px rgba(99,102,241,0.12);
  transform: translateY(-4px);
}

.visual-icon {
  font-size: 36px;
}

.visual-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.steps-section {
  margin-bottom: 0;
  padding: 48px 0;
  position: relative;
}

.steps-section::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 50%, #f8fafc 100%);
  z-index: -1;
}

.section-heading {
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.section-desc {
  font-size: 15px;
  color: #64748b;
  margin-bottom: 28px;
}

.steps-grid {
  display: flex;
  align-items: center;
  gap: 20px;
  justify-content: center;
}

.step-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 32px 28px;
  max-width: 280px;
  text-align: center;
  transition: all 0.2s ease;
}
.step-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  transform: translateY(-2px);
}

.step-num {
  font-size: 36px;
  font-weight: 900;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 12px;
}

.step-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}

.step-desc {
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
}

.step-arrow {
  font-size: 24px;
  color: #c7d2fe;
  font-weight: 700;
}

.tools-section {
  margin-bottom: 0;
  padding: 48px 0;
  position: relative;
}

.tools-section::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(135deg, #eef2ff 0%, #faf5ff 50%, #eef2ff 100%);
  z-index: -1;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.tool-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 28px;
  text-decoration: none;
  transition: all 0.2s ease;
  display: block;
}
.tool-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  transform: translateY(-2px);
  border-color: #c7d2fe;
}

.tool-card-ai {
  background: linear-gradient(135deg, #faf5ff, #eef2ff);
  border-color: #e9d5ff;
}
.tool-card-ai:hover {
  border-color: #c084fc;
  box-shadow: 0 4px 20px rgba(139,92,246,0.12);
}

.tool-icon {
  font-size: 32px;
  margin-bottom: 14px;
}

.tool-name {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
}

.tool-desc {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
}

.stats-section {
  margin-bottom: 0;
  padding: 40px 0;
}

.stat-card-revenue {
  background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
  border-color: #bbf7d0;
}
.stat-card-revenue .stat-value {
  color: #059669;
}

.ranking-section {
  margin-bottom: 0;
  padding: 40px 0;
}

.dual-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.panel-card {
  min-height: 400px;
}

.panel-header {
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

.revenue-cell {
  white-space: nowrap;
}

.revenue-main {
  color: #059669;
  font-weight: 700;
}

@media (max-width: 1024px) {
  .hero-inner {
    flex-direction: column;
    text-align: center;
    gap: 32px;
  }
  .hero-title {
    font-size: 32px;
  }
  .hero-actions {
    justify-content: center;
  }
  .hero-visual {
    justify-content: center;
  }
  .steps-grid {
    flex-direction: column;
  }
  .step-arrow {
    transform: rotate(90deg);
  }
  .tools-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .dual-panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .section-inner {
    padding: 0 16px;
  }
  .tools-grid {
    grid-template-columns: 1fr;
  }
}
</style>
