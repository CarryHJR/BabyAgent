from typing import Dict, List, Type, Any
from .base_tool import BaseTool
from .search_tool import SearchTool
from .write_code import WriteCodeTool
from .terminal_run import TerminalRun

class ToolManager:
    """工具管理器"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        default_tools = [
            SearchTool(),
            WriteCodeTool(),
            TerminalRun()
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: BaseTool):
        """注册工具"""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> BaseTool:
        """获取工具"""
        if name not in self._tools:
            raise ValueError(f"工具不存在: {name}")
        return self._tools[name]
    
    def get_all_tools(self) -> List[BaseTool]:
        """获取所有工具"""
        return list(self._tools.values())
    
    def get_tool_schemas(self) -> List[Dict]:
        """获取所有工具的模式"""
        return [tool.get_schema() for tool in self._tools.values()]

    def get_tools(self) -> Dict[str, BaseTool]:
        """获取所有工具"""
        return {tool.name: tool.get_schema() for tool in self._tools.values()}