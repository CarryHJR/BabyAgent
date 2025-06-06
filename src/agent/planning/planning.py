from typing import List, Dict, Any, Optional
import os
from datetime import datetime

from src.agent.prompt import resolve_planning_prompt
from src.logger import get_logger
from src.utils.llm import call as call_llm
from src.models import File, Experience

logger = get_logger(__name__)


async def planning(goal: str, files: List[File], previous_result: Dict[str, Any], conversation_id: str) -> List[Dict[str, Any]]:
    """
    规划任务执行
    
    Args:
        goal: 目标
        files: 相关文件列表
        previous_result: 之前的执行结果
        conversation_id: 对话ID
        
    Returns:
        List[Dict[str, Any]]: 任务列表
    """
    try:
        # 准备提示词
        prompt = await resolve_planning_prompt(
            goal=goal,
            files=files,
            previous_result=previous_result,
            conversation_id=conversation_id
        )
        print(f'Planning prompt: {prompt}')
        logger.info("\n==== planning prompt ====")
        logger.info(prompt)

        # 保存prompt到文件
        import pathlib
        prompt_path = pathlib.Path(f"prompt.txt")
        prompt_path.write_text(prompt, encoding='utf-8')
        
        # 调用LLM进行规划
        result = await call_llm(
            prompt, 
            conversation_id, 
            'assistant',
            {
                # 'response_format': 'json',
                # todo: 暂时关闭response_format 改用手动解析
                'temperature': 0
            }
        )
        
        logger.info("\n==== planning result ====")
        logger.info(result)

        # 解析JSON结果
        import json
        try:
            # 尝试直接解析JSON
            tasks = json.loads(result)
        except json.JSONDecodeError:
            # 如果直接解析失败,尝试提取JSON部分
            import re
            json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
            if json_match:
                tasks = json.loads(json_match.group(1))
            else:
                # 如果还是失败,尝试提取数组部分
                array_match = re.search(r'\[(.*?)\]', result, re.DOTALL)
                if array_match:
                    tasks = json.loads(f"[{array_match.group(1)}]")
                else:
                    raise Exception("无法解析规划结果")
        
        # 确保tasks是列表
        if not isinstance(tasks, list):
            tasks = [tasks]
            
        # 过滤有效任务
        tasks = [task for task in tasks if task.get('tools') and len(task['tools']) > 0]
        
        return tasks
    except Exception as e:
        logger.error(f'规划任务失败: {str(e)}')
        raise

    """
    获取相似任务的经验
    
    Args:
        goal: 用户目标
        conversation_id: 对话ID
        
    Returns:
        Dict[str, Any]: 相似任务的经验
    """
    if os.getenv('USE_EXPERIENCE', 'TRUE') != 'TRUE':
        return {'goal': None, 'content': None}
        
    # 获取所有启用的经验
    experiences = await Experience.filter(is_enabled=True)
    experience_list = [
        {
            'id': exp.id,
            'title': exp.title,
            'goal': exp.goal
        }
        for exp in experiences
    ]
    
    # 构建相似度分析提示词
    prompt = f"""You are a semantic similarity analyzer. Your core task is to accurately identify the single most semantically similar historical goal from the provided list of goal_examples based on the given target_goal.

Here is the current target_goal you need to evaluate:
{goal}

And here are the goal_examples (a JSON array of objects, where each object has an id and a goal field) from which you must find the closest match:
{experience_list}

Processing Logic: 1. Understand Goal Semantics: Thoroughly analyze and deeply understand the semantic meaning, intent, and core requirements of the target_goal. 2. Semantic Similarity Comparison: Perform a precise semantic similarity comparison between the target_goal's meaning and the goal field of each historical goal object within the goal_examples array. 3. Select Closest Match: Identify the single historical goal object that is most semantically similar (or closest) to the target_goal. 4. Single Result Principle: Even if multiple historical goals appear very similar, you must select and return only one historical goal's id that you determine to be the absolute closest.

Output Requirements: You must and shall return only one JSON object. This JSON object must contain only the id field of the closest goal-example found. Strictly do not return any additional text, explanations, preambles, postscripts, or formatting (other than the JSON object itself).

Output Format Example: {{"id": "id_of_the_closest_goal_example"}}
"""
    
    # 调用LLM进行相似度分析
    result = await call_llm(
        prompt,
        conversation_id,
        'assistant',
        {
            'response_format': 'json',
            'temperature': 0
        }
    )
    
    # 获取最相似的经验
    experience = await Experience.get(id=result['id'])
    return experience 