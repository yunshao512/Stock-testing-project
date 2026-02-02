#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速回测统计
只输出最终的胜率统计
"""

import sys
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict
import statistics


# 测试股票
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


def generate_history(symbol: str, days: int = 100) -> List[Dict]:
    """生成历史数据"""
    if '60' in symbol:
        base_price = random.uniform(10, 30)
    elif '000' in symbol:
        base_price = random.uniform(10, 30)
    elif '688' in symbol or '300' in symbol:
        base_price = random.uniform(20, 50)
    else:
        base_price = random.uniform(20, 40)

    candles = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
        
        price_change = base_price * random.uniform(0.0005, 0.002)
        open_price = base_price * (1 + random.uniform(-0.01, 0.01))
        close_price = open_price + price_change
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.005))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.005))
        volume = random.randint(1000000, 50000000)

        candles.append({
            'date': date,
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume
        })

        base_price = close_price

    return candles


def predict_direction(history: List[Dict], predict_days: int = 3) -> List[str]:
    """预测方向"""
    base_history = history[-80:] if len(history) >= 80 else history
    
    if len(base_history) < 10:
        return ["未知"] * predict_days

    short_trend = (base_history[-1]['close'] - base_history[-6]['close']) / base_history[-6]['close']
    mid_trend = (base_history[-1]['close'] - base_history[-21]['close']) / base_history[-21]['close']

    if short_trend > 0.02 and mid_trend > 0.02:
        trend = "上涨"
    elif short_trend < -0.02 and mid_trend < -0.02:
        trend = "下跌"
    else:
        trend = "横盘"

    predictions = []
    for i in range(predict_days):
        if trend == "上涨":
            direction = "上涨"
        elif trend == "下跌":
            direction = "下跌"
        else:
            direction = random.choice(["上涨", "下跌"])

        predictions.append(direction)

    return predictions


def calculate_win_rate(history: List[Dict], predictions: List[str]) -> Dict:
    """计算胜率"""
    if len(predictions) == 0:
        return {'win_rate': 0.0, 'accuracy': 0.0}

    actual_data = history[-len(predictions):]

    actual_directions = []
    for i in range(len(actual_data)):
        if i == 0:
            prev_close = actual_data[i-1]['close']
        else:
            prev_close = actual_data[i-1]['close']

        if actual_data[i]['close'] > prev_close:
            actual_directions.append("上涨")
        elif actual_data[i]['close'] < prev_close:
            actual_directions.append("下跌")
        else:
            actual_directions.append("横盘")

    correct = sum(1 for p, a in zip(predictions, actual_directions) if p == a)
    win_rate = correct / len(predictions)

    return {
        'total_days': len(predictions),
        'correct_days': correct,
        'win_rate': win_rate
    }


def main():
    """主函数"""
    print("="*80)
    print("📊 股票预测胜率回测")
    print("="*80)
    print()

    predict_days_list = [3, 5]

    for predict_days in predict_days_list:
        print(f"\n{'='*80}")
        print(f"🎯 {predict_days}天预测胜率")
        print(f"{'='*80}\n")

        results = []

        for symbol in test_symbols:
            # 生成历史
            history = generate_history(symbol, days=100)

            # 预测
            predictions = predict_direction(history, predict_days)

            # 计算胜率
            result = calculate_win_rate(history, predictions)
            result['symbol'] = symbol
            result['predict_days'] = predict_days

            results.append(result)

        # 统计
        win_rates = [r['win_rate'] for r in results]
        avg_win_rate = statistics.mean(win_rates)
        max_win_rate = max(win_rates)
        min_win_rate = min(win_rates)

        # 排序
        sorted_results = sorted(results, key=lambda x: x['win_rate'], reverse=True)

        # 输出统计
        print(f"平均胜率: {avg_win_rate*100:.1f}%")
        print(f"最高胜率: {max_win_rate*100:.1f}%")
        print(f"最低胜率: {min_win_rate*100:.1f}%")

        win_count = sum(1 for wr in win_rates if wr > 0.5)
        print(f"胜率>50%: {win_count}/{len(results)} ({win_count/len(results)*100:.1f}%)")

        print(f"\n胜率排名:")
        print(f"{'='*80}")
        print(f"{'排名':<6} {'股票代码':<12} {'胜率':<10} {'准确':<8}/{predict_days}天")
        print(f"{'-'*60}")

        for i, result in enumerate(sorted_results, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            print(f"{emoji:<6} {result['symbol']:<12} {result['win_rate']*100:>6.1f}% {result['correct_days']:>3}/{predict_days}")

    print(f"\n{'='*80}")
    print("✅ 回测完成")
    print(f"{'='*80}\n")

    # 保存结果
    final_results = {
        'symbols': test_symbols,
        'predict_days_list': predict_days_list,
        'results_3days': [r for r in results if r['predict_days'] == 3],
        'results_5days': [r for r in results if r['predict_days'] == 5],
        'avg_win_rate_3days': statistics.mean([r['win_rate'] for r in results if r['predict_days'] == 3]),
        'avg_win_rate_5days': statistics.mean([r['win_rate'] for r in results if r['predict_days'] == 5])
    }

    import json
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backtest_summary_{timestamp}.json"
    filepath = os.path.join(os.path.dirname(__file__), '..', 'data', filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)

    print(f"📄 回测结果已保存: {filepath}")


if __name__ == "__main__":
    main()
