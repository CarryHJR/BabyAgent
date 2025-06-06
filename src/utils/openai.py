from typing import Dict, Any, Optional
import os
import json
from openai import AsyncOpenAI
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
        
        # 创建客户端
        client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_API_BASE
        )
        
        # 准备消息
        messages = [
            {"role": "system", "content": "你是一个智能助手，可以帮助用户完成各种任务。"},
            {"role": role, "content": prompt}
        ]
        
        # 准备参数
        params = {
            "model": config.MODEL_NAME,
            "messages": messages,
            "temperature": config.MODEL_TEMPERATURE,
            "max_tokens": config.MODEL_MAX_TOKENS
        }
        
        # 添加选项
        if options:
            params.update(options)
        
        # 调用API
        response = await client.chat.completions.create(**params)
        
        # 返回结果
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"调用LLM失败: {str(e)}")
        raise 