from typing import Dict, Any, Tuple
import asyncio

class RetryHandler:
    """重试处理器"""
    
    def __init__(self, max_retries: int = 3, max_total_retries: int = 10, delay: float = 0.5):
        """
        初始化重试处理器
        
        Args:
            max_retries: 最大连续重试次数
            max_total_retries: 最大总重试次数
            delay: 重试延迟（秒）
        """
        self.max_retries = max_retries
        self.max_total_retries = max_total_retries
        self.delay = delay
        self.retry_count = 0
        self.total_retry_attempts = 0
        
    async def handle_retry(self, error_message: str = "") -> Tuple[bool, Dict[str, Any]]:
        """
        处理重试逻辑
        
        Args:
            error_message: 错误信息
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (是否继续重试, 结果)
        """
        # 检查是否达到最大连续重试次数
        if self.retry_count >= self.max_retries:
            return False, {
                "status": "failure",
                "comments": f"连续{error_message and '异常' or '执行失败'}达到最大次数({self.max_retries}){error_message and ': ' + error_message or ''}"
            }
            
        # 检查是否达到最大总重试次数
        if self.total_retry_attempts >= self.max_total_retries:
            return False, {
                "status": "failure",
                "comments": f"达到最大总重试次数({self.max_total_retries}){error_message and ': ' + error_message or ''}"
            }
            
        # 可以继续重试
        self.retry_count += 1
        self.total_retry_attempts += 1
        await asyncio.sleep(self.delay)
        return True, {}
        
    def reset_retry_count(self) -> None:
        """重置连续重试计数"""
        self.retry_count = 0 