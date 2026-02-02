#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from stock_api import fetch_stock_data, format_stock
from indicators import (
    calculate_sma, calculate_ema, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, interpret_rsi, interpret_macd
)

def analyze_stock(stock_codes):
    """股票综合分析"""
    # 获取实时数据
    stocks = fetch_stock_data(stock_codes)

    if not stocks:
        print("❌ 获取数据失败")
        return

    for stock in stocks:
        print("=" * 60)
        print(format_stock(stock))
        print("=" * 60)

        # 基础技术分析
        print("\n📈 技术分析:")

        # 趋势判断
        if stock['open'] and stock['high'] and stock['low']:
            if stock['price'] > stock['open']:
                print("  ✅ 日线趋势: 上涨")
            elif stock['price'] < stock['open']:
                print("  ❌ 日线趋势: 下跌")
            else:
                print("  ➡️ 日线趋势: 平盘")

            # 位置判断
            total_range = stock['high'] - stock['low']
            if total_range > 0:
                position = (stock['price'] - stock['low']) / total_range * 100
                if position > 80:
                    print(f"  📊 日内位置: 接近高位 ({position:.1f}%)")
                elif position < 20:
                    print(f"  📊 日内位置: 接近低位 ({position:.1f}%)")
                else:
                    print(f"  📊 日内位置: 中位 ({position:.1f}%)")

        # 量能分析
        if stock['volume']:
            print(f"  📊 成交量: {stock['volume']:,.0f} 手")

            # 买卖力量对比
            buy_volume = sum([
                stock.get('buy1_volume', 0),
                stock.get('buy2_volume', 0),
                stock.get('buy3_volume', 0),
                stock.get('buy4_volume', 0),
                stock.get('buy5_volume', 0)
            ])
            sell_volume = sum([
                stock.get('sell1_volume', 0),
                stock.get('sell2_volume', 0),
                stock.get('sell3_volume', 0),
                stock.get('sell4_volume', 0),
                stock.get('sell5_volume', 0)
            ])

            if buy_volume > 0 and sell_volume > 0:
                buy_sell_ratio = buy_volume / sell_volume
                if buy_sell_ratio > 1.5:
                    print(f"  💪 买盘强势 (买/卖比: {buy_sell_ratio:.2f})")
                elif buy_sell_ratio < 0.67:
                    print(f"  📉 卖盘压力大 (买/卖比: {buy_sell_ratio:.2f})")
                else:
                    print(f"  ⚖️ 买卖平衡 (买/卖比: {buy_sell_ratio:.2f})")

        # 委托分析
        buy1 = stock.get('buy1_price')
        sell1 = stock.get('sell1_price')
        if buy1 and sell1:
            spread = sell1 - buy1
            spread_percent = (spread / buy1) * 100
            print(f"  📏 买卖价差: {spread:.2f} 元 ({spread_percent:.3f}%)")

        # 综合建议
        print("\n💡 综合建议:")
        signals = []

        # 趋势信号
        if stock['price'] > stock['open']:
            signals.append("✅ 日线上涨")
        elif stock['price'] < stock['open']:
            signals.append("❌ 日线下跌")

        # 涨跌幅信号
        if stock['change_percent'] > 5:
            signals.append("🔥 大涨，注意风险")
        elif stock['change_percent'] > 2:
            signals.append("📈 强势上涨")
        elif stock['change_percent'] < -5:
            signals.append("💥 大跌，观察反弹")
        elif stock['change_percent'] < -2:
            signals.append("📉 弱势下跌")

        # 输出建议
        if signals:
            for signal in signals:
                print(f"  {signal}")
        else:
            print("  ➡️ 震荡行情，观望为主")

        print("\n" + "-" * 60)

def main():
    if len(sys.argv) < 2:
        print("📊 A股综合分析工具")
        print("\n用法:")
        print("  python3 analyze.py <股票代码>     # 分析单股")
        print("  python3 analyze.py <代码1>,<代码2>  # 分析多股")
        print("\n示例:")
        print("  python3 analyze.py sh600519")
        print("  python3 analyze.py 茅台")
        print("  python3 analyze.py sh600519,sz000001")
        sys.exit(0)

    # 解析股票代码
    input_codes = sys.argv[1]
    stock_codes = []

    if ',' in input_codes:
        codes = input_codes.split(',')
        for code in codes:
            stock_codes.append(code.strip())
    else:
        stock_codes = [input_codes]

    print(f"\n📊 正在分析: {', '.join(stock_codes)}")
    print("=" * 60)

    analyze_stock(stock_codes)

if __name__ == "__main__":
    main()
