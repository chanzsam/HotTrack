<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand" @click="$router.push('/')">
        <div class="brand-icon">🔥</div>
        <span class="brand-text">HotTrack</span>
        <span class="brand-tag">AI</span>
      </div>
      <div class="nav-links">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/top-viewed" class="nav-link">播放排行</router-link>
        <router-link to="/trending" class="nav-link">热门趋势</router-link>
        <router-link to="/viral" class="nav-link">爆红追踪</router-link>
        <router-link to="/revenue" class="nav-link">收入估算</router-link>
        <router-link to="/ai-tools" class="nav-link nav-link-ai">✨ AI 工具</router-link>
        <router-link to="/crawl" class="nav-link">数据采集</router-link>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
    <footer class="footer">
      <p>HotTrack AI — YouTube & TikTok 热门视频智能分析平台 · 数据仅供参考</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: #f1f5f9;
}
::-webkit-scrollbar-thumb {
  background: #c7d2fe;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #818cf8;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f8fafc;
  color: #1e293b;
  min-height: 100vh;
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 64px;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(226,232,240,0.6);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}
.nav-brand:hover {
  transform: scale(1.02);
}

.brand-icon {
  font-size: 24px;
}

.brand-text {
  font-size: 22px;
  font-weight: 900;
  background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}

.brand-tag {
  font-size: 10px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: #fff;
  letter-spacing: 0.5px;
}

.nav-links {
  display: flex;
  gap: 2px;
}

.nav-link {
  padding: 8px 16px;
  border-radius: 8px;
  text-decoration: none;
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: #1e293b;
  background: #f1f5f9;
}

.nav-link.router-link-active {
  color: #6366f1;
  background: #eef2ff;
  font-weight: 600;
}

.nav-link-ai {
  background: linear-gradient(135deg, #eef2ff, #faf5ff);
  color: #7c3aed;
  border: 1px solid #e9d5ff;
}
.nav-link-ai:hover {
  background: linear-gradient(135deg, #e0e7ff, #f3e8ff);
  color: #6d28d9;
}
.nav-link-ai.router-link-active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border-color: transparent;
}

.main-content {
  flex: 1;
  width: 100%;
}

.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 40px;
  min-height: calc(100vh - 64px - 72px);
}

.page-fullwidth {
  width: 100%;
}

.section-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border-radius: 8px;
}

.table-wrapper::-webkit-scrollbar {
  height: 4px;
}
.table-wrapper::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.footer {
  text-align: center;
  padding: 24px;
  color: #94a3b8;
  font-size: 13px;
  border-top: 1px solid rgba(226,232,240,0.6);
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.page-header {
  margin-bottom: 28px;
}

.page-title {
  font-size: 32px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.5px;
  margin-bottom: 6px;
}

.page-subtitle {
  font-size: 15px;
  color: #64748b;
  font-weight: 400;
}

.card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  transition: all 0.2s ease;
  overflow: hidden;
}
.card:hover {
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}

.stat-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  position: relative;
  overflow: hidden;
  transition: all 0.2s ease;
}
.stat-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  transform: translateY(-2px);
}

.stat-card .stat-value {
  font-size: 32px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -1px;
  line-height: 1.1;
}

.stat-card .stat-label {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  font-weight: 600;
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-bar select,
.filter-bar input {
  padding: 10px 16px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #1e293b;
  font-size: 14px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}
.filter-bar select:hover,
.filter-bar input:hover {
  border-color: #c7d2fe;
}
.filter-bar select:focus,
.filter-bar input:focus {
  outline: none;
  border-color: #818cf8;
  box-shadow: 0 0 0 3px rgba(129,140,248,0.15);
}
.filter-bar input::placeholder {
  color: #94a3b8;
}

.btn {
  padding: 10px 22px;
  border-radius: 10px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  box-shadow: 0 2px 8px rgba(99,102,241,0.3);
}
.btn-primary:hover {
  box-shadow: 0 4px 16px rgba(99,102,241,0.4);
  transform: translateY(-1px);
}
.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}
.btn-secondary:hover {
  background: #e2e8f0;
}
.btn-secondary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-danger {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
}
.btn-danger:hover {
  background: #fecaca;
}
.btn-danger:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-success {
  background: linear-gradient(135deg, #059669, #10b981);
  color: #fff;
  box-shadow: 0 2px 8px rgba(5,150,105,0.3);
}
.btn-success:hover {
  box-shadow: 0 4px 16px rgba(5,150,105,0.4);
  transform: translateY(-1px);
}
.btn-success:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-accent {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: #fff;
  box-shadow: 0 2px 12px rgba(99,102,241,0.3);
}
.btn-accent:hover {
  box-shadow: 0 4px 20px rgba(99,102,241,0.45);
  transform: translateY(-1px);
}
.btn-accent:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.video-table {
  width: 100%;
  border-collapse: collapse;
}

.video-table th {
  text-align: center;
  padding: 12px 6px;
  border-bottom: 2px solid #e2e8f0;
  color: #64748b;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  white-space: nowrap;
  background: #fafbfc;
}

.video-table th:nth-child(1) { width: 50px; }
.video-table th:nth-child(2) { width: 55px; }
.video-table th:nth-child(4) { width: 85px; }
.video-table th:nth-child(5) { width: 70px; }
.video-table th:nth-child(6) { width: 75px; }
.video-table th:nth-child(7) { width: 80px; }

.video-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 13px;
  color: #334155;
  vertical-align: middle;
  text-align: center;
}

