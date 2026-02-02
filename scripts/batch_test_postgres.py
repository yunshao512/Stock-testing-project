#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量测试系统 v1.0
使用PostgreSQL存储数据，批量测试500只股票
"""

import sys
sys.path.append('/home/parallels/.openclaw/workspace/skills/a-stock-fetcher/scripts')
from stock_pool import StockPool
from new_analysis_model import NewAnalysisModel
from postgres_stock_database_v2 import PostgresStockDatabase
from datetime import datetime
import time as time_module

class BatchTestSystemPostgres:
    """批量测试系统（PostgreSQL）"""

    def __init__(self, pool: StockPool, model: NewAnalysisModel, db: PostgresStockDatabase):
        """
        初始化批量测试系统

        Args:
            pool: 股票池
            model: 分析模型
            db: PostgreSQL数据库
        """
        self.pool = pool
        self.model = model
        self.db = db
        self.test_results = []

    def test_batch(self, batch_size: int = 10, start: int = 0) -> dict:
        """
        测试一批股票

        Args:
            batch_size: 批次大小
            start: 起始索引

        Returns:
            测试结果
        """
        batch = self.pool.get_batch(batch_size, start)

        if not batch:
            return {
                'batch_start': start,
                'batch_size': batch_size,
                'total_stocks': 0,
                'valid_signals': 0,
                'signals': {}
            }

        print(f"\n📊 开始测试批次 {start+1}-{start+len(batch)} ({len(batch)}只股票)\n")
        print("="*80)

        results = {}
        date = datetime.now().strftime("%Y-%m-%d")

        for i, stock in enumerate(batch):
            print(f"\n[{i+1}/{len(batch)}] {stock['name']} ({stock['symbol']})")

            # 使用新模型分析
            signal = self.model.analyze(stock['symbol'], days=30)

            if signal:
                print(f"  信号: {signal.action}")
                print(f"  信心: {signal.confidence*100:.0f}%")

                # 添加到数据库
                self.db.add_signal(
                    date=date,
                    symbol=stock['symbol'],
                    signal_type='new_model',
                    action=signal.action,
                    price=signal.price,
                    confidence=signal.confidence,
                    rsi=None,  # 新模型不使用RSI
                    kdj_k=None,  # 新模型不使用KDJ
                    kdj_d=None,
                    macd_hist=None,
                    volume_ratio=None,
                    position_pct=None,
                    short_trend=None,
                    mid_trend=None,
                    reasons="; ".join(signal.reasons)
                )

                # 如果信号足够强，记录
                if signal.confidence >= 0.5:
                    results[stock['symbol']] = {
                        'name': stock['name'],
                        'action': signal.action,
                        'price': signal.price,
                        'stop_loss': signal.stop_loss,
                        'take_profit': signal.take_profit,
                        'confidence': signal.confidence,
                        'reasons': signal.reasons,
                        'category': stock['category']
                    }
            else:
                print(f"  无有效信号")

            # 避免请求过快
            time_module.sleep(1)

        # 添加每日汇总
        if results:
            self.db.add_daily_summary(date)

        return {
            'batch_start': start,
            'batch_size': batch_size,
            'total_stocks': len(batch),
            'valid_signals': len(results),
            'signals': results
        }

    def test_all(self, batch_size: int = 10, stop_at: int = None) -> dict:
        """
        测试所有股票

        Args:
            batch_size: 批次大小
            stop_at: 停止批次号（None表示全部）

        Returns:
            所有测试结果
        """
        print("\n" + "="*80)
        print("🚀 开始测试所有股票")
        print("="*80)

        active_stocks = self.pool.get_active_stocks()
        total_batches = (len(active_stocks) + batch_size - 1) // batch_size

        if stop_at:
            total_batches = min(total_batches, stop_at)

        print(f"  总股票数: {len(active_stocks)}")
        print(f"  批次大小: {batch_size}")
        print(f"  总批次: {total_batches}")
        if stop_at:
            print(f"  停止批次: {stop_at}")
        print("="*80)

        all_results = {}
        batch_num = 0

        for start in range(0, min(len(active_stocks), stop_at * batch_size if stop_at else len(active_stocks)), batch_size):
            batch_num += 1
            print(f"\n批次 {batch_num}/{total_batches}")

            results = self.test_batch(batch_size, start)

            if results['valid_signals'] > 0:
                all_results.update(results['signals'])

            # 每批完成后汇报
            print(f"\n{'='*80}")
            print(f"✅ 批次 {batch_num} 完成！")
            print(f"  测试股票: {results['total_stocks']}")
            print(f"  有效信号: {results['valid_signals']}")
            print(f"{'='*80}")

            # 获取有效信号详情
            if results['valid_signals'] > 0:
                buy_signals = [s for s in results['signals'].values() if s['action'] == "买入"]
                sell_signals = [s for s in results['signals'].values() if s['action'] in ["卖出", "卖出/减仓"]]

                print(f"\n🟢 买入信号: {len(buy_signals)}")
                for signal in buy_signals:
                    print(f"  {signal['symbol']} ({signal['name']}): "
                          f"¥{signal['price']:.2f} (信心{signal['confidence']*100:.0f}%)")

                if sell_signals:
                    print(f"\n🔴 卖出信号: {len(sell_signals)}")
                    for signal in sell_signals:
                        print(f"  {signal['symbol']} ({signal['name']}): "
                              f"¥{signal['price']:.2f} (信心{signal['confidence']*100:.0f}%)")

        print("\n" + "="*80)
        print("✅ 全部测试完成！")
        print("="*80)

        # 统计
        buy_signals = sum(1 for r in all_results.values() if r['action'] == "买入")
        sell_signals = sum(1 for r in all_results.values() if r['action'] in ["卖出", "卖出/减仓"])

        print(f"  测试股票: {len(active_stocks)}")
        print(f"  买入信号: {buy_signals}")
        print(f"  卖出信号: {sell_signals}")
        print(f"  总信号: {len(all_results)}")
        print("="*80)

        return all_results

    def format_batch_results(self, results: dict) -> str:
        """格式化批次结果"""
        if not results or results.get('valid_signals', 0) == 0:
            return "无有效信号"

        buy_signals = [r for r in results['signals'].values() if r['action'] == "买入"]
        sell_signals = [r for r in results['signals'].values() if r['action'] in ["卖出", "卖出/减仓"]]

        output = f"""
