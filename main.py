#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票预测系统 - 主入口
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph.trading_graph import TradingAgentsGraph


def main():
    """主函数"""
    print("="*80)
    print("📈 股票预测系统 - A股多智能体分析平台")
    print("="*80)
    print()

    # 获取股票代码
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
    else:
        print("请输入股票代码（如：600519）：", end="")
        symbol = input().strip()

    if not symbol:
        print("❌ 股票代码不能为空")
        return

    print()
    print(f"📊 正在分析股票: {symbol}")
    print()

    # 创建系统
    system = TradingAgentsGraph(debug=True)

    # 分析股票
    decision = system.propagate(symbol, days=30)

    # 输出结果
    print()
    print(decision.format_output())

    # 保存决策记录
    save_decision(decision)

    print("✅ 分析完成！")
    print()


def save_decision(decision):
    """保存决策记录"""
    import json
    from datetime import datetime

    # 创建数据目录
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)

    # 保存为JSON
    filename = f"decision_{decision.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(data_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(decision.to_dict(), f, ensure_ascii=False, indent=2)

    print(f"📄 决策记录已保存: {filepath}")


if __name__ == "__main__":
    main()
