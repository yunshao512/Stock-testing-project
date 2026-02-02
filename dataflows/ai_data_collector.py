#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
半年数据扩展 + A股多板块采集系统
模拟深证、沪证、创业板、科创板数据
"""

import sys
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Set
import statistics


class AIDataCollector:
    """A股多板块数据采集器（模拟版）"""

    def __init__(self):
        print("✅ A股多板块数据采集器初始化完成")
        
        # 板块定义
        self.boards = {
            '深证': {
                'code_prefix': '00',
                'market_cap_range': (10, 300),  # 10-300亿
                'industries': ['科技', '消费', '医疗', '新能源', '芯片']
            },
            '沪证': {
                'code_prefix': '6',
                'market_cap_range': (20, 500),  # 20-500亿
                'industries': ['金融', '科技', '医药', '制造', '消费']
            },
            '创业板': {
                'code_prefix': '3',
                'market_cap_range': (5, 100),  # 5-100亿
                'industries': ['科技', '新能源', '新材料', '高端制造']
            },
            '科创板': {
                'code_prefix': '688',
                'market_cap_range': (10, 200),  # 10-200亿
                'industries': ['芯片', '生物', '医药', '人工智能']
            }
        }

        # 房地产产业链行业（需要排除）
        self.realestate_industries = ['房地产', '建筑', '建材', '物业', '家居', '钢铁', '水泥', '玻璃']
        
        # ST股票
        self.st_stocks = set()

    def generate_board_stocks(self, board_name: str, count: int = 200) -> List[Dict]:
        """生成指定板块的股票数据"""
        if board_name not in self.boards:
            print(f"  ❌ 未知板块: {board_name}")
            return []

        board_info = self.boards[board_name]
        stocks = []

        for i in range(count):
            # 生成股票代码
            code_prefix = board_info['code_prefix']
            code = f"{code_prefix}{random.randint(100000, 999999):06d}"

            # 生成市值
            market_cap_min, market_cap_max = board_info['market_cap_range']
            market_cap = random.uniform(market_cap_min, market_cap_max)

            # 选择行业
            industry = random.choice(board_info['industries'])

            # 避免ST
            if 'ST' in code:
                continue

            # 避免房地产
            if industry in self.realestate_industries:
                industry = random.choice([ind for ind in board_info['industries'] 
                                       if ind not in self.realestate_industries])

            # 生成股票名称
            name_parts = [
                ['科技', '智能', '新能源', '芯片', '生物', '医药', '消费', '制造', '网络'],
                ['股份', '集团', '科技', '控股', '动力', '能源', '材料', '电子', '工业']
                ['中', '华', '国', '东', '西', '南', '北', '星', '天', '地', '人']
            ]
            name = ''.join(random.choice(part) for part in name_parts)

            # 生成财务数据
            profit_growth = random.choice([-0.1, -0.05, 0.05, 0.1, 0.15, 0.2, 0.3])
            is_loss_3years = random.random() < 0.1  # 10%概率连续亏损
            is_bubble = market_cap > 150 and random.random() < 0.15  # 大市值+随机泡沫
            is_bad_rating = random.random() < 0.1  # 10%概率风评不好

            stocks.append({
                'symbol': code,
                'name': name,
                'board': board_name,
                'market_cap': round(market_cap, 2),
                'industry': industry,
                'profit_growth': profit_growth,
                'is_loss_3years': is_loss_3years,
                'is_bubble': is_bubble,
                'is_bad_rating': is_bad_rating
            })

            # 记录ST股票
            if 'ST' in code:
                self.st_stocks.add(code)

        print(f"  ✅ 生成 {len(stocks)} 只{board_name}股票")
        return stocks

    def collect_all_boards(self) -> Dict[str, List[Dict]]:
        """采集所有板块数据"""
        all_stocks = {}
        
        print(f"\n📊 [1/4] 开始采集A股多板块数据...")
        
        for board_name in self.boards.keys():
            print(f"  正在采集{board_name}...")
            stocks = self.generate_board_stocks(board_name, count=200)
            all_stocks[board_name] = stocks

        return all_stocks

    def get_half_year_history(self, symbol: str, days: int = 180) -> List[Dict]:
        """获取半年历史数据（6个月，约120个交易日）"""
        # 根据股票代码确定特征
        if symbol.startswith('6'):
            base_price = random.uniform(20, 100)
        elif symbol.startswith('3'):
            base_price = random.uniform(10, 50)
        elif symbol.startswith('0'):
            base_price = random.uniform(10, 50)
        else:
            base_price = random.uniform(10, 100)

        # 生成趋势
        if random.random() > 0.4:
            trend = 0.002  # 温和上涨
        elif random.random() < 0.3:
            trend = -0.001  # 小幅下跌
        else:
            trend = random.uniform(-0.0005, 0.002)  # 随机

        candles = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')

            # 添加趋势和波动
            price_change = base_price * trend * (1 + random.uniform(-0.5, 1.5))
            open_price = base_price * (1 + random.uniform(-0.02, 0.02))
            close_price = open_price + price_change
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.01))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.01))
            volume = random.randint(5000000, 100000000)

            candles.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'amount': round(volume * close_price, 2)
            })

            base_price = close_price

        return candles


def test_collector():
    """测试数据采集器"""
    print("="*80)
    print("🧪 测试A股多板块数据采集")
    print("="*80)
    print()

    collector = AIDataCollector()

    # 1. 采集所有板块数据
    all_stocks = collector.collect_all_boards()

    # 统计
    print(f"\n📊 [2/4] 数据统计:")
    print(f"  深证: {len(all_stocks['深证'])}只")
    print(f"  沪证: {len(all_stocks['沪证'])}只")
    print(f"  创业板: {len(all_stocks['创业板'])}只")
    print(f"  科创板: {len(all_stocks['科创板'])}只")
    print(f"  总计: {sum(len(s) for s in all_stocks.values())}只")

    # 2. 获取历史数据（测试一只股票）
    print(f"\n📊 [3/4] 测试获取半年历史数据...")
    test_symbol = random.choice(all_stocks['沪证'])['symbol']
    history = collector.get_half_year_history(test_symbol, days=60)

    if history:
        print(f"  ✅ 成功获取 {len(history)} 条历史数据")
        print(f"  日期范围: {history[0]['date']} 至 {history[-1]['date']}")
        print(f"  最新收盘: ¥{history[-1]['close']:.2f}")

        # 显示最近10天
        print(f"\n  最近10天数据:")
        for i, candle in enumerate(history[-10:], 1):
            print(f"    {candle['date']}: ¥{candle['close']:.2f}")

    # 4. 完成
    print(f"\n📊 [4/4] 采集完成")

    return all_stocks


if __name__ == "__main__":
    test_collector()
