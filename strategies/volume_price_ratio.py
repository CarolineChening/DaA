import pandas as pd
import numpy as np

class VolumePriceRatioStrategy:
    def __init__(self, period=20, threshold=1.5):
        self.period = period
        self.threshold = threshold
    
    def generate_signal(self, data):
        if len(data) < self.period + 1:
            return 'hold'
        
        data = data.copy()
        
        data['price_change'] = data['close'].pct_change()
        data['volume_change'] = data['volume'].pct_change()
        
        data['vp_ratio'] = abs(data['volume_change']) / abs(data['price_change'])
        
        data['vp_ratio_ma'] = data['vp_ratio'].rolling(window=self.period).mean()
        data['volume_ma'] = data['volume'].rolling(window=self.period).mean()
        
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        volume_spike = latest['volume'] > self.threshold * data['volume_ma'].iloc[-1]
        price_momentum = latest['price_change']
        
        if volume_spike and price_momentum > 0.02 and prev['price_change'] <= 0.02:
            return 'buy'
        elif volume_spike and price_momentum < -0.02 and prev['price_change'] >= -0.02:
            return 'sell'
        elif latest['vp_ratio'] < data['vp_ratio_ma'].iloc[-1] * 0.5 and abs(latest['price_change']) > 0.03:
            if latest['price_change'] > 0:
                return 'buy'
            else:
                return 'sell'
        
        return 'hold'
    
    def backtest(self, data):
        if len(data) < self.period + 1:
            return pd.DataFrame()
        
        data = data.copy()
        data['price_change'] = data['close'].pct_change()
        data['volume_change'] = data['volume'].pct_change()
        data['vp_ratio'] = abs(data['volume_change']) / abs(data['price_change'])
        data['vp_ratio_ma'] = data['vp_ratio'].rolling(window=self.period).mean()
        data['volume_ma'] = data['volume'].rolling(window=self.period).mean()
        data['signal'] = 'hold'
        
        for i in range(self.period + 1, len(data)):
            volume_spike = data['volume'].iloc[i] > self.threshold * data['volume_ma'].iloc[i]
            price_momentum = data['price_change'].iloc[i]
            prev_price_change = data['price_change'].iloc[i-1]
            
            if volume_spike and price_momentum > 0.02 and prev_price_change <= 0.02:
                data['signal'].iloc[i] = 'buy'
            elif volume_spike and price_momentum < -0.02 and prev_price_change >= -0.02:
                data['signal'].iloc[i] = 'sell'
        
        data['position'] = data['signal'].replace({'buy': 1, 'sell': -1, 'hold': np.nan}).ffill().fillna(0)
        data['strategy_return'] = data['position'].shift(1) * data['close'].pct_change()
        data['cumulative_return'] = (1 + data['strategy_return']).cumprod()
        
        return data
    
    def get_name(self):
        return f"量价比策略 ({self.period}, {self.threshold}x)"