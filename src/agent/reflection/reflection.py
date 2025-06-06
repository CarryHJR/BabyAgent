from typing import Dict, Any

async def reflection(requirement: str, action_result: Dict[str, Any], conversation_id: str) -> Dict[str, str]:
    """
    反思执行结果并决定下一步行动
    
    Args:
        requirement: 任务要求
        action_result: 执行结果
        conversation_id: 对话ID
        
    Returns:
        Dict[str, str]: 包含状态和评论的字典
    """
    status = action_result.status
    if status == 'success':
        return {
            "status": "success",
            "comments": action_result.meta.get('content')
        }
    else:
        return {
            "status": "failure",
            "comments": action_result.error
        }
    
    # 调用LLM进行反思
    # reflection_result = await call(prompt, conversation_id)
    


def resolve_evaluation_prompt(requirement: str, result: str) -> str:
    return f"""Please act as a professional review expert, fully understand the user's requirements and expected results, compare and analyze the execution results, evaluate whether the execution results meet the user's requirements
1. If the execution result fully meets the expected result, return success
2. If the execution result cannot be directly delivered, return failure, and return feedback, missing content, and suggestions for optimization
3. If the execution result partially meets or fails to execute the key steps, return partial, and return suggestions for补充遗漏内容

=== Task Goal ===
{requirement}
=== END ===

=== Code Execution Result ===
{result}
=== END ===

=== Return Format === 
<evaluation>
<status>success/failure/partial</status>
<comments>
// evaluation result
</comments>
</evaluation>

Start:""" 