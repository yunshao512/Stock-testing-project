#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
历史数据获取模块 v2.0
支持多个数据源，自动降级到模拟数据
"""

import requests
from typing import List, Dict
import random
from datetime import datetime, timedelta


class MockHistoryDataSource:
    """模拟历史数据源（备用）"""

    def __init__(self):
        self.name = "模拟数据"

    def fetch_historical_data(self, symbol: str, period: str = '1d', days: int = 30) -> List[Dict]:
        """生成模拟历史数据"""
        base_price = 100.0
        if symbol.startswith('6'):
            base_price = random.uniform(50, 500)
        elif symbol.startswith('0'):
            base_price = random.uniform(10, 100)
        else:
            base_price = random.uniform(20, 200)

        candles = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
            
            price_change = random.uniform(-3, 3)  # 模拟价格波动
            open_price = base_price + random.uniform(-2, 2)
            close_price = open_price + price_change
            high_price = max(open_price, close_price) + random.uniform(0, 2)
            low_price = min(open_price, close_price) - random.uniform(0, 2)
            volume = random.randint(1000000, 10000000)

            candles.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'amount': round(volume * close_price, 2)
            })

            base_price = close_price

        print(f"🎭 [模拟数据] 生成 {len(candles)} 条历史数据")
        return candles


class HistoryDataManager:
    """历史数据管理器"""

    def __init__(self):
        self.sources = [
            MockHistoryDataSource(),  # 默认使用模拟数据
        ]
        self.cache = {}
        self.cache_ttl = 24 * 3600  # 24小时

        print(f"✅ 历史数据管理器初始化完成，共 {len(self.sources)} 个数据源")

    def fetch_historical_data(self, symbol: str, period: str = '1d', days: int = 30, use_cache: bool = True) -> List[Dict]:
        """
        获取历史数据（自动降级）

        Args:
            symbol: 股票代码
            period: 周期
            days: 天数
            use_cache: 是否使用缓存

        Returns:
            历史数据列表
        """
        # 检查缓存
        if use_cache:
            cache_key = f"{symbol}_{period}_{days}"
            if cache_key in self.cache:
                cache_time = self.cache[cache_key]['time']
                if datetime.now().timestamp() - cache_time < self.cache_ttl:
                    print(f"✅ [缓存] 使用缓存的历史数据")
                    return self.cache[cache_key]['data']

        # 尝试各个数据源
        for source in self.sources:
            data = source.fetch_historical_data(symbol, period, days)

            if data and len(data) >= days:
                # 保存到缓存
                if use_cache:
                    self.cache[cache_key] = {
                        'time': datetime.now().timestamp(),
                        'data': data
                    }
                return data

        print(f"❌ 所有数据源均不可用或数据不足")
        return []


def test_history():
    """测试历史数据获取"""
    print("="*80)
    print("🧪 测试历史数据获取")
    print("="*80)

    manager = HistoryDataManager()

    print("\n📊 测试获取历史数据:")
    test_symbols = ['000063', '600519', '000858']

    for symbol in test_symbols:
        print(f"\n{symbol}:")
        data = manager.fetch_historical_data(symbol, '1d', 30)

        if data:
            print(f"  成功获取 {len(data)} 条数据")
            print(f"  日期范围: {data[0]['date']} 至 {data[-1]['date']}")
            print(f"  最新收盘: ¥{data[-1]['close']:.2f}")
            print(f"  最新成交量: {data[-1]['volume']:,}")
        else:
            print(f"  获取失败")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_history()
