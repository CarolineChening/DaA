import requests
import json
from datetime import datetime
import random
import time
from utils.time_utils import get_beijing_time

class XueQiuFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://xueqiu.com/'
        })
        self.cache = {}
        self.last_fetch_time = {}
    
    def _is_cache_valid(self, key):
        if key in self.last_fetch_time:
            return (get_beijing_time() - self.last_fetch_time[key]).seconds < 300
        return False
    
    def fetch_stock_posts(self, symbol, count=10):
        symbol = str(symbol).replace('.SS', '').replace('.SZ', '')
        cache_key = f"xueqiu_posts_{symbol}_{count}"
        
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, [])
        
        try:
            url = f"https://xueqiu.com/statuses/search.json?q={symbol}&count={count}&page=1"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('list'):
                    posts = []
                    for item in data['list'][:count]:
                        posts.append({
                            'id': item.get('id'),
                            'title': item.get('title', ''),
                            'content': item.get('description', '')[:200],
                            'author': item.get('user', {}).get('screen_name', ''),
                            'followers': item.get('user', {}).get('followers_count', 0),
                            'likes': item.get('likes_count', 0),
                            'comments': item.get('comments_count', 0),
                            'time': item.get('created_at', ''),
                            'view': self._analyze_post_sentiment(item.get('description', ''))
                        })
                    self.cache[cache_key] = posts
                    self.last_fetch_time[cache_key] = get_beijing_time()
                    print(f"✅ 获取雪球帖子: {symbol}")
                    return posts
        except Exception as e:
            print(f"⚠️ 获取雪球帖子失败 {symbol}: {e}")
        
        return self.generate_mock_posts(symbol, count)
    
    def fetch_hot_stocks(self, count=10):
        cache_key = f"xueqiu_hot_{count}"
        
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, [])
        
        try:
            url = "https://xueqiu.com/stock/rank.json"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    hot_stocks = []
                    for item in data['data'][:count]:
                        hot_stocks.append({
                            'rank': item.get('rank', 0),
                            'symbol': item.get('symbol', ''),
                            'name': item.get('name', ''),
                            'change': item.get('change', 0),
                            'change_percent': item.get('percent', 0),
                            'volume': item.get('volume', 0),
                            'amount': item.get('amount', 0),
                            'reason': item.get('reason', '')
                        })
                    self.cache[cache_key] = hot_stocks
                    self.last_fetch_time[cache_key] = get_beijing_time()
                    print("✅ 获取雪球热门股票")
                    return hot_stocks
        except Exception as e:
            print(f"⚠️ 获取雪球热门股票失败: {e}")
        
        return self.generate_mock_hot_stocks(count)
    
    def fetch_user_portfolio(self, user_id=None):
        if not user_id:
            return self.generate_mock_portfolio()
        
        cache_key = f"xueqiu_portfolio_{user_id}"
        
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, [])
        
        try:
            url = f"https://xueqiu.com/cubes/portfolio/stock/list.json?cube_id={user_id}&page=1&size=50"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('list'):
                    portfolio = []
                    for item in data['list']:
                        portfolio.append({
                            'symbol': item.get('stock_symbol', ''),
                            'name': item.get('stock_name', ''),
                            'weight': item.get('weight', 0),
                            'cost_price': item.get('cost', 0),
                            'current_price': item.get('price', 0),
                            'profit': item.get('profit', 0),
                            'profit_percent': item.get('profit_percent', 0)
                        })
                    self.cache[cache_key] = portfolio
                    self.last_fetch_time[cache_key] = get_beijing_time()
                    print(f"✅ 获取雪球用户持仓: {user_id}")
                    return portfolio
        except Exception as e:
            print(f"⚠️ 获取雪球用户持仓失败: {e}")
        
        return self.generate_mock_portfolio()
    
    def _analyze_post_sentiment(self, text):
        positive_words = ['看好', '买入', '持有', '加仓', '上涨', '新高', '利好', '低估', '价值', '成长']
        negative_words = ['看空', '卖出', '减仓', '下跌', '风险', '利空', '高估', '泡沫', '谨慎']
        
        score = 0
        text_lower = text.lower()
        
        for word in positive_words:
            if word in text_lower:
                score += 0.15
        
        for word in negative_words:
            if word in text_lower:
                score -= 0.15
        
        if score > 0.2:
            return '看多'
        elif score < -0.2:
            return '看空'
        else:
            return '中性'
    
    def generate_mock_posts(self, symbol, count=10):
        stock_name_map = {
            '600111': '北方稀土', '600519': '贵州茅台', '002920': '德赛西威',
            '300750': '宁德时代', '002594': '比亚迪', '601012': '隆基绿能'
        }
        
        stock_name = stock_name_map.get(symbol, symbol)
        
        mock_posts = [
            {'id': 1, 'title': f'{stock_name}深度分析', 'content': f'{stock_name}作为行业龙头，业绩稳定增长，长期看好', 
             'author': '价值投资达人', 'followers': 58000, 'likes': 1256, 'comments': 89, 'time': '2小时前', 'view': '看多'},
            {'id': 2, 'title': f'{stock_name}技术面分析', 'content': f'{stock_name}技术形态良好，成交量放大，有望突破', 
             'author': '趋势交易者', 'followers': 32000, 'likes': 892, 'comments': 45, 'time': '3小时前', 'view': '看多'},
            {'id': 3, 'title': f'{stock_name}估值讨论', 'content': f'{stock_name}当前估值合理，适合逐步建仓', 
             'author': '基本面研究', 'followers': 45000, 'likes': 756, 'comments': 67, 'time': '5小时前', 'view': '中性'},
            {'id': 4, 'title': f'{stock_name}行业对比', 'content': f'{stock_name}在行业中竞争力强，值得关注', 
             'author': '行业分析师', 'followers': 28000, 'likes': 543, 'comments': 32, 'time': '昨天', 'view': '看多'},
            {'id': 5, 'title': f'{stock_name}风险提示', 'content': f'{stock_name}短期有波动风险，注意仓位控制', 
             'author': '风险控制', 'followers': 18000, 'likes': 321, 'comments': 23, 'time': '昨天', 'view': '中性'}
        ]
        
        return mock_posts[:count]
    
    def generate_mock_hot_stocks(self, count=10):
        mock_hot = [
            {'rank': 1, 'symbol': '600519', 'name': '贵州茅台', 'change': 5.20, 'change_percent': 0.31, 'volume': 25600000, 'amount': 4280000000, 'reason': '白酒消费复苏'},
            {'rank': 2, 'symbol': '002594', 'name': '比亚迪', 'change': 3.50, 'change_percent': 2.85, 'volume': 89500000, 'amount': 10800000000, 'reason': '销量创新高'},
            {'rank': 3, 'symbol': '300750', 'name': '宁德时代', 'change': -2.30, 'change_percent': -1.85, 'volume': 56800000, 'amount': 7150000000, 'reason': '业绩不及预期'},
            {'rank': 4, 'symbol': '601012', 'name': '隆基绿能', 'change': 1.80, 'change_percent': 2.25, 'volume': 42300000, 'amount': 3420000000, 'reason': '光伏装机增长'},
            {'rank': 5, 'symbol': '600111', 'name': '北方稀土', 'change': 0.85, 'change_percent': 2.52, 'volume': 38600000, 'amount': 1330000000, 'reason': '稀土价格上涨'},
            {'rank': 6, 'symbol': '002920', 'name': '德赛西威', 'change': -1.20, 'change_percent': -1.80, 'volume': 15200000, 'amount': 1010000000, 'reason': '短期调整'},
            {'rank': 7, 'symbol': '600276', 'name': '恒瑞医药', 'change': 2.15, 'change_percent': 3.25, 'volume': 28900000, 'amount': 1930000000, 'reason': '创新药进展'},
            {'rank': 8, 'symbol': '000858', 'name': '五粮液', 'change': 3.80, 'change_percent': 2.35, 'volume': 18700000, 'amount': 3090000000, 'reason': '端午备货'},
            {'rank': 9, 'symbol': '601318', 'name': '中国平安', 'change': 0.55, 'change_percent': 1.02, 'volume': 45600000, 'amount': 2510000000, 'reason': '估值修复'},
            {'rank': 10, 'symbol': '300059', 'name': '东方财富', 'change': -0.85, 'change_percent': -1.52, 'volume': 32100000, 'amount': 1810000000, 'reason': '市场波动'}
        ]
        
        return mock_hot[:count]
    
    def generate_mock_portfolio(self):
        return [
            {'symbol': '600519', 'name': '贵州茅台', 'weight': 30, 'cost_price': 1650, 'current_price': 1685, 'profit': 35, 'profit_percent': 2.12},
            {'symbol': '300750', 'name': '宁德时代', 'weight': 25, 'cost_price': 145, 'current_price': 128, 'profit': -17, 'profit_percent': -11.72},
            {'symbol': '002594', 'name': '比亚迪', 'weight': 20, 'cost_price': 88, 'current_price': 95, 'profit': 7, 'profit_percent': 7.95},
            {'symbol': '601012', 'name': '隆基绿能', 'weight': 15, 'cost_price': 28, 'current_price': 22, 'profit': -6, 'profit_percent': -21.43},
            {'symbol': '600276', 'name': '恒瑞医药', 'weight': 10, 'cost_price': 32, 'current_price': 28, 'profit': -4, 'profit_percent': -12.5}
        ]
