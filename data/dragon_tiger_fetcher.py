import pandas as pd
import time
from datetime import datetime
from utils.time_utils import get_beijing_time, format_beijing_date

class DragonTigerFetcher:
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        
    def fetch_dragon_tiger_data(self):
        cache_key = 'daily'
        if cache_key in self.cache:
            cache_timestamp = self.cache_time.get(cache_key, 0)
            if time.time() - cache_timestamp < 300:
                return self.cache[cache_key]
        
        try:
            import akshare as ak
            df = ak.stock_lhb_stock_statistic_em()
            
            if df is not None and not df.empty:
                df['代码'] = df['代码'].astype(str)
                df = df[['代码', '名称', '收盘价', '涨跌幅', '龙虎榜净买额', '龙虎榜买入额', '龙虎榜卖出额', 
                         '买方机构次数', '卖方机构次数', '机构买入净额']]
                df.columns = ['symbol', 'name', 'close', 'change_percent', 'net_amount', 'buy_amount', 
                              'sell_amount', 'buy_institution_count', 'sell_institution_count', 'institution_net_amount']
                
                self.cache[cache_key] = df
                self.cache_time[cache_key] = time.time()
                
                return df
        except Exception as e:
            print(f"⚠️ 龙虎榜数据获取失败: {e}")
        
        return pd.DataFrame()
    
    def get_top_stocks(self, limit=10):
        df = self.fetch_dragon_tiger_data()
        if df.empty:
            return []
        
        df = df.sort_values('net_amount', ascending=False)
        top_stocks = []
        
        for _, row in df.head(limit).iterrows():
            top_stocks.append({
                'symbol': row['symbol'],
                'name': row['name'],
                'close': row['close'],
                'change_percent': row['change_percent'],
                'buy_amount': row['buy_amount'],
                'sell_amount': row['sell_amount'],
                'net_amount': row['net_amount'],
                'buy_institution_count': row['buy_institution_count'],
                'sell_institution_count': row['sell_institution_count'],
                'institution_net_amount': row['institution_net_amount']
            })
        
        return top_stocks
    
    def get_stock_dragon_tiger(self, symbol):
        df = self.fetch_dragon_tiger_data()
        if df.empty:
            return None
        
        symbol_str = str(symbol).replace('.SS', '').replace('.SZ', '')
        result = df[df['symbol'] == symbol_str]
        
        if result.empty:
            return None
        
        row = result.iloc[0]
        return {
            'symbol': row['symbol'],
            'name': row['name'],
            'close': row['close'],
            'change_percent': row['change_percent'],
            'buy_amount': row['buy_amount'],
            'sell_amount': row['sell_amount'],
            'net_amount': row['net_amount'],
            'buy_institution_count': row['buy_institution_count'],
            'sell_institution_count': row['sell_institution_count'],
            'institution_net_amount': row['institution_net_amount']
        }
    
    def get_dragon_tiger_signal(self, symbol):
        data = self.get_stock_dragon_tiger(symbol)
        if not data:
            return 'neutral', 0
        
        net_amount = data['net_amount']
        buy_institution_count = data['buy_institution_count']
        sell_institution_count = data['sell_institution_count']
        institution_net_amount = data['institution_net_amount']
        
        score = 0
        
        if net_amount > 50000000:
            score += 0.5
        elif net_amount > 20000000:
            score += 0.3
        elif net_amount > 5000000:
            score += 0.15
        elif net_amount < -50000000:
            score -= 0.5
        elif net_amount < -20000000:
            score -= 0.3
        elif net_amount < -5000000:
            score -= 0.15
        
        if buy_institution_count > sell_institution_count:
            score += 0.3
            if buy_institution_count >= 2 and sell_institution_count == 0:
                score += 0.2
        elif sell_institution_count > buy_institution_count:
            score -= 0.3
            if sell_institution_count >= 2 and buy_institution_count == 0:
                score -= 0.2
        
        if institution_net_amount > 0:
            score += 0.2
        elif institution_net_amount < 0:
            score -= 0.2
        
        if score > 0.5:
            return 'buy', score
        elif score < -0.5:
            return 'sell', score
        else:
            return 'neutral', score
