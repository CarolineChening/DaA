#!/usr/bin/env python3

import os
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.time_utils import format_beijing_time, get_beijing_time

from config import Config
from data import DataFetcher, NewsFetcher, FinancialFetcher
from strategies import (
    MovingAverageStrategy,
    MACDStrategy,
    RSIStrategy,
    BollingerBandsStrategy,
    CombinedStrategy
)
from backtesting import Backtester
from scheduler import ReminderScheduler
from optimizer import StrategyOptimizer
from rules import TradingRules
from research import ResearchAnalyst
from industry import IndustryAnalyst

class StockTradingApp:
    def __init__(self):
        self.config = Config()
        self.data_fetcher = DataFetcher()
        self.news_fetcher = NewsFetcher()
        self.financial_fetcher = FinancialFetcher()
        self.backtester = Backtester(
            initial_capital=self.config.INITIAL_CAPITAL,
            transaction_cost=self.config.TRANSACTION_COST
        )
        self.scheduler = ReminderScheduler()
        self.strategies = [
            MovingAverageStrategy(),
            MACDStrategy(),
            RSIStrategy(),
            BollingerBandsStrategy(),
            CombinedStrategy()
        ]
        self.optimizer = StrategyOptimizer(self.strategies)
        self.trading_rules = TradingRules()
        self.research_analyst = ResearchAnalyst()
        self.industry_analyst = IndustryAnalyst()
        
        self.scheduler.add_morning_reminder(self.execute_morning_analysis)
        self.scheduler.add_afternoon_reminder(self.execute_afternoon_analysis)
    
    def print_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    A股策略分析系统                           ║
