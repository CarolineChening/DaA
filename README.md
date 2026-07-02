# A股策略分析系统

智能分析 · 科学决策 · 稳健投资

## 功能特性

- 📊 追踪止损（Trailing Stop）- 止损价随股价上涨动态调整
- 📈 技术指标分析（MACD、RSI、均线、神奇九转）
- 📰 新闻事件驱动选股 - 根据政策和新闻动态筛选股票
- 🧠 大V观点分析 - 综合孙宇晨、白毛女等大V的产业判断
- 📱 移动端支持 - 响应式设计，手机可访问
- 🔔 止损预警通知 - 距离止损线<2%时推送提醒
- 🌍 远程访问 - 通过ngrok实现公网访问

## 技术栈

- Python 3.8+
- Flask 2.0+
- AKShare（股票数据）
- pandas / numpy

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python web_app.py

# 访问
# 本地: http://localhost:8080
# 局域网: http://本机IP:8080
```

## 配置

### ngrok远程访问

1. 访问 https://dashboard.ngrok.com/signup 注册账号
2. 获取认证token
3. 在系统页面配置token并开启远程访问

## 项目结构

```
DaA/
├── web_app.py          # Flask后端API入口
├── config/             # 配置文件（持仓数据、交易规则）
├── data/               # 数据模块（行业数据、概念数据、龙虎榜）
├── strategies/         # 策略模块（神奇九转、MACD、RSI等）
├── research/           # 研究分析（大V观点、行业研究）
├── utils/              # 工具函数（时间工具、调度器、远程访问）
└── templates/          # 前端模板（HTML页面）
```

## 免责声明

本系统仅供学习参考，不构成投资建议。投资有风险，入市需谨慎。