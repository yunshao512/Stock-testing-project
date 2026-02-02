#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试涨跌停预警功能
"""

import sys
sys.path.append('/home/parallels/.openclaw/workspace/skills/a-stock-fetcher/scripts')
from alert_watcher import (
    get_stock_type, get_limit_percent, calculate_limits,
    check_limit_reached, format_alert_message, AlertWatcher, log_alert
)
from stock_api import fetch_stock_data

print("🔔 测试涨跌停预警功能\n")
print("=" * 80)

# 测试1：判断股票类型
print("\n📊 测试1：判断股票类型")
print("-" * 80)

test_stocks = [
    ('sh600519', '主板', 0.10),
    ('sh688981', '科创板', 0.20),
    ('sz300750', '创业板', 0.10),
    ('sz000858', '主板', 0.10),
]

for code, expected_type, expected_percent in test_stocks:
    stock_type = get_stock_type(code)
    limit_percent = get_limit_percent(code)
    status = "✅" if stock_type == expected_type else "❌"
    print(f"{status} {code}: {stock_type} (预期: {expected_type}), 涨跌幅: {limit_percent*100}%")

# 测试2：计算涨跌停价格
print("\n📊 测试2：计算涨跌停价格")
print("-" * 80)

stock_code = 'sh600519'
yesterday_close = 100.0  # 假设昨收100元
limits = calculate_limits(stock_code, yesterday_close)

print(f"股票: {stock_code}")
print(f"昨收价: ¥{yesterday_close:.2f}")
print(f"涨停价: ¥{limits['up_limit']:.2f}")
print(f"跌停价: ¥{limits['down_limit']:.2f}")
print(f"涨跌幅限制: ±{limits['limit_percent']:.2f}%")

# 测试3：检查涨跌停（模拟数据）
print("\n📊 测试3：检查涨跌停状态")
print("-" * 80)

test_prices = [
    100.0,   # 平盘
    110.0,   # 涨停
    90.0,    # 跌停
    109.5,   # 接近涨停
    90.5,    # 接近跌停
]

for price in test_prices:
    mock_stock = {
        'code': 'sh600519',
        'name': '贵州茅台',
        'price': price,
        'yesterday_close': 100.0,
        'change': price - 100.0,
        'change_percent': (price - 100.0) / 100.0 * 100
    }

    alert_info = check_limit_reached(mock_stock)

    if alert_info['is_up_limit']:
        status = "🔴 涨停"
    elif alert_info['is_down_limit']:
        status = "🟢 跌停"
    else:
        status = "➡️ 正常"

    message = format_alert_message(mock_stock, alert_info)
    print(f"¥{price:6.2f}: {status}")
    if message:
        print(f"        {message}")

# 测试4：单次检查
print("\n📊 测试4：单次检查（实际数据）")
print("-" * 80)

symbols = ['sh600519', 'sz000001']
stocks = fetch_stock_data(symbols, use_cache=False)

if stocks:
    for stock in stocks:
        alert_info = check_limit_reached(stock)
        status = "正常"

        if alert_info['is_up_limit']:
            status = "🔴 涨停"
        elif alert_info['is_down_limit']:
            status = "🟢 跌停"

        print(f"{stock['name']} ({stock['code']}): {status}")
        print(f"  当前价: ¥{stock['price']:.2f}")
        print(f"  涨跌幅: {stock['change_percent']:+.2f}%")

        if alert_info['up_limit']:
            print(f"  涨停价: ¥{alert_info['up_limit']:.2f}")
            print(f"  距涨停: ¥{alert_info['distance_to_up']:+.2f}")
        if alert_info['down_limit']:
            print(f"  跌停价: ¥{alert_info['down_limit']:.2f}")
            print(f"  距跌停: ¥{alert_info['distance_to_down']:+.2f}")
        print()

print("=" * 80)
print("✅ 测试完成！")
