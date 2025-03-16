from scrapers.base_scraper import BaseScraper
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json


class XiaohongshuScraper(BaseScraper):
    def __init__(self, platform_name, platform_url):
        super().__init__(platform_name, platform_url, "xiaohongshu")
        # 小红书特定的初始化
        self.headers.update({
            "User-Agent": "特定的小红书UA",
            "Referer": "https://www.xiaohongshu.com"
        })
        # 小红书API端点或URL模板
        self.api_endpoint = "https://www.xiaohongshu.com/api/sns/v10/search/notes"
        # 可能需要的特定参数
        self.cookies = {}

    def scrape_posts(self, *args, **kwargs):
        # 完全重写，使用小红书特定的API或HTML结构
        # 这里不应该复用ForumScraper的逻辑
        pass

    def scrape_replies(self, post_id, *args, **kwargs):
        # 小红书特定的评论抓取逻辑
        pass

    def parse_content(self, raw_content):
        # 小红书特定的内容解析逻辑
        pass


def run_browser_and_parse():
    """运行浏览器并解析内容"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        context = page.context

        print("是否要使用已保存的cookie访问小红书？(y/n)")
        choice = input()

        if choice.lower() == "y":
            with open("xiaohongshu_cookies.json", "r") as f:
                xhs_cookies = json.load(f)
            new_context = browser.new_context()
            new_context.add_cookies(xhs_cookies)
            page = context.new_page()

        # 访问网页
        page.goto("https://www.xiaohongshu.com")
        page.wait_for_load_state("networkidle")

        print("请在浏览器中进行操作（如登录、浏览到目标页面等），之后点击inspector中的继续按钮...")
        page.pause()

        # 截图，记录当前页面状态
        page.screenshot(path="xiaohongshu_after_manual_operation.png")
        print("已完成等待，正在提取页面内容...")

        # 登录后保存Cookie
        if choice.lower() != "y":
            xhs_cookies = page.context.cookies()
            with open("xiaohongshu_cookies.json", "w") as f:
                json.dump(xhs_cookies, f)

        # 方案一：获取HTML并使用BeautifulSoup解析
        html_content = page.content()
        posts_from_bs4 = parse_xiaohongshu_content(html_content)

        try:
            # 或者方案二：直接使用Playwright提取
            posts_from_playwright = extract_with_playwright(page)
        except Exception as e:
            print(f"使用Playwright提取数据时出错: {e}")
            posts_from_playwright = []

        browser.close()

        # 返回解析结果
        return {
            'bs4_results': posts_from_bs4,
            'playwright_results': posts_from_playwright
        }


def parse_xiaohongshu_content(html_content):
    """解析小红书页面内容"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 根据实际HTML结构提取数据
    # 以下选择器需要根据小红书实际HTML结构调整

    # 示例：提取笔记标题
    posts = []
    post_elements = soup.select('div.note-item')  # 假设的选择器

    for post in post_elements:
        title = post.select_one('div.title')
        author = post.select_one('span.author')
        likes = post.select_one('span.likes')

        posts.append({
            'title': title.text.strip() if title else '',
            'author': author.text.strip() if author else '',
            'likes': likes.text.strip() if likes else '',
            # 其他需要的信息
        })

    return posts


def extract_with_playwright(page):
    """使用Playwright从页面中提取数据"""
    # 获取所有笔记元素
    # 注意：选择器需要根据小红书实际DOM结构调整
    posts = []

    # 等待内容加载完成
    page.wait_for_selector('div.note-item')  # 假设的选择器

    # 计算页面上笔记的数量
    post_count = page.evaluate('() => document.querySelectorAll("div.note-item").length')

    for i in range(post_count):
        # 对每个笔记提取信息
        selector_base = f'div.note-item:nth-child({i + 1})'

        # 提取信息（根据实际情况调整选择器）
        title = page.text_content(f'{selector_base} div.title') or ''
        author = page.text_content(f'{selector_base} span.author') or ''
        likes = page.text_content(f'{selector_base} span.likes') or ''

        posts.append({
            'title': title.strip(),
            'author': author.strip(),
            'likes': likes.strip(),
            # 其他需要的信息
        })

    return posts


if __name__ == "__main__":
    # 调用新的函数
    results = run_browser_and_parse()

    # 打印解析结果
    print(f"找到 {len(results['bs4_results'])} 条通过BS4解析的内容")
    print(f"找到 {len(results['playwright_results'])} 条通过Playwright提取的内容")

    # 保存结果到文件(可选)
    with open("xiaohongshu_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("结果已保存到 xiaohongshu_results.json")
