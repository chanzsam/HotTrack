@echo off
echo ========================================
echo   HotTrack - YouTube & TikTok 热门视频分析
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist .env (
    echo 正在创建 .env 配置文件...
    copy .env.example .env
    echo.
    echo [重要] 请编辑 backend\.env 文件，填入你的 YouTube API Key
    echo.
)

echo 正在安装 Python 依赖...
pip install -r requirements.txt -q

echo.
echo 正在安装前端依赖...
cd /d "%~dp0frontend"
call npm install

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 启动方式：
echo   后端: cd backend ^&^& python -m uvicorn app.main:app --reload
echo   前端: cd frontend ^&^& npm run dev
echo.
echo 访问地址：
echo   前端页面: http://localhost:5173
echo   后端API文档: http://localhost:8000/docs
echo.
pause
