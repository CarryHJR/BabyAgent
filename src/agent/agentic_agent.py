import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from openai import AsyncOpenAI

from src.agent.planning.planning import planning
from src.agent.code_act import complete_code_act
from src.agent.task_manager import TaskManager
from src.agent.prompt import auto_reply, generate_result
from src.utils.llm import call as call_llm
from src.utils.message import MessageFormatter
from src.models.file import File
from src.utils.planning import get_todo_md
from src.runtime import LocalRuntime
# from src.runtime.docker_runtime import DockerRuntime
from src.logger import get_logger
from .memory.conversation_memory import ConversationMemory
from src.agent.prompt.system import SYSTEM_PROMPT, TOOL_PROMPT
from src.tools import ToolManager

class AgenticAgent:
    """智能代理"""
    
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.memory = ConversationMemory(conversation_id=context.get('conversation_id', 'default'))
        self.tool_manager = ToolManager()
        self.llm_client = AsyncOpenAI(
            api_key=context['config'].OPENAI_API_KEY,
            base_url=context['config'].OPENAI_API_BASE
        )
        self.llm_client.model = context['config'].MODEL_NAME  # 设置模型名称
        self.logger = get_logger(__name__)
        self.task_manager = TaskManager(
            self.context.get('log_file', 'task_log.md'),
            self.context.get('conversation_id')
        )
        
        # 初始化运行时环境
        runtime_type = os.getenv('RUNTIME_TYPE', 'local')
        runtime_map = {
            'local': LocalRuntime,
            # 'docker': DockerRuntime
        }
        self.runtime = runtime_map[runtime_type]()
        
        # 设置上下文
        self.context.update({
            'runtime': self.runtime,
            'max_retry_times': 3,  # 与 CodeAct 保持一致
            'max_total_retries': 10  # 与 CodeAct 保持一致
        })
        
        self.on_token_stream = self.context.get('on_token_stream')
        self.is_stop = False
        
        self.logger.info('AgenticAgent initialized.')

    async def run(self, user_input: str) -> Dict[str, Any]:
        """运行代理"""
        try:
            # 1. 记录用户输入
            self.memory.add_message("user", user_input)
            
            # 2. 规划阶段
            await self.plan(user_input)
            if self.is_stop:
                self.logger.info('Agent stopped.')
                return {"status": "stopped"}
            
            # 3. 执行阶段
            self.logger.info('====== start execute ======')
            results = await self.execute()
            if self.is_stop:
                self.logger.info('Agent stopped.')
                return {"status": "stopped"}
            
            # 4. 生成总结 todo暂时不生成总结意义不大
            summary = "dummy summary"

            # 5. 返回最终结果
            return {
                "status": "success",
                "results": results,
                "summary": summary
            }
            
        except Exception as e:
            error_msg = f"代理执行失败: {str(e)}"
            self.logger.error(error_msg)
            self.memory.add_message("assistant", error_msg, {"error": str(e)})
            return {
                "status": "failed",
                "error": error_msg
            }
    
    def _parse_tool_parameters(self, params_text: str) -> Dict[str, Any]:
        """解析工具参数"""
        params = {}
        for line in params_text.split("\n"):
            if "参数设置" in line:
                try:
                    params_str = line.split(":", 1)[1].strip()
                    params = json.loads(params_str)
                except Exception as e:
                    print(f"解析参数失败: {line}, 错误: {str(e)}")
                    continue
        return params
    


    async def plan(self, goal: str) -> None:
        """任务规划阶段"""
        self.logger.info('Planning phase started.')
        try:
            # 1. 获取文件列表
            # files = await File.filter(conversation_id=self.context['conversation_id'])
            # todo: 暂时关闭文件列表
            files = []
            self.context['files'] = files
            
            # 2. 获取之前的执行结果
            # previous_result = await self.get_previous_result()
            # todo: 暂时关闭之前的执行结果
            previous_result = ''
            
            # 3. 生成任务计划
            planned_tasks = await planning(goal, files, previous_result, self.context['conversation_id']) or []
            
            # 4. 设置任务，添加必要的上下文信息
            for task in planned_tasks:
                task['conversation_id'] = self.context['conversation_id']
                task['on_token_stream'] = self.on_token_stream
                
            await self.task_manager.set_tasks(planned_tasks)
            
            # 5. 发送规划成功消息
            tasks = await self.task_manager.get_tasks()
            msg = MessageFormatter.format({
                'status': 'success',
                'action_type': "plan",
                'content': '',
                'json': tasks
            })
            self.on_token_stream(msg)
            await MessageFormatter.save_to_db(msg, self.context['conversation_id'])
            self.logger.info(f'Planning completed. {len(tasks)} tasks generated.')
            
            # 6. 生成并写入TODO文件
            dir_name = f"Conversation_{self.context['conversation_id'][:6]}"
            uuid_str = str(uuid.uuid4())
            
            # 发送TODO文件写入开始消息
            todo_running_msg = MessageFormatter.format({
                'content': "todo.md",
                'uuid': uuid_str,
                'status': 'running',
                'action_type': 'write_code'
            })
            self.on_token_stream(todo_running_msg)
            await MessageFormatter.save_to_db(todo_running_msg, self.context['conversation_id'])
            
            # 生成TODO内容并写入文件
            todo_md = await get_todo_md(tasks)
            todo_path = Path(dir_name) / "todo.md"
            todo_path.write_text(todo_md, encoding='utf-8')
            
            # 更新生成文件列表
            if not self.context.get('generate_files'):
                self.context['generate_files'] = []
            self.context['generate_files'].append(str(todo_path))
            
            # 发送TODO文件写入完成消息
            plan_msg = MessageFormatter.format({
                'uuid': uuid_str,
                'status': 'success',
                'memorized': '',
                'content': '',
                'action_type': 'write_code',
                'filepath': str(todo_path),
                'meta_content': todo_md
            })
            self.on_token_stream(plan_msg)
            await MessageFormatter.save_to_db(plan_msg, self.context['conversation_id'])
            
            return True
            
        except Exception as e:
            error_msg = f'Planning failed: {str(e)}'
            self.logger.error(error_msg)
            raise Exception(error_msg)

    async def execute(self) -> List[Dict]:
        """执行任务"""
        self.logger.info('Execution phase started.')
        results = []
        
        try:
            # 获取任务列表
            tasks = await self.task_manager.get_tasks()
            
            if not tasks:
                self.logger.info('No tasks to execute.')
                return results
            
            # 执行每个任务
            for task in tasks:
                if self.is_stop:
                    self.logger.info('Agent stopped.')
                    return results
                    
                # 更新任务状态为运行中
                await self.task_manager.update_task_status(task['id'], 'running')
                self.logger.info(f"Executing task {task['id']}: {task['requirement']}")
                
                # 发送任务开始消息
                msg = MessageFormatter.format({
                    'status': 'running',
                    'task_id': task['id'],
                    'action_type': 'task'
                })
                self.on_token_stream(msg)
                await MessageFormatter.save_to_db(msg, self.context['conversation_id'])
                
                try:
                    # 使用 CodeAct 执行任务
                    result = await complete_code_act(task, self.context)
                    
                    # 更新任务状态为完成
                    await self.task_manager.update_task_status(
                        task['id'], 
                        'completed',
                        {'result': result.get('content'), 'memorized': result.get('memorized', '')}
                    )
                    
                    # 更新上下文中的任务列表
                    self.context['tasks'] = await self.task_manager.get_tasks()
                    
                    # 更新 TODO 文件
                    new_tasks = await self.task_manager.get_tasks()
                    todo_md = await get_todo_md(new_tasks)
                    dir_name = f"Conversation_{self.context['conversation_id'][:6]}"
                    
                    # 发送 TODO 更新消息
                    todo_msg = MessageFormatter.format({
                        'content': "todo.md",
                        'uuid': str(uuid.uuid4()),
                        'status': 'running',
                        'task_id': task['id'],
                        'action_type': 'write_code'
                    })
                    self.on_token_stream(todo_msg)
                    await MessageFormatter.save_to_db(todo_msg, self.context['conversation_id'])
                    
                    # 写入 TODO 文件
                    todo_path = Path(dir_name) / "todo.md"
                    todo_path.write_text(todo_md, encoding='utf-8')
                    
                    # 发送任务完成消息
                    success_msg = MessageFormatter.format({
                        'status': 'success',
                        'task_id': task['id'],
                        'action_type': 'task',
                        'json': result
                    })
                    self.on_token_stream(success_msg)
                    await MessageFormatter.save_to_db(success_msg, self.context['conversation_id'])
                    
                    results.append(result)
                    
                except Exception as e:
                    # 更新任务状态为失败
                    await self.task_manager.update_task_status(
                        task['id'],
                        'failed',
                        {'error': str(e)}
                    )
                    self.logger.error(f"Task {task['id']} failed: {str(e)}")
                    
                    # 发送任务失败消息
                    failure_msg = MessageFormatter.format({
                        'status': 'failure',
                        'task_id': task['id'],
                        'action_type': 'task',
                        'json': str(e)
                    })
                    self.on_token_stream(failure_msg)
                    await MessageFormatter.save_to_db(failure_msg, self.context['conversation_id'])
                    
                    # 如果任务失败，停止执行
                    break
                
            self.logger.info('All tasks processed.')
            return results
                
        except Exception as e:
            self.logger.error(f'Execution failed: {str(e)}')
            raise

    async def stop(self) -> None:
        """停止执行"""
        self.is_stop = True
        self.logger.info('Execution stopped by user.')


    # async def _get_all_files(self, dir_path: Path) -> List[Dict[str, Any]]:
    #     """获取目录下所有文件"""
    #     files = []
    #     for file_path in dir_path.rglob("*"):
    #         if file_path.is_file():
    #             files.append({
    #                 "path": str(file_path.relative_to(dir_path)),
    #                 "content": file_path.read_text(encoding='utf-8')
    #             })
    #     return files

    # async def _generate_todo_file(self, tasks: List[Dict], dir_name: str) -> None:
    #     """生成TODO文件"""
    #     todo_content = get_todo_md(tasks)
    #     todo_path = Path(dir_name) / "TODO.md"
    #     todo_path.write_text(todo_content, encoding='utf-8') 