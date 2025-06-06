import os
from pathlib import Path
from typing import Optional

# 系统提示词
SYSTEM_PROMPT = """你是一个智能助手，可以帮助用户完成各种任务。
请根据用户的需求，使用提供的工具来完成任务。
如果遇到问题，请尝试不同的方法，直到任务完成。"""

# 工具提示词
TOOL_PROMPT = """请根据以下工具描述和任务需求，设置合适的参数：

工具描述：
{tool_schemas}

任务需求：
{task_description}

请以JSON格式返回参数设置，格式如下：
参数设置: {{"param1": "value1", "param2": "value2"}}"""

async def load_system_prompt(key: Optional[str] = None) -> str:
    """
    加载系统提示文件
    
    Args:
        key: 可选的提示键名，如果提供则只加载对应的提示文件
        
    Returns:
        str: 提示内容
    """
    prompt_dir = Path(__file__).parent
    
    if key:
        # 如果指定了key，只加载对应的文件
        file_path = prompt_dir / f"{key}.md"
        try:
            content = file_path.read_text(encoding='utf-8')
            print(f"Loaded specific prompt: {key} from {file_path}")
            return content
        except FileNotFoundError:
            print(f"Prompt file not found for key: {key} at {file_path}")
            return ""
        except Exception as e:
            print(f"Error reading prompt file for key {key} at {file_path}: {e}")
            return ""
    
    # 如果没有指定key，加载所有.md文件
    prompts = {}
    try:
        for item in prompt_dir.iterdir():
            if item.is_dir():
                # 递归加载子目录
                sub_prompts = await load_system_prompt()
                prompts.update(sub_prompts)
            elif item.is_file() and item.suffix == '.md':
                # 读取Markdown文件内容
                content = item.read_text(encoding='utf-8')
                prompt_name = item.stem  # 使用文件名（不含扩展名）作为键
                prompts[prompt_name] = content
                print(f"Loaded prompt: {prompt_name} from {item}")
    except Exception as e:
        print(f"Error loading prompts from {prompt_dir}: {e}")
    
    return prompts 