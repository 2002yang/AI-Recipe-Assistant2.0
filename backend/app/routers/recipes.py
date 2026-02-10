from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.recipe import Recipe, RecipeListItem
from app.services.recipe_matcher import recipe_service
from app.services.nlp_service import nlp_service

router = APIRouter()


@router.get("/list", response_model=List[RecipeListItem])
async def get_recipes(
    tag: Optional[str] = None,
    difficulty: Optional[str] = None
):
    """
    获取菜谱列表
    """
    recipes = recipe_service.get_all_recipes()
    
    if tag:
        recipes = [r for r in recipes if tag in r.tags]
    
    if difficulty:
        recipes = [r for r in recipes if r.difficulty == difficulty]
    
    return recipes


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int):
    """
    获取菜谱详情
    """
    recipe = recipe_service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    return recipe


@router.post("/search")
async def search_recipes(
    ingredients: List[str],
    restrictions: Optional[List[str]] = None,
    top_k: int = 5
):
    """
    基于食材搜索菜谱
    """
    matches = recipe_service.search_by_ingredients(
        ingredients=ingredients,
        restrictions=restrictions or [],
        top_k=top_k
    )
    
    return {
        "results": [
            {
                "recipe": {
                    "id": m["recipe"].id,
                    "name": m["recipe"].name,
                    "name_en": m["recipe"].name_en,
                    "category": m["recipe"].category,
                    "difficulty": m["recipe"].difficulty,
                    "time": m["recipe"].time,
                    "servings": m["recipe"].servings,
                    "nutrition": m["recipe"].nutrition.dict(),
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
    }


@router.get("/{recipe_id}/substitutions/{ingredient_name}")
async def get_ingredient_substitutions(recipe_id: int, ingredient_name: str):
    """
    获取食材替代建议
    """
    # 首先检查数据库中的替代方案
    substitutions = recipe_service.get_substitutions(recipe_id, ingredient_name)
    
    # 如果没有，使用AI生成
    if not substitutions:
        recipe = recipe_service.get_recipe_by_id(recipe_id)
        recipe_name = recipe.name if recipe else "这道菜"
        ai_suggestion = await nlp_service.generate_substitution_suggestions(
            ingredient_name, 
            recipe_name
        )
        return {
            "ingredient": ingredient_name,
            "database_substitutions": [],
            "ai_suggestion": ai_suggestion
        }
    
    return {
        "ingredient": ingredient_name,
        "database_substitutions": substitutions,
        "ai_suggestion": None
    }


@router.get("/tags/{tag}")
async def get_recipes_by_tag(tag: str):
    """
    根据标签获取菜谱
    """
    recipes = recipe_service.get_recipes_by_tag(tag)
    return recipes