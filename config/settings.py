"""
全局配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础路径
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "storage" / "data"
LOGS_DIR = BASE_DIR / "storage" / "logs"

# 确保路径存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# 数据库配置
DATABASE = {
    "type": os.getenv("DB_TYPE", "sqlite"),  # sqlite, mysql, mongodb
    "sqlite": {
        "path": str(DATA_DIR / "database.db"),
    },
    "mysql": {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "ai_rpa"),
    },
    "mongodb": {
        "host": os.getenv("MONGO_HOST", "localhost"),
        "port": int(os.getenv("MONGO_PORT", 27017)),
        "database": os.getenv("MONGO_DATABASE", "ai_rpa"),
    }
}

# 爬虫配置
SCRAPER = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "request_timeout": 30,
    "retry_times": 3,
    "retry_interval": 5,
}

# API密钥配置
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY", ""),
}

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") 