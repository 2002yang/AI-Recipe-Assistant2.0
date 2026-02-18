"""
LangChain 版本的 NLP 服务
使用 Chain 和 Memory 提供更智能的对话体验
"""
import os
from typing import List, Dict, Any
from langchain.chains import LLMChain, ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.llms import DeepSeek
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import json

from app.services.vector_store import vector_store
from app.services.recipe_matcher import recipe_service


class LangChainNLPService:
    """基于 LangChain 的 NLP 服务"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "sk-5c3ef01a3b5b475bafe94d5051c6ef0b")
        self.api_base = "https://api.deepseek.com/v1"
        
        # 初始化 LLM
        self.llm = self._init_llm()
        
        # 初始化各种 Chain
        self.intent_chain = self._create_intent_chain()
        self.response_chain = self._create_response_chain()
        
        print("LangChain NLP Service initialized")
    
    def _init_llm(self):
        """初始化 LLM"""
        # 使用 OpenAI 兼容的方式调用 DeepSeek
        from langchain_openai import ChatOpenAI
        
        return ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=self.api_key,
            openai_api_base=self.api_base,
            temperature=0.7,
            max_tokens=1000
        )
    
    def _create_intent_chain(self):
        """创建意图识别 Chain"""
        intent_prompt = PromptTemplate(
            input_variables=["input"],
            template="""你是一个专业的美食助手。请分析用户的输入，提取以下信息并以 JSON 格式返回：

用户输入: {input}

请返回以下格式的 JSON：
{{
    "intent": "用户意图，可选值: recommend_by_ingredients(食材推荐)/cooking_guide(烹饪指导)/nutrition_query(营养查询)/substitution(替代建议)/general(一般对话)",
    "ingredients": ["提取的食材列表，如番茄、鸡蛋等"],
    "restrictions": ["饮食限制，如素食、无辣、低碳水等"],
    "preferences": ["口味偏好"],
    "target_dish": "用户提到的具体菜品名称，如果没有则为空字符串",
    "question_type": "问题类型"
}}

注意：
1. 只返回 JSON，不要有其他文字
2. 食材要标准化（如"西红柿"应为"番茄"）
3. 识别用户提到的饮食限制和过敏信息
4. 如果用户说"不吃/不要/过敏"等，要标记在 restrictions 中
"""
        )
        
        return intent_prompt | self.llm | JsonOutputParser()
    
    def _create_response_chain(self):
        """创建对话回复 Chain"""
        response_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是"美食推荐与食谱智能助手"，一个专业、友好的烹饪助手。

你的特点：
1. 根据用户的食材和偏好推荐合适的菜谱
2. 详细解释烹饪步骤，适合烹饪新手
3. 提供营养和热量信息
4. 给出食材替代建议

回复风格：
- 热情友好，像一位经验丰富的厨师
- 回答清晰、结构分明
- 适当使用 emoji 增加亲和力
- 如果推荐菜谱，请简洁介绍菜品特色

当前对话上下文：
{history}
"""),
            ("human", "{input}")
        ])
        
        return response_prompt | self.llm | StrOutputParser()
    
    async def parse_user_intent(self, message: str) -> Dict[str, Any]:
        """
        解析用户意图 - 使用 LangChain Chain
        """
        try:
            # 使用 Chain 解析意图
            result = await self.intent_chain.ainvoke({"input": message})
            
            # 确保所有必需字段存在
            defaults = {
                "intent": "general",
                "ingredients": [],
                "restrictions": [],
                "preferences": [],
                "target_dish": "",
                "question_type": "general"
            }
            defaults.update(result)
            return defaults
            
        except Exception as e:
            print(f"Error in intent parsing: {e}")
            # 降级到备用解析
            return self._fallback_parse(message)
    
    def _fallback_parse(self, message: str) -> Dict[str, Any]:
        """备用解析方法"""
        result = {
            "intent": "recommend_by_ingredients",
            "ingredients": [],
            "restrictions": [],
            "preferences": [],
            "target_dish": "",
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
        if "海鲜" in message and "过敏" in message:
            result["restrictions"].append("无海鲜")
        if "辣" in message and ("不吃" in message or "不要" in message):
            result["restrictions"].append("无辣")
        if "低碳水" in message or "低碳" in message:
            result["restrictions"].append("低碳水")
        if "减肥" in message:
            result["restrictions"].append("减肥")
        
        return result
    
    async def search_recipes_with_rag(
        self, 
        query: str, 
        ingredients: List[str] = None,
        restrictions: List[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        使用 RAG 搜索菜谱
        
        Args:
            query: 自然语言查询
            ingredients: 食材列表（可选）
            restrictions: 饮食限制（可选）
            top_k: 返回数量
            
        Returns:
            匹配的菜谱列表
        """
        # 构建语义查询
        if ingredients:
            search_query = f"包含{ '、'.join(ingredients)}的菜"
            if restrictions:
                search_query += f"，{'、'.join(restrictions)}"
        else:
            search_query = query
        
        print(f"RAG Search Query: {search_query}")
        
        # 使用向量搜索
        vector_results = vector_store.search(search_query, n_results=top_k * 2)
        
        # 获取完整菜谱信息
        enriched_results = []
        for vr in vector_results:
            # 从原始数据中获取完整信息
            full_recipe = recipe_service.get_recipe_by_id(vr['id'])
            if full_recipe:
                # 检查饮食限制
                if restrictions and self._check_restrictions(full_recipe, restrictions):
                    continue
                
                # 计算食材匹配
                matched_ingredients = []
                if ingredients:
                    recipe_ingredients = [i.name for i in full_recipe.ingredients]
                    matched_ingredients = list(set(ingredients) & set(recipe_ingredients))
                
                enriched_results.append({
                    "recipe": full_recipe,
                    "match_score": vr['similarity'],
                    "matched_ingredients": matched_ingredients,
                    "missing_ingredients": [],
                    "vector_similarity": vr['similarity']
                })
        
        # 按匹配分数排序
        enriched_results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return enriched_results[:top_k]
    
    def _check_restrictions(self, recipe, restrictions: List[str]) -> bool:
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
    
    async def generate_response(
        self, 
        user_message: str, 
        history: List[Dict] = None,
        recipes: List[Dict] = None
    ) -> str:
        """
        生成对话回复 - 使用 LangChain
        """
        try:
            # 格式化历史对话
            history_text = ""
            if history:
                for msg in history[-5:]:  # 最近5轮
                    if msg['role'] == 'user':
                        history_text += f"用户: {msg['content']}\n"
                    else:
                        history_text += f"助手: {msg['content']}\n"
            
            # 添加菜谱信息
            input_text = user_message
            if recipes:
                input_text += "\n\n相关菜谱信息：\n"
                for i, r in enumerate(recipes[:3], 1):
                    recipe = r['recipe']
                    input_text += f"{i}. {recipe.name}：{', '.join(recipe.tags)}，难度{recipe.difficulty}\n"
            
            # 使用 Chain 生成回复
            response = await self.response_chain.ainvoke({
                "history": history_text,
                "input": input_text
            })
            
            return response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "抱歉，我暂时无法回答，请稍后再试。"
    
    async def generate_substitution_suggestions(
        self, 
        ingredient: str, 
        recipe_name: str
    ) -> str:
        """生成食材替代建议"""
        prompt = f"用户在制作{recipe_name}时没有{ingredient}，请提供3-5个可以替代的食材，并简要说明为什么可以替代。"
        
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"Error generating substitution: {e}")
            return f"建议尝试用相似的食材替代{ingredient}。"


# 单例模式
langchain_nlp_service = LangChainNLPService()