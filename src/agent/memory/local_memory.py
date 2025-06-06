from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path
from datetime import datetime

class LocalMemory:
    """本地记忆实现，用于存储和检索执行历史"""
    
    def __init__(self, options: Dict[str, Any] = None):
        """
        初始化本地记忆
        
        Args:
            options: 配置选项，包含key等
        """
        self.options = options or {}
        self.key = self.options.get('key', 'default')
        print(f"LocalMemory initialized with key: {self.key}")
        self.cache_dir = Path(__file__).parent.parent.parent.parent / 'cache' / 'memory'
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.messages = []
        self._load_memory()
        
    def _get_file_path(self) -> Path:
        """获取记忆文件路径"""
        return self.cache_dir / f"{self.key}.json"
        
    def _load_memory(self) -> None:
        """加载记忆"""
        file_path = self._get_file_path()
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
            except Exception as e:
                print(f"Error loading memory for {self.key}: {e}")
                self.messages = []
                
    def _save_memory(self) -> None:
        """保存记忆"""
        file_path = self._get_file_path()
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
            print(f"Memory for task {self.key} saved successfully.")
        except Exception as e:
            print(f"Error saving memory for {self.key}: {e}")
            raise Exception(f"Failed to save memory for task {self.key}")
            
    async def add_message(self, role: str, content: str, action_type: str = '', memorized: bool = False) -> None:
        """
        添加消息
        
        Args:
            role: 消息角色
            content: 消息内容
            action_type: 动作类型
            memorized: 是否记忆
        """
        self.messages.append({
            'role': role,
            'content': content,
            'action_type': action_type,
            'memorized': memorized,
            'timestamp': str(datetime.now())
        })
        self._save_memory()
        
    async def get_messages(self, summarize: bool = False) -> List[Dict[str, Any]]:
        """
        获取消息历史
        
        Args:
            summarize: 是否总结消息
            
        Returns:
            List[Dict[str, Any]]: 消息列表
        """
        if summarize and len(self.messages) > 10:
            return self.messages[-10:]
        return self.messages
        
    async def get_memorized_content(self) -> str:
        """
        获取记忆内容
        
        Returns:
            str: 记忆内容
        """
        list = []
        for message in self.messages:
            action_type = message.get('action_type', '')
            memorized = message.get('memorized', False)
            if not memorized:
                continue
            list.append(f"{action_type.upper()}: {message['content']}")
        return "\n".join(list)

    async def clear_memory(self) -> None:
        """清除所有记忆"""
        file_path = self._get_file_path()
        try:
            if file_path.exists():
                os.remove(file_path)
            print(f"Memory for task {self.key} cleared successfully.")
        except Exception as e:
            print(f"Error clearing memory for {self.key}: {e}")
            raise Exception(f"Failed to clear memory for task {self.key}")

    def get_context(self) -> Dict[str, Any]:
        """
        获取当前上下文
        
        Returns:
            Dict[str, Any]: 上下文信息
        """
        return {
            'key': self.key,
            'message_count': len(self.messages),
            'last_message': self.messages[-1] if self.messages else None
        }

    def update_max_messages(self, max_messages: int) -> None:
        """
        更新最大消息数量
        
        Args:
            max_messages: 新的最大消息数量
        """
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
            self._save_memory() 