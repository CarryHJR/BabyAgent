from typing import List, Dict, Any
import xml.etree.ElementTree as ET

def resolve_xml(content: str) -> Dict[str, Any]:
    """
    解析XML内容为字典格式
    
    Args:
        content: XML格式的字符串内容
        
    Returns:
        Dict[str, Any]: 工具名称和参数的字典
    """
    try:
        root = ET.fromstring(content.strip())
        result = {}
        
        # 获取工具名称作为key
        tool_name = root.tag
        
        # 获取所有子元素作为参数
        params = {}
        for child in root:
            params[child.tag] = child.text.strip() if child.text else ""
            
        result[tool_name] = params
        return result
        
    except Exception as e:
        print(f"解析XML错误: {e}")
        return {}

def resolve_actions(content: str) -> List[Dict[str, Any]]:
    """
    解析动作列表
    
    Args:
        content: 内容
        
    Returns:
        List[Dict[str, Any]]: 动作列表
    """
    try:
        resolved = resolve_xml(content)
        actions = []
        
        for action_type, params in resolved.items():
            actions.append({
                'type': action_type,
                'params': params
            })
            
        return actions
    except Exception as e:
        print(f"解析动作错误: {e}")
        return [] 
    



if __name__ == "__main__":
    content = '''
    <write_code>
    <path>test.py</path>
    <content>
    print("hello world")
    </content>
    </write_code>
    '''
    print(resolve_actions(content))