📊 批次测试结果
{'='*80}
买入信号: {len(buy_signals)}
卖出信号: {len(sell_signals)}
{'='*80}
"""

        if buy_signals:
            output += "\n🟢 买入信号:\n"
            for signal in buy_signals:
                output += f"  {signal['symbol']} ({signal['name']}): "
                output += f"¥{signal['price']:.2f} (信心{signal['confidence']*100:.0f}%)\n"
                if signal['stop_loss']:
                    output += f"    止损: ¥{signal['stop_loss']:.2f} | "
                    output += f"止盈: ¥{signal['take_profit']:.2f}\n"
                if signal['reasons']:
                    output += f"    原因: {'; '.join(signal['reasons'][:2])}\n"

        if sell_signals:
            output += "\n🔴 卖出信号:\n"
            for signal in sell_signals:
                output += f"  {signal['symbol']} ({signal['name']}): "
                output += f"¥{signal['price']:.2f} (信心{signal['confidence']*100:.0f}%)\n"
                if signal['reasons']:
                    output += f"    原因: {'; '.join(signal['reasons'][:2])}\n"

        output += f"{'='*80}\n"

        return output

def run_daily_batch_test():
    """运行每日批量测试（PostgreSQL）"""
    print("🧪 每日批量测试系统（PostgreSQL）\n")

    # 初始化系统
    pool = StockPool()
    model = NewAnalysisModel()
    db = PostgresStockDatabase()
    batch_test = BatchTestSystemPostgres(pool, model, db)

    # 测试第一批（10只）
    results = batch_test.test_batch(batch_size=10, start=0)

    # 显示结果
    print(batch_test.format_batch_results(results))

    # 显示数据库摘要
    print(db.format_summary())

if __name__ == "__main__":
    run_daily_batch_test()
