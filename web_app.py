#!/usr/bin/env python3

import os
import sys
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.time_utils import get_beijing_time, format_beijing_time, get_beijing_timestamp

from flask import Flask, render_template, request, jsonify
from config import Config
from data import DataFetcher, NewsFetcher, FinancialFetcher, XueQiuFetcher, DynamicWatchlist, ConceptData, DragonTigerFetcher, IndustryData
from strategies import (
    MovingAverageStrategy,
    MACDStrategy,
    RSIStrategy,
    BollingerBandsStrategy,
    CombinedStrategy,
    VolumePriceRatioStrategy,
    EMACrossoverStrategy,
    NineTurnsStrategy
)
from rules import TradingRules
from research import ResearchAnalyst
from research.influencer_analyst import influencer_analyst
from industry import IndustryAnalyst
from industry.chain_data import industry_chains
from utils.scheduler import scheduler, price_alert
from utils.remote_access import remote_access
import json
import socket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stock_strategy_key'

config = Config()
data_fetcher = DataFetcher()
news_fetcher = NewsFetcher()
financial_fetcher = FinancialFetcher()
xueqiu_fetcher = XueQiuFetcher()
watchlist_fetcher = DynamicWatchlist()
concept_data = ConceptData()
dragon_tiger_fetcher = DragonTigerFetcher()
industry_data = IndustryData()
strategies = [
    MovingAverageStrategy(short_window=5, long_window=20),
    EMACrossoverStrategy(short_period=12, long_period=26),
    MACDStrategy(fast_period=12, slow_period=26, signal_period=9),
    RSIStrategy(period=14, overbought=70, oversold=30),
    BollingerBandsStrategy(period=20, num_std=2),
    VolumePriceRatioStrategy(period=20, threshold=1.5),
    NineTurnsStrategy(),
    CombinedStrategy()
]
trading_rules = TradingRules()
research_analyst = ResearchAnalyst()
industry_analyst = IndustryAnalyst()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/api/portfolio')
def get_portfolio():
    portfolio = config.get_portfolio()
    portfolio_data = data_fetcher.get_portfolio_data(portfolio)
    
    total_value = sum(p['market_value'] for p in portfolio_data)
    total_cost = sum(p['quantity'] * p['cost_price'] for p in portfolio_data)
    total_profit = sum(p['profit'] for p in portfolio_data)
    
    return jsonify({
        'stocks': portfolio_data,
        'total_value': round(total_value, 2),
        'total_cost': round(total_cost, 2),
        'total_profit': round(total_profit, 2),
        'total_profit_percent': round((total_profit / total_cost * 100) if total_cost > 0 else 0, 2)
    })

@app.route('/api/add_stock', methods=['POST'])
def add_stock():
    data = request.json
    config.add_stock_to_portfolio({
        'symbol': data['symbol'].upper(),
        'name': data['name'],
        'quantity': int(data['quantity']),
        'cost_price': float(data['cost_price'])
    })
    return jsonify({'success': True})

@app.route('/api/add_position', methods=['POST'])
def add_position():
    data = request.json
    symbol = data['symbol'].upper()
    quantity = int(data['quantity'])
    price = float(data['price'])
    config.add_position_to_stock(symbol, quantity, price)
    return jsonify({'success': True})

@app.route('/api/remove_stock', methods=['POST'])
def remove_stock():
    symbol = request.json['symbol']
    config.remove_stock_from_portfolio(symbol)
    return jsonify({'success': True})

