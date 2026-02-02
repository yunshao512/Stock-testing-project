#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速批量测试 v1.0
快速测试所有80只股票（2月2日7点前完成）
"""

import sys
sys.path.append('/home/parallels/.openclaw/workspace/skills/a-stock-fetcher/scripts')
from stock_pool import StockPool
from postgres_stock_database_v2 import PostgresStockDatabase
from new_analysis_model import NewAnalysisModel
from datetime import datetime
import time as time_module

class FastBatchTest:
    """快速批量测试"""

    def __init__(self):
        """初始化"""
        self.pool = StockPool()
        self.db = PostgresStockDatabase()
        self.model = NewAnalysisModel()
        self.date = datetime.now().strftime("%Y-%m-%d")

    def test_all_stocks(self, batch_size: int = 10):
        """测试所有股票"""
        active_stocks = self.pool.get_active_stocks()
        total_batches = (len(active_stocks) + batch_size - 1) // batch_size

        print(f"\n📊 开始快速测试")
        print("="*80)
        print(f"  总股票数: {len(active_stocks)}")
        print(f"  批次大小: {batch_size}")
        print(f"  总批次: {total_batches}")
        print("="*80)

        all_buy_signals = 0
        all_sell_signals = 0

        for batch_num in range(total_batches):
            start = batch_num * batch_size
            end = min(start + batch_size, len(active_stocks))
            batch = active_stocks[start:end]

            print(f"\n批次 {batch_num+1}/{total_batches} ({start+1}-{end})")

            for stock in batch:
                symbol = stock['symbol']
                name = stock['name']

                print(f"\n📊 {name} ({symbol})")

                # 分析
                signal = self.model.analyze(symbol, days=30)

                if signal:
                    # 添加到数据库
                    self.db.add_signal(
                        date=self.date,
                        symbol=symbol,
                        signal_type='new_model',
                        action=signal.action,
                        price=signal.price,
                        confidence=signal.confidence,
                        reasons="; ".join(signal.reasons)
                    )

                    print(f"  信号: {signal.action}")
                    print(f"  信心: {signal.confidence*100:.0f}%")

                    # 统计
                    if signal.action == "买入":
                        all_buy_signals += 1
                    elif "卖出" in signal.action:
                        all_sell_signals += 1
                else:
                    print(f"  无信号")

                # 短暂延迟（避免API限流）
                time_module.sleep(0.5)

        # 添加每日汇总
        print("\n" + "="*80)
        print("添加每日汇总...")
        self.db.add_daily_summary(self.date)

        # 显示摘要
        print("\n" + "="*80)
        print("📊 测试完成！")
        print("="*80)
        print(f"  测试股票: {len(active_stocks)}")
        print(f"  买入信号: {all_buy_signals}")
        print(f"  卖出信号: {all_sell_signals}")
        print(f"  总信号: {all_buy_signals + all_sell_signals}")
        print("="*80)

        # 显示数据库摘要
        print(self.db.format_summary())

def run_fast_test():
    """运行快速测试"""
    print("🧪 快速批量测试系统\n")

    fast_test = FastBatchTest()
    fast_test.test_all_stocks(batch_size=10)

if __name__ == "__main__":
    run_fast_test()
