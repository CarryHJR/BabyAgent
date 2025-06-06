import os
import sys
import asyncio
import uuid
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from src.agent import AgenticAgent
from src.logger import get_logger
from src.models import Message
from src.runtime import LocalRuntime
from src.config import get_config




class TerminalInterface:
    """终端界面"""
    
    def __init__(self):
        """初始化终端界面"""
        try:
            self.config = get_config()
            self.console = Console()
            self.logger = get_logger(__name__)
            self.conversation_id = str(uuid.uuid4())
            
            # 初始化运行时环境
            self.runtime = LocalRuntime()
            
            # 初始化上下文
            self.context = {
                'conversation_id': self.conversation_id,
                'runtime': self.runtime,
                'on_token_stream': self._handle_token_stream,
                'config': self.config,
                'log_file': 'task_log.md'  # 添加日志文件配置
            }
            
            # 初始化代理
            self.agent = AgenticAgent(self.context)
            self.logger.info("终端界面初始化成功")
            
        except Exception as e:
            self.console.print(f"[red]初始化失败: {str(e)}[/red]")
            raise
    
    async def _handle_token_stream(self, message: Dict[str, Any]) -> None:
        """处理token流"""
        try:
            if message.get('status') == 'running':
                self.console.print(f"\n[cyan]🔄 {message.get('content', '')}[/cyan]")
            elif message.get('status') == 'success':
                if message.get('action_type') == 'auto_reply':
                    self.console.print(f"\n[green]🤖 {message.get('content', '')}[/green]")
                elif message.get('action_type') == 'plan':
                    self.console.print("\n[blue]📋 任务计划：[/blue]")
                    tasks = message.get('json', [])
                    for task in tasks:
                        self.console.print(f"  - {task.get('requirement', '')}")
                elif message.get('action_type') == 'finish':
                    self.console.print(f"\n[green]✅ {message.get('content', '')}[/green]")
            elif message.get('status') == 'error':
                self.console.print(f"\n[red]❌ 错误：{message.get('content', '')}[/red]")
        except Exception as e:
            self.console.print(f"[red]处理消息时出错: {str(e)}[/red]")
    
    async def start(self) -> None:
        """启动终端界面"""
        try:
            # 显示欢迎信息
            self.console.print(Panel.fit(
                f"[bold blue]{self.config.APP_NAME} v{self.config.VERSION}[/bold blue]\n"
                "正在生成轻量语义分割网络的文献综述...",
                title="智能助手",
                border_style="blue"
            ))
            
            # 设置运行时环境
            await self.runtime.setup()
            
            # 构建文献综述的提示词
            prompt = """
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
            
            # 运行智能体
            self.console.print("\n[cyan]开始生成文献综述...[/cyan]")
            result = await self.agent.run(prompt)
            
            if result.get('status') == 'failed':
                self.console.print(f"\n[red]❌ 生成失败：{result.get('error', '未知错误')}[/red]")
            elif result.get('status') == 'partial_failure':
                self.console.print("\n[yellow]⚠️ 部分内容生成失败，请检查结果[/yellow]")
            
            # 清理资源
            await self.runtime.cleanup()
            
        except Exception as e:
            import traceback
            error_info = traceback.format_exc()
            self.console.print(f"[red]启动失败: {str(e)}[/red]")
            self.console.print(f"[red]错误详情:\n{error_info}[/red]")
            raise

async def main():
    """主函数"""
    try:
        # 启动终端界面
        interface = TerminalInterface()
        await interface.start()
        
    except Exception as e:
        import traceback
        error_info = traceback.format_exc()
        print(f"主程序错误: {str(e)}")
        print(f"错误详情:\n{error_info}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 