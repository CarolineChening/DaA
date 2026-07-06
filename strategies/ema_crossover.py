import pandas as pd
import numpy as np

class EMACrossoverStrategy:
    def __init__(self, short_period=12, long_period=26):
        self.short_period = short_period
        self.long_period = long_period
        self.name = "EMA"
    
    def generate_signal(self, data):
        if len(data) < self.long_period + 1:
            return 'hold'
        
        data = data.copy()
        data['ema_short'] = data['close'].ewm(span=self.short_period, adjust=False).mean()
        data['ema_long'] = data['close'].ewm(span=self.long_period, adjust=False).mean()
        
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        if latest['ema_short'] > latest['ema_long'] and prev['ema_short'] <= prev['ema_long']:
            return 'buy'
        elif latest['ema_short'] < latest['ema_long'] and prev['ema_short'] >= prev['ema_long']:
            return 'sell'
        else:
            return 'hold'
    
    def backtest(self, data):
        if len(data) < self.long_period + 1:
            return pd.DataFrame()
        
        data = data.copy()
        data['ema_short'] = data['close'].ewm(span=self.short_period, adjust=False).mean()
        data['ema_long'] = data['close'].ewm(span=self.long_period, adjust=False).mean()
        data['signal'] = 'hold'
        
        for i in range(self.long_period + 1, len(data)):
            if data['ema_short'].iloc[i] > data['ema_long'].iloc[i] and data['ema_short'].iloc[i-1] <= data['ema_long'].iloc[i-1]:
                data['signal'].iloc[i] = 'buy'
            elif data['ema_short'].iloc[i] < data['ema_long'].iloc[i] and data['ema_short'].iloc[i-1] >= data['ema_long'].iloc[i-1]:
                data['signal'].iloc[i] = 'sell'
        
        data['position'] = data['signal'].replace({'buy': 1, 'sell': -1, 'hold': np.nan}).ffill().fillna(0)
        data['strategy_return'] = data['position'].shift(1) * data['close'].pct_change()
        data['cumulative_return'] = (1 + data['strategy_return']).cumprod()
        
        return data
    
    def get_name(self):
        return f"EMA交叉策略 ({self.short_period}/{self.long_period})"