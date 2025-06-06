from typing import Any, Dict
import asyncio
from .base_tool import BaseTool, ToolResult

class TerminalRun(BaseTool):
    """终端执行工具"""
    
    def __init__(self):
        super().__init__(
            name="terminal_run",
            description="Execute the specified command in the terminal and return the result. For reading .docx and .doc and .pdf and .xlsx files:\n\n- For .docx files, try using 'pandoc <file_path> -t plain' or 'antiword <file_path>'.\n- For .pdf files, try using 'pdftotext <file_path> -' to output the text to standard output.\n\nPrioritize using 'pandoc' if available due to its broader format support. If these tools are not available, try other suitable command-line tools for reading these file types."
        )
    
    def _get_parameters(self) -> Dict[str, Any]:
        """获取参数模式"""
        return {
            "type": "object",
            "properties": {
                "command": {
                    "description": "The shell command to execute.",
                    "type": "string"
                },
                "cwd": {
                    "description": "The working directory to execute the command.",
                    "type": "string"
                }
            },
            "required": ["command"]
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        try:
            command = kwargs.get("command")
            cwd = kwargs.get("cwd", ".")
            
            if not command:
                return ToolResult(
                    success=False,
                    error="Missing required parameter: command"
                )
            
            # 创建进程
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            # 等待进程完成
            stdout, stderr = await process.communicate()
            
            # 检查返回码
            if process.returncode == 0:
                return ToolResult(
                    success=True,
                    data={
                        "stdout": stdout.decode() if stdout else "",
                        "stderr": stderr.decode() if stderr else "",
                        "returncode": process.returncode
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"Command failed with return code {process.returncode}: {stderr.decode() if stderr else ''}"
                )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            ) 