@app.route('/api/analysis')
def get_analysis():
    portfolio = config.get_portfolio()
    news = news_fetcher.fetch_general_news()
    market_sentiment = news_fetcher.get_market_sentiment()
    
    def analyze_stock(stock):
        try:
            data = data_fetcher.get_stock_data(stock['symbol'], period='1y')
            if data.empty:
                return None
            
            stock_news = news_fetcher.fetch_stock_news(stock['symbol'])
            stock_sentiment = news_fetcher.get_stock_sentiment(stock['symbol'])
            research_view = research_analyst.get_consensus_view(stock['symbol'])
            financial_health = financial_fetcher.analyze_financial_health(stock['symbol'])
            
            signals = []
            for strategy in strategies:
                result = strategy.generate_signal(data)
                if isinstance(result, tuple):
                    signal, turn_count = result
                else:
                    signal = result
                    turn_count = 0
                signals.append({
                    'strategy': strategy.get_name(),
                    'signal': signal,
                    'turn_count': int(turn_count)
                })
            
            realtime_data = data_fetcher.get_realtime_price(stock['symbol'])
            current_price = realtime_data['price'] if isinstance(realtime_data, dict) else realtime_data
            if current_price is None:
                current_price = data['close'].iloc[-1] if not data.empty else stock['cost_price']
            
            buy_count = sum(1 for s in signals if s['signal'] == 'buy')
            sell_count = sum(1 for s in signals if s['signal'] == 'sell')
            
            reasoning = []
            
            if stock_sentiment > 0.1:
                reasoning.append(f"个股新闻情绪看多 (得分: {stock_sentiment:.2f})")
            elif stock_sentiment < -0.1:
                reasoning.append(f"个股新闻情绪看空 (得分: {stock_sentiment:.2f})")
            else:
                reasoning.append(f"个股新闻情绪中性 (得分: {stock_sentiment:.2f})")
            
            if research_view['sentiment_score'] > 0.3:
                reasoning.append(f"机构研报观点看多")
            elif research_view['sentiment_score'] < -0.3:
                reasoning.append(f"机构研报观点看空")
            else:
                reasoning.append(f"机构研报观点中性")
            
            if financial_health.get('health_level') == '健康':
                reasoning.append(f"财务状况健康 (评分: {financial_health.get('score', 0)}/{financial_health.get('max_score', 6)})")
            elif financial_health.get('health_level') == '一般':
                reasoning.append(f"财务状况一般 (评分: {financial_health.get('score', 0)}/{financial_health.get('max_score', 6)})")
            else:
                reasoning.append(f"财务状况存在风险 (评分: {financial_health.get('score', 0)}/{financial_health.get('max_score', 6)})")
            
            if buy_count >= 2:
                reasoning.append(f"技术指标: {buy_count}个策略发出买入信号")
            elif sell_count >= 2:
                reasoning.append(f"技术指标: {sell_count}个策略发出卖出信号")
            else:
                reasoning.append(f"技术指标: 信号不明确")
            
            combined_score = 0
            if buy_count >= 2:
                combined_score += 1
            if sell_count >= 2:
                combined_score -= 1
            if stock_sentiment > 0.1:
                combined_score += 0.5
            elif stock_sentiment < -0.1:
                combined_score -= 0.5
            if research_view['sentiment_score'] > 0.3:
                combined_score += 0.4
            elif research_view['sentiment_score'] < -0.3:
                combined_score -= 0.4
            if financial_health.get('health_level') == '健康':
                combined_score += 0.3
            elif financial_health.get('health_level') == '风险':
                combined_score -= 0.3
            
            if combined_score > 0.5:
                final_signal = 'buy'
                conclusion = '技术面偏多，可关注；观望等待更好时机也是合理选择。'
            elif combined_score < -0.5:
                final_signal = 'sell'
                conclusion = '综合分析后，建议卖出该股票。'
            else:
                final_signal = 'hold'
                conclusion = '综合分析后，建议继续持有观察。'
            
            return {
                'symbol': stock['symbol'],
                'name': stock['name'],
                'current_price': round(current_price, 2),
                'cost_price': stock['cost_price'],
                'stock_sentiment': round(stock_sentiment, 2),
                'research_view': research_view.get('view', '中性'),
                'research_sentiment': round(research_view.get('sentiment_score', 0), 2),
                'financial_health': financial_health.get('health_level', '未知'),
                'financial_score': financial_health.get('score', 0),
                'signals': signals,
                'reasoning': reasoning,
                'conclusion': conclusion,
                'final_signal': final_signal,
                'news_summary': [{'title': n['title'], 'sentiment': news_fetcher.analyze_sentiment(n['title'] + ' ' + (n.get('summary', '')))} for n in stock_news[:3]]
            }
        except Exception as e:
            print(f"⚠️ 分析持仓 {stock['symbol']} 失败: {e}")
            return None
    
    results = []
    if portfolio:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(analyze_stock, stock) for stock in portfolio]
            
            for future in concurrent.futures.as_completed(futures, timeout=60):
                result = future.result()
                if result:
                    results.append(result)
    
    return jsonify({
        'market_sentiment': round(market_sentiment, 2),
        'market_news': [{'title': n['title'], 'source': n.get('source', ''), 'sentiment': news_fetcher.analyze_sentiment(n['title'] + ' ' + (n.get('description', '')))} for n in news[:5]],
        'stocks': results
    })

