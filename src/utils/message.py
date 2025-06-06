from typing import Dict, Any, List
from datetime import datetime
import json
import os
from src.models.message import Message

def format_message(
    role: str,
    content: str,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    格式化消息
    
    Args:
        role: 角色
        content: 内容
        metadata: 元数据
        
    Returns:
        Dict[str, Any]: 格式化后的消息
    """
    message = {
        'role': role,
        'content': content,
        'timestamp': datetime.now().isoformat()
    }
    
    if metadata:
        message['metadata'] = metadata
        
    return message

def format_messages(
    messages: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    格式化消息列表
    
    Args:
        messages: 消息列表
        
    Returns:
        List[Dict[str, Any]]: 格式化后的消息列表
    """
    return [
        format_message(
            role=msg.get('role', 'user'),
            content=msg.get('content', ''),
            metadata=msg.get('metadata')
        )
        for msg in messages
    ]

class MessageFormatter:
    """消息格式化类"""
    
    @staticmethod
    def format(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化消息
        
        Args:
            data: 消息数据
            
        Returns:
            Dict[str, Any]: 格式化后的消息
        """
        return {
            'status': data.get('status', 'success'),
            'task_id': data.get('task_id'),
            'action_type': data.get('action_type'),
            'content': data.get('content', ''),
            'comments': data.get('comments', ''),
            'memorized': data.get('memorized', []),
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    async def save_to_db(message: Dict[str, Any], conversation_id: str) -> None:
        """
        保存消息到数据库
        
        Args:
            message: 消息数据
            conversation_id: 对话ID
        """
        # 确保目录存在
        os.makedirs('data/messages', exist_ok=True)
        
        # 构建文件路径
        filepath = f'data/messages/{conversation_id}.json'
        
        # 读取现有消息
        messages = []
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    messages = json.load(f)
                except json.JSONDecodeError:
                    messages = []
        
        # 添加新消息
        messages.append(message)
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2) 