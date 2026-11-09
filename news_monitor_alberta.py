import feedparser
import requests
from datetime import datetime

# ==================== 配置区域 ====================
# 1. 你想要监控的 RSS 订阅源列表（这里以 Google 新闻中文版、IT之家为例）
Old_RSS_URLS = [
    "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-CN",
    "https://www.ithome.com/rss/",  # 科技数码类 RSS 示例
]

RSS_URLS = [
    # Global News
    "https://globalnews.ca/calgary/feed/",
    "https://globalnews.ca/edmonton/feed/",

    # CTV News
    "https://calgary.ctvnews.ca/rss/ctv-news-calgary-1.822341",
    "https://edmonton.ctvnews.ca/rss/ctv-news-edmonton-1.822347",

    # Calgary Herald / Edmonton Journal
    "https://calgaryherald.com/feed/",
    "https://edmontonjournal.com/feed/",

    # Calgary Sun / Edmonton Sun
    "https://calgarysun.com/feed",
    "https://edmontonsun.com/feed",
    
    "https://www.cbc.ca/webfeed/rss/rss-topstories",
    "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/canada/",
    "https://nationalpost.com/feed",
    #"https://www.ctvnews.ca/rss/ctvnews-ca-top-stories-public-rss-1.822009",
    #"https://globalnews.ca/feed/",
    #"https://financialpost.com/feed",
    #"https://www.thestar.com/search/?f=rss&t=article&l=50&s=start_time&sd=desc",
    #"https://edmontonjournal.com/feed",
    #"https://vancouversun.com/feed",
    #"https://macleans.ca/feed/",
]

# 2. 你的过滤关键字（只要标题或摘要包含其中任意一个就会被选中）
KEYWORDS = [
    "China", "Chinese", "chinatown", "china town",
    "immigration", "immigrant", "immigrants",
    "University of Alberta", "UAlberta", "uofa", 
    ]

# 3. PushPlus 的 Token（填入你在 pushplus.plus 获取的 Token）
PUSHPLUS_TOKEN = "39ffbb4223ef4cbab12e7d7897f573c4"
# ==================================================

def fetch_and_filter_news():
    """抓取 RSS 并根据关键字过滤"""
    matched_news = []
    seen_links = set()  # 用于去重
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%Sing')}] 开始抓取新闻...")

    for url in RSS_URLS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                link = entry.get('link', '')
                
                # 去重校验
                if link in seen_links:
                    continue
                
                # 检查是否包含任何关键字
                for kw in KEYWORDS:
                    if kw in title or kw in summary:
                        matched_news.append({
                            'title': title,
                            'link': link,
                            'published': entry.get('published', '近期'),
                            'keyword': kw
                        })
                        seen_links.add(link)
                        break  # 匹配到一个关键字即跳出内循环
        except Exception as e:
            print(f"解析 RSS 出错 ({url}): {e}")

    return matched_news

def old_send_wechat_notification(news_list):
    """通过 PushPlus 将新闻 Markdown 格式推送到微信"""
    if not news_list:
        print("今天没有发现包含关键字的新闻。")
        return
    
    # 组装 Markdown 内容
    content = f"### 📌 关键字新闻提醒 ({datetime.now().strftime('%m-%d %H:%M')})\n\n"
    for idx, item in enumerate(news_list, 1):
        content += f"{idx}. **[{item['keyword']}]** [{item['title']}]({item['link']})\n\n"
    
    payload = {
        "token": PUSHPLUS_TOKEN,
        "title": f"今日alberta新闻监控：命中 {len(len(news_list) if isinstance(news_list, list) else news_list)} 条", # 修正长度计算
        "content": content,
        "template": "markdown"
    }
    
    # 修正推送标题中的长度计算
    payload["title"] = f"今日alberta新闻监控：命中 {len(news_list)} 条"

    try:
        response = requests.post("http://www.pushplus.plus/send", json=payload)
        result = response.json()
        if result.get("code") == 200:
            print("🎉 微信推送成功！")
        else:
            print(f"❌ 推送失败: {result.get('msg')}")
    except Exception as e:
        print(f"❌ 网络请求异常: {e}")

def send_wechat_notification(news_list):
    """通过 PushPlus 将新闻 Markdown 格式推送到微信"""
    if not news_list:
        print("今天没有发现包含关键字的新闻。")
        return
    
    # 组装 Markdown 内容
    content = f"### 📌 关键字新闻提醒 ({datetime.now().strftime('%m-%d %H:%M')})\n\n"
    for idx, item in enumerate(news_list, 1):
        content += f"{idx}. **[{item['keyword']}]** [{item['title']}]({item['link']})\n\n"
    
    # 修复这里的标题长度计算（直接用 len(news_list) 即可）
    payload = {
        "token": PUSHPLUS_TOKEN,
        "title": f"今日alberta新闻监控：命中 {len(news_list)} 条",
        "content": content,
        "template": "markdown"
    }

    try:
        response = requests.post("http://www.pushplus.plus/send", json=payload)
        result = response.json()
        if result.get("code") == 200:
            print("🎉 微信推送成功！")
        else:
            print(f"❌ 推送失败: {result.get('msg')}")
    except Exception as e:
        print(f"❌ 网络请求异常: {e}")

if __name__ == "__main__":
    news = fetch_and_filter_news()
    print(f"共筛选出 {len(news)} 条符合条件的新闻。")
    send_wechat_notification(news)