@app.route('/api/market')
def get_market():
    try:
        market_data = data_fetcher.get_market_summary()
        return jsonify(market_data)
    except Exception as e:
        print(f"⚠️ 获取市场数据失败: {e}")
        return jsonify({
            'shanghai': {'index': 0, 'change': 0, 'change_percent': 0},
            'shenzhen': {'index': 0, 'change': 0, 'change_percent': 0},
            'star': {'index': 0, 'change': 0, 'change_percent': 0},
            'hot_concepts': [],
            'market_status': 'closed'
        })

@app.route('/api/news')
def get_news():
    news = news_fetcher.fetch_general_news()
    return jsonify(news[:20])

@app.route('/api/news/highlights')
def get_news_highlights():
    news = news_fetcher.fetch_general_news(count=150)
    highlights = news_fetcher.analyze_today_highlights(news)
    
    top_news = []
    for n in news[:80]:
        top_news.append({
            'title': n['title'],
            'source': n.get('source', ''),
            'description': n.get('description', ''),
            'time': n.get('time', ''),
            'sentiment': news_fetcher.analyze_sentiment(n['title'] + ' ' + (n.get('description', ''))),
            'impact_score': news_fetcher.calculate_news_impact(n)
        })
    
    top_news.sort(key=lambda x: x['impact_score'], reverse=True)
    
    return jsonify({
        'news_count': len(news),
        'highlights': highlights,
        'top_news': top_news[:50]
    })

@app.route('/api/financial/<symbol>')
def get_financial(symbol):
    health = financial_fetcher.analyze_financial_health(symbol)
    earnings = financial_fetcher.analyze_recent_earnings(symbol)
    
    return jsonify({
        'health': health,
        'earnings': earnings
    })

@app.route('/api/research/<symbol>')
def get_research(symbol):
    view = research_analyst.get_consensus_view(symbol)
    return jsonify(view)

@app.route('/api/influencers')
def get_influencers():
    influencers = influencer_analyst.get_influencer_list()
    opinions = influencer_analyst.get_recent_opinions(count=10)
    top_topics = influencer_analyst.get_top_topics(count=5)
    return jsonify({
        'influencers': influencers,
        'recent_opinions': opinions,
        'top_topics': top_topics
    })

@app.route('/api/influencers/stock/<symbol>')
def get_influencer_opinion_for_stock(symbol):
    opinions = influencer_analyst.get_opinion_for_stock(symbol)
    score = influencer_analyst.calculate_influencer_score(symbol)
    return jsonify({
        'opinions': opinions,
        'score': score
    })

@app.route('/api/influencers/search')
def search_influencer_opinions():
    keyword = request.args.get('keyword', '')
    results = influencer_analyst.search_opinions(keyword)
    return jsonify(results)

@app.route('/api/access_info')
def get_access_info():
    public_url = remote_access.get_public_url()
    return jsonify({
        'local_ip': local_ip,
        'port': 8080,
        'local_url': f'http://{local_ip}:8080',
        'localhost_url': 'http://localhost:8080',
        'public_url': public_url,
        'remote_enabled': public_url is not None
    })

@app.route('/api/remote_access/toggle', methods=['POST'])
def toggle_remote_access():
    data = request.json
    action = data.get('action', 'start')
    
    if action == 'start':
        public_url = remote_access.start_ngrok(8080)
        status = remote_access.get_status()
        
        if public_url:
            return jsonify({
                'success': True,
                'public_url': public_url,
                'message': f'远程访问已开启: {public_url}'
            })
        elif not status['authtoken_configured']:
            return jsonify({
                'success': False,
                'message': '请先配置ngrok认证token',
                'need_authtoken': True,
                'last_error': status.get('last_error')
            })
        else:
            return jsonify({
                'success': False,
                'message': '远程访问启动失败',
                'last_error': status.get('last_error'),
                'help': '手机不需要VPN，但需要配置有效的ngrok认证token。请访问 https://dashboard.ngrok.com/get-started/your-authtoken 获取'
            })
    elif action == 'stop':
        remote_access.stop_ngrok()
        return jsonify({
            'success': True,
            'message': '远程访问已关闭'
        })
    
    return jsonify({'success': False, 'message': '无效操作'})

