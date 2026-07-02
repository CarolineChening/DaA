import requests
from datetime import datetime, timedelta
import random
from utils.time_utils import get_beijing_time

class ResearchAnalyst:
    def __init__(self):
        self.cache = {}
    
    def fetch_research_reports(self, symbol):
        reports = []
        
        stock_name_map = {
            '600111': '北方稀土', '600519': '贵州茅台', '002920': '德赛西威',
            '300750': '宁德时代', '002594': '比亚迪', '601012': '隆基绿能',
            '600276': '恒瑞医药', '000858': '五粮液', '601318': '中国平安',
            '600036': '招商银行', '000333': '美的集团', '600887': '伊利股份',
            '300059': '东方财富', '002460': '赣锋锂业', '002566': '天齐锂业'
        }
        
        stock_name = stock_name_map.get(str(symbol).replace('.SS', '').replace('.SZ', ''), str(symbol))
        
        mock_reports = [
            {
                'institution': '中信证券',
                'title': f'{stock_name}深度报告：行业景气延续，业绩增长可期',
                'view': '买入',
                'target_price': None,
                'date': (get_beijing_time() - timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d'),
                'summary': f'我们看好{stock_name}在行业高景气周期中的表现，预计公司业绩将保持稳健增长。'
            },
            {
                'institution': '华泰证券',
                'title': f'{stock_name}跟踪报告：Q2业绩符合预期',
                'view': '增持',
                'target_price': None,
                'date': (get_beijing_time() - timedelta(days=random.randint(1, 14))).strftime('%Y-%m-%d'),
                'summary': f'{stock_name}Q2业绩符合市场预期，维持增持评级。'
            },
            {
                'institution': '国泰君安',
                'title': f'{stock_name}投资价值分析',
                'view': '买入',
                'target_price': None,
                'date': (get_beijing_time() - timedelta(days=random.randint(1, 21))).strftime('%Y-%m-%d'),
                'summary': f'{stock_name}具备长期投资价值，建议逢低布局。'
            }
        ]
        
        return mock_reports
    
    def get_consensus_view(self, symbol):
        reports = self.fetch_research_reports(symbol)
        
        buy_count = sum(1 for r in reports if r['view'] in ['买入', '增持'])
        hold_count = sum(1 for r in reports if r['view'] == '持有')
        sell_count = sum(1 for r in reports if r['view'] in ['卖出', '减持'])
        
        total = len(reports)
        if total == 0:
            return {
                'view': '中性',
                'sentiment_score': 0,
                'report_count': 0,
                'buy_count': 0,
                'hold_count': 0,
                'sell_count': 0
            }
        
        if buy_count >= 2:
            view = '看多'
            sentiment_score = 0.78
        elif sell_count >= 2:
            view = '看空'
            sentiment_score = -0.5
        elif hold_count >= total / 2:
            view = '中性'
            sentiment_score = 0
        else:
            view = '看多' if buy_count > sell_count else '看空'
            sentiment_score = 0.3 if buy_count > sell_count else -0.3
        
        return {
            'view': view,
            'sentiment_score': sentiment_score,
            'report_count': total,
            'buy_count': buy_count,
            'hold_count': hold_count,
            'sell_count': sell_count
        }
    
    def get_snowball_opinions(self, symbol, count=3):
        stock_name_map = {
            '600111': '北方稀土', '600519': '贵州茅台', '002920': '德赛西威',
            '300750': '宁德时代', '002594': '比亚迪', '601012': '隆基绿能',
            '600276': '恒瑞医药', '000858': '五粮液', '601318': '中国平安'
        }
        
        stock_name = stock_name_map.get(str(symbol).replace('.SS', '').replace('.SZ', ''), str(symbol))
        
        opinions = [
            {
                'author': '价值投资大师',
                'avatar': '',
                'followers': '50万',
                'view': '看多',
                'content': f'{stock_name}作为行业龙头，具备长期投资价值。当前估值合理，建议长期持有。',
                'likes': random.randint(500, 2000),
                'time': '2小时前'
            },
            {
                'author': '趋势交易者',
                'avatar': '',
                'followers': '30万',
                'view': '看多',
                'content': f'{stock_name}技术形态良好，成交量持续放大，有望继续上行。',
                'likes': random.randint(300, 1500),
                'time': '5小时前'
            },
            {
                'author': '基本面研究员',
                'avatar': '',
                'followers': '25万',
                'view': '中性',
                'content': f'{stock_name}业绩符合预期，但需要关注行业竞争格局变化。',
                'likes': random.randint(200, 1000),
                'time': '昨天'
            }
        ]
        
        return opinions[:count]
    
    def get_institutional_views(self):
        return [
            {'institution': '中信证券', 'strategy': '看多A股', 'reason': '经济复苏预期增强，流动性环境友好'},
            {'institution': '华泰证券', 'strategy': '中性偏多', 'reason': '市场处于震荡格局，建议均衡配置'},
            {'institution': '国泰君安', 'strategy': '谨慎乐观', 'reason': '关注政策落地和经济数据'},
            {'institution': '海通证券', 'strategy': '看多', 'reason': '估值处于历史低位，具备配置价值'},
            {'institution': '广发证券', 'strategy': '中性', 'reason': '内外因素交织，市场等待方向'}
        ]
