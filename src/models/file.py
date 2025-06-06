from typing import Optional
from datetime import datetime
from pydantic import Field
from .base_model import BaseModel

class File(BaseModel):
    """文件模型"""
    
    conversation_id: str
    name: str
    path: str
    content: Optional[str] = None
    size: int = 0
    is_directory: bool = False
    
    class Config:
        """模型配置"""
        schema_extra = {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "example.py",
                "path": "workspace/example.py",
                "content": "print('Hello, World!')",
                "size": 20,
                "is_directory": False
            }
        }
    
    @classmethod
    def create_file(cls, conversation_id: str, name: str, path: str, content: str = None) -> 'File':
        """创建文件"""
        return cls(
            conversation_id=conversation_id,
            name=name,
            path=path,
            content=content,
            size=len(content) if content else 0,
            is_directory=False
        )
    
    @classmethod
    def create_directory(cls, conversation_id: str, name: str, path: str) -> 'File':
        """创建目录"""
        return cls(
            conversation_id=conversation_id,
            name=name,
            path=path,
            is_directory=True
        ) 