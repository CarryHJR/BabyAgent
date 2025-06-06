import asyncio
from typing import Dict, Any, Optional, Tuple
import os

from src.agent.code_act.thinking import thinking
from src.utils.resolve import resolve_actions
from src.utils.message import MessageFormatter
from src.agent.memory.local_memory import LocalMemory
from src.agent.reflection import reflection

MAX_RETRY_TIMES = 3
MAX_TOTAL_RETRIES = 10

async def delay(ms: int) -> None:
    """延迟执行"""
    await asyncio.sleep(ms / 1000)

def retry_handle(retry_count: int, total_retry_attempts: int, max_retries: int, max_total_retries: int, error_message: str = "") -> Tuple[bool, Dict[str, Any]]:
    """
    处理重试逻辑
    
    Args:
        retry_count: 当前连续重试次数
        total_retry_attempts: 当前总重试次数
        max_retries: 最大连续重试次数
        max_total_retries: 最大总重试次数
        error_message: 错误信息
        
    Returns:
        Tuple[bool, Dict[str, Any]]: (是否继续重试, 结果)
    """
    # 检查是否达到最大连续重试次数
    if retry_count >= max_retries:
        return False, {
            'status': 'failure',
            'comments': f'连续{"异常" if error_message else "执行失败"}达到最大次数({max_retries}){": " + error_message if error_message else ""}'
        }
    
    # 检查是否达到最大总重试次数
    if total_retry_attempts >= max_total_retries:
        return False, {
            'status': 'failure',
            'comments': f'达到最大总重试次数({max_total_retries}){": " + error_message if error_message else ""}'
        }
    
    # 可以继续重试
    return True, {}

async def finish_action(action: Dict[str, Any], context: Dict[str, Any], task_id: int) -> Dict[str, Any]:
    """
    处理任务完成动作
    
    Args:
        action: 动作信息
        context: 上下文信息
        task_id: 任务ID
        
    Returns:
        Dict[str, Any]: 执行结果
    """
    memory = context['memory']
    memorized_content = await memory.get_memorized_content()
    
    result = {
        'status': 'success',
        'comments': 'Task Success !',
        'content': action['params']['message'],
        'memorized': memorized_content,
        'meta': {
            'action_type': 'finish',
        },
        'timestamp': asyncio.get_event_loop().time() * 1000
    }
    
    msg = MessageFormatter.format({
        'status': 'success',
        'task_id': task_id,
        'action_type': 'finish',
        'content': result['content'],
        'comments': result['comments'],
        'memorized': result['memorized']
    })
    
    if context.get('on_token_stream'):
        context['on_token_stream'](msg)
    await MessageFormatter.save_to_db(msg, context['conversation_id'])
    
    return result

async def complete_code_act(task: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    执行代码行为直到任务完成或达到最大重试次数
    
    Args:
        task: 任务信息
        context: 上下文信息
        
    Returns:
        Dict[str, Any]: 任务执行结果
    """
    # 初始化参数和环境
    task = task or {}
    context = context or {} # 即使为{}也构建了dict
    requirement = task.get('description', '')
    task_id = task.get('id')
    max_retries = context.get('max_retry_times', MAX_RETRY_TIMES)
    max_total_retries = context.get('max_total_retries', MAX_TOTAL_RETRIES)
    
    memory = LocalMemory(options={'key': task_id})
    memory._load_memory()
    context['memory'] = memory
    
    retry_count = 0
    total_retry_attempts = 0

    # 主执行循环
    while True:
        try:
            # 1. LLM思考
            print("thinking.requirement", requirement)
            content = await thinking(requirement, context)
            print("thinking.结果\r\n", content)

            # 2. 解析动作
            actions = resolve_actions(content)
            action = actions[0] if actions else None
            print("action", action)

            
            # 3. 验证动作 - thinking结果不一定是符合期望的action xml格式 解析action失败就重试
            if not action:
                should_continue, result = retry_handle(retry_count, total_retry_attempts, max_retries, max_total_retries)
                if not should_continue:
                    return result
                await delay(500)
                retry_count += 1
                total_retry_attempts += 1
                context['retry_count'] = retry_count
                continue
            
            # 4. 如果thinking阶段判断task已经完成，则直接返回
            if action['type'] == 'finish':
                return await finish_action(action, context, task_id)
            
            # 5. 执行动作
            action_result = await context['runtime'].execute_action(action, context, task_id)
            print("action_result", action_result)
            if not context.get('generate_files'):
                context['generate_files'] = []
            if action_result.meta.get('filepath'):
                context['generate_files'].append(action_result.meta['filepath'])
            
            print("context['generate_files']", context['generate_files'])


            # 6. 反思和评估
            reflection_result = await reflection(requirement, action_result, context['conversation_id'])
            print("reflection_result", reflection_result)
            status = reflection_result['status']
            comments = reflection_result['comments']


            
            # 7. 处理执行结果
            if status == 'success':
                retry_count = 0  # 重置重试计数
                if action['type'] == task['tools'][0]:
                    finish_result = {'params': {'message': action_result.meta.get('content')}}
                    return await finish_action(finish_result, context, task_id)
                continue
            else:
                should_continue, result = retry_handle(retry_count, total_retry_attempts, max_retries, max_total_retries)
                if not should_continue:
                    return result
                retry_count += 1
                total_retry_attempts += 1
                context['reflection'] = comments
                print("code-act.memory logging user prompt")
                await memory.add_message("user", comments, action_type='reflection', memorized=True)
                await delay(500)
                print(f"Retrying ({retry_count}/{max_retries}). Total attempts: {total_retry_attempts}/{max_total_retries}...")
                
        except Exception as error:
            # 8. 异常处理
            print("An error occurred:", error)
            raise error
            should_continue, result = retry_handle(retry_count, total_retry_attempts, max_retries, max_total_retries, str(error))
            if not should_continue:
                return result
            retry_count += 1
            total_retry_attempts += 1
            print(f"Retrying ({retry_count}/{max_retries}). Total attempts: {total_retry_attempts}/{max_total_retries}...")
