# AI-RPA爬虫项目

这是一个用Python实现的RPA爬虫项目，专门用于收集各个社区、论坛、Discord的帖子、用户回复等信息，然后通过AI分析，挖掘高价值的用户内容。

## 项目结构

```
ai-rpa/
├── analyzers/            # AI分析模块
├── config/               # 配置文件
├── processors/           # 数据处理模块
├── scrapers/             # 爬虫模块
│   └── platforms/        # 各平台爬虫实现
├── storage/              # 数据存储模块
│   └── data/             # 存储数据
├── utils/                # 工具函数
├── main.py               # 主程序入口
├── requirements.txt      # 依赖库
└── README.md             # 项目说明
```

## 功能特点

- **模块化设计**：各个功能模块独立，易于扩展和维护
- **多平台支持**：可以轻松添加新的平台爬虫
- **数据标准化**：统一的数据模型和处理流程
- **AI分析**：使用NLP技术对内容进行分析
- **灵活存储**：支持SQLite、MySQL和MongoDB多种存储方式

## 使用方法

### 安装依赖

```bash
pip install -r requirements.txt
```

### 初始化环境

首次运行前，需要初始化环境变量：

```bash
cp .env.example .env
```

然后编辑`.env`文件，设置相关配置。

### 注册平台

```bash
python main.py --register --name "平台名称" --url "平台URL" --type "forum"
```

### 运行爬虫

```bash
# 抓取所有注册的平台
python main.py

# 抓取指定平台
python main.py --platform "平台名称"

# 抓取多个页面
python main.py --platform "平台名称" --pages 5

# 抓取但不执行分析
python main.py --no-analysis
```

## 扩展平台

要添加新的平台支持，需要在`scrapers/platforms/`目录下创建新的爬虫类，并继承`BaseScraper`基类：

```python
from scrapers.base_scraper import BaseScraper

class MyNewScraper(BaseScraper):
    def __init__(self, platform_name, platform_url):
        super().__init__(platform_name, platform_url, "my_platform_type")
        # 平台特定的初始化代码
    
    def scrape_posts(self, *args, **kwargs):
        # 实现抓取帖子的逻辑
        pass
        
    def scrape_replies(self, post_id, *args, **kwargs):
        # 实现抓取回复的逻辑
        pass
        
    def parse_content(self, raw_content):
        # 实现内容解析逻辑
        pass
```

## 许可证

MIT