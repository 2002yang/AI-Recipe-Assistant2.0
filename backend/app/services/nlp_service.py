import os
import httpx
from typing import List, Dict, Any
import json


class NLPService:
    """DeepSeek AI 自然语言处理服务"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "sk-5c3ef01a3b5b475bafe94d5051c6ef0b")
        self.api_base = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
    
    async def parse_user_intent(self, message: str) -> Dict[str, Any]:
        """
        解析用户意图，提取关键信息
        """
        system_prompt = """你是一个专业的美食助手，负责解析用户的自然语言输入。
请从用户消息中提取以下信息并以JSON格式返回：
{
    "intent": "用户意图(recommend_by_ingredients/cooking_guide/nutrition_query/substitution/multi_turn/other)",
    "ingredients": ["食材列表"],
    "restrictions": ["饮食限制"],
    "preferences": ["口味偏好"],
    "target_dish": "目标菜品（如果有）",
    "question_type": "问题类型"
}

注意：
- 食材要标准化，例如"西红柿"统一为"番茄"
- 饮食限制包括：素食、纯素、无海鲜、无辣、低碳水、减肥
- 如果用户提到过敏，也要标记在restrictions中"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # 尝试解析JSON
                    try:
                        parsed = json.loads(content)
                        return parsed
                    except json.JSONDecodeError:
                        # 如果返回的不是纯JSON，尝试提取
                        return self._fallback_parse(message)
                else:
                    print(f"API Error: {response.status_code}")
                    return self._fallback_parse(message)
                    
        except Exception as e:
            print(f"Error calling DeepSeek API: {e}")
            return self._fallback_parse(message)
    
    def _fallback_parse(self, message: str) -> Dict[str, Any]:
        """当API调用失败时的备用解析"""
        result = {
            "intent": "recommend_by_ingredients",
            "ingredients": [],
            "restrictions": [],
            "preferences": [],
            "target_dish": None,
            "question_type": "general"
        }
        
        # 简单的关键词匹配
        common_ingredients = [
            "番茄", "鸡蛋", "土豆", "猪肉", "鸡肉", "牛肉", "鱼", "虾",
            "豆腐", "茄子", "青椒", "洋葱", "大蒜", "姜", "葱",
            "胡萝卜", "白菜", "青菜", "黄瓜", "冬瓜", "南瓜",
            "面条", "米饭", "粉丝", "腐竹"
        ]
        
        for ingredient in common_ingredients:
            if ingredient in message:
                result["ingredients"].append(ingredient)
        
        # 检测饮食限制
        if any(word in message for word in ["素食", "不吃肉", "素"]):
            result["restrictions"].append("素食")
        if any(word in message for word in ["海鲜", "鱼", "虾"]) and "过敏" in message:
            result["restrictions"].append("无海鲜")
        if "辣" in message and ("不吃" in message or "不要" in message):
            result["restrictions"].append("无辣")
        if "低碳水" in message or "低碳" in message:
            result["restrictions"].append("低碳水")
        if "减肥" in message:
            result["restrictions"].append("减肥")
        
        return result
    
    async def generate_response(
        self, 
        user_message: str, 
        context: List[Dict],
        recipes: List[Dict] = None
    ) -> str:
        """
        生成对话回复
        """
        system_prompt = """你是"美食推荐与食谱智能助手"，一个专业、友好的烹饪助手。

你的特点：
1. 根据用户提供的食材推荐合适的菜谱
2. 详细解释烹饪步骤，适合烹饪新手
3. 提供营养和热量信息
4. 给出食材替代建议
5. 支持多轮对话，记住之前的上下文

回复风格：
- 热情友好，像一位经验丰富的厨师
- 回答清晰、结构分明
- 适当使用表情符号增加亲和力
- 如果推荐菜谱，请简洁介绍菜品特色

注意：
- 如果用户询问具体做法，要提供详细步骤
- 如果用户询问营养，提供热量和主要营养成分
- 如果用户需要食材替代，解释替代原因"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加上下文
        for msg in context[-5:]:  # 只保留最近5轮对话
            messages.append(msg)
        
        # 添加当前消息
        messages.append({"role": "user", "content": user_message})
        
        # 如果有推荐菜谱信息，添加到消息中
        if recipes:
            recipe_info = "\n\n相关菜谱信息：\n"
            for r in recipes:
                # r 包含嵌套的 recipe 对象
                recipe = r['recipe']
                recipe_info += f"- {recipe['name']}：{', '.join(recipe['tags'])}，难度{recipe['difficulty']}，约{recipe['time']}\n"
                recipe_info += f"  匹配度：{int(r['match_score']*100)}%，已有食材：{', '.join(r['matched_ingredients'])}\n"
            messages[-1]["content"] += recipe_info
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    return "抱歉，我暂时无法回答，请稍后再试。"
                    
        except Exception as e:
            print(f"Error generating response: {e}")
            return "抱歉，我遇到了技术问题，请稍后再试。"
    
    async def generate_substitution_suggestions(
        self, 
        ingredient: str, 
        recipe_name: str
    ) -> str:
        """
        生成食材替代建议
        """
        prompt = f"用户在制作{recipe_name}时没有{ingredient}，请提供3-5个可以替代的食材，并简要说明为什么可以替代。"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "你是食材替代专家，请根据食材的口味、质地和功能提供合适的替代建议。"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    return f"建议尝试用相似的食材替代{ingredient}。"
                    
        except Exception as e:
            print(f"Error generating substitution: {e}")
            return f"建议尝试用相似的食材替代{ingredient}。"


# 单例模式
nlp_service = NLPService()