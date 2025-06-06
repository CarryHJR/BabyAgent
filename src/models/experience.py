import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class Experience:
    """经验模型"""
    
    def __init__(self, id: str, title: str, goal: str, content: str, is_enabled: bool = True):
        self.id = id
        self.title = title
        self.goal = goal
        self.content = content
        self.is_enabled = is_enabled
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @classmethod
    async def get(cls, id: str) -> Optional['Experience']:
        """获取单个经验"""
        experiences = await cls.filter(is_enabled=True)
        for exp in experiences:
            if exp.id == id:
                return exp
        return None
    
    @classmethod
    async def filter(cls, is_enabled: bool = None) -> List['Experience']:
        """获取经验列表"""
        experiences = []
        data_dir = os.path.join(os.path.dirname(__file__), '../../data')
        os.makedirs(data_dir, exist_ok=True)
        
        file_path = os.path.join(data_dir, 'experiences.json')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if is_enabled is None or item.get('is_enabled') == is_enabled:
                        exp = cls(
                            id=item['id'],
                            title=item['title'],
                            goal=item['goal'],
                            content=item['content'],
                            is_enabled=item.get('is_enabled', True)
                        )
                        exp.created_at = datetime.fromisoformat(item['created_at'])
                        exp.updated_at = datetime.fromisoformat(item['updated_at'])
                        experiences.append(exp)
        return experiences
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'goal': self.goal,
            'content': self.content,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    async def create(cls, title: str, goal: str, content: str) -> 'Experience':
        """创建新经验"""
        exp = cls(
            id=str(uuid.uuid4()),
            title=title,
            goal=goal,
            content=content
        )
        await exp.save()
        return exp
    
    async def save(self):
        """保存经验"""
        data_dir = os.path.join(os.path.dirname(__file__), '../../data')
        os.makedirs(data_dir, exist_ok=True)
        
        file_path = os.path.join(data_dir, 'experiences.json')
        experiences = []
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                experiences = json.load(f)
        
        # 更新或添加经验
        found = False
        for i, item in enumerate(experiences):
            if item['id'] == self.id:
                experiences[i] = self.to_dict()
                found = True
                break
        
        if not found:
            experiences.append(self.to_dict())
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(experiences, f, ensure_ascii=False, indent=2) 