from datetime import datetime
from utils.time_utils import get_beijing_time, format_beijing_time
from .capital_allocation import CapitalAllocation

class TradingRules:
    def __init__(self):
        self.trailing_stop_pct = 10
        self.max_position_size = 0.2
        self.max_daily_trades = 3
        self.total_capital = 100000.0
        
        self.today_trades = []
        
        self.capital_allocation = CapitalAllocation()
    
    def set_parameters(self, params):
        if 'trailing_stop_pct' in params:
            self.trailing_stop_pct = params['trailing_stop_pct']
        if 'max_position_size' in params:
            self.max_position_size = params['max_position_size']
        if 'max_daily_trades' in params:
            self.max_daily_trades = params['max_daily_trades']
        if 'total_capital' in params:
            self.total_capital = params['total_capital']
    
    def check_trailing_stop(self, current_price, highest_price):
        if highest_price <= 0:
            return False, 0, 0
        
        trailing_stop_price = highest_price * (1 - self.trailing_stop_pct / 100)
        is_triggered = current_price <= trailing_stop_price
        loss_from_high = (highest_price - current_price) / highest_price * 100
        
        return is_triggered, trailing_stop_price, loss_from_high
    
    def check_position_size(self, current_value, portfolio_total, current_position=0):
        new_position = current_position + current_value
        return new_position <= portfolio_total * self.max_position_size
    
    def can_trade_today(self):
        today = get_beijing_time().date()
        today_trade_count = sum(1 for t in self.today_trades if t['date'] == today)
        return today_trade_count < self.max_daily_trades
    
    def record_trade(self, symbol, action, price, quantity):
        today = get_beijing_time().date()
        
        self.today_trades.append({
            'date': today,
            'symbol': symbol,
            'action': action,
            'price': price,
            'quantity': quantity,
            'time': get_beijing_time()
        })
        
        return True
    
    def analyze_position(self, symbol, current_price, cost_price, highest_price=None):
        results = []
        
        if highest_price is None:
            highest_price = max(current_price, cost_price)
        
        trailing_stop_triggered, trailing_stop_price, loss_from_high = self.check_trailing_stop(current_price, highest_price)
        if trailing_stop_triggered:
            results.append({
                'rule': '追踪止损',
                'action': 'sell',
                'reason': f'从最高点 {highest_price:.2f} 下跌 {loss_from_high:.1f}%，当前价 {current_price:.2f} 低于追踪止损价 {trailing_stop_price:.2f}，触发止损',
                'priority': 'high',
                'trailing_stop_price': trailing_stop_price,
                'highest_price': highest_price
            })
        
        return results
    
    def get_rules_summary(self):
        return {
            '总资金': f'{self.total_capital:.2f} 元',
            '追踪止损': f'{self.trailing_stop_pct}% (最高价)',
            '最大仓位': f'{self.max_position_size * 100}%',
            '每日最大交易次数': self.max_daily_trades
        }
    
    def calculate_deployment_suggestion(self, available_cash, recommendations):
        allocation = self.capital_allocation.calculate_allocation(
            self.total_capital,
            self.total_capital - available_cash,
            recommendations
        )
        
        portfolio_value = self.total_capital - available_cash
        max_total_position = self.total_capital * 0.5
        remaining_capacity = max_total_position - portfolio_value
        
        if remaining_capacity <= 0:
            return {
                'available_cash': round(available_cash, 2),
                'total_capital': round(self.total_capital, 2),
                'suggestions': [],
                'remaining_after_deployment': available_cash,
                'deployment_ratio': 0,
                'deployable_cash': 0,
                'allocation_summary': {
                    '提示': f'当前仓位 {round(portfolio_value / self.total_capital * 100, 1)}%，已达上限50%，建议观望'
                },
                'aggressive_amount': 0,
                'conservative_amount': 0,
                'reserve_amount': available_cash,
                'max_position_limit': 0.5,
                'current_position_pct': round(portfolio_value / self.total_capital * 100, 1),
                'remaining_capacity': 0
            }
        
        all_suggestions = []
        total_suggested = 0
        
        for rec in allocation['aggressive_suggestions']:
            if total_suggested >= remaining_capacity:
                break
            
            suggested_amount = rec.get('suggested_amount', 0)
            actual_amount = min(suggested_amount, remaining_capacity - total_suggested)
            
            if actual_amount > 0:
                price = rec.get('current_price', 10)
                quantity = int(actual_amount / price) // 100 * 100
                actual_amount = quantity * price
                
                all_suggestions.append({
                    'symbol': rec.get('symbol', ''),
                    'name': rec.get('name', ''),
                    'current_price': rec.get('current_price', 0),
                    'suggested_quantity': quantity,
                    'suggested_amount': round(actual_amount, 2),
                    'allocation_pct': round(actual_amount / self.total_capital * 100, 2),
                    'reason': rec.get('reasoning', ['综合评分较高']),
                    'combined_score': rec.get('combined_score', 0),
                    'signal': rec.get('final_signal', 'buy'),
                    'allocation_type': '激进',
                    'risk_level': '高',
                    'style_reason': rec.get('style_reason', '')
                })
                total_suggested += actual_amount
        
        for rec in allocation['conservative_suggestions']:
            if total_suggested >= remaining_capacity:
                break
            
            suggested_amount = rec.get('suggested_amount', 0)
            actual_amount = min(suggested_amount, remaining_capacity - total_suggested)
            
            if actual_amount > 0:
                price = rec.get('current_price', 10)
                quantity = int(actual_amount / price) // 100 * 100
                actual_amount = quantity * price
                
                all_suggestions.append({
                    'symbol': rec.get('symbol', ''),
                    'name': rec.get('name', ''),
                    'current_price': rec.get('current_price', 0),
                    'suggested_quantity': quantity,
                    'suggested_amount': round(actual_amount, 2),
                    'allocation_pct': round(actual_amount / self.total_capital * 100, 2),
                    'reason': rec.get('reasoning', ['综合评分较高']),
                    'combined_score': rec.get('combined_score', 0),
                    'signal': rec.get('final_signal', 'buy'),
                    'allocation_type': '稳健',
                    'risk_level': '低',
                    'style_reason': rec.get('style_reason', '')
                })
                total_suggested += actual_amount
        
        new_position_pct = round((portfolio_value + total_suggested) / self.total_capital * 100, 1)
        
        allocation_summary = {
            '激进策略': f'¥{round(allocation["aggressive_amount"], 2)} ({round(self.capital_allocation.aggressive_ratio * 100, 1)}%) - 短线追高、热点强势股',
            '稳健策略': f'¥{round(allocation["conservative_amount"], 2)} ({round(self.capital_allocation.conservative_ratio * 100, 1)}%) - 基本面投资、产业链潜力股',
            '预留资金': f'¥{round(allocation["reserve_amount"], 2)} ({round(self.capital_allocation.reserve_ratio * 100, 1)}%) - 应对突发机会',
            '仓位控制': f'当前 {round(portfolio_value / self.total_capital * 100, 1)}% → 建议 {new_position_pct}%（上限50%）'
        }
        
        if not all_suggestions:
            allocation_summary['操作建议'] = '✓ 当前无明确买入信号，持有现金等待更佳机会是明智选择'
        else:
            allocation_summary['操作建议'] = '⚡ 有买入信号，但观望等待更好时机往往更优；若参与建议轻仓试错'
        
        return {
            'available_cash': round(available_cash, 2),
            'total_capital': round(self.total_capital, 2),
            'suggestions': all_suggestions,
            'remaining_after_deployment': round(available_cash - total_suggested, 2),
            'deployment_ratio': round(total_suggested / available_cash, 2) if available_cash > 0 else 0,
            'deployable_cash': round(total_suggested, 2),
            'allocation_summary': allocation_summary,
            'aggressive_amount': round(allocation['aggressive_amount'], 2),
            'conservative_amount': round(allocation['conservative_amount'], 2),
            'reserve_amount': round(allocation['reserve_amount'], 2),
            'max_position_limit': 0.5,
            'current_position_pct': round(portfolio_value / self.total_capital * 100, 1),
            'remaining_capacity': round(remaining_capacity, 2),
            'new_position_pct': new_position_pct
        }