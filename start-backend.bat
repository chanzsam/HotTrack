@echo off
echo 正在启动 HotTrack 后端服务...
cd /d "%~dp0backend"
"C:\Program Files\Python311\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
