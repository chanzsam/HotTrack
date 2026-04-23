---
title: HotTrack - YouTube & TikTok Analyzer
emoji: 📹
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
short_description: Real-time analysis of trending videos on YouTube and TikTok
---

# 🎬 HotTrack - YouTube & TikTok 热门视频分析平台

> 实时分析 YouTube 和 TikTok 上最热门、增长最快的视频，包括收入估算

[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Space-blue)](https://huggingface.co/spaces/chanfasf/HotTrack)
[![GitHub](https://img.shields.io/badge/GitHub-chanzsam-black?logo=github)](https://github.com/chanzsam)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 功能特性

| 功能 | 描述 |
|------|------|
| 📊 **热门排行榜** | 查看播放量最高的视频，支持按平台筛选 |
| 🔥 **趋势分析** | 发现正在爆红的视频，追踪增长趋势 |
| ⚡ **爆红速度** | 分析视频增长速度，预测下一个爆款 |
| 💰 **收入估算** | 基于播放量的广告收入预测，包含详细分成 |
| 🎯 **AI 分析** | 标题评分、领域推荐、趋势预测 |

## 🛠️ 技术栈

- **后端**: FastAPI + SQLAlchemy + APScheduler
- **前端**: Vue 3 + Vite + Chart.js
- **数据源**: YouTube Data API v3 + TikHub API
- **部署**: Docker + Hugging Face Spaces

## 📸 截图

<details>
<summary>点击查看界面截图</summary>

- **仪表盘**: 数据概览，实时统计
- **热门排行**: 按播放量、点赞数排序
- **趋势分析**: 时间维度趋势追踪
- **收入估算**: CPM 模型收入计算

</details>

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- YouTube API Key（可选）
- TikHub API Key（可选）

### 本地运行

```bash
# 克隆项目
git clone https://github.com/chanzsam/hottrack.git
cd hottrack

# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端（新终端）
cd frontend
npm install
npm run dev
```

### 环境变量

创建 `backend/.env` 文件：

```env
YOUTUBE_API_KEY=your_youtube_api_key
TIKHUB_API_KEY=your_tikhub_api_key
```

> 💡 即使不配置 API Key，应用也会使用演示数据运行

## 📊 API 文档

启动后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👤 作者

**chanzsam**

- 🐙 GitHub: [https://github.com/chanzsam](https://github.com/chanzsam)
- 🤗 Hugging Face: [https://huggingface.co/chanfasf](https://huggingface.co/chanfasf)

---

⭐ 如果这个项目对你有帮助，请给一个 Star！
