import pandas as pd
import numpy as np
import random
import requests
from datetime import datetime, timedelta
import os

from utils.time_utils import get_beijing_time
from .industry_data import IndustryData

os.environ['USE_REAL_DATA'] = 'true'

try:
    import akshare as ak
    AK_SHARE_AVAILABLE = True
    print("✅ AKShare已安装")
except ImportError:
    AK_SHARE_AVAILABLE = False
    print("❌ AKShare未安装")

class DataFetcher:
    def __init__(self):
        self.cache = {}
        self.last_fetch_time = {}
        self.industry_data = IndustryData()
    
    def _normalize_symbol(self, symbol):
        symbol = str(symbol).strip().upper()
        if symbol.startswith('SH'):
            return symbol[2:] + '.SS'
        elif symbol.startswith('SZ'):
            return symbol[2:] + '.SZ'
        elif '.' not in symbol:
            if symbol.startswith('6'):
                return symbol + '.SS'
            else:
                return symbol + '.SZ'
        return symbol
    
    def _is_cache_valid(self, key):
        if key in self.last_fetch_time:
            return (get_beijing_time() - self.last_fetch_time[key]).seconds < 300
        return False
    
    def get_stock_data(self, symbol, start_date=None, end_date=None, period='1y'):
        symbol = self._normalize_symbol(symbol)
        cache_key = f"stock_data_{symbol}_{period}"
        
        if self._is_cache_valid(cache_key):
            cached = self.cache.get(cache_key)
            if cached is not None and not cached.empty:
                return cached
        
        try:
            if AK_SHARE_AVAILABLE:
                ak_symbol = symbol.replace('.SS', '').replace('.SZ', '')
                days = {'1y': 252, '1mo': 21, '3mo': 63, '6mo': 126}.get(period, 252)
                
                end_dt = get_beijing_time()
                start_dt = end_dt - timedelta(days=days + 50)
                
                try:
                    data = ak.stock_zh_a_hist(
                        symbol=ak_symbol,
                        start_date=start_dt.strftime('%Y%m%d'),
                        end_date=end_dt.strftime('%Y%m%d'),
                        adjust='qfq'
                    )
                    
                    if not data.empty:
                        data = data[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
                        data.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
                        data['date'] = pd.to_datetime(data['date']).dt.date
                        data.set_index(pd.to_datetime(data['date']), inplace=True)
                        self.cache[cache_key] = data
                        self.last_fetch_time[cache_key] = get_beijing_time()
                        print(f"✅ 获取真实历史数据(AKShare): {symbol}")
                        return data
                except Exception as e:
                    print(f"⚠️ AKShare历史数据获取失败: {e}")
        
        except Exception as e:
            print(f"⚠️ 获取历史数据失败: {e}")
        
        data = self._fetch_historical_data_sina(symbol, period)
        if data is not None and not data.empty:
            self.cache[cache_key] = data
            self.last_fetch_time[cache_key] = get_beijing_time()
            return data
        
        data = self._fetch_historical_data_eastmoney(symbol, period)
        if data is not None and not data.empty:
            self.cache[cache_key] = data
            self.last_fetch_time[cache_key] = get_beijing_time()
            return data
        
        print(f"❌ 无法获取真实历史数据: {symbol}")
        return pd.DataFrame()
    
    def _fetch_historical_data_sina(self, symbol, period):
        ak_symbol = symbol.replace('.SS', '').replace('.SZ', '')
        market = 'sh' if symbol.endswith('.SS') else 'sz'
        days = {'1y': 252, '1mo': 21, '3mo': 63, '6mo': 126}.get(period, 252)
        
        try:
            url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={market}{ak_symbol}&scale=240&ma=no&datalen={days}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data and isinstance(data, list):
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['day'])
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(int)
                df.set_index('date', inplace=True)
                print(f"✅ 获取真实历史数据(新浪财经): {symbol}")
                return df[['open', 'high', 'low', 'close', 'volume']]
        except Exception as e:
            print(f"⚠️ 新浪财经历史数据获取失败: {e}")
        
        return None
    
    def _fetch_historical_data_eastmoney(self, symbol, period):
        ak_symbol = symbol.replace('.SS', '').replace('.SZ', '')
        market = '1' if symbol.endswith('.SS') else '0'
        days = {'1y': 252, '1mo': 21, '3mo': 63, '6mo': 126}.get(period, 252)
        
        try:
            url = f"http://push2his.eastmoney.com/api/qt/stock/kline/get?secid={market}.{ak_symbol}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58&klt=101&fqt=1&beg=20250101&end=20261231"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and data['data'].get('klines'):
                klines = data['data']['klines']
                rows = []
                for kline in klines:
                    parts = kline.split(',')
                    if len(parts) >= 6:
                        rows.append({
                            'date': parts[0],
                            'open': float(parts[1]),
                            'close': float(parts[2]),
                            'high': float(parts[3]),
                            'low': float(parts[4]),
                            'volume': int(parts[5])
                        })
                
                df = pd.DataFrame(rows)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                print(f"✅ 获取真实历史数据(东方财富): {symbol}")
                return df[['open', 'high', 'low', 'close', 'volume']]
        except Exception as e:
            print(f"⚠️ 东方财富历史数据获取失败: {e}")
        
        return None
    
    def get_realtime_price(self, symbol):
        symbol = self._normalize_symbol(symbol)
        ak_symbol = symbol.replace('.SS', '').replace('.SZ', '')
        
        tencent_url = f"https://qt.gtimg.cn/q=sh{ak_symbol}" if symbol.endswith('.SS') else f"https://qt.gtimg.cn/q=sz{ak_symbol}"
        
        try:
            response = requests.get(tencent_url, timeout=10)
            response.raise_for_status()
            content = response.text
            
            if content and '=' in content:
                        parts = content.split('~')
                        if len(parts) > 3:
                            price = float(parts[3])
                            high_today = float(parts[33]) if len(parts) > 33 else price
                            low_today = float(parts[34]) if len(parts) > 34 else price
                            change = float(parts[31]) if len(parts) > 31 else 0
                            change_percent = float(parts[32]) if len(parts) > 32 else 0
                            prev_close = float(parts[4]) if len(parts) > 4 else price
                            stock_name = parts[1] if len(parts) > 1 else 'Unknown'
                            print(f"✅ 腾讯财经实时抓取: {stock_name} ({symbol}) = ¥{price}, 涨跌 {change_percent}%, 今日最高 ¥{high_today}")
                            return {'price': price, 'high_today': high_today, 'low_today': low_today, 'change': change, 'change_percent': change_percent, 'prev_close': prev_close}
            else:
                print(f"⚠️ 腾讯财经API返回空数据: {symbol}")
        except Exception as e:
            print(f"⚠️ 腾讯财经API调用失败 {symbol}: {e}")
        
        sina_url = f"https://hq.sinajs.cn/list=sh{ak_symbol}" if symbol.endswith('.SS') else f"https://hq.sinajs.cn/list=sz{ak_symbol}"
        
        try:
            response = requests.get(sina_url, timeout=10)
            response.raise_for_status()
            content = response.text
            if content:
                parts = content.split(',')
                if len(parts) > 6:
                    price = float(parts[3])
                    high_today = float(parts[6]) if len(parts) > 6 else price
                    print(f"✅ 新浪财经抓取: {symbol} = ¥{price}, 今日最高 ¥{high_today}")
                    return {'price': price, 'high_today': high_today}
        except Exception as e:
            print(f"⚠️ 新浪财经API调用失败 {symbol}: {e}")
        
        eastmoney_url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={'1' if symbol.endswith('.SS') else '0'}.{ak_symbol}&fields=f57,f58,f2,f3,f61"
        
        try:
            response = requests.get(eastmoney_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                price = float(data['data']['f2']) / 100
                high_today = float(data['data']['f61']) / 100 if data['data'].get('f61') else price
                stock_name = data['data']['f58']
                print(f"✅ 东方财富抓取: {stock_name} ({symbol}) = ¥{price}, 今日最高 ¥{high_today}")
                return {'price': price, 'high_today': high_today}
        except Exception as e:
            print(f"⚠️ 东方财富API调用失败 {symbol}: {e}")
        
        print(f"❌ 无法获取真实价格: {symbol}")
        return None
    
    def get_stock_info(self, symbol):
        symbol = self._normalize_symbol(symbol)
        cache_key = f"info_{symbol}"
        
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, {})
        
        try:
            if AK_SHARE_AVAILABLE:
                ak_symbol = symbol.replace('.SS', '').replace('.SZ', '')
                try:
                    df = ak.stock_zh_a_spot_em()
                    if not df.empty:
                        stock_data = df[df['代码'] == ak_symbol]
                        if not stock_data.empty:
                            industry = self.industry_data.get_industry(symbol)
                            info = {
                                'symbol': symbol,
                                'name': stock_data['名称'].iloc[0],
                                'sector': industry,
                                'industry': industry,
                                'market_cap': 0,
                                'pe_ratio': float(stock_data['市盈率'].iloc[0]) if pd.notna(stock_data['市盈率'].iloc[0]) else 0,
                                'dividend_yield': 0,
                                'beta': 1,
                                '52_week_high': 0,
                                '52_week_low': 0,
                                'current_price': float(stock_data['最新价'].iloc[0]),
                                'change': float(stock_data['涨跌幅'].iloc[0]),
                                'volume': int(stock_data['成交量'].iloc[0])
                            }
                            self.cache[cache_key] = info
                            self.last_fetch_time[cache_key] = get_beijing_time()
                            return info
                except Exception as e:
                    print(f"⚠️ AKShare股票信息获取失败: {e}")
        
        except Exception as e:
            print(f"⚠️ 获取股票信息失败: {e}")
        
        industry = self.industry_data.get_industry(symbol)
        return {
            'symbol': symbol,
            'name': symbol.replace('.SS', '').replace('.SZ', ''),
            'sector': industry,
            'industry': industry,
            'market_cap': 0,
            'pe_ratio': 0,
            'dividend_yield': 0,
            'beta': 1,
            '52_week_high': 0,
            '52_week_low': 0
        }
    
    def get_market_overview(self):
        cache_key = 'market_overview'
        
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, {})
        
        try:
            if AK_SHARE_AVAILABLE:
                try:
                    df = ak.stock_zh_index_spot_em()
                    result = {}
                    for _, row in df.iterrows():
                        name = row['名称']
                        if name in ['上证指数', '深证成指', '创业板指']:
                            result[name] = {
                                'name': name,
                                'value': float(row['最新价']),
                                'change': float(row['涨跌幅']),
                                'volume': row.get('成交量', 0)
                            }
                    if result:
                        self.cache[cache_key] = result
                        self.last_fetch_time[cache_key] = get_beijing_time()
                        print("✅ 获取真实市场指数数据")
                        return result
                except Exception as e:
                    print(f"⚠️ AKShare市场指数获取失败: {e}")
        except Exception as e:
            print(f"⚠️ 获取市场指数失败: {e}")
        
        print("❌ 无法获取真实市场指数数据")
        return {}
    
    def calculate_indicators(self, data):
        if data.empty:
            return data
        
        data = data.copy()
        data['daily_return'] = data['close'].pct_change()
        data['cumulative_return'] = (1 + data['daily_return']).cumprod()
        data['volatility'] = data['daily_return'].rolling(window=20).std() * np.sqrt(252)
        
        data['sma_20'] = data['close'].rolling(window=20).mean()
        data['sma_50'] = data['close'].rolling(window=50).mean()
        data['sma_200'] = data['close'].rolling(window=200).mean()
        
        ema_fast = data['close'].ewm(span=12, adjust=False).mean()
        ema_slow = data['close'].ewm(span=26, adjust=False).mean()
        data['macd'] = ema_fast - ema_slow
        data['signal_line'] = data['macd'].ewm(span=9, adjust=False).mean()
        
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss.replace(0, 0.001)
        data['rsi'] = 100 - (100 / (1 + rs))
        
        data['upper_band'] = data['sma_20'] + 2 * data['close'].rolling(window=20).std()
        data['middle_band'] = data['sma_20']
        data['lower_band'] = data['sma_20'] - 2 * data['close'].rolling(window=20).std()
        
        return data
    
    def get_portfolio_data(self, portfolio):
        portfolio_data = []
        
        for stock in portfolio:
            symbol = stock['symbol']
            try:
                data = self.get_stock_data(symbol, period='1y')
                if not data.empty:
                    latest = data.iloc[-1]
                    realtime_data = self.get_realtime_price(symbol)
                    realtime_price = realtime_data['price'] if isinstance(realtime_data, dict) else realtime_data
                    high_today = realtime_data['high_today'] if isinstance(realtime_data, dict) else None
                    
                    if isinstance(realtime_data, dict) and 'change_percent' in realtime_data:
                        change = realtime_data['change']
                        change_percent = realtime_data['change_percent']
                    else:
                        prev_close = data.iloc[-2]['close'] if len(data) > 1 else latest['close']
                        change = latest['close'] - prev_close
                        change_percent = (change / prev_close * 100) if prev_close != 0 else 0
                    
                    purchase_date = stock.get('purchase_date')
                    if purchase_date and not data.empty:
                        try:
                            purchase_dt = pd.to_datetime(purchase_date)
                            data_since_purchase = data[data.index >= purchase_dt]
                            if not data_since_purchase.empty:
                                high_since_purchase = data_since_purchase['high'].max()
                            else:
                                high_since_purchase = stock['cost_price']
                        except:
                            high_since_purchase = data['high'].max() if not data.empty else stock['cost_price']
                    else:
                        high_since_purchase = data['high'].max() if not data.empty else stock['cost_price']
                    
                    if high_today and high_today > high_since_purchase:
                        high_since_purchase = high_today
                    
                    portfolio_data.append({
                        'symbol': symbol,
                        'name': stock.get('name', symbol),
                        'quantity': stock['quantity'],
                        'cost_price': stock['cost_price'],
                        'purchase_date': purchase_date,
                        'current_price': realtime_price if realtime_price else latest['close'],
                        'close_price': latest['close'],
                        'change': change,
                        'change_percent': change_percent,
                        'market_value': stock['quantity'] * (realtime_price if realtime_price else latest['close']),
                        'profit': stock['quantity'] * ((realtime_price if realtime_price else latest['close']) - stock['cost_price']),
                        'profit_percent': (((realtime_price if realtime_price else latest['close']) - stock['cost_price']) / stock['cost_price'] * 100) if stock['cost_price'] != 0 else 0,
                        'high_since_purchase': high_since_purchase,
                        'trailing_stop_pct': stock.get('trailing_stop_pct', 10)
                    })
                else:
                    portfolio_data.append({
                        'symbol': symbol,
                        'name': stock.get('name', symbol),
                        'quantity': stock['quantity'],
                        'cost_price': stock['cost_price'],
                        'current_price': stock['cost_price'],
                        'close_price': stock['cost_price'],
                        'change': 0,
                        'change_percent': 0,
                        'market_value': stock['quantity'] * stock['cost_price'],
                        'profit': 0,
                        'profit_percent': 0
                    })
            except Exception as e:
                print(f"⚠️ 处理持仓数据失败 {symbol}: {e}")
                portfolio_data.append({
                    'symbol': symbol,
                    'name': stock.get('name', symbol),
                    'quantity': stock['quantity'],
                    'cost_price': stock['cost_price'],
                    'current_price': stock['cost_price'],
                    'close_price': stock['cost_price'],
                    'change': 0,
                    'change_percent': 0,
                    'market_value': stock['quantity'] * stock['cost_price'],
                    'profit': 0,
                    'profit_percent': 0
                })
        
        return portfolio_data
    
    def get_market_summary(self):
        cache_key = "market_summary"
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, {})
        
        result = {
            'shanghai': {'index': 0, 'change': 0, 'change_percent': 0},
            'shenzhen': {'index': 0, 'change': 0, 'change_percent': 0},
            'star': {'index': 0, 'change': 0, 'change_percent': 0},
            'hot_concepts': [],
            'market_status': 'closed'
        }
        
        try:
            proxies = None
            try:
                import os
                if 'http_proxy' in os.environ:
                    del os.environ['http_proxy']
                    del os.environ['https_proxy']
            except:
                pass
            
            session = requests.Session()
            session.trust_env = False
            
            try:
                url = 'https://qt.gtimg.cn/q=sh000001,sz399001,sz399006'
                response = session.get(url, timeout=5)
                if response.status_code == 200:
                    lines = response.text.split('\n')
                    for line in lines:
                        if 'sh000001' in line:
                            parts = line.split('~')
                            if len(parts) >= 4:
                                price = float(parts[3])
                                prev_close = float(parts[4])
                                change = price - prev_close
                                change_percent = (change / prev_close * 100) if prev_close != 0 else 0
                                result['shanghai'] = {
                                    'index': round(price, 2),
                                    'change': round(change, 2),
                                    'change_percent': round(change_percent, 2)
                                }
                        elif 'sz399001' in line or '深证成指' in line:
                            parts = line.split('~')
                            if len(parts) >= 4:
                                price = float(parts[3])
                                prev_close = float(parts[4])
                                change = price - prev_close
                                change_percent = (change / prev_close * 100) if prev_close != 0 else 0
                                result['shenzhen'] = {
                                    'index': round(price, 2),
                                    'change': round(change, 2),
                                    'change_percent': round(change_percent, 2)
                                }
                        elif 'sz399006' in line:
                            parts = line.split('~')
                            if len(parts) >= 4:
                                price = float(parts[3])
                                prev_close = float(parts[4])
                                change = price - prev_close
                                change_percent = (change / prev_close * 100) if prev_close != 0 else 0
                                result['star'] = {
                                    'index': round(price, 2),
                                    'change': round(change, 2),
                                    'change_percent': round(change_percent, 2)
                                }
            except Exception as e:
                print(f"⚠️ 腾讯财经市场指数获取失败: {e}")
            
            try:
                url = 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=10&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=b:BK0000&fields=f14,f57,f3'
                response = session.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    hot_concepts = []
                    for item in data.get('data', {}).get('diff', []):
                        hot_concepts.append({
                            'name': str(item.get('f14', '')),
                            'change_percent': round(float(item.get('f3', 0)), 2),
                            'leader': ''
                        })
                    result['hot_concepts'] = hot_concepts[:10]
            except Exception as e:
                print(f"⚠️ 热点概念获取失败: {e}")
            
            now = get_beijing_time()
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=15, minute=0, second=0, microsecond=0)
            lunch_start = now.replace(hour=11, minute=30, second=0, microsecond=0)
            lunch_end = now.replace(hour=13, minute=0, second=0, microsecond=0)
            
            if market_open <= now < market_close:
                if now < lunch_start or now >= lunch_end:
                    result['market_status'] = 'open'
                else:
                    result['market_status'] = 'lunch'
            else:
                result['market_status'] = 'closed'
            
            self.cache[cache_key] = result
            self.last_fetch_time[cache_key] = get_beijing_time()
            
        except Exception as e:
            print(f"⚠️ 获取市场数据失败: {e}")
        
        return result
