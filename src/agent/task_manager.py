from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import os

class TaskManager:
    def __init__(self, log_file: str, conversation_id: str):
        """
        初始化任务管理器
        
        Args:
            log_file: 日志文件名
            conversation_id: 对话ID
        """
        self.log_file = log_file
        self.conversation_id = conversation_id
        self.tasks = []
        self._load_tasks()

    def _load_tasks(self) -> None:
        """从日志文件加载任务"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []

    def _save_tasks(self) -> None:
        """保存任务到日志文件"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    async def set_tasks(self, tasks: List[Dict[str, Any]]) -> None:
        """
        设置任务列表
        
        Args:
            tasks: 任务列表
        """
        self.tasks = tasks
        self._save_tasks()

    def get_tasks(self) -> List[Dict[str, Any]]:
        """
        获取任务列表
        
        Returns:
            List[Dict[str, Any]]: 任务列表
        """
        return self.tasks

    def update_task_status(self, task_id: int, status: str, result: Optional[Dict[str, Any]] = None) -> None:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 任务状态
            result: 任务结果
        """
        for task in self.tasks:
            if task.get('id') == task_id:
                task['status'] = status
                if result:
                    task['result'] = result
                break
        self._save_tasks()

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[Dict[str, Any]]: 任务信息
        """
        for task in self.tasks:
            if task.get('id') == task_id:
                return task
        return None

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """
        获取下一个待执行的任务
        
        Returns:
            Optional[Dict[str, Any]]: 下一个任务
        """
        for task in self.tasks:
            if task.get('status') == 'pending':
                return task
        return None

    def is_all_tasks_completed(self) -> bool:
        """
        检查是否所有任务都已完成
        
        Returns:
            bool: 是否所有任务都已完成
        """
        return all(task.get('status') == 'completed' for task in self.tasks)

    def get_task_progress(self) -> Dict[str, Any]:
        """
        获取任务进度
        
        Returns:
            Dict[str, Any]: 任务进度信息
        """
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.get('status') == 'completed')
        failed = sum(1 for task in self.tasks if task.get('status') == 'failed')
        pending = total - completed - failed

        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'progress': (completed / total * 100) if total > 0 else 0
        } 