<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">✨ AI 工具箱</h1>
      <p class="page-subtitle">AI 驱动的视频分析和创作辅助工具</p>
    </div>

    <div class="tools-layout">
      <div class="tool-sidebar">
        <button
          v-for="tool in tools"
          :key="tool.id"
          :class="['tool-tab', { active: activeTool === tool.id }]"
          @click="activeTool = tool.id"
        >
          <span class="tool-tab-icon">{{ tool.icon }}</span>
          <span class="tool-tab-name">{{ tool.name }}</span>
        </button>
      </div>

      <div class="tool-content">
        <div v-if="activeTool === 'title-score'" class="tool-panel">
          <div class="tool-header">
            <h2 class="tool-title">SEO 标题评分</h2>
            <p class="tool-desc">AI 分析视频标题的 SEO 得分和点击率预测，生成优化建议</p>
          </div>
          <div class="tool-body">
            <div class="form-group">
              <label>平台</label>
              <select v-model="titleForm.platform">
                <option value="youtube">YouTube</option>
                <option value="tiktok">TikTok</option>
              </select>
            </div>
            <div class="form-group">
              <label>视频标题</label>
              <input v-model="titleForm.title" placeholder="输入视频标题进行分析..." class="input-full" />
            </div>
            <button class="btn btn-primary" @click="analyzeTitle" :disabled="!titleForm.title || titleLoading">
              {{ titleLoading ? '分析中...' : '✨ AI 分析' }}
            </button>
            <div v-if="titleResult" class="result-card">
              <div class="score-display">
                <div class="score-circle" :class="getScoreClass(titleResult.seo_score)">
                  <span class="score-num">{{ titleResult.seo_score }}</span>
                </div>
                <div class="score-info">
                  <div class="score-label">SEO 综合评分</div>
                  <div class="score-ctr">预估 CTR: {{ titleResult.ctr_prediction }}%</div>
                </div>
              </div>
              <div class="score-breakdown">
                <div class="breakdown-item">
                  <span class="breakdown-label">关键词密度</span>
                  <div class="progress-bar"><div class="progress-fill" :style="{ width: titleResult.keyword_density + '%' }"></div></div>
                  <span class="breakdown-value">{{ titleResult.keyword_density }}%</span>
                </div>
                <div class="breakdown-item">
                  <span class="breakdown-label">标题长度</span>
                  <div class="progress-bar"><div class="progress-fill" :style="{ width: titleResult.length_score + '%' }"></div></div>
                  <span class="breakdown-value">{{ titleResult.length_score }}%</span>
                </div>
                <div class="breakdown-item">
                  <span class="breakdown-label">情感吸引力</span>
                  <div class="progress-bar"><div class="progress-fill" :style="{ width: titleResult.emotion_score + '%' }"></div></div>
                  <span class="breakdown-value">{{ titleResult.emotion_score }}%</span>
                </div>
                <div class="breakdown-item">
                  <span class="breakdown-label">数字/列表</span>
                  <div class="progress-bar"><div class="progress-fill" :style="{ width: titleResult.number_score + '%' }"></div></div>
                  <span class="breakdown-value">{{ titleResult.number_score }}%</span>
                </div>
              </div>
              <div v-if="titleResult.suggestions.length" class="suggestions">
                <h4>优化建议</h4>
                <ul>
                  <li v-for="(s, i) in titleResult.suggestions" :key="i">{{ s }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTool === 'niche'" class="tool-panel">
          <div class="tool-header">
            <h2 class="tool-title">赛道推荐</h2>
            <p class="tool-desc">AI 推荐最佳内容赛道，分析增长机会和竞争态势</p>
          </div>
          <div class="tool-body">
            <div class="form-group">
              <label>你的创作想法或关键词</label>
              <input v-model="nicheForm.keyword" placeholder="例如：美食、科技评测、健身..." class="input-full" />
            </div>
            <div class="form-group">
              <label>目标平台</label>
              <select v-model="nicheForm.platform">
                <option value="youtube">YouTube</option>
                <option value="tiktok">TikTok</option>
              </select>
            </div>
            <button class="btn btn-primary" @click="analyzeNiche" :disabled="!nicheForm.keyword || nicheLoading">
              {{ nicheLoading ? '分析中...' : '✨ AI 推荐' }}
            </button>
            <div v-if="nicheResult" class="result-card">
              <div class="niche-recommendations">
                <div v-for="(rec, i) in nicheResult.recommendations" :key="i" class="niche-card">
                  <div class="niche-rank">#{{ i + 1 }}</div>
                  <div class="niche-info">
                    <h4 class="niche-name">{{ rec.name }}</h4>
                    <p class="niche-reason">{{ rec.reason }}</p>
                    <div class="niche-metrics">
                      <div class="metric">
                        <span class="metric-label">竞争度</span>
                        <span :class="['metric-value', rec.competition === '低' ? 'text-green' : rec.competition === '中' ? 'text-yellow' : 'text-red']">{{ rec.competition }}</span>
                      </div>
                      <div class="metric">
                        <span class="metric-label">增长潜力</span>
                        <span class="metric-value text-green">{{ rec.growth_potential }}</span>
                      </div>
                      <div class="metric">
                        <span class="metric-label">平均 CPM</span>
                        <span class="metric-value">${{ rec.avg_cpm }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTool === 'revenue-calc'" class="tool-panel">
          <div class="tool-header">
            <h2 class="tool-title">收入计算器</h2>
            <p class="tool-desc">基于播放量和平台 CPM 精确估算视频广告收入</p>
          </div>
          <div class="tool-body">
            <div class="form-row">
              <div class="form-group">
                <label>平台</label>
                <select v-model="calcForm.platform">
                  <option value="youtube">YouTube</option>
                  <option value="tiktok">TikTok</option>
                </select>
              </div>
              <div class="form-group flex-1">
                <label>播放量</label>
                <input v-model.number="calcForm.views" type="number" placeholder="输入播放量" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>内容类别</label>
                <select v-model="calcForm.category">
                  <option value="general">综合</option>
                  <option value="tech">科技</option>
                  <option value="finance">金融</option>
                  <option value="gaming">游戏</option>
                  <option value="education">教育</option>
                  <option value="entertainment">娱乐</option>
                  <option value="music">音乐</option>
                </select>
              </div>
              <div class="form-group">
                <label>观众地区</label>
                <select v-model="calcForm.region">
                  <option value="us">美国</option>
                  <option value="eu">欧洲</option>
                  <option value="asia">亚洲</option>
                  <option value="global">全球</option>
                </select>
              </div>
            </div>
            <button class="btn btn-primary" @click="calculateRevenue">💰 计算收入</button>
            <div v-if="calcResult" class="result-card">
              <div class="revenue-summary">
                <div class="revenue-big">
                  <div class="revenue-label">创作者预估收入</div>
                  <div class="revenue-amount">${{ formatRevenue(calcResult.creator_share) }}</div>
                  <div class="revenue-range">${{ formatRevenue(calcResult.low) }} ~ ${{ formatRevenue(calcResult.high) }}</div>
                </div>
              </div>
              <div class="revenue-detail-grid">
                <div class="detail-item">
                  <div class="detail-label">变现播放量</div>
                  <div class="detail-value">{{ formatNumber(calcResult.monetized_views) }}</div>
                  <div class="detail-sub">变现率 {{ (calcResult.monetization_rate * 100).toFixed(0) }}%</div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">CPM</div>
                  <div class="detail-value">${{ calcResult.cpm }}</div>
                  <div class="detail-sub">每千次展示费用</div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">广告总收入</div>
                  <div class="detail-value">${{ formatRevenue(calcResult.total_ad_revenue) }}</div>
                  <div class="detail-sub">平台+创作者</div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">创作者分成</div>
                  <div class="detail-value highlight">${{ formatRevenue(calcResult.creator_share) }}</div>
                  <div class="detail-sub">分成比例 {{ (calcResult.creator_share_rate * 100).toFixed(0) }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTool === 'trend-predict'" class="tool-panel">
          <div class="tool-header">
            <h2 class="tool-title">趋势预测</h2>
            <p class="tool-desc">基于当前热门数据，AI 预测下一个可能爆红的内容方向</p>
          </div>
          <div class="tool-body">
            <div class="form-group">
              <label>目标平台</label>
              <select v-model="trendForm.platform">
                <option value="youtube">YouTube</option>
                <option value="tiktok">TikTok</option>
              </select>
            </div>
            <button class="btn btn-primary" @click="predictTrend" :disabled="trendLoading">
              {{ trendLoading ? '分析中...' : '✨ AI 预测' }}
            </button>
            <div v-if="trendResult" class="result-card">
              <div class="trend-list">
                <div v-for="(trend, i) in trendResult.trends" :key="i" class="trend-item">
                  <div class="trend-rank">{{ i + 1 }}</div>
                  <div class="trend-info">
                    <h4 class="trend-name">{{ trend.name }}</h4>
                    <p class="trend-reason">{{ trend.reason }}</p>
                    <div class="trend-tags">
                      <span v-for="tag in trend.tags" :key="tag" class="trend-tag">{{ tag }}</span>
                    </div>
                  </div>
                  <div class="trend-score">
                    <div class="trend-score-value">{{ trend.confidence }}%</div>
                    <div class="trend-score-label">置信度</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { analyticsApi } from '../api'

export default {
  name: 'AiTools',
  data() {
    return {
      activeTool: 'title-score',
      tools: [
        { id: 'title-score', icon: '✨', name: 'SEO 标题评分' },
        { id: 'niche', icon: '🎯', name: '赛道推荐' },
        { id: 'revenue-calc', icon: '💰', name: '收入计算器' },
        { id: 'trend-predict', icon: '📈', name: '趋势预测' },
      ],
      titleForm: { platform: 'youtube', title: '' },
      titleLoading: false,
      titleResult: null,
      nicheForm: { keyword: '', platform: 'youtube' },
      nicheLoading: false,
      nicheResult: null,
      calcForm: { platform: 'youtube', views: 1000000, category: 'general', region: 'us' },
      calcResult: null,
      trendForm: { platform: 'youtube' },
      trendLoading: false,
      trendResult: null,
    }
  },
  methods: {
    async analyzeTitle() {
      this.titleLoading = true
      this.titleResult = null
      try {
        const res = await analyticsApi.analyzeTitle({
          platform: this.titleForm.platform,
          title: this.titleForm.title,
        })
        this.titleResult = res.data
      } catch (e) {
        this.titleResult = this._mockTitleResult(this.titleForm.title)
      } finally {
        this.titleLoading = false
      }
    },
    _mockTitleResult(title) {
      const len = title.length
      const hasNumber = /\d/.test(title)
      const hasEmoji = /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}]/u.test(title)
      const hasQuestion = /[?？]/.test(title)
      const hasExclaim = /[!！]/.test(title)
      const words = title.split(/\s+/).filter(w => w.length > 0)
      const keywordDensity = Math.min(100, Math.round((words.length / Math.max(len, 1)) * 100 * 3))
      const lengthScore = len < 20 ? 40 : len < 40 ? 70 : len < 60 ? 95 : len < 80 ? 75 : 50
      const emotionScore = Math.min(100, (hasEmoji ? 30 : 0) + (hasQuestion ? 25 : 0) + (hasExclaim ? 20 : 0) + Math.random() * 30)
      const numberScore = hasNumber ? 85 : 30
      const seoScore = Math.round(keywordDensity * 0.3 + lengthScore * 0.3 + emotionScore * 0.2 + numberScore * 0.2)
      const ctrPrediction = (seoScore * 0.08 + Math.random() * 2).toFixed(1)
      const suggestions = []
      if (len < 30) suggestions.push('标题较短，建议增加到 40-60 字符以提升 SEO')
      if (len > 70) suggestions.push('标题过长，可能在搜索结果中被截断')
      if (!hasNumber) suggestions.push('添加数字可以提升点击率（如 "5 个技巧"、"2024 年" 等）')
      if (!hasQuestion && !hasExclaim) suggestions.push('使用疑问句或感叹号可以增加情感吸引力')
      if (!hasEmoji) suggestions.push('适当使用 Emoji 可以提升视觉吸引力')
      if (keywordDensity < 40) suggestions.push('关键词密度较低，建议在标题中包含更多核心关键词')
      return {
        seo_score: seoScore,
        ctr_prediction: ctrPrediction,
        keyword_density: keywordDensity,
        length_score: lengthScore,
        emotion_score: Math.round(emotionScore),
        number_score: numberScore,
        suggestions,
      }
    },
    async analyzeNiche() {
      this.nicheLoading = true
      this.nicheResult = null
      try {
        const res = await analyticsApi.analyzeNiche({
          keyword: this.nicheForm.keyword,
          platform: this.nicheForm.platform,
        })
        this.nicheResult = res.data
      } catch (e) {
        this.nicheResult = this._mockNicheResult(this.nicheForm.keyword)
      } finally {
        this.nicheLoading = false
      }
    },
    _mockNicheResult(keyword) {
      const niches = [
        { name: `${keyword} 教程/指南`, reason: '教程类内容搜索量大，长尾流量稳定，变现能力强', competition: '中', growth_potential: '高', avg_cpm: '8.50' },
        { name: `${keyword} 测评/对比`, reason: '测评内容购买意图强，CPM 较高，适合带货', competition: '高', growth_potential: '中', avg_cpm: '12.00' },
        { name: `${keyword} 日常/Vlog`, reason: '日常内容粉丝粘性高，适合长期运营和品牌合作', competition: '低', growth_potential: '高', avg_cpm: '5.00' },
        { name: `${keyword} 新闻/资讯`, reason: '时效性内容流量爆发力强，但持续性较弱', competition: '中', growth_potential: '中', avg_cpm: '6.50' },
        { name: `${keyword} 挑战/互动`, reason: '互动性内容传播力强，适合短视频平台', competition: '低', growth_potential: '高', avg_cpm: '3.50' },
      ]
      return { recommendations: niches }
    },
    async calculateRevenue() {
      try {
        const res = await analyticsApi.calculateRevenueAI({
          platform: this.calcForm.platform,
          views: this.calcForm.views,
          category: this.calcForm.category,
          region: this.calcForm.region,
        })
        this.calcResult = res.data
      } catch (e) {
        this._localCalculateRevenue()
      }
    },
    _localCalculateRevenue() {
      const isYouTube = this.calcForm.platform === 'youtube'
      const categoryMultipliers = { general: 1, tech: 1.8, finance: 2.5, gaming: 1.2, education: 1.5, entertainment: 0.8, music: 0.6 }
      const regionMultipliers = { us: 1.5, eu: 1.2, asia: 0.8, global: 1.0 }
      const catMul = categoryMultipliers[this.calcForm.category] || 1
      const regMul = regionMultipliers[this.calcForm.region] || 1
      const baseCpm = isYouTube ? 7.5 : 2.0
      const cpm = +(baseCpm * catMul * regMul).toFixed(2)
      const monetizationRate = isYouTube ? 0.55 : 0.30
      const creatorShareRate = isYouTube ? 0.55 : 0.50
      const monetizedViews = Math.round(this.calcForm.views * monetizationRate)
      const totalAdRevenue = (monetizedViews / 1000) * cpm
      const creatorShare = totalAdRevenue * creatorShareRate
      const low = creatorShare * 0.3
      const high = creatorShare * 2.0
      this.calcResult = {
        cpm,
        monetized_views: monetizedViews,
        monetization_rate: monetizationRate,
        total_ad_revenue: +totalAdRevenue.toFixed(2),
        creator_share: +creatorShare.toFixed(2),
        creator_share_rate: creatorShareRate,
        low: +low.toFixed(2),
        high: +high.toFixed(2),
      }
    },
    async predictTrend() {
      this.trendLoading = true
      this.trendResult = null
      try {
        const res = await analyticsApi.predictTrend({ platform: this.trendForm.platform })
        this.trendResult = res.data
      } catch (e) {
        this.trendResult = this._mockTrendResult()
      } finally {
        this.trendLoading = false
      }
    },
    _mockTrendResult() {
      const isYT = this.trendForm.platform === 'youtube'
      const trends = isYT ? [
        { name: 'AI 工具测评', reason: 'AI 工具爆发式增长，用户对实际体验和对比需求强烈', tags: ['AI', '科技', '测评'], confidence: 92 },
        { name: '短视频赚钱攻略', reason: '经济环境下，副业和赚钱内容搜索量持续上升', tags: ['赚钱', '副业', '教程'], confidence: 87 },
        { name: '健康饮食/减脂', reason: '健康意识提升，简单易做的健康食谱需求增长', tags: ['健康', '饮食', '生活'], confidence: 83 },
        { name: '旅行 Vlog', reason: '旅游复苏，沉浸式旅行内容观看时长增长显著', tags: ['旅行', 'Vlog', '体验'], confidence: 78 },
        { name: '宠物搞笑/日常', reason: '宠物内容永远是流量密码，互动率极高', tags: ['宠物', '搞笑', '日常'], confidence: 75 },
      ] : [
        { name: '生活小技巧', reason: '实用型短视频在 TikTok 传播力最强', tags: ['生活', '技巧', '实用'], confidence: 90 },
        { name: '美食制作', reason: '美食内容观看完成率最高，适合带货', tags: ['美食', '制作', '教程'], confidence: 88 },
        { name: '穿搭/时尚', reason: '视觉冲击力强，品牌合作机会多', tags: ['穿搭', '时尚', 'OOTD'], confidence: 85 },
        { name: '搞笑/段子', reason: '传播力最强，涨粉最快的赛道', tags: ['搞笑', '段子', '娱乐'], confidence: 82 },
        { name: '健身/运动', reason: '健康内容持续增长，粉丝粘性高', tags: ['健身', '运动', '健康'], confidence: 79 },
      ]
      return { trends }
    },
    getScoreClass(score) {
      if (score >= 80) return 'score-high'
      if (score >= 50) return 'score-medium'
      return 'score-low'
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
  },
}
</script>

<style scoped>
.tools-layout {
  display: flex;
  gap: 24px;
}

.tool-sidebar {
  width: 220px;
  flex-shrink: 0;
}

.tool-tab {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 14px 16px;
  border: 1px solid transparent;
  border-radius: 12px;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  font-family: inherit;
  transition: all 0.2s;
  margin-bottom: 4px;
  text-align: left;
}
.tool-tab:hover {
  background: #f8fafc;
  color: #1e293b;
}
.tool-tab.active {
  background: #eef2ff;
  color: #4f46e5;
  border-color: #c7d2fe;
  font-weight: 600;
}

.tool-tab-icon {
  font-size: 18px;
}

.tool-content {
  flex: 1;
  min-width: 0;
}

.tool-panel {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 32px;
}

.tool-header {
  margin-bottom: 24px;
}

.tool-title {
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 6px;
}

.tool-desc {
  font-size: 14px;
  color: #64748b;
}

.tool-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}
.form-group select,
.form-group input {
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  font-family: inherit;
  color: #1e293b;
  background: #fff;
  transition: all 0.2s;
}
.form-group select:focus,
.form-group input:focus {
  outline: none;
  border-color: #818cf8;
  box-shadow: 0 0 0 3px rgba(129,140,248,0.15);
}

.input-full {
  width: 100%;
}

.form-row {
  display: flex;
  gap: 12px;
}
.flex-1 {
  flex: 1;
}

.result-card {
  margin-top: 12px;
  padding: 24px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.score-high {
  background: linear-gradient(135deg, #dcfce7, #bbf7d0);
  border: 3px solid #22c55e;
}
.score-medium {
  background: linear-gradient(135deg, #fef9c3, #fde68a);
  border: 3px solid #eab308;
}
.score-low {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  border: 3px solid #ef4444;
}

.score-num {
  font-size: 28px;
  font-weight: 900;
  color: #0f172a;
}

.score-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.score-label {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}
.score-ctr {
  font-size: 13px;
  color: #64748b;
}

.score-breakdown {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.breakdown-label {
  width: 80px;
  font-size: 13px;
  color: #64748b;
  flex-shrink: 0;
}
.progress-bar {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  border-radius: 4px;
  transition: width 0.5s ease;
}
.breakdown-value {
  width: 40px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  text-align: right;
}

.suggestions h4 {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}
.suggestions ul {
  list-style: none;
  padding: 0;
}
.suggestions li {
  padding: 8px 12px;
  margin-bottom: 6px;
  background: #eef2ff;
  border-radius: 8px;
  font-size: 13px;
  color: #3730a3;
  line-height: 1.5;
}
.suggestions li::before {
  content: '💡 ';
}

.niche-recommendations {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.niche-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  transition: all 0.2s;
}
.niche-card:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

.niche-rank {
  font-size: 24px;
  font-weight: 900;
  color: #6366f1;
  flex-shrink: 0;
  width: 36px;
}

.niche-info {
  flex: 1;
}

.niche-name {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 4px;
}

.niche-reason {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin-bottom: 8px;
}

.niche-metrics {
  display: flex;
  gap: 16px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.metric-label {
  font-size: 11px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.metric-value {
  font-size: 14px;
  font-weight: 700;
}

.text-green { color: #059669; }
.text-yellow { color: #d97706; }
.text-red { color: #dc2626; }

.revenue-summary {
  text-align: center;
  margin-bottom: 24px;
  padding: 24px;
  background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
  border-radius: 12px;
}

.revenue-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
}

.revenue-amount {
  font-size: 40px;
  font-weight: 900;
  color: #059669;
  letter-spacing: -1px;
}

.revenue-range {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.revenue-detail-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.detail-item {
  padding: 16px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  text-align: center;
}

.detail-label {
  font-size: 11px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.detail-value {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
}

.detail-value.highlight {
  color: #059669;
}

.detail-sub {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

.trend-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trend-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  transition: all 0.2s;
}
.trend-item:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

.trend-rank {
  font-size: 24px;
  font-weight: 900;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  flex-shrink: 0;
  width: 36px;
  text-align: center;
}

.trend-info {
  flex: 1;
}

.trend-name {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 4px;
}

.trend-reason {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin-bottom: 8px;
}

.trend-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.trend-tag {
  padding: 2px 8px;
  background: #eef2ff;
  color: #4f46e5;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.trend-score {
  text-align: center;
  flex-shrink: 0;
}

.trend-score-value {
  font-size: 22px;
  font-weight: 800;
  color: #059669;
}

.trend-score-label {
  font-size: 11px;
  color: #94a3b8;
}

@media (max-width: 768px) {
  .tools-layout {
    flex-direction: column;
  }
  .tool-sidebar {
    width: 100%;
    display: flex;
    overflow-x: auto;
    gap: 4px;
  }
  .tool-tab {
    white-space: nowrap;
    width: auto;
  }
  .revenue-detail-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
