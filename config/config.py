import os
import json
from dotenv import load_dotenv
from utils.time_utils import get_beijing_time, format_beijing_date

class Config:
    def __init__(self):
        load_dotenv()
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        self.portfolio_file = os.path.join(self.data_dir, 'portfolio.json')
        
        self.PORTFOLIO = self.load_portfolio()
        
        self.INITIAL_CAPITAL = int(os.getenv('INITIAL_CAPITAL', 100000))
        self.TRANSACTION_COST = float(os.getenv('TRANSACTION_COST', 0.001))
        
        self.MORNING_REMINDER_TIME = os.getenv('MORNING_REMINDER_TIME', '10:00')
        self.AFTERNOON_REMINDER_TIME = os.getenv('AFTERNOON_REMINDER_TIME', '14:30')
        
        self.DATA_FETCH_INTERVAL = int(os.getenv('DATA_FETCH_INTERVAL', 60))
        
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    def load_portfolio(self):
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return [
            {'symbol': 'AAPL', 'name': '苹果公司', 'quantity': 100, 'cost_price': 150},
            {'symbol': 'MSFT', 'name': '微软', 'quantity': 50, 'cost_price': 300},
            {'symbol': 'GOOGL', 'name': '谷歌', 'quantity': 30, 'cost_price': 140},
            {'symbol': 'NVDA', 'name': '英伟达', 'quantity': 20, 'cost_price': 800},
            {'symbol': 'META', 'name': 'Meta', 'quantity': 40, 'cost_price': 500}
        ]
    
    def save_portfolio(self):
        with open(self.portfolio_file, 'w') as f:
            json.dump(self.PORTFOLIO, f, indent=2, ensure_ascii=False)
    
    def get_portfolio(self):
        return self.PORTFOLIO
    
    def update_portfolio(self, portfolio):
        self.PORTFOLIO = portfolio
        self.save_portfolio()
    
    def add_stock_to_portfolio(self, stock):
        stock['purchase_date'] = format_beijing_date()
        self.PORTFOLIO.append(stock)
        self.save_portfolio()
    
    def add_position_to_stock(self, symbol, quantity, price):
        for stock in self.PORTFOLIO:
            if stock['symbol'].upper() == symbol.upper():
                old_quantity = stock['quantity']
                old_cost_price = stock['cost_price']
                new_quantity = old_quantity + quantity
                new_cost_price = (old_quantity * old_cost_price + quantity * price) / new_quantity
                stock['quantity'] = new_quantity
                stock['cost_price'] = round(new_cost_price, 2)
                self.save_portfolio()
                return
        raise ValueError(f"股票 {symbol} 不在持仓中")
    
    def remove_stock_from_portfolio(self, symbol):
        self.PORTFOLIO = [s for s in self.PORTFOLIO if s['symbol'] != symbol]
        self.save_portfolio()
