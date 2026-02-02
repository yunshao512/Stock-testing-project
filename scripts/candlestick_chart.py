#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASCII K线图生成器
使用纯Python生成可打印的K线图，无需额外依赖
"""

def draw_candle(open_price: float, high: float, low: float, close: float,
                width: int = 20, height: int = 8) -> str:
    """
    绘制单根K线

    Args:
        open_price: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        width: K线宽度
        height: K线高度

    Returns:
        K线ASCII字符串
    """
    # 判断涨跌
    is_up = close >= open_price

    # 计算价格范围
    price_range = high - low
    if price_range == 0:
        price_range = 1  # 避免除零

    # 生成K线
    lines = []

    for i in range(height):
        y = high - (i * price_range / (height - 1))

        line = ""
        for j in range(width):
            x = j / width

            # 影线（上下影）
            if j == width // 2:
                if low <= y <= high:
                    if is_up:
                        line += "│"
                    else:
                        line += "│"
                else:
                    line += " "
            # 实体部分
            else:
                if min(open_price, close) <= y <= max(open_price, close):
                    if is_up:
                        line += "█"
                    else:
                        line += "█"
                else:
                    line += " "

        lines.append(line)

    return "\n".join(lines)

def draw_candlestick_chart(candles: list, width: int = 80, height: int = 20,
                           show_ma: bool = True) -> str:
    """
    绘制K线图

    Args:
        candles: K线数据列表 [{'date', 'open', 'high', 'low', 'close', 'volume'}]
        width: 图表宽度
        height: 图表高度
        show_ma: 是否显示均线

    Returns:
        ASCII图表字符串
    """
    if not candles:
        return "❌ 没有数据"

    # 限制显示的K线数量
    max_candles = (width - 20) // 3  # 每根K线占3个字符
    display_candles = candles[-max_candles:]

    # 计算价格范围
    all_highs = [c['high'] for c in display_candles]
    all_lows = [c['low'] for c in display_candles]
    min_price = min(all_lows)
    max_price = max(all_highs)
    price_range = max_price - min_price

    if price_range == 0:
        price_range = 1

    # 生成图表
    lines = []

    # 标题
    title = f"{' ' * (width // 2 - 10)}K线图 (最近{len(display_candles)}根)"
    lines.append(title)
    lines.append("─" * width)

    # K线区域
    for i in range(height):
        y = max_price - (i * price_range / (height - 1))

        line = f"{y:8.2f}│"  # 左侧价格标签

        for candle in display_candles:
            open_p = candle['open']
            high_p = candle['high']
            low_p = candle['low']
            close_p = candle['close']

            is_up = close_p >= open_p

            # 影线
            if low_p <= y <= high_p:
                line += "│" if is_up else "│"
            else:
                line += " "

            # 实体
            if min(open_p, close_p) <= y <= max(open_p, close_p):
                line += "█" if is_up else "█"

        lines.append(line)

    # 时间轴
    lines.append("─" * width)
    date_line = "         │"
    for i, candle in enumerate(display_candles):
        if i % 10 == 0:  # 每隔10根K线显示日期
            date_str = candle['date'][-5:] if 'date' in candle else ""
            date_line += date_str.center(2)
        else:
            date_line += "  "
    lines.append(date_line)

    # 底部信息
    latest = display_candles[-1]
    info = f"最新: {latest['close']:.2f} | 涨跌: {latest['close'] - latest['open']:+.2f} | 振幅: {((latest['high'] - latest['low']) / latest['open'] * 100):.2f}%"
    lines.append("─" * width)
    lines.append(info)

    return "\n".join(lines)

def draw_volume_chart(candles: list, width: int = 80, height: int = 8) -> str:
    """
    绘制成交量图

    Args:
        candles: K线数据列表
        width: 图表宽度
        height: 图表高度

    Returns:
        成交量图ASCII字符串
    """
    if not candles:
        return "❌ 没有数据"

    max_candles = width // 3
    display_candles = candles[-max_candles:]

    # 获取成交量范围
    volumes = [c['volume'] for c in display_candles if c.get('volume')]
    if not volumes:
        return "❌ 没有成交量数据"

    max_volume = max(volumes)
    min_volume = min(volumes)

    lines = []
    lines.append("─" * width)
    lines.append(f"{' ' * (width // 2 - 5)}成交量")

    for i in range(height):
        level = max_volume - (i * (max_volume - min_volume) / (height - 1))

        line = f"{level/10000:8.0f}万│"  # 左侧成交量标签

        for candle in display_candles:
            vol = candle.get('volume', 0)
            close = candle.get('close', 0)
            open_p = candle.get('open', 0)

            # 根据涨跌选择颜色字符
            if vol >= level:
                if close >= open_p:
                    line += "↑"  # 阳线成交量
                else:
                    line += "↓"  # 阴线成交量
            else:
                line += " "

        lines.append(line)

    lines.append("─" * width)
    return "\n".join(lines)

def draw_indicators_chart(indicators: dict, width: int = 80, height: int = 8) -> str:
    """
    绘制指标图（RSI/MACD等）

    Args:
        indicators: 指标数据
        width: 图表宽度
        height: 图表高度

    Returns:
        指标图ASCII字符串
    """
    lines = []

    # RSI图
    rsi = indicators.get('rsi', [])
    if rsi and rsi[-1]:
        lines.append("─" * width)
        lines.append(f"{' ' * (width // 2 - 3)}RSI (14)")

        # 显示RSI值和位置
        current_rsi = rsi[-1]
        lines.append(f"当前RSI: {current_rsi:.2f}")

        # 简单的RSI柱状图
        bar_width = min(int(abs(current_rsi - 50) * 0.6), 35)
        if current_rsi > 50:
            bar = "█" * bar_width + " " * (35 - bar_width)
            lines.append(f"50 |{bar}| {current_rsi:.1f} (超买区)")
        else:
            bar = " " * (35 - bar_width) + "█" * bar_width
            lines.append(f"  |{bar}| 50 {current_rsi:.1f} (超卖区)")

    # MACD图
    macd_data = indicators.get('macd', {})
    macd_line = macd_data.get('macd', [])
    histogram = macd_data.get('histogram', [])

    if macd_line and macd_line[-1] and histogram and histogram[-1]:
        lines.append("─" * width)
        lines.append(f"{' ' * (width // 2 - 4)}MACD (12,26,9)")

        current_macd = macd_line[-1]
        current_histogram = histogram[-1]

        hist_bar = "█" * min(int(abs(current_histogram) * 2), 35)
        if current_histogram > 0:
            lines.append(f"0 |{hist_bar}| {current_histogram:+.2f} (多头)")
        else:
            lines.append(f"  |{hist_bar}| 0 {current_histogram:+.2f} (空头)")

        lines.append(f"MACD: {current_macd:+.4f}")

    # KDJ图
    kdj_data = indicators.get('kdj', {})
    k_value = kdj_data.get('K', [])
    d_value = kdj_data.get('D', [])
    j_value = kdj_data.get('J', [])

    if k_value and k_value[-1]:
        lines.append("─" * width)
        lines.append(f"{' ' * (width // 2 - 3)}KDJ (9,3,3)")

        current_k = k_value[-1]
        current_d = d_value[-1] if d_value else 0
        current_j = j_value[-1] if j_value else 0

        lines.append(f"K: {current_k:.2f} | D: {current_d:.2f} | J: {current_j:.2f}")

        if current_k > current_d:
            lines.append("K > D 金叉信号 ⬆️")
        else:
            lines.append("K < D 死叉信号 ⬇️")

    if lines:
        lines.append("─" * width)

    return "\n".join(lines)

def draw_full_chart(candles: list, indicators: dict = None) -> str:
    """
    绘制完整图表（K线 + 成交量 + 指标）

    Args:
        candles: K线数据
        indicators: 技术指标

    Returns:
        完整ASCII图表
    """
    chart = ""
    chart += draw_candlestick_chart(candles)
    chart += "\n\n"
    chart += draw_volume_chart(candles)
    chart += "\n\n"

    if indicators:
        chart += draw_indicators_chart(indicators)

    return chart
