cat > README.md << 'EOF'
# A股策略分析系统

智能分析 · 科学决策 · 稳健投资

## 功能特性

- 📊 追踪止损（Trailing Stop）
- 📈 技术指标分析（MACD、RSI、均线、神奇九转）
- 📰 新闻事件驱动选股
- 🧠 大V观点分析
- 📱 移动端支持
- 🔔 止损预警通知

## 技术栈

- Python 3.8+
- Flask
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
