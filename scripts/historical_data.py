#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
历史数据查询模块
基于新浪财经API获取K线历史数据
"""

import urllib.request
import json
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

# API配置
HISTORY_API_URL = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"

# 周期映射
SCALE_MAP = {
    '1m': '5',      # 1分钟
    '5m': '5',      # 5分钟
    '15m': '15',    # 15分钟
    '30m': '30',    # 30分钟
    '60m': '60',    # 60分钟
    '1d': '240',    # 日K
    '1w': '1001',   # 周K
    '1M': '1002',   # 月K
}

def fetch_historical_data(symbol: str, period: str = '1d', count: int = 100) -> Optional[List[Dict]]:
    """
    获取历史K线数据

    Args:
        symbol: 股票代码（如 sh600519, sz000001）
        period: 周期（1m, 5m, 15m, 30m, 60m, 1d, 1w, 1M）
        count: 获取数量

    Returns:
        K线数据列表，每个元素包含 day, open, high, low, close, volume
    """
    # 转换周期代码
    scale = SCALE_MAP.get(period, '240')

    # 构建URL
    params = {
        'symbol': symbol,
        'scale': scale,
        'ma': 'no',
        'datalen': count
    }

    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    url = f"{HISTORY_API_URL}?{query_string}"

    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        req.add_header('Referer', 'http://money.finance.sina.com.cn/')

        print(f"📊 正在获取历史数据: {symbol} ({period}, {count}根)")

        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read().decode('utf-8')

        # 解析JSON
        if not data or data == '':
            print(f"❌ 未获取到数据")
            return None

        # 新浪API返回的是类似JSON但不是标准JSON
        # 需要手动解析
        import re

        # 提取JSON部分
        json_match = re.search(r'\[.*\]', data)
        if not json_match:
            print(f"❌ 数据格式错误")
            return None

        json_str = json_match.group(0)
        raw_data = json.loads(json_str)

        # 转换数据格式
        candles = []
        for item in raw_data:
            candle = {
                'date': item.get('day'),
                'open': float(item.get('open', 0)),
                'high': float(item.get('high', 0)),
                'low': float(item.get('low', 0)),
                'close': float(item.get('close', 0)),
                'volume': int(item.get('volume', 0))
            }
            candles.append(candle)

        print(f"✅ 成功获取 {len(candles)} 根K线数据")
        return candles

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP错误: {e.code}")
        return None
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
        return None
    except Exception as e:
        print(f"❌ 解析错误: {e}")
        return None

def fetch_multiple_stocks(symbols: List[str], period: str = '1d', count: int = 100) -> Dict[str, List[Dict]]:
    """
    批量获取多只股票的历史数据

    Args:
        symbols: 股票代码列表
        period: 周期
        count: 数量

    Returns:
        字典，键为股票代码，值为K线数据列表
    """
    result = {}

    for symbol in symbols:
        print(f"\n{'='*60}")
        data = fetch_historical_data(symbol, period, count)
        if data:
            result[symbol] = data

        # 避免请求过快
        time.sleep(0.5)

    return result

def calculate_returns(candles: List[Dict], days: int = 1) -> List[float]:
    """
    计算收益率

    Args:
        candles: K线数据
        days: 计算周期

    Returns:
        收益率列表
    """
    returns = []

    for i in range(len(candles) - days):
        if candles[i]['close'] == 0:
            returns.append(0)
        else:
            ret = (candles[i + days]['close'] - candles[i]['close']) / candles[i]['close'] * 100
            returns.append(ret)

    # 前面days个数据为None
    for _ in range(days):
        returns.insert(0, None)

    return returns

def get_summary_stats(candles: List[Dict]) -> Dict:
    """
    获取统计摘要

    Args:
        candles: K线数据

    Returns:
        统计信息字典
    """
    if not candles:
        return {}

    latest = candles[-1]
    first = candles[0]

    # 计算涨跌
    total_change = latest['close'] - first['close']
    total_change_pct = (total_change / first['close']) * 100 if first['close'] > 0 else 0

    # 最高最低
    highs = [c['high'] for c in candles]
    lows = [c['low'] for c in candles]
    volumes = [c['volume'] for c in candles]

    return {
        'first_price': first['close'],
        'latest_price': latest['close'],
        'total_change': total_change,
        'total_change_pct': total_change_pct,
        'highest_price': max(highs),
        'lowest_price': min(lows),
        'avg_volume': sum(volumes) / len(volumes),
        'total_days': len(candles),
        'start_date': first['date'],
        'end_date': latest['date']
    }

def format_summary_stats(stats: Dict) -> str:
    """格式化统计信息"""
    if not stats:
        return "❌ 无统计数据"

    arrow = "↑" if stats['total_change'] > 0 else "↓" if stats['total_change'] < 0 else "→"
    color_sign = "+" if stats['total_change'] > 0 else ""

    return f"""
📊 统计摘要
─────────────────────────────────────
  起始日期: {stats['start_date']}
  结束日期: {stats['end_date']}
  统计天数: {stats['total_days']}天
─────────────────────────────────────
  起始价格: ¥{stats['first_price']:.2f}
  当前价格: ¥{stats['latest_price']:.2f}
  总涨跌:   {arrow}{abs(stats['total_change']):.2f} ({color_sign}{abs(stats['total_change_pct']):.2f}%)
─────────────────────────────────────
  最高价格: ¥{stats['highest_price']:.2f}
  最低价格: ¥{stats['lowest_price']:.2f}
  价格区间: ¥{stats['highest_price'] - stats['lowest_price']:.2f}
─────────────────────────────────────
  平均成交量: {stats['avg_volume']:,.0f} 手
"""
