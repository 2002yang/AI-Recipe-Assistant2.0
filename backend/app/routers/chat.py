from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.chat import ChatRequest, ChatResponse, ChatMessage
from app.services.nlp_service import nlp_service
from app.services.recipe_matcher import recipe_service
from app.services.conversation import conversation_manager
import uuid

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    处理用户对话消息
    """
    try:
        # 获取或创建对话ID
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = conversation_manager.create_conversation()
        
        # 获取对话上下文
        context = conversation_manager.get_recent_context(conversation_id)
        
        # 解析用户意图
        parsed_intent = await nlp_service.parse_user_intent(request.message)
        
        # 提取信息
        ingredients = parsed_intent.get("ingredients", [])
        restrictions = parsed_intent.get("restrictions", [])
        target_dish = parsed_intent.get("target_dish")
        intent = parsed_intent.get("intent", "other")
        
        # 更新对话上下文
        conversation_manager.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
            ingredients=ingredients,
            restrictions=restrictions
        )
        
        # 根据意图处理
        suggested_recipes = []
        nutrition_info = None
        
        if intent == "recommend_by_ingredients" and ingredients:
            # 基于食材推荐
            matches = recipe_service.search_by_ingredients(
                ingredients=ingredients,
                restrictions=restrictions,
                top_k=3
            )
            suggested_recipes = [
                {
                    "recipe": {
                        "id": m["recipe"].id,
                        "name": m["recipe"].name,
                        "name_en": m["recipe"].name_en,
                        "category": m["recipe"].category,
                        "difficulty": m["recipe"].difficulty,
                        "time": m["recipe"].time,
                        "servings": m["recipe"].servings,
                        "nutrition": {
                            "calories": m["recipe"].nutrition.calories,
                            "protein": m["recipe"].nutrition.protein,
                            "fat": m["recipe"].nutrition.fat,
                            "carbs": m["recipe"].nutrition.carbs,
                            "fiber": m["recipe"].nutrition.fiber
                        },
                        "tags": m["recipe"].tags,
                        "steps": m["recipe"].steps,
                        "tips": m["recipe"].tips
                    },
                    "match_score": m["match_score"],
                    "matched_ingredients": m["matched_ingredients"],
                    "missing_ingredients": m["missing_ingredients"]
                }
                for m in matches
            ]
        
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
        
        # 生成AI回复
        ai_response = await nlp_service.generate_response(
            user_message=request.message,
            context=context,
            recipes=suggested_recipes
        )
        
        # 记录助手回复
        conversation_manager.add_message(
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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/new")
async def new_conversation():
    """
    创建新对话
    """
    conversation_id = conversation_manager.create_conversation()
    return {
        "conversation_id": conversation_id,
        "message": "新对话已创建，请告诉我你想吃什么？"
    }


@router.get("/history/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    获取对话历史
    """
    conversation = conversation_manager.get_conversation(conversation_id)
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
        "detected_restrictions": conversation.detected_restrictions
    }