@app.route('/api/remote_access/configure', methods=['POST'])
def configure_remote_access():
    data = request.json
    authtoken = data.get('authtoken', '')
    
    success = remote_access.set_authtoken(authtoken)
    status = remote_access.get_status()
    
    if success:
        return jsonify({
            'success': True,
            'message': 'ngrok认证已配置，请重新启动远程访问'
        })
    return jsonify({
        'success': False,
        'message': '配置失败',
        'last_error': status.get('last_error'),
        'help': '请输入有效的ngrok认证token（纯字符串，不含URL）。获取地址: https://dashboard.ngrok.com/get-started/your-authtoken'
    })

@app.route('/api/industries')
def get_industries():
    return jsonify(list(industry_chains.keys()))

@app.route('/api/industry/<industry>')
def get_industry(industry):
    analysis = industry_analyst.get_industry_analysis(industry)
    return jsonify(analysis)

@app.route('/api/concepts')
def get_concepts():
    hot_concepts = concept_data.get_hot_concepts()
    return jsonify({'concepts': hot_concepts})

@app.route('/api/concepts/<concept>')
def get_concept(concept):
    stocks = concept_data.get_stocks_for_concept(concept)
    return jsonify({'concept': concept, 'stocks': stocks})

@app.route('/api/stock_concepts/<symbol>')
def get_stock_concepts(symbol):
    concepts = concept_data.get_concepts_for_stock(symbol)
    return jsonify({'symbol': symbol, 'concepts': concepts})

@app.route('/api/rules')
def get_rules():
    return jsonify(trading_rules.get_rules_summary())

@app.route('/api/update_rules', methods=['POST'])
def update_rules():
    data = request.json
    trading_rules.set_parameters(data)
    return jsonify({'success': True, 'rules': trading_rules.get_rules_summary()})

recommendations_cache = {}
cache_timestamp = 0

def update_recommendations_cache():
    global recommendations_cache, cache_timestamp
    now = get_beijing_timestamp()
    if now - cache_timestamp > 300:
        result = get_recommendations()
        if hasattr(result, 'get_json'):
            recommendations_cache = result.get_json()
        else:
            recommendations_cache = result
        cache_timestamp = now
    return recommendations_cache

@app.route('/api/deployment')
def get_deployment():
    portfolio = config.get_portfolio()
    portfolio_data = data_fetcher.get_portfolio_data(portfolio)
    
    total_value = sum(p['market_value'] for p in portfolio_data)
    available_cash = trading_rules.total_capital - total_value
    
    recommend_data = update_recommendations_cache()
    recommendations = recommend_data.get('recommendations', [])
    
    deployment = trading_rules.calculate_deployment_suggestion(available_cash, recommendations)
    
    return jsonify({
        'total_capital': trading_rules.total_capital,
        'portfolio_value': round(total_value, 2),
        'available_cash': round(available_cash, 2),
        'deployment': deployment
    })

def get_recommendations_internal():
    dynamic_stocks = watchlist_fetcher.get_dynamic_watchlist()
    
    watchlist = []
    for stock in dynamic_stocks:
        symbol = stock['symbol']
        suffix = '.SS' if symbol.startswith('6') else '.SZ'
        watchlist.append({
            'symbol': symbol + suffix,
            'name': stock['name'],
            'type': stock.get('type', ''),
            'reason': stock.get('reason', '')
        })
    
    industry_potential_stocks = industry_analyst.get_all_potential_stocks()
    for stock in industry_potential_stocks:
        symbol = stock['symbol']
        suffix = '.SS' if symbol.startswith('6') else '.SZ'
        full_symbol = symbol + suffix
        if full_symbol not in [s['symbol'] for s in watchlist]:
            watchlist.append({
                'symbol': full_symbol,
                'name': stock['name'],
                'type': '产业链潜力股',
                'reason': stock['reason'],
                'industry': stock.get('industry', '')
            })
    
    recommendations = []
    
    for stock in watchlist[:10]:
        try:
            realtime_data = data_fetcher.get_realtime_price(stock['symbol'])
            current_price = realtime_data['price'] if isinstance(realtime_data, dict) else realtime_data
            
            if current_price and current_price > 0:
                recommendations.append({
                    'symbol': stock['symbol'],
                    'name': stock['name'],
                    'current_price': round(current_price, 2),
                    'combined_score': stock.get('potential_score', 0.5),
                    'final_signal': 'buy',
                    'reasoning': [stock.get('reason', '综合评分较高')],
                    'type': stock.get('type', ''),
                    'industry': stock.get('industry', '')
                })
        except Exception as e:
            continue
    
    return recommendations

