import pandas as pd
import numpy as np

class MovingAverageStrategy:
    def __init__(self, short_window=5, long_window=20):
        self.short_window = short_window
        self.long_window = long_window
        self.name = "均线"
    
    def generate_signal(self, data):
        if len(data) < self.long_window:
            return 'hold'
        
        data = data.copy()
        data['short_ma'] = data['close'].rolling(window=self.short_window).mean()
        data['long_ma'] = data['close'].rolling(window=self.long_window).mean()
        
        latest = data.iloc[-1]
        
        if latest['short_ma'] > latest['long_ma']:
            prev_data = data.iloc[-2]
            if prev_data['short_ma'] <= prev_data['long_ma']:
                return 'buy'
            return 'hold'
        else:
            prev_data = data.iloc[-2]
            if prev_data['short_ma'] >= prev_data['long_ma']:
                return 'sell'
            return 'hold'
    
    def backtest(self, data):
        if len(data) < self.long_window:
            return pd.DataFrame()
        
        data = data.copy()
        data['short_ma'] = data['close'].rolling(window=self.short_window).mean()
        data['long_ma'] = data['close'].rolling(window=self.long_window).mean()
        data['signal'] = 'hold'
        
        for i in range(self.long_window, len(data)):
            if data['short_ma'].iloc[i] > data['long_ma'].iloc[i]:
                if data['short_ma'].iloc[i-1] <= data['long_ma'].iloc[i-1]:
                    data['signal'].iloc[i] = 'buy'
                else:
                    data['signal'].iloc[i] = 'hold'
            else:
                if data['short_ma'].iloc[i-1] >= data['long_ma'].iloc[i-1]:
                    data['signal'].iloc[i] = 'sell'
                else:
                    data['signal'].iloc[i] = 'hold'
        
        data['position'] = data['signal'].replace({'buy': 1, 'sell': -1, 'hold': np.nan}).ffill().fillna(0)
        data['strategy_return'] = data['position'].shift(1) * data['close'].pct_change()
        data['cumulative_return'] = (1 + data['strategy_return']).cumprod()
        
        return data
    
    def get_name(self):
        return f"移动平均线策略 ({self.short_window}/{self.long_window})"
