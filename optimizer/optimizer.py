import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from datetime import datetime, timedelta
import pickle
import os

class StrategyOptimizer:
    def __init__(self, strategies):
        self.strategies = strategies
        self.models = {}
        self.best_params = {}
        self.model_path = 'models/'
        os.makedirs(self.model_path, exist_ok=True)
    
    def generate_features(self, data, sentiment_score=0):
        features = pd.DataFrame()
        
        data = data.copy()
        data['daily_return'] = data['close'].pct_change()
        data['volatility'] = data['daily_return'].rolling(window=20).std() * np.sqrt(252)
        
        data['sma_5'] = data['close'].rolling(window=5).mean()
        data['sma_20'] = data['close'].rolling(window=20).mean()
        data['sma_50'] = data['close'].rolling(window=50).mean()
        
        ema_fast = data['close'].ewm(span=12, adjust=False).mean()
        ema_slow = data['close'].ewm(span=26, adjust=False).mean()
        data['macd'] = ema_fast - ema_slow
        
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        data['bb_mid'] = data['close'].rolling(window=20).mean()
        data['bb_std'] = data['close'].rolling(window=20).std()
        data['bb_upper'] = data['bb_mid'] + (data['bb_std'] * 2)
        data['bb_lower'] = data['bb_mid'] - (data['bb_std'] * 2)
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_mid']
        
        data['momentum'] = data['close'] / data['close'].shift(20) - 1
        data['volume_change'] = data['volume'].pct_change()
        
        features['sma_ratio'] = data['sma_5'] / data['sma_20']
        features['macd_signal'] = data['macd']
        features['rsi'] = data['rsi']
        features['bb_width'] = data['bb_width']
        features['momentum'] = data['momentum']
        features['volatility'] = data['volatility']
        features['volume_change'] = data['volume_change']
        features['sentiment'] = sentiment_score
        
        features['target'] = (data['close'].shift(-1) > data['close']).astype(int)
        
        return features.dropna()
    
    def train_model(self, symbol, data, sentiment_scores=None):
        if sentiment_scores is None:
            sentiment_scores = [0] * len(data)
        
        features = self.generate_features(data, sentiment_scores[-len(data):] if len(sentiment_scores) >= len(data) else 0)
        
        if len(features) < 100:
            print("数据不足，无法训练模型")
            return None
        
        X = features.drop('target', axis=1)
        y = features['target']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"模型训练完成，准确率: {accuracy:.2f}")
        
        self.models[symbol] = model
        
        model_file = os.path.join(self.model_path, f"{symbol}_model.pkl")
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        
        return accuracy
    
    def predict_signal(self, symbol, data, sentiment_score=0):
        if symbol not in self.models:
            model_file = os.path.join(self.model_path, f"{symbol}_model.pkl")
            if os.path.exists(model_file):
                with open(model_file, 'rb') as f:
                    self.models[symbol] = pickle.load(f)
            else:
                return 'hold'
        
        features = self.generate_features(data.tail(25), sentiment_score)
        
        if features.empty:
            return 'hold'
        
        latest_features = features.drop('target', axis=1).iloc[-1:]
        
        try:
            prediction = self.models[symbol].predict(latest_features)[0]
            return 'buy' if prediction == 1 else 'sell'
        except Exception as e:
            print(f"预测失败: {e}")
            return 'hold'
    
    def optimize_strategy_params(self, strategy_name, data):
        param_grids = {
            'MovingAverageStrategy': {
                'short_window': [5, 10, 15],
                'long_window': [20, 30, 50]
            },
            'RSIStrategy': {
                'period': [10, 14, 20],
                'overbought': [65, 70, 75],
                'oversold': [25, 30, 35]
            },
            'MACDStrategy': {
                'fast_period': [10, 12, 14],
                'slow_period': [24, 26, 28],
                'signal_period': [8, 9, 10]
            },
            'BollingerBandsStrategy': {
                'period': [15, 20, 25],
                'num_std': [1.5, 2.0, 2.5]
            }
        }
        
        best_score = -float('inf')
        best_params = {}
        
        grid = param_grids.get(strategy_name, {})
        
        if not grid:
            return best_params
        
        from itertools import product
        
        keys = list(grid.keys())
        values = list(grid.values())
        
        for combination in product(*values):
            params = dict(zip(keys, combination))
            
            try:
                strategy = self._create_strategy(strategy_name, params)
                result = strategy.backtest(data)
                
                if not result.empty and 'cumulative_return' in result.columns:
                    final_return = result['cumulative_return'].iloc[-1]
                    
                    if final_return > best_score:
                        best_score = final_return
                        best_params = params
            except Exception as e:
                continue
        
        if best_params:
            print(f"优化完成，最优参数: {best_params}")
        
        return best_params
    
    def _create_strategy(self, name, params):
        from strategies import (
            MovingAverageStrategy,
            MACDStrategy,
            RSIStrategy,
            BollingerBandsStrategy
        )
        
        strategy_map = {
            'MovingAverageStrategy': MovingAverageStrategy,
            'MACDStrategy': MACDStrategy,
            'RSIStrategy': RSIStrategy,
            'BollingerBandsStrategy': BollingerBandsStrategy
        }
        
        strategy_class = strategy_map.get(name)
        if strategy_class:
            return strategy_class(**params)
        return None
    
    def adaptive_learning(self, symbol, data, sentiment_scores):
        accuracy = self.train_model(symbol, data, sentiment_scores)
        
        if accuracy is not None and accuracy < 0.55:
            print("模型准确率较低，正在重新优化...")
            self.optimize_all_strategies(data)
    
    def optimize_all_strategies(self, data):
        for strategy in self.strategies:
            name = strategy.__class__.__name__
            best_params = self.optimize_strategy_params(name, data)
            
            if best_params:
                self.best_params[name] = best_params
                print(f"策略 {name} 优化完成")
