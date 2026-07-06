import pandas as pd
import numpy as np

class RSIStrategy:
    def __init__(self, period=14, overbought=70, oversold=30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.name = "RSI"
    
    def generate_signal(self, data):
        if len(data) < self.period + 1:
            return 'hold'
        
        data = data.copy()
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        latest_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2]
        
        if latest_rsi < self.oversold and prev_rsi >= self.oversold:
            return 'buy'
        elif latest_rsi > self.overbought and prev_rsi <= self.overbought:
            return 'sell'
        else:
            return 'hold'
    
    def backtest(self, data):
        if len(data) < self.period + 1:
            return pd.DataFrame()
        
        data = data.copy()
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        
        rs = avg_gain / avg_loss
        data['rsi'] = 100 - (100 / (1 + rs))
        data['signal'] = 'hold'
        
        for i in range(self.period + 1, len(data)):
            if data['rsi'].iloc[i] < self.oversold and data['rsi'].iloc[i-1] >= self.oversold:
                data['signal'].iloc[i] = 'buy'
            elif data['rsi'].iloc[i] > self.overbought and data['rsi'].iloc[i-1] <= self.overbought:
                data['signal'].iloc[i] = 'sell'
        
        data['position'] = data['signal'].replace({'buy': 1, 'sell': -1, 'hold': np.nan}).ffill().fillna(0)
        data['strategy_return'] = data['position'].shift(1) * data['close'].pct_change()
        data['cumulative_return'] = (1 + data['strategy_return']).cumprod()
        
        return data
    
    def get_name(self):
        return f"RSI策略 ({self.period}, {self.oversold}/{self.overbought})"
