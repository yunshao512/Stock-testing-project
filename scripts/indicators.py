#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Optional
import math

def calculate_sma(prices: List[float], period: int) -> List[Optional[float]]:
    """
    计算简单移动平均线 (SMA)

    Args:
        prices: 价格列表（从旧到新）
        period: 周期

    Returns:
        SMA值列表（前面period-1个为None）
    """
    if len(prices) < period:
        return [None] * len(prices)

    sma = []
    for i in range(len(prices)):
        if i < period - 1:
            sma.append(None)
        else:
            sum_price = sum(prices[i-period+1:i+1])
            sma.append(sum_price / period)

    return sma

def calculate_ema(prices: List[float], period: int) -> List[Optional[float]]:
    """
    计算指数移动平均线 (EMA)

    Args:
        prices: 价格列表（从旧到新）
        period: 周期

    Returns:
        EMA值列表
    """
    if len(prices) < period:
        return [None] * len(prices)

    # 计算平滑系数
    multiplier = 2 / (period + 1)

    # 初始EMA（使用前period个价格的SMA）
    initial_ema = sum(prices[:period]) / period

    ema = []
    for i in range(len(prices)):
        if i < period - 1:
            ema.append(None)
        elif i == period - 1:
            ema.append(initial_ema)
        else:
            current_ema = (prices[i] * multiplier) + (ema[-1] * (1 - multiplier))
            ema.append(current_ema)

    return ema

def calculate_rsi(prices: List[float], period: int = 14) -> List[Optional[float]]:
    """
    计算相对强弱指标 (RSI)

    Args:
        prices: 价格列表（从旧到新）
        period: 周期，默认14

    Returns:
        RSI值列表（0-100）
    """
    if len(prices) < period + 1:
        return [None] * len(prices)

    # 计算价格变化
    changes = []
    for i in range(1, len(prices)):
        changes.append(prices[i] - prices[i-1])

    rsi = [None]  # 第一个数据点无RSI

    # 初始平均涨跌幅
    gains = [c if c > 0 else 0 for c in changes[:period]]
    losses = [-c if c < 0 else 0 for c in changes[:period]]

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    # 第一个RSI
    if avg_loss == 0:
        rsi.append(100)
    else:
        rs = avg_gain / avg_loss
        rsi.append(100 - (100 / (1 + rs)))

    # 后续RSI
    for i in range(period, len(changes)):
        gain = changes[i] if changes[i] > 0 else 0
        loss = -changes[i] if changes[i] < 0 else 0

        # 使用EMA方法计算平均涨跌幅
        avg_gain = ((avg_gain * (period - 1)) + gain) / period
        avg_loss = ((avg_loss * (period - 1)) + loss) / period

        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))

    return rsi

def calculate_macd(prices: List[float], fast_period=12, slow_period=26, signal_period=9) -> Dict[str, List[Optional[float]]]:
    """
    计算MACD指标

    Args:
        prices: 价格列表（从旧到新）
        fast_period: 快线周期，默认12
        slow_period: 慢线周期，默认26
        signal_period: 信号线周期，默认9

    Returns:
        包含MACD、Signal、Histogram的字典
    """
    # 计算快速和慢速EMA
    ema_fast = calculate_ema(prices, fast_period)
    ema_slow = calculate_ema(prices, slow_period)

    # 计算MACD线
    macd_line = []
    for i in range(len(prices)):
        if ema_fast[i] is None or ema_slow[i] is None:
            macd_line.append(None)
        else:
            macd_line.append(ema_fast[i] - ema_slow[i])

    # 计算信号线（MACD的EMA）
    # 过滤None值用于计算EMA
    valid_macd = [m for m in macd_line if m is not None]
    if len(valid_macd) < signal_period:
        return {'macd': macd_line, 'signal': [None] * len(macd_line), 'histogram': [None] * len(macd_line)}

    ema_signal = calculate_ema(valid_macd, signal_period)

    # 将信号线对齐到原始长度
    signal_line = [None] * (len(prices) - len(ema_signal)) + ema_signal

    # 计算柱状图
    histogram = []
    for i in range(len(prices)):
        if macd_line[i] is None or signal_line[i] is None:
            histogram.append(None)
        else:
            histogram.append(macd_line[i] - signal_line[i])

    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }

def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, List[Optional[float]]]:
    """
    计算布林带

    Args:
        prices: 价格列表（从旧到新）
        period: 周期，默认20
        std_dev: 标准差倍数，默认2

    Returns:
        包含middle, upper, lower的字典
    """
    middle = calculate_sma(prices, period)
    upper = []
    lower = []

    for i in range(len(prices)):
        if middle[i] is None or i < period - 1:
            upper.append(None)
            lower.append(None)
        else:
            # 计算标准差
            slice_prices = prices[i-period+1:i+1]
            mean = middle[i]
            variance = sum((p - mean) ** 2 for p in slice_prices) / period
            std = math.sqrt(variance)

            upper.append(mean + std_dev * std)
            lower.append(mean - std_dev * std)

    return {
        'middle': middle,
        'upper': upper,
        'lower': lower
    }

def interpret_rsi(rsi_value: float) -> str:
    """解读RSI值"""
    if rsi_value is None:
        return "无数据"

    if rsi_value >= 80:
        return "极度超买，可能有回调风险"
    elif rsi_value >= 70:
        return "超买区域，注意回调"
    elif rsi_value >= 50:
        return "多头市场，趋势向上"
    elif rsi_value >= 30:
        return "空头市场，趋势向下"
    elif rsi_value >= 20:
        return "超卖区域，可能反弹"
    else:
        return "极度超卖，反弹机会大"

def interpret_macd(macd: float, signal: float, histogram: float) -> str:
    """解读MACD信号"""
    if macd is None or signal is None:
        return "无数据"

    if macd > signal and histogram > 0:
        return "金叉，多头信号，考虑买入"
    elif macd < signal and histogram < 0:
        return "死叉，空头信号，考虑卖出"
    elif macd > 0 and signal > 0:
        return "双线在零轴上方，多头市场"
    elif macd < 0 and signal < 0:
        return "双线在零轴下方，空头市场"
    else:
        return "震荡行情"
