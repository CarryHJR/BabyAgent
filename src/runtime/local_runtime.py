import os
import sys
import io
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, List, Optional
import psutil
import json
from pathlib import Path
import asyncio
from datetime import datetime

from src.runtime.base_runtime import BaseRuntime
from src.utils.message import Message
from src.config import get_config, get_workspace_dir, get_log_dir
from src.logger import get_logger


class LocalRuntime(BaseRuntime):
    """本地运行时"""
    
    def __init__(self):
        """初始化"""
        super().__init__()
        self.config = get_config()
        self.workspace_dir = get_workspace_dir()
        self.log_dir = get_log_dir()
        self.current_dir = None
        self.logger = get_logger(__name__)
        self.process = None
        self.connected = False
        self.available_tools = [
            'write_code',
            'read_file',
            'search_file',
            'execute_command'
        ]

    async def setup(self) -> None:
        """设置运行时环境"""
        try:
            # 创建工作目录
            self.workspace_dir.mkdir(parents=True, exist_ok=True)
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建当前会话目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_dir = self.workspace_dir / f"session_{timestamp}"
            self.current_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"运行时环境设置成功: {self.current_dir}")
        except Exception as e:
            self.logger.error(f"设置运行时环境失败: {str(e)}")
            raise

    async def connect(self) -> None:
        """连接到本地环境"""
        self.connected = True
        self.logger.info('Connected to local runtime')

    async def disconnect(self) -> None:
        """断开与本地环境的连接"""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.sleep(1)
                if self.process.poll() is None:
                    self.process.kill()
            except Exception as e:
                self.logger.error(f'Error terminating process: {e}')
        self.connected = False
        self.logger.info('Disconnected from local runtime')

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
        if not self.connected:
            raise RuntimeError('Not connected to runtime')

        if not await self.validate_action(action):
            raise ValueError(f'Invalid action: {action}')

        try:
            action_type = action['type']
            if action_type == 'write_code':
                from src.tools.write_code import WriteCodeTool
                tool = WriteCodeTool()
                result = await tool.execute(**action.get('params', {}))
                return result
            else:
                raise ValueError(f'Unknown action type: {action_type}')
        except Exception as e:
            raise e
            return await self.handle_error(e)

    async def get_status(self) -> Dict[str, Any]:
        """
        获取运行时状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            'connected': self.connected,
            'process_running': self.process is not None and self.process.poll() is None,
            'available_tools': self.available_tools
        }

    async def cleanup(self) -> None:
        """清理运行时环境"""
        await self.disconnect()
        # 清理临时文件等资源
        temp_dir = Path('temp')
        if temp_dir.exists():
            for file in temp_dir.glob('*'):
                try:
                    file.unlink()
                except Exception as e:
                    self.logger.error(f'Error cleaning up file {file}: {e}')

    async def validate_action(self, action: Dict[str, Any]) -> bool:
        """
        验证动作是否有效
        
        Args:
            action: 动作信息
            
        Returns:
            bool: 是否有效
        """
        if not isinstance(action, dict):
            return False
            
        action_type = action.get('type')
        if not action_type or action_type not in self.available_tools:
            return False
            
        params = action.get('params', {})
        if not isinstance(params, dict):
            return False
            
        return True

    async def get_available_tools(self) -> List[str]:
        """
        获取可用的工具列表
        
        Returns:
            List[str]: 工具列表
        """
        return self.available_tools

    async def get_resource_usage(self) -> Dict[str, Any]:
        """
        获取资源使用情况
        
        Returns:
            Dict[str, Any]: 资源使用信息
        """
        process = psutil.Process()
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'memory_info': process.memory_info()._asdict(),
            'disk_usage': psutil.disk_usage('/')._asdict()
        }

    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        处理错误
        
        Args:
            error: 错误信息
            
        Returns:
            Dict[str, Any]: 错误处理结果
        """
        self.logger.error(f'Error in local runtime: {str(error)}')
        import traceback
        error_stack = traceback.format_exc()
        self.logger.error(f'Error stack trace:\n{error_stack}')
        return {
            'status': 'error',
            'error': str(error),
            'error_type': type(error).__name__
        }

    