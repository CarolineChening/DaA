import pandas as pd
import numpy as np

class NineTurnsStrategy:
    def __init__(self):
        self.name = "神奇九转"
    
    def generate_signal(self, data):
        if len(data) < 13:
            return 'hold', 0
        
        data_copy = data.copy()
        data_copy = self._calculate_nine_turns(data_copy)
        
        latest = data_copy.iloc[-1]
        buy_count = latest.get('buy_count', 0)
        sell_count = latest.get('sell_count', 0)
        
        if buy_count == 9:
            return 'buy', 9
        elif sell_count == 9:
            return 'sell', 9
        elif buy_count >= 8:
            return 'buy', buy_count
        elif sell_count >= 8:
            return 'sell', sell_count
        else:
            return 'hold', max(buy_count, sell_count)
    
    def _calculate_nine_turns(self, data):
        buy_counts = [0] * len(data)
        sell_counts = [0] * len(data)
        signals = ['none'] * len(data)
        
        for i in range(4, len(data)):
            current_close = data['close'].iloc[i]
            four_days_ago_close = data['close'].iloc[i - 4]
            
            if current_close < four_days_ago_close:
                prev_count = buy_counts[i - 1]
                if prev_count > 0:
                    buy_counts[i] = prev_count + 1
                else:
                    buy_counts[i] = 1
                sell_counts[i] = 0
            elif current_close > four_days_ago_close:
                prev_count = sell_counts[i - 1]
                if prev_count > 0:
                    sell_counts[i] = prev_count + 1
                else:
                    sell_counts[i] = 1
                buy_counts[i] = 0
            else:
                buy_counts[i] = 0
                sell_counts[i] = 0
            
            if buy_counts[i] == 9:
                signals[i] = 'buy'
            elif sell_counts[i] == 9:
                signals[i] = 'sell'
        
        data['buy_count'] = buy_counts
        data['sell_count'] = sell_counts
        data['nine_turns_signal'] = signals
        
        return data
    
    def backtest(self, data):
        if len(data) < 13:
            return pd.DataFrame()
        
        data_copy = data.copy()
        data_copy = self._calculate_nine_turns(data_copy)
        
        data_copy['signal'] = 'hold'
        data_copy.loc[data_copy['nine_turns_signal'] == 'buy', 'signal'] = 'buy'
        data_copy.loc[data_copy['nine_turns_signal'] == 'sell', 'signal'] = 'sell'
        
        data_copy['position'] = data_copy['signal'].replace({'buy': 1, 'sell': -1, 'hold': np.nan}).ffill().fillna(0)
        data_copy['strategy_return'] = data_copy['position'].shift(1) * data_copy['close'].pct_change()
        data_copy['cumulative_return'] = (1 + data_copy['strategy_return']).cumprod()
        
        return data_copy
    
    def get_name(self):
        return "神奇九转策略"
    
    def get_current_turn(self, data):
        if len(data) < 13:
            return 0, 'neutral'
        
        data_copy = data.copy()
        data_copy = self._calculate_nine_turns(data_copy)
        
        latest = data_copy.iloc[-1]
        buy_count = latest.get('buy_count', 0)
        sell_count = latest.get('sell_count', 0)
        
        if buy_count > 0:
            return buy_count, 'buy'
        elif sell_count > 0:
            return sell_count, 'sell'
        else:
            return 0, 'neutral'
