import requests
import pandas as pd
from datetime import datetime
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from utils.time_utils import get_beijing_time
from data.news_fetcher import NewsFetcher

class DynamicWatchlist:
    def __init__(self):
        self.cache = {}
        self.last_fetch_time = {}
    
    def _fetch_dragon_tiger_list(self):
        stocks = []
        try:
            url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=30&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f12&fs=m:0+t:6,m:0+t:80&fields=f12,f14,f2,f3,f62,f184,f204,f205,f124,f108,f116"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and data['data'].get('diff'):
                for item in data['data']['diff'][:15]:
                    stocks.append({
                        'symbol': item.get('f12', ''),
                        'name': item.get('f14', ''),
                        'type': '龙虎榜热门',
                        'reason': f"涨幅 {item.get('f3', 0)}%"
                    })
            print(f"✅ 抓取龙虎榜 {len(stocks)} 只股票")
        except Exception as e:
            print(f"⚠️ 龙虎榜抓取失败: {e}")
        
        return stocks
    
    def _fetch_top_gainers(self):
        stocks = []
        try:
            url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f12,f14,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and data['data'].get('diff'):
                for item in data['data']['diff'][:10]:
                    stocks.append({
                        'symbol': item.get('f12', ''),
                        'name': item.get('f14', ''),
                        'type': '涨幅榜',
                        'reason': f"涨幅 {item.get('f3', 0)}%"
                    })
            print(f"✅ 抓取涨幅榜 {len(stocks)} 只股票")
        except Exception as e:
            print(f"⚠️ 涨幅榜抓取失败: {e}")
        
        return stocks
    
    def _fetch_top_volume(self):
        stocks = []
        try:
            url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f57&fs=m:0+t:6,m:0+t:80&fields=f12,f14,f2,f3,f57,f58,f59,f60,f61"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and data['data'].get('diff'):
                for item in data['data']['diff'][:10]:
                    stocks.append({
                        'symbol': item.get('f12', ''),
                        'name': item.get('f14', ''),
                        'type': '成交量榜',
                        'reason': '高成交量'
                    })
            print(f"✅ 抓取成交量榜 {len(stocks)} 只股票")
        except Exception as e:
            print(f"⚠️ 成交量榜抓取失败: {e}")
        
        return stocks
    
    def _fetch_hot_concept(self):
        stocks = []
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=b:BK1003,b:BK1002,b:BK1006,b:BK1005,b:BK1004&fields=f12,f14,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and data['data'].get('diff'):
                for item in data['data']['diff'][:10]:
                    stocks.append({
                        'symbol': item.get('f12', ''),
                        'name': item.get('f14', ''),
                        'type': '热点概念',
                        'reason': f"涨幅 {item.get('f3', 0)}%"
                    })
            print(f"✅ 抓取热点概念 {len(stocks)} 只股票")
        except Exception as e:
            print(f"⚠️ 热点概念抓取失败: {e}")
        
        return stocks
    
    def _fetch_event_stocks(self):
        stocks = []
        stock_name_map = {
            '000333': '美的集团', '000651': '格力电器', '600690': '海尔智家',
            '300750': '宁德时代', '002594': '比亚迪', '601012': '隆基绿能',
            '600519': '贵州茅台', '000858': '五粮液', '600111': '北方稀土',
            '600276': '恒瑞医药', '601318': '中国平安', '000977': '浪潮信息',
            '300308': '中际旭创', '688012': '中芯国际', '688256': '寒武纪',
            '300364': '中文在线', '002261': '拓维信息', '300474': '景嘉微',
            '000100': 'TCL科技', '000725': '京东方A', '002920': '德赛西威',
            '600584': '长电科技', '603986': '兆易创新', '002407': '多氟多'
        }
        
        try:
            news_fetcher = NewsFetcher()
            news_list = news_fetcher.fetch_general_news(50)
            event_chains = news_fetcher.analyze_event_impact(news_list)
            
            for chain in event_chains:
                for symbol in chain.get('affected_stocks', []):
                    if symbol in stock_name_map and symbol not in [s['symbol'] for s in stocks]:
                        stocks.append({
                            'symbol': symbol,
                            'name': stock_name_map[symbol],
                            'type': '产业链潜力股',
                            'reason': chain.get('reasoning', '')
                        })
            
            highlights = news_fetcher.analyze_today_highlights(news_list)
            for highlight in highlights[:10]:
                keyword = highlight['keyword']
                concept_stocks = {
                    '新能源': ['300750', '002594', '601012'],
                    '光伏': ['601012', '300274', '600438'],
                    '半导体': ['688012', '600584', '603986'],
                    '芯片': ['688256', '300474', '603986'],
                    'AI': ['000977', '300308', '688256'],
                    '人工智能': ['000977', '300308', '688256'],
                    '大数据': ['000977', '300222', '300104'],
                    '云计算': ['000977', '300339', '002335'],
                    '医药': ['600276', '300760', '002437'],
                    '创新药': ['600276', '300760', '300122'],
                    '消费': ['600519', '000858', '000333'],
                    '白酒': ['600519', '000858', '000568'],
                    '家电': ['000333', '000651', '600690'],
                    '房地产': ['000002', '600048', '000858'],
                    '金融': ['601318', '601988', '600036'],
                    '银行': ['601318', '601988', '600036'],
                    '证券': ['600030', '601211', '000776'],
                    '保险': ['601318', '601628', '601336'],
                    '军工': ['600893', '000768', '300034'],
                    '汽车': ['002594', '002920', '601633'],
                    '特斯拉': ['002594', '300750', '002460'],
                    '出口': ['000333', '000651', '600690'],
                    '海外': ['000333', '000651', '600690'],
                    '欧洲': ['000333', '000651', '600690'],
                    '高温': ['000333', '000651', '600690'],
                    '热浪': ['000333', '000651', '600690'],
                    '订单': ['000333', '002594', '601012'],
                    '销量': ['000333', '002594', '600519'],
                    '增长': ['000333', '002594', '600519'],
                    '政策': ['601318', '300750', '002594'],
                    '央行': ['601318', '601988', '600036'],
                    '利好': ['300750', '002594', '600519'],
                    '降准': ['601318', '601988', '600036'],
                    '降息': ['601318', '601988', '600036'],
                    '财政': ['601318', '600036', '000002'],
                    '补贴': ['300750', '002594', '601012'],
                    '支持': ['300750', '002594', '601012'],
                    '改革': ['601318', '000002', '600036'],
                    '规划': ['300750', '002594', '601012'],
                    '会议': ['601318', '300750', '002594'],
                    '微短剧': ['300364', '002261', '300588'],
                    '短剧': ['300364', '002261', '300588'],
                    'CPO': ['300308', '002475', '603055'],
                    '光模块': ['300308', '002475', '603055'],
                    '机器人': ['300024', '600893', '002527'],
                    '稀土': ['600111', '000831', '600392'],
                    '储能': ['300750', '300274', '002121'],
                    '锂电': ['300750', '002460', '002407'],
                    '消费电子': ['000100', '000725', '002456']
                }
                
                if keyword in concept_stocks:
                    for symbol in concept_stocks[keyword]:
                        if symbol in stock_name_map and symbol not in [s['symbol'] for s in stocks]:
                            stocks.append({
                                'symbol': symbol,
                                'name': stock_name_map[symbol],
                                'type': '产业链潜力股',
                                'reason': f"{keyword}概念受关注"
                            })
            
            print(f"✅ 基于新闻事件选股 {len(stocks)} 只股票")
        except Exception as e:
            print(f"⚠️ 新闻事件选股失败: {e}")
        
        return stocks
    
    def _is_cache_valid(self, key):
        if key in self.last_fetch_time:
            return (get_beijing_time() - self.last_fetch_time[key]).seconds < 300
        return False
    
    def get_dynamic_watchlist(self):
        cache_key = "dynamic_watchlist"
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, [])
        
        all_stocks = []
        
        fetch_methods = [
            self._fetch_dragon_tiger_list,
            self._fetch_top_gainers,
            self._fetch_top_volume,
            self._fetch_hot_concept,
            self._fetch_event_stocks,
        ]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(method): method.__name__ for method in fetch_methods}
            
            for future in concurrent.futures.as_completed(futures, timeout=25):
                try:
                    result = future.result()
                    if result:
                        all_stocks.extend(result)
                except concurrent.futures.TimeoutError:
                    print(f"⚠️ {futures[future]} 抓取超时")
                except Exception as e:
                    print(f"⚠️ {futures[future]} 抓取异常: {e}")
        
        seen = set()
        unique_stocks = []
        for stock in all_stocks:
            if stock['symbol'] not in seen and stock['symbol']:
                seen.add(stock['symbol'])
                unique_stocks.append(stock)
        
        default_stocks = [
            {'symbol': '600519', 'name': '贵州茅台', 'type': '权重股', 'reason': '贵州茅台', 'industry': '食品饮料'},
            {'symbol': '000858', 'name': '五粮液', 'type': '权重股', 'reason': '五粮液', 'industry': '食品饮料'},
            {'symbol': '300750', 'name': '宁德时代', 'type': '权重股', 'reason': '宁德时代', 'industry': '电力设备'},
            {'symbol': '002594', 'name': '比亚迪', 'type': '权重股', 'reason': '比亚迪', 'industry': '汽车'},
            {'symbol': '000333', 'name': '美的集团', 'type': '权重股', 'reason': '家电龙头', 'industry': '家用电器'},
            {'symbol': '000651', 'name': '格力电器', 'type': '权重股', 'reason': '家电龙头', 'industry': '家用电器'},
            {'symbol': '600690', 'name': '海尔智家', 'type': '权重股', 'reason': '家电龙头', 'industry': '家用电器'},
            {'symbol': '300364', 'name': '中文在线', 'type': '热点概念', 'reason': '微短剧概念龙头', 'industry': '文化传媒'},
            {'symbol': '002261', 'name': '拓维信息', 'type': '热点概念', 'reason': '人工智能概念', 'industry': '计算机'},
            {'symbol': '300308', 'name': '中际旭创', 'type': '热点概念', 'reason': 'CPO光模块龙头', 'industry': '通信'},
            {'symbol': '688256', 'name': '寒武纪', 'type': '热点概念', 'reason': 'AI芯片龙头', 'industry': '半导体'},
            {'symbol': '300024', 'name': '机器人', 'type': '热点概念', 'reason': '机器人概念', 'industry': '机械设备'},
            {'symbol': '300474', 'name': '景嘉微', 'type': '热点概念', 'reason': 'GPU芯片', 'industry': '半导体'},
            {'symbol': '600111', 'name': '北方稀土', 'type': '权重股', 'reason': '稀土龙头', 'industry': '有色金属'},
            {'symbol': '002920', 'name': '德赛西威', 'type': '权重股', 'reason': '汽车电子', 'industry': '汽车'},
            {'symbol': '000977', 'name': '浪潮信息', 'type': '热点概念', 'reason': 'AI服务器龙头', 'industry': '计算机'},
            {'symbol': '688012', 'name': '中芯国际', 'type': '权重股', 'reason': '芯片制造龙头', 'industry': '半导体'},
            {'symbol': '601012', 'name': '隆基绿能', 'type': '权重股', 'reason': '光伏龙头', 'industry': '电力设备'},
            {'symbol': '600276', 'name': '恒瑞医药', 'type': '权重股', 'reason': '创新药龙头', 'industry': '医药生物'},
            {'symbol': '601318', 'name': '中国平安', 'type': '权重股', 'reason': '保险龙头', 'industry': '非银金融'},
            {'symbol': '000100', 'name': 'TCL科技', 'type': '权重股', 'reason': '面板龙头', 'industry': '电子'},
            {'symbol': '000725', 'name': '京东方A', 'type': '权重股', 'reason': '面板龙头', 'industry': '电子'},
            {'symbol': '600584', 'name': '长电科技', 'type': '热点概念', 'reason': '半导体封测', 'industry': '半导体'},
            {'symbol': '603986', 'name': '兆易创新', 'type': '热点概念', 'reason': '存储芯片', 'industry': '半导体'},
            {'symbol': '002407', 'name': '多氟多', 'type': '热点概念', 'reason': '氟化工', 'industry': '化工'},
            {'symbol': '300274', 'name': '阳光电源', 'type': '权重股', 'reason': '光伏逆变器', 'industry': '电力设备'},
            {'symbol': '002460', 'name': '赣锋锂业', 'type': '权重股', 'reason': '锂矿龙头', 'industry': '有色金属'},
            {'symbol': '600893', 'name': '航发动力', 'type': '热点概念', 'reason': '军工发动机', 'industry': '国防军工'},
            {'symbol': '300034', 'name': '钢研高纳', 'type': '热点概念', 'reason': '军工材料', 'industry': '国防军工'},
            {'symbol': '000831', 'name': '五矿稀土', 'type': '热点概念', 'reason': '稀土', 'industry': '有色金属'},
            {'symbol': '300760', 'name': '迈瑞医疗', 'type': '权重股', 'reason': '医疗器械', 'industry': '医药生物'},
            {'symbol': '002335', 'name': '科华数据', 'type': '热点概念', 'reason': 'IDC', 'industry': '通信'},
            {'symbol': '002456', 'name': '欧菲光', 'type': '热点概念', 'reason': '消费电子', 'industry': '电子'},
            {'symbol': '300104', 'name': '乐视网', 'type': '热点概念', 'reason': '大数据', 'industry': '传媒'},
            {'symbol': '300222', 'name': '科大讯飞', 'type': '热点概念', 'reason': 'AI语音', 'industry': '计算机'},
            {'symbol': '600030', 'name': '中信证券', 'type': '权重股', 'reason': '券商龙头', 'industry': '非银金融'}
        ]
        
        for stock in default_stocks:
            if stock['symbol'] not in seen:
                unique_stocks.append(stock)
        
        result = unique_stocks[:50]
        self.cache[cache_key] = result
        self.last_fetch_time[cache_key] = get_beijing_time()
        
        print(f"📊 动态选股共 {len(unique_stocks)} 只股票")
        return result