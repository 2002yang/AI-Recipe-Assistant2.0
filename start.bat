@echo off
chcp 65001 >nul
echo ==========================================
echo 美食推荐与食谱智能助手 - 启动脚本
echo ==========================================
echo.

:: 检查 Python
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
echo [✓] Python 已安装

:: 检查 Node.js
echo.
echo [2/4] 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)
echo [✓] Node.js 已安装

:: 启动后端
echo.
echo [3/4] 启动后端服务...
echo 正在安装后端依赖...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -q -r requirements.txt

start "后端服务" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
echo [✓] 后端服务已启动 (http://localhost:8000)

:: 启动前端
echo.
echo [4/4] 启动前端服务...
cd ..\frontend
if not exist node_modules (
    echo 正在安装前端依赖...
    npm install
)

start "前端服务" cmd /k "cd frontend && npm run dev"
echo [✓] 前端服务已启动 (http://localhost:5173)

:: 等待服务启动
echo.
echo 等待服务启动...
timeout /t 5 /nobreak >nul

:: 打开浏览器
echo.
echo ==========================================
echo 启动完成！
echo ==========================================
echo 后端 API: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo 前端应用: http://localhost:5173
echo ==========================================
echo.
echo 正在打开浏览器...
start http://localhost:5173

echo.
echo 提示：
echo - 后端窗口显示 "Application startup complete" 表示启动成功
echo - 前端窗口显示 "Local: http://localhost:5173" 表示启动成功
echo - 按 Ctrl+C 可以停止服务
echo.
pause