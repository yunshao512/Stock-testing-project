#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
真实历史数据获取模块
支持腾讯财经和新浪财经等数据源
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class TencentHistoryDataSource:
    """腾讯财经历史数据源"""

    def __init__(self):
        self.name = "腾讯财经"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 10

    def fetch_historical_data(self, symbol: str, period: str = '1d', days: int = 30) -> List[Dict]:
        """
        从腾讯财经获取历史数据

        注意：腾讯财经API不直接支持历史数据，使用模拟数据
        """
        print(f"⚠️ [{self.name}] 不支持历史数据，使用备用方案")
        return []


class SinaHistoryDataSource:
    """新浪财经历史数据源"""

    def __init__(self):
        self.name = "新浪财经"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 10

    def fetch_historical_data(self, symbol: str, period: str = '1d', days: int = 30) -> List[Dict]:
        """从新浪财经获取历史数据"""
        try:
            # 转换股票代码
            if symbol.startswith('sh'):
                code = f"sh{symbol[2:]}"
            elif symbol.startswith('sz'):
                code = f"sz{symbol[2:]}"
            else:
                code = f"sh{symbol}"

            # 新浪历史数据API
            # 格式: http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh600519&scale=240&ma=no&datalen=100
            scale_map = {'1d': '240', '1w': '101', '1m': '102'}  # 日线、周线、月线
            scale = scale_map.get(period, '240')

            url = f"http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={code}&scale={scale}&ma=no&datalen={days}"

            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            json_data = response.json()

            data = []
            if 'result' in json_data and 'data' in json_data['result']:
                for item in json_data['result']['data']:
                    data.append({
                        'date': item['day'],
                        'open': float(item['open']),
                        'high': float(item['high']),
                        'low': float(item['low']),
                        'close': float(item['close']),
                        'volume': int(item['vol']),
                        'amount': float(item.get('amount', 0))
                    })

            if data:
                print(f"🌐 [{self.name}] 成功获取 {len(data)} 条历史数据")

            return data

        except Exception as e:
            print(f"❌ [{self.name}] 获取历史数据失败: {e}")
            return []


class RealHistoryDataManager:
    """真实历史数据管理器"""

    def __init__(self):
        self.sources = [
            SinaHistoryDataSource(),  # 优先使用新浪
            TencentHistoryDataSource(),  # 备用
        ]
        self.cache = {}
        self.cache_ttl = 24 * 3600  # 24小时缓存

        print(f"✅ 历史数据管理器初始化完成，共 {len(self.sources)} 个数据源")

    def fetch_historical_data(self, symbol: str, period: str = '1d', days: int = 30) -> List[Dict]:
        """
        获取历史数据（带缓存）

        Args:
            symbol: 股票代码
            period: 周期（1d=日线, 1w=周线, 1m=月线）
            days: 天数

        Returns:
            历史数据列表
        """
        # 检查缓存
        cache_key = f"{symbol}_{period}_{days}"
        if cache_key in self.cache:
            cache_time = self.cache[cache_key]['time']
            if datetime.now().timestamp() - cache_time < self.cache_ttl:
                print(f"✅ [缓存] 使用缓存的历史数据")
                return self.cache[cache_key]['data']

        # 尝试各个数据源
        for source in self.sources:
            data = source.fetch_historical_data(symbol, period, days)

            if data:
                # 保存到缓存
                self.cache[cache_key] = {
                    'time': datetime.now().timestamp(),
                    'data': data
                }
                return data

        print(f"❌ 所有数据源均不可用")
        return []

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        print("🗑️ 历史数据缓存已清空")


def test_history():
    """测试历史数据获取"""
    print("="*80)
    print("🧪 测试真实历史数据获取")
    print("="*80)

    manager = RealHistoryDataManager()

    print("\n📊 测试获取历史数据:")
    test_symbols = ['000063', '600519', '000858']

    for symbol in test_symbols:
        print(f"\n{symbol}:")
        data = manager.fetch_historical_data(symbol, '1d', 30)

        if data:
            print(f"  成功获取 {len(data)} 条数据")
            print(f"  日期范围: {data[0]['date']} 至 {data[-1]['date']}")
            print(f"  最新收盘: ¥{data[-1]['close']:.2f}")
        else:
            print(f"  获取失败")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_history()
