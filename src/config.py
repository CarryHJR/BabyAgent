def get_config():
    """获取配置信息"""
    class Config:
        """配置类"""
        def __init__(self):
            # 应用配置
            self.APP_NAME = 'LemonAI'
            self.VERSION = '1.0.0'

            # 模型配置
            self.MODEL_NAME = 'gpt-4o'
            self.MODEL_TEMPERATURE = 0.7
            self.MODEL_MAX_TOKENS = 2000

            # API配置
            self.OPENAI_API_KEY = 'sk-xxxxxxxxx'
            self.OPENAI_API_BASE = 'https://one.ooo.cool/v1'

            # 代理配置
            self.AGENT_MEMORY_SIZE = 10
            self.AGENT_MAX_ITERATIONS = 3

    return Config()


def get_workspace_dir():
    """获取工作目录"""
    import os
    from pathlib import Path

    workspace_dir = Path(os.getcwd()) / 'workspace'

    # 确保目录存在
    workspace_dir.mkdir(parents=True, exist_ok=True)

    return workspace_dir

def get_log_dir():
    """获取日志目录"""
    import os
    from pathlib import Path

    log_dir = Path(os.getcwd()) / 'logs'

    # 确保目录存在
    log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir

