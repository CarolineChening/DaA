import requests
from datetime import datetime, timedelta
import random
from utils.time_utils import get_beijing_time
import re

class InfluencerAnalyst:
    def __init__(self):
        self.cache = {}
        self.influencers = {
            '孙宇晨': {
                'followers': '500万+',
                'platform': '微博/Twitter',
                'expertise': ['区块链', '加密货币', 'Web3', 'AI', '跨境电商'],
                'style': '前瞻性、趋势判断',
                'reliability': 0.75
            },
            '白毛女': {
                'followers': '300万+',
                'platform': '雪球/微博',
                'expertise': ['宏观经济', '房地产', '消费', '医药'],
                'style': '深度分析、逻辑严密',
                'reliability': 0.85
            },
            '饭统戴老板': {
                'followers': '200万+',
                'platform': '公众号/微博',
                'expertise': ['产业研究', '商业分析', '科技趋势'],
                'style': '深度长文、产业洞察',
                'reliability': 0.88
            },
            '卢克文工作室': {
                'followers': '400万+',
                'platform': '公众号',
                'expertise': ['国际政治', '宏观经济', '产业链'],
                'style': '宏大叙事、产业链分析',
                'reliability': 0.78
            },
            '智本社': {
                'followers': '150万+',
                'platform': '公众号/微博',
                'expertise': ['宏观经济', '金融', '投资'],
                'style': '学术严谨、数据驱动',
                'reliability': 0.82
            },
            '秦朔朋友圈': {
                'followers': '250万+',
                'platform': '公众号',
                'expertise': ['商业评论', '企业家精神', '消费'],
                'style': '商业洞察、人文视角',
                'reliability': 0.80
            },
            '洪灏': {
                'followers': '350万+',
                'platform': '微博',
                'expertise': ['宏观策略', '市场分析'],
                'style': '精准预测、数据说话',
                'reliability': 0.85
            },
            '任志强': {
                'followers': '400万+',
                'platform': '微博',
                'expertise': ['房地产', '宏观经济'],
                'style': '直言不讳、独立思考',
                'reliability': 0.70
            }
        }
        
        self.influencer_opinions = {
            '孙宇晨': [
                {'topic': 'AI', 'view': '看多', 'content': 'AI是未来10年最大的产业趋势，算力、数据、应用三层都值得布局', 'time': '3小时前', 'impact': 0.8},
                {'topic': '区块链', 'view': '看多', 'content': '加密市场正在迎来新一轮牛市，关注底层基础设施和Layer2项目', 'time': '1天前', 'impact': 0.7},
                {'topic': '跨境电商', 'view': '看多', 'content': '东南亚电商渗透率快速提升，出海企业迎来黄金期', 'time': '2天前', 'impact': 0.75},
                {'topic': '半导体', 'view': '看多', 'content': '国产替代是长期趋势，芯片设计和制造环节都有机会', 'time': '3天前', 'impact': 0.82}
            ],
            '白毛女': [
                {'topic': '房地产', 'view': '中性', 'content': '房地产市场分化加剧，一线城市核心资产仍有价值', 'time': '2小时前', 'impact': 0.85},
                {'topic': '消费', 'view': '看多', 'content': '消费复苏趋势明确，关注可选消费和服务消费', 'time': '1天前', 'impact': 0.78},
                {'topic': '医药', 'view': '看多', 'content': '创新药估值处于低位，看好研发管线丰富的企业', 'time': '2天前', 'impact': 0.83},
                {'topic': '宏观', 'view': '谨慎', 'content': '外部环境复杂，保持适度防御性配置', 'time': '3天前', 'impact': 0.9}
            ],
            '饭统戴老板': [
                {'topic': '新能源', 'view': '看多', 'content': '新能源产业从政策驱动转向技术驱动，关注储能和绿氢', 'time': '4小时前', 'impact': 0.88},
                {'topic': '制造业', 'view': '看多', 'content': '中国制造业竞争力持续提升，高端制造是长期主线', 'time': '1天前', 'impact': 0.85},
                {'topic': 'AI应用', 'view': '看多', 'content': 'AI应用落地加速，关注垂直行业解决方案提供商', 'time': '2天前', 'impact': 0.9},
                {'topic': '消费电子', 'view': '中性', 'content': '消费电子处于周期底部，等待换机潮到来', 'time': '3天前', 'impact': 0.75}
            ],
            '卢克文工作室': [
                {'topic': '产业链', 'view': '看多', 'content': '中国产业链完整性是核心竞争力，关注自主可控领域', 'time': '5小时前', 'impact': 0.85},
                {'topic': '东南亚', 'view': '看多', 'content': '东南亚正在成为新的世界工厂，相关产业链值得关注', 'time': '1天前', 'impact': 0.8},
                {'topic': '能源', 'view': '看多', 'content': '能源安全是国家战略，新能源和传统能源都有机会', 'time': '2天前', 'impact': 0.82},
                {'topic': '科技', 'view': '看多', 'content': '科技自立自强是大方向，硬科技企业值得长期跟踪', 'time': '3天前', 'impact': 0.88}
            ],
            '洪灏': [
                {'topic': 'A股', 'view': '中性偏多', 'content': '市场处于底部区域，逐步增加权益配置', 'time': '1小时前', 'impact': 0.85},
                {'topic': '流动性', 'view': '看多', 'content': '流动性环境有利于市场表现', 'time': '1天前', 'impact': 0.8},
                {'topic': '成长股', 'view': '看多', 'content': '成长股估值吸引力提升，关注高景气赛道', 'time': '2天前', 'impact': 0.78},
                {'topic': '消费', 'view': '中性', 'content': '消费复苏仍需观察，等待数据验证', 'time': '3天前', 'impact': 0.75}
            ],
            '智本社': [
                {'topic': '宏观', 'view': '谨慎', 'content': '经济复苏基础尚不牢固，保持理性预期', 'time': '3小时前', 'impact': 0.82},
                {'topic': '金融', 'view': '中性', 'content': '金融改革深化，关注券商和保险的估值修复', 'time': '1天前', 'impact': 0.78},
                {'topic': '投资', 'view': '看多', 'content': '长期投资价值显现，关注优质企业', 'time': '2天前', 'impact': 0.8},
                {'topic': '创新', 'view': '看多', 'content': '创新驱动发展，科技企业是长期赢家', 'time': '3天前', 'impact': 0.85}
            ]
        }
        
        self.topic_stock_mapping = {
            'AI': ['000977', '300308', '688256', '300474', '300222'],
            '人工智能': ['000977', '300308', '688256', '300474', '300222'],
            '区块链': ['300364', '002261', '300059'],
            'Web3': ['300364', '002261'],
            '新能源': ['300750', '002594', '601012', '300274'],
            '光伏': ['601012', '300274', '600438'],
            '储能': ['300750', '300274', '002121'],
            '半导体': ['688012', '600584', '603986', '688256'],
            '芯片': ['688256', '300474', '603986'],
            '消费': ['600519', '000858', '000333', '600887'],
            '医药': ['600276', '300760', '002437'],
            '创新药': ['600276', '300760', '300122'],
            '房地产': ['000002', '600048', '000858'],
            '宏观': ['601318', '601988', '600036'],
            '金融': ['601318', '601988', '600036', '600030'],
            '制造业': ['000333', '002594', '601012'],
            '消费电子': ['000100', '000725', '002456'],
            '跨境电商': ['002095', '002291', '300133'],
            '能源': ['601012', '300750', '600028'],
            '科技': ['000977', '300308', '688012'],
            '成长股': ['300750', '688256', '300308'],
            '券商': ['600030', '601211', '000776'],
            '高端制造': ['002594', '600893', '300024'],
            '算力': ['000977', '300308', '600584'],
            '数据': ['000977', '300222', '300104']
        }
    
    def get_influencer_list(self):
        result = []
        for name, info in self.influencers.items():
            result.append({
                'name': name,
                'followers': info['followers'],
                'platform': info['platform'],
                'expertise': info['expertise'],
                'reliability': info['reliability']
            })
        return result
    
    def get_recent_opinions(self, influencer_name=None, count=5):
        if influencer_name:
            opinions = self.influencer_opinions.get(influencer_name, [])
        else:
            opinions = []
            for name, ops in self.influencer_opinions.items():
                for op in ops:
                    opinions.append({**op, 'author': name, 'reliability': self.influencers[name]['reliability']})
        
        opinions.sort(key=lambda x: x['impact'] * x['reliability'] if 'reliability' in x else x['impact'], reverse=True)
        return opinions[:count]
    
    def get_opinion_for_stock(self, symbol):
        symbol_clean = str(symbol).replace('.SS', '').replace('.SZ', '')
        
        stock_opinions = []
        for topic, stocks in self.topic_stock_mapping.items():
            if symbol_clean in stocks:
                for name, ops in self.influencer_opinions.items():
                    for op in ops:
                        if op['topic'] == topic:
                            stock_opinions.append({
                                'author': name,
                                'topic': topic,
                                'view': op['view'],
                                'content': op['content'],
                                'time': op['time'],
                                'impact': op['impact'],
                                'reliability': self.influencers[name]['reliability']
                            })
        
        stock_opinions.sort(key=lambda x: x['impact'] * x['reliability'], reverse=True)
        return stock_opinions[:3]
    
    def calculate_influencer_score(self, symbol):
        symbol_clean = str(symbol).replace('.SS', '').replace('.SZ', '')
        
        score = 0
        total_weight = 0
        
        for topic, stocks in self.topic_stock_mapping.items():
            if symbol_clean in stocks:
                for name, ops in self.influencer_opinions.items():
                    for op in ops:
                        if op['topic'] == topic:
                            weight = op['impact'] * self.influencers[name]['reliability']
                            if op['view'] in ['看多', '买入']:
                                score += weight * 0.5
                            elif op['view'] in ['看空', '卖出']:
                                score -= weight * 0.5
                            elif op['view'] == '中性偏多':
                                score += weight * 0.25
                            elif op['view'] == '谨慎乐观':
                                score += weight * 0.2
                            elif op['view'] == '中性':
                                score += weight * 0
                            elif op['view'] == '谨慎':
                                score -= weight * 0.2
                            total_weight += weight
        
        if total_weight > 0:
            score = score / total_weight
        else:
            score = 0
        
        return round(score, 3)
    
    def get_top_topics(self, count=5):
        topic_scores = {}
        
        for name, ops in self.influencer_opinions.items():
            reliability = self.influencers[name]['reliability']
            for op in ops:
                topic = op['topic']
                if topic not in topic_scores:
                    topic_scores[topic] = {'score': 0, 'count': 0, 'views': []}
                
                view_score = 0
                if op['view'] in ['看多', '买入']:
                    view_score = 1
                elif op['view'] in ['看空', '卖出']:
                    view_score = -1
                elif op['view'] == '中性偏多':
                    view_score = 0.5
                elif op['view'] == '谨慎乐观':
                    view_score = 0.3
                elif op['view'] == '中性':
                    view_score = 0
                elif op['view'] == '谨慎':
                    view_score = -0.3
                
                topic_scores[topic]['score'] += view_score * op['impact'] * reliability
                topic_scores[topic]['count'] += 1
                topic_scores[topic]['views'].append({
                    'author': name,
                    'view': op['view'],
                    'content': op['content'],
                    'reliability': reliability
                })
        
        sorted_topics = sorted(topic_scores.items(), key=lambda x: abs(x[1]['score']), reverse=True)
        
        result = []
        for topic, data in sorted_topics[:count]:
            result.append({
                'topic': topic,
                'score': round(data['score'], 2),
                'sentiment': '看多' if data['score'] > 0.2 else ('看空' if data['score'] < -0.2 else '中性'),
                'stocks': self.topic_stock_mapping.get(topic, []),
                'opinions': data['views'][:3]
            })
        
        return result
    
    def search_opinions(self, keyword):
        results = []
        keyword = keyword.lower()
        
        for name, ops in self.influencer_opinions.items():
            for op in ops:
                if keyword in op['topic'].lower() or keyword in op['content'].lower():
                    results.append({
                        'author': name,
                        'topic': op['topic'],
                        'view': op['view'],
                        'content': op['content'],
                        'time': op['time'],
                        'impact': op['impact'],
                        'reliability': self.influencers[name]['reliability']
                    })
        
        results.sort(key=lambda x: x['impact'] * x['reliability'], reverse=True)
        return results

influencer_analyst = InfluencerAnalyst()