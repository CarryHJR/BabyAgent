from typing import Any, Dict
import os
from .base_tool import BaseTool, ToolResult
from pathlib import Path
from src.config import get_workspace_dir

class WriteCodeTool(BaseTool):
    """写入代码工具"""
    
    def __init__(self):
        super().__init__(
            name="write_code",
            description="Write the code content to the specified file path."
        )
    
    def _get_parameters(self) -> Dict[str, Any]:
        """获取参数模式"""
        return {
            "type": "object",
            "properties": {
                "path": {
                    "description": "The path of the file to write.",
                    "type": "string"
                },
                "content": {
                    "description": "The code content to write.",
                    "type": "string"
                }
            },
            "required": ["path", "content"]
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        try:
            relative_path = kwargs.get("path")
            content = kwargs.get("content")

            print("write_code", relative_path)
            # 获取工作目录
            workspace_dir = get_workspace_dir()
            # conversation_dir = workspace_dir / f"Conversation_{self.context['conversation_id'][:6]}"
            
            # 转换为绝对路径
            absolute_path = workspace_dir / relative_path

            print("write_code", absolute_path)
            
            # 确保目录存在
            absolute_path.parent.mkdir(parents=True, exist_ok=True)


            
            # 写入文件
            absolute_path.write_text(content, encoding='utf-8')

            
            return ToolResult(
                status='success',
                meta={
                    "path": str(relative_path),  # 返回相对路径
                    "filepath": str(absolute_path),
                    "content": content
                }
            )
            
        except Exception as e:
            return ToolResult(
                status='failure',
                error=str(e)
            ) 