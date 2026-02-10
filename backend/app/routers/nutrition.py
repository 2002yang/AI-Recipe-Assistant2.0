from fastapi import APIRouter, HTTPException
from app.services.nutrition_calc import nutrition_calculator
from app.services.recipe_matcher import recipe_service

router = APIRouter()


@router.get("/recipe/{recipe_id}")
async def get_recipe_nutrition(recipe_id: int):
    """
    获取菜谱营养信息
    """
    recipe = recipe_service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    
    analysis = nutrition_calculator.analyze_meal_nutrition(
        recipe.nutrition, 
        recipe.servings
    )
    
    return {
        "recipe_id": recipe_id,
        "recipe_name": recipe.name,
        "nutrition_per_serving": analysis["per_serving"],
        "daily_percentage": analysis["daily_percentage"],
        "health_tips": analysis["health_tips"]
    }


@router.get("/recipe/{recipe_id}/diet/{diet_type}")
async def check_diet_suitability(recipe_id: int, diet_type: str):
    """
    检查菜谱是否适合特定饮食
    """
    recipe = recipe_service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    
    result = nutrition_calculator.is_suitable_for_diet(
        recipe.nutrition,
        diet_type,
        recipe.servings
    )
    
    return {
        "recipe_id": recipe_id,
        "recipe_name": recipe.name,
        "diet_type": diet_type,
        "suitable": result["suitable"],
        "message": result["message"]
    }


@router.get("/daily-needs")
async def get_daily_nutrition_needs(
    weight: float = 60,
    height: float = 170,
    age: int = 30,
    gender: str = "female",
    activity_level: str = "moderate"
):
    """
    计算每日营养需求
    """
    needs = nutrition_calculator.calculate_daily_needs(
        weight=weight,
        height=height,
        age=age,
        gender=gender,
        activity_level=activity_level
    )
    
    return {
        "profile": {
            "weight": weight,
            "height": height,
            "age": age,
            "gender": gender,
            "activity_level": activity_level
        },
        "daily_needs": needs
    }