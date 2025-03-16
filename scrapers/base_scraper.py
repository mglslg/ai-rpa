"""
爬虫基类模块
"""
import time
import random
import requests
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional

from config.settings import SCRAPER
from utils.logger import log


class BaseScraper(ABC):
    """
    爬虫基类，定义了爬虫的基本接口和通用方法
    """
    
    def __init__(self, platform_name: str, platform_url: str, platform_type: str):
        """
        初始化爬虫
        
        Args:
            platform_name: 平台名称
            platform_url: 平台URL
            platform_type: 平台类型
        """
        self.platform_name = platform_name
        self.platform_url = platform_url
        self.platform_type = platform_type
        self.headers = {
            "User-Agent": SCRAPER["user_agent"],
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.timeout = SCRAPER["request_timeout"]
        self.retry_times = SCRAPER["retry_times"]
        self.retry_interval = SCRAPER["retry_interval"]
    
    def request_get(self, url: str, params: Dict = None) -> Optional[requests.Response]:
        """
        发送GET请求
        
        Args:
            url: 请求的URL
            params: 请求参数
            
        Returns:
            响应对象，失败返回None
        """
        for i in range(self.retry_times + 1):
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                log.warning(f"请求失败: {url}, 错误: {str(e)}, 重试中: {i+1}/{self.retry_times}")
                if i < self.retry_times:
                    # 添加随机延迟
                    time.sleep(self.retry_interval + random.uniform(0.1, 2.0))
                else:
                    log.error(f"请求最终失败: {url}")
                    return None
    
    def request_post(self, url: str, data: Dict = None, json: Dict = None) -> Optional[requests.Response]:
        """
        发送POST请求
        
        Args:
            url: 请求的URL
            data: 表单数据
            json: JSON数据
            
        Returns:
            响应对象，失败返回None
        """
        for i in range(self.retry_times + 1):
            try:
                response = self.session.post(
                    url, 
                    data=data, 
                    json=json, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                log.warning(f"POST请求失败: {url}, 错误: {str(e)}, 重试中: {i+1}/{self.retry_times}")
                if i < self.retry_times:
                    # 添加随机延迟
                    time.sleep(self.retry_interval + random.uniform(0.1, 2.0))
                else:
                    log.error(f"POST请求最终失败: {url}")
                    return None
    
    @abstractmethod
    def scrape_posts(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        抓取帖子列表
        
        Returns:
            帖子数据列表
        """
        pass
    
    @abstractmethod
    def scrape_replies(self, post_id: str, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        抓取帖子的回复
        
        Args:
            post_id: 帖子ID
            
        Returns:
            回复数据列表
        """
        pass
    
    @abstractmethod
    def parse_content(self, raw_content: Any) -> Dict[str, Any]:
        """
        解析内容
        
        Args:
            raw_content: 原始内容数据
            
        Returns:
            解析后的数据字典
        """
        pass
    
    def normalize_time(self, time_str: str) -> Optional[datetime]:
        """
        将时间字符串标准化为datetime对象
        
        Args:
            time_str: 时间字符串
            
        Returns:
            datetime对象，失败返回None
        """
        try:
            # 这里需要根据具体平台自定义实现
            return datetime.now()
        except Exception as e:
            log.error(f"解析时间失败: {time_str}, 错误: {str(e)}")
            return None
    
    def close(self):
        """
        关闭会话
        """
        self.session.close()
        log.info(f"爬虫会话已关闭: {self.platform_name}") 