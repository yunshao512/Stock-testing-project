#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
涨跌停预警模块
监控股票价格，触发涨跌停时发送提醒
"""

import json
import os
from datetime import datetime, time
from typing import List, Dict, Optional, Callable
import time as time_module
from stock_api import fetch_stock_data

# 预警配置
ALERT_CONFIG_FILE = "/tmp/a_stock_alerts.json"
ALERT_LOG_FILE = "/tmp/a_stock_alerts.log"

# A股涨跌停限制
LIMIT_RULES = {
    'main': 0.10,      # 主板涨跌停：±10%
    'start': 0.10,     # 创业板：±10%
    'science': 0.20,   # 科创板：±20%
    'growth': 0.20,    # 创业板注册制：±20%
}

# 根据股票代码判断板块
def get_stock_type(symbol: str) -> str:
    """判断股票类型"""
    code = symbol.replace('sh', '').replace('sz', '')

    # 科创板：688xxx
    if code.startswith('688'):
        return 'science'

    # 创业板注册制：30xxxx
    if code.startswith('30'):
        return 'growth'

    # 创业板：300xxx（非注册制）
    if code.startswith('300'):
        return 'start'

    # 默认主板
    return 'main'

def get_limit_percent(symbol: str) -> float:
    """获取涨跌停幅度"""
    stock_type = get_stock_type(symbol)
    return LIMIT_RULES[stock_type]

def calculate_limits(symbol: str, yesterday_close: float) -> Dict[str, float]:
    """计算涨跌停价格"""
    limit_percent = get_limit_percent(symbol)

    return {
        'up_limit': yesterday_close * (1 + limit_percent),
        'down_limit': yesterday_close * (1 - limit_percent),
        'limit_percent': limit_percent * 100
    }

def check_limit_reached(stock: Dict) -> Dict[str, any]:
    """
    检查是否涨跌停

    Returns:
        {
            'is_up_limit': bool,
            'is_down_limit': bool,
            'distance_to_up': float,  # 距离涨停价格
            'distance_to_down': float  # 距离跌停价格
        }
    """
    if not stock.get('yesterday_close') or not stock.get('price'):
        return {
            'is_up_limit': False,
            'is_down_limit': False,
            'distance_to_up': None,
            'distance_to_down': None
        }

    limits = calculate_limits(stock['code'], stock['yesterday_close'])

    current_price = stock['price']
    up_limit = limits['up_limit']
    down_limit = limits['down_limit']

    # 判断是否涨跌停（允许小误差）
    epsilon = 0.001  # 0.01%

    is_up_limit = abs(current_price - up_limit) / up_limit < epsilon
    is_down_limit = abs(current_price - down_limit) / down_limit < epsilon

    return {
        'is_up_limit': is_up_limit,
        'is_down_limit': is_down_limit,
        'distance_to_up': up_limit - current_price,
        'distance_to_down': current_price - down_limit,
        'up_limit': up_limit,
        'down_limit': down_limit,
        'limit_percent': limits['limit_percent']
    }

def format_alert_message(stock: Dict, alert_info: Dict) -> str:
    """格式化预警消息"""
    name = stock['name']
    code = stock['code']
    price = stock['price']
    change_percent = stock['change_percent']

    if alert_info['is_up_limit']:
        emoji = "🔴"
        alert_type = "涨停"
        limit_price = alert_info['up_limit']
        return f"{emoji} {name} ({code}) 涨停！\n   当前价: ¥{price:.2f}\n   涨跌幅: +{abs(change_percent):.2f}%\n   涨停价: ¥{limit_price:.2f}"

    elif alert_info['is_down_limit']:
        emoji = "🟢"
        alert_type = "跌停"
        limit_price = alert_info['down_limit']
        return f"{emoji} {name} ({code}) 跌停！\n   当前价: ¥{price:.2f}\n   涨跌幅: -{abs(change_percent):.2f}%\n   跌停价: ¥{limit_price:.2f}"

    else:
        # 接近涨跌停警告
        up_distance_pct = (alert_info['distance_to_up'] / stock['price']) * 100
        down_distance_pct = (alert_info['distance_to_down'] / stock['price']) * 100

        if up_distance_pct < 1.0:
            return f"⚠️ {name} ({code}) 接近涨停！\n   距涨停: ¥{alert_info['distance_to_up']:.2f} ({up_distance_pct:.2f}%)"
        elif down_distance_pct < 1.0:
            return f"⚠️ {name} ({code}) 接近跌停！\n   距跌停: ¥{alert_info['distance_to_down']:.2f} ({down_distance_pct:.2f}%)"
        else:
            return ""

class AlertWatcher:
    """预警监控器"""

    def __init__(self, symbols: List[str], callback: Optional[Callable] = None):
        """
        初始化监控器

        Args:
            symbols: 监控股票代码列表
            callback: 预警回调函数
        """
        self.symbols = symbols
        self.callback = callback
        self.alerted_stocks = set()  # 已触发预警的股票

    def check(self) -> List[str]:
        """检查一次，返回预警消息列表"""
        alert_messages = []

        # 获取数据
        stocks = fetch_stock_data(self.symbols, use_cache=False)

        if not stocks:
            return alert_messages

        for stock in stocks:
            # 检查涨跌停
            alert_info = check_limit_reached(stock)

            # 触发预警
            if alert_info['is_up_limit'] or alert_info['is_down_limit']:
                key = (stock['code'], alert_info['is_up_limit'])
                if key not in self.alerted_stocks:
                    message = format_alert_message(stock, alert_info)
                    alert_messages.append(message)
                    self.alerted_stocks.add(key)

                    # 调用回调
                    if self.callback:
                        self.callback(stock, alert_info)

            # 接近涨跌停警告
            elif alert_info['distance_to_up'] is not None:
                up_distance_pct = (alert_info['distance_to_up'] / stock['price']) * 100
                down_distance_pct = (alert_info['distance_to_down'] / stock['price']) * 100

                if up_distance_pct < 1.0 or down_distance_pct < 1.0:
                    message = format_alert_message(stock, alert_info)
                    if message:
                        alert_messages.append(message)

        return alert_messages

    def reset_alerted(self, code: Optional[str] = None):
        """
        重置预警状态

        Args:
            code: 股票代码，如果为None则重置所有
        """
        if code:
            self.alerted_stocks = {k for k in self.alerted_stocks if k[0] != code}
        else:
            self.alerted_stocks = set()

def log_alert(message: str):
    """记录预警日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    try:
        with open(ALERT_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"❌ 写入日志失败: {e}")

