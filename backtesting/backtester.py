import pandas as pd
import numpy as np
from datetime import datetime

class Backtester:
    def __init__(self, initial_capital=100000, transaction_cost=0.001):
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
    
    def run_backtest(self, strategy, data):
        if data.empty:
            return None
        
        result = strategy.backtest(data)
        if result.empty:
            return None
        
        result['cash'] = self.initial_capital
        result['holdings'] = 0
        result['total_assets'] = self.initial_capital
        
        position = 0
        cash = self.initial_capital
        holdings = 0
        
        for i in range(len(result)):
            date = result.index[i]
            price = result['close'].iloc[i]
            signal = result['signal'].iloc[i]
            
            if signal == 'buy' and position == 0:
                shares = cash // price
                cost = shares * price
                fee = cost * self.transaction_cost
                cash -= cost + fee
                holdings = shares
                position = 1
            elif signal == 'sell' and position == 1:
                revenue = holdings * price
                fee = revenue * self.transaction_cost
                cash += revenue - fee
                holdings = 0
                position = 0
            
            result['cash'].iloc[i] = cash
            result['holdings'].iloc[i] = holdings * price
            result['total_assets'].iloc[i] = cash + holdings * price
        
        return result
    
    def calculate_metrics(self, result):
        if result is None or result.empty:
            return {}
        
        total_return = (result['total_assets'].iloc[-1] - self.initial_capital) / self.initial_capital * 100
        
        daily_returns = result['total_assets'].pct_change().dropna()
        sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std()
        
        max_drawdown = 0
        peak = self.initial_capital
        for value in result['total_assets']:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        winning_trades = len(result[result['signal'] == 'buy'])
        losing_trades = len(result[result['signal'] == 'sell'])
        
        return {
            'total_return': round(total_return, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'total_trades': winning_trades + losing_trades,
            'final_value': round(result['total_assets'].iloc[-1], 2),
            'cagr': self._calculate_cagr(result),
            'win_rate': round((winning_trades / (winning_trades + losing_trades)) * 100, 2) if (winning_trades + losing_trades) > 0 else 0
        }
    
    def _calculate_cagr(self, result):
        if result.empty:
            return 0
        
        start_date = result.index[0]
        end_date = result.index[-1]
        years = (end_date - start_date).days / 365.25
        final_value = result['total_assets'].iloc[-1]
        
        if years > 0 and final_value > 0:
            return round(((final_value / self.initial_capital) ** (1 / years) - 1) * 100, 2)
        return 0
    
    def compare_strategies(self, strategies, data):
        results = []
        
        for strategy in strategies:
            result = self.run_backtest(strategy, data)
            if result is not None:
                metrics = self.calculate_metrics(result)
                metrics['strategy'] = strategy.get_name()
                results.append(metrics)
        
        return pd.DataFrame(results)
