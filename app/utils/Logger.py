"""
日志工具类

提供统一的日志记录功能，支持控制台输出和文件记录。
轮转功能：日志文件大小超过 10MB 时，自动创建新文件，保留 5 个旧文件。
日志文件存储在项目根目录下的 logs 目录中。

使用方法：
    from utils.Logger import Logger
    logger = Logger.get_logger(__name__)
    logger.info("这是一条信息日志")
    logger.error("这是一条错误日志")
"""

import logging
from logging.handlers import RotatingFileHandler  # 日志轮转
from pathlib import Path


class Logger:
    _logger = None  # 单例，防止重复初始化
    @classmethod
    def get_logger(cls, name=__name__):
        """
        获取全局 Logger 实例（单例模式）
        - 日志级别: INFO 及以上级别
        - 日志格式: 时间 - 日志级别 - 日志模块 - 日志消息
        """
        if cls._logger:
            return cls._logger

        # 项目根目录
        base_dir = Path(__file__).resolve().parent.parent

        log_dir = base_dir / "logs"
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / "app.log"

        logger = logging.getLogger(name)
        # 设置日志级别为 INFO 及以上级别
        logger.setLevel(logging.INFO)

        # 防止重复添加 handler
        if not logger.handlers:

            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
            )

            # 控制台
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            # 日志轮转（10MB 一个，保留 5个）
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8"
            )
            file_handler.setFormatter(formatter)

            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        cls._logger = logger
        return logger