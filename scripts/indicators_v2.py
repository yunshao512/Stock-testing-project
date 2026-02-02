#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
技术指标计算模块 v2.0
包含：SMA, EMA, RSI, MACD, 布林带, KDJ
"""

from typing import List, Dict, Optional, Tuple
import math
import sys
sys.path.append('/home/parallels/.openclaw/workspace/skills/a-stock-fetcher/scripts')
from kdj_indicator import calculate_kdj, interpret_kdj

def calculate_sma(prices: List[float], period: int) -> List[Optional[float]]:
    """计算简单移动平均线 (SMA)"""
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
    """计算指数移动平均线 (EMA)"""
    if len(prices) < period:
        return [None] * len(prices)

    multiplier = 2 / (period + 1)
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
    """计算相对强弱指标 (RSI)"""
    if len(prices) < period + 1:
        return [None] * len(prices)

    changes = []
    for i in range(1, len(prices)):
        changes.append(prices[i] - prices[i-1])

    rsi = [None]

    gains = [c if c > 0 else 0 for c in changes[:period]]
    losses = [-c if c < 0 else 0 for c in changes[:period]]

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        rsi.append(100)
    else:
        rs = avg_gain / avg_loss
        rsi.append(100 - (100 / (1 + rs)))

    for i in range(period, len(changes)):
        gain = changes[i] if changes[i] > 0 else 0
        loss = -changes[i] if changes[i] < 0 else 0

        avg_gain = ((avg_gain * (period - 1)) + gain) / period
        avg_loss = ((avg_loss * (period - 1)) + loss) / period

        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))

    return rsi

def calculate_macd(prices: List[float], fast_period=12, slow_period=26, signal_period=9) -> Dict[str, List[Optional[float]]]:
    """计算MACD指标"""
    ema_fast = calculate_ema(prices, fast_period)
    ema_slow = calculate_ema(prices, slow_period)

    macd_line = []
    for i in range(len(prices)):
        if ema_fast[i] is None or ema_slow[i] is None:
            macd_line.append(None)
        else:
            macd_line.append(ema_fast[i] - ema_slow[i])

    valid_macd = [m for m in macd_line if m is not None]
    if len(valid_macd) < signal_period:
        return {'macd': macd_line, 'signal': [None] * len(macd_line), 'histogram': [None] * len(macd_line)}

    ema_signal = calculate_ema(valid_macd, signal_period)
    signal_line = [None] * (len(prices) - len(ema_signal)) + ema_signal

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
    """计算布林带"""
    middle = calculate_sma(prices, period)
    upper = []
    lower = []

    for i in range(len(prices)):
        if middle[i] is None or i < period - 1:
            upper.append(None)
            lower.append(None)
        else:
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

def calculate_all_indicators(candles: List[Dict]) -> Dict[str, any]:
    """
    计算所有技术指标

    Args:
        candles: K线数据列表，每个元素包含 open, high, low, close

    Returns:
        包含所有指标的字典
    """
    # 提取价格数据
    closes = [c['close'] for c in candles]
    highs = [c['high'] for c in candles]
    lows = [c['low'] for c in candles]

    # 计算所有指标
    result = {
        'sma_5': calculate_sma(closes, 5),
        'sma_10': calculate_sma(closes, 10),
        'sma_20': calculate_sma(closes, 20),
        'sma_60': calculate_sma(closes, 60),
        'ema_12': calculate_ema(closes, 12),
        'ema_26': calculate_ema(closes, 26),
        'rsi': calculate_rsi(closes, 14),
        'macd': calculate_macd(closes),
        'bollinger': calculate_bollinger_bands(closes),
        'kdj': calculate_kdj(closes, highs, lows, 9, 3, 3)
    }

    return result

def interpret_indicators(indicators: Dict, latest_index: int = -1) -> Dict[str, str]:
    """
    解读所有技术指标

    Returns:
        包含各指标解读的字典
    """
    result = {}

    # RSI解读
    rsi = indicators['rsi'][latest_index]
    if rsi:
        if rsi >= 80:
            result['rsi'] = f"极度超买 ({rsi:.2f})"
        elif rsi >= 70:
            result['rsi'] = f"超买 ({rsi:.2f})"
        elif rsi >= 30:
            result['rsi'] = f"正常 ({rsi:.2f})"
        elif rsi >= 20:
            result['rsi'] = f"超卖 ({rsi:.2f})"
        else:
            result['rsi'] = f"极度超卖 ({rsi:.2f})"
    else:
        result['rsi'] = "无数据"

    # MACD解读
    macd = indicators['macd']['macd'][latest_index]
    signal = indicators['macd']['signal'][latest_index]
    histogram = indicators['macd']['histogram'][latest_index]

    if macd and signal:
        if macd > signal and histogram > 0:
            result['macd'] = "金叉，多头信号"
        elif macd < signal and histogram < 0:
            result['macd'] = "死叉，空头信号"
        elif macd > 0 and signal > 0:
            result['macd'] = "多头市场"
        elif macd < 0 and signal < 0:
            result['macd'] = "空头市场"
        else:
            result['macd'] = "震荡行情"
    else:
        result['macd'] = "无数据"

    # KDJ解读
    k = indicators['kdj']['K'][latest_index]
    d = indicators['kdj']['D'][latest_index]
    j = indicators['kdj']['J'][latest_index]
    result['kdj'] = interpret_kdj(k, d, j)

    # 布林带解读
    bb_upper = indicators['bollinger']['upper'][latest_index]
    bb_lower = indicators['bollinger']['lower'][latest_index]
    bb_middle = indicators['bollinger']['middle'][latest_index]
    current_price = indicators['sma_20'][latest_index]

    if bb_upper and bb_lower and bb_middle:
        if current_price >= bb_upper:
            result['bollinger'] = "触及上轨，可能回调"
        elif current_price <= bb_lower:
            result['bollinger'] = "触及下轨，可能反弹"
        else:
            result['bollinger'] = "中轨附近，正常"
    else:
        result['bollinger'] = "无数据"

    # 均线趋势
    sma5 = indicators['sma_5'][latest_index]
    sma10 = indicators['sma_10'][latest_index]
    sma20 = indicators['sma_20'][latest_index]

    if sma5 and sma10 and sma20:
        if sma5 > sma10 > sma20:
            result['ma_trend'] = "多头排列，看涨"
        elif sma5 < sma10 < sma20:
            result['ma_trend'] = "空头排列，看跌"
        else:
            result['ma_trend'] = "均线交叉，趋势不明"
    else:
        result['ma_trend'] = "无数据"

    return result
