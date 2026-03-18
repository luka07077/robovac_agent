"""
日志处理工具类
"""
import os
import logging
from datetime import datetime
from utils.path_tool import get_abs_path


# 日志保存目录
LOG_PATH = get_abs_path('logs/')
# 默认日志名称
LOG_DEFAULT_NAME = 'agent'

# 确保日志目录存在
os.makedirs(LOG_PATH, exist_ok=True)

# 日志的配置格式
DEFAULT_LOG_FORMAT = (
    "%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s"
)

def get_logger(
        name: str = LOG_DEFAULT_NAME,
        console_level: int = logging.DEBUG,
        file_level: int = logging.INFO,
        log_file_path: str = None
) -> logging.Logger:
    """
    获取日志处理对象logger
    :param name: 日志名称
    :param console_level: 控制台日志级别
    :param file_level: 文件日志级别
    :param log_file_path: 日志文件路径
    :return: logger
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        return logger

    # 定义控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    logger.addHandler(console_handler)

    # 定义文件handler
    if not log_file_path:
        log_file_path = os.path.join(LOG_PATH, f'{name}_{datetime.now().strftime("%Y%m%d%H%M")}.log')
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    logger.addHandler(file_handler)

    return logger


# 定义全局实例
logger = get_logger()


if __name__ == '__main__':
    logger.info('info')
    logger.error('error')
    logger.warning('warning')


