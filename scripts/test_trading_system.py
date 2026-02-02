#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试交易系统完整流程
"""

import sys
sys.path.append('/home/parallels/.openclaw/workspace/skills/a-stock-fetcher/scripts')
from trading_system import TradingSystem
from analysis_model import AnalysisModel
from daily_workflow import run_daily_workflow

print("🧪 测试交易系统\n")
print("="*80)

# 测试1：初始化交易系统
print("\n📊 测试1：初始化交易系统")
print("-"*80)

trading_system = TradingSystem(initial_capital=100000.0)
print(trading_system.format_summary())

# 测试2：分析模型
print("\n📊 测试2：分析模型")
print("-"*80)

analysis_model = AnalysisModel(stop_loss_pct=0.05, take_profit_pct=0.10)
symbol = 'sh600519'

signal = analysis_model.analyze(symbol, days=30)
if signal:
    print(analysis_model.format_signal(signal))
else:
    print("❌ 分析失败")

# 测试3：模拟买入
print("\n📊 测试3：模拟买入")
print("-"*80)

if signal and signal.action == "买入":
    success = trading_system.buy(
        symbol=signal.symbol,
        price=signal.price,
        quantity=100,
        stop_loss_pct=0.05,
        take_profit_pct=0.10,
        reason="技术分析信号",
        confidence=signal.confidence
    )
    if success:
        print("✅ 买入成功")
        print(trading_system.format_summary())

# 测试4：模拟卖出
print("\n📊 测试4：模拟卖出")
print("-"*80)

if trading_system.positions:
    for symbol in list(trading_system.positions.keys()):
        success = trading_system.sell(
            symbol=symbol,
            price=trading_system.positions[symbol].buy_price * 1.08,  # 假设涨8%
            reason="测试卖出"
        )
        if success:
            print("✅ 卖出成功")
            print(trading_system.format_summary())

# 测试5：每日工作流程
print("\n📊 测试5：每日工作流程")
print("-"*80)

watch_list = ['sh600519', 'sz000001', 'sz000858']
run_daily_workflow(watch_list, mode="simulation")

print("\n" + "="*80)
print("✅ 所有测试完成！")
