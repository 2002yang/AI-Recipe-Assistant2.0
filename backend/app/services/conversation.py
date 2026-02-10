from typing import Dict, List
from datetime import datetime
import uuid
from app.models.chat import ChatMessage, ConversationContext


class ConversationManager:
    """对话管理器 - 管理多轮对话上下文"""
    
    def __init__(self):
        # 内存中存储对话上下文（生产环境应使用Redis或数据库）
        self.conversations: Dict[str, ConversationContext] = {}
    
    def create_conversation(self) -> str:
        """创建新的对话"""
        conversation_id = str(uuid.uuid4())
        now = datetime.now()
        
        self.conversations[conversation_id] = ConversationContext(
            conversation_id=conversation_id,
            messages=[],
            detected_ingredients=[],
            detected_restrictions=[],
            user_preferences={},
            created_at=now,
            updated_at=now
        )
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> ConversationContext:
        """获取对话上下文"""
        return self.conversations.get(conversation_id)
    
    def add_message(
        self, 
        conversation_id: str, 
        role: str, 
        content: str,
        ingredients: List[str] = None,
        restrictions: List[str] = None
    ):
        """添加消息到对话"""
        if conversation_id not in self.conversations:
            conversation_id = self.create_conversation()
        
        conversation = self.conversations[conversation_id]
        
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
    
    def update_preferences(self, conversation_id: str, preferences: Dict):
        """更新用户偏好"""
        if conversation_id in self.conversations:
            self.conversations[conversation_id].user_preferences.update(preferences)
    
    def clear_conversation(self, conversation_id: str):
        """清空对话"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]


# 单例模式
conversation_manager = ConversationManager()