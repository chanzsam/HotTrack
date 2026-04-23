@echo off
echo ========================================
echo   Hugging Face Spaces 部署脚本
echo ========================================
echo.

set /p HF_USERNAME="请输入你的 Hugging Face 用户名: "
set SPACE_NAME=youtube-tiktok-analyzer

echo.
echo 正在准备部署文件...

if exist "hf-deploy" rmdir /s /q "hf-deploy"
mkdir "hf-deploy"

echo 复制文件...
xcopy /E /I /Q "backend" "hf-deploy\backend"
xcopy /E /I /Q "frontend" "hf-deploy\frontend"
copy "Dockerfile" "hf-deploy\"
copy "README.md" "hf-deploy\"
copy ".dockerignore" "hf-deploy\"
copy ".gitignore" "hf-deploy\"

echo.
echo ========================================
echo   文件准备完成！
echo ========================================
echo.
echo 接下来请执行以下命令：
echo.
echo   cd hf-deploy
echo   git init
echo   git lfs install
echo   git add .
echo   git commit -m "Initial deployment"
echo   git remote add origin https://huggingface.co/spaces/%HF_USERNAME%/%SPACE_NAME%
echo   git push -u origin main
echo.
echo 或者，你也可以：
echo 1. 在 Hugging Face 创建一个新的 Docker Space
echo 2. 手动上传 hf-deploy 文件夹中的所有文件
echo.
pause
