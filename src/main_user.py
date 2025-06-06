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
from src.logger import Logger
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
            self.logger = Logger('TerminalInterface')
            self.conversation_id = str(uuid.uuid4())
            
            # 初始化运行时环境
            self.runtime = LocalRuntime()
            
            # 初始化上下文
            self.context = {
                'conversation_id': self.conversation_id,
                'runtime': self.runtime,
                'on_token_stream': self._handle_token_stream,
                'config': self.config
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
                "输入 'exit' 或 'quit' 退出程序\n"
                "输入 'clear' 清除对话历史",
                title="智能助手",
                border_style="blue"
            ))
            
            # 设置运行时环境
            await self.runtime.setup()
            
            while True:
                try:
                    # 获取用户输入
                    user_input = Prompt.ask("\n[bold]请输入您的需求[/bold]")
                    
                    # 处理特殊命令
                    if user_input.lower() in ['exit', 'quit']:
                        self.console.print("\n[blue]感谢使用，再见！[/blue]")
                        break
                    elif user_input.lower() == 'clear':
                        self.agent.memory.clear()
                        self.console.print("\n[green]对话历史已清除[/green]")
                        continue
                    elif not user_input:
                        continue
                    
                    # 记录用户输入
                    message = Message.create_user_message(
                        self.conversation_id,
                        user_input
                    )
                    
                    # 运行智能体
                    self.console.print("\n[cyan]开始执行任务...[/cyan]")
                    result = await self.agent.run(user_input)
                    
                    if result.get('status') == 'failed':
                        self.console.print(f"\n[red]❌ 任务执行失败：{result.get('error', '未知错误')}[/red]")
                    elif result.get('status') == 'partial_failure':
                        self.console.print("\n[yellow]⚠️ 任务部分完成，请检查结果[/yellow]")
                    
                except KeyboardInterrupt:
                    self.console.print("\n\n[blue]程序被中断[/blue]")
                    break
                except Exception as e:
                    self.logger.error(f"发生错误：{str(e)}")
                    self.console.print(f"\n[red]❌ 发生错误：{str(e)}[/red]")
            
            # 清理资源
            await self.runtime.cleanup()
            
        except Exception as e:
            self.console.print(f"[red]启动失败: {str(e)}[/red]")
            raise


async def main():
    """主函数"""
    try:
        # 启动终端界面
        interface = TerminalInterface()
        await interface.start()
        
    except Exception as e:
        print(f"主程序错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 