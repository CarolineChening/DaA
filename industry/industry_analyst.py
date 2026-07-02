from .chain_data import get_industry_chains, get_industry_data, find_potential_stocks, analyze_chain
import random

class IndustryAnalyst:
    def __init__(self):
        pass
    
    def get_industries(self):
        return get_industry_chains()
    
    def get_industry_analysis(self, industry_name):
        data = get_industry_data(industry_name)
        if not data:
            return None
        
        return {
            'name': industry_name,
            'analysis': {
                'subsectors': data['subsectors'],
                'characteristics': data['characteristics'],
                'key_metrics': data['key_metrics'],
                'risks': data['risks'],
                'industry_chain': {
                    '上游': [item['name'] for item in data['chain']['上游']],
                    '中游': [item['name'] for item in data['chain']['中游']],
                    '下游': [item['name'] for item in data['chain']['下游']]
                }
            },
            'outlook': {
                'trend': data['trend'],
                'drivers': data['drivers'],
                'challenges': data['challenges'],
                'investment_themes': data['investment_themes']
            },
            'chain_details': data['chain'],
            'potential_stocks': data['chain']['潜力股']
        }
    
    def recommend_stocks_based_on_chain(self, industry_name=None, limit=10):
        all_potential = find_potential_stocks(industry_name)
        
        recommendations = []
        for stock in all_potential[:limit]:
            recommendations.append({
                'name': stock['name'],
                'symbol': stock['symbol'],
                'industry': stock.get('industry', industry_name) if industry_name else stock.get('industry', '未知'),
                'reason': stock['reason'],
                'potential': stock['potential'],
                'investment_rating': self._calculate_rating(stock)
            })
        
        return recommendations
    
    def _calculate_rating(self, stock):
        potential_score = {'高': 5, '中高': 4, '中': 3}[stock['potential']]
        return min(5, potential_score)
    
    def analyze_industry_trend(self, industry_name):
        data = get_industry_data(industry_name)
        if not data:
            return None
        
        trend_score = {'上升': 5, '中性': 3, '下降': 1}[data['trend']]
        
        return {
            'industry': industry_name,
            'trend': data['trend'],
            'trend_score': trend_score,
            'drivers': data['drivers'],
            'challenges': data['challenges'],
            'investment_themes': data['investment_themes']
        }
    
    def get_all_potential_stocks(self):
        return find_potential_stocks()
    
    def get_chain_details(self, industry_name):
        data = get_industry_data(industry_name)
        if not data:
            return None
        
        return data['chain']
