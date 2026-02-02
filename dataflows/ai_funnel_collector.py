#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A股多板块采集+漏斗筛选系统
深证、沪证、创业板、科创板 + 7重漏斗筛选
"""

import sys
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple
import statistics


class StockFilter:
    """股票漏斗筛选器"""

    def __init__(self):
        print("✅ 股票漏斗筛选器初始化完成")

        # 房地产产业链行业
        self.realestate_industries = {
            '房地产', '地产', '建筑', '建材', '水泥', '玻璃', '物业', '装饰', '厨卫',
            '家具', '地板', '门窗', '涂料', '钢铁', '冶金', '采掘', '煤炭', '电力', '水务',
            '燃气', '供热', '环保', '固废处理', '市政工程', '基础设施'
        }

        # ST股票关键词
        self.st_keywords = ['ST', '退', '停', '风险', '警告', '问询']

    def filter_by_market_cap(self, stocks: List[Dict], max_cap: float = 200) -> List[Dict]:
        """
        筛选1：市值小于2000亿
        """
        print(f"  [1/7] 市值筛选：<{max_cap}亿")
        filtered = [s for s in stocks if s['market_cap'] < max_cap]
        print(f"       通过: {len(filtered)}/{len(stocks)}")
        return filtered

    def filter_by_non_st(self, stocks: List[Dict]) -> List[Dict]:
        """
        筛选2：非ST股票
        """
        print(f"  [2/7] 去除ST股票")
        filtered = [s for s in stocks if not self._is_st_stock(s)]
        print(f"       通过: {len(filtered)}/{len(stocks)}")
        return filtered

    def filter_by_non_realestate(self, stocks: List[Dict]) -> List[Dict]:
        """
        筛选3：非房地产产业链
        """
        print(f"  [3/7] 去除房地产产业链")
        filtered = [s for s in stocks if s['industry'] not in self.realestate_industries]
        print(f"       通过: {len(filtered)}/{len(stocks)}")
        return filtered

    def filter_by_profit_growth(self, stocks: List[Dict]) -> List[Dict]:
        """
        筛选4：非连续亏损，有盈利能力
        """
        print(f"  [4/7] 盈利能力筛选")
        filtered = [s for s in stocks if not s['is_loss_3years'] and s['profit_growth'] > 0]
        print(f"       通过: {len(filtered)}/{len(stocks)}")
        return filtered

    def filter_by_good_rating(self, stocks: List[Dict]) -> List[Dict]:
        """
        筛选5：风评较好
        """
        print(f"  [5/7] 风评筛选")
        filtered = [s for s in stocks if not s['is_bad_rating']]
        print(f"       通过: {len(filtered)}/{len(stocks)}")
        return filtered

    def filter_by_no_bubble(self, stocks: List[Dict]) -> List[Dict]:
        """
        筛选6：无泡沫
        """
        print(f"  [6/7] 泡沫筛选")
        filtered = [s for s in stocks if not s['is_bubble']]
        print(f"       通过: {len(filtered)}/{len(stocks)}")
        return filtered

    def filter_by_score(self, stocks: List[Dict], min_score: float = 0.6) -> List[Dict]:
        """
        筛选7：综合评分（估值、财务、成长、技术）
        """
        print(f"  [7/7] 综合评分筛选: >{min_score}")
        # 假设每只股票有综合评分
        for stock in stocks:
            # 计算综合评分（模拟）
            val_score = random.uniform(0.3, 0.8) if not stock.get('is_bubble') else 0.2
            profit_score = random.uniform(0.3, 0.8) if stock.get('profit_growth', 0) > 0 else 0.2
            growth_score = random.uniform(0.3, 0.8) if not stock.get('is_loss_3years') else 0.2

            # 综合评分（权重：估值30%+财务30%+成长20%+技术20%）
            overall_score = val_score * 0.3 + profit_score * 0.3 + growth_score * 0.2 + random.uniform(0, 0.2)
            stock['score'] = min(1.0, overall_score)

        filtered = [s for s in stocks if s.get('score', 0) > min_score]
        print(f"       通过: {len(filtered)}/{len(stocks)}")
        return filtered

    def _is_st_stock(self, stock: Dict) -> bool:
        """判断是否为ST股票"""
        for keyword in self.st_keywords:
            if keyword in stock['symbol'] or keyword in stock['name']:
                return True
        return False

    def apply_funnel(self, stocks: List[Dict], target_count: int = 500) -> List[Dict]:
        """
        应用7重漏斗筛选
        """
        print(f"\n📊 开始7重漏斗筛选（目标：{target_count}只）")
        print(f"{'='*80}")

        step1 = self.filter_by_market_cap(stocks)
        step2 = self.filter_by_non_st(step1)
        step3 = self.filter_by_non_realestate(step2)
        step4 = self.filter_by_profit_growth(step3)
        step5 = self.filter_by_good_rating(step4)
        step6 = self.filter_by_no_bubble(step5)
        step7 = self.filter_by_score(step6)

        # 如果超过目标数量，取评分最高的
        if len(step7) > target_count:
            step7 = sorted(step7, key=lambda x: x.get('score', 0), reverse=True)[:target_count]

        print(f"\n✅ 漏斗筛选完成")
        print(f"  最终通过: {len(step7)}/{len(stocks)}只")
        print(f"  目标数量: {target_count}只")

        return step7


class MultiBoardCollector:
    """A股多板块采集器"""

    def __init__(self):
        print("✅ A股多板块采集器初始化完成")

        # 板块配置
        self.boards = {
            '深证': {
                'code_prefix': '00',
                'market_cap_range': (10, 300),  # 10-300亿
                'industries': ['科技', '消费', '医疗', '新能源', '制造', '医药']
            },
            '沪证': {
                'code_prefix': '6',
                'market_cap_range': (20, 500),  # 20-500亿
                'industries': ['金融', '科技', '医药', '制造', '消费', '能源']
            },
            '创业板': {
                'code_prefix': '3',
                'market_cap_range': (5, 100),  # 5-100亿
                'industries': ['科技', '新能源', '新材料', '生物', '医药', '高端制造']
            },
            '科创板': {
                'code_prefix': '688',
                'market_cap_range': (10, 200),  # 10-200亿
                'industries': ['芯片', '生物', '医药', '人工智能', '量子', '新材料']
            }
        }

        # 总板块数量
        self.total_stocks_per_board = 200  # 每个板块200只股票
        self.total_boards = len(self.boards)

    def collect_all_boards(self) -> Dict[str, List[Dict]]:
        """
        采集所有板块股票
        """
        print(f"\n📊 [1/4] 开始采集4个板块股票")
        print(f"  目标: 每个板块{self.total_stocks_per_board}只，共{self.total_boards * self.total_stocks_per_board}只")

        all_stocks = {}

        for board_name, board_config in self.boards.items():
            print(f"\n  正在采集{board_name}...")
            stocks = self._generate_board_stocks(board_name, board_config)
            all_stocks[board_name] = stocks

        # 汇总
        print(f"\n📊 采集汇总:")
        for board_name, stocks in all_stocks.items():
            print(f"  {board_name}: {len(stocks)}只")

        print(f"  总计: {sum(len(s) for s in all_stocks.values())}只")

        return all_stocks

    def _generate_board_stocks(self, board_name: str, config: Dict) -> List[Dict]:
        """生成单个板块的股票数据"""
        code_prefix = config['code_prefix']
        market_cap_range = config['market_cap_range']
        industries = config['industries']

        stocks = []
        for i in range(self.total_stocks_per_board):
            # 生成股票代码
            code = f"{code_prefix}{random.randint(100000, 999999):06d}"

            # 生成市值
            market_cap = random.uniform(market_cap_range[0], market_cap_range[1])

            # 选择行业
            industry = random.choice(industries)

            # 生成股票名称
            name_parts_list = [
                ['科技', '智能', '新能源', '芯片', '生物', '医药', '消费', '制造', '网络'],
                ['股份', '集团', '科技', '控股', '动力', '能源', '材料', '电子', '工业'],
                ['中', '华', '国', '东', '西', '南', '北', '星', '天', '地', '人']
            ]
            name = ''.join(random.choice(part) for part in name_parts_list)

            # 生成财务数据
            profit_growth = random.choice([-0.1, -0.05, 0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5])
            is_loss_3years = random.random() < 0.15  # 15%概率连续亏损

            # 判断泡沫
            is_bubble = market_cap > 100 and random.random() < 0.2  # 大市值+20%泡沫概率

            # 判断风评
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

        return stocks


def test_system():
    """测试多板块采集+漏斗筛选"""
    print("="*80)
    print("🧪 测试A股多板块采集+漏斗筛选")
    print("="*80)
    print()

    # 1. 采集所有板块
    collector = MultiBoardCollector()
    all_stocks = collector.collect_all_boards()

    # 2. 漏斗筛选
    print(f"\n📊 [2/4] 开始7重漏斗筛选")
    
    # 合并所有板块股票
    combined_stocks = []
    for board_name, stocks in all_stocks.items():
        combined_stocks.extend(stocks)

    print(f"  合并前: {len(combined_stocks)}只")

    # 应用漏斗筛选
    filter = StockFilter()
    filtered_stocks = filter.apply_funnel(combined_stocks, target_count=500)

    # 3. 输出结果
    print(f"\n📊 [3/4] 筛选结果")
    print(f"{'='*80}")
    print(f"  初始股票: {len(combined_stocks)}只")
    print(f"  最终通过: {len(filtered_stocks)}只")
    print(f"  筛选率: {len(filtered_stocks)/len(combined_stocks)*100:.1f}%")

    # 显示部分股票
    print(f"\n📊 [4/4] 部分股票示例:")
    print(f"{'='*80}")
    print(f"{'排名':<6} {'股票':<20} {'板块':<15} {'市值':<12} {'评分':<8}")
    print(f"{'-'*80}")

    for i, stock in enumerate(filtered_stocks[:20], 1):
        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        print(f"{rank_emoji:<6} {stock['symbol']:<20} {stock['board']:<15} {stock['market_cap']:>8.1f}亿 {stock.get('score', 0.5)*100:>5.0f}")

    print(f"\n✅ 测试完成")


if __name__ == "__main__":
    test_system()
