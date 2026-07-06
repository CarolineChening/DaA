import pandas as pd
import numpy as np
from .moving_average import MovingAverageStrategy
from .macd import MACDStrategy
from .rsi import RSIStrategy
from .bollinger_bands import BollingerBandsStrategy
from .nine_turns import NineTurnsStrategy

class CombinedStrategy:
    def __init__(self):
        self.name = "综合"
        self.strategies = [
            MovingAverageStrategy(),
            MACDStrategy(),
            RSIStrategy(),
            BollingerBandsStrategy(),
            NineTurnsStrategy()
        ]
    
    def generate_signal(self, data):
        signals = []
        for strategy in self.strategies:
            result = strategy.generate_signal(data)
            if isinstance(result, tuple):
                signal = result[0]
            else:
                signal = result
            signals.append(signal)
        
        buy_count = signals.count('buy')
        sell_count = signals.count('sell')
        
        if buy_count >= 2:
            return 'buy'
        elif sell_count >= 2:
            return 'sell'
        else:
            return 'hold'
    
    def backtest(self, data):
        data = data.copy()
        
        all_signals = pd.DataFrame()
        for i, strategy in enumerate(self.strategies):
            result = strategy.backtest(data)
            if not result.empty:
                all_signals[f'signal_{i}'] = result['signal']
        
        data['combined_signal'] = 'hold'
        
        if not all_signals.empty:
            for i in range(len(data)):
                row = all_signals.iloc[i] if i < len(all_signals) else None
                if row is not None:
                    buy_count = (row == 'buy').sum()
                    sell_count = (row == 'sell').sum()
                    
                    if buy_count >= 2:
                        data['combined_signal'].iloc[i] = 'buy'
                    elif sell_count >= 2:
                        data['combined_signal'].iloc[i] = 'sell'
        
        data['signal'] = data['combined_signal']
        data['position'] = data['signal'].replace({'buy': 1, 'sell': -1, 'hold': np.nan}).ffill().fillna(0)
        data['strategy_return'] = data['position'].shift(1) * data['close'].pct_change()
        data['cumulative_return'] = (1 + data['strategy_return']).cumprod()
        
        return data
    
    def get_name(self):
        return "组合策略 (MA+MACD+RSI+布林带)"
