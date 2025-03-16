"""
数据库连接和操作模块
"""
import sqlite3
from sqlalchemy import create_engine, MetaData
from pymongo import MongoClient

from config.settings import DATABASE
from utils.logger import log


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.db_type = DATABASE["type"]
        self.connection = None
        self.engine = None
    
    def connect(self):
        """连接到数据库"""
        try:
            if self.db_type == "sqlite":
                # SQLite连接
                db_path = DATABASE["sqlite"]["path"]
                self.engine = create_engine(f"sqlite:///{db_path}")
                log.info(f"成功连接到SQLite数据库: {db_path}")
                
            elif self.db_type == "mysql":
                # MySQL连接
                config = DATABASE["mysql"]
                connection_string = (
                    f"mysql+pymysql://{config['user']}:{config['password']}@"
                    f"{config['host']}:{config['port']}/{config['database']}"
                )
                self.engine = create_engine(connection_string)
                log.info(f"成功连接到MySQL数据库: {config['host']}:{config['port']}/{config['database']}")
                
            elif self.db_type == "mongodb":
                # MongoDB连接
                config = DATABASE["mongodb"]
                self.connection = MongoClient(
                    host=config["host"],
                    port=config["port"]
                )
                log.info(f"成功连接到MongoDB: {config['host']}:{config['port']}/{config['database']}")
                
            else:
                log.error(f"不支持的数据库类型: {self.db_type}")
                raise ValueError(f"不支持的数据库类型: {self.db_type}")
                
        except Exception as e:
            log.error(f"数据库连接失败: {str(e)}")
            raise
    
    def get_connection(self):
        """获取数据库连接"""
        if not self.connection and not self.engine:
            self.connect()
            
        if self.db_type in ["sqlite", "mysql"]:
            return self.engine
        else:  # mongodb
            db_name = DATABASE["mongodb"]["database"]
            return self.connection[db_name]
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            log.info("数据库连接已关闭")


# 全局数据库管理器
db_manager = DatabaseManager() 