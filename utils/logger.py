"""
日志工具模块
"""
import sys
from pathlib import Path
from loguru import logger

from config.settings import LOG_LEVEL, LOGS_DIR


def setup_logger():
    """
    配置日志系统
    """
    # 清除默认处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(sys.stdout, level=LOG_LEVEL)
    
    # 添加文件输出
    log_file = LOGS_DIR / "app.log"
    logger.add(
        log_file,
        rotation="1 day",    # 每天轮换一次
        retention="7 days",  # 保留7天的日志
        level=LOG_LEVEL,
        encoding="utf-8",
    )
    
    return logger

# 全局日志对象
log = setup_logger() 