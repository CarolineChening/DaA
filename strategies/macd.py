import pandas as pd
import numpy as np

class MACDStrategy:
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.name = "MACD"
    
    def generate_signal(self, data):
        if len(data) < self.slow_period + self.signal_period + 5:
            return 'hold', 0
        
        data = data.copy()
        ema_fast = data['close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = data['close'].ewm(span=self.slow_period, adjust=False).mean()
        data['macd'] = ema_fast - ema_slow
        data['signal'] = data['macd'].ewm(span=self.signal_period, adjust=False).mean()
        data['histogram'] = data['macd'] - data['signal']
        
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        prev2 = data.iloc[-3]
        
        signal_score = 0
        
        if latest['macd'] > latest['signal'] and prev['macd'] <= prev['signal']:
            signal_score += 3
        
        if latest['macd'] > 0 and prev['macd'] <= 0:
            signal_score += 2
        
        if latest['histogram'] > 0 and prev['histogram'] <= 0:
            signal_score += 2
        
        if prev['histogram'] < 0 and latest['histogram'] > prev['histogram'] and latest['histogram'] < 0:
            signal_score += 1
        
        if prev2['histogram'] < prev['histogram'] < 0 and latest['histogram'] > prev['histogram']:
            signal_score += 1
        
        if abs(latest['macd'] - latest['signal']) < abs(prev['macd'] - prev['signal']) and latest['macd'] < latest['signal']:
            signal_score += 1
        
        if latest['macd'] > prev['macd'] and latest['signal'] > prev['signal']:
            signal_score += 1
        
        if latest['macd'] > 0 and latest['signal'] > 0 and latest['macd'] > latest['signal']:
            signal_score += 1
        
        if latest['macd'] < latest['signal'] and prev['macd'] >= prev['signal']:
            signal_score -= 3
        
        if latest['macd'] < 0 and prev['macd'] >= 0:
            signal_score -= 2
        
        if latest['histogram'] < 0 and prev['histogram'] >= 0:
            signal_score -= 2
        
        if prev['histogram'] > 0 and latest['histogram'] < prev['histogram'] and latest['histogram'] > 0:
            signal_score -= 1
        
        if signal_score >= 3:
            return 'buy', signal_score
        elif signal_score <= -3:
            return 'sell', abs(signal_score)
        elif signal_score >= 1:
            return 'buy', signal_score
        elif signal_score <= -1:
            return 'sell', abs(signal_score)
        else:
            return 'hold', 0
    
    def get_name(self):
        return f"MACD策略 ({self.fast_period}/{self.slow_period}/{self.signal_period})"
    
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
        
        return data