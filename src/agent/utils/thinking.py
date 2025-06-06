from typing import Tuple, Dict, Any

def resolve_thinking(content: str) -> Tuple[Dict[str, Any], str]:
    """
    解析思考内容
    
    Args:
        content: 思考内容
        
    Returns:
        Tuple[Dict[str, Any], str]: (思考信息, 实际内容)
    """
    # 提取思考信息
    thinking_info = {}
    
    # 匹配思考模式
    if content.startswith('<think>'):
        # 提取思考标签中的内容
        thinking_content = content[7:-8]  # 移除 <think> 和 </think>
        
        # 解析思考信息
        info_pattern = r'<info\s+name="([^"]+)"\s*>(.*?)</info>'
        import re
        matches = re.finditer(info_pattern, thinking_content, re.DOTALL)
        
        for match in matches:
            name = match.group(1)
            value = match.group(2).strip()
            thinking_info[name] = value
            
        # 提取实际内容
        content_pattern = r'<content>(.*?)</content>'
        content_match = re.search(content_pattern, thinking_content, re.DOTALL)
        if content_match:
            actual_content = content_match.group(1).strip()
        else:
            actual_content = thinking_content
            
        return thinking_info, actual_content
        
    return thinking_info, content 