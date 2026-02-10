from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    suggested_recipes: Optional[List[dict]] = []
    detected_ingredients: Optional[List[str]] = []
    detected_restrictions: Optional[List[str]] = []
    nutrition_info: Optional[dict] = None


class ConversationContext(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]
    detected_ingredients: List[str] = []
    detected_restrictions: List[str] = []
    user_preferences: Dict = {}
    created_at: datetime
    updated_at: datetime