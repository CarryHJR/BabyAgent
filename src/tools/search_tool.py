import aiohttp
from typing import Any, Dict
from .base_tool import BaseTool, ToolResult

class SearchTool(BaseTool):
    """网络搜索工具"""
    
    def __init__(self):
        super().__init__(
            name="search",
            description="用于网络搜索的工具"
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """执行搜索"""
        try:
            query = kwargs.get("query")
            if not query:
                return ToolResult(success=False, error="搜索关键词不能为空")
            
            # 使用 DuckDuckGo API 进行搜索
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": 1,
                        "skip_disambig": 1
                    }
                ) as response:
                    if response.status != 200:
                        return ToolResult(
                            success=False,
                            error=f"搜索请求失败: {response.status}"
                        )
                    
                    data = await response.json()
                    results = []
                    
                    # 提取搜索结果
                    if "Abstract" in data and data["Abstract"]:
                        results.append({
                            "title": "摘要",
                            "content": data["Abstract"]
                        })
                    
                    if "RelatedTopics" in data:
                        for topic in data["RelatedTopics"]:
                            if "Text" in topic:
                                results.append({
                                    "title": "相关主题",
                                    "content": topic["Text"]
                                })
                    
                    return ToolResult(success=True, data=results)
                    
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _get_parameters(self) -> Dict[str, Any]:
        """获取参数模式"""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词"
                }
            },
            "required": ["query"]
        } 