"""
内容处理模块
"""
import re
from typing import Dict, Any, List
from datetime import datetime

from utils.logger import log


class ContentProcessor:
    """
    内容处理器
    负责清洗和标准化抓取的原始内容
    """
    
    def __init__(self):
        """初始化处理器"""
        pass
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        if not text:
            return ""
            
        # 移除HTML标签
        clean = re.sub(r'<.*?>', '', text)
        
        # 替换多个空格为单个空格
        clean = re.sub(r'\s+', ' ', clean)
        
        # 替换多个换行为单个换行
        clean = re.sub(r'\n+', '\n', clean)
        
        # 移除前后空白
        clean = clean.strip()
        
        return clean
    
    def normalize_url(self, url: str) -> str:
        """
        标准化URL
        
        Args:
            url: 原始URL
            
        Returns:
            标准化后的URL
        """
        if not url:
            return ""
            
        # 确保URL包含协议
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # 移除URL结尾的斜杠
        url = url.rstrip('/')
        
        return url
    
    def process_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理内容
        
        Args:
            content: 原始内容数据
            
        Returns:
            处理后的内容数据
        """
        if not content:
            return {}
            
        try:
            # 复制原始数据
            processed = content.copy()
            
            # 清洗文本内容
            if 'content' in processed:
                processed['content'] = self.clean_text(processed['content'])
                
            # 清洗标题
            if 'title' in processed and processed['title']:
                processed['title'] = self.clean_text(processed['title'])
                
            # 标准化URL
            if 'url' in processed:
                processed['url'] = self.normalize_url(processed['url'])
                
            # 标记为已处理
            processed['processed'] = True
            
            return processed
            
        except Exception as e:
            log.error(f"处理内容失败: {str(e)}")
            return content
    
    def process_batch(self, contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量处理内容
        
        Args:
            contents: 原始内容数据列表
            
        Returns:
            处理后的内容数据列表
        """
        return [self.process_content(content) for content in contents] 