#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import json
import sys
import time
from datetime import datetime

# 腾讯财经API
API_URL = "http://qt.gtimg.cn/q={codes}"

def fetch_stock_data(stock_codes):
    """获取股票数据"""
    if isinstance(stock_codes, str):
        stock_codes = [stock_codes]

    codes_str = ",".join(stock_codes)
    url = API_URL.format(codes=codes_str)

    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gbk')
        return data
    except Exception as e:
        return None

def parse_stock_data(raw_data):
    """解析股票数据"""
    if not raw_data or not raw_data.startswith('v_'):
        return []

    stocks = []
    lines = raw_data.strip().split('\n')

    for line in lines:
        if not line.startswith('v_'):
            continue

        try:
            # 去除开头的v_和结尾的";
            content = line[2:].rstrip('";')
            parts = content.split('~')

            if len(parts) < 50:
                continue

            code = parts[2]
            name = parts[1]

            # 如果没有数据，跳过
            if not code or code == '':
                continue

            stock = {
                'code': code,
                'name': name,
                'price': parse_float(parts[3]),           # 当前价
                'yesterday_close': parse_float(parts[4]), # 昨收
                'open': parse_float(parts[5]),           # 今开
                'high': parse_float(parts[33]),          # 最高
                'low': parse_float(parts[34]),           # 最低
                'volume': parse_float(parts[6]),         # 成交量（手）
                'amount': parse_float(parts[37]),        # 成交额（元）
                'timestamp': parse_timestamp(parts[30]),
            }

            # 计算涨跌幅
            if stock['yesterday_close'] and stock['price']:
                stock['change'] = stock['price'] - stock['yesterday_close']
                stock['change_percent'] = (stock['change'] / stock['yesterday_close']) * 100
            else:
                stock['change'] = 0
                stock['change_percent'] = 0

            # 买1-买5
            stock['buy1_price'] = parse_float(parts[9])
            stock['buy1_volume'] = parse_float(parts[10])
            stock['buy2_price'] = parse_float(parts[11])
            stock['buy2_volume'] = parse_float(parts[12])
            stock['buy3_price'] = parse_float(parts[13])
            stock['buy3_volume'] = parse_float(parts[14])
            stock['buy4_price'] = parse_float(parts[15])
            stock['buy4_volume'] = parse_float(parts[16])
            stock['buy5_price'] = parse_float(parts[17])
            stock['buy5_volume'] = parse_float(parts[18])

            # 卖1-卖5
            stock['sell1_price'] = parse_float(parts[19])
            stock['sell1_volume'] = parse_float(parts[20])
            stock['sell2_price'] = parse_float(parts[21])
            stock['sell2_volume'] = parse_float(parts[22])
            stock['sell3_price'] = parse_float(parts[23])
            stock['sell3_volume'] = parse_float(parts[24])
            stock['sell4_price'] = parse_float(parts[25])
            stock['sell4_volume'] = parse_float(parts[26])
            stock['sell5_price'] = parse_float(parts[27])
            stock['sell5_volume'] = parse_float(parts[28])

            stocks.append(stock)

        except Exception as e:
            continue

    return stocks

def parse_float(value):
    """解析浮点数"""
    try:
        if value == '' or value is None:
            return None
        return float(value)
    except:
        return None

def parse_timestamp(ts_str):
    """解析时间戳"""
    try:
        if not ts_str or ts_str == '':
            return None
        # 腾讯API格式：20260130161413
        ts = datetime.strptime(ts_str, "%Y%m%d%H%M%S")
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

def format_stock(stock):
    """格式化股票信息"""
    if not stock['price']:
        return f"{stock['name']} ({stock['code']}) - 停牌或无数据"

    arrow = "↑" if stock['change'] > 0 else "↓" if stock['change'] < 0 else "→"
    color = "\033[92m" if stock['change'] > 0 else "\033[91m" if stock['change'] < 0 else "\033[0m"
    reset = "\033[0m"

    return f"""
{color}{stock['name']} ({stock['code']}){reset}
  股价: {color}¥{stock['price']:.2f}{reset} {arrow}{color}{abs(stock['change']):.2f} ({abs(stock['change_percent']):.2f}%){reset}
  今开: ¥{stock['open']:.2f} | 最高: ¥{stock['high']:.2f} | 最低: ¥{stock['low']:.2f}
  成交量: {stock['volume']:,} 手 | 成交额: ¥{stock['amount']/100000000:.2f} 亿
  时间: {stock['timestamp']}
"""

def format_json(stocks):
    """格式化JSON输出"""
    return json.dumps(stocks, ensure_ascii=False, indent=2)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 a_stock.py <股票代码> [股票代码...]")
        print("示例: python3 a_stock.py sh600519")
        print("      python3 a_stock.py sh600519,sz000001,hk00700")
        sys.exit(1)

    stock_codes = sys.argv[1].split(',')

    print(f"📊 正在查询: {', '.join(stock_codes)}\n")

    raw_data = fetch_stock_data(stock_codes)

    if not raw_data:
        print("❌ 获取数据失败")
        sys.exit(1)

    stocks = parse_stock_data(raw_data)

    if len(stocks) == 0:
        print("❌ 未找到股票数据")
        sys.exit(1)

    # 输出格式化信息
    for stock in stocks:
        print(format_stock(stock))

    # 输出JSON（可选）
    # print("\n--- JSON数据 ---")
    # print(format_json(stocks))

if __name__ == "__main__":
    main()
