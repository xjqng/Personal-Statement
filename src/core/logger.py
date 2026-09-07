import os
import sys
from loguru import logger

# 日志文件夹路径
LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

# 清空默认处理器
logger.remove()

# 自定义日志格式：时间 | 级别 | 代码位置 | 内容
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"

# 1. 控制台输出（开发调试用，DEBUG级别）
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level="DEBUG",
    enqueue=True
)

# 2. 文件持久化：按50MB切割，保留7天，文件只记录INFO及以上
logger.add(
    os.path.join(LOG_FOLDER, "app.log"),
    format=LOG_FORMAT,
    level="INFO",
    rotation="50 MB",
    retention="7 days",
    encoding="utf-8",
    enqueue=True,
    diagnose=False
)