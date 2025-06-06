import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 设置日志级别
    logger.setLevel(logging.DEBUG)
    
    # 创建日志目录
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # 创建文件处理器
    log_file = log_dir / f'{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建文件格式化器
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # 创建控制台格式化器 - 包含异常信息
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
        'File "%(pathname)s", line %(lineno)d, in %(funcName)s\n'
        '%(exc_info)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# class Logger:
#     """日志记录器"""
    
#     def __init__(self, name: str, log_dir: Optional[str] = None):
#         self.name = name
#         self.logger = logging.getLogger(name)
#         self.logger.setLevel(logging.DEBUG)
        
#         # 设置日志目录
#         if log_dir is None:
#             # 设置为当前目录
#             log_dir = os.getcwd()
#         self.log_dir = Path(log_dir)
#         self.log_dir.mkdir(parents=True, exist_ok=True)
        
#         # 设置日志文件
#         log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
#         file_handler = logging.FileHandler(log_file, encoding='utf-8')
#         file_handler.setLevel(logging.DEBUG)
        
#         # 设置控制台输出
#         console_handler = logging.StreamHandler()
#         console_handler.setLevel(logging.INFO)
        
#         # 设置日志格式
#         formatter = logging.Formatter(
#             '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#         )
#         file_handler.setFormatter(formatter)
#         console_handler.setFormatter(formatter)
        
#         # 添加处理器
#         self.logger.addHandler(file_handler)
#         self.logger.addHandler(console_handler)
    
#     def debug(self, message: str) -> None:
#         """记录调试信息"""
#         self.logger.debug(message)
    
#     def info(self, message: str) -> None:
#         """记录一般信息"""
#         self.logger.info(message)
    
#     def warning(self, message: str) -> None:
#         """记录警告信息"""
#         self.logger.warning(message)
    
#     def error(self, message: str) -> None:
#         """记录错误信息"""
#         self.logger.error(message)
    
#     def critical(self, message: str) -> None:
#         """记录严重错误信息"""
#         self.logger.critical(message)
    
#     def log(self, message: str) -> None:
#         """记录一般信息（info的别名）"""
#         self.info(message)

#     def set_level(self, level: int) -> None:
#         """
#         设置日志级别
        
#         Args:
#             level: 日志级别
#         """
#         self.logger.setLevel(level)
#         for handler in self.logger.handlers:
#             handler.setLevel(level)

#     def get_log_file(self) -> Optional[str]:
#         """
#         获取当前日志文件路径
        
#         Returns:
#             Optional[str]: 日志文件路径
#         """
#         for handler in self.logger.handlers:
#             if isinstance(handler, logging.FileHandler):
#                 return handler.baseFilename
#         return None

#     def clear_handlers(self) -> None:
#         """清除所有处理器"""
#         for handler in self.logger.handlers[:]:
#             self.logger.removeHandler(handler)

#     def add_handler(self, handler: logging.Handler) -> None:
#         """
#         添加处理器
        
#         Args:
#             handler: 日志处理器
#         """
#         self.logger.addHandler(handler) 