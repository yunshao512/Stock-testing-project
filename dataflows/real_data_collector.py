#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
真实数据接入 - 使用AkShare获取A股数据
"""

import sys
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time


class RealDataCollector:
    """真实数据收集器"""

    def __init__(self):
        print("✅ 真实数据收集器初始化完成")

    def check_akshare(self) -> bool:
        """检查AkShare是否可用"""
        try:
            import akshare as ak
            print("✅ AkShare已安装")
            return True
        except ImportError:
            print("⚠️ AkShare未安装，尝试安装...")
            return self._install_akshare()

    def _install_akshare(self) -> bool:
        """尝试安装AkShare"""
        try:
            import subprocess
            print("  正在安装AkShare...")
            subprocess.run([sys.executable, "-m", "pip", "install", "akshare"], 
                         check=True, timeout=300)
            print("✅ AkShare安装成功")
            return True
        except Exception as e:
            print(f"❌ AkShare安装失败: {e}")
            return False

    def fetch_real_history(self, symbol: str, days: int = 30) -> List[Dict]:
        """
        获取真实历史数据

        Args:
            symbol: 股票代码（如 '000063', '600519'）
            days: 天数

        Returns:
            历史K线数据
        """
        if not self.check_akshare():
            print("❌ 无法获取真实数据，使用备用方案")
            return []

        try:
            import akshare as ak

            # AkShare历史数据API
            # 转换股票代码格式
            if symbol.startswith('6'):
                ak_symbol = f"sh{symbol}"
            elif symbol.startswith('3'):
                ak_symbol = f"sh{symbol}"
            elif symbol.startswith('0'):
                ak_symbol = f"sz{symbol}"
            else:
                ak_symbol = f"sh{symbol}"

            # 计算开始日期
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 10)

            print(f"  📡 获取 {ak_symbol} 的历史数据...")
            print(f"     日期范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")

            # 获取历史数据
            df = ak.stock_zh_a_hist(symbol=ak_symbol,
                                       period="daily",
                                       start_date=start_date.strftime('%Y%m%d'),
                                       end_date=end_date.strftime('%Y%m%d'),
                                       adjust="qfq")  # 前复权
                                       )

            if df is None or len(df) == 0:
                print(f"  ❌ 未获取到数据")
                return []

            print(f"  ✅ 获取到 {len(df)} 条历史数据")

            # 转换为标准格式
            candles = []
            for i in range(min(days, len(df))):
                row = df.iloc[len(df) - i - 1]
                
                candle = {
                    'date': row['trade_date'],
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['vol']),
                    'amount': float(row.get('amount', 0))
                }
                candles.append(candle)

            return candles

        except Exception as e:
            print(f"  ❌ 获取真实数据失败: {e}")
            return []

    def fetch_month_history(self, symbol: str) -> List[Dict]:
        """
        获取一个月的历史数据（约20个交易日）

        Args:
            symbol: 股票代码

        Returns:
            历史K线数据
        """
        # A股一个月约20个交易日
        days = 20
        return self.fetch_real_history(symbol, days)


def test_real_data():
    """测试真实数据获取"""
    print("="*80)
    print("🧪 测试真实数据接入")
    print("="*80)

    collector = RealDataCollector()

    print("\n📊 测试获取真实历史数据:")
    test_symbol = "000063"  # 中兴通讯

    history = collector.fetch_month_history(test_symbol)

    if history:
        print(f"\n  成功获取 {len(history)} 条真实数据:")
        print(f"  日期范围: {history[0]['date']} 至 {history[-1]['date']}")
        print(f"  最新收盘: ¥{history[-1]['close']:.2f}")
        print(f"  最早收盘: ¥{history[0]['close']:.2f}")

        # 显示最近5天数据
        print(f"\n  最近5天数据:")
        for i, candle in enumerate(history[-5:], 1):
            print(f"    {candle['date']}: ¥{candle['close']:.2f} " +
                  f"(涨跌:{((candle['close'] - history[-(i+1)-1]['close']) / history[-(i+1)-1]['close'] * 100):+.1f}%)" if i > 0 else "")
    else:
        print("  ❌ 获取失败")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_real_data()
