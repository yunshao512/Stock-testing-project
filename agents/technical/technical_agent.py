#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
技术分析智能体
负责K线形态、技术指标、量价关系分析
"""

import sys
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# 添加scripts目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from stock_api import fetch_stock_data
from historical_data import fetch_historical_data


@dataclass
class TechnicalAnalysisResult:
    """技术分析结果"""
    trend: str = "未知"  # 上升/下降/横盘
    position: str = "未知"  # 高位/中位/低位
    patterns: List[str] = field(default_factory=list)  # 形态列表
    indicators: Dict = field(default_factory=dict)  # 技术指标
    volume_price: str = ""  # 量价关系
    score: float = 0.0  # 评分 0-1
    signals: List[str] = field(default_factory=list)  # 信号列表


class TechnicalAnalysisAgent:
    """技术分析智能体"""

    def __init__(self, debug: bool = False):
        self.debug = debug

    def analyze(self, symbol: str, days: int = 30) -> TechnicalAnalysisResult:
        """
        执行技术分析

        Args:
            symbol: 股票代码
            days: 分析天数

        Returns:
            TechnicalAnalysisResult: 分析结果
        """
        result = TechnicalAnalysisResult()

        # 获取实时数据
        stocks = fetch_stock_data([symbol], use_cache=False)
        if not stocks:
            if self.debug:
                print(f"  ❌ 无法获取 {symbol} 的实时数据")
            return result

        stock = stocks[0]
        current_price = stock['price']

        # 获取历史数据
        candles = fetch_historical_data(symbol, '1d', days)
        if not candles or len(candles) < 10:
            if self.debug:
                print(f"  ❌ 历史数据不足")
            return result

        # 1. 趋势分析
        result.trend = self._analyze_trend(candles)

        # 2. 位置分析
        result.position = self._analyze_position(candles, current_price)

        # 3. 形态识别
        result.patterns = self._recognize_patterns(candles)

        # 4. 技术指标
        result.indicators = self._calculate_indicators(candles)

        # 5. 量价关系
        result.volume_price = self._analyze_volume_price(candles, stock)

        # 6. 综合评分
        result.score = self._calculate_score(result)

        # 7. 生成信号
        result.signals = self._generate_signals(result, current_price)

        if self.debug:
            print(f"  ✅ 技术分析完成，评分: {result.score*100:.0f}%")
            print(f"     趋势: {result.trend}, 位置: {result.position}")

        return result

    def _analyze_trend(self, candles: List[Dict]) -> str:
        """分析趋势"""
        if len(candles) < 5:
            return "未知"

        # 计算短期和中期趋势
        short_trend = (candles[-1]['close'] - candles[-6]['close']) / candles[-6]['close']
        mid_trend = (candles[-1]['close'] - candles[-21]['close']) / candles[-21]['close']

        if short_trend > 0.02 and mid_trend > 0.02:
            return "上升"
        elif short_trend < -0.02 and mid_trend < -0.02:
            return "下降"
        else:
            return "横盘"

    def _analyze_position(self, candles: List[Dict], current_price: float) -> str:
        """分析价格位置"""
        if len(candles) < 10:
            return "未知"

        # 计算近期高低点
        recent_highs = [c['high'] for c in candles[-10:]]
        recent_lows = [c['low'] for c in candles[-10:]]
        highest = max(recent_highs)
        lowest = min(recent_lows)
        range_size = highest - lowest

        if range_size <= 0:
            return "未知"

        position = (current_price - lowest) / range_size

        if position < 0.3:
            return "低位"
        elif position > 0.7:
            return "高位"
        else:
            return "中位"

    def _recognize_patterns(self, candles: List[Dict]) -> List[str]:
        """识别K线形态"""
        patterns = []

        if len(candles) < 3:
            return patterns

        # 底部横盘形态
        recent_lows = [c['low'] for c in candles[-10:]]
        if max(recent_lows) - min(recent_lows) < 0.05 * min(recent_lows):
            patterns.append("底部横盘")

        # 上升趋势细分（均线多头排列）
        ma5 = sum(c['close'] for c in candles[-5:]) / 5
        ma10 = sum(c['close'] for c in candles[-10:]) / 10
        ma20 = sum(c['close'] for c in candles[-20:]) / 20

        if ma5 > ma10 > ma20:
            patterns.append("均线多头")

        # 下降趋势细分（均线空头排列）
        if ma5 < ma10 < ma20:
            patterns.append("均线空头")

        # 特殊K线形态
        last = candles[-1]
        prev = candles[-2]

        # 吞没形态
        if (last['close'] > prev['open'] and last['open'] < prev['close'] and
            last['close'] > prev['close'] and last['open'] < prev['open']):
            patterns.append("阳线吞没")

        if (last['close'] < prev['open'] and last['open'] > prev['close'] and
            last['close'] < prev['close'] and last['open'] > prev['open']):
            patterns.append("阴线吞没")

        # 金叉（简化版：5日线上穿10日线）
        ma5_prev = sum(c['close'] for c in candles[-6:-1]) / 5
        ma10_prev = sum(c['close'] for c in candles[-11:-1]) / 10
        if ma5_prev <= ma10_prev and ma5 > ma10:
            patterns.append("MA金叉")

        # 死叉
        if ma5_prev >= ma10_prev and ma5 < ma10:
            patterns.append("MA死叉")

        return patterns

    def _calculate_indicators(self, candles: List[Dict]) -> Dict:
        """计算技术指标"""
        indicators = {}

        # RSI（简化版）
        if len(candles) >= 14:
            gains = []
            losses = []
            for i in range(len(candles) - 13, len(candles)):
                change = candles[i]['close'] - candles[i-1]['close']
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))

            avg_gain = sum(gains) / 14 if gains else 0
            avg_loss = sum(losses) / 14 if losses else 0

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            indicators['RSI'] = round(rsi, 2)

        # MACD（简化版）
        if len(candles) >= 26:
            ema12 = self._calculate_ema(candles, 12)
            ema26 = self._calculate_ema(candles, 26)
            macd = ema12 - ema26
            indicators['MACD'] = round(macd, 2)

        return indicators

    def _calculate_ema(self, candles: List[Dict], period: int) -> float:
        """计算EMA"""
        if len(candles) < period:
            return candles[-1]['close']

        multiplier = 2 / (period + 1)
        ema = sum(c['close'] for c in candles[:period]) / period

        for c in candles[period:]:
            ema = (c['close'] - ema) * multiplier + ema

        return ema

    def _analyze_volume_price(self, candles: List[Dict], stock: Dict) -> str:
        """分析量价关系"""
        if len(candles) < 10:
            return "未知"

        current_volume = stock['volume']
        avg_volume = sum(c['volume'] for c in candles[-10:-1]) / 9
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

        change_pct = stock['change_percent']

        if change_pct > 2.0 and volume_ratio > 1.5:
            return "放量上涨"
        elif change_pct < -2.0 and volume_ratio > 1.5:
            return "放量下跌"
        elif change_pct > 2.0 and volume_ratio < 0.8:
            return "缩量上涨"
        elif change_pct < -2.0 and volume_ratio < 0.8:
            return "缩量下跌"
        else:
            return "量价正常"

    def _calculate_score(self, result: TechnicalAnalysisResult) -> float:
        """计算技术分析评分"""
        score = 0.0

        # 趋势评分
        if result.trend == "上升":
            score += 0.25
        elif result.trend == "下降":
            score -= 0.25

        # 位置评分
        if result.position == "低位":
            score += 0.20
        elif result.position == "高位":
            score -= 0.20

        # 形态评分
        positive_patterns = ["底部横盘", "均线多头", "阳线吞没", "MA金叉"]
        negative_patterns = ["均线空头", "阴线吞没", "MA死叉"]

        for pattern in result.patterns:
            if pattern in positive_patterns:
                score += 0.10
            elif pattern in negative_patterns:
                score -= 0.10

        # 量价评分
        if "放量上涨" in result.volume_price:
            score += 0.15
        elif "放量下跌" in result.volume_price:
            score -= 0.15

        # RSI指标评分
        rsi = result.indicators.get('RSI', 50)
        if rsi < 30:  # 超卖
            score += 0.15
        elif rsi > 70:  # 超买
            score -= 0.15

        # 限制在0-1之间
        score = max(0.0, min(1.0, score))

        return score

    def _generate_signals(self, result: TechnicalAnalysisResult, current_price: float) -> List[str]:
        """生成技术信号"""
        signals = []

        if result.score >= 0.7:
            signals.append("强烈买入信号")
        elif result.score >= 0.5:
            signals.append("买入信号")
        elif result.score <= 0.3:
            signals.append("卖出信号")
        elif result.score <= 0.1:
            signals.append("强烈卖出信号")
        else:
            signals.append("观望")

        return signals
