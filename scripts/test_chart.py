#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试K线图生成
"""

import sys
sys.path.append('/home/parallels/.openclaw/workspace/skills/a-stock-fetcher/scripts')
from candlestick_chart import draw_full_chart

# 生成测试数据
def generate_test_data(days=20):
    """生成模拟K线数据"""
    candles = []
    import random

    base_price = 100.0
    for i in range(days):
        open_p = base_price + random.uniform(-2, 2)
        close_p = open_p + random.uniform(-5, 5)
        high_p = max(open_p, close_p) + random.uniform(0, 2)
        low_p = min(open_p, close_p) - random.uniform(0, 2)
        volume = random.randint(10000, 100000)

        candles.append({
            'date': f'2026-01-{i+1:02d}',
            'open': round(open_p, 2),
            'high': round(high_p, 2),
            'low': round(low_p, 2),
            'close': round(close_p, 2),
            'volume': volume
        })

        base_price = close_p

    return candles

# 生成模拟指标数据
def generate_test_indicators():
    """生成模拟指标数据"""
    import random

    rsi = [None] * 5 + [random.uniform(30, 70) for _ in range(15)]
    macd = [None] * 10 + [random.uniform(-1, 1) for _ in range(10)]
    histogram = [(m + random.uniform(-0.5, 0.5)) if m is not None else None for m in macd]

    k = [None] * 5 + [random.uniform(20, 80) for _ in range(15)]
    d = [(val - random.uniform(-5, 5)) if val is not None else None for val in k]
    j = [(val * 3 - prev * 2) if val is not None and prev is not None else None for val, prev in zip(k, d)]

    return {
        'rsi': rsi,
        'macd': {
            'macd': macd,
            'histogram': histogram
        },
        'kdj': {
            'K': k,
            'D': d,
            'J': j
        }
    }

# 测试
print("📊 测试K线图生成\n")
print("=" * 80)

candles = generate_test_data(20)
indicators = generate_test_indicators()

chart = draw_full_chart(candles, indicators)
print(chart)

print("\n" + "=" * 80)
print("✅ K线图生成测试完成！")
