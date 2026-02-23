"""
增强的对话管理器 - 集成 LangChain Memory
支持持久化存储和向量检索历史对话
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import json
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from app.models.chat import ChatMessage, ConversationContext


class EnhancedConversationManager:
    """增强的对话管理器"""
    
    def __init__(self):
        self.conversations: Dict[str, ConversationContext] = {}
        self.chat_histories: Dict[str, ChatMessageHistory] = {}
    
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
        
        self.chat_histories[conversation_id] = ChatMessageHistory()
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        return self.conversations.get(conversation_id)
    
    def get_chat_history(self, conversation_id: str) -> Optional[ChatMessageHistory]:
        return self.chat_histories.get(conversation_id)
    
    def add_message(
        self, 
        conversation_id: str, 
        role: str, 
        content: str,
        ingredients: Optional[List[str]] = None,
        restrictions: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ):
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
        
        if ingredients:
            conversation.detected_ingredients.extend(ingredients)
            conversation.detected_ingredients = list(set(conversation.detected_ingredients))
        
        if restrictions:
            conversation.detected_restrictions.extend(restrictions)
            conversation.detected_restrictions = list(set(conversation.detected_restrictions))
        
        if conversation_id in self.chat_histories:
            history = self.chat_histories[conversation_id]
            if role == "user":
                history.add_user_message(content)
            elif role == "assistant":
                history.add_ai_message(content)
    
    def get_recent_context(self, conversation_id: str, limit: int = 5) -> List[Dict]:
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return []
        
        recent_messages = conversation.messages[-limit:]
        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
        ]
    
    def get_langchain_history(self, conversation_id: str) -> str:
        history = self.chat_histories.get(conversation_id)
        if not history:
            return ""
        
        history_str = ""
        for msg in history.messages:
            if isinstance(msg, HumanMessage):
                history_str += f"用户: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                history_str += f"助手: {msg.content}\n"
        
        return history_str
    
    def get_conversation_summary(self, conversation_id: str) -> str:
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
        if conversation_id in self.conversations:
            self.conversations[conversation_id].user_preferences.update(preferences)
    
    def get_user_context_for_prompt(self, conversation_id: str) -> str:
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return ""
        
        context_parts = []
        
        if conversation.detected_ingredients:
            context_parts.append(f"用户已有食材: {', '.join(conversation.detected_ingredients)}")
        
        if conversation.detected_restrictions:
            context_parts.append(f"用户饮食限制: {', '.join(conversation.detected_restrictions)}")
        
        if conversation.user_preferences:
            prefs = ', '.join([f"{k}={v}" for k, v in conversation.user_preferences.items()])
            context_parts.append(f"用户偏好: {prefs}")
        
        return '\n'.join(context_parts) if context_parts else ""
    
    def clear_conversation(self, conversation_id: str):
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
        if conversation_id in self.chat_histories:
            del self.chat_histories[conversation_id]
    
    def search_similar_conversations(
        self, 
        query: str, 
        user_id: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict]:
        results = []
        for conv_id, conv in self.conversations.items():
            if user_id and conv.user_preferences.get('user_id') != user_id:
                continue
            
            if any(query in msg.content for msg in conv.messages):
                results.append({
                    'conversation_id': conv_id,
                    'messages': conv.messages[-3:],
                    'ingredients': conv.detected_ingredients,
                    'restrictions': conv.detected_restrictions
                })
        
        return results[:top_k]


enhanced_conversation_manager = EnhancedConversationManager()
