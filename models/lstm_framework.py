#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LSTM深度学习预测模型（框架版）
"""

import sys
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import statistics


class LSTMStockPredictor:
    """LSTM股票预测器（框架版）"""

    def __init__(self, use_real_model: bool = False):
        self.use_real_model = use_real_model
        print(f"✅ LSTM预测器初始化完成 (真实模型: {use_real_model})")

    def predict_with_lstm(self, history: List[Dict], predict_days: int = 5) -> List[Dict]:
        """
        使用LSTM预测未来走势

        Args:
            history: 历史数据
            predict_days: 预测天数

        Returns:
            预测结果
        """
        if self.use_real_model:
            print(f"  ⚠️  真实LSTM模型未实现，使用模拟算法")
        else:
            print(f"  🤖 使用模拟LSTM算法")

        if len(history) < 10:
            return []

        # 提取价格序列
        prices = [c['close'] for c in history]

        # 计算多种特征
        # 1. 短期趋势（5天）
        short_trend = (prices[-1] - prices[-6]) / prices[-6] if len(prices) > 6 else 0

        # 2. 中期趋势（20天）
        mid_trend = (prices[-1] - prices[-21]) / prices[-21] if len(prices) > 21 else 0

        # 3. 移动平均（5日、10日、20日）
        ma5 = statistics.mean(prices[-5:])
        ma10 = statistics.mean(prices[-10:])
        ma20 = statistics.mean(prices[-20:])

        # 4. 波动率（10天）
        volatility = statistics.stdev(prices[-10:]) if len(prices) >= 10 else 0

        # 5. RSI
        gains = []
        losses = []
        for i in range(len(prices) - 13, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
            else:
                losses.append(abs(change))

        if gains and losses:
            avg_gain = sum(gains) / len(gains)
            avg_loss = sum(losses) / len(losses)
            rsi = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss > 0 else 50
        else:
            rsi = 50

        # LSTM模拟预测（加权特征预测）
        predictions = []
        base_price = prices[-1]

        for i in range(predict_days):
            # 特征权重
            trend_weight = 0.35
            ma_weight = 0.30
            volatility_weight = 0.20
            rsi_weight = 0.15

            # 计算趋势影响（更远的预测，趋势影响递减）
            trend_factor = 1.0 - (i * 0.04)  # 趋势权重递减
            
            if short_trend > 0.02 and mid_trend > 0.02:
                trend_change = short_trend * (1 + i * 0.01) * trend_factor
            elif short_trend < -0.02 and mid_trend < -0.02:
                trend_change = short_trend * (1 + i * 0.01) * trend_factor
            else:
                # 横盘时，随机选择方向
                trend_change = random.uniform(-0.005, 0.005) * (1 - i * 0.05)

            # 计算MA回归影响
            # 价格有回归到MA的趋势
            ma_diff = base_price - ma5
            ma_change = -ma_diff * 0.05 * (1 - i * 0.02)  # 越势回归到均值

            # 计算波动率影响（高斯分布模拟随机性）
            vol_change = random.gauss(0, volatility) if volatility > 0 else 0

            # 计算RSI调整（超买回调，超卖反弹）
            if rsi > 70:
                rsi_change = -0.01 * i * (rsi - 70) / 30  # 超买，涨幅减小
            elif rsi < 30:
                rsi_change = 0.01 * i * (30 - rsi) / 30    # 超卖，涨幅增大
            else:
                rsi_change = 0

            # 综合变化
            total_change = (
                trend_change * trend_weight +
                ma_change * ma_weight +
                vol_change * volatility_weight +
                rsi_change * rsi_weight
            )

            # 预测价格
            pred_price = base_price * (1 + total_change)

            # 判断方向
            if total_change > 0.005:
                direction = "上涨"
            elif total_change < -0.005:
                direction = "下跌"
            else:
                direction = "横盘"

            predictions.append({
                'day': i + 1,
                'predicted_price': round(pred_price, 2),
                'change_percent': round(total_change * 100, 2),
                'direction': direction,
                'features': {
                    'short_trend': round(short_trend * 100, 2),
                    'mid_trend': round(mid_trend * 100, 2),
                    'ma5': round(ma5, 2),
                    'ma10': round(ma10, 2),
                    'ma20': round(ma20, 2),
                    'volatility': round(volatility * 100, 2),
                    'rsi': round(rsi, 2)
                }
            })

            base_price = pred_price

        return predictions

    def calculate_confidence(self, history: List[Dict], predictions: List[Dict]) -> float:
        """
        计算预测信心度

        Args:
            history: 历史数据
            predictions: 预测结果

        Returns:
            信心度 0-1
        """
        if not predictions:
            return 0.5

        # 基于历史波动率计算信心度
        prices = [c['close'] for c in history]
        if len(prices) < 10:
            return 0.5

        # 计算最近10天的波动率
        volatility = statistics.stdev(prices[-10:]) if len(prices) >= 10 else 0

        # 波动率越低，信心度越高
        # 基础信心度 65%
        base_confidence = 0.65

        if volatility < 0.01:
            confidence = base_confidence + 0.25
        elif volatility < 0.02:
            confidence = base_confidence + 0.15
        elif volatility < 0.03:
            confidence = base_confidence + 0.10
        elif volatility < 0.05:
            confidence = base_confidence
        else:
            confidence = base_confidence - 0.10

        # 趋势一致性调整
        # 检查预测的一致性
        if len(predictions) >= 2:
            direction_changes = 0
            for i in range(1, len(predictions)):
                if predictions[i]['direction'] != predictions[i-1]['direction']:
                    direction_changes += 1

            # 方向越一致，信心度越高
            if direction_changes == 0:
                confidence += 0.15
            elif direction_changes == 1:
                confidence += 0.05
            else:
                confidence -= 0.05

        return max(0.3, min(0.95, confidence))


def test_lstm_predictor():
    """测试LSTM预测器"""
    print("="*80)
    print("🧪 测试LSTM预测系统")
    print("="*80)

    # 生成测试数据
    print("\n[1/3] 生成测试数据...")
    history = []
    base_price = 100.0
    for i in range(60):
        date = (datetime.now() - timedelta(days=60-i-1)).strftime('%Y-%m-%d')

        price_change = base_price * random.uniform(0.0005, 0.002)
        open_price = base_price * (1 + random.uniform(-0.01, 0.01))
        close_price = open_price + price_change
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.005))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.005))
        volume = random.randint(1000000, 10000000)

        history.append({
            'date': date,
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume,
            'amount': round(volume * close_price, 2)
        })

        base_price = close_price

    # 测试模拟LSTM
    print("[2/3] 测试模拟LSTM预测...")
    predictor = LSTMStockPredictor(use_real_model=False)
    predictions = predictor.predict_with_lstm(history, predict_days=5)
    confidence = predictor.calculate_confidence(history, predictions)

    print(f"\n  预测天数: {len(predictions)}")
    print(f"  预测信心度: {confidence*100:.1f}%")

    # 输出预测结果
    print(f"\n  未来5天预测:")
    for pred in predictions:
        print(f"    第{pred['day']}天: ¥{pred['predicted_price']:.2f} ({pred['change_percent']:+.2f}%) {pred['direction']}")
        print(f"      特征: 趋势{pred['features']['short_trend']}%, MA5{pred['features']['ma5']:.2f}, RSI{pred['features']['rsi']:.0f}")

    # 测试真实数据接入（如果可能）
    print("\n[3/3] 测试真实数据接入...")
    try:
        # 尝试获取真实数据
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from dataflows.real_data_collector import RealDataCollector
        collector = RealDataCollector()
        real_history = collector.fetch_month_history("000063")

        if real_history:
            print(f"  ✅ 成功获取 {len(real_history)} 条真实数据")

            # 使用真实数据预测
            real_predictions = predictor.predict_with_lstm(real_history, predict_days=5)
            real_confidence = predictor.calculate_confidence(real_history, real_predictions)

            print(f"\n  真实数据预测结果:")
            print(f"  预测天数: {len(real_predictions)}")
            print(f"  预测信心度: {real_confidence*100:.1f}%")

            for pred in real_predictions[:3]:
                print(f"    第{pred['day']}天: ¥{pred['predicted_price']:.2f} ({pred['change_percent']:+.2f}%) {pred['direction']}")
        else:
            print("  ❌ 无法获取真实数据")
    except Exception as e:
        print(f"  ❌ 真实数据接入失败: {e}")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_lstm_predictor()
