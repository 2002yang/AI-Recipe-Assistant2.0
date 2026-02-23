from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import chat, recipes, nutrition


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 50)
    print("Starting AI Recipe Assistant (LangChain + RAG)...")
    print("=" * 50)
    
    print("\n[1/3] Loading vector database...")
    from app.services.vector_store import vector_store
    recipe_count = vector_store.collection.count()
    print(f"      Loaded {recipe_count} recipes to vector store")
    
    print("\n[2/3] Initializing LangChain NLP service...")
    from app.services.langchain_nlp import langchain_nlp_service
    print("      LangChain NLP service ready")
    
    print("\n[3/3] Initializing conversation manager...")
    from app.services.enhanced_conversation import enhanced_conversation_manager
    print("      Conversation manager ready")
    
    print("\n" + "=" * 50)
    print("All services initialized successfully!")
    print("=" * 50)
    
    yield
    print("\nService shutdown")


app = FastAPI(
    title="美食推荐与食谱智能助手 API",
    description="基于 AI 的智能菜谱推荐和营养咨询服务 (LangChain + RAG)",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["对话"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["菜谱"])
app.include_router(nutrition.router, prefix="/api/nutrition", tags=["营养"])


@app.get("/")
async def root():
    return {
        "message": "美食推荐与食谱智能助手 API",
        "version": "2.0.0 (LangChain + RAG)",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}