║              Stock Strategy Analysis System                  ║
║  整合新闻情绪 · 财报分析 · 研报观点 · 智能策略优化            ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def execute_morning_analysis(self):
        print("\n" + "="*60)
        print(f"📈 上午分析报告 - {format_beijing_time()}")
        print("="*60)
        self.run_strategy_analysis_with_sentiment()
    
    def execute_afternoon_analysis(self):
        print("\n" + "="*60)
        print(f"📉 下午分析报告 - {format_beijing_time()}")
        print("="*60)
        self.run_strategy_analysis_with_sentiment()
    
    def get_market_sentiment_report(self):
        print("\n📰 市场情绪报告")
        print("-" * 40)
        
        market_sentiment = self.news_fetcher.get_market_sentiment()
        sentiment_text = "中性"
        sentiment_color = "\033[93m"
        
        if market_sentiment > 0.1:
            sentiment_text = "偏多"
            sentiment_color = "\033[92m"
        elif market_sentiment < -0.1:
            sentiment_text = "偏空"
            sentiment_color = "\033[91m"
        
        print(f"整体市场情绪: {sentiment_color}{sentiment_text} (得分: {market_sentiment:.2f}){chr(27)}[0m")
        
        industries = ['科技', '金融', '消费', '医药', '新能源']
        for industry in industries:
            impact = self.news_fetcher.get_industry_impact(industry)
            impact_text = "中性"
            impact_color = "\033[93m"
            
            if impact > 0.1:
                impact_text = "利好"
                impact_color = "\033[92m"
            elif impact < -0.1:
                impact_text = "利空"
                impact_color = "\033[91m"
            
            print(f"  {industry}: {impact_color}{impact_text}{chr(27)}[0m")
        
        return market_sentiment
    
    def run_strategy_analysis_with_sentiment(self):
        market_sentiment = self.get_market_sentiment_report()
        portfolio = self.config.get_portfolio()
        
        for stock in portfolio:
            print(f"\n📊 分析股票: {stock['name']} ({stock['symbol']})")
            print("-" * 40)
            
            data = self.data_fetcher.get_stock_data(stock['symbol'], period='1y')
            stock_sentiment = self.news_fetcher.get_stock_sentiment(stock['symbol'])
            
            sentiment_text = "中性"
            sentiment_color = "\033[93m"
            if stock_sentiment > 0.1:
                sentiment_text = "看多"
                sentiment_color = "\033[92m"
            elif stock_sentiment < -0.1:
                sentiment_text = "看空"
                sentiment_color = "\033[91m"
            
            print(f"  个股情绪: {sentiment_color}{sentiment_text} (得分: {stock_sentiment:.2f}){chr(27)}[0m")
            
            research_view = self.research_analyst.get_consensus_view(stock['symbol'])
            view_color = "\033[93m"
            if research_view['view'] == '看多':
                view_color = "\033[92m"
            elif research_view['view'] == '看空':
                view_color = "\033[91m"
            print(f"  机构观点: {view_color}{research_view['view']} (得分: {research_view['sentiment_score']:.2f}){chr(27)}[0m")
            
            if data.empty:
                print("  ❌ 获取数据失败")
                continue
            
            signals = []
            for strategy in self.strategies:
                signal = strategy.generate_signal(data)
                signals.append(signal)
                print(f"  {strategy.get_name()}: {signal.upper()}")
            
            ml_signal = self.optimizer.predict_signal(stock['symbol'], data, stock_sentiment)
            print(f"  🤖 机器学习模型: {ml_signal.upper()}")
            
            realtime_data = self.data_fetcher.get_realtime_price(stock['symbol'])
            current_price = realtime_data['price'] if isinstance(realtime_data, dict) else (realtime_data or data['close'].iloc[-1])
            rules_result = self.trading_rules.analyze_position(
                stock['symbol'], current_price, stock['cost_price']
            )
            
            if rules_result:
                print("\n  📋 交易规则检查:")
                for rule in rules_result:
                    priority_color = "\033[94m"
                    if rule['priority'] == 'high':
                        priority_color = "\033[91m"
                    elif rule['priority'] == 'medium':
                        priority_color = "\033[93m"
                    print(f"    [{priority_color}{rule['rule']}{chr(27)}[0m] {rule['reason']}")
            
            final_signal = self.generate_final_signal(signals, ml_signal, stock_sentiment, market_sentiment, research_view['sentiment_score'])
            print(f"\n  ✅ 最终建议: \033[94m{final_signal.upper()}\033[0m")
    
    def generate_final_signal(self, signals, ml_signal, stock_sentiment, market_sentiment, research_sentiment):
        buy_count = signals.count('buy')
        sell_count = signals.count('sell')
        
        combined_score = 0
        
        if buy_count >= 2:
            combined_score += 1
        if sell_count >= 2:
            combined_score -= 1
        
        if ml_signal == 'buy':
            combined_score += 1
        elif ml_signal == 'sell':
            combined_score -= 1
        
        if stock_sentiment > 0.1:
            combined_score += 0.5
        elif stock_sentiment < -0.1:
            combined_score -= 0.5
        
        if market_sentiment > 0.1:
            combined_score += 0.3
        elif market_sentiment < -0.1:
            combined_score -= 0.3
        
        if research_sentiment > 0.3:
            combined_score += 0.4
        elif research_sentiment < -0.3:
            combined_score -= 0.4
        
        if combined_score > 0.5:
            return 'buy'
        elif combined_score < -0.5:
            return 'sell'
        else:
            return 'hold'
    
    def run_strategy_analysis(self):
        self.run_strategy_analysis_with_sentiment()
    
    def show_portfolio(self):
        print("\n" + "="*60)
        print("📋 当前持仓")
        print("="*60)
        
        portfolio_data = self.data_fetcher.get_portfolio_data(self.config.get_portfolio())
        
        total_market_value = 0
        total_profit = 0
        total_cost = 0
        
        for stock in portfolio_data:
            profit_color = "\033[92m" if stock['profit'] >= 0 else "\033[91m"
            reset_color = "\033[0m"
            
            print(f"\n{stock['name']} ({stock['symbol']})")
            print(f"  持仓数量: {stock['quantity']}股")
            print(f"  成本价: ¥{stock['cost_price']:.2f}")
            print(f"  当前价: ¥{stock['current_price']:.2f}")
            print(f"  市值: ¥{stock['market_value']:.2f}")
            print(f"  盈亏: {profit_color}¥{stock['profit']:.2f} ({stock['profit_percent']:.2f}%){reset_color}")
            
            health = self.financial_fetcher.analyze_financial_health(stock['symbol'])
            health_color = "\033[92m" if health['health_level'] == '健康' else "\033[93m" if health['health_level'] == '一般' else "\033[91m"
            print(f"  财务健康: {health_color}{health['health_level']} ({health['score']}/{health['max_score']}){reset_color}")
            
            total_market_value += stock['market_value']
            total_profit += stock['profit']
            total_cost += stock['quantity'] * stock['cost_price']
        
        profit_color = "\033[92m" if total_profit >= 0 else "\033[91m"
        reset_color = "\033[0m"
        
        print("\n" + "="*60)
        print(f"总资产: ¥{total_market_value:.2f}")
        print(f"总成本: ¥{total_cost:.2f}")
        print(f"总盈亏: {profit_color}¥{total_profit:.2f} ({(total_profit/total_cost*100):.2f}%){reset_color}")
        print("="*60)
    
    def run_backtest(self):
        print("\n" + "="*60)
        print("🔬 策略回测")
        print("="*60)
        
        symbol = input("请输入股票代码 (如 AAPL): ").strip().upper()
        if not symbol:
            symbol = "AAPL"
        
        print(f"\n正在回测 {symbol}...")
        
        data = self.data_fetcher.get_stock_data(symbol, period='5y')
        
        if data.empty:
            print("❌ 获取数据失败")
            return
        
        results = self.backtester.compare_strategies(self.strategies, data)
        
        print("\n" + "-"*60)
        print(f"回测结果 ({symbol})")
        print("-"*60)
        print(results[['strategy', 'total_return', 'sharpe_ratio', 'max_drawdown', 'total_trades', 'win_rate']].to_string(index=False))
        
        best_strategy = results.loc[results['total_return'].idxmax()]
        print(f"\n🏆 最优策略: {best_strategy['strategy']}")
        print(f"   总收益: {best_strategy['total_return']}%")
        print(f"   夏普比率: {best_strategy['sharpe_ratio']}")
        print(f"   最大回撤: {best_strategy['max_drawdown']}%")
    
    def train_and_optimize_model(self):
        print("\n" + "="*60)
        print("🧠 模型训练与优化")
        print("="*60)
        
        symbol = input("请输入要训练的股票代码: ").strip().upper()
        if not symbol:
            symbol = "AAPL"
        
        print(f"\n正在获取 {symbol} 的历史数据...")
        data = self.data_fetcher.get_stock_data(symbol, period='5y')
        
        if data.empty:
            print("❌ 获取数据失败")
            return
        
        print(f"数据长度: {len(data)} 天")
        
        print("\n正在训练机器学习模型...")
        accuracy = self.optimizer.train_model(symbol, data)
        
        if accuracy:
            print(f"\n✅ 模型训练完成，准确率: {accuracy:.2f}")
            
            print("\n正在优化策略参数...")
            self.optimizer.optimize_all_strategies(data)
            
            print("\n✅ 策略优化完成")
    
    def run_auto_correction(self):
        print("\n" + "="*60)
        print("🔄 自动策略修正")
        print("="*60)
        
        print("正在对所有持仓股票进行回测和模型修正...")
        
        portfolio = self.config.get_portfolio()
        
        for stock in portfolio:
            print(f"\n📊 正在分析: {stock['name']} ({stock['symbol']})")
            
            data = self.data_fetcher.get_stock_data(stock['symbol'], period='3y')
            
            if data.empty:
                print("  ❌ 获取数据失败，跳过")
                continue
            
            print("  正在回测...")
            results = self.backtester.compare_strategies(self.strategies, data)
            
            if results.empty:
                print("  ❌ 回测失败，跳过")
                continue
            
            best_strategy = results.loc[results['total_return'].idxmax()]
            print(f"  最优策略: {best_strategy['strategy']}")
            print(f"  回测收益: {best_strategy['total_return']}%")
            
            if best_strategy['total_return'] < 10:
                print("  ⚠️ 回测收益较低，正在重新优化...")
                self.optimizer.optimize_strategy_params(best_strategy['strategy'], data)
            
            sentiment_scores = [self.news_fetcher.get_stock_sentiment(stock['symbol'])] * len(data)
            self.optimizer.adaptive_learning(stock['symbol'], data, sentiment_scores)
        
        print("\n✅ 自动修正完成")
    
    def view_financial_report(self):
        print("\n" + "="*60)
        print("📊 财报分析")
        print("="*60)
        
        symbol = input("请输入股票代码: ").strip().upper()
        if not symbol:
            symbol = "AAPL"
        
        print(f"\n正在分析 {symbol} 的财务状况...")
        
        health = self.financial_fetcher.analyze_financial_health(symbol)
        
        print("\n" + "-"*40)
        print("财务健康评估")
        print("-"*40)
        
        health_color = "\033[92m" if health['health_level'] == '健康' else "\033[93m" if health['health_level'] == '一般' else "\033[91m"
        print(f"综合评级: {health_color}{health['health_level']}{chr(27)}[0m")
        print(f"评分: {health['score']}/{health['max_score']}")
        
        print("\n评估理由:")
        for reason in health['reasons']:
            print(f"  • {reason}")
        
        print("\n" + "-"*40)
        print("关键财务指标")
        print("-"*40)
        
        metrics = health['metrics']
        print(f"市盈率 (PE): {metrics['pe_ratio']:.1f}")
        print(f"预期市盈率: {metrics['forward_pe']:.1f}")
        print(f"PEG比率: {metrics['peg_ratio']:.2f}")
        print(f"市净率 (PB): {metrics['pb_ratio']:.2f}")
        print(f"市销率 (PS): {metrics['ps_ratio']:.2f}")
        print(f"股息率: {metrics['dividend_yield']:.2f}%")
        print(f"净利润率: {metrics['profit_margin']:.2f}%")
        print(f"ROE: {metrics['return_on_equity']:.2f}%")
        print(f"ROA: {metrics['return_on_assets']:.2f}%")
        print(f"资产负债率: {metrics['debt_to_equity']:.2f}")
        print(f"流动比率: {metrics['current_ratio']:.2f}")
        
        earnings = self.financial_fetcher.analyze_recent_earnings(symbol)
        if earnings:
            print("\n" + "-"*40)
            print(f"{earnings['year']}年 {earnings['quarter']}财报")
            print("-"*40)
            print(f"营收: ¥{earnings['revenue']/100000000:.2f}亿")
            print(f"净利润: ¥{earnings['earnings']/100000000:.2f}亿")
            if 'revenue_growth' in earnings:
                rev_color = "\033[92m" if earnings['revenue_growth'] > 0 else "\033[91m"
                earn_color = "\033[92m" if earnings['earnings_growth'] > 0 else "\033[91m"
                print(f"营收增长: {rev_color}{earnings['revenue_growth']:.1f}%{chr(27)}[0m ({earnings['revenue_grade']})")
                print(f"净利润增长: {earn_color}{earnings['earnings_growth']:.1f}%{chr(27)}[0m ({earnings['earnings_grade']})")
    
    def view_research_reports(self):
        print("\n" + "="*60)
        print("📰 研报与观点分析")
        print("="*60)
        
        symbol = input("请输入股票代码: ").strip().upper()
        if not symbol:
            symbol = "AAPL"
        
        view = self.research_analyst.get_consensus_view(symbol)
        
        print(f"\n📊 {symbol} - 综合观点")
        view_color = "\033[92m" if view['view'] == '看多' else "\033[93m" if view['view'] == '中性' else "\033[91m"
        print(f"市场观点: {view_color}{view['view']}{chr(27)}[0m")
        print(f"情绪得分: {view['sentiment_score']:.2f}")
        print(f"研报数量: {view['research_count']} | 雪球观点: {view['opinion_count']}")
        
        print("\n" + "-"*40)
        print("📋 券商研报")
        print("-"*40)
        
        for report in view['research_reports']:
            rating_color = "\033[92m" if report['rating'] in ['买入', '增持'] else "\033[93m" if report['rating'] == '中性' else "\033[91m"
            print(f"\n📝 {report['title']}")
            print(f"   机构: {report['institute']} | 分析师: {report['analyst']}")
            print(f"   评级: {rating_color}{report['rating']}{chr(27)}[0m | 日期: {report['date']}")
            print(f"   摘要: {report['summary']}")
        
        print("\n" + "-"*40)
        print("💬 雪球大V观点")
        print("-"*40)
        
        for opinion in view['snowball_opinions']:
            opinion_color = "\033[92m" if opinion['opinion'] in ['长期', '买入'] else "\033[93m" if opinion['opinion'] == '观望' else "\033[91m"
            print(f"\n👤 {opinion['author']}")
            print(f"   标题: {opinion['title']}")
            print(f"   观点: {opinion_color}{opinion['opinion']}{chr(27)}[0m | 信心: {opinion['confidence']}%")
            print(f"   日期: {opinion['date']}")
            print(f"   内容: {opinion['content']}")
    
    def view_trading_rules(self):
        print("\n" + "="*60)
        print("⚙️ 交易规则设置")
        print("="*60)
        
        rules = self.trading_rules.get_rules_summary()
        
        print("当前规则配置:")
        for key, value in rules.items():
            print(f"  • {key}: {value}")
        
        print("\n是否修改规则设置? (y/n)")
        choice = input().strip().lower()
        
        if choice == 'y':
            print("\n请输入新的规则值（直接回车保持原值）:")
            
            stop_loss = input(f"止损比例 ({rules['止损比例']}): ").strip()
            if stop_loss:
                self.trading_rules.stop_loss_pct = float(stop_loss.rstrip('%'))
            
            take_profit = input(f"止盈比例 ({rules['止盈比例']}): ").strip()
            if take_profit:
                self.trading_rules.take_profit_pct = float(take_profit.rstrip('%'))
            
            max_pos = input(f"最大仓位 ({rules['最大仓位']}): ").strip()
            if max_pos:
                self.trading_rules.max_position_size = float(max_pos.rstrip('%')) / 100
            
            max_trades = input(f"每日最大交易次数 ({rules['每日最大交易次数']}): ").strip()
            if max_trades:
                self.trading_rules.max_daily_trades = int(max_trades)
            
            cooloff = input(f"卖出冷却时间 ({rules['卖出冷却时间']}): ").strip()
            if cooloff:
                self.trading_rules.sell_cooloff_hours = int(cooloff.rstrip('小时'))
            
            min_days = input(f"最短持有天数 ({rules['最短持有天数']}): ").strip()
            if min_days:
                self.trading_rules.hold_min_days = int(min_days)
            
            max_days = input(f"最长持有天数 ({rules['最长持有天数']}): ").strip()
            if max_days:
                self.trading_rules.max_hold_days = int(max_days)
            
            print("\n✅ 规则更新完成")
    
    def add_stock(self):
        print("\n" + "="*60)
        print("➕ 添加股票")
        print("="*60)
        
        symbol = input("股票代码: ").strip().upper()
        name = input("股票名称: ").strip()
        quantity = int(input("持仓数量: ").strip())
        cost_price = float(input("成本价: ").strip())
        
        self.config.add_stock_to_portfolio({
            'symbol': symbol,
            'name': name if name else symbol,
            'quantity': quantity,
            'cost_price': cost_price
        })
        
        print(f"\n✅ 已添加 {name} ({symbol})")
    
    def remove_stock(self):
        print("\n" + "="*60)
        print("➖ 删除股票")
        print("="*60)
        
        portfolio = self.config.get_portfolio()
        
        for i, stock in enumerate(portfolio):
            print(f"{i+1}. {stock['name']} ({stock['symbol']})")
        
        index = int(input("\n请输入要删除的序号: ").strip()) - 1
        
        if 0 <= index < len(portfolio):
            stock = portfolio[index]
            self.config.remove_stock_from_portfolio(stock['symbol'])
            print(f"\n✅ 已删除 {stock['name']} ({stock['symbol']})")
        else:
            print("\n❌ 无效序号")
    
    def show_next_reminder(self):
        next_time = self.scheduler.get_next_reminder_time()
        now = get_beijing_time()
        diff = next_time - now
        
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        
        print(f"\n⏰ 下次提醒时间: {next_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   距离现在还有: {hours}小时{minutes}分钟")
    
    def start_scheduler(self):
        print("\n🚀 启动定时提醒服务...")
        self.scheduler.start()
        print("✅ 定时提醒已启动")
        print("   上午提醒: 10:00")
        print("   下午提醒: 14:30")
    
    def stop_scheduler(self):
        print("\n⏹️ 停止定时提醒服务...")
        self.scheduler.stop()
        print("✅ 定时提醒已停止")
    
    def show_news(self):
        print("\n" + "="*60)
        print("📰 最新新闻")
        print("="*60)
        
        news = self.news_fetcher.fetch_general_news()
        
        if not news:
            print("暂无新闻数据")
            return
        
        for i, article in enumerate(news[:5], 1):
            sentiment = self.news_fetcher.analyze_sentiment(article.get('title', '') + ' ' + article.get('description', ''))
            sentiment_text = "中性"
            sentiment_color = "\033[93m"
            
            if sentiment > 0.1:
                sentiment_text = "利好"
                sentiment_color = "\033[92m"
            elif sentiment < -0.1:
                sentiment_text = "利空"
                sentiment_color = "\033[91m"
            
            print(f"\n{i}. {article.get('title', '')}")
            print(f"   来源: {article.get('source', '')}")
            print(f"   情绪: {sentiment_color}{sentiment_text}{chr(27)}[0m")
    
    def analyze_industry(self):
        print("\n" + "="*60)
        print("🏭 行业分析（紫苏叶原理）")
        print("="*60)
        
        industries = self.industry_analyst.get_all_industries()
        
        print("请选择要分析的行业:")
        for i, industry in enumerate(industries, 1):
            print(f"{i}. {industry}")
        
        choice = int(input("\n请输入序号: ").strip()) - 1
        
        if choice < 0 or choice >= len(industries):
            print("❌ 无效选择")
            return
        
        industry = industries[choice]
        print(f"\n正在分析 {industry} 行业...")
        
        analysis = self.industry_analyst.analyze_industry_chain(industry)
        
        print("\n" + "-"*40)
        print(f"{industry}行业概况")
        print("-"*40)
        print(f"细分领域: {', '.join(analysis['subsectors'])}")
        print(f"行业特征: {', '.join(analysis['characteristics'])}")
        print(f"关键指标: {', '.join(analysis['key_metrics'])}")
        print(f"主要风险: {', '.join(analysis['risks'])}")
        
        print("\n" + "-"*40)
        print("产业链分析")
        print("-"*40)
        print("🔹 上游环节:")
        for item in analysis['industry_chain']['上游']:
            print(f"   • {item}")
        
        print("\n🔹 中游环节:")
        for item in analysis['industry_chain']['中游']:
            print(f"   • {item}")
        
        print("\n🔹 下游环节:")
        for item in analysis['industry_chain']['下游']:
            print(f"   • {item}")
        
        outlook = self.industry_analyst.analyze_industry_outlook(industry)
        if outlook:
            trend_color = "\033[92m" if outlook['trend'] == '上升' else "\033[93m" if outlook['trend'] == '中性' else "\033[91m"
            print(f"\n" + "-"*40)
            print("行业展望")
            print("-"*40)
            print(f"趋势判断: {trend_color}{outlook['trend']}{chr(27)}[0m")
            print("\n驱动因素:")
            for driver in outlook['drivers']:
                print(f"   • {driver}")
            print("\n挑战因素:")
            for challenge in outlook['challenges']:
                print(f"   • {challenge}")
            print("\n投资主题:")
            for theme in outlook['investment_themes']:
                print(f"   • {theme}")
        
        leaders = self.industry_analyst.get_industry_leaders(industry)
        if leaders:
            print(f"\n" + "-"*40)
            print("行业龙头")
            print("-"*40)
            for leader in leaders:
                print(f"\n📈 {leader['name']} ({leader['symbol']})")
                print(f"   市值: ¥{leader['market_cap']/100000000:.2f}亿")
                print(f"   市盈率: {leader['pe_ratio']:.1f}")
                print(f"   利润率: {leader['profit_margin']:.1f}%")
    
    def suggest_stocks_by_industry(self):
        print("\n" + "="*60)
        print("💡 行业选股推荐")
        print("="*60)
        
        industries = self.industry_analyst.get_all_industries()
        
        print("请选择行业:")
        for i, industry in enumerate(industries, 1):
            print(f"{i}. {industry}")
        
        choice = int(input("\n请输入序号: ").strip()) - 1
        
        if choice < 0 or choice >= len(industries):
            print("❌ 无效选择")
            return
        
        industry = industries[choice]
        
        print("\n选股标准:")
        print("1. 成长型 - 关注营收和盈利增长")
        print("2. 价值型 - 关注估值水平")
        print("3. 质量型 - 关注利润率和ROE")
        
        criteria_choice = input("\n请输入选股标准 (1-3): ").strip()
        criteria_map = {'1': 'growth', '2': 'value', '3': 'quality'}
        criteria = criteria_map.get(criteria_choice, 'growth')
        
        print(f"\n正在为 {industry} 行业筛选股票...")
        suggestions = self.industry_analyst.suggest_stocks_by_industry(industry, criteria)
        
        print("\n" + "-"*40)
        print(f"{industry}行业推荐股票")
        print("-"*40)
        
        for i, stock in enumerate(suggestions, 1):
            print(f"\n{i}. {stock['name']} ({stock['symbol']})")
            print(f"   综合评分: {stock['score']:.2f}")
            print(f"   市值: ¥{stock['market_cap']/100000000:.2f}亿")
            print(f"   市盈率: {stock['pe_ratio']:.1f}")
            print(f"   利润率: {stock['profit_margin']:.1f}%")
            print(f"   营收增长: {stock['revenue_growth']:.1f}%")
            print(f"   盈利增长: {stock['earnings_growth']:.1f}%")
            print(f"   ROE: {stock['return_on_equity']:.1f}%")
    
    def show_menu(self):
        menu = """
╔══════════════════════════════════════╗
║              主菜单                  ║
╠══════════════════════════════════════╣
║  1. 查看持仓                         ║
║  2. 添加股票                         ║
║  3. 删除股票                         ║
║  4. 执行策略分析                     ║
║  5. 策略回测                         ║
║  6. 查看最新新闻                     ║
║  7. 查看财报分析                     ║
║  8. 查看研报观点                     ║
║  9. 行业分析（紫苏叶原理）            ║
║ 10. 行业选股推荐                     ║
║ 11. 交易规则设置                     ║
║ 12. 训练机器学习模型                  ║
║ 13. 自动策略修正                     ║
║ 14. 查看下次提醒                     ║
║ 15. 启动定时提醒                     ║
║ 16. 停止定时提醒                     ║
║ 17. 退出                             ║
╚══════════════════════════════════════╝
请输入选项 (1-17): """
        return input(menu).strip()
    
    def run(self):
        self.print_banner()
        
        while True:
            try:
                choice = self.show_menu()
                
                if choice == '1':
                    self.show_portfolio()
                elif choice == '2':
                    self.add_stock()
                elif choice == '3':
                    self.remove_stock()
                elif choice == '4':
                    self.run_strategy_analysis()
                elif choice == '5':
                    self.run_backtest()
                elif choice == '6':
                    self.show_news()
                elif choice == '7':
                    self.view_financial_report()
                elif choice == '8':
                    self.view_research_reports()
                elif choice == '9':
                    self.analyze_industry()
                elif choice == '10':
                    self.suggest_stocks_by_industry()
                elif choice == '11':
                    self.view_trading_rules()
                elif choice == '12':
                    self.train_and_optimize_model()
                elif choice == '13':
                    self.run_auto_correction()
                elif choice == '14':
                    self.show_next_reminder()
                elif choice == '15':
                    self.start_scheduler()
                elif choice == '16':
                    self.stop_scheduler()
                elif choice == '17':
                    print("\n👋 退出程序")
                    self.scheduler.stop()
                    break
                else:
                    print("\n❌ 无效选项，请输入 1-17")
            
            except KeyboardInterrupt:
                print("\n\n👋 退出程序")
                self.scheduler.stop()
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    app = StockTradingApp()
    app.run()
