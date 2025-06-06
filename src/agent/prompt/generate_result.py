from typing import List, Dict, Any

def resolve_result_prompt(goal: str, tasks: List[Dict[str, Any]]) -> str:
    """
    生成结果生成提示
    
    Args:
        goal: 目标
        tasks: 任务列表
        
    Returns:
        str: 结果生成提示
    """
    new_tasks = [
        {
            "title": task["title"],
            "description": task["description"],
            "status": task["status"],
            "result": task["result"]
        }
        for task in tasks
    ]
    
    prompt = f"""
You are a helpful AI assistant named Lemon. Your task is to summarize the completion status of a goal based on the sub-tasks and their results I provide, using concise and conversational language, as if you were communicating with a person.

I will provide you with:
1. The overall goal.
2. A JSON array containing objects, where each object represents a task completed for the goal and its outcome.

Please analyze the goal and the results of the sub-tasks in the JSON array, and then tell me how well the overall goal has been achieved. 
**Crucially, please detect the language of the 'goal' you receive and ensure your entire summary is provided in that same language.**
Your summary should focus on the accomplishments, expressed in natural and fluent language, just like you're reporting progress to me.

Please wait for me to provide the goal and the task information.
  
  goal:{goal}
  tasks: {str(new_tasks)}
  """
    
    return prompt 