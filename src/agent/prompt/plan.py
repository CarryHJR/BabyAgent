from typing import List, Dict, Any, Optional
import os
from datetime import datetime
from src.utils.llm import call
from src.models import Experience
from .tool import resolve_tool_prompt
USE_EXPERIENCE = os.getenv('USE_EXPERIENCE', 'TRUE')

async def resolve_planning_prompt(
    goal: str,
    files: List[Dict[str, Any]] = None,
    previous_result: str = '',
    conversation_id: str = None
) -> str:
    """
    生成规划提示词
    
    Args:
        goal: 目标
        files: 文件列表
        previous_result: 之前的执行结果
        conversation_id: 对话ID
        
    Returns:
        str: 规划提示词
    """
    if files is None:
        files = []
        
    # 构建文件字符串
    file_str = '\n'.join(f'upload/{file["name"]}' for file in files)
    
    # 获取工具提示词
    tool_prompt = await resolve_tool_prompt()

    # 获取经验提示词 todo: 暂时关闭经验提示词
    # experience_prompt = await resolve_experience_prompt(goal, conversation_id)
    experience_prompt = ''
    
    # 构建规划提示词
    planning_prompt = f"""Please act as a task planning expert, analyze the <task goal> from a professional perspective, based on the existing tool capabilities, provide a step-by-step task plan to ensure the goal is achieved, return json array format
**Important Note:** The 'title' and 'description' fields within the JSON output MUST be in the same language as the <task goal>.

==== Current System Environment ===
- Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
====

=== Format Description ===
{{
  "type": "object",
  "properties": {{
    "title": {{
      "type": "string",
      "description": "Task title"
    }},
    "description": {{
      "type": "string",
      "description": "task desc should be specific, operable, and have clear completion criteria"
    }},
    "tools": {{
      "type": "array",
      "description": "List of tools required for the task",
      "minItems": 1,
      "items": {{
        "type": "string",
        "description": "Tool name"
      }}
    }}
  }},
  "required": [
    "title",
    "description",
    "tools"
  ]
}}
=== END ===

=== Core Ideas ===
1. Ability awareness: Only add tasks that can be completed using available tools and capabilities
2. Task planning: First complete the acquisition of prerequisites (files, search content, etc.) based on task requirements, then complete the task goal based on relevant knowledge
3. File search: Please first use the file search tool to determine the file to depend on, then use the file read tool to read the file content
4. When need write code, please describe the requirements for code writing in one go, do not describe and implement separately
=== END ===

{experience_prompt}

{tool_prompt}

--- Task Decomposition Example ---
When a broader objective within the <task goal> implies researching or performing actions on *multiple distinct entities or items* (as exemplified in the "Planning Detail Reference"), each of these specific entities/items should form its *own separate JSON object* within the main array.

For instance, if the Task Goal implies "Research major landmarks including LandmarkA, LandmarkB, and LandmarkC," the output should be structured as follows, with *each specific landmark* becoming an individual task:

[
  {{
    "title": "Research LandmarkA Details",
    "description": "Use web search tool to find open hours, ticket prices, and other relevant information for LandmarkA.",
    "tools": ["web_search"]
  }},
  {{
    "title": "Research LandmarkB Details",
    "description": "Use web search tool to find open hours, ticket prices, and other relevant information for LandmarkB.",
    "tools": ["web_search"]
  }}
]
This explicit example clarifies that each distinct entity/item that requires specific action becomes an individual task in the JSON array, rather than being grouped together or listed as bullet points within a single task's description.

=== Previous Execution Result ===
{previous_result}
=== END ===

=== Task Goal ===
{goal}

=== Uploaded files that can be used ===
{file_str}

=== END ===

=== Best Practice ===
0. If there is an uploaded file, please read the file first to understand the file content and the result of the file (xlsx)
1. Find|Search for relevant information (if necessary, use the web_search tool). If there is a file that needs to be analyzed and processed, please use read_file/code to read the file content first, make sure you understand the requirements, and then proceed to the next step
2. Understand|Analyze the information required for the final code and write it into the markdown file
3. The final code uses the write_code tool to create an html/markdown file to generate a web page or report (completed in one go), do not implement it step by step
--- The web page code should be generated in one file at a time. HTML/js/css should be used to complete the task in as complete and minimal steps as possible. Do not implement it in batches to affect the speed. Please clearly describe the detailed requirements of write_code for the final task to avoid deviations from the original requirements during execution ---
=== END ===
Start analyzing and planning with required format strictly:"""

    return planning_prompt

async def resolve_experience_prompt(goal: str, conversation_id: str) -> str:
    """
    生成经验提示词
    
    Args:
        goal: 目标
        conversation_id: 对话ID
        
    Returns:
        str: 经验提示词
    """
    if USE_EXPERIENCE != 'TRUE':
        return ''
        
    experience = await get_experience(goal, conversation_id)
    experience_goal = experience.get('goal')
    experience_todo = experience.get('content')
    
    if not experience_goal:
        return ''
        
    return f"""--- Planning Detail Reference (Content Only, Format Unaffected) ---
As a task planning expert, when generating the task plan, please refer to the following checklist for guidance on breaking down high-level tasks into smaller, more specific, and atomic actionable sub-tasks. Each bullet point in this example represents a distinct and actionable step. This example serves to inform the quality and granularity of your planning, not the output format. Your final output MUST strictly adhere to the JSON format described above.
Reference Goal Example: {experience_goal}

Example Planning Content (for Quality Reference):

{experience_todo}
---"""

async def get_experience(goal: str, conversation_id: str) -> Dict[str, Any]:
    """
    获取相似任务的经验
    
    Args:
        goal: 目标
        conversation_id: 对话ID
        
    Returns:
        Dict[str, Any]: 相似任务的经验
    """
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
    result = await call(
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