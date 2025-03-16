"""
数据模型定义
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from config.settings import DATABASE

Base = declarative_base()


class Platform(Base):
    """平台信息表"""
    __tablename__ = "platforms"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, comment="平台名称")
    website = Column(String(255), nullable=False, comment="网站地址")
    type = Column(String(20), nullable=False, comment="平台类型: forum, social, qa, discord, etc")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    contents = relationship("Content", back_populates="platform")


class Content(Base):
    """内容表(帖子/回复)"""
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    content_id = Column(String(100), nullable=False, comment="内容在原平台的ID")
    url = Column(String(255), nullable=False, comment="内容URL")
    title = Column(String(255), nullable=True, comment="标题(可能为空)")
    content = Column(Text, nullable=False, comment="内容正文")
    author = Column(String(100), nullable=True, comment="作者")
    author_id = Column(String(100), nullable=True, comment="作者ID")
    parent_id = Column(Integer, ForeignKey("contents.id"), nullable=True, comment="父内容ID(回复)")
    created_time = Column(DateTime, nullable=True, comment="内容创建时间")
    scraped_time = Column(DateTime, default=datetime.now, comment="抓取时间")
    content_type = Column(String(20), default="post", comment="内容类型: post, reply, comment, etc")
    processed = Column(Boolean, default=False, comment="是否已处理")
    analyzed = Column(Boolean, default=False, comment="是否已分析")
    
    # 关联
    platform = relationship("Platform", back_populates="contents")
    replies = relationship("Content", foreign_keys=[parent_id])
    analysis = relationship("ContentAnalysis", back_populates="content", uselist=False)


class ContentAnalysis(Base):
    """内容分析结果表"""
    __tablename__ = "content_analysis"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False, unique=True)
    sentiment = Column(String(20), nullable=True, comment="情感: positive, negative, neutral")
    topics = Column(Text, nullable=True, comment="主题标签(JSON格式)")
    keywords = Column(Text, nullable=True, comment="关键词(JSON格式)")
    summary = Column(Text, nullable=True, comment="摘要")
    importance_score = Column(Integer, nullable=True, comment="重要性评分(1-100)")
    language = Column(String(20), nullable=True, comment="语言")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    content = relationship("Content", back_populates="analysis")


def init_db():
    """初始化数据库表结构"""
    if DATABASE["type"] in ["sqlite", "mysql"]:
        if DATABASE["type"] == "sqlite":
            db_path = DATABASE["sqlite"]["path"]
            engine = create_engine(f"sqlite:///{db_path}")
        else:  # mysql
            config = DATABASE["mysql"]
            connection_string = (
                f"mysql+pymysql://{config['user']}:{config['password']}@"
                f"{config['host']}:{config['port']}/{config['database']}"
            )
            engine = create_engine(connection_string)
            
        # 创建表
        Base.metadata.create_all(engine)
        return engine 