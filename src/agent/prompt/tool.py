from typing import List, Dict, Any
from src.tools.tool_manager import ToolManager

async def resolve_tool_prompt() -> str:
    """
    生成工具列表的提示模板
    
    Returns:
        str: 工具列表的提示模板
    """
    tool_description = ""
    
    # 
    tool_schemas = ToolManager().get_tool_schemas()
    for tool in tool_schemas:
        # 格式化工具定义为JSON字符串
        tool_definition = {
            "description": tool['description'],
            "name": tool['name'],
            "params": tool['parameters']
        }
        
        # 添加工具定义到提示中
        tool_description += f"""<tool {tool['name']}>
{str(tool_definition)}
</tool>
"""
    
    # 使用模板字符串构建工具提示
    prompt = f"""<tools>
<tool_list>
You are provided with tools to complete user's task and proposal. Here is a list of tools you can use:
{tool_description}
</tool_list>

<tool_call_guidelines>
Follow these guidelines regarding tool calls
- The conversation history, or tool_call history may refer to tools that are no longer available. NEVER call tools that are not explicitly provided.
- You MUST only use the tools explicitly provided in the tool list. Do not treat file names or code functions as tool names. The available tool names:
- {chr(10).join(f'  - {schema["name"]}' for schema in tool_schemas)}
</tool_call_guidelines>

</tools>"""

    return prompt 