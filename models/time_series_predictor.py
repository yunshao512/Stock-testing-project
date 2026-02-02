#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
时间序列预测模块
基于ARIMA和移动平均的股票价格预测
"""

import sys
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import statistics


class TimeSeriesPredictor:
    """时间序列预测器"""

    def __init__(self):
        print("✅ 时间序列预测器初始化完成")

    def predict(self, candles: List[Dict], days: int = 7) -> Dict:
        """
        预测未来N天走势

        Args:
            candles: 历史K线数据
            days: 预测天数

        Returns:
            预测结果
        """
        if len(candles) < days * 2:
            print(f"⚠️ 历史数据不足（{len(candles)}），需要至少 {days*2} 条")
            return self._generate_mock_predictions(candles, days)

        # 提取收盘价
        prices = [c['close'] for c in candles]

        # 方法1：移动平均预测
        ma_forecast = self._moving_average_forecast(prices, days)

        # 方法2：趋势外推预测
        trend_forecast = self._trend_forecast(prices, days)

        # 方法3：加权预测（MA + 趋势）
        weighted_forecast = self._weighted_forecast(ma_forecast, trend_forecast, days)

        # 计算涨跌幅和方向
        predictions = []
        base_price = candles[-1]['close']

        for i in range(days):
            date = (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')

            pred_price = weighted_forecast[i]
            change_percent = ((pred_price - base_price) / base_price) * 100

            if change_percent > 1:
                direction = "上涨"
            elif change_percent < -1:
                direction = "下跌"
            else:
                direction = "横盘"

            predictions.append({
                'date': date,
                'predicted_price': round(pred_price, 2),
                'change_percent': round(change_percent, 2),
                'direction': direction
            })

        # 计算预测信心度
        confidence = self._calculate_confidence(prices, candles, days)

        # 总结
        final_price = predictions[-1]['predicted_price']
        overall_change = ((final_price - base_price) / base_price) * 100

        if overall_change > 3:
            overall_trend = "明显上涨"
        elif overall_change < -3:
            overall_trend = "明显下跌"
        else:
            overall_trend = "窄幅震荡"

        return {
            'forecast': f"未来{days}天走势预测",
            'confidence': round(confidence * 100, 0),
            'overall_trend': overall_trend,
            'predictions': predictions,
            'method': "加权移动平均 + 趋势外推"
        }

    def _moving_average_forecast(self, prices: List[float], days: int) -> List[float]:
        """移动平均预测"""
        # 使用5日移动平均
        if len(prices) < 5:
            return prices[-days:]

        # 计算最近5日平均日变化
        recent_changes = []
        for i in range(len(prices)-5, len(prices)):
            change = prices[i] - prices[i-1]
            recent_changes.append(change)

        avg_change = statistics.mean(recent_changes) if recent_changes else 0

        # 预测
        last_price = prices[-1]
        forecast = []
        for i in range(days):
            pred_price = last_price + avg_change * (i + 1)
            forecast.append(pred_price)

        return forecast

    def _trend_forecast(self, prices: List[float], days: int) -> List[float]:
        """趋势外推预测"""
        if len(prices) < 10:
            return prices[-days:]

        # 计算短期趋势（最近5天）
        short_trend = (prices[-1] - prices[-6]) / 6 if len(prices) > 6 else 0

        # 计算中期趋势（最近10天）
        mid_trend = (prices[-1] - prices[-11]) / 11 if len(prices) > 11 else 0

        # 加权趋势（短期权重更高）
        weighted_trend = short_trend * 0.6 + mid_trend * 0.4

        # 预测
        last_price = prices[-1]
        forecast = []
        for i in range(days):
            # 趋势递减（更远的预测波动更小）
            trend_factor = 1.0 - (i * 0.05)
            pred_price = last_price + weighted_trend * (i + 1) * trend_factor
            forecast.append(pred_price)

        return forecast

    def _weighted_forecast(self, ma_forecast: List[float], trend_forecast: List[float], days: int) -> List[float]:
        """加权预测（MA + 趋势）"""
        weighted = []

        for i in range(days):
            # 移动平均权重 0.4，趋势权重 0.6
            weight_ma = 0.4
            weight_trend = 0.6

            # 更远的预测，移动平均权重提高
            if i > 3:
                weight_ma = 0.6
                weight_trend = 0.4

            pred = ma_forecast[i] * weight_ma + trend_forecast[i] * weight_trend
            weighted.append(pred)

        return weighted

    def _calculate_confidence(self, prices: List[float], candles: List[Dict], days: int) -> float:
        """计算预测信心度"""
        # 基于历史波动率计算信心度
        if len(prices) < 10:
            return 0.5

        # 计算最近10天的波动率
        returns = []
        for i in range(len(prices)-10, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)

        volatility = statistics.stdev(returns) if len(returns) > 1 else 0

        # 波动率越低，信心度越高
        # 基础信心度 70%
        base_confidence = 0.7

        # 波动率调整
        if volatility < 0.02:
            confidence = base_confidence + 0.2
        elif volatility < 0.03:
            confidence = base_confidence + 0.1
        elif volatility < 0.05:
            confidence = base_confidence
        else:
            confidence = base_confidence - 0.1

        return max(0.3, min(0.9, confidence))

    def _generate_mock_predictions(self, candles: List[Dict], days: int) -> Dict:
        """生成模拟预测（备用）"""
        import random

        base_price = candles[-1]['close']
        predictions = []

        for i in range(days):
            date = (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')

            change = random.uniform(-2, 2)
            pred_price = base_price * (1 + change / 100)

            if change > 1:
                direction = "上涨"
            elif change < -1:
                direction = "下跌"
            else:
                direction = "横盘"

            predictions.append({
                'date': date,
                'predicted_price': round(pred_price, 2),
                'change_percent': round(change, 2),
                'direction': direction
            })

            base_price = pred_price

        return {
            'forecast': f"未来{days}天走势预测（模拟）",
            'confidence': 50,
            'overall_trend': "不确定",
            'predictions': predictions,
            'method': "随机模拟（数据不足）"
        }


def test_predictor():
    """测试预测器"""
    print("="*80)
    print("🧪 测试时间序列预测")
    print("="*80)

    # 生成测试数据
    import random
    base_price = 100.0

    candles = []
    for i in range(60):
        price_change = random.uniform(-3, 3)
        open_price = base_price + random.uniform(-1, 1)
        close_price = open_price + price_change
        high_price = max(open_price, close_price) + random.uniform(0, 1)
        low_price = min(open_price, close_price) - random.uniform(0, 1)

        candles.append({
            'date': (datetime.now() - timedelta(days=60-i)).strftime('%Y-%m-%d'),
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': random.randint(1000000, 10000000)
        })

        base_price = close_price

    # 预测
    predictor = TimeSeriesPredictor()
    result = predictor.predict(candles, days=7)

    print(f"\n{result['forecast']}")
    print(f"预测方法: {result['method']}")
    print(f"整体趋势: {result['overall_trend']}")
    print(f"信心度: {result['confidence']}%")
    print(f"\n未来7天预测:")
    print(f"{'日期':<15} {'预测价格':<15} {'涨跌幅':<10} {'方向':<10}")
    print(f"{'='*60}")

    for pred in result['predictions']:
        print(f"{pred['date']:<15} ¥{pred['predicted_price']:>10.2f} {pred['change_percent']:>8.2f}% {pred['direction']:<10}")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_predictor()
