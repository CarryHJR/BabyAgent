from typing import List, Dict, Any
from datetime import datetime
from src.models.message import Message

class ConversationMemory:
    """对话记忆管理"""
    
    def __init__(self, conversation_id: str = "default", max_messages: int = 10):
        self.conversation_id = conversation_id
        self.max_messages = max_messages
        self.messages: List[Message] = []
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """添加消息"""
        message = Message(
            conversation_id=self.conversation_id,
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        
        # 保持消息数量在限制范围内
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_messages(self) -> List[Message]:
        """获取所有消息"""
        return self.messages
    
    def get_formatted_history(self) -> str:
        """获取格式化的对话历史"""
        history = []
        for msg in self.messages:
            history.append(f"{msg.role}: {msg.content}")
        return "\n".join(history)
    
    def clear(self):
        """清除所有消息"""
        self.messages = []
    
    def get_last_message(self) -> Message:
        """获取最后一条消息"""
        return self.messages[-1] if self.messages else None
    
    def get_messages_by_role(self, role: str) -> List[Message]:
        """获取指定角色的消息"""
        return [msg for msg in self.messages if msg.role == role] 