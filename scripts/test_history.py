#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试历史数据查询和K线图生成
"""

import sys
sys.path.append('/home/parallels/.openclaw/workspace/skills/a-stock-fetcher/scripts')
from historical_data import fetch_historical_data, get_summary_stats, format_summary_stats
from candlestick_chart import draw_full_chart
from indicators_v2 import calculate_all_indicators, interpret_indicators

print("📊 测试历史数据查询和图表生成\n")
print("=" * 80)

# 获取茅台30天日K数据
candles = fetch_historical_data('sh600519', '1d', 30)

if candles:
    print("\n" + "=" * 80)
    print("📊 统计摘要")
    print("=" * 80)

    stats = get_summary_stats(candles)
    print(format_summary_stats(stats))

    print("\n" + "=" * 80)
    print("📈 K线图")
    print("=" * 80)

    # 计算技术指标
    indicators = calculate_all_indicators(candles)
    interpretation = interpret_indicators(indicators, -1)

    print("\n指标解读:")
    for key, value in interpretation.items():
        print(f"  {key}: {value}")

    print("\n")
    chart = draw_full_chart(candles, indicators)
    print(chart)

    print("\n" + "=" * 80)
    print("✅ 测试完成！")
else:
    print("❌ 获取数据失败")
