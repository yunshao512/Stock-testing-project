#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据源适配器 v2.1
支持多个A股数据源，自动切换和降级（含新浪财经）
"""

import sys
import os
from typing import List, Dict, Optional

# 添加项目根目录到路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from backup_data_sources import SinaDataSource, DataQualityScorer
from scripts.stock_api_fixed import fetch_stock_data as fetch_stock_fixed
from data_cache import get_cache


class DataAdapterManager:
    """数据源适配器管理器（简化版）"""

    def __init__(self):
        """初始化数据源管理器"""
        self.sources = []

        # 添加数据源（新浪财经）
        self.sina_source = SinaDataSource()
        self.sources.append(self.sina_source)

        # 数据质量评分器
        self.quality_scorer = DataQualityScorer()

        # 缓存管理器
        self.cache = get_cache(cache_hours=1)

        print(f"✅ 数据源管理器初始化完成，共 {len(self.sources)} 个数据源")

    def fetch_stock_data(self, symbols: List[str], use_cache: bool = True) -> List[Dict]:
        """
        获取股票实时数据（自动切换数据源）

        Args:
            symbols: 股票代码列表
            use_cache: 是否使用缓存

        Returns:
            股票数据列表
        """
        # 尝试从缓存获取
        if use_cache:
            cache_key = ','.join(sorted(symbols))
            cached_data = self.cache.get('stock_data', symbols=cache_key)

            if cached_data:
                print(f"✅ [缓存] 使用缓存的股票数据")
                return cached_data.get('stocks', [])

        # 1. 尝试新浪财经
        data = self.sina_source.fetch_stock_data(symbols)

        if data:
            # 保存到缓存
            if use_cache:
                self.cache.set('stock_data', {'stocks': data}, symbols=cache_key)
            return data

        # 2. 如果新浪失败，尝试旧API
        print(f"⚠️ 新浪财经返回空数据，尝试备用方案...")
        data = fetch_stock_fixed(symbols, use_cache=False)

        if data:
            return data

        print(f"❌ 所有数据源均不可用")
        return []

    def fetch_historical_data(self, symbol: str, period: str = '1d', days: int = 30) -> List[Dict]:
        """
        获取历史数据（自动切换数据源）

        Args:
            symbol: 股票代码
            period: 周期（1d=日线, 1w=周线, 1m=月线）
            days: 天数

        Returns:
            历史数据列表
        """
        # 尝试从缓存获取
        if use_cache:
            cached_data = self.cache.get('historical_data', symbol=symbol, period=period, days=days)

            if cached_data:
                print(f"✅ [缓存] 使用缓存的历史数据")
                return cached_data.get('candles', [])

        # 1. 尝试新浪财经
        data = self.sina_source.fetch_historical_data(symbol, period, days)

        if data:
            return data

        print(f"❌ 所有数据源均不可用")
        return []

    def get_available_sources(self) -> List[str]:
        """获取可用的数据源列表"""
        return [s.get_name() for s in self.sources if s.is_available()]


# 单例模式
_adapter_instance = None

def get_adapter() -> DataAdapterManager:
    """获取数据源适配器实例（单例）"""
    global _adapter_instance

    if _adapter_instance is None:
        _adapter_instance = DataAdapterManager()

    return _adapter_instance


def test_adapter():
    """测试数据源适配器"""
    print("="*80)
    print("🧪 测试数据源适配器")
    print("="*80)

    adapter = get_adapter()

    print("\n📊 可用数据源:")
    for source_name in adapter.get_available_sources():
        print(f"  • {source_name}")

    print("\n📊 测试获取股票数据:")
    data = adapter.fetch_stock_data(['600519', '000063', '000858'])

    for stock in data:
        quality = adapter.quality_scorer.score_data(stock)
        print(f"\n  {stock['symbol']} {stock['name']} [质量: {quality*100:.0f}%]")
        print(f"    价格: ¥{stock['price']:.2f}")
        print(f"    涨跌: {stock['change_percent']:+.2f}%")
        print(f"    来源: {stock.get('source', 'N/A')}")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_adapter()
