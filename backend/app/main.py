from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import chat, recipes, nutrition


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting AI Recipe Assistant...")
    yield
    print("Service shutdown")


app = FastAPI(
    title="美食推荐与食谱智能助手 API",
    description="基于 AI 的智能菜谱推荐和营养咨询服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api/chat", tags=["对话"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["菜谱"])
app.include_router(nutrition.router, prefix="/api/nutrition", tags=["营养"])


@app.get("/")
async def root():
    return {
        "message": "美食推荐与食谱智能助手 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}