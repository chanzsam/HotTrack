import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
})

export const videosApi = {
  getTopViewed: (params) => api.get('/videos/top-viewed', { params }),
  getTopLiked: (params) => api.get('/videos/top-liked', { params }),
  getTrending: (params) => api.get('/videos/trending', { params }),
  getStats: () => api.get('/videos/stats'),
}

export const analyticsApi = {
  getViral: (params) => api.get('/analytics/viral', { params }),
  calculateViral: (params) => api.post('/analytics/viral/calculate', null, { params }),
  getRevenue: (params) => api.get('/analytics/revenue', { params }),
  getRevenueRanking: (params) => api.get('/analytics/revenue/ranking', { params }),
  calculateRevenue: (params) => api.post('/analytics/revenue/calculate', null, { params }),
  analyzeTitle: (data) => api.post('/ai/analyze-title', data),
  analyzeNiche: (data) => api.post('/ai/analyze-niche', data),
  predictTrend: (data) => api.post('/ai/predict-trend', data),
  calculateRevenueAI: (data) => api.post('/ai/calculate-revenue', data),
}

export const tasksApi = {
  getConfigStatus: () => api.get('/crawl/config-status'),
  testYoutubeApi: () => api.get('/crawl/test-youtube-api'),
  startCrawl: (platform, params) => api.post(`/crawl/${platform}`, null, { params }),
  seedDemo: () => api.post('/crawl/seed-demo'),
  resetAndCrawl: () => api.post('/crawl/reset-and-crawl'),
}

export const crawlApi = {
  crawlYoutubeTrending: (params) => api.post('/crawl/youtube/trending', null, { params }),
  crawlYoutubeMostViewed: (params) => api.post('/crawl/youtube/most-viewed', null, { params }),
  crawlYoutubeViral: (params) => api.post('/crawl/youtube/viral-candidates', null, { params }),
  crawlTiktokTrending: (params) => api.post('/crawl/tiktok/trending', null, { params }),
  crawlTiktokMostViewed: (params) => api.post('/crawl/tiktok/most-viewed', null, { params }),
  crawlTiktokViral: (params) => api.post('/crawl/tiktok/viral-candidates', null, { params }),
  crawlAll: (params) => api.post('/crawl/all', null, { params }),
}

export default api
