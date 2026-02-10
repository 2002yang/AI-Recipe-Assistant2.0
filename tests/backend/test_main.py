import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.recipe_matcher import recipe_service
from app.services.nlp_service import nlp_service

client = TestClient(app)


class TestRecipeMatcher:
    """测试菜谱匹配功能"""
    
    def test_load_recipes(self):
        """测试菜谱数据加载"""
        assert len(recipe_service.recipes) == 50
        assert recipe_service.recipes[0].name == "番茄炒蛋"
    
    def test_search_by_ingredients(self):
        """测试基于食材搜索"""
        results = recipe_service.search_by_ingredients(
            ingredients=["番茄", "鸡蛋"],
            top_k=3
        )
        assert len(results) > 0
        # 番茄炒蛋应该排在第一位
        assert results[0]["recipe"].name == "番茄炒蛋"
        assert results[0]["match_score"] > 0.5
    
    def test_search_with_restrictions(self):
        """测试带饮食限制的搜索"""
        results = recipe_service.search_by_ingredients(
            ingredients=["豆腐"],
            restrictions=["素食"],
            top_k=5
        )
        # 确保没有肉类菜品
        for result in results:
            for ingredient in result["recipe"].ingredients:
                assert ingredient.category != "肉类"
    
    def test_get_recipe_by_id(self):
        """测试获取菜谱详情"""
        recipe = recipe_service.get_recipe_by_id(1)
        assert recipe is not None
        assert recipe.name == "番茄炒蛋"
        assert len(recipe.ingredients) > 0
        assert len(recipe.steps) > 0
    
    def test_get_substitutions(self):
        """测试获取食材替代建议"""
        subs = recipe_service.get_substitutions(3, "花生米")
        assert len(subs) > 0
        assert "腰果" in subs or "杏仁" in subs


class TestNutritionCalculator:
    """测试营养计算功能"""
    
    def test_calculate_daily_needs(self):
        """测试每日营养需求计算"""
        from app.services.nutrition_calc import nutrition_calculator
        
        needs = nutrition_calculator.calculate_daily_needs(
            weight=60, height=165, age=30, gender="female"
        )
        
        assert "calories" in needs
        assert "protein" in needs
        assert "fat" in needs
        assert "carbs" in needs
        assert needs["calories"] > 1000
        assert needs["protein"] > 50
    
    def test_analyze_meal_nutrition(self):
        """测试单餐营养分析"""
        from app.services.nutrition_calc import nutrition_calculator
        from app.models.recipe import Nutrition
        
        nutrition = Nutrition(
            calories=300, protein=15, fat=12, carbs=30, fiber=3
        )
        
        analysis = nutrition_calculator.analyze_meal_nutrition(nutrition, servings=2)
        
        assert "per_serving" in analysis
        assert "daily_percentage" in analysis
        assert analysis["per_serving"]["calories"] == 150
        assert "health_tips" in analysis
    
    def test_diet_suitability(self):
        """测试饮食适合性检查"""
        from app.services.nutrition_calc import nutrition_calculator
        from app.models.recipe import Nutrition
        
        # 低热量菜品应该适合减肥
        low_cal = Nutrition(calories=150, protein=10, fat=5, carbs=15, fiber=2)
        result = nutrition_calculator.is_suitable_for_diet(low_cal, "减肥")
        assert result["suitable"] is True
        
        # 高热量菜品应该不适合减肥
        high_cal = Nutrition(calories=500, protein=15, fat=30, carbs=40, fiber=1)
        result = nutrition_calculator.is_suitable_for_diet(high_cal, "减肥")
        assert result["suitable"] is False


class TestAPI:
    """测试API端点"""
    
    def test_root(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        assert "美食推荐" in response.json()["message"]
    
    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_get_recipes(self):
        """测试获取菜谱列表"""
        response = client.get("/api/recipes/list")
        assert response.status_code == 200
        assert len(response.json()) == 50
    
    def test_get_recipe_detail(self):
        """测试获取菜谱详情"""
        response = client.get("/api/recipes/1")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "番茄炒蛋"
        assert "ingredients" in data
        assert "steps" in data
    
    def test_search_recipes(self):
        """测试搜索菜谱"""
        response = client.post(
            "/api/recipes/search",
            json={"ingredients": ["番茄", "鸡蛋"], "top_k": 3}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0
    
    def test_get_nutrition(self):
        """测试获取营养信息"""
        response = client.get("/api/nutrition/recipe/1")
        assert response.status_code == 200
        data = response.json()
        assert "nutrition_per_serving" in data
        assert "health_tips" in data


class TestConversationManager:
    """测试对话管理器"""
    
    def test_create_conversation(self):
        """测试创建对话"""
        from app.services.conversation import conversation_manager
        
        conv_id = conversation_manager.create_conversation()
        assert conv_id is not None
        assert len(conv_id) > 0
        
        conversation = conversation_manager.get_conversation(conv_id)
        assert conversation is not None
        assert conversation.conversation_id == conv_id
    
    def test_add_message(self):
        """测试添加消息"""
        from app.services.conversation import conversation_manager
        
        conv_id = conversation_manager.create_conversation()
        conversation_manager.add_message(
            conv_id, "user", "我有番茄和鸡蛋",
            ingredients=["番茄", "鸡蛋"]
        )
        
        conversation = conversation_manager.get_conversation(conv_id)
        assert len(conversation.messages) == 1
        assert "番茄" in conversation.detected_ingredients
    
    def test_get_recent_context(self):
        """测试获取最近上下文"""
        from app.services.conversation import conversation_manager
        
        conv_id = conversation_manager.create_conversation()
        conversation_manager.add_message(conv_id, "user", "你好")
        conversation_manager.add_message(conv_id, "assistant", "你好！")
        conversation_manager.add_message(conv_id, "user", "我想吃番茄炒蛋")
        
        context = conversation_manager.get_recent_context(conv_id, limit=2)
        assert len(context) == 2
        assert context[-1]["content"] == "我想吃番茄炒蛋"


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])