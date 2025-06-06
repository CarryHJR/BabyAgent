from typing import Dict, Any, Optional
import os
import json
import aiohttp
from src.config import get_config
from src.logger import get_logger

logger = get_logger(__name__)

class LLMError(Exception):
    """LLM调用错误"""
    pass

async def call(
    prompt: str,
    conversation_id: str,
    role: str = "user",
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    调用LLM
    
    Args:
        prompt: 提示词
        conversation_id: 对话ID
        role: 角色
        options: 选项
        
    Returns:
        str: 响应内容
    """
    try:
        # 获取配置
        config = get_config()
        
        # 构建请求头
        headers = {
            'Authorization': f'Bearer {config.OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # 准备消息
        messages = options.get('messages', []) if options else []
        if prompt:
            messages.append({"role": role, "content": prompt})
        
        # 构建请求体
        data = {
            "model": config.MODEL_NAME,
            "messages": messages,
            "temperature": config.MODEL_TEMPERATURE,
            "max_tokens": config.MODEL_MAX_TOKENS
        }
        
        # 记录请求
        # logger.info(f'OpenAI request: model={config.MODEL_NAME}, conversation_id={conversation_id}')
        # logger.debug(f'OpenAI request data: {json.dumps(data, ensure_ascii=False)}')
        
        # 发送请求
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{config.OPENAI_API_BASE}/chat/completions',
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    logger.error(f'OpenAI API error: {error}')
                    raise LLMError(f'OpenAI API error: {error}')
                    
                result = await response.json()
                return result['choices'][0]['message']['content']
                
    except Exception as e:
        logger.error(f"调用LLM失败: {str(e)}")
        raise LLMError(f"调用LLM失败: {str(e)}")
    


import asyncio
import pathlib
if __name__ == "__main__":
    prompt_path = pathlib.Path(f"prompt.txt")
    prompt = prompt_path.read_text(encoding='utf-8')


    # print(asyncio.run(call(prompt, "123")))

    prompt = """
You are a helpful AI assistant named Lemon. Your task is to think through the problem and plan your actions carefully before executing them.

=== THINKING PROCESS ===
1. Analyze the current goal and context
2. Consider potential approaches and their implications
3. Identify potential challenges and risks
4. Plan the sequence of actions needed
5. Evaluate the feasibility of the plan

=== CONTEXT ===
Goal: 使用Python编写代码以可视化YOLO格式的标注文件。代码应读取标注文件和对应的图片，并在图片上绘制标注框和类别名称。

=== INSTRUCTIONS ===
Please think through the following aspects:
1. What is the core problem we need to solve?
2. What are the key constraints and requirements?
3. What tools and resources do we have available?
4. What could go wrong and how can we prevent it?
5. What is the most efficient sequence of actions?

Provide your analysis in a structured format, focusing on:
- Problem Analysis
- Approach Selection
- Risk Assessment
- Action Plan
- Success Criteria

Remember to:
- Think step by step
- Consider edge cases
- Plan for error handling
- Optimize for efficiency
- Maintain code quality

Please provide your detailed thinking process below:
"""

    print(asyncio.run(call(prompt, "123", 'assistant',
            {
                # 'response_format': 'json',
                # 'temperature': 0
            }
        )))