def monitor_stocks(symbols: List[str], interval: int = 60, max_checks: int = None):
    """
    监控股票（持续监控）

    Args:
        symbols: 监控股票代码列表
        interval: 检查间隔（秒）
        max_checks: 最大检查次数，None表示无限
    """
    watcher = AlertWatcher(symbols, callback=log_alert)

    check_count = 0

    print(f"🔔 开始监控 {len(symbols)} 只股票...")
    print(f"   检查间隔: {interval}秒")
    if max_checks:
        print(f"   最大检查次数: {max_checks}")
    else:
        print(f"   最大检查次数: 无限")
    print("=" * 60)

    try:
        while True:
            if max_checks and check_count >= max_checks:
                print(f"\n✅ 已完成 {check_count} 次检查，停止监控")
                break

            check_count += 1
            print(f"\n📊 [{check_count}] 检查时间: {datetime.now().strftime('%H:%M:%S')}")

            alerts = watcher.check()

            if alerts:
                print(f"\n🚨 触发预警 ({len(alerts)}条):")
                for alert in alerts:
                    print(f"  {alert}")
                    log_alert(alert)
            else:
                print("  ✅ 无预警")

            if max_checks and check_count >= max_checks:
                break

            # 等待下一次检查
            if not max_checks or check_count < max_checks:
                time_module.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n\n⏸️  监控已停止（用户中断）")
    except Exception as e:
        print(f"\n\n❌ 监控出错: {e}")
