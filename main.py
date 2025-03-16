"""
AI-RPA爬虫项目主入口
"""
import os
import sys
import argparse
from datetime import datetime
from sqlalchemy.orm import sessionmaker

from utils.logger import log
from storage.database import db_manager
from storage.models import init_db, Platform, Content, ContentAnalysis
from processors.content_processor import ContentProcessor
from analyzers.content_analyzer import ContentAnalyzer
from scrapers.platforms.forum_scraper import ForumScraper
from scrapers.platforms.xhs_scraper import XiaohongshuScraper


class RpaApp:
    """
    RPA应用主类
    """

    def __init__(self):
        """初始化应用"""
        self.db_engine = None
        self.session = None
        self.processor = ContentProcessor()
        self.analyzer = ContentAnalyzer()
        self.scrapers = {}

    def initialize(self):
        """初始化应用环境"""
        try:
            # 初始化数据库
            self.db_engine = init_db()
            if self.db_engine:
                Session = sessionmaker(bind=self.db_engine)
                self.session = Session()

            log.info("应用初始化完成")
            return True

        except Exception as e:
            log.error(f"应用初始化失败: {str(e)}")
            return False

    def register_platform(self, name: str, website: str, platform_type: str):
        """
        注册平台
        
        Args:
            name: 平台名称
            website: 平台网址
            platform_type: 平台类型
        """
        try:
            # 检查平台是否已存在
            platform = self.session.query(Platform).filter_by(name=name).first()

            if not platform:
                # 创建新平台
                platform = Platform(
                    name=name,
                    website=website,
                    type=platform_type
                )
                self.session.add(platform)
                self.session.commit()
                log.info(f"注册平台成功: {name}")

            # 初始化对应的爬虫
            if platform_type == "forum":
                scraper = ForumScraper(name, website)
                self.scrapers[name] = scraper
                log.info(f"初始化爬虫: {name}")
            elif platform_type == "xiaohongshu":  # 添加这个条件分支
                scraper = XiaohongshuScraper(name, website)
                self.scrapers[name] = scraper

            return platform

        except Exception as e:
            log.error(f"注册平台失败: {str(e)}")
            self.session.rollback()
            return None

    def scrape_platform(self, platform_name: str, max_pages: int = 1):
        """
        抓取平台内容
        
        Args:
            platform_name: 平台名称
            max_pages: 最大页数
        """
        scraper = self.scrapers.get(platform_name)
        if not scraper:
            log.error(f"找不到平台爬虫: {platform_name}")
            return

        platform = self.session.query(Platform).filter_by(name=platform_name).first()
        if not platform:
            log.error(f"找不到平台: {platform_name}")
            return

        try:
            # 抓取帖子
            log.info(f"开始抓取平台: {platform_name}")
            posts = scraper.scrape_posts(max_pages=max_pages)

            if not posts:
                log.warning(f"未抓取到帖子: {platform_name}")
                return

            log.info(f"抓取到 {len(posts)} 个帖子")

            # 处理帖子
            for post_data in posts:
                # 抓取完整帖子内容
                post_id = post_data.get('content_id')
                full_post = scraper.scrape_post_content(post_id)

                if not full_post:
                    log.warning(f"抓取帖子内容失败: {post_id}")
                    continue

                # 处理帖子内容
                processed_post = self.processor.process_content(full_post)

                # 保存到数据库
                self.save_content(platform.id, processed_post)

                # 抓取回复
                replies = scraper.scrape_replies(post_id, max_pages=max_pages)

                if replies:
                    log.info(f"抓取到 {len(replies)} 个回复")

                    # 处理回复
                    processed_replies = self.processor.process_batch(replies)

                    # 保存回复
                    for reply in processed_replies:
                        self.save_content(platform.id, reply)

            log.info(f"平台 {platform_name} 抓取完成")

        except Exception as e:
            log.error(f"抓取平台失败: {str(e)}")
        finally:
            scraper.close()

    def save_content(self, platform_id: int, content_data: dict):
        """
        保存内容到数据库
        
        Args:
            platform_id: 平台ID
            content_data: 内容数据
        """
        try:
            # 检查内容是否已存在
            content_id = content_data.get('content_id')
            existing = self.session.query(Content).filter_by(
                platform_id=platform_id,
                content_id=content_id
            ).first()

            if existing:
                log.info(f"内容已存在: {content_id}")
                return existing

            # 创建内容记录
            parent_id = None
            if content_data.get('parent_id'):
                # 查找父内容
                parent = self.session.query(Content).filter_by(
                    platform_id=platform_id,
                    content_id=content_data.get('parent_id')
                ).first()

                if parent:
                    parent_id = parent.id

            content = Content(
                platform_id=platform_id,
                content_id=content_data.get('content_id'),
                url=content_data.get('url', ''),
                title=content_data.get('title', ''),
                content=content_data.get('content', ''),
                author=content_data.get('author', ''),
                author_id=content_data.get('author_id', ''),
                parent_id=parent_id,
                created_time=content_data.get('created_time'),
                content_type=content_data.get('content_type', 'post'),
                processed=True,
                analyzed=False
            )

            self.session.add(content)
            self.session.commit()
            log.info(f"保存内容成功: {content_id}")

            return content

        except Exception as e:
            log.error(f"保存内容失败: {str(e)}")
            self.session.rollback()
            return None

    def analyze_contents(self, limit: int = 10):
        """
        分析未分析的内容
        
        Args:
            limit: 最大分析数量
        """
        try:
            # 查询未分析的内容
            contents = self.session.query(Content).filter_by(analyzed=False).limit(limit).all()

            if not contents:
                log.info("没有需要分析的内容")
                return

            log.info(f"开始分析 {len(contents)} 个内容")

            for content in contents:
                # 分析内容
                content_data = {
                    'content_id': content.content_id,
                    'title': content.title,
                    'content': content.content,
                    'author': content.author,
                    'content_type': content.content_type,
                    'replies_count': len(content.replies) if content.replies else 0
                }

                analysis_result = self.analyzer.analyze_content(content_data)

                if not analysis_result:
                    log.warning(f"内容分析失败: {content.content_id}")
                    continue

                # 保存分析结果
                analysis = ContentAnalysis(
                    content_id=content.id,
                    sentiment=analysis_result.get('sentiment'),
                    topics=analysis_result.get('topics'),
                    keywords=analysis_result.get('keywords'),
                    summary=analysis_result.get('summary'),
                    importance_score=analysis_result.get('importance_score'),
                    language=analysis_result.get('language')
                )

                self.session.add(analysis)

                # 更新内容分析状态
                content.analyzed = True

                self.session.commit()
                log.info(f"内容分析完成: {content.content_id}")

            log.info("内容分析完成")

        except Exception as e:
            log.error(f"分析内容失败: {str(e)}")
            self.session.rollback()

    def run(self, platform_names: list = None, max_pages: int = 1, analyze: bool = True):
        """
        运行应用
        
        Args:
            platform_names: 平台名称列表，为空则抓取所有平台
            max_pages: 最大页数
            analyze: 是否分析内容
        """
        if not self.initialize():
            return

        try:
            if not platform_names:
                # 获取所有平台
                platforms = self.session.query(Platform).all()
                platform_names = [p.name for p in platforms]

            # 抓取指定平台
            for name in platform_names:
                self.scrape_platform(name, max_pages)

            # 分析内容
            if analyze:
                self.analyze_contents()

        except Exception as e:
            log.error(f"运行应用失败: {str(e)}")
        finally:
            if self.session:
                self.session.close()

            db_manager.close()
            log.info("应用运行结束")


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='AI-RPA爬虫')
    parser.add_argument('--platform', '-p', type=str,
                        help='指定要抓取的平台名称，多个平台用逗号分隔')
    parser.add_argument('--pages', type=int, default=1,
                        help='抓取的最大页数')
    parser.add_argument('--no-analysis', action='store_true',
                        help='不执行内容分析')
    parser.add_argument('--register', action='store_true',
                        help='注册新平台')
    parser.add_argument('--name', type=str,
                        help='平台名称')
    parser.add_argument('--url', type=str,
                        help='平台URL')
    parser.add_argument('--type', type=str, default='forum',
                        help='平台类型')

    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()

    app = RpaApp()

    if args.register:
        if not args.name or not args.url:
            print("注册平台需要提供名称和URL")
            return

        app.initialize()
        app.register_platform(args.name, args.url, args.type)
    else:
        platforms = None
        if args.platform:
            platforms = [p.strip() for p in args.platform.split(',')]

        app.run(
            platform_names=platforms,
            max_pages=args.pages,
            analyze=not args.no_analysis
        )


if __name__ == "__main__":
    main()
