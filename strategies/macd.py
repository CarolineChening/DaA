import pandas as pd
import numpy as np

class MACDStrategy:
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def generate_signal(self, data):
        if len(data) < self.slow_period + self.signal_period:
            return 'hold'
        
        data = data.copy()
        ema_fast = data['close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = data['close'].ewm(span=self.slow_period, adjust=False).mean()
        data['macd'] = ema_fast - ema_slow
        data['signal'] = data['macd'].ewm(span=self.signal_period, adjust=False).mean()
        data['histogram'] = data['macd'] - data['signal']
        
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        if latest['macd'] > latest['signal'] and prev['macd'] <= prev['signal']:
            return 'buy'
        elif latest['macd'] < latest['signal'] and prev['macd'] >= prev['signal']:
            return 'sell'
        else:
            return 'hold'
    
    def backtest(self, data):
        if len(data) < self.slow_period + self.signal_period:
            return pd.DataFrame()
        
        data = data.copy()
        ema_fast = data['close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = data['close'].ewm(span=self.slow_period, adjust=False).mean()
        data['macd'] = ema_fast - ema_slow
        data['signal_line'] = data['macd'].ewm(span=self.signal_period, adjust=False).mean()
        data['histogram'] = data['macd'] - data['signal_line']
        data['signal'] = 'hold'
        
        for i in range(self.slow_period + self.signal_period, len(data)):
            if data['macd'].iloc[i] > data['signal_line'].iloc[i] and data['macd'].iloc[i-1] <= data['signal_line'].iloc[i-1]:
                data['signal'].iloc[i] = 'buy'
            elif data['macd'].iloc[i] < data['signal_line'].iloc[i] and data['macd'].iloc[i-1] >= data['signal_line'].iloc[i-1]:
                data['signal'].iloc[i] = 'sell'
        
        data['position'] = data['signal'].replace({'buy': 1, 'sell': -1, 'hold': np.nan}).ffill().fillna(0)
        data['strategy_return'] = data['position'].shift(1) * data['close'].pct_change()
        data['cumulative_return'] = (1 + data['strategy_return']).cumprod()
        
        return data
    
    def get_name(self):
        return f"MACD策略 ({self.fast_period}/{self.slow_period}/{self.signal_period})"
