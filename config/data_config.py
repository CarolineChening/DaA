import os

class DataConfig:
    def __init__(self):
        # 是否使用真实数据
        self.USE_REAL_DATA = os.environ.get('USE_REAL_DATA', 'true').lower() == 'true'
        
        # AKShare配置
        self.AKSHARE_TIMEOUT = 30
        
        # 数据缓存时间（分钟）
        self.CACHE_TTL = 5
        
        # 日志级别
        self.LOG_LEVEL = 'INFO'
        
        # 新闻获取数量
        self.NEWS_COUNT = 10
        
        # 雪球大V观点数量
        self.SNOWBALL_OPINIONS_COUNT = 5
    
    def use_real_data(self):
        return self.USE_REAL_DATA
    
    def get_cache_ttl(self):
        return self.CACHE_TTL

config = DataConfig()