#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from stock_cache import StockDataCache, RateLimiter

# 腾讯财经API
API_URL = "http://qt.gtimg.cn/q={codes}"

# 初始化缓存和限流器
cache = StockDataCache(cache_ttl=60)  # 缓存60秒
rate_limiter = RateLimiter(max_requests=10, time_window=60)  # 每分钟最多10次请求

def fetch_stock_data(stock_codes: List[str], use_cache=True) -> Optional[List[Dict]]:
    """
    获取股票数据（带缓存和限流）

    Args:
        stock_codes: 股票代码列表
        use_cache: 是否使用缓存

    Returns:
        股票数据列表
    """
    # 合并代码，减少API调用
    cache_key = ",".join(sorted(stock_codes))

    # 尝试从缓存获取
    if use_cache:
        cached_data = cache.get(cache_key)
        if cached_data:
            print(f"📦 使用缓存数据 ({cache_key})")
            return cached_data

    # 检查频率限制
    if not rate_limiter.can_request():
        wait_time = rate_limiter.get_wait_time()
        status = rate_limiter.get_status()
        print(f"⏸️  请求过于频繁，请等待 {wait_time:.1f} 秒")
        print(f"   已用: {status['recent_requests']}/{status['max_requests']} 请求 (每{status['time_window']}秒)")

        # 如果有缓存，即使过期也返回
        cached_data = cache.get(cache_key)
        if cached_data:
            print(f"📦 使用过期缓存数据")
            return cached_data

        return None

    # 发起API请求
    codes_str = ",".join(stock_codes)
    url = API_URL.format(codes=codes_str)

    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        req.add_header('Referer', 'https://xueqiu.com/')

        print(f"🌐 正在请求API: {codes_str}")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gbk')

        # 解析数据
        stocks = parse_stock_data(data)

        # 保存到缓存
        if stocks and use_cache:
            cache.set(cache_key, stocks)

        return stocks

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP错误: {e.code} - {e.reason}")
        if e.code == 429:
            print("   触发频率限制，请等待1-2分钟")
        return None
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
        return None
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return None

def parse_stock_data(raw_data: str) -> List[Dict]:
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

def parse_float(value) -> Optional[float]:
    """解析浮点数"""
    try:
        if value == '' or value is None:
            return None
        return float(value)
    except:
        return None

def parse_timestamp(ts_str) -> Optional[str]:
    """解析时间戳"""
    try:
        if not ts_str or ts_str == '':
            return None
        ts = datetime.strptime(ts_str, "%Y%m%d%H%M%S")
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

def format_stock(stock: Dict) -> str:
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
  成交量: {stock['volume']:,.0f} 手 | 成交额: ¥{stock['amount']/100000000:.2f} 亿
  买1: ¥{stock['buy1_price']:.2f} ({stock['buy1_volume']:,.0f}手) | 卖1: ¥{stock['sell1_price']:.2f} ({stock['sell1_volume']:,.0f}手)
  时间: {stock['timestamp']}
"""

def get_rate_limiter_status() -> Dict[str, Any]:
    """获取限流器状态"""
    return rate_limiter.get_status()

def clear_cache():
    """清空缓存"""
    cache.clear()
    print("✅ 缓存已清空")