def get_portfolio_industry_distribution():
    portfolio = config.get_portfolio()
    industry_counts = {}
    total_value = 0
    
    for stock in portfolio:
        industry = stock.get('industry', '未知')
        if industry not in industry_counts:
            industry_counts[industry] = 0
        industry_counts[industry] += stock.get('quantity', 0) * stock.get('cost_price', 0)
        total_value += stock.get('quantity', 0) * stock.get('cost_price', 0)
    
    return {industry: round(value / total_value * 100, 1) if total_value > 0 else 0 
            for industry, value in industry_counts.items()}

@app.route('/api/recommend')
def get_recommendations():
    market_news = news_fetcher.fetch_general_news()
    market_sentiment = news_fetcher.get_market_sentiment()
    
    dynamic_stocks = watchlist_fetcher.get_dynamic_watchlist()
    
    watchlist = []
    for stock in dynamic_stocks[:30]:
        symbol = stock['symbol']
        suffix = '.SS' if symbol.startswith('6') else '.SZ'
        watchlist.append({
            'symbol': symbol + suffix,
            'name': stock['name'],
            'type': stock.get('type', ''),
            'reason': stock.get('reason', ''),
            'industry': stock.get('industry', '')
        })
    
    industry_potential_stocks = industry_analyst.get_all_potential_stocks()
    for stock in industry_potential_stocks[:3]:
        symbol = stock['symbol']
        suffix = '.SS' if symbol.startswith('6') else '.SZ'
        full_symbol = symbol + suffix
        if full_symbol not in [s['symbol'] for s in watchlist]:
            watchlist.append({
                'symbol': full_symbol,
                'name': stock['name'],
                'type': '产业链潜力股',
                'reason': stock['reason'],
                'industry': stock.get('industry', '')
            })
    
    dragon_tiger_stocks = dragon_tiger_fetcher.get_top_stocks(8)
    for stock in dragon_tiger_stocks:
        symbol = stock['symbol']
        suffix = '.SS' if symbol.startswith('6') else '.SZ'
        full_symbol = symbol + suffix
        if full_symbol not in [s['symbol'] for s in watchlist]:
            industry = industry_data.get_industry(symbol)
            watchlist.append({
                'symbol': full_symbol,
                'name': stock['name'],
                'type': '龙虎榜股票',
                'reason': f'龙虎榜净流入{stock["net_amount"]/10000:.1f}万，机构买入{stock["buy_institution_count"]}次',
                'industry': industry
            })
    
    portfolio_industry_dist = get_portfolio_industry_distribution()
    max_industry_weight = 40
    
    recommendations = []
    
    def analyze_stock(stock):
        try:
            data = data_fetcher.get_stock_data(stock['symbol'], period='1y')
            if data.empty:
                return None
                
            realtime_data = data_fetcher.get_realtime_price(stock['symbol'])
            current_price = realtime_data['price'] if isinstance(realtime_data, dict) else realtime_data
            if not current_price or current_price <= 0:
                return None
            
            financial_health = financial_fetcher.analyze_financial_health(stock['symbol'])
            research_view = research_analyst.get_consensus_view(stock['symbol'])
            
            news_sentiment = news_fetcher.get_news_sentiment_score(stock['symbol'])
            stock_sentiment = news_fetcher.get_stock_sentiment(stock['symbol'])
            
            signals = []
            for strategy in strategies:
                result = strategy.generate_signal(data)
                if isinstance(result, tuple):
                    signal, turn_count = result
                else:
                    signal = result
                    turn_count = 0
                signals.append({
                    'strategy': strategy.get_name(),
                    'signal': signal,
                    'turn_count': int(turn_count)
                })
            
            buy_count = sum(1 for s in signals if s['signal'] == 'buy')
            sell_count = sum(1 for s in signals if s['signal'] == 'sell')
            
            base_symbol = stock['symbol'].replace('.SS', '').replace('.SZ', '')
            dt_signal, dt_score = dragon_tiger_fetcher.get_dragon_tiger_signal(base_symbol)
            
            signals.append({
                'strategy': '龙虎榜策略',
                'signal': dt_signal,
                'turn_count': 0
            })
            
            if dt_signal == 'buy':
                buy_count += 1.5
            elif dt_signal == 'sell':
                sell_count += 1.5
            
            base_score = 0
            tech_signal = 'neutral'
            
            if buy_count >= 2:
                base_score += 1
                tech_signal = 'buy'
            elif sell_count >= 2:
                base_score -= 1
                tech_signal = 'sell'
            
            other_score = 0
            
            if dt_score > 0:
                other_score += dt_score
            elif dt_score < 0:
                other_score += dt_score
            
            if news_sentiment > 0.1:
                other_score += news_sentiment * 0.6
            elif news_sentiment < -0.1:
                other_score += news_sentiment * 0.6
            if stock_sentiment > 0.1:
                other_score += 0.2
            elif stock_sentiment < -0.1:
                other_score -= 0.2
            if research_view['sentiment_score'] > 0.3:
                other_score += 0.3
            elif research_view['sentiment_score'] < -0.3:
                other_score -= 0.3
            
            influencer_score = influencer_analyst.calculate_influencer_score(stock['symbol'])
            if influencer_score > 0.2:
                other_score += influencer_score * 0.4
                influencer_opinions = influencer_analyst.get_opinion_for_stock(stock['symbol'])
                if influencer_opinions:
                    top_opinion = influencer_opinions[0]
                    recommendation_reasons.append(f"【大V观点】{top_opinion['author']}看好{top_opinion['topic']}概念")
            elif influencer_score < -0.2:
                other_score += influencer_score * 0.4
            
            if financial_health.get('health_level') == '健康':
                other_score += 0.2
            elif financial_health.get('health_level') == '风险':
                other_score -= 0.2
            
            recommendation_reasons = []
            industry_analysis = industry_analyst.analyze_industry_trend(stock.get('industry', '')) if stock.get('industry') else None
            is_main_trend_up = industry_analysis and industry_analysis.get('trend') == '上升'
            
            event_chains = news_fetcher.get_stock_event_analysis(stock['symbol'].replace('.SS', '').replace('.SZ', ''))
            if event_chains:
                for chain in event_chains[:2]:
                    recommendation_reasons.append(f"【事件驱动】{chain['reasoning']}")
                    recommendation_reasons.append(f"   触发事件: {chain['news_title']}")
                    other_score += chain.get('sentiment', 0) * 0.2
            
            if stock.get('type') == '产业链潜力股':
                industry = stock.get('industry', '')
                recommendation_reasons.append(f"🌿 【紫苏叶原理】{industry}产业链潜力股")
                recommendation_reasons.append(f"   - {stock.get('reason', '')}")
                
                if is_main_trend_up:
                    other_score += 0.3
                    recommendation_reasons.append(f"【行业趋势】{industry} - 📈 主升浪")
                    if industry_analysis and industry_analysis.get('drivers'):
                        recommendation_reasons.append(f"   - 驱动因素: {', '.join(industry_analysis['drivers'][:2])}")
                else:
                    other_score -= 0.2
                    recommendation_reasons.append(f"【行业趋势】{industry} - {industry_analysis.get('trend', '未知')}趋势")
                    recommendation_reasons.append(f"   - ⚠️ 非主升浪，谨慎关注")
            elif stock.get('type'):
                recommendation_reasons.append(f"【来源】{stock['type']}: {stock.get('reason', '')}")
                if is_main_trend_up and industry_analysis:
                    recommendation_reasons.append(f"【行业趋势】{industry_analysis.get('industry', '')} - 📈 上升趋势")
            
            if len(data) >= 20:
                recent_data = data.tail(20)
                momentum = (recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) / recent_data['close'].iloc[0]
                volume_ratio = recent_data['volume'].mean() / data['volume'].mean() if data['volume'].mean() > 0 else 1
                
                if momentum > 0.1:
                    other_score += 0.3
                    recommendation_reasons.append(f"【赚钱效应】近20日涨幅 {momentum*100:.1f}%，趋势强势")
                elif momentum > 0.05:
                    other_score += 0.15
                    recommendation_reasons.append(f"【赚钱效应】近20日涨幅 {momentum*100:.1f}%，趋势向上")
                elif momentum < -0.1:
                    other_score -= 0.2
                    recommendation_reasons.append(f"【赚钱效应】近20日跌幅 {abs(momentum)*100:.1f}%，趋势疲软")
                
                if volume_ratio > 1.5:
                    other_score += 0.15
                    recommendation_reasons.append(f"【量能】放量上涨，资金关注")
            
            industry = stock.get('industry', '')
            if not industry:
                industry = industry_data.get_industry(stock['symbol'])
            current_industry_weight = portfolio_industry_dist.get(industry, 0)
            
            if current_industry_weight >= max_industry_weight:
                other_score -= 0.3
                recommendation_reasons.append(f"【分散风险】当前持仓中{industry}行业占比{current_industry_weight}%，已达上限，谨慎加仓")
            elif current_industry_weight >= max_industry_weight * 0.5:
                other_score -= 0.15
                recommendation_reasons.append(f"【分散风险】当前持仓中{industry}行业占比{current_industry_weight}%，建议控制仓位")
            
            if tech_signal == 'sell':
                combined_score = base_score + other_score
                recommendation_reasons.insert(0, f"【技术面】{sell_count}个技术指标发出卖出信号，技术面看空")
            elif tech_signal == 'buy':
                combined_score = base_score + other_score
                recommendation_reasons.insert(0, f"【技术面】{buy_count}个技术指标发出买入信号，技术面看多")
            else:
                combined_score = other_score
                if other_score > 0.3:
                    recommendation_reasons.insert(0, f"【技术面】暂无明确买卖信号，但其他因素偏多")
                elif other_score < -0.3:
                    recommendation_reasons.insert(0, f"【技术面】暂无明确买卖信号，其他因素偏空")
                else:
                    recommendation_reasons.insert(0, f"【技术面】暂无明确买卖信号，建议观察")
            
            if news_sentiment > 0.3:
                recommendation_reasons.append(f"【舆情】相关新闻情绪积极 (情绪值: {news_sentiment:.2f})")
            elif news_sentiment < -0.3:
                recommendation_reasons.append(f"【舆情】相关新闻情绪消极 (情绪值: {news_sentiment:.2f})")
            if stock_sentiment > 0.2:
                recommendation_reasons.append(f"【个股情绪】个股市场情绪偏多")
            elif stock_sentiment < -0.2:
                recommendation_reasons.append(f"【个股情绪】个股市场情绪偏空")
            if research_view.get('sentiment_score', 0) > 0.3:
                recommendation_reasons.append(f"【机构观点】机构研报观点看多")
            elif research_view.get('sentiment_score', 0) < -0.3:
                recommendation_reasons.append(f"【机构观点】机构研报观点看空")
            if financial_health.get('health_level') == '健康':
                recommendation_reasons.append(f"【基本面】财务状况健康 (评分: {financial_health.get('score', 0)})")
            elif financial_health.get('health_level') == '风险':
                recommendation_reasons.append(f"【基本面】财务状况存在风险 (评分: {financial_health.get('score', 0)})")
            
            if tech_signal == 'buy' and combined_score > 0.5:
                final_signal = 'buy'
                conclusion = '技术面偏多，可关注；观望等待更好时机也是合理选择。'
            elif tech_signal == 'sell' or combined_score < -0.5:
                final_signal = 'sell'
                conclusion = '建议回避或卖出'
            elif combined_score > 0.3:
                final_signal = 'hold'
                conclusion = '建议观察，等待技术信号'
            else:
                final_signal = 'hold'
                conclusion = '建议观察'
            
            detailed_reason = '\n'.join(recommendation_reasons) if recommendation_reasons else '暂无足够数据支持推荐理由'
            
            base_symbol = stock['symbol'].replace('.SS', '').replace('.SZ', '')
            concepts = concept_data.get_concepts_for_stock(base_symbol)
            
            return {
                'symbol': base_symbol,
                'full_symbol': stock['symbol'],
                'name': stock['name'],
                'current_price': round(current_price, 2),
                'combined_score': round(combined_score, 2),
                'final_signal': final_signal,
                'reasoning': recommendation_reasons,
                'detailed_reason': detailed_reason,
                'conclusion': conclusion,
                'type': stock.get('type', ''),
                'industry': industry,
                'concepts': concepts,
                'signals': signals,
                'news_sentiment': round(news_sentiment, 2),
                'stock_sentiment': round(stock_sentiment, 2),
                'financial_health': financial_health.get('health_level', '未知'),
                'financial_score': financial_health.get('score', 0),
                'research_view': research_view.get('sentiment_label', '中性'),
                'current_industry_weight': current_industry_weight
            }
        except Exception as e:
            print(f"⚠️ 分析股票 {stock['symbol']} 失败: {e}")
            return None
    
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(analyze_stock, stock) for stock in watchlist]
        
        for future in concurrent.futures.as_completed(futures, timeout=60):
            result = future.result()
            if result:
                recommendations.append(result)
    
    recommendations.sort(key=lambda x: x['combined_score'], reverse=True)
    
    buy_recommendations = [r for r in recommendations if r['final_signal'] == 'buy']
    
    if buy_recommendations:
        top_recommendations = buy_recommendations[:5]
    else:
        top_recommendations = []
    
    return jsonify({
        'recommendations': top_recommendations,
        'market_sentiment': market_sentiment,
        'total_analyzed': len(watchlist),
        'portfolio_industry_distribution': portfolio_industry_dist,
        'max_industry_weight': max_industry_weight,
        'recommendation_count': len(top_recommendations)
    })

