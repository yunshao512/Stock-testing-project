#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量测试系统 v1.0
批量测试股票池中的股票，使用新模型
"""

import sys
import os
sys.path.append('/home/parallels/.openclaw/workspace/skills/a-stock-fetcher/scripts')
from stock_pool import StockPool
from new_analysis_model import NewAnalysisModel
from trading_system import TradingSystem
import json
from datetime import datetime
import time as time_module

class BatchTestSystem:
    """批量测试系统"""

    def __init__(self, pool: StockPool, model: NewAnalysisModel,
                 trading_system: TradingSystem,
                 results_file: str = "/tmp/a_stock_batch_test_results.json"):
        """
        初始化批量测试系统

        Args:
            pool: 股票池
            model: 分析模型
            trading_system: 交易系统
            results_file: 结果文件
        """
        self.pool = pool
        self.model = model
        self.trading_system = trading_system
        self.results_file = results_file

        # 加载历史结果
        self.test_results = self._load_results()

    def _load_results(self) -> dict:
        """加载测试结果"""
        if not os.path.exists(self.results_file):
            return {}

        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载测试结果失败: {e}")
            return {}

    def _save_results(self):
        """保存测试结果"""
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存测试结果失败: {e}")

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
            print("❌ 没有股票可测试")
            return {}

        print(f"\n📊 开始测试批次 {start+1}-{start+len(batch)} ({len(batch)}只股票)\n")
        print("="*80)

        results = {}

        for i, stock in enumerate(batch):
            print(f"\n[{i+1}/{len(batch)}] {stock['name']} ({stock['symbol']})")

            # 使用新模型分析
            signal = self.model.analyze(stock['symbol'], days=30)

            if signal:
                print(f"  信号: {signal.action}")
                print(f"  信心: {signal.confidence*100:.0f}%")

                # 记录到股票池
                self.pool.add_signal(
                    stock['symbol'],
                    signal.action,
                    signal.confidence,
                    "; ".join(signal.reasons)
                )

                # 如果是买入信号且信心度够高，记录
                if signal.action == "买入" and signal.confidence >= 0.5:
                    results[stock['symbol']] = {
                        'name': stock['name'],
                        'action': signal.action,
                        'price': signal.price,
                        'stop_loss': signal.stop_loss,
                        'take_profit': signal.take_profit,
                        'confidence': signal.confidence,
                        'reasons': signal.reasons,
                        'category': stock['category'],
                        'test_date': datetime.now().isoformat()
                    }
                elif signal.action == "卖出/减仓" and signal.confidence >= 0.5:
                    results[stock['symbol']] = {
                        'name': stock['name'],
                        'action': signal.action,
                        'price': signal.price,
                        'confidence': signal.confidence,
                        'reasons': signal.reasons,
                        'category': stock['category'],
                        'test_date': datetime.now().isoformat()
                    }
            else:
                print(f"  无有效信号")

            # 避免请求过快
            time_module.sleep(1)

        # 保存结果
        date_key = datetime.now().strftime("%Y-%m-%d")
        if date_key not in self.test_results:
            self.test_results[date_key] = []

        self.test_results[date_key].append({
            'batch_start': start,
            'batch_size': batch_size,
            'signals': results,
            'total_stocks': len(batch),
            'valid_signals': len(results),
            'timestamp': datetime.now().isoformat()
        })

        self._save_results()

        print(f"\n{'='*80}")
        print(f"✅ 批次测试完成！")
        print(f"  测试股票: {len(batch)}")
        print(f"  有效信号: {len(results)}")

        if results:
            print(f"\n有效信号:\n")
            for symbol, data in results.items():
                print(f"  {symbol} ({data['name']}): {data['action']} (信心{data['confidence']*100:.0f}%)")
        else:
            print(f"\n无有效信号")

        return results

    def test_all(self, batch_size: int = 10) -> dict:
        """
        测试所有股票

        Args:
            batch_size: 批次大小

        Returns:
            所有测试结果
        """
        print("\n" + "="*80)
        print("🚀 开始测试所有股票")
        print("="*80)

        active_stocks = self.pool.get_active_stocks()
        total_batches = (len(active_stocks) + batch_size - 1) // batch_size

        print(f"  总股票数: {len(active_stocks)}")
        print(f"  批次大小: {batch_size}")
        print(f"  总批次: {total_batches}")
        print("="*80)

        all_results = {}
        batch_num = 0

        for start in range(0, len(active_stocks), batch_size):
            batch_num += 1
            print(f"\n批次 {batch_num}/{total_batches}")

            results = self.test_batch(batch_size, start)

            for symbol, data in results.items():
                all_results[symbol] = data

        print("\n" + "="*80)
        print("✅ 全部测试完成！")
        print("="*80)

        # 统计
        buy_signals = sum(1 for r in all_results.values() if r['action'] == "买入")
        sell_signals = sum(1 for r in all_results.values() if r['action'] == "卖出/减仓")

        print(f"  测试股票: {len(active_stocks)}")
        print(f"  买入信号: {buy_signals}")
        print(f"  卖出信号: {sell_signals}")
        print(f"  总信号: {len(all_results)}")
        print("="*80)

        return all_results

    def format_batch_results(self, results: dict) -> str:
        """格式化批次结果"""
        if not results:
            return "无有效信号"

        output = f"""
📊 批次测试结果
{'='*80}
"""

        buy_signals = [r for r in results.values() if r['action'] == "买入"]
        sell_signals = [r for r in results.values() if r['action'] == "卖出/减仓"]

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

    def get_daily_summary(self, date: str = None) -> dict:
        """
        获取每日汇总

        Args:
            date: 日期 (YYYY-MM-DD)，默认今天

        Returns:
            每日汇总
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        if date not in self.test_results:
            return {}

        day_data = self.test_results[date]

        summary = {
            'date': date,
            'total_batches': len(day_data),
            'total_stocks': sum(b['total_stocks'] for b in day_data),
            'total_signals': sum(len(b['signals']) for b in day_data),
            'buy_signals': sum(
                sum(1 for s in b['signals'].values() if s['action'] == "买入")
                for b in day_data
            ),
            'sell_signals': sum(
                sum(1 for s in b['signals'].values() if s['action'] == "卖出/减仓")
                for b in day_data
            )
        }

        return summary

def run_daily_batch_test():
    """运行每日批量测试"""
    print("🧪 每日批量测试系统\n")

    # 初始化系统
    pool = StockPool()
    model = NewAnalysisModel()
    trading_system = TradingSystem()
    batch_test = BatchTestSystem(pool, model, trading_system)

    # 测试第一批（10只）
    results = batch_test.test_batch(batch_size=10, start=0)

    # 显示结果
    print(batch_test.format_batch_results(results))

    # 保存每日汇总
    summary = batch_test.get_daily_summary()
    print(f"\n📊 每日汇总:")
    print(f"  测试股票: {summary['total_stocks']}")
    print(f"  总信号: {summary['total_signals']}")
    print(f"  买入信号: {summary['buy_signals']}")
    print(f"  卖出信号: {summary['sell_signals']}")

if __name__ == "__main__":
    run_daily_batch_test()
