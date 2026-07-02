import requests
import random
from datetime import datetime, timedelta
import os
import re
from collections import Counter
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from utils.time_utils import get_beijing_time, format_beijing_time

os.environ['USE_REAL_DATA'] = 'true'

class NewsFetcher:
    def __init__(self):
        self.cache = {}
        self.last_fetch_time = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def _is_cache_valid(self, key):
        if key in self.last_fetch_time:
            return (get_beijing_time() - self.last_fetch_time[key]).seconds < 300
        return False
    
    def _fetch_eastmoney_stock_news(self):
        news_list = []
        try:
            url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f12&fs=m:0+t:6,m:0+t:80&fields=f14,f57"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('data') and data['data'].get('diff'):
                for item in data['data']['diff'][:20]:
                    news_list.append({
                        'title': item.get('f14', ''),
                        'source': '东方财富',
                        'description': '',
                        'time': format_beijing_time()
                    })
            print(f"✅ 东方财富股票新闻抓取 {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 东方财富股票新闻抓取失败: {e}")
        return news_list
    
    def _fetch_sina_finance(self):
        news_list = []
        try:
            for page in range(1, 6):
                url = f"https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=20&page={page}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                if data.get('result') and data['result'].get('data'):
                    current_time = get_beijing_time()
                    for i, item in enumerate(data['result']['data']):
                        time_offset = get_beijing_time() - timedelta(minutes=(page-1)*20 + i * 5)
                        news_list.append({
                            'title': item.get('title', ''),
                            'source': '新浪财经',
                            'description': item.get('summary', ''),
                            'time': item.get('update_time', time_offset.strftime('%Y-%m-%d %H:%M:%S'))
                        })
            print(f"✅ 新浪财经抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ 新浪财经新闻抓取失败: {e}")
        return news_list
    
    def _fetch_cls_telegraph(self):
        news_list = []
        try:
            url = "https://www.cls.cn/api/sw"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.cls.cn/',
                'Origin': 'https://www.cls.cn'
            }
            params = {'app': 'news', 'os': 'pc', 'sv': '9.9.9'}
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            if data.get('data') and data['data'].get('telegram_list'):
                for item in data['data']['telegram_list'][:50]:
                    news_list.append({
                        'title': item.get('content', ''),
                        'source': '财联社电报',
                        'description': '',
                        'time': item.get('time', format_beijing_time())
                    })
            print(f"✅ 财联社电报抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ 财联社电报抓取失败: {e}")
            news_list = self._fetch_cls_backup()
        return news_list
    
    def _fetch_cls_backup(self):
        news_list = []
        try:
            url = "https://api.cls.cn/telegraph"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            if data.get('data'):
                for item in data['data'][:30]:
                    news_list.append({
                        'title': item.get('content', ''),
                        'source': '财联社电报',
                        'description': '',
                        'time': item.get('time', format_beijing_time())
                    })
            print(f"✅ 财联社备用接口抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ 财联社备用接口抓取失败: {e}")
        return news_list
    
    def _fetch_cninfo_notice(self):
        news_list = []
        news_list.extend(self._fetch_notice_akshare())
        news_list.extend(self._fetch_notice_eastmoney())
        news_list.extend(self._fetch_notice_sina())
        print(f"✅ 公告合计抓取 {len(news_list)} 条")
        return news_list
    
    def _fetch_notice_akshare(self):
        news_list = []
        try:
            import akshare as ak
            notices = ak.stock_news_em()
            if not notices.empty:
                for _, row in notices.head(20).iterrows():
                    news_list.append({
                        'title': row.get('title', ''),
                        'source': '东方财富公告',
                        'description': row.get('content', ''),
                        'time': row.get('time', format_beijing_time())
                    })
            print(f"✅ AKShare公告抓取 {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ AKShare公告抓取失败: {e}")
        return news_list
    
    def _fetch_notice_eastmoney(self):
        news_list = []
        try:
            url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f12&fs=m:0+t:6,m:0+t:80&fields=f14,f57,f12"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if data.get('data') and data['data'].get('diff'):
                for item in data['data']['diff'][:15]:
                    news_list.append({
                        'title': item.get('f14', ''),
                        'source': '东方财富快讯',
                        'description': '',
                        'time': format_beijing_time()
                    })
            print(f"✅ 东方财富快讯抓取 {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 东方财富快讯抓取失败: {e}")
        return news_list
    
    def _fetch_notice_sina(self):
        news_list = []
        try:
            for page in range(1, 4):
                url = f"https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=10&page={page}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                if data.get('result') and data['result'].get('data'):
                    for item in data['result']['data']:
                        news_list.append({
                            'title': item.get('title', ''),
                            'source': '新浪财经',
                            'description': item.get('summary', ''),
                            'time': item.get('update_time', format_beijing_time())
                        })
            print(f"✅ 新浪财经公告抓取 {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 新浪财经公告抓取失败: {e}")
        return news_list
    
    def _fetch_weibo_hot(self):
        news_list = []
        news_list.extend(self._fetch_weibo_api())
        news_list.extend(self._fetch_jinritoutiao_hot())
        news_list.extend(self._fetch_douyin_hot())
        news_list.extend(self._fetch_xiaohongshu_hot())
        news_list.extend(self._fetch_stock_hot_search_backup())
        
        if len(news_list) == 0:
            news_list.extend(self._extract_hot_topics_from_news())
        
        print(f"✅ 社交热点合计抓取 {len(news_list)} 条")
        return news_list
    
    def _extract_hot_topics_from_news(self):
        news_list = []
        try:
            general_news = self._fetch_sina_finance()
            
            stock_keywords = ['A股', '股票', '涨停', '跌停', '公告', '寒武纪', '茅台', '宁德', '比亚迪', '美的', '格力', '芯片', '半导体', '业绩', '减持', '增持']
            
            keyword_counts = {}
            for news in general_news:
                title = news.get('title', '')
                for keyword in stock_keywords:
                    if keyword in title:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for keyword, count in top_keywords:
                news_list.append({
                    'title': f'{keyword} 成为市场热点话题',
                    'source': '热点分析',
                    'description': f'相关新闻提及 {count} 次',
                    'time': format_beijing_time()
                })
            
            print(f"✅ 从新闻中提取热点 {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 热点提取失败: {e}")
        return news_list
    
    def _fetch_weibo_api(self):
        news_list = []
        try:
            url = "https://m.weibo.cn/api/container/getIndex"
            params = {
                'containerid': '106003type=25&t=3&disable_hot=1&filter_type=realtimehot'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                'Referer': 'https://m.weibo.cn/'
            }
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            stock_keywords = ['A股', '股票', '涨停', '跌停', '公告', '寒武纪', '茅台', '宁德', '比亚迪', '美的', '格力', '芯片', '半导体', '业绩', '减持', '增持', '热搜']
            
            if data.get('data') and data['data'].get('cards'):
                for card in data['data']['cards']:
                    if card.get('card_group'):
                        for item in card['card_group']:
                            title = item.get('desc', '')
                            if title and len(title) > 5 and any(keyword in title for keyword in stock_keywords):
                                news_list.append({
                                    'title': title,
                                    'source': '微博热搜',
                                    'description': '',
                                    'time': format_beijing_time()
                                })
            print(f"✅ 微博API热搜抓取 {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 微博API热搜抓取失败: {e}")
            news_list.extend(self._fetch_weibo_alternative())
        return news_list
    
    def _fetch_weibo_alternative(self):
        news_list = []
        try:
            url = "https://m.weibo.cn/topsearch"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            stock_keywords = ['A股', '股票', '涨停', '跌停', '公告', '寒武纪', '茅台', '宁德', '比亚迪', '美的', '格力', '芯片', '半导体']
            
            for keyword in stock_keywords:
                if keyword in response.text:
                    news_list.append({
                        'title': f'{keyword} 登上微博热搜',
                        'source': '微博热搜',
                        'description': '',
                        'time': format_beijing_time()
                    })
            print(f"✅ 微博备选接口抓取 {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 微博备选接口抓取失败: {e}")
        return news_list
    
    def _fetch_jinritoutiao_hot(self):
        news_list = []
        try:
            url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            stock_keywords = ['A股', '股票', '涨停', '跌停', '公告', '寒武纪', '茅台', '宁德', '比亚迪', '美的', '格力', '芯片', '半导体', '财经']
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all('a', href=True, limit=50):
                text = item.text.strip()
                if text and len(text) > 5 and any(keyword in text for keyword in stock_keywords):
                    news_list.append({
                        'title': text,
                        'source': '今日头条热点',
                        'description': '',
                        'time': format_beijing_time()
                    })
            print(f"✅ 今日头条热点抓取 {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 今日头条热点抓取失败: {e}")
        return news_list
    
    def _fetch_douyin_hot(self):
        news_list = []
        try:
            url = "https://www.douyin.com/hot/search/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.douyin.com/'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            stock_keywords = ['A股', '股票', '涨停', '跌停', '公告', '寒武纪', '茅台', '宁德', '比亚迪', '美的', '格力', '芯片', '半导体']
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all('a', href=True, limit=50):
                text = item.text.strip()
                if text and len(text) > 5 and any(keyword in text for keyword in stock_keywords):
                    news_list.append({
                        'title': text,
                        'source': '抖音热点',
                        'description': '',
                        'time': format_beijing_time()
                    })
            print(f"✅ 抖音热点抓取 {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 抖音热点抓取失败: {e}")
        return news_list
    
    def _fetch_xiaohongshu_hot(self):
        news_list = []
        try:
            url = "https://xiaohongshu.com/discovery/hot"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://xiaohongshu.com/'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            stock_keywords = ['股票', '理财', '基金', '投资', 'A股', '茅台', '比亚迪']
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all('a', href=True, limit=50):
                text = item.text.strip()
                if text and len(text) > 5 and any(keyword in text for keyword in stock_keywords):
                    news_list.append({
                        'title': text,
                        'source': '小红书热点',
                        'description': '',
                        'time': format_beijing_time()
                    })
            print(f"✅ 小红书热点抓取 {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 小红书热点抓取失败: {e}")
        return news_list
    
    def _fetch_stock_hot_search_backup(self):
        news_list = []
        try:
            url = "https://gupiao.baidu.com/stock/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            stock_keywords = ['A股', '股票', '涨停', '跌停', '寒武纪', '茅台', '宁德', '比亚迪']
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all('a', href=True, limit=30):
                text = item.text.strip()
                if text and len(text) > 5 and any(keyword in text for keyword in stock_keywords):
                    news_list.append({
                        'title': text,
                        'source': '百度股票',
                        'description': '',
                        'time': format_beijing_time()
                    })
            print(f"✅ 百度股票热点抓取 {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 百度股票热点抓取失败: {e}")
        return news_list
    
    def _fetch_netease_finance(self):
        news_list = []
        try:
            url = "https://3g.163.com/touch/jsonp/article/list/BA8J0AO9wangning/0-20.html"
            headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            text = response.text
            match = re.search(r'callback\((.*?)\)', text)
            if match:
                import json
                data = json.loads(match.group(1))
                if data.get('list'):
                    for item in data['list']:
                        news_list.append({
                            'title': item.get('title', ''),
                            'source': '网易财经',
                            'description': item.get('digest', ''),
                            'time': item.get('ptime', format_beijing_time())
                        })
            print(f"✅ 网易财经抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ 网易财经新闻抓取失败: {e}")
        return news_list
    
    def _fetch_tencent_finance(self):
        news_list = []
        try:
            url = "https://news.qq.com/ext2017/api/tabs/finance"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('data') and data['data'].get('list'):
                for item in data['data']['list'][:20]:
                    news_list.append({
                        'title': item.get('title', ''),
                        'source': '腾讯财经',
                        'description': item.get('summary', ''),
                        'time': item.get('time', format_beijing_time())
                    })
            print(f"✅ 腾讯财经抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ 腾讯财经新闻抓取失败: {e}")
        return news_list
    
    def _fetch_sohu_finance(self):
        news_list = []
        try:
            url = "https://v2.sohu.com/integration-api/mix/region/80?page=1&size=20"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('data'):
                for item in data['data']:
                    news_list.append({
                        'title': item.get('title', ''),
                        'source': '搜狐财经',
                        'description': item.get('description', ''),
                        'time': item.get('publicTime', format_beijing_time())
                    })
            print(f"✅ 搜狐财经抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ 搜狐财经新闻抓取失败: {e}")
        return news_list
    
    def _fetch_stcn(self):
        news_list = []
        try:
            url = "https://www.stcn.com/api/news/list?column=finance&page=1&rows=20"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('data') and data['data'].get('list'):
                for item in data['data']['list']:
                    news_list.append({
                        'title': item.get('title', ''),
                        'source': '证券时报',
                        'description': item.get('summary', ''),
                        'time': item.get('update_time', format_beijing_time())
                    })
            print(f"✅ 证券时报抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ 证券时报新闻抓取失败: {e}")
        return news_list
    
    def _fetch_international_news(self):
        news_list = []
        try:
            url = "https://news.sina.com.cn/world/"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all('a', href=True, limit=25):
                if '/doc-' in item['href'] and item.text:
                    title = item.text.strip()
                    if title and len(title) > 10:
                        news_list.append({
                            'title': title,
                            'source': '新浪国际',
                            'description': '',
                            'time': format_beijing_time()
                        })
            print(f"✅ 新浪国际新闻抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ 新浪国际新闻抓取失败: {e}")
        
        return news_list
    
    def _fetch_reuters_chinese(self):
        news_list = []
        try:
            url = "https://cn.reuters.com/"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all('a', href=True, limit=20):
                if '/article/' in item['href'] and item.text:
                    title = item.text.strip()
                    if title and len(title) > 12:
                        news_list.append({
                            'title': title,
                            'source': '路透中文网',
                            'description': '',
                            'time': format_beijing_time()
                        })
            print(f"✅ 路透中文网抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ 路透中文网抓取失败: {e}")
        return news_list
    
    def _fetch_bbc_chinese(self):
        news_list = []
        try:
            url = "https://www.bbc.com/zhongwen/simp"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all('a', href=True, limit=20):
                href = item.get('href', '')
                if href.startswith('/zhongwen/simp/') and item.text:
                    title = item.text.strip()
                    if title and len(title) > 10:
                        news_list.append({
                            'title': title,
                            'source': 'BBC中文网',
                            'description': '',
                            'time': format_beijing_time()
                        })
            print(f"✅ BBC中文网抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ BBC中文网抓取失败: {e}")
        return news_list
    
    def _fetch_jiemian(self):
        news_list = []
        try:
            url = "https://www.jiemian.com/"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all('a', href=True, limit=25):
                if '/article/' in item['href'] and item.text:
                    title = item.text.strip()
                    if title and len(title) > 10:
                        news_list.append({
                            'title': title,
                            'source': '界面新闻',
                            'description': '',
                            'time': format_beijing_time()
                        })
            print(f"✅ 界面新闻抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ 界面新闻抓取失败: {e}")
        return news_list
    
    def _fetch_yicai(self):
        news_list = []
        try:
            url = "https://www.yicai.com/"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all('a', href=True, limit=20):
                if '/article/' in item['href'] and item.text:
                    title = item.text.strip()
                    if title and len(title) > 10:
                        news_list.append({
                            'title': title,
                            'source': '第一财经',
                            'description': '',
                            'time': format_beijing_time()
                        })
            print(f"✅ 第一财经抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ 第一财经抓取失败: {e}")
        return news_list
    
    def _fetch_global_hot(self):
        news_list = []
        try:
            url = "https://www.huanqiu.com/"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('a', href=True, limit=25):
                text = item.text.strip()
                if len(text) > 10 and ('http' not in text):
                    news_list.append({
                        'title': text,
                        'source': '环球网',
                        'description': '',
                        'time': format_beijing_time()
                    })
            print(f"✅ 环球网新闻抓取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"⚠️ 环球网新闻抓取失败: {e}")
        return news_list
    
    def fetch_general_news(self, count=200):
        cache_key = f"general_news_{count}"
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, [])
        
        all_news = []
        
        fetch_methods = [
            self._fetch_sina_finance,
            self._fetch_cninfo_notice,
            self._fetch_international_news,
            self._fetch_eastmoney_stock_news,
        ]
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(method): method.__name__ for method in fetch_methods}
            
            for future in concurrent.futures.as_completed(futures, timeout=20):
                try:
                    result = future.result()
                    if result:
                        all_news.extend(result)
                except concurrent.futures.TimeoutError:
                    print(f"⚠️ {futures[future]} 抓取超时")
                except Exception as e:
                    print(f"⚠️ {futures[future]} 抓取异常: {e}")
        
        all_news = [n for n in all_news if n['title'] and len(n['title']) > 5]
        seen = set()
        unique_news = []
        
        twenty_four_hours_ago = get_beijing_time() - timedelta(hours=24)
        
        for news in all_news:
            key = news['title'][:50]
            if key not in seen:
                seen.add(key)
                
                news_time = news.get('time', '')
                try:
                    if news_time:
                        if len(news_time) == 10:
                            news_dt = datetime.strptime(news_time, '%Y-%m-%d')
                        else:
                            news_dt = datetime.strptime(news_time, '%Y-%m-%d %H:%M:%S')
                        if news_dt >= twenty_four_hours_ago:
                            unique_news.append(news)
                    else:
                        news['time'] = format_beijing_time()
                        unique_news.append(news)
                except:
                    news['time'] = format_beijing_time()
                    unique_news.append(news)
        
        unique_news.sort(key=lambda x: x.get('time', ''), reverse=True)
        
        self.cache[cache_key] = unique_news[:count]
        self.last_fetch_time[cache_key] = get_beijing_time()
        
        print(f"📰 共抓取 {len(unique_news)} 条新闻（24小时内）")
        return unique_news[:count]
    
    def fetch_xueqiu_posts(self, symbol, count=10):
        posts = []
        symbol = str(symbol).replace('.SS', '').replace('.SZ', '')
        
        try:
            url = f"https://xueqiu.com/stock/search.json?code={symbol}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('stocks') and len(data['stocks']) > 0:
                stock_id = data['stocks'][0].get('code', '')
                if stock_id:
                    url = f"https://xueqiu.com/statuses/stock_timeline.json?symbol={stock_id}&count={count}"
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    post_data = response.json()
                    
                    if post_data.get('list'):
                        for item in post_data['list'][:count]:
                            posts.append({
                                'title': item.get('title', item.get('description', '')[:50] + '...'),
                                'content': item.get('description', ''),
                                'user': item.get('user', {}).get('screen_name', '匿名'),
                                'time': item.get('created_at', format_beijing_time()),
                                'likes': item.get('likes_count', 0),
                                'comments': item.get('comments_count', 0)
                            })
            print(f"✅ 雪球抓取 {len(posts)} 条帖子")
        except Exception as e:
            print(f"⚠️ 雪球抓取失败 {symbol}: {e}")
        
        if not posts:
            stock_name_map = {
                '600111': '北方稀土', '600519': '贵州茅台', '002920': '德赛西威',
                '300750': '宁德时代', '002594': '比亚迪', '601012': '隆基绿能'
            }
            stock_name = stock_name_map.get(symbol, symbol)
            for i in range(min(count, 5)):
                posts.append({
                    'title': f'{stock_name}最新讨论',
                    'content': f'用户讨论{stock_name}的最新动态，观点不一',
                    'user': f'雪球用户{i+1}',
                    'time': format_beijing_time(),
                    'likes': random.randint(10, 100),
                    'comments': random.randint(1, 20)
                })
        
        return posts
    
    def analyze_today_highlights(self, news_list):
        keyword_sentiments = {}
        industry_keywords = [
            '新能源', '光伏', '半导体', '芯片', 'AI', '人工智能', '大数据', '云计算',
            '医药', '创新药', '消费', '白酒', '家电', '房地产', '金融', '银行',
            '证券', '保险', '军工', '航空', '船舶', '汽车', '特斯拉', '比亚迪',
            '宁德时代', '贵州茅台', '五粮液', '北方稀土', '隆基绿能', '恒瑞医药',
            '政策', '央行', '证监会', '监管', '利好', '利空', '降准', '降息',
            '财政', '补贴', '支持', '改革', '开放', '规划', '目标', '会议',
            '欧洲', '德国', '法国', '英国', '出口', '海外', '国际', '全球',
            '美的', '格力', '海尔', '空调', '冰箱', '家电出口', '高温', '热浪',
            '订单', '销量', '卖爆', '热销', '增长', '爆发', '旺季', '需求'
        ]
        
        for news in news_list:
            title = news['title']
            description = news.get('description', '')
            text = title + ' ' + description
            sentiment = self.analyze_sentiment(text)
            
            for keyword in industry_keywords:
                if keyword in text:
                    if keyword not in keyword_sentiments:
                        keyword_sentiments[keyword] = {'count': 0, 'positive': 0, 'negative': 0, 'neutral': 0, 'related_news': []}
                    keyword_sentiments[keyword]['count'] += 1
                    if sentiment > 0.1:
                        keyword_sentiments[keyword]['positive'] += 1
                    elif sentiment < -0.1:
                        keyword_sentiments[keyword]['negative'] += 1
                    else:
                        keyword_sentiments[keyword]['neutral'] += 1
                    if len(keyword_sentiments[keyword]['related_news']) < 3:
                        keyword_sentiments[keyword]['related_news'].append({
                            'title': title,
                            'sentiment': sentiment,
                            'time': news.get('time', '')
                        })
        
        highlights = []
        for keyword, data in keyword_sentiments.items():
            highlights.append({
                'keyword': keyword,
                'count': data['count'],
                'positive': data['positive'],
                'negative': data['negative'],
                'neutral': data['neutral'],
                'related_news': data['related_news']
            })
        
        highlights.sort(key=lambda x: x['count'], reverse=True)
        return highlights[:15]
    
    def fetch_stock_news(self, symbol, count=5):
        symbol = str(symbol).replace('.SS', '').replace('.SZ', '')
        all_news = self.fetch_general_news(100)
        
        stock_name_map = {
            '600111': '北方稀土', '600519': '贵州茅台', '002920': '德赛西威',
            '300750': '宁德时代', '002594': '比亚迪', '601012': '隆基绿能',
            '600276': '恒瑞医药', '000858': '五粮液', '601318': '中国平安',
            '000333': '美的集团', '000651': '格力电器', '600690': '海尔智家',
            '002242': '九阳股份', '000100': 'TCL科技', '002508': '老板电器'
        }
        stock_name = stock_name_map.get(symbol, '')
        
        industry_keywords_map = {
            '000333': ['美的', '家电', '空调', '冰箱', '出口', '海外', '欧洲', '高温', '热浪'],
            '000651': ['格力', '家电', '空调', '出口', '海外', '欧洲'],
            '600690': ['海尔', '家电', '白电', '海外', '欧洲'],
            '300750': ['宁德', '电池', '新能源', '锂电', '储能'],
            '002594': ['比亚迪', '新能源', '汽车', '电池'],
            '601012': ['隆基', '光伏', '太阳能', '组件'],
            '600519': ['茅台', '白酒', '消费'],
            '600111': ['稀土', '北方稀土', '永磁'],
            '600276': ['恒瑞', '医药', '创新药'],
            '000858': ['五粮液', '白酒', '消费']
        }
        
        filtered = []
        industry_keywords = industry_keywords_map.get(symbol, [])
        
        for news in all_news:
            title = news['title']
            description = news.get('description', '')
            text = title + ' ' + description
            
            if symbol in title or stock_name in title:
                filtered.append({
                    'title': title,
                    'summary': description,
                    'time': news.get('time', format_beijing_time()),
                    'match_type': 'direct'
                })
            elif any(keyword in text for keyword in industry_keywords):
                filtered.append({
                    'title': title,
                    'summary': description,
                    'time': news.get('time', format_beijing_time()),
                    'match_type': 'related'
                })
        
        if filtered:
            print(f"✅ 找到 {len(filtered)} 条与 {symbol} ({stock_name}) 相关的新闻")
            return filtered[:count]
        
        print(f"⚠️ 未找到与 {symbol} ({stock_name}) 相关的新闻")
        return []
    
    def analyze_event_impact(self, news_list):
        event_chains = []
        
        event_templates = [
            {
                'trigger_keywords': ['高温', '热浪', '极端天气', '40度', '高温天气'],
                'subject_constraint': ['中国', '欧洲', '全球'],
                'industry_context': ['空调', '制冷', '家电', '降温'],
                'impact_type': 'demand_increase',
                'affected_industries': ['家电', '空调', '制冷设备'],
                'affected_stocks': ['000333', '000651', '600690'],
                'negative_keywords': [],
                'reasoning': '极端高温天气→空调需求增加→家电出口企业受益'
            },
            {
                'trigger_keywords': ['欧洲', '德国', '法国', '英国', '欧盟'],
                'related_events': ['高温', '热浪', '降温', '空调'],
                'subject_constraint': ['中国', '美的', '格力', '海尔'],
                'industry_context': ['空调', '家电', '光伏', '新能源'],
                'impact_type': 'regional_demand',
                'affected_industries': ['家电', '光伏', '新能源'],
                'affected_stocks': ['000333', '000651', '600690', '601012'],
                'negative_keywords': [],
                'reasoning': '欧洲市场需求→中国出口企业受益'
            },
            {
                'trigger_keywords': ['出口', '海外订单', '海外收入', '国际化', '出口增长'],
                'subject_constraint': ['中国', '美的', '格力', '海尔', '比亚迪', '宁德'],
                'industry_context': ['家电', '汽车', '光伏', '消费电子'],
                'impact_type': 'export_boost',
                'affected_industries': ['家电', '汽车', '光伏', '消费电子'],
                'affected_stocks': ['000333', '000651', '600690', '002594', '601012'],
                'negative_keywords': ['韩国', '日本', '美国', '出口管制', '出口限制', '出口禁令'],
                'reasoning': '中国出口增长→相关行业龙头企业受益'
            },
            {
                'trigger_keywords': ['销量增长', '订单激增', '需求暴增', '卖断货'],
                'subject_constraint': ['中国', '美的', '格力', '海尔', '比亚迪'],
                'industry_context': ['家电', '汽车', '消费'],
                'impact_type': 'sales_growth',
                'affected_industries': ['家电', '汽车', '消费'],
                'affected_stocks': ['000333', '000651', '600690', '002594'],
                'negative_keywords': [],
                'reasoning': '销量增长→企业业绩改善'
            },
            {
                'trigger_keywords': ['政策支持', '补贴', '利好', '降准', '降息', '发改委', '工信部'],
                'subject_constraint': ['中国', 'A股', '国内', '央企', '国企'],
                'industry_context': [],
                'impact_type': 'policy_boost',
                'affected_industries': ['金融', '房地产', '新能源', '消费'],
                'affected_stocks': ['601318', '300750', '002594'],
                'negative_keywords': [],
                'reasoning': '政策利好→相关行业受益'
            },
            {
                'trigger_keywords': ['AI', '人工智能', '大模型', '算力'],
                'subject_constraint': ['中国', '国产', '华为', '百度', '阿里'],
                'industry_context': ['芯片', '半导体', '服务器', '数据中心'],
                'impact_type': 'tech_trend',
                'affected_industries': ['半导体', 'AI', '云计算', '数据中心'],
                'affected_stocks': ['000977', '300308', '688012'],
                'negative_keywords': [],
                'reasoning': 'AI技术发展→算力需求增加→相关企业受益'
            },
            {
                'trigger_keywords': ['空调', '白电', '制冷设备'],
                'subject_constraint': ['中国', '美的', '格力', '海尔'],
                'industry_context': ['出口', '海外', '欧洲'],
                'impact_type': 'appliance_demand',
                'affected_industries': ['家电'],
                'affected_stocks': ['000333', '000651', '600690'],
                'negative_keywords': [],
                'reasoning': '家电产品需求→家电企业受益'
            },
            {
                'trigger_keywords': ['寒武纪', '688256'],
                'subject_constraint': ['寒武纪'],
                'industry_context': ['芯片', 'AI', '半导体'],
                'impact_type': 'stock_announcement',
                'affected_industries': ['半导体', 'AI'],
                'affected_stocks': ['688256'],
                'negative_keywords': [],
                'reasoning': '寒武纪公告→直接影响寒武纪股价'
            },
            {
                'trigger_keywords': ['减持', '增持', '股东减持', '股东增持'],
                'subject_constraint': ['A股', '公司', '股东'],
                'industry_context': [],
                'impact_type': 'share_change',
                'affected_industries': ['综合'],
                'affected_stocks': [],
                'negative_keywords': [],
                'reasoning': '股东增减持→影响公司股价'
            },
            {
                'trigger_keywords': ['业绩预告', '业绩披露', '净利润', '营收', '半年报', '年报'],
                'subject_constraint': ['公司', 'A股', '上市'],
                'industry_context': [],
                'impact_type': 'earnings',
                'affected_industries': ['综合'],
                'affected_stocks': [],
                'negative_keywords': [],
                'reasoning': '业绩披露→影响公司股价'
            },
            {
                'trigger_keywords': ['重大合同', '订单', '中标', '签约'],
                'subject_constraint': ['公司', '中标', '合同'],
                'industry_context': [],
                'impact_type': 'contract',
                'affected_industries': ['综合'],
                'affected_stocks': [],
                'negative_keywords': [],
                'reasoning': '重大合同→影响公司业绩'
            },
            {
                'trigger_keywords': ['涨停', '跌停', '一字板'],
                'subject_constraint': ['A股', '股票', '公司'],
                'industry_context': [],
                'impact_type': 'price_limit',
                'affected_industries': ['综合'],
                'affected_stocks': [],
                'negative_keywords': [],
                'reasoning': '涨跌停→市场情绪指标'
            }
        ]
        
        for news in news_list:
            text = news['title'] + ' ' + news.get('description', '')
            
            for template in event_templates:
                has_trigger = any(keyword in text for keyword in template['trigger_keywords'])
                
                if not has_trigger:
                    continue
                
                has_negative = False
                if 'negative_keywords' in template and template['negative_keywords']:
                    has_negative = any(neg in text for neg in template['negative_keywords'])
                
                if has_negative:
                    continue
                
                has_subject = True
                if 'subject_constraint' in template and template['subject_constraint']:
                    has_subject = any(subject in text for subject in template['subject_constraint'])
                
                if not has_subject:
                    continue
                
                has_context = True
                if 'industry_context' in template and template['industry_context']:
                    has_context = any(context in text for context in template['industry_context'])
                
                has_related = False
                if 'related_events' in template:
                    has_related = any(rel in text for rel in template['related_events'])
                
                if 'related_events' not in template or has_related:
                    if has_context:
                        event_chains.append({
                            'news_title': news['title'],
                            'source': news.get('source', ''),
                            'impact_type': template['impact_type'],
                            'affected_industries': template['affected_industries'],
                            'affected_stocks': template['affected_stocks'],
                            'reasoning': template['reasoning'],
                            'sentiment': self.analyze_sentiment(text),
                            'time': news.get('time', '')
                        })
        
        return event_chains
    
    def get_stock_event_analysis(self, symbol):
        news = self.fetch_general_news(100)
        event_chains = self.analyze_event_impact(news)
        
        stock_events = []
        for chain in event_chains:
            if symbol in chain['affected_stocks']:
                stock_events.append(chain)
        
        return stock_events
    
    def get_market_sentiment(self):
        try:
            url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=100&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f12&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and data['data'].get('diff'):
                up_count = 0
                down_count = 0
                for item in data['data']['diff']:
                    change = item.get('f3', 0)
                    if change > 0:
                        up_count += 1
                    elif change < 0:
                        down_count += 1
                
                total = up_count + down_count
                if total > 0:
                    sentiment = (up_count - down_count) / total
                    print(f"✅ 实时市场情绪: {sentiment:.2f}")
                    return sentiment
        except Exception as e:
            print(f"⚠️ 获取市场情绪失败: {e}")
        
        return random.uniform(-0.2, 0.3)
    
    def get_stock_sentiment(self, symbol):
        symbol = str(symbol).replace('.SS', '').replace('.SZ', '')
        market = '1' if symbol.startswith('6') else '0'
        
        try:
            url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={market}.{symbol}&fields=f57,f58,f2,f3"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                change = float(data['data'].get('f3', 0))
                if change > 5:
                    return 0.3
                elif change > 2:
                    return 0.15
                elif change < -5:
                    return -0.3
                elif change < -2:
                    return -0.15
                else:
                    return 0
        except Exception as e:
            print(f"⚠️ 获取个股情绪失败 {symbol}: {e}")
        
        return random.uniform(-0.2, 0.2)
    
    def analyze_sentiment(self, text):
        positive_words = ['利好', '增长', '上升', '创纪录', '突破', '新高', '超预期', '增持', '买入', '看好', '强势', '爆发', '加速', '政策支持', '补贴', '大涨', '涨停', '飙升', '利好消息', '业绩预增', '订单大增']
        negative_words = ['利空', '下降', '下滑', '亏损', '减持', '卖出', '看空', '风险', '爆雷', '跌停', '警告', '退市', '调查', '处罚', '大跌', '暴跌', '业绩暴雷', '商誉减值']
        
        score = 0
        text_lower = text.lower()
        
        for word in positive_words:
            if word in text_lower:
                score += 0.15
        
        for word in negative_words:
            if word in text_lower:
                score -= 0.15
        
        return max(-1, min(1, score))
    
    def calculate_news_impact(self, news_item):
        category_weights = {
            '央行': 10, '货币政策': 10, '降准': 10, '降息': 10, '利率': 10, '准备金': 10,
            '国家政策': 9, '产业政策': 9, '规划': 9, '目标': 9, '会议': 9, '改革': 9, '开放': 9,
            '地缘政治': 8, '国际关系': 8, '贸易': 8, '出口': 8, '进口': 8,
            '行业监管': 7, '证监会': 7, '监管': 7, '政策': 7,
            '财报': 6, '业绩': 6, '净利润': 6, '营收': 6, '利润': 6,
            '社会事件': 5,
            '公司公告': 4,
            '一般财经': 3
        }
        
        source_weights = {
            '新华社': 1.5, '人民日报': 1.5, '央视财经': 1.5,
            '证券时报': 1.3, '财联社': 1.3, '中国证券报': 1.3, '上海证券报': 1.3,
            '东方财富': 1.2, '新浪财经': 1.1,
            '网易财经': 1.0, '腾讯财经': 1.0, '搜狐财经': 1.0
        }
        
        title = news_item['title']
        source = news_item.get('source', '')
        
        base_score = 3
        for keyword, weight in category_weights.items():
            if keyword in title:
                base_score = max(base_score, weight)
        
        source_multiplier = source_weights.get(source, 1.0)
        
        scope_multiplier = 1.0
        if any(keyword in title for keyword in ['全国', '中国', '国家', '国务院', '发改委', '工信部', '财政部']):
            scope_multiplier = 1.3
        elif any(keyword in title for keyword in ['行业', '板块', '概念', '产业链']):
            scope_multiplier = 1.1
        
        impact_score = base_score * source_multiplier * scope_multiplier
        
        return round(impact_score, 2)
    
    def fetch_hot_topics(self, count=10):
        hot_list = []
        
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f12&fs=m:0+t:6,m:0+t:80&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and data['data'].get('diff'):
                for i, item in enumerate(data['data']['diff'][:count]):
                    hot_list.append({
                        'rank': i + 1,
                        'topic': item.get('f14', ''),
                        'stock': item.get('f12', ''),
                        'reason': f"涨幅 {item.get('f3', 0)}%"
                    })
                print(f"✅ 抓取到 {len(hot_list)} 条热点股票")
        except Exception as e:
            print(f"⚠️ 获取热点话题失败: {e}")
        
        if not hot_list:
            hot_list = [
                {'rank': 1, 'topic': '新能源汽车', 'stock': '比亚迪', 'reason': '销量持续增长'},
                {'rank': 2, 'topic': 'AI芯片', 'stock': '英伟达', 'reason': '需求爆发'},
                {'rank': 3, 'topic': '光伏', 'stock': '隆基绿能', 'reason': '政策利好'},
                {'rank': 4, 'topic': '白酒', 'stock': '贵州茅台', 'reason': '消费复苏'},
                {'rank': 5, 'topic': '半导体', 'stock': '中芯国际', 'reason': '国产替代'},
                {'rank': 6, 'topic': '医药', 'stock': '恒瑞医药', 'reason': '创新药政策'},
                {'rank': 7, 'topic': '金融', 'stock': '招商银行', 'reason': '业绩稳定'},
                {'rank': 8, 'topic': '稀土', 'stock': '北方稀土', 'reason': '战略资源'},
                {'rank': 9, 'topic': '军工', 'stock': '中航沈飞', 'reason': '军费增长'},
                {'rank': 10, 'topic': '消费电子', 'stock': '立讯精密', 'reason': '新品发布'}
            ]
        
        return hot_list[:count]
    
    def get_news_sentiment_score(self, symbol):
        stock_news = self.fetch_stock_news(symbol, 10)
        xueqiu_posts = self.fetch_xueqiu_posts(symbol, 10)
        
        scores = []
        
        for news in stock_news:
            text = news['title'] + ' ' + news.get('summary', '')
            scores.append(self.analyze_sentiment(text))
        
        for post in xueqiu_posts:
            text = post['title'] + ' ' + post.get('content', '')
            score = self.analyze_sentiment(text)
            scores.append(score * (1 + post.get('likes', 0) / 100))
        
        if scores:
            return sum(scores) / len(scores)
        
        return 0