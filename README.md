# 📈 股票预测系统

## 📋 项目概述

基于多智能体协作架构的A股预测系统，通过分析师团队的智能协作，提供买入/卖出决策、价格预测和风险管理建议。

## 🎯 核心功能

### 智能体团队

- **📊 技术分析智能体**: K线形态、技术指标、量价关系
- **💰 基本面分析智能体**: 财务数据、估值模型、行业分析
- **📰 情绪分析智能体**: 新闻情绪、事件影响、市场热度
- **🐂🐻 多空辩论智能体**: 看涨看跌辩论、风险评估
- **🎯 决策智能体**: 综合分析、交易建议、止盈止损

### 决策输出

当用户输入任意A股代码时，系统返回：

- ✅ **操作建议**: 买入 / 卖出 / 观望
- 💰 **买入价格**: 建议买入价位
- 📈 **目标价格**: 预期目标价位
- ⛔ **止损价格**: 风险控制价位
- 📊 **信心度**: 决策可靠性评分
- 📝 **决策理由**: 多维度分析依据

## 🏗️ 项目架构

```
股票预测系统/
├── agents/                 # 智能体模块
│   ├── technical/         # 技术分析智能体
│   ├── fundamental/       # 基本面分析智能体
│   ├── sentiment/         # 情绪分析智能体
│   ├── debate/             # 辩论智能体（多空）
│   └── decision/          # 决策智能体
├── dataflows/            # 数据流处理
│   ├── stock_api.py       # A股数据接口
│   ├── indicators.py      # 技术指标计算
│   ├── patterns.py        # 形态识别
│   └── cache.py           # 数据缓存
├── graph/                # 智能体协作图
│   ├── trading_graph.py  # 主流程编排
│   ├── setup.py          # 智能体初始化
│   └── propagation.py    # 信号传播
├── models/               # 分析模型
│   ├── pattern_recognition.py  # 形态识别
│   ├── scoring.py              # 评分系统
│   └── diagnosis.py            # 诊断系统
├── utils/                # 工具函数
│   └── logger.py         # 日志管理
├── main.py              # 主入口
└── requirements.txt     # 依赖包
```

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Redis（可选，用于缓存）
- PostgreSQL（可选，用于历史数据）

### 安装

```bash
# 克隆仓库
git clone https://github.com/yunshao512/Stock-testing-project.git
cd Stock-testing-project

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

### 使用示例

```python
from trading_graph import TradingAgentsGraph

# 初始化系统
system = TradingAgentsGraph()

# 分析股票
symbol = "600519"  # 贵州茅台
decision = system.propagate(symbol)

print(f"操作建议: {decision.action}")
print(f"买入价格: {decision.buy_price}")
print(f"止损价格: {decision.stop_loss}")
```

## 📊 功能模块

### 1. 形态识别系统

- 底部横盘形态
- 上升趋势细分形态
- 下降趋势细分形态
- 特殊K线形态（金叉、死叉、吞没等）

### 2. 评分系统

- **形态打分**: K线形态质量评分
- **量价打分**: 量价配合度评分
- **技术指标打分**: RSI、MACD、KDJ等指标评分
- **综合评分**: 多维度加权评分

### 3. 诊断系统

- **趋势诊断**: 短/中/长期趋势判断
- **位置诊断**: 价格在波段中的位置
- **形态诊断**: 当前形态识别
- **信号诊断**: 买卖信号强度

### 4. 风险管理

- 自动止损（-3%）
- 自动止盈（+5%）
- 动态仓位管理
- 风险预警

## 🔄 自动提交策略

### 每日凌晨4点自动提交

```bash
# Cron任务配置
0 4 * * * cd /path/to/Stock-testing-project && bash auto_commit.sh
```

**提交内容**:
- ✅ 可运行的代码
- ✅ 符合开发规范
- ✅ 测试通过
- ✅ 文档更新

## 📚 参考项目

本系统参考了 [tradingagents](https://github.com/oficcejo/tradingagents.git) 的整体框架和设计思路。

## 📝 开发日志

- 2026-02-02: 项目初始化，创建仓库结构
- 待更新...

## ⚠️ 免责声明

本系统仅供学习和研究使用，不构成投资建议。股市有风险，投资需谨慎。

---

**开发者**: 小智 (AI Assistant)
**仓库**: https://github.com/yunshao512/Stock-testing-project.git
**更新时间**: 2026-02-02
