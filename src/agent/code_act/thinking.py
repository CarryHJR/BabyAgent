from typing import Dict, Any, Optional, List
from ..prompt import resolve_think_prompt
from src.utils.llm import call
from ..memory import LocalMemory


async def thinking(requirement: str, context: Dict[str, Any]) -> str:
    """
    执行思考过程
    
    Args:
        requirement: 任务要求
        context: 上下文信息
        
    Returns:
        str: 思考结果
    """
    # 初始化记忆

    memory = context.get('memory')
    if not memory:
        memory = LocalMemory(options={'key': context.get('conversation_id', 'default')})
        context['memory'] = memory
        
    # 获取消息历史
    messages = await memory.get_messages(summarize=False)
    # print("current history messages", messages)
    
    # 如果最后一条消息是助手的回复，直接返回
    for msg in messages:
        print("role", msg['role'])

    if messages and messages[-1]['role'] == 'assistant':
        return messages[-1]['content']
        
    # 生成思考提示
    if len(messages) == 0:
        prompt = await resolve_think_prompt(requirement, context)
        print(prompt)
    else:
        prompt = ''
    # 对话记录
    options = {
        'messages': [
            {'role': msg['role'], 'content': msg['content']}
            for msg in messages
        ]
    }
    
    content = await call(prompt, context.get('conversation_id'), role='assistant', options=options)
    
    # 保存思考结果
    if prompt:
        await memory.add_message('user', prompt, action_type='thinking', memorized=True)
    await memory.add_message('assistant', content, action_type='thinking', memorized=True)
    
    # todo: 暂时不处理think字段
    # 如果思考结果以<think>开头，提取实际内容
    # if content and content.startswith('<think>'):
    #     from src.utils.thinking import resolve_thinking
    #     _, output = resolve_thinking(content)
    #     return output
        
    return content 


