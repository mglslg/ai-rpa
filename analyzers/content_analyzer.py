"""
内容分析模块 - 使用OpenAI API
"""
import json
import os
from typing import Dict, List, Any, Optional
import requests
from time import sleep

from utils.logger import log
from config.settings import API_KEYS


class ContentAnalyzer:
    """
    内容分析器
    负责对抓取的内容进行分析，使用OpenAI API替代本地模型
    """
    
    def __init__(self):
        """初始化分析器"""
        self.openai_api_key = API_KEYS.get("openai")
        self.api_endpoint = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"  # 可以配置为gpt-4等更高级模型
        
        if not self.openai_api_key:
            log.warning("未设置OpenAI API密钥，内容分析功能将不可用")
    
    def _call_openai_api(self, messages: List[Dict], max_retries: int = 3) -> Optional[Dict]:
        """
        调用OpenAI API
        
        Args:
            messages: 对话消息列表
            max_retries: 最大重试次数
            
        Returns:
            API响应，失败返回None
        """
        if not self.openai_api_key:
            log.error("未设置OpenAI API密钥")
            return None
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3  # 保持输出稳定性
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_endpoint,
                    headers=headers,
                    json=data,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                log.error(f"OpenAI API请求失败: {str(e)}")
                if attempt < max_retries - 1:
                    sleep_time = 2 ** attempt  # 指数退避
                    log.info(f"等待{sleep_time}秒后重试...")
                    sleep(sleep_time)
                else:
                    log.error("已达到最大重试次数")
                    return None
    
    def analyze_sentiment(self, text: str) -> str:
        """
        情感分析
        
        Args:
            text: 文本内容
            
        Returns:
            情感标签: positive, negative, neutral
        """
        if not self.openai_api_key:
            return "unknown"
            
        try:
            # 构建提示
            messages = [
                {"role": "system", "content": "你是一个情感分析助手。请分析以下文本的情感，只回复'positive'、'negative'或'neutral'之一。"},
                {"role": "user", "content": text[:1000]}  # 限制长度
            ]
            
            response = self._call_openai_api(messages)
            if not response or "choices" not in response:
                return "unknown"
                
            sentiment = response["choices"][0]["message"]["content"].strip().lower()
            
            # 标准化为positive, negative, neutral
            if "positive" in sentiment:
                return "positive"
            elif "negative" in sentiment:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            log.error(f"情感分析失败: {str(e)}")
            return "unknown"
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        提取关键词
        
        Args:
            text: 文本内容
            top_n: 返回的关键词数量
            
        Returns:
            关键词列表
        """
        if not self.openai_api_key:
            return []
            
        try:
            # 构建提示
            messages = [
                {"role": "system", "content": f"你是一个关键词提取助手。请从以下文本中提取最多{top_n}个关键词，以JSON数组格式返回，格式为[\"关键词1\", \"关键词2\", ...]。"},
                {"role": "user", "content": text[:1500]}  # 限制长度
            ]
            
            response = self._call_openai_api(messages)
            if not response or "choices" not in response:
                return []
                
            content = response["choices"][0]["message"]["content"].strip()
            
            # 尝试解析JSON
            try:
                # 查找内容中的JSON数组
                start_idx = content.find('[')
                end_idx = content.rfind(']') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    keywords = json.loads(json_str)
                    # 确保结果是字符串列表
                    keywords = [str(kw).strip() for kw in keywords if kw]
                    return keywords[:top_n]  # 限制数量
                else:
                    # 如果没有找到JSON数组，按行分割
                    words = [line.strip() for line in content.split('\n') if line.strip()]
                    # 清理可能的序号和标点
                    keywords = [w.split('.')[-1].strip(' "\',.;:()[]{}') for w in words]
                    return [k for k in keywords if k][:top_n]
            except json.JSONDecodeError:
                # 如果JSON解析失败，按行分割
                words = [line.strip() for line in content.split('\n') if line.strip()]
                # 清理可能的序号和标点
                keywords = [w.split('.')[-1].strip(' "\',.;:()[]{}') for w in words]
                return [k for k in keywords if k][:top_n]
                
        except Exception as e:
            log.error(f"提取关键词失败: {str(e)}")
            return []
    
    def extract_topics(self, text: str, keywords: List[str] = None) -> List[str]:
        """
        提取主题
        
        Args:
            text: 文本内容
            keywords: 已提取的关键词
            
        Returns:
            主题列表
        """
        if not self.openai_api_key:
            return []
            
        try:
            # 构建提示
            system_content = "你是一个主题提取专家。请从以下文本中识别5个主要主题或类别，以JSON数组格式返回，格式为[\"主题1\", \"主题2\", ...]。"
            if keywords and len(keywords) > 0:
                system_content += f"参考关键词: {', '.join(keywords[:10])}"
                
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": text[:1500]}  # 限制长度
            ]
            
            response = self._call_openai_api(messages)
            if not response or "choices" not in response:
                return keywords[:5] if keywords else []
                
            content = response["choices"][0]["message"]["content"].strip()
            
            # 尝试解析JSON
            try:
                # 查找内容中的JSON数组
                start_idx = content.find('[')
                end_idx = content.rfind(']') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    topics = json.loads(json_str)
                    # 确保结果是字符串列表
                    topics = [str(t).strip() for t in topics if t]
                    return topics[:5]  # 限制数量
                else:
                    # 如果没有找到JSON数组，按行分割
                    topics = [line.strip() for line in content.split('\n') if line.strip()]
                    # 清理可能的序号和标点
                    topics = [t.split('.')[-1].strip(' "\',.;:()[]{}') for t in topics]
                    return [t for t in topics if t][:5]
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试按行分割
                topics = [line.strip() for line in content.split('\n') if line.strip()]
                # 清理可能的序号和标点
                topics = [t.split('.')[-1].strip(' "\',.;:()[]{}') for t in topics]
                return [t for t in topics if t][:5]
                    
        except Exception as e:
            log.error(f"提取主题失败: {str(e)}")
            return keywords[:5] if keywords else []
    
    def generate_summary(self, text: str, max_length: int = 150) -> str:
        """
        生成摘要
        
        Args:
            text: 文本内容
            max_length: 摘要最大长度
            
        Returns:
            摘要文本
        """
        if not self.openai_api_key:
            # 简单的提取式摘要作为后备
            if len(text) <= max_length:
                return text
                
            return text[:max_length].rsplit('.', 1)[0] + '.'
            
        try:
            # 构建提示
            messages = [
                {"role": "system", "content": f"你是一个文本摘要专家。请为以下文本生成一个简洁的摘要，不超过{max_length}个字符。"},
                {"role": "user", "content": text[:2000]}  # 限制长度
            ]
            
            response = self._call_openai_api(messages)
            if not response or "choices" not in response:
                # 后备方案
                if len(text) <= max_length:
                    return text
                    
                return text[:max_length].rsplit('.', 1)[0] + '.'
                
            summary = response["choices"][0]["message"]["content"].strip()
            
            # 确保不超过最大长度
            if len(summary) > max_length:
                summary = summary[:max_length].rsplit('.', 1)[0] + '.'
                
            return summary
                
        except Exception as e:
            log.error(f"生成摘要失败: {str(e)}")
            # 后备方案
            if len(text) <= max_length:
                return text
                
            return text[:max_length].rsplit('.', 1)[0] + '.'
    
    def calculate_importance_score(self, 
                                   content: Dict[str, Any], 
                                   keywords: List[str] = None, 
                                   sentiment: str = None) -> int:
        """
        计算内容重要性评分
        
        Args:
            content: 内容数据
            keywords: 关键词列表
            sentiment: 情感标签
            
        Returns:
            重要性评分(1-100)
        """
        if not self.openai_api_key:
            # 简单的评分逻辑作为后备
            score = 50  # 默认中等重要性
            
            # 根据内容长度调整分数
            text = content.get('content', '')
            if len(text) > 1000:
                score += 10
            elif len(text) < 100:
                score -= 10
                
            # 根据回复数量调整分数(如果有)
            replies_count = content.get('replies_count', 0)
            if replies_count > 10:
                score += 15
            elif replies_count > 5:
                score += 10
            elif replies_count > 0:
                score += 5
                
            # 确保分数在1-100范围内
            return max(1, min(score, 100))
        
        try:
            # 构建上下文信息
            context = {
                "content_length": len(content.get('content', '')),
                "has_title": bool(content.get('title')),
                "replies_count": content.get('replies_count', 0),
                "content_type": content.get('content_type', 'post'),
            }
            
            if keywords:
                context["keywords"] = keywords[:10]
                
            if sentiment:
                context["sentiment"] = sentiment
                
            # 构建提示
            messages = [
                {"role": "system", "content": "你是一个内容评估专家。请为以下内容评定重要性分数(1-100)，只返回一个整数。"},
                {"role": "user", "content": f"内容: {content.get('content', '')[:1000]}\n\n上下文信息: {json.dumps(context, ensure_ascii=False)}"}
            ]
            
            response = self._call_openai_api(messages)
            if not response or "choices" not in response:
                # 后备方案
                return self._fallback_importance_score(content, keywords, sentiment)
                
            score_text = response["choices"][0]["message"]["content"].strip()
            
            # 尝试提取数字
            import re
            score_match = re.search(r'\b(\d{1,3})\b', score_text)
            if score_match:
                score = int(score_match.group(1))
                # 确保分数在1-100范围内
                return max(1, min(score, 100))
            else:
                # 后备方案
                return self._fallback_importance_score(content, keywords, sentiment)
                
        except Exception as e:
            log.error(f"计算重要性评分失败: {str(e)}")
            # 后备方案
            return self._fallback_importance_score(content, keywords, sentiment)
    
    def _fallback_importance_score(self, content: Dict[str, Any], keywords: List[str] = None, sentiment: str = None) -> int:
        """简单的重要性评分逻辑作为后备方案"""
        score = 50  # 默认中等重要性
        
        # 根据内容长度调整分数
        text = content.get('content', '')
        if len(text) > 1000:
            score += 10
        elif len(text) < 100:
            score -= 10
            
        # 根据关键词匹配度调整分数
        if keywords:
            found_keywords = sum(1 for kw in keywords if kw.lower() in text.lower())
            keyword_score = min(found_keywords * 5, 20)  # 最多加20分
            score += keyword_score
            
        # 根据回复数量调整分数(如果有)
        replies_count = content.get('replies_count', 0)
        if replies_count > 10:
            score += 15
        elif replies_count > 5:
            score += 10
        elif replies_count > 0:
            score += 5
            
        # 确保分数在1-100范围内
        return max(1, min(score, 100))
    
    def analyze_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析内容
        
        Args:
            content: 内容数据
            
        Returns:
            分析结果
        """
        text = content.get('content', '')
        if not text:
            log.warning("分析内容为空")
            return {}
            
        try:
            if not self.openai_api_key:
                log.warning("未设置OpenAI API密钥，将使用简化分析")
                # 简单的后备分析
                summary = text[:150].rsplit('.', 1)[0] + '.' if len(text) > 150 else text
                return {
                    'sentiment': 'neutral',
                    'keywords': json.dumps([]),
                    'topics': json.dumps([]),
                    'summary': summary,
                    'importance_score': self._fallback_importance_score(content),
                    'language': 'unknown',
                }
            
            # 情感分析
            sentiment = self.analyze_sentiment(text)
            
            # 提取关键词
            keywords = self.extract_keywords(text)
            
            # 提取主题
            topics = self.extract_topics(text, keywords)
            
            # 生成摘要
            summary = self.generate_summary(text)
            
            # 计算重要性评分
            importance_score = self.calculate_importance_score(content, keywords, sentiment)
            
            # 组装分析结果
            analysis_result = {
                'sentiment': sentiment,
                'keywords': json.dumps(keywords),
                'topics': json.dumps(topics),
                'summary': summary,
                'importance_score': importance_score,
                'language': 'zh' if any('\u4e00' <= char <= '\u9fff' for char in text) else 'en',  # 简单语言检测
            }
            
            return analysis_result
            
        except Exception as e:
            log.error(f"内容分析失败: {str(e)}")
            return {} 