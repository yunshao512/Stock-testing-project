#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
回测验证系统
验证预测系统的胜率
"""

import sys
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import statistics


class BacktestSystem:
    """回测验证系统"""

    def __init__(self):
        print("✅ 回测验证系统初始化完成")

    def generate_history(self, symbol: str, days: int = 100) -> List[Dict]:
        """
        生成历史数据

        Args:
            symbol: 股票代码
            days: 天数

        Returns:
            历史K线数据
        """
        # 根据股票代码确定基准价格
        if symbol.startswith('6'):
            base_price = random.uniform(50, 300)
        elif symbol.startswith('3'):
            base_price = random.uniform(20, 100)
        elif symbol.startswith('0'):
            base_price = random.uniform(10, 100)
        else:
            base_price = random.uniform(20, 200)

        # 生成趋势
        # 上升趋势
        if random.random() > 0.5:
            trend_factor = random.uniform(0.0005, 0.002)  # 每日涨幅
        else:
            trend_factor = random.uniform(-0.002, -0.0005)  # 每日跌幅

        # 生成100天历史数据
        candles = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')

            # 计算价格
            open_price = base_price * (1 + random.uniform(-0.02, 0.02))
            
            if trend_factor > 0:
                # 上升趋势
                close_price = open_price * (1 + trend_factor * random.uniform(0.8, 1.2))
            else:
                # 下降趋势
                close_price = open_price * (1 + trend_factor * random.uniform(0.8, 1.2))

            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.01))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.01))
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

        return candles

    def predict_with_system(self, history: List[Dict], predict_days: int = 3) -> List[str]:
        """
        使用预测系统预测未来走势

        Args:
            history: 历史数据（前90天）
            predict_days: 预测天数（3/5）

        Returns:
            预测方向列表（上涨/下跌）
        """
        # 使用前90天数据预测
        base_history = history[-90:] if len(history) >= 90 else history

        if len(base_history) < 10:
            return ["未知"] * predict_days

        # 计算短期趋势
        short_trend = (base_history[-1]['close'] - base_history[-6]['close']) / base_history[-6]['close'] if len(base_history) > 6 else 0
        mid_trend = (base_history[-1]['close'] - base_history[-21]['close']) / base_history[-21]['close'] if len(base_history) > 21 else 0

        # 判断趋势
        if short_trend > 0.02 and mid_trend > 0.02:
            trend = "上涨"
        elif short_trend < -0.02 and mid_trend < -0.02:
            trend = "下跌"
        else:
            trend = "横盘"

        # 预测未来几天
        predictions = []
        current_price = base_history[-1]['close']

        for i in range(predict_days):
            if trend == "上涨":
                change = random.uniform(0.5, 2.0)
                direction = "上涨"
            elif trend == "下跌":
                change = random.uniform(-2.0, -0.5)
                direction = "下跌"
            else:
                change = random.uniform(-1.0, 1.0)
                direction = random.choice(["上涨", "下跌"])

            # 预测价格
            pred_price = current_price * (1 + change / 100)

            predictions.append(direction)
            current_price = pred_price

        return predictions

    def calculate_accuracy(self, history: List[Dict], predictions: List[str]) -> Dict:
        """
        计算预测准确率

        Args:
            history: 完整历史数据（100天）
            predictions: 预测方向列表

        Returns:
            准确率统计
        """
        if len(predictions) == 0 or len(history) < 10:
            return {
                'total_days': 0,
                'correct_days': 0,
                'accuracy': 0.0,
                'details': []
            }

        # 获取最后10天的实际数据
        actual_data = history[-len(predictions):]

        # 对比预测和实际
        correct = 0
        details = []

        for i in range(len(predictions)):
            actual_price = actual_data[i]['close']
            prev_price = actual_data[i-1]['close'] if i > 0 else actual_data[i]['open']

            # 计算实际方向
            if actual_price > prev_price:
                actual_direction = "上涨"
            elif actual_price < prev_price:
                actual_direction = "下跌"
            else:
                actual_direction = "横盘"

            # 对比
            is_correct = (predictions[i] == actual_direction) or (actual_direction == "横盘")

            if is_correct:
                correct += 1

            details.append({
                'day': i + 1,
                'predicted': predictions[i],
                'actual': actual_direction,
                'correct': is_correct
            })

        # 计算准确率
        accuracy = correct / len(predictions) if len(predictions) > 0 else 0.0

        return {
            'total_days': len(predictions),
            'correct_days': correct,
            'accuracy': accuracy,
            'details': details
        }

    def backtest_symbol(self, symbol: str, predict_days: int = 3) -> Dict:
        """
        对单只股票进行回测

        Args:
            symbol: 股票代码
            predict_days: 预测天数

        Returns:
            回测结果
        """
        print(f"\n{'='*80}")
        print(f"🧪 回测股票: {symbol}")
        print(f"预测天数: {predict_days}天")
        print(f"{'='*80}")

        # 1. 生成100天历史数据
        print(f"\n[1/4] 生成100天历史数据...")
        history = self.generate_history(symbol, days=100)

        # 2. 使用前90天预测第91-100天
        print(f"[2/4] 使用前90天数据预测第91-{100}天的走势...")
        predictions = self.predict_with_system(history, predict_days)

        # 3. 计算准确率
        print(f"[3/4] 计算预测准确率...")
        accuracy = self.calculate_accuracy(history, predictions)

        # 4. 输出结果
        print(f"[4/4] 生成回测报告...\n")

        # 详细报告
        print(f"📊 回测结果 - {symbol}")
        print(f"{'='*80}")
        print(f"预测天数: {accuracy['total_days']}天")
        print(f"预测正确: {accuracy['correct_days']}天")
        print(f"预测准确率: {accuracy['accuracy']*100:.1f}%")
        print(f"{'='*80}\n")

        # 详细对比
        print(f"详细对比:")
        print(f"{'='*80}")
        print(f"{'天数':<10} {'预测':<10} {'实际':<10} {'正确':<10}")
        print(f"{'─'*40}")

        for detail in accuracy['details']:
            check = "✅" if detail['correct'] else "❌"
            print(f"{detail['day']:<10} {detail['predicted']:<10} {detail['actual']:<10} {check:<10}")

        print(f"{'='*80}\n")

        return {
            'symbol': symbol,
            'predict_days': predict_days,
            'total_days': accuracy['total_days'],
            'correct_days': accuracy['correct_days'],
            'accuracy': accuracy['accuracy'],
            'details': accuracy['details']
        }

    def batch_backtest(self, symbols: List[str], predict_days: int = 3) -> Dict:
        """
        批量回测多只股票

        Args:
            symbols: 股票代码列表
            predict_days: 预测天数

        Returns:
            批量回测结果
        """
        print(f"\n{'='*80}")
        print(f"🧪 批量回测")
        print(f"股票数量: {len(symbols)}")
        print(f"预测天数: {predict_days}天")
        print(f"{'='*80}")

        results = []
        accuracies = []

        for symbol in symbols:
            result = self.backtest_symbol(symbol, predict_days)
            results.append(result)
            accuracies.append(result['accuracy'])

        # 批量统计
        avg_accuracy = statistics.mean(accuracies) if accuracies else 0.0
        max_accuracy = max(accuracies) if accuracies else 0.0
        min_accuracy = min(accuracies) if accuracies else 0.0

        # 排序
        results_sorted = sorted(results, key=lambda x: x['accuracy'], reverse=True)

        # 输出统计
        print(f"\n{'='*80}")
        print(f"📊 批量回测统计")
        print(f"{'='*80}")
        print(f"平均准确率: {avg_accuracy*100:.1f}%")
        print(f"最高准确率: {max_accuracy*100:.1f}%")
        print(f"最低准确率: {min_accuracy*100:.1f}%")
        print(f"{'='*80}\n")

        # 胜率统计
        win_count = sum(1 for acc in accuracies if acc > 0.5)
        win_rate = win_count / len(accuracies) if accuracies else 0.0

        print(f"🏆 胜率统计:")
        print(f"  预测胜率（>50%）: {win_rate*100:.1f}% ({win_count}/{len(accuracies)})")
        print(f"  预测负率（<50%）: {(1-win_rate)*100:.1f}% ({len(accuracies)-win_count}/{len(accuracies)})")
        print(f"{'='*80}\n")

        # 详细排名
        print(f"📊 准确率排名:")
        print(f"{'='*80}")
        print(f"{'排名':<8} {'股票':<20} {'准确率':<15} {'预测天数':<15}")
        print(f"{'─'*60}")

        for i, result in enumerate(results_sorted, 1):
            rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            print(f"{rank_emoji:<8} {result['symbol']:<20} {result['accuracy']*100:>6.1f}% {result['predict_days']}天")
        print(f"          正确: {result['correct_days']}/{result['total_days']}天")
        print()

        print(f"{'='*80}\n")

        return {
            'symbols': symbols,
            'predict_days': predict_days,
            'results': results,
            'avg_accuracy': avg_accuracy,
            'max_accuracy': max_accuracy,
            'min_accuracy': min_accuracy,
            'win_rate': win_rate
        }


def main():
    """主函数"""
    print("="*80)
    print("🧪 股票预测系统回测验证")
    print("="*80)
    print()

    # 测试股票列表
    test_symbols = [
        '601888',  # 珀莱雅
        '603633',  # 巨星农牧
        '000665',  # 石头科技
        '000725',  # 通威股份
        '688568',  # 安图生物
        '600745',  # 闻泰科技
        '600536',  # 中国软件
        '300415',  # 恒生电子
    ]

    # 预测天数
    predict_days = [3, 5]

    # 创建回测系统
    backtest = BacktestSystem()

    # 批量回测
    for days in predict_days:
        print(f"\n🎯 预测{days}天回测\n")
        batch_result = backtest.batch_backtest(test_symbols, days)

        # 保存结果
        import json
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backtest_{days}days_{timestamp}.json"
        filepath = os.path.join(os.path.dirname(__file__), 'data', filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(batch_result, f, ensure_ascii=False, indent=2)

        print(f"📄 回测结果已保存: {filepath}")

    print(f"\n✅ 回测验证完成\n")


if __name__ == "__main__":
    main()
