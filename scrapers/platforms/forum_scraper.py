"""
通用论坛爬虫模块
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.logger import log


class ForumScraper(BaseScraper):
    """
    通用论坛爬虫
    适用于常见的论坛结构
    """
    
    def __init__(self, platform_name: str, platform_url: str):
        super().__init__(platform_name, platform_url, platform_type="forum")
        self.forum_base_url = platform_url
        # 子类中可以根据具体论坛重写这些URL模板
        self.list_url_template = f"{platform_url}/forum/list?page={{page}}"
        self.post_url_template = f"{platform_url}/forum/post/{{post_id}}"
        
    def scrape_posts(self, max_pages: int = 1) -> List[Dict[str, Any]]:
        """
        抓取帖子列表
        
        Args:
            max_pages: 最大页数
            
        Returns:
            帖子数据列表
        """
        all_posts = []
        
        for page in range(1, max_pages + 1):
            url = self.list_url_template.format(page=page)
            log.info(f"抓取帖子列表: {url}")
            
            response = self.request_get(url)
            if not response:
                log.error(f"抓取帖子列表失败: {url}")
                continue
                
            # 解析页面获取帖子列表
            soup = BeautifulSoup(response.content, 'html.parser')
            post_elements = soup.select('.post-item')  # 根据实际网站调整选择器
            
            if not post_elements:
                log.warning(f"页面未找到帖子: {url}")
                continue
                
            for post_elem in post_elements:
                try:
                    # 根据实际网站调整数据提取方式
                    post_id = post_elem.get('data-id') or post_elem.find('a', class_='post-link').get('href').split('/')[-1]
                    title = post_elem.select_one('.post-title').text.strip()
                    author = post_elem.select_one('.post-author').text.strip()
                    author_id = post_elem.select_one('.post-author').get('data-userid')
                    created_time_str = post_elem.select_one('.post-time').text.strip()
                    created_time = self.normalize_time(created_time_str)
                    url = self.post_url_template.format(post_id=post_id)
                    
                    post_data = {
                        'content_id': post_id,
                        'url': url,
                        'title': title,
                        'author': author,
                        'author_id': author_id,
                        'created_time': created_time,
                        'content_type': 'post',
                    }
                    
                    all_posts.append(post_data)
                    
                except Exception as e:
                    log.error(f"解析帖子元素失败: {str(e)}")
                    continue
            
            log.info(f"第{page}页抓取完成，获取{len(post_elements)}个帖子")
        
        return all_posts
    
    def scrape_post_content(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        抓取帖子内容
        
        Args:
            post_id: 帖子ID
            
        Returns:
            帖子内容数据
        """
        url = self.post_url_template.format(post_id=post_id)
        log.info(f"抓取帖子内容: {url}")
        
        response = self.request_get(url)
        if not response:
            log.error(f"抓取帖子内容失败: {url}")
            return None
            
        # 解析页面获取帖子内容
        soup = BeautifulSoup(response.content, 'html.parser')
        
        try:
            # 根据实际网站调整数据提取方式
            title = soup.select_one('.post-title').text.strip()
            content = soup.select_one('.post-content').text.strip()
            author = soup.select_one('.post-author').text.strip()
            author_id = soup.select_one('.post-author').get('data-userid')
            created_time_str = soup.select_one('.post-time').text.strip()
            created_time = self.normalize_time(created_time_str)
            
            post_data = {
                'content_id': post_id,
                'url': url,
                'title': title,
                'content': content,
                'author': author,
                'author_id': author_id,
                'created_time': created_time,
                'content_type': 'post',
            }
            
            return post_data
            
        except Exception as e:
            log.error(f"解析帖子内容失败: {str(e)}")
            return None
    
    def scrape_replies(self, post_id: str, max_pages: int = 1) -> List[Dict[str, Any]]:
        """
        抓取帖子的回复
        
        Args:
            post_id: 帖子ID
            max_pages: 最大页数
            
        Returns:
            回复数据列表
        """
        all_replies = []
        
        for page in range(1, max_pages + 1):
            url = f"{self.post_url_template.format(post_id=post_id)}?page={page}"
            log.info(f"抓取帖子回复: {url}")
            
            response = self.request_get(url)
            if not response:
                log.error(f"抓取帖子回复失败: {url}")
                continue
                
            # 解析页面获取回复列表
            soup = BeautifulSoup(response.content, 'html.parser')
            reply_elements = soup.select('.reply-item')  # 根据实际网站调整选择器
            
            if not reply_elements:
                log.warning(f"页面未找到回复: {url}")
                continue
                
            for reply_elem in reply_elements:
                try:
                    # 根据实际网站调整数据提取方式
                    reply_id = reply_elem.get('data-id')
                    content = reply_elem.select_one('.reply-content').text.strip()
                    author = reply_elem.select_one('.reply-author').text.strip()
                    author_id = reply_elem.select_one('.reply-author').get('data-userid')
                    created_time_str = reply_elem.select_one('.reply-time').text.strip()
                    created_time = self.normalize_time(created_time_str)
                    
                    reply_data = {
                        'content_id': reply_id,
                        'parent_id': post_id,
                        'url': f"{url}#reply-{reply_id}",
                        'content': content,
                        'author': author,
                        'author_id': author_id,
                        'created_time': created_time,
                        'content_type': 'reply',
                    }
                    
                    all_replies.append(reply_data)
                    
                except Exception as e:
                    log.error(f"解析回复元素失败: {str(e)}")
                    continue
            
            log.info(f"第{page}页回复抓取完成，获取{len(reply_elements)}个回复")
        
        return all_replies
    
    def parse_content(self, raw_content: Any) -> Dict[str, Any]:
        """
        解析内容
        
        Args:
            raw_content: 原始内容数据
            
        Returns:
            解析后的数据字典
        """
        # 这个方法具体实现取决于原始数据的格式
        # 如果已经是字典，可能只需要简单转换
        if isinstance(raw_content, dict):
            return raw_content
        elif isinstance(raw_content, str):
            # 尝试解析JSON字符串
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                log.error("解析内容失败: 无效的JSON格式")
                return {}
        else:
            log.error(f"解析内容失败: 不支持的数据类型 {type(raw_content)}")
            return {} 