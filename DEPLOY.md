# Hugging Face Spaces 部署指南

## 前置准备

1. 注册 [Hugging Face](https://huggingface.co/) 账号
2. 获取 YouTube API Key（可选，用于真实数据）
3. 获取 TikHub API Key（可选，用于 TikTok 数据）

## 部署步骤

### 1. 创建 Hugging Face Space

1. 登录 Hugging Face
2. 点击右上角头像 → "New Space"
3. 填写信息：
   - **Space name**: `youtube-tiktok-analyzer`（或你喜欢的名字）
   - **License**: MIT
   - **SDK**: 选择 **Docker**
   - **Hardware**: CPU basic (免费) 或 CPU upgrade
4. 点击 "Create Space"

### 2. 上传代码

#### 方法 A: 使用 Git（推荐）

```bash
# 克隆你的 Space
git clone https://huggingface.co/spaces/<你的用户名>/youtube-tiktok-analyzer

# 进入目录
cd youtube-tiktok-analyzer

# 复制项目文件（排除不需要的文件）
# 将项目中的以下文件/文件夹复制到此目录：
# - backend/
# - frontend/
# - Dockerfile
# - README.md
# - .dockerignore

# 添加所有文件
git add .

# 提交
git commit -m "Initial deployment"

# 推送到 Hugging Face
git push
```

#### 方法 B: 使用网页上传

1. 进入你的 Space 页面
2. 点击 "Files" 标签
3. 点击 "Add file" → "Upload files"
4. 上传以下文件/文件夹：
   - `backend/` 文件夹
   - `frontend/` 文件夹
   - `Dockerfile`
   - `README.md`
   - `.dockerignore`

### 3. 配置 Secrets（环境变量）

1. 进入你的 Space 页面
2. 点击 "Settings" 标签
3. 滚动到 "Repository secrets" 部分
4. 添加以下 secrets：

| Name | Value | 说明 |
|------|-------|------|
| `YOUTUBE_API_KEY` | `AIzaSy...` | YouTube Data API Key |
| `TIKHUB_API_KEY` | `orBSPO...` | TikHub API Key |

> 注意：即使不添加 API Key，应用也会使用演示数据运行。

### 4. 等待构建完成

- 上传代码后，Hugging Face 会自动开始构建 Docker 镜像
- 构建过程大约需要 5-10 分钟
- 可以在 "Logs" 标签查看构建进度

### 5. 访问应用

构建完成后，访问：
```
https://huggingface.co/spaces/<你的用户名>/youtube-tiktok-analyzer
```

## 常见问题

### Q: 构建失败怎么办？

1. 查看 "Logs" 标签中的错误信息
2. 常见原因：
   - `requirements.txt` 中缺少依赖
   - `package.json` 中缺少依赖
   - Dockerfile 语法错误

### Q: 应用启动后没有数据？

1. 检查是否配置了 API Keys
2. 如果没有配置，应用会自动生成演示数据
3. 点击 "数据采集" 页面手动触发数据更新

### Q: 如何更新代码？

```bash
# 修改代码后
git add .
git commit -m "Update code"
git push
```

Hugging Face 会自动重新构建和部署。

### Q: 如何查看日志？

1. 进入 Space 页面
2. 点击 "Logs" 标签
3. 可以看到实时日志输出

## 资源限制

Hugging Face Spaces 免费版限制：

| 资源 | 限制 |
|------|------|
| CPU | 2 vCPU |
| 内存 | 16 GB |
| 存储 | 临时存储（重启后清空） |
| 带宽 | 有限制 |

> 注意：由于使用临时存储，数据库会在重启后清空。如需持久化数据，考虑使用外部数据库服务。

## 升级到付费版

如果需要更好的性能和持久化存储，可以升级到：

- **CPU Upgrade**: $0.60/小时
- **GPU**: $0.60-$2.50/小时
- **Persistent Storage**: 额外费用

## 项目结构

```
youtube-tiktok-analyzer/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── crawlers/     # 爬虫模块
│   │   ├── analyzers/    # 分析模块
│   │   ├── demo/         # 演示数据
│   │   ├── models/       # 数据模型
│   │   ├── scheduler/    # 定时任务
│   │   └── main.py       # 入口文件
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── api/          # API 客户端
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
├── Dockerfile
├── README.md
└── .dockerignore
```

## 技术支持

如有问题，请访问：
- [Hugging Face 文档](https://huggingface.co/docs/hub/spaces)
- [项目 GitHub Issues](如有)
