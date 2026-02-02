#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
研报数据接入模块
模拟研报数据获取
"""

import random
from typing import List, Dict
from datetime import datetime, timedelta


class ReportProvider:
    """研报数据提供者（模拟）"""

    def __init__(self):
        self.reports = [
            {
                'title': '2024年度投资策略报告',
                'institution': '中信证券',
                'rating': '增持',
                'target_price': 0.0,
                'date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            },
            {
                'title': '科技行业深度分析',
                'institution': '华泰证券',
                'rating': '买入',
                'target_price': 0.0,
                'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            },
            {
                'title': '5G产业链投资机会',
                'institution': '国泰君安',
                'rating': '观望',
                'target_price': 0.0,
                'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            }
        ]
        print(f"✅ 研报数据提供者初始化完成，共 {len(self.reports)} 份研报")

    def get_reports(self, symbol: str) -> List[Dict]:
        """
        获取研报（模拟）

        Args:
            symbol: 股票代码

        Returns:
            研报列表
        """
        # 根据股票代码筛选相关研报
        if symbol.startswith('6'):
            filtered_reports = [r for r in self.reports if '科技' in r['title'] or '策略' in r['title']]
        else:
            filtered_reports = self.reports

        # 添加目标价格（模拟）
        for report in filtered_reports:
            report['target_price'] = random.uniform(100, 200) * random.uniform(0.8, 1.2)
            report['symbol'] = symbol

        return filtered_reports

    def analyze_sentiment(self, reports: List[Dict]) -> Dict:
        """
        分析研报情绪

        Args:
            reports: 研报列表

        Returns:
            情绪分析结果
        """
        buy_count = sum(1 for r in reports if r['rating'] == '买入')
        hold_count = sum(1 for r in reports if r['rating'] == '观望')
        sell_count = sum(1 for r in reports if r['rating'] == '减持')

        if not reports:
            return {
                'sentiment': '无研报',
                'buy_count': 0,
                'hold_count': 0,
                'sell_count': 0
            }

        total = len(reports)
        sentiment_score = (buy_count - sell_count) / total if total > 0 else 0

        if sentiment_score > 0.3:
            sentiment = '强烈看多'
        elif sentiment_score > 0.1:
            sentiment = '偏多'
        elif sentiment_score < -0.3:
            sentiment = '强烈看空'
        elif sentiment_score < -0.1:
            sentiment = '偏空'
        else:
            sentiment = '中性'

        return {
            'sentiment': sentiment,
            'buy_count': buy_count,
            'hold_count': hold_count,
            'sell_count': sell_count,
            'sentiment_score': sentiment_score
        }


def test_reports():
    """测试研报数据"""
    print("="*80)
    print("🧪 测试研报数据获取")
    print("="*80)

    provider = ReportProvider()

    print("\n📊 测试获取研报:")
    reports = provider.get_reports('000063')

    print(f"\n获取到 {len(reports)} 份相关研报:\n")
    for i, report in enumerate(reports, 1):
        print(f"  {i}. {report['title']}")
        print(f"     机构: {report['institution']}")
        print(f"     评级: {report['rating']}")
        print(f"     日期: {report['date']}\n")

    print("📊 研报情绪分析:")
    sentiment = provider.analyze_sentiment(reports)

    print(f"  情绪: {sentiment['sentiment']}")
    print(f"  买入: {sentiment['buy_count']}份")
    print(f"  观望: {sentiment['hold_count']}份")
    print(f"  减持: {sentiment['sell_count']}份")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_reports()
