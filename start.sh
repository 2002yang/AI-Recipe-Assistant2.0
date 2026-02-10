#!/bin/bash

echo "=========================================="
echo "美食推荐与食谱智能助手 - 启动脚本"
echo "=========================================="
echo ""

# 检查 Python
echo "[1/4] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi
echo "[✓] Python 已安装"

# 检查 Node.js
echo ""
echo "[2/4] 检查 Node.js 环境..."
if ! command -v node &> /dev/null; then
    echo "[错误] 未找到 Node.js，请先安装 Node.js 16+"
    exit 1
fi
echo "[✓] Node.js 已安装"

# 启动后端
echo ""
echo "[3/4] 启动后端服务..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo "启动后端服务..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "[✓] 后端服务已启动 (PID: $BACKEND_PID, http://localhost:8000)"

# 启动前端
echo ""
echo "[4/4] 启动前端服务..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "正在安装前端依赖..."
    npm install
fi

echo "启动前端服务..."
npm run dev &
FRONTEND_PID=$!
echo "[✓] 前端服务已启动 (PID: $FRONTEND_PID, http://localhost:5173)"

# 等待服务启动
echo ""
echo "等待服务启动..."
sleep 5

echo ""
echo "=========================================="
echo "启动完成！"
echo "=========================================="
echo "后端 API: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo "前端应用: http://localhost:5173"
echo "=========================================="
echo ""
echo "提示："
echo "- 后端 PID: $BACKEND_PID"
echo "- 前端 PID: $FRONTEND_PID"
echo "- 运行 'kill $BACKEND_PID $FRONTEND_PID' 停止服务"
echo ""

# 打开浏览器（仅 macOS）
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:5173
fi

wait