from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseRuntime(ABC):
    """运行时环境基类"""
    
    @abstractmethod
    async def connect(self) -> None:
        """连接到运行时环境"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """断开与运行时环境的连接"""
        pass

    @abstractmethod
    async def execute_action(self, action: Dict[str, Any], context: Dict[str, Any], task_id: int) -> Dict[str, Any]:
        """
        执行动作
        
        Args:
            action: 动作信息
            context: 上下文信息
            task_id: 任务ID
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        获取运行时状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """清理运行时环境"""
        pass

    @abstractmethod
    async def validate_action(self, action: Dict[str, Any]) -> bool:
        """
        验证动作是否有效
        
        Args:
            action: 动作信息
            
        Returns:
            bool: 是否有效
        """
        pass

    @abstractmethod
    async def get_available_tools(self) -> List[str]:
        """
        获取可用的工具列表
        
        Returns:
            List[str]: 工具列表
        """
        pass

    @abstractmethod
    async def get_resource_usage(self) -> Dict[str, Any]:
        """
        获取资源使用情况
        
        Returns:
            Dict[str, Any]: 资源使用信息
        """
        pass

    @abstractmethod
    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        处理错误
        
        Args:
            error: 错误信息
            
        Returns:
            Dict[str, Any]: 错误处理结果
        """
        pass 