@app.route('/api/xueqiu/posts/<symbol>')
def get_xueqiu_posts(symbol):
    posts = xueqiu_fetcher.fetch_stock_posts(symbol)
    return jsonify(posts)

@app.route('/api/xueqiu/hot')
def get_xueqiu_hot():
    hot_stocks = xueqiu_fetcher.fetch_hot_stocks()
    return jsonify(hot_stocks)

@app.route('/api/xueqiu/portfolio/<user_id>')
def get_xueqiu_portfolio(user_id):
    portfolio = xueqiu_fetcher.fetch_user_portfolio(user_id)
    return jsonify(portfolio)

@app.route('/api/financial/report/<symbol>')
def get_financial_report(symbol):
    report = financial_fetcher.get_financial_report(symbol)
    return jsonify(report)

@app.route('/api/financial/health/<symbol>')
def get_financial_health(symbol):
    health = financial_fetcher.analyze_financial_health(symbol)
    return jsonify(health)

@app.route('/api/financial/earnings/<symbol>')
def get_recent_earnings(symbol):
    earnings = financial_fetcher.get_recent_earnings(symbol)
    return jsonify(earnings)

def load_account():
    try:
        with open('/Users/ccchen/Downloads/DaA/data/account.json', 'r') as f:
            return json.load(f)
    except:
        return {'total_amount': 50000, 'initial_amount': 50000, 'cash': 0}

