from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class ToolResult(BaseModel):
    """工具执行结果"""
    status: str
    meta: Optional[Any] = None
    error: Optional[str] = None

class BaseTool(ABC):
    """工具基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具模式"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters()
        }
    
    @abstractmethod
    def _get_parameters(self) -> Dict[str, Any]:
        """获取参数模式"""
        pass 