#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
形态识别模块 v2.0
扩展K线形态识别，支持更复杂的形态
"""

from typing import List, Dict, Tuple


class PatternRecognizer:
    """形态识别器"""

    def __init__(self):
        self.min_bars = 20  # 最少K线数量

    def recognize_all(self, candles: List[Dict]) -> List[str]:
        """
        识别所有形态

        Args:
            candles: K线数据列表

        Returns:
            识别到的形态列表
        """
        if len(candles) < self.min_bars:
            return []

        patterns = []

        # 基础形态
        patterns.extend(self._recognize_basic_patterns(candles))

        # 高级形态
        patterns.extend(self._recognize_head_shoulders(candles))
        patterns.extend(self._recognize_double_bottom_top(candles))
        patterns.extend(self._recognize_triangle(candles))
        patterns.extend(self._recognize_flag(candles))
        patterns.extend(self._recognize_wedge(candles))

        return patterns

    def _recognize_basic_patterns(self, candles: List[Dict]) -> List[str]:
        """识别基础形态"""
        patterns = []

        if len(candles) < 5:
            return patterns

        # 底部横盘
        recent_lows = [c['low'] for c in candles[-10:]]
        if len(recent_lows) >= 5:
            low_range = max(recent_lows) - min(recent_lows)
            avg_low = sum(recent_lows) / len(recent_lows)

            if low_range < 0.05 * avg_low:
                patterns.append("底部横盘")

        # 均线多头排列（上升趋势）
        ma5 = sum(c['close'] for c in candles[-5:]) / 5
        ma10 = sum(c['close'] for c in candles[-10:]) / 10
        ma20 = sum(c['close'] for c in candles[-20:]) / 20

        if ma5 > ma10 > ma20:
            patterns.append("均线多头")

        # 均线空头排列（下降趋势）
        if ma5 < ma10 < ma20:
            patterns.append("均线空头")

        # 吞没形态
        last = candles[-1]
        prev = candles[-2]

        # 阳线吞没
        if (last['close'] > prev['open'] and
            last['open'] < prev['close'] and
            last['close'] > prev['close'] and
            last['open'] < prev['open']):
            patterns.append("阳线吞没")

        # 阴线吞没
        if (last['close'] < prev['open'] and
            last['open'] > prev['close'] and
            last['close'] < prev['close'] and
            last['open'] > prev['open']):
            patterns.append("阴线吞没")

        # MA金叉
        ma5_prev = sum(c['close'] for c in candles[-6:-1]) / 5
        ma10_prev = sum(c['close'] for c in candles[-11:-1]) / 10
        if ma5_prev <= ma10_prev and ma5 > ma10:
            patterns.append("MA金叉")

        # MA死叉
        if ma5_prev >= ma10_prev and ma5 < ma10:
            patterns.append("MA死叉")

        return patterns

    def _recognize_head_shoulders(self, candles: List[Dict]) -> List[str]:
        """
        识别头肩底/顶形态

        Args:
            candles: K线数据

        Returns:
            识别到的形态列表
        """
        patterns = []

        if len(candles) < 30:
            return patterns

        # 寻找关键点（高点/低点）
        highs = []
        lows = []

        for i in range(2, len(candles) - 2):
            # 高点
            if (candles[i]['high'] > candles[i-1]['high'] and
                candles[i]['high'] > candles[i-2]['high'] and
                candles[i]['high'] > candles[i+1]['high'] and
                candles[i]['high'] > candles[i+2]['high']):
                highs.append({
                    'index': i,
                    'price': candles[i]['high'],
                    'date': candles[i].get('date', '')
                })

            # 低点
            if (candles[i]['low'] < candles[i-1]['low'] and
                candles[i]['low'] < candles[i-2]['low'] and
                candles[i]['low'] < candles[i+1]['low'] and
                candles[i]['low'] < candles[i+2]['low']):
                lows.append({
                    'index': i,
                    'price': candles[i]['low'],
                    'date': candles[i].get('date', '')
                })

        # 头肩顶
        if len(highs) >= 3:
            # 检查最近3个高点
            recent_highs = highs[-3:]

            # 检查是否是头肩顶：左肩 < 头 > 右肩
            h1, h2, h3 = recent_highs

            if h1['price'] < h2['price'] > h3['price']:
                # 检查左肩和右肩高度接近
                if abs(h1['price'] - h3['price']) / h1['price'] < 0.05:
                    patterns.append("头肩顶")

        # 头肩底
        if len(lows) >= 3:
            # 检查最近3个低点
            recent_lows = lows[-3:]

            # 检查是否是头肩底：左肩 > 头 < 右肩
            l1, l2, l3 = recent_lows

            if l1['price'] > l2['price'] < l3['price']:
                # 检查左肩和右肩高度接近
                if abs(l1['price'] - l3['price']) / l1['price'] < 0.05:
                    patterns.append("头肩底")

        return patterns

    def _recognize_double_bottom_top(self, candles: List[Dict]) -> List[str]:
        """
        识别双底/双顶形态

        Args:
            candles: K线数据

        Returns:
            识别到的形态列表
        """
        patterns = []

        if len(candles) < 20:
            return patterns

        # 寻找关键点
        highs = []
        lows = []

        for i in range(5, len(candles) - 5):
            # 高点
            if (candles[i]['high'] > candles[i-1]['high'] and
                candles[i]['high'] > candles[i-2]['high'] and
                candles[i]['high'] > candles[i+1]['high'] and
                candles[i]['high'] > candles[i+2]['high']):
                highs.append({
                    'index': i,
                    'price': candles[i]['high']
                })

            # 低点
            if (candles[i]['low'] < candles[i-1]['low'] and
                candles[i]['low'] < candles[i-2]['low'] and
                candles[i]['low'] < candles[i+1]['low'] and
                candles[i]['low'] < candles[i+2]['low']):
                lows.append({
                    'index': i,
                    'price': candles[i]['low']
                })

        # 双顶
        if len(highs) >= 2:
            # 检查最近2个高点
            h1, h2 = highs[-2], highs[-1]

            # 检查是否是双顶：两个高点高度接近
            if abs(h1['price'] - h2['price']) / h1['price'] < 0.03:
                # 检查中间有回调
                min_between = min(c['low'] for c in candles[h1['index']:h2['index']])
                if min_between < h1['price'] * 0.95:
                    patterns.append("双顶")

        # 双底
        if len(lows) >= 2:
            # 检查最近2个低点
            l1, l2 = lows[-2], lows[-1]

            # 检查是否是双底：两个低点高度接近
            if abs(l1['price'] - l2['price']) / l1['price'] < 0.03:
                # 检查中间有反弹
                max_between = max(c['high'] for c in candles[l1['index']:l2['index']])
                if max_between > l1['price'] * 1.05:
                    patterns.append("双底")

        return patterns

    def _recognize_triangle(self, candles: List[Dict]) -> List[str]:
        """
        识别三角形整理形态

        Args:
            candles: K线数据

        Returns:
            识别到的形态列表
        """
        patterns = []

        if len(candles) < 20:
            return patterns

        # 获取最近20根K线的高低点
        recent = candles[-20:]

        highs = [c['high'] for c in recent]
        lows = [c['low'] for c in recent]

        # 计算高低点趋势
        high_trend = (highs[-1] - highs[0]) / highs[0]
        low_trend = (lows[-1] - lows[0]) / lows[0]

        # 上升三角形：低点上升，高点横盘
        if low_trend > 0.05 and abs(high_trend) < 0.02:
            patterns.append("上升三角形")

        # 下降三角形：高点下降，低点横盘
        if high_trend < -0.05 and abs(low_trend) < 0.02:
            patterns.append("下降三角形")

        # 对称三角形：高点下降，低点上升
        if high_trend < -0.05 and low_trend > 0.05:
            patterns.append("对称三角形")

        return patterns

    def _recognize_flag(self, candles: List[Dict]) -> List[str]:
        """
        识别旗形整理形态

        Args:
            candles: K线数据

        Returns:
            识别到的形态列表
        """
        patterns = []

        if len(candles) < 20:
            return patterns

        # 分为两部分：旗杆（前10根）和旗面（后10根）
        pole = candles[-20:-10]
        flag = candles[-10:]

        # 计算旗杆趋势
        pole_start = pole[0]['close']
        pole_end = pole[-1]['close']
        pole_trend = (pole_end - pole_start) / pole_start

        # 计算旗面波动
        flag_highs = [c['high'] for c in flag]
        flag_lows = [c['low'] for c in flag]
        flag_range = max(flag_highs) - min(flag_lows)
        flag_close = flag[-1]['close']

        # 上升旗形：旗杆上涨，旗面回调
        if pole_trend > 0.05 and flag_close < pole_end:
            if flag_range < pole_end * 0.05:
                patterns.append("上升旗形")

        # 下降旗形：旗杆下跌，旗面反弹
        if pole_trend < -0.05 and flag_close > pole_end:
            if flag_range < pole_end * 0.05:
                patterns.append("下降旗形")

        return patterns

    def _recognize_wedge(self, candles: List[Dict]) -> List[str]:
        """
        识别楔形形态

        Args:
            candles: K线数据

        Returns:
            识别到的形态列表
        """
        patterns = []

        if len(candles) < 20:
            return patterns

        # 获取最近20根K线的高低点
        recent = candles[-20:]

        highs = [c['high'] for c in recent]
        lows = [c['low'] for c in recent]

        # 计算高低点趋势
        high_trend = (highs[-1] - highs[0]) / highs[0]
        low_trend = (lows[-1] - lows[0]) / lows[0]

        # 上升楔形：高点下降，低点上升（收敛）
        if high_trend < -0.05 and low_trend > 0.05:
            # 检查是否收敛
            high_range = max(highs) - min(highs)
            low_range = max(lows) - min(lows)

            if high_range < low_range * 0.5:
                patterns.append("上升楔形")

        # 下降楔形：高点上升，低点下降（扩散）
        if high_trend > 0.05 and low_trend < -0.05:
            patterns.append("下降楔形")

        return patterns

    def calculate_pattern_quality(self, pattern: str, candles: List[Dict]) -> float:
        """
        计算形态质量评分

        Args:
            pattern: 形态名称
            candles: K线数据

        Returns:
            质量评分 0-1
        """
        # 简化版：基于形态类型给分
        quality_scores = {
            "头肩顶": 0.85,
            "头肩底": 0.85,
            "双顶": 0.80,
            "双底": 0.80,
            "上升三角形": 0.75,
            "下降三角形": 0.75,
            "对称三角形": 0.70,
            "上升旗形": 0.75,
            "下降旗形": 0.75,
            "上升楔形": 0.65,
            "下降楔形": 0.65,
            "底部横盘": 0.70,
            "均线多头": 0.60,
            "均线空头": 0.60,
            "阳线吞没": 0.65,
            "阴线吞没": 0.65,
            "MA金叉": 0.55,
            "MA死叉": 0.55,
        }

        return quality_scores.get(pattern, 0.5)


def test_patterns():
    """测试形态识别"""
    print("="*80)
    print("🧪 测试形态识别")
    print("="*80)

    # 生成测试数据
    import random

    candles = []
    base_price = 100.0

    for i in range(50):
        price_change = random.uniform(-2, 2)
        open_price = base_price + random.uniform(-1, 1)
        close_price = open_price + price_change
        high_price = max(open_price, close_price) + random.uniform(0, 1)
        low_price = min(open_price, close_price) - random.uniform(0, 1)

        candles.append({
            'date': f'2024-01-{i+1:02d}',
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': random.randint(1000000, 10000000)
        })

        base_price = close_price

    # 识别形态
    recognizer = PatternRecognizer()
    patterns = recognizer.recognize_all(candles)

    print(f"\n📊 识别到 {len(patterns)} 个形态:\n")

    for pattern in patterns:
        quality = recognizer.calculate_pattern_quality(pattern, candles)
        print(f"  • {pattern} (质量评分: {quality*100:.0f}%)")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_patterns()
