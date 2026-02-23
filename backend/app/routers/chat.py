from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.chat import ChatRequest, ChatResponse, ChatMessage
from app.services.langchain_nlp import langchain_nlp_service
from app.services.recipe_matcher import recipe_service
from app.services.enhanced_conversation import enhanced_conversation_manager
from app.services.vector_store import vector_store

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    处理用户对话消息 - LangChain + RAG 版本
    """
    try:
        # 获取或创建对话ID
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = enhanced_conversation_manager.create_conversation()
        
        # 获取对话上下文和 Memory
        context = enhanced_conversation_manager.get_recent_context(conversation_id)
        user_context = enhanced_conversation_manager.get_user_context_for_prompt(conversation_id)
        
        # 使用 LangChain 解析用户意图
        parsed_intent = await langchain_nlp_service.parse_user_intent(request.message)
        
        # 提取信息
        ingredients = parsed_intent.get("ingredients", [])
        restrictions = parsed_intent.get("restrictions", [])
        target_dish = parsed_intent.get("target_dish")
        intent = parsed_intent.get("intent", "other")
        
        print(f"Intent: {intent}, Ingredients: {ingredients}, Restrictions: {restrictions}")
        
        # 更新对话上下文
        enhanced_conversation_manager.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
            ingredients=ingredients,
            restrictions=restrictions
        )
        
        # 根据意图处理
        suggested_recipes = []
        nutrition_info = None
        
        if intent == "recommend_by_ingredients":
            # 使用 RAG 向量搜索 + 传统匹配
            if ingredients:
                # 方法1: RAG 语义搜索
                rag_results = await langchain_nlp_service.search_recipes_with_rag(
                    query=request.message,
                    ingredients=ingredients,
                    restrictions=restrictions,
                    top_k=5
                )
                
                # 转换为前端需要的格式
                suggested_recipes = [
                    {
                        "recipe": {
                            "id": r["recipe"].id,
                            "name": r["recipe"].name,
                            "name_en": r["recipe"].name_en,
                            "category": r["recipe"].category,
                            "difficulty": r["recipe"].difficulty,
                            "time": r["recipe"].time,
                            "servings": r["recipe"].servings,
                            "nutrition": {
                                "calories": r["recipe"].nutrition.calories,
                                "protein": r["recipe"].nutrition.protein,
                                "fat": r["recipe"].nutrition.fat,
                                "carbs": r["recipe"].nutrition.carbs,
                                "fiber": r["recipe"].nutrition.fiber
                            },
                            "tags": r["recipe"].tags,
                            "steps": r["recipe"].steps,
                            "tips": r["recipe"].tips
                        },
                        "match_score": r["match_score"],
                        "matched_ingredients": r["matched_ingredients"],
                        "missing_ingredients": r["missing_ingredients"]
                    }
                    for r in rag_results
                ]
            else:
                # 如果没有提取到食材，使用向量搜索
                vector_results = vector_store.search(request.message, n_results=3)
                for vr in vector_results:
                    full_recipe = recipe_service.get_recipe_by_id(vr['id'])
                    if full_recipe:
                        suggested_recipes.append({
                            "recipe": {
                                "id": full_recipe.id,
                                "name": full_recipe.name,
                                "name_en": full_recipe.name_en,
                                "category": full_recipe.category,
                                "difficulty": full_recipe.difficulty,
                                "time": full_recipe.time,
                                "servings": full_recipe.servings,
                                "nutrition": {
                                    "calories": full_recipe.nutrition.calories,
                                    "protein": full_recipe.nutrition.protein,
                                    "fat": full_recipe.nutrition.fat,
                                    "carbs": full_recipe.nutrition.carbs,
                                    "fiber": full_recipe.nutrition.fiber
                                },
                                "tags": full_recipe.tags,
                                "steps": full_recipe.steps,
                                "tips": full_recipe.tips
                            },
                            "match_score": vr['similarity'],
                            "matched_ingredients": [],
                            "missing_ingredients": []
                        })
        
        elif intent == "nutrition_query" and target_dish:
            # 查询营养信息
            recipe = None
            for r in recipe_service.recipes:
                if target_dish in r.name or r.name in target_dish:
                    recipe = r
                    break
            
            if recipe:
                from app.services.nutrition_calc import nutrition_calculator
                nutrition_info = nutrition_calculator.analyze_meal_nutrition(
                    recipe.nutrition, 
                    recipe.servings
                )
        
        # 使用 LangChain 生成 AI 回复
        ai_response = await langchain_nlp_service.generate_response(
            user_message=request.message,
            history=context,
            recipes=suggested_recipes
        )
        
        # 记录助手回复到 Memory
        enhanced_conversation_manager.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response
        )
        
        return ChatResponse(
            message=ai_response,
            conversation_id=conversation_id,
            suggested_recipes=suggested_recipes,
            detected_ingredients=ingredients,
            detected_restrictions=restrictions,
            nutrition_info=nutrition_info
        )
        
    except Exception as e:
        print(f"Error in chat: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/new")
async def new_conversation():
    """
    创建新对话
    """
    conversation_id = enhanced_conversation_manager.create_conversation()
    return {
        "conversation_id": conversation_id,
        "message": "新对话已创建，请告诉我你想吃什么？"
    }


@router.get("/history/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    获取对话历史
    """
    conversation = enhanced_conversation_manager.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in conversation.messages
        ],
        "detected_ingredients": conversation.detected_ingredients,
        "detected_restrictions": conversation.detected_restrictions,
        "summary": enhanced_conversation_manager.get_conversation_summary(conversation_id)
    }


@router.post("/search")
async def semantic_search(query: str, top_k: int = 5):
    """
    语义搜索菜谱（RAG 演示）
    """
    try:
        results = vector_store.search(query, n_results=top_k)
        return {
            "query": query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))