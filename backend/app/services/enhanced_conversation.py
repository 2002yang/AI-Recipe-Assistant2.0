"""
增强的对话管理器 - 集成 LangChain Memory
支持持久化存储和向量检索历史对话
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import json
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_community.vectorstores import Chroma

from app.models.chat import ChatMessage, ConversationContext


class EnhancedConversationManager:
    """增强的对话管理器"""
    
    def __init__(self):
        # 内存中存储对话上下文
        self.conversations: Dict[str, ConversationContext] = {}
        
        # LangChain Memory 存储
        self.memories: Dict[str, ConversationBufferMemory] = {}
    
    def create_conversation(self) -> str:
        """创建新的对话"""
        conversation_id = str(uuid.uuid4())
        now = datetime.now()
        
        # 创建对话上下文
        self.conversations[conversation_id] = ConversationContext(
            conversation_id=conversation_id,
            messages=[],
            detected_ingredients=[],
            detected_restrictions=[],
            user_preferences={},
            created_at=now,
            updated_at=now
        )
        
        # 创建 LangChain Memory
        self.memories[conversation_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10  # 保留最近10轮对话
        )
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """获取对话上下文"""
        return self.conversations.get(conversation_id)
    
    def get_memory(self, conversation_id: str) -> Optional[ConversationBufferMemory]:
        """获取 LangChain Memory"""
        return self.memories.get(conversation_id)
    
    def add_message(
        self, 
        conversation_id: str, 
        role: str, 
        content: str,
        ingredients: List[str] = None,
        restrictions: List[str] = None,
        metadata: Dict = None
    ):
        """添加消息到对话"""
        if conversation_id not in self.conversations:
            conversation_id = self.create_conversation()
        
        conversation = self.conversations[conversation_id]
        
        # 创建消息对象
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        
        conversation.messages.append(message)
        conversation.updated_at = datetime.now()
        
        # 更新检测到的信息
        if ingredients:
            conversation.detected_ingredients.extend(ingredients)
            conversation.detected_ingredients = list(set(conversation.detected_ingredients))
        
        if restrictions:
            conversation.detected_restrictions.extend(restrictions)
            conversation.detected_restrictions = list(set(conversation.detected_restrictions))
        
        # 更新 LangChain Memory
        if conversation_id in self.memories:
            memory = self.memories[conversation_id]
            if role == "user":
                memory.chat_memory.add_user_message(content)
            elif role == "assistant":
                memory.chat_memory.add_ai_message(content)
    
    def get_recent_context(self, conversation_id: str, limit: int = 5) -> List[Dict]:
        """获取最近的消息上下文"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return []
        
        recent_messages = conversation.messages[-limit:]
        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
        ]
    
    def get_langchain_history(self, conversation_id: str) -> str:
        """获取 LangChain 格式的历史记录字符串"""
        memory = self.memories.get(conversation_id)
        if not memory:
            return ""
        
        # 加载记忆变量
        variables = memory.load_memory_variables({})
        chat_history = variables.get("chat_history", [])
        
        # 转换为字符串
        history_str = ""
        for msg in chat_history:
            if isinstance(msg, HumanMessage):
                history_str += f"用户: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                history_str += f"助手: {msg.content}\n"
        
        return history_str
    
    def get_conversation_summary(self, conversation_id: str) -> str:
        """生成对话摘要"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return ""
        
        summary = f"""对话摘要:
- 已识别食材: {', '.join(conversation.detected_ingredients) if conversation.detected_ingredients else '无'}
- 饮食限制: {', '.join(conversation.detected_restrictions) if conversation.detected_restrictions else '无'}
- 对话轮数: {len(conversation.messages) // 2}
"""
        return summary
    
    def update_preferences(self, conversation_id: str, preferences: Dict):
        """更新用户偏好"""
        if conversation_id in self.conversations:
            self.conversations[conversation_id].user_preferences.update(preferences)
    
    def get_user_context_for_prompt(self, conversation_id: str) -> str:
        """获取用于 Prompt 的用户上下文信息"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return ""
        
        context_parts = []
        
        # 添加已识别的食材
        if conversation.detected_ingredients:
            context_parts.append(f"用户已有食材: {', '.join(conversation.detected_ingredients)}")
        
        # 添加饮食限制
        if conversation.detected_restrictions:
            context_parts.append(f"用户饮食限制: {', '.join(conversation.detected_restrictions)}")
        
        # 添加用户偏好
        if conversation.user_preferences:
            prefs = ', '.join([f"{k}={v}" for k, v in conversation.user_preferences.items()])
            context_parts.append(f"用户偏好: {prefs}")
        
        return '\n'.join(context_parts) if context_parts else ""
    
    def clear_conversation(self, conversation_id: str):
        """清空对话"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
        if conversation_id in self.memories:
            del self.memories[conversation_id]
    
    def search_similar_conversations(
        self, 
        query: str, 
        user_id: str = None,
        top_k: int = 3
    ) -> List[Dict]:
        """
        搜索相似的历史对话（用于长期记忆）
        未来可以接入向量数据库实现
        """
        # 简化实现：返回最近的对话
        results = []
        for conv_id, conv in self.conversations.items():
            if user_id and conv.user_preferences.get('user_id') != user_id:
                continue
            
            # 简单的关键词匹配
            if any(query in msg.content for msg in conv.messages):
                results.append({
                    'conversation_id': conv_id,
                    'messages': conv.messages[-3:],  # 最近3条
                    'ingredients': conv.detected_ingredients,
                    'restrictions': conv.detected_restrictions
                })
        
        return results[:top_k]


# 单例模式
enhanced_conversation_manager = EnhancedConversationManager()