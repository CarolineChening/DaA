import pandas as pd
import numpy as np
from datetime import datetime
import os

from utils.time_utils import get_beijing_time

os.environ['USE_REAL_DATA'] = 'true'

try:
    import akshare as ak
    AK_SHARE_AVAILABLE = True
    print("✅ AKShare已安装，将使用真实财报数据")
except ImportError:
    AK_SHARE_AVAILABLE = False
    print("❌ AKShare未安装，部分财务数据功能将不可用")

class FinancialFetcher:
    def __init__(self):
        self.cache = {}
        self.last_fetch_time = {}
    
    def _is_cache_valid(self, key):
        if key in self.last_fetch_time:
            return (get_beijing_time() - self.last_fetch_time[key]).seconds < 300
        return False
    
    def get_financial_report(self, symbol):
        symbol = str(symbol).replace('.SS', '').replace('.SZ', '')
        cache_key = f"financial_{symbol}"
        
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, {})
        
        try:
            if AK_SHARE_AVAILABLE:
                try:
                    df = ak.stock_financial_report_sina(symbol=symbol)
                    if not df.empty:
                        report = {
                            'symbol': symbol,
                            'report_date': df.iloc[0].get('报告日期', ''),
                            'type': df.iloc[0].get('报表类型', ''),
                            'basic_eps': float(df.iloc[0].get('基本每股收益', 0)),
                            'diluted_eps': float(df.iloc[0].get('稀释每股收益', 0)),
                            'revenue': float(df.iloc[0].get('营业总收入', 0)),
                            'revenue_yoy': float(df.iloc[0].get('同比增长率(%)', 0)),
                            'net_profit': float(df.iloc[0].get('净利润', 0)),
                            'net_profit_yoy': float(df.iloc[0].get('净利润同比增长率(%)', 0)),
                            'gross_profit_margin': float(df.iloc[0].get('毛利率(%)', 0)),
                            'net_profit_margin': float(df.iloc[0].get('净利率(%)', 0)),
                            'roa': float(df.iloc[0].get('总资产报酬率(%)', 0)),
                            'roe': float(df.iloc[0].get('净资产收益率(%)', 0)),
                            'assets': float(df.iloc[0].get('总资产', 0)),
                            'liabilities': float(df.iloc[0].get('总负债', 0)),
                            'equity': float(df.iloc[0].get('股东权益合计', 0)),
                            'cash_flow': float(df.iloc[0].get('经营活动产生的现金流量净额', 0)),
                            'pe': float(df.iloc[0].get('市盈率', 0)),
                            'pb': float(df.iloc[0].get('市净率', 0)),
                            'ps': float(df.iloc[0].get('市销率', 0))
                        }
                        self.cache[cache_key] = report
                        self.last_fetch_time[cache_key] = get_beijing_time()
                        print(f"✅ 获取真实财报数据: {symbol}")
                        return report
                except Exception as e:
                    print(f"⚠️ AKShare财报获取失败: {e}")
        except Exception as e:
            print(f"⚠️ 获取财报数据失败: {e}")
        
        print(f"❌ 无法获取真实财报数据: {symbol}")
        self.cache[cache_key] = {}
        self.last_fetch_time[cache_key] = get_beijing_time()
        return {}
    
    def analyze_financial_health(self, symbol):
        financial_data = self.get_financial_report(symbol)
        
        score = 0
        factors = []
        
        pe_ratio = financial_data.get('pe', 30)
        if pe_ratio > 0 and pe_ratio < 30:
            score += 1
            factors.append('市盈率合理')
        elif pe_ratio >= 30 and pe_ratio < 50:
            score += 0.5
            factors.append('市盈率偏高')
        elif pe_ratio >= 50:
            factors.append('市盈率过高')
        else:
            score += 0.5
            factors.append('市盈率数据缺失')
        
        pb_ratio = financial_data.get('pb', 3)
        if pb_ratio > 0 and pb_ratio < 3:
            score += 1
            factors.append('市净率合理')
        elif pb_ratio >= 3 and pb_ratio < 5:
            score += 0.5
            factors.append('市净率偏高')
        else:
            factors.append('市净率数据异常')
        
        roe = financial_data.get('roe', 10)
        if roe >= 15:
            score += 1
            factors.append('ROE优秀')
        elif roe >= 10:
            score += 0.5
            factors.append('ROE良好')
        else:
            factors.append('ROE偏低')
        
        gross_margin = financial_data.get('gross_profit_margin', 20)
        if gross_margin >= 30:
            score += 1
            factors.append('毛利率高')
        elif gross_margin >= 20:
            score += 0.5
            factors.append('毛利率一般')
        else:
            factors.append('毛利率较低')
        
        net_profit_yoy = financial_data.get('net_profit_yoy', 0)
        if net_profit_yoy >= 20:
            score += 1
            factors.append('净利润增长强劲')
        elif net_profit_yoy >= 0:
            score += 0.5
            factors.append('净利润稳定')
        else:
            factors.append('净利润下滑')
        
        debt_ratio = financial_data.get('liabilities', 0) / (financial_data.get('assets', 1) + 0.0001)
        if debt_ratio < 0.5:
            score += 1
            factors.append('负债率健康')
        elif debt_ratio < 0.7:
            score += 0.5
            factors.append('负债率偏高')
        else:
            factors.append('负债率过高')
        
        if score >= 5:
            health_level = '健康'
        elif score >= 3:
            health_level = '一般'
        else:
            health_level = '风险'
        
        return {
            'symbol': symbol,
            'score': int(round(score)),
            'max_score': 6,
            'health_level': health_level,
            'factors': factors,
            'financial_data': financial_data
        }
    
    def get_recent_earnings(self, symbol):
        symbol = str(symbol).replace('.SS', '').replace('.SZ', '')
        
        try:
            if AK_SHARE_AVAILABLE:
                try:
                    df = ak.stock_report_eps_detail(symbol=symbol)
                    if not df.empty:
                        earnings = []
                        for _, row in df.head(8).iterrows():
                            earnings.append({
                                'quarter': row.get('报告期', ''),
                                'eps': float(row.get('基本每股收益', 0)),
                                'eps_yoy': float(row.get('同比增长率(%)', 0)),
                                'revenue': float(row.get('营业总收入', 0)),
                                'revenue_yoy': float(row.get('营业总收入同比增长率(%)', 0)),
                                'net_profit': float(row.get('净利润', 0)),
                                'net_profit_yoy': float(row.get('净利润同比增长率(%)', 0))
                            })
                        return earnings
                except Exception as e:
                    print(f"⚠️ AKShare业绩获取失败: {e}")
        except Exception as e:
            print(f"⚠️ 获取业绩数据失败: {e}")
        
        print(f"❌ 无法获取真实业绩数据: {symbol}")
        return []
