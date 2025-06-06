from typing import List, Dict, Any
from pydantic import BaseModel
import json
from src.agent.prompt import resolve_planning_prompt
from src.agent.prompt.system import SYSTEM_PROMPT

class TaskStep(BaseModel):
    """任务步骤"""
    tool_name: str
    purpose: str
    parameters: Dict[str, Any] = {}

class TaskPlan(BaseModel):
    """任务计划"""
    steps: List[TaskStep]
    description: str

class TaskPlanner:
    """任务规划器"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def create_plan(self, user_input: str, tool_schemas: List[Dict]) -> TaskPlan:
        """创建任务计划"""
        # 准备提示词
        prompt = await resolve_planning_prompt(
            goal=user_input,
            files=[],
            previous_result='',
            conversation_id=None
        )
        print(f'Planning prompt: {prompt}')
        
        # 调用 LLM 生成计划
        response = await self.llm_client.chat.completions.create(
            model=self.llm_client.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        print(f'Planning response: {response}')
        
        # 解析计划
        plan_text = response.choices[0].message.content
        steps = self._parse_plan_steps(plan_text)
        
        return TaskPlan(
            steps=steps,
            description=user_input
        )
    
    def _parse_plan_steps(self, plan_text: str) -> List[TaskStep]:
        """解析计划步骤"""
        steps = []
        for line in plan_text.split("\n"):
            if not line.strip() or not line[0].isdigit():
                continue
            
            # 解析步骤
            try:
                # 格式：1. 步骤1：[工具名称] - [目的]
                parts = line.split(":", 1)[1].strip()
                tool_name, purpose = parts.split(" - ", 1)
                tool_name = tool_name.strip("[]")
                
                steps.append(TaskStep(
                    tool_name=tool_name,
                    purpose=purpose.strip()
                ))
            except Exception as e:
                print(f"解析步骤失败: {line}, 错误: {str(e)}")
                continue
        
        return steps 