def save_account(account):
    account['last_updated'] = get_beijing_time().isoformat()
    with open('/Users/ccchen/Downloads/DaA/data/account.json', 'w') as f:
        json.dump(account, f, indent=2)

@app.route('/api/account')
def get_account():
    account = load_account()
    return jsonify(account)

@app.route('/api/account/update', methods=['POST'])
def update_account():
    data = request.json
    account = load_account()
    if 'total_amount' in data:
        account['total_amount'] = data['total_amount']
    if 'cash' in data:
        account['cash'] = data['cash']
    save_account(account)
    return jsonify({'success': True, 'account': account})

@app.route('/api/reminders')
def get_reminders():
    jobs = scheduler.get_scheduled_jobs()
    alerts = price_alert.get_alerts()
    return jsonify({
        'running': scheduler.is_scheduler_running(),
        'scheduled_jobs': jobs,
        'price_alerts': alerts
    })

@app.route('/api/reminders/add_alert', methods=['POST'])
def add_price_alert():
    data = request.json
    alert = price_alert.add_alert(
        symbol=data['symbol'],
        target_price=data['target_price'],
        condition=data['condition'],
        callback=None
    )
    return jsonify({'success': True, 'alert': alert})

@app.route('/api/reminders/remove_alert/<alert_id>', methods=['DELETE'])
def remove_price_alert(alert_id):
    price_alert.remove_alert(int(alert_id))
    return jsonify({'success': True})

def send_reminder(label):
    print(f"🔔 定时提醒: {label}")
    try:
        import subprocess
        subprocess.run(['osascript', '-e', f'display notification "{label}" with title "A股策略提醒" sound name "Glass"'], 
                      check=True, capture_output=True)
    except Exception as e:
        print(f"⚠️ 桌面通知发送失败: {e}")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def init_scheduler():
    scheduler.add_daily_reminder(10, 0, send_reminder, "上午10:00 操作提醒")
    scheduler.add_daily_reminder(14, 30, send_reminder, "下午2:30 操作提醒")
    scheduler.start()
    print("✅ 定时提醒已设置: 每天 10:00 和 14:30")

init_scheduler()

local_ip = get_local_ip()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
