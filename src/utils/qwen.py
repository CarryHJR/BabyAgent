from typing import Dict, Any, List, Optional
import os
import json
import aiohttp
import requests
from src.config import Settings
from src.logger import get_logger
from .llm import LLMError

settings = Settings()
logger = get_logger(__name__)

async def call_qwen(
    prompt: str,
    conversation_id: str,
    model: str = None,
    options: Dict[str, Any] = None
) -> str:
    """
    调用Qwen API
    
    Args:
        prompt: 提示词
        conversation_id: 对话ID
        model: 模型名称
        options: 其他选项
        
    Returns:
        str: Qwen响应
        
    Raises:
        LLMError: Qwen API调用错误
    """
    try:
        # 获取配置
        api_key = settings.qwen_api_key
        api_base = settings.qwen_api_base
        model = model or settings.qwen_default_model
        
        # 构建请求头
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 构建请求体
        data = {
            'model': model,
            'input': {
                'messages': [
                    {'role': 'system', 'content': prompt}
                ]
            }
        }
        
        # 添加历史消息
        if options and 'messages' in options:
            data['input']['messages'].extend(options['messages'])
            
        # 添加其他选项
        if options:
            for key, value in options.items():
                if key != 'messages':
                    data[key] = value
                    
        # 记录请求
        logger.info(f'Qwen request: model={model}, conversation_id={conversation_id}')
        logger.debug(f'Qwen request data: {json.dumps(data, ensure_ascii=False)}')
                    
        # 发送请求
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{api_base}/v1/services/aigc/text-generation/generation',
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    logger.error(f'Qwen API error: {error}')
                    raise LLMError(f'Qwen API error: {error}')
                    
                result = await response.json()
                content = result['output']['text']
                
                # 记录响应
                logger.info(f'Qwen response: conversation_id={conversation_id}')
                logger.debug(f'Qwen response content: {content}')
                
                return content
                
    except aiohttp.ClientError as e:
        logger.error(f'Qwen request error: {str(e)}')
        raise LLMError(f'Qwen request error: {str(e)}')
    except Exception as e:
        logger.error(f'Qwen unexpected error: {str(e)}')
        raise LLMError(f'Qwen unexpected error: {str(e)}') 