from typing import List, Dict, Any
from src.logger import get_logger

logger = get_logger(__name__)

def get_todo_md(tasks: List[Dict[str, Any]]) -> str:
    """将任务列表转换为Markdown格式的TODO列表"""
    markdown = "## TODO List\n"
    for task in tasks:
        checkbox = "[ ]" if task.get('status') == "pending" else "[x]"
        markdown += f"- {checkbox} {task['requirement']}\n"
    return markdown 