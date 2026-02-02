#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
添加KDJ指标到indicators.py
KDJ指标又称随机指标，是一种相当常用的技术分析工具
"""

def calculate_kdj(prices: list, highs: list, lows: list, period: int = 9, m1: int = 3, m2: int = 3) -> dict:
    """
    计算KDJ指标

    Args:
        prices: 收盘价列表（从旧到新）
        highs: 最高价列表（从旧到新）
        lows: 最低价列表（从旧到新）
        period: 周期，默认9
        m1: K值平滑系数，默认3
        m2: D值平滑系数，默认3

    Returns:
        包含K、D、J值的字典
    """
    if len(prices) < period or len(highs) < period or len(lows) < period:
        return {'K': [None] * len(prices), 'D': [None] * len(prices), 'J': [None] * len(prices)}

    K = [None] * len(prices)
    D = [None] * len(prices)
    J = [None] * len(prices)

    # 计算RSV (Raw Stochastic Value)
    RSV = []
    for i in range(period - 1, len(prices)):
        high_period = max(highs[i-period+1:i+1])
        low_period = min(lows[i-period+1:i+1])

        if high_period == low_period:
            rsv = 50  # 避免除零错误
        else:
            rsv = ((prices[i] - low_period) / (high_period - low_period)) * 100

        RSV.append(rsv)

    # 前面period-1个值设为None
    for i in range(period - 1):
        K[i] = None
        D[i] = None
        J[i] = None

    # 计算K值（RSV的移动平均）
    # 第一个K值等于RSV
    K[period - 1] = RSV[0]

    for i in range(period, len(prices)):
        K[i] = ((m1 - 1) * K[i-1] + RSV[i-period+1]) / m1

    # 计算D值（K值的移动平均）
    D[period - 1] = K[period - 1]

    for i in range(period, len(prices)):
        D[i] = ((m2 - 1) * D[i-1] + K[i]) / m2

    # 计算J值
    for i in range(len(prices)):
        if K[i] is None or D[i] is None:
            J[i] = None
        else:
            J[i] = 3 * K[i] - 2 * D[i]

    return {
        'K': K,
        'D': D,
        'J': J
    }

def interpret_kdj(k: float, d: float, j: float) -> str:
    """
    解读KDJ信号

    Args:
        k: K值
        d: D值
        j: J值

    Returns:
        信号描述
    """
    if k is None or d is None or j is None:
        return "无数据"

    # 超买超卖判断
    if k > 80 and d > 80:
        return "⚠️ KDJ高位超买，注意风险"
    elif k < 20 and d < 20:
        return "✅ KDJ低位超卖，关注反弹"

    # 金叉死叉判断
    if k > d and j > k:
        return "📈 KDJ金叉，买入信号"
    elif k < d and j < k:
        return "📉 KDJ死叉，卖出信号"
    elif k > d:
        return "📊 K线上穿D线，多头趋势"
    elif k < d:
        return "📊 K线下穿D线，空头趋势"
    else:
        return "➡️ KDJ震荡中"
