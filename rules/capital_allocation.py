import json
import os
from datetime import datetime

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../data/config.json')

class CapitalAllocation:
    def __init__(self):
        self.aggressive_ratio = 0.2
        self.conservative_ratio = 0.4
        self.reserve_ratio = 0.4
        
        self.aggressive_threshold = 0.7
        self.conservative_threshold = 0.5
        
        self.load_config()
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                if 'allocation' in config:
                    self.aggressive_ratio = config['allocation'].get('aggressive_ratio', 0.3)
                    self.conservative_ratio = config['allocation'].get('conservative_ratio', 0.5)
                    self.reserve_ratio = config['allocation'].get('reserve_ratio', 0.2)
                    self.aggressive_threshold = config['allocation'].get('aggressive_threshold', 0.7)
                    self.conservative_threshold = config['allocation'].get('conservative_threshold', 0.5)
    
    def save_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        config['allocation'] = {
            'aggressive_ratio': self.aggressive_ratio,
            'conservative_ratio': self.conservative_ratio,
            'reserve_ratio': self.reserve_ratio,
            'aggressive_threshold': self.aggressive_threshold,
            'conservative_threshold': self.conservative_threshold
        }
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    def analyze_stock_style(self, stock_data, news_sentiment, technical_score):
        scores = []
        
        volume_change = 0
        if len(stock_data) > 20:
            recent_volume = stock_data['volume'][-5:].mean()
            avg_volume = stock_data['volume'][-20:].mean()
            volume_change = (recent_volume - avg_volume) / avg_volume if avg_volume > 0 else 0
        scores.append(min(volume_change, 2))
        
        price_change = 0
        if len(stock_data) > 5:
            recent_price = stock_data['close'][-5:]
            price_change = (recent_price.iloc[-1] - recent_price.iloc[0]) / recent_price.iloc[0]
        scores.append(min(price_change * 10, 2))
        
        scores.append(news_sentiment)
        
        style_score = sum(scores) / len(scores)
        
        if style_score >= self.aggressive_threshold:
            return 'aggressive', style_score, '热点强势股，适合激进策略'
        elif style_score >= self.conservative_threshold:
            return 'mixed', style_score, '均衡型股票，可灵活配置'
        else:
            return 'conservative', style_score, '稳健型股票，适合长线投资'
    
    def calculate_allocation(self, total_capital, portfolio_value, recommendations):
        available_cash = total_capital - portfolio_value
        
        aggressive_amount = available_cash * self.aggressive_ratio
        conservative_amount = available_cash * self.conservative_ratio
        reserve_amount = available_cash * self.reserve_ratio
        
        aggressive_stocks = []
        conservative_stocks = []
        
        for rec in recommendations:
            style, score, reason = 'mixed', 0.5, '默认分类'
            
            combined_score = rec.get('combined_score', 0)
            final_signal = rec.get('final_signal', 'hold')
            
            if final_signal != 'buy':
                continue
            
            if rec.get('type') == '涨幅榜' or rec.get('type') == '龙虎榜热门':
                style = 'aggressive'
                reason = '热点强势股，短线机会'
            elif combined_score >= 1.0:
                style = 'aggressive'
                reason = '高评分股票，短期上涨潜力大'
            elif rec.get('type') == '产业链潜力股':
                style = 'conservative'
                reason = '产业链潜力股，基本面支撑'
            elif rec.get('type') == '权重股':
                style = 'conservative'
                reason = '权重股，稳定性高'
            else:
                style = 'conservative'
                reason = '稳健型股票，适合长线投资'
            
            if style == 'aggressive':
                aggressive_stocks.append({**rec, 'style': style, 'style_reason': reason})
            else:
                conservative_stocks.append({**rec, 'style': 'conservative', 'style_reason': reason})
        
        aggressive_stocks.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        conservative_stocks.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        
        aggressive_suggestions = []
        remaining_aggressive = aggressive_amount
        
        for rec in aggressive_stocks[:3]:
            if remaining_aggressive <= 0:
                break
            
            price = rec.get('current_price', 10)
            if price <= 0:
                continue
            
            quantity = int(remaining_aggressive * 0.5 / price) // 100 * 100
            
            if quantity >= 100:
                actual_amount = quantity * price
                aggressive_suggestions.append({
                    **rec,
                    'suggested_quantity': quantity,
                    'suggested_amount': round(actual_amount, 2),
                    'allocation_type': '激进',
                    'risk_level': '高'
                })
                remaining_aggressive -= actual_amount
        
        conservative_suggestions = []
        remaining_conservative = conservative_amount
        
        for rec in conservative_stocks[:5]:
            if remaining_conservative <= 0:
                break
            
            price = rec.get('current_price', 10)
            if price <= 0:
                continue
            
            quantity = int(remaining_conservative * 0.4 / price) // 100 * 100
            
            if quantity >= 100:
                actual_amount = quantity * price
                conservative_suggestions.append({
                    **rec,
                    'suggested_quantity': quantity,
                    'suggested_amount': round(actual_amount, 2),
                    'allocation_type': '稳健',
                    'risk_level': '低'
                })
                remaining_conservative -= actual_amount
        
        return {
            'total_capital': round(total_capital, 2),
            'portfolio_value': round(portfolio_value, 2),
            'available_cash': round(available_cash, 2),
            'aggressive_amount': round(aggressive_amount, 2),
            'conservative_amount': round(conservative_amount, 2),
            'reserve_amount': round(reserve_amount, 2),
            'aggressive_suggestions': aggressive_suggestions,
            'conservative_suggestions': conservative_suggestions,
            'allocation_summary': {
                '激进策略': f'¥{round(aggressive_amount, 2)} ({round(self.aggressive_ratio * 100, 1)}%) - 短线追高、热点强势股',
                '稳健策略': f'¥{round(conservative_amount, 2)} ({round(self.conservative_ratio * 100, 1)}%) - 基本面投资、产业链潜力股',
                '预留资金': f'¥{round(reserve_amount, 2)} ({round(self.reserve_ratio * 100, 1)}%) - 应对突发机会'
            }
        }
    
    def update_ratios(self, aggressive_ratio, conservative_ratio, reserve_ratio):
        total = aggressive_ratio + conservative_ratio + reserve_ratio
        if abs(total - 1.0) > 0.01:
            return False, '比例总和必须等于1'
        
        self.aggressive_ratio = aggressive_ratio
        self.conservative_ratio = conservative_ratio
        self.reserve_ratio = reserve_ratio
        self.save_config()
        return True, '配置已更新'