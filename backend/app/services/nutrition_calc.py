from app.models.recipe import Nutrition
from typing import Dict, List


class NutritionCalculator:
    """营养计算器"""
    
    @staticmethod
    def calculate_daily_needs(
        weight: float = 60,
        height: float = 170,
        age: int = 30,
        gender: str = "female",
        activity_level: str = "moderate"
    ) -> Dict:
        """
        计算每日营养需求（Mifflin-St Jeor公式）
        """
        # 基础代谢率 (BMR)
        if gender == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # 活动系数
        activity_multipliers = {
            "sedentary": 1.2,      # 久坐
            "light": 1.375,        # 轻度活动
            "moderate": 1.55,      # 中度活动
            "active": 1.725,       # 重度活动
            "very_active": 1.9     # 极度活动
        }
        
        tdee = bmr * activity_multipliers.get(activity_level, 1.55)
        
        return {
            "calories": round(tdee),
            "protein": round(weight * 1.2, 1),  # 每公斤体重1.2g蛋白质
            "fat": round(tdee * 0.25 / 9, 1),   # 25%热量来自脂肪
            "carbs": round(tdee * 0.5 / 4, 1),  # 50%热量来自碳水
            "fiber": 25  # 每日纤维需求
        }
    
    @staticmethod
    def analyze_meal_nutrition(nutrition: Nutrition, servings: int = 1) -> Dict:
        """
        分析单餐营养
        """
        daily_needs = NutritionCalculator.calculate_daily_needs()
        
        # 按份数计算
        actual_calories = nutrition.calories / servings
        actual_protein = nutrition.protein / servings
        actual_fat = nutrition.fat / servings
        actual_carbs = nutrition.carbs / servings
        
        return {
            "per_serving": {
                "calories": actual_calories,
                "protein": actual_protein,
                "fat": actual_fat,
                "carbs": actual_carbs,
                "fiber": nutrition.fiber / servings
            },
            "daily_percentage": {
                "calories": round(actual_calories / daily_needs["calories"] * 100, 1),
                "protein": round(actual_protein / daily_needs["protein"] * 100, 1),
                "fat": round(actual_fat / daily_needs["fat"] * 100, 1),
                "carbs": round(actual_carbs / daily_needs["carbs"] * 100, 1)
            },
            "health_tips": NutritionCalculator._generate_health_tips(
                actual_calories, actual_protein, actual_fat, actual_carbs
            )
        }
    
    @staticmethod
    def _generate_health_tips(calories: float, protein: float, fat: float, carbs: float) -> List[str]:
        """生成健康建议"""
        tips = []
        
        if calories < 200:
            tips.append("这是一道低热量菜品，适合减肥期间食用")
        elif calories > 400:
            tips.append("这道菜热量较高，建议搭配蔬菜食用")
        
        if protein > 15:
            tips.append("蛋白质丰富，有助于肌肉修复和生长")
        
        if fat > 20:
            tips.append("脂肪含量较高，适量食用")
        
        if carbs < 10:
            tips.append("低碳水化合物，适合生酮饮食")
        
        return tips
    
    @staticmethod
    def is_suitable_for_diet(
        nutrition: Nutrition, 
        diet_type: str,
        servings: int = 1
    ) -> Dict:
        """
        判断是否适合特定饮食
        """
        calories_per_serving = nutrition.calories / servings
        
        diet_criteria = {
            "减肥": {
                "max_calories": 300,
                "description": "低热量、高纤维"
            },
            "增肌": {
                "min_protein": 20,
                "description": "高蛋白"
            },
            "低碳": {
                "max_carbs": 10,
                "description": "低碳水化合物"
            },
            "生酮": {
                "max_carbs": 5,
                "description": "极低碳水、高脂肪"
            }
        }
        
        if diet_type not in diet_criteria:
            return {
                "suitable": True,
                "message": "暂无特定判断标准"
            }
        
        criteria = diet_criteria[diet_type]
        suitable = True
        reasons = []
        
        if "max_calories" in criteria and calories_per_serving > criteria["max_calories"]:
            suitable = False
            reasons.append(f"热量({calories_per_serving:.0f}卡)超过{criteria['max_calories']}卡限制")
        
        if "min_protein" in criteria and nutrition.protein < criteria["min_protein"]:
            suitable = False
            reasons.append(f"蛋白质({nutrition.protein}g)低于{criteria['min_protein']}g要求")
        
        if "max_carbs" in criteria and nutrition.carbs > criteria["max_carbs"]:
            suitable = False
            reasons.append(f"碳水({nutrition.carbs}g)超过{criteria['max_carbs']}g限制")
        
        return {
            "suitable": suitable,
            "message": "适合" + criteria["description"] if suitable else "；".join(reasons),
            "diet_type": diet_type
        }


# 单例模式
nutrition_calculator = NutritionCalculator()