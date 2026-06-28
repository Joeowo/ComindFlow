"""
日志系统模块

使用 Loguru 实现结构化日志系统
"""
from loguru import logger
import sys
from pathlib import Path


def init_logger(
    level: str = "INFO",
    file_path: str = None,
    rotation: str = "100 MB",
    retention: str = "30 days"
):
    """初始化日志系统

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        file_path: 日志文件路径 (可选)
        rotation: 日志轮转配置 (如 "100 MB", "00:00", "1 week")
        retention: 日志保留配置 (如 "30 days", "1 week", "10 MB")
    """
    # 移除默认处理器
    logger.remove()

    # 添加控制台处理器（带颜色）
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )

    # 添加文件处理器
    if file_path:
        log_path = Path(file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            file_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
            rotation=rotation,
            retention=retention,
            compression="zip"
        )

    logger.info("日志系统初始化完成")
