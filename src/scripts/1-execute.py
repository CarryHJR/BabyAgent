# 添加项目根目录到Python路径
import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))


import asyncio
files = []
previous_result = ''
conversation_id = '20250604150000'

import json
import uuid
from pathlib import Path


# 创建conversation_id对应的文件夹
task_dir = Path(f'tasks/{conversation_id}')
tasks = json.load(open(task_dir / 'todo.json', 'r', encoding='utf-8'))
import pprint   
pprint.pprint(tasks)

from src.runtime import LocalRuntime

runtime = LocalRuntime()
asyncio.run(runtime.setup())
asyncio.run(runtime.connect())

context = {
    'conversation_id': conversation_id,
    'runtime': runtime,
    'log_file': 'task_log.md'  # 添加日志文件配置
}



from src.agent.code_act import complete_code_act
for task in tasks[:]:
    # 执行任务
    result = asyncio.run(complete_code_act(task, context))
    # 更新任务状态
    task['status'] = 'done'
    task['result'] = result
    # 保存任务状态
    with open(task_dir / 'todo.json', 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)