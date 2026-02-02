#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票数据获取模块 - 使用数据适配器
集成多数据源和缓存机制
"""

import sys
import os
from typing import List

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataflows import get_adapter, get_cache


def fetch_stock_data(symbols: list, use_cache: bool = True) -> list:
    """
    获取股票实时数据（使用数据适配器）

    Args:
        symbols: 股票代码列表（如 ['600519', '000858']）
        use_cache: 是否使用缓存

    Returns:
        股票数据列表
    """
    adapter = get_adapter()
    cache = get_cache()

    # 尝试从缓存获取
    if use_cache:
        cache_key = ','.join(sorted(symbols))
        cached_data = cache.get('stock_data', symbols=cache_key)

        if cached_data:
            print(f"✅ [缓存] 使用缓存的股票数据")
            return cached_data.get('stocks', [])

    # 从数据源获取
    stocks = adapter.fetch_stock_data(symbols, use_cache=False)

    # 保存到缓存
    if stocks and use_cache:
        cache.set('stock_data', {'stocks': stocks}, symbols=cache_key)

    return stocks


def fetch_historical_data(symbol: str, period: str = '1d', days: int = 30, use_cache: bool = True) -> list:
    """
    获取历史数据（使用数据适配器）

    Args:
        symbol: 股票代码
        period: 周期（1d=日线, 1w=周线, 1m=月线）
        days: 天数
        use_cache: 是否使用缓存

    Returns:
        历史数据列表
    """
    adapter = get_adapter()
    cache = get_cache()

    # 尝试从缓存获取
    if use_cache:
        cached_data = cache.get('historical_data', symbol=symbol, period=period, days=days)

        if cached_data:
            print(f"✅ [缓存] 使用缓存的历史数据")
            return cached_data.get('candles', [])

    # 从数据源获取
    candles = adapter.fetch_historical_data(symbol, period, days)

    # 保存到缓存
    if candles and use_cache:
        cache.set('historical_data', {'candles': candles}, symbol=symbol, period=period, days=days)

    return candles


def test_fetch():
    """测试数据获取"""
    print("="*80)
    print("🧪 测试数据获取模块")
    print("="*80)

    print("\n📊 测试实时数据:")
    stocks = fetch_stock_data(['000063', '600519', '000858', '300750'])

    for stock in stocks:
        print(f"  {stock['symbol']} {stock['name']}: ¥{stock['price']:.2f} ({stock['change_percent']:+.2f}%)")

    print("\n📊 测试缓存效果:")
    print("  第二次获取（应该使用缓存）...")
    stocks_cached = fetch_stock_data(['000063', '600519', '000858', '300750'])

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_fetch()
