from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import Field
from .base_model import BaseModel

class Message(BaseModel):
    """消息模型"""
    
    conversation_id: str
    role: str
    content: str
    status: str = "success"
    action_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """模型配置"""
        schema_extra = {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "user",
                "content": "你好",
                "status": "success",
                "action_type": "message",
                "metadata": {}
            }
        }
    
    @classmethod
    def create_user_message(cls, conversation_id: str, content: str) -> 'Message':
        """创建用户消息"""
        return cls(
            conversation_id=conversation_id,
            role="user",
            content=content,
            action_type="message"
        )
    
    @classmethod
    def create_assistant_message(cls, conversation_id: str, content: str, action_type: str = "message") -> 'Message':
        """创建助手消息"""
        return cls(
            conversation_id=conversation_id,
            role="assistant",
            content=content,
            action_type=action_type
        )
    
    @classmethod
    def create_system_message(cls, conversation_id: str, content: str) -> 'Message':
        """创建系统消息"""
        return cls(
            conversation_id=conversation_id,
            role="system",
            content=content,
            action_type="system"
        ) 