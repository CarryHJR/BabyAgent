# 添加项目根目录到Python路径
import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))


from src.agent.planning.planning import planning


goal = """
请帮我生成一篇关于轻量语义分割网络的文献综述。要求如下：

1. 综述范围：
   - 重点关注2018年至今的轻量语义分割网络研究进展
   - 包括但不限于：MobileNet、ShuffleNet、EfficientNet等轻量级骨干网络
   - 关注网络压缩、知识蒸馏、量化等技术在语义分割中的应用

2. 内容要求：
   - 分析不同轻量语义分割网络的特点和优势
   - 比较不同方法的计算复杂度、参数量和精度
   - 总结当前研究面临的挑战和未来发展趋势

3. 格式要求：
   - 按照研究背景、方法分类、技术分析、应用场景、未来展望等章节组织
   - 每个方法需要包含：网络结构、创新点、性能指标
   - 使用表格形式对比不同方法的性能

请生成一篇结构完整、内容详实的文献综述。"""

goal = '''
目标检测数据集根目录:
images 存储图片
labels 存储标注文件，yolo格式
class_names.txt 存储类别名称

帮我编写代码转为VOC格式和coco格式，请注意:
1. 对原始标注格式编写可视化代码，
2. 图片不需要复制，采用软链接的方式 
3. 对转换后的标注文件编写可视化代码

'''
import asyncio
files = []
previous_result = ''
conversation_id = '20250604150000'
planned_tasks = asyncio.run(planning(goal, files, previous_result, conversation_id))
print(planned_tasks)

# planned_tasks = [{'title': '搜索轻量语义分割网络的研究进展', 'description': '使用网络搜索工具查找2018年至今关于轻量语义分割网络的研究进展，包括MobileNet、ShuffleNet、EfficientNet等轻量级骨干网络，以及网络压缩、知识蒸馏、量化等技术在语义分割中的应用。', 'tools': ['search']}, {'title': '分析轻量语义分割网络的特点和优势', 'description': '分析不同轻量语义分割网络的特点和优势，比较不同方法的计算复杂度、参数量和精度。', 'tools': ['search']}, {'title': '总结轻量语义分割网络的挑战和未来发展趋势', 'description': '总结当前轻量语义分割网络研究面临的挑战和未来发展趋势。', 'tools': ['search']}, {'title': '生成轻量语义分割网络文献综述报告', 'description': '根据研究背景、方法分类、技术分析、应用场景、未来展望等章节组织文献综述。每个方法需要包含：网络结构、创新点、性能指标，并使用表格形式对比不同方法的性能。', 'tools': ['file']}]
import json
import uuid
from pathlib import Path

# 为每个task添加uuid和status字段
for task in planned_tasks:
    task['id'] = str(uuid.uuid4())
    task['status'] = 'todo'

# 创建conversation_id对应的文件夹
task_dir = Path(f'tasks/{conversation_id}')
task_dir.mkdir(parents=True, exist_ok=True)

# 保存tasks到todo.json
with open(task_dir / 'todo.json', 'w', encoding='utf-8') as f:
    json.dump(planned_tasks, f, ensure_ascii=False, indent=2)

print(f'任务列表已保存到 {task_dir / "todo.json"}')