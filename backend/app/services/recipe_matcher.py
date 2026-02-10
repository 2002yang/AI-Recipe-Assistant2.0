import json
import os
from typing import List, Dict, Any
from app.models.recipe import Recipe, RecipeListItem


class RecipeService:
    def __init__(self):
        self.recipes = self._load_recipes()
        self.ingredient_index = self._build_ingredient_index()
    
    def _load_recipes(self) -> List[Recipe]:
        """加载菜谱数据"""
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'recipes.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Recipe(**recipe) for recipe in data['recipes']]
    
    def _build_ingredient_index(self) -> Dict[str, List[int]]:
        """构建食材索引"""
        index = {}
        for recipe in self.recipes:
            for ingredient in recipe.ingredients:
                ingredient_name = ingredient.name
                if ingredient_name not in index:
                    index[ingredient_name] = []
                if recipe.id not in index[ingredient_name]:
                    index[ingredient_name].append(recipe.id)
        return index
    
    def get_all_recipes(self) -> List[RecipeListItem]:
        """获取所有菜谱列表"""
        return [
            RecipeListItem(
                id=r.id,
                name=r.name,
                difficulty=r.difficulty,
                time=r.time,
                tags=r.tags
            )
            for r in self.recipes
        ]
    
    def get_recipe_by_id(self, recipe_id: int) -> Recipe:
        """根据ID获取菜谱详情"""
        for recipe in self.recipes:
            if recipe.id == recipe_id:
                return recipe
        return None
    
    def search_by_ingredients(
        self, 
        ingredients: List[str], 
        restrictions: List[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        基于食材匹配菜谱
        使用简单的交集算法计算匹配分数
        """
        if restrictions is None:
            restrictions = []
        
        results = []
        
        for recipe in self.recipes:
            # 检查饮食限制
            if self._check_restrictions(recipe, restrictions):
                continue
            
            # 计算匹配分数
            recipe_ingredients = [i.name for i in recipe.ingredients]
            matched = set(ingredients) & set(recipe_ingredients)
            
            if len(matched) > 0:
                # 匹配分数 = 匹配食材数 / 所需食材总数
                score = len(matched) / len(recipe_ingredients)
                
                results.append({
                    "recipe": recipe,
                    "match_score": score,
                    "matched_ingredients": list(matched),
                    "missing_ingredients": list(set(recipe_ingredients) - matched)
                })
        
        # 按匹配分数排序
        results.sort(key=lambda x: x["match_score"], reverse=True)
        
        return results[:top_k]
    
    def _check_restrictions(self, recipe: Recipe, restrictions: List[str]) -> bool:
        """检查菜谱是否违反饮食限制"""
        restriction_keywords = {
            "素食": ["肉类", "水产"],
            "纯素": ["肉类", "水产", "蛋奶"],
            "无海鲜": ["水产"],
            "无辣": ["辣"],
            "低碳水": ["主食"],
            "减肥": ["高热量"]
        }
        
        for restriction in restrictions:
            if restriction in restriction_keywords:
                categories = restriction_keywords[restriction]
                # 检查食材分类
                for ingredient in recipe.ingredients:
                    if ingredient.category in categories:
                        return True
                # 检查标签
                for category in categories:
                    if category in recipe.tags:
                        return True
                        
        return False
    
    def get_substitutions(self, recipe_id: int, ingredient_name: str) -> List[str]:
        """获取食材替代建议"""
        recipe = self.get_recipe_by_id(recipe_id)
        if recipe and ingredient_name in recipe.substitutions:
            return recipe.substitutions[ingredient_name]
        return []
    
    def get_recipes_by_tag(self, tag: str) -> List[RecipeListItem]:
        """根据标签筛选菜谱"""
        filtered = [r for r in self.recipes if tag in r.tags]
        return [
            RecipeListItem(
                id=r.id,
                name=r.name,
                difficulty=r.difficulty,
                time=r.time,
                tags=r.tags
            )
            for r in filtered
        ]


# 单例模式
recipe_service = RecipeService()