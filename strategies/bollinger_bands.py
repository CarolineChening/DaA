import pandas as pd
import numpy as np

class BollingerBandsStrategy:
    def __init__(self, period=20, num_std=2):
        self.period = period
        self.num_std = num_std
    
    def generate_signal(self, data):
        if len(data) < self.period:
            return 'hold'
        
        data = data.copy()
        data['sma'] = data['close'].rolling(window=self.period).mean()
        data['std'] = data['close'].rolling(window=self.period).std()
        data['upper_band'] = data['sma'] + (data['std'] * self.num_std)
        data['lower_band'] = data['sma'] - (data['std'] * self.num_std)
        data['percent_b'] = (data['close'] - data['lower_band']) / (data['upper_band'] - data['lower_band'])
        
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        if latest['close'] <= latest['lower_band'] and prev['close'] > prev['lower_band']:
            return 'buy'
        elif latest['close'] >= latest['upper_band'] and prev['close'] < prev['upper_band']:
            return 'sell'
        else:
            return 'hold'
    
    def backtest(self, data):
        if len(data) < self.period:
            return pd.DataFrame()
        
        data = data.copy()
        data['sma'] = data['close'].rolling(window=self.period).mean()
        data['std'] = data['close'].rolling(window=self.period).std()
        data['upper_band'] = data['sma'] + (data['std'] * self.num_std)
        data['lower_band'] = data['sma'] - (data['std'] * self.num_std)
        data['percent_b'] = (data['close'] - data['lower_band']) / (data['upper_band'] - data['lower_band'])
        data['signal'] = 'hold'
        
        for i in range(self.period, len(data)):
            if data['close'].iloc[i] <= data['lower_band'].iloc[i] and data['close'].iloc[i-1] > data['lower_band'].iloc[i-1]:
                data['signal'].iloc[i] = 'buy'
            elif data['close'].iloc[i] >= data['upper_band'].iloc[i] and data['close'].iloc[i-1] < data['upper_band'].iloc[i-1]:
                data['signal'].iloc[i] = 'sell'
        
        data['position'] = data['signal'].replace({'buy': 1, 'sell': -1, 'hold': np.nan}).ffill().fillna(0)
        data['strategy_return'] = data['position'].shift(1) * data['close'].pct_change()
        data['cumulative_return'] = (1 + data['strategy_return']).cumprod()
        
        return data
    
    def get_name(self):
        return f"布林带策略 ({self.period}, {self.num_std}σ)"