.video-table tbody tr {
  transition: all 0.15s ease;
}
.video-table tbody tr:hover {
  background: #f8fafc;
}

.video-info {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.video-thumb {
  width: 72px;
  height: 42px;
  border-radius: 6px;
  object-fit: cover;
  background: #f1f5f9;
  flex-shrink: 0;
  border: 1px solid #e2e8f0;
}

.video-title {
  font-weight: 600;
  color: #1e293b;
  max-width: 280px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  font-size: 13px;
  line-height: 1.4;
  word-break: break-word;
}
a.video-title {
  text-decoration: none;
  transition: color 0.2s;
}
a.video-title:hover {
  color: #6366f1;
}

.video-channel {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 3px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 280px;
}

.platform-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.platform-badge.youtube {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.platform-badge.tiktok {
  background: #f0fdfa;
  color: #0d9488;
  border: 1px solid #99f6e4;
}

.rank-number {
  font-weight: 800;
  font-size: 16px;
  color: #f59e0b;
}

.growth-positive {
  color: #059669;
  font-weight: 600;
}

.growth-negative {
  color: #dc2626;
  font-weight: 600;
}

.data-value {
  font-weight: 600;
  color: #1e293b;
  font-size: 13px;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
  font-size: 13px;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #94a3b8;
}
.empty-state .empty-icon {
  font-size: 52px;
  margin-bottom: 16px;
  opacity: 0.6;
}
.empty-state p {
  font-size: 14px;
  color: #94a3b8;
}

.viral-score {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  font-variant-numeric: tabular-nums;
}

.viral-score.high {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.viral-score.medium {
  background: #fffbeb;
  color: #d97706;
  border: 1px solid #fde68a;
}

.viral-score.low {
  background: #f0fdf4;
  color: #059669;
  border: 1px solid #bbf7d0;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 16px;
  letter-spacing: -0.2px;
}

.data-value {
  font-variant-numeric: tabular-nums;
}

.revenue-cell {
  white-space: nowrap;
}

.revenue-main {
  color: #059669;
  font-weight: 700;
  font-size: 13px;
}

.revenue-range {
  display: block;
  font-size: 10px;
  color: #94a3b8;
  margin-top: 2px;
}

.revenue-detail {
  display: block;
  font-size: 10px;
  color: #94a3b8;
  margin-top: 1px;
}

.result-box {
  margin-top: 12px;
  padding: 16px 20px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 12px;
}

.warn-box {
  margin-top: 16px;
  padding: 14px 18px;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 10px;
}
.warn-box p {
  color: #92400e;
  font-size: 12px;
  line-height: 1.6;
}

.info-box {
  margin-bottom: 16px;
  padding: 14px 18px;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  border-radius: 10px;
}
.info-box p {
  color: #3730a3;
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 1024px) {
  .navbar {
    flex-direction: column;
    height: auto;
    padding: 12px 20px;
    gap: 8px;
  }
  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
    gap: 2px;
  }
  .nav-link {
    padding: 6px 10px;
    font-size: 12px;
  }
  .page-container {
    padding: 20px 24px;
  }
  .section-inner {
    padding: 0 24px;
  }
  .video-thumb {
    width: 64px;
    height: 36px;
  }
  .video-title {
    max-width: 180px;
  }
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .page-title {
    font-size: 24px;
  }
}

@media (max-width: 640px) {
  .page-container {
    padding: 16px;
  }
  .section-inner {
    padding: 0 16px;
  }
  .video-table {
    font-size: 12px;
  }
  .video-table th,
  .video-table td {
    padding: 10px 10px;
  }
  .video-thumb {
    width: 56px;
    height: 32px;
  }
  .stat-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
