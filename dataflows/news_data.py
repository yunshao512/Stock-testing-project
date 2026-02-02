#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新闻数据获取模块
接入新闻API，用于情绪分析
"""

import sys
import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataflows import get_cache


class NewsDataProvider:
    """新闻数据提供者"""

    def __init__(self):
        self.cache = get_cache(cache_hours=2)  # 新闻数据缓存2小时
        self.sources = {}

        # 初始化数据源
        self._init_sources()

    def _init_sources(self):
        """初始化数据源"""
        # 新浪财经新闻API（免费）
        self.sources['sina'] = True
        print(f"✅ [新闻] 新浪财经API已配置")

        # 东方财富API（免费）
        self.sources['eastmoney'] = True
        print(f"✅ [新闻] 东方财富API已配置")

    def fetch_news(self, symbol: str, count: int = 10, use_cache: bool = True) -> List[Dict]:
        """
        获取新闻

        Args:
            symbol: 股票代码
            count: 新闻数量
            use_cache: 是否使用缓存

        Returns:
            新闻列表
        """
        # 尝试从缓存获取
        if use_cache:
            cached_data = self.cache.get('news', symbol=symbol, count=count)
            if cached_data:
                print(f"✅ [新闻] 使用缓存的新闻数据")
                return cached_data.get('news', [])

        # 尝试从各数据源获取
        all_news = []

        for source_name in self.sources.keys():
            try:
                news = self._fetch_from_source(source_name, symbol, count)
                if news:
                    all_news.extend(news)
                    # 只使用一个数据源
                    break
            except Exception as e:
                print(f"❌ [新闻] {source_name}获取失败: {e}")
                continue

        # 如果没有新闻，生成模拟数据
        if not all_news:
            all_news = self._get_mock_news(symbol)

        # 保存到缓存
        if all_news and use_cache:
            self.cache.set('news', {'news': all_news}, symbol=symbol, count=count)

        return all_news

    def _fetch_from_source(self, source_name: str, symbol: str, count: int) -> Optional[List[Dict]]:
        """从指定数据源获取新闻"""
        if source_name == 'sina':
            return self._fetch_from_sina(symbol, count)
        elif source_name == 'eastmoney':
            return self._fetch_from_eastmoney(symbol, count)
        return None

    def _fetch_from_sina(self, symbol: str, count: int) -> Optional[List[Dict]]:
        """从新浪财经获取新闻"""
        try:
            import requests

            # 新浪财经新闻API
            url = f"http://vip.stock.finance.sina.com.cn/corp/go.php/vFD_AllNewsStock/symbol/{symbol}/p/{count}.js"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://finance.sina.com.cn'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'

            # 解析JSONP响应
            text = response.text
            if text.startswith('var Data='):
                text = text[9:-2]  # 去掉前后缀

            data = json.loads(text)

            # 转换为统一格式
            news_list = []
            for item in data:
                news_list.append({
                    'title': item.get('title', ''),
                    'time': item.get('time', ''),
                    'url': item.get('url', ''),
                    'source': '新浪财经'
                })

            print(f"🌐 [新闻] 新浪财经获取 {len(news_list)} 条新闻")
            return news_list

        except Exception as e:
            print(f"❌ [新闻] 新浪财经获取失败: {e}")
            return None

    def _fetch_from_eastmoney(self, symbol: str, count: int) -> Optional[List[Dict]]:
        """从东方财富获取新闻"""
        try:
            import requests

            # 东方财富新闻API
            # 注意：需要根据实际情况调整URL
            url = f"http://data.eastmoney.com/NewsData/Notic/{symbol}.json"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://quote.eastmoney.com'
            }

            response = requests.get(url, headers=headers, timeout=10)

            data = response.json()

            # 转换为统一格式
            news_list = []
            for item in data.get('list', [])[:count]:
                news_list.append({
                    'title': item.get('title', ''),
                    'time': item.get('time', ''),
                    'url': item.get('url', ''),
                    'source': '东方财富'
                })

            print(f"🌐 [新闻] 东方财富获取 {len(news_list)} 条新闻")
            return news_list

        except Exception as e:
            print(f"❌ [新闻] 东方财富获取失败: {e}")
            return None

    def _get_mock_news(self, symbol: str) -> List[Dict]:
        """生成模拟新闻（备用方案）"""
        import random

        titles = [
            f"{symbol} 发布年度业绩预告，净利润同比增长20%",
            f"{symbol} 董事会通过重大资产重组方案",
            f"{symbol} 获得政府补贴5000万元",
            f"{symbol} 新产品研发取得重大突破",
            f"{symbol} 发布投资者关系活动记录",
        ]

        mock_news = []
        for i in range(5):
            mock_news.append({
                'title': random.choice(titles),
                'time': (datetime.now() - timedelta(days=random.randint(0, 3))).strftime('%Y-%m-%d %H:%M:%S'),
                'url': f'http://example.com/news/{symbol}_{i}',
                'source': '模拟数据'
            })

        print(f"🎭 [新闻] 生成 {len(mock_news)} 条模拟新闻")
        return mock_news

    def analyze_sentiment(self, news_list: List[Dict]) -> Dict:
        """
        分析新闻情绪

        Args:
            news_list: 新闻列表

        Returns:
            情绪分析结果
        """
        if not news_list:
            return {
                'sentiment': '中性',
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'score': 0.0
            }

        # 简化版情绪分析（基于关键词）
        positive_keywords = ['增长', '上涨', '盈利', '突破', '利好', '优秀', '推荐', '买入', '业绩']
        negative_keywords = ['下跌', '亏损', '风险', '利空', '减持', '卖出', '下滑', '预警']

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for news in news_list:
            title = news.get('title', '')

            has_positive = any(keyword in title for keyword in positive_keywords)
            has_negative = any(keyword in title for keyword in negative_keywords)

            if has_positive and not has_negative:
                positive_count += 1
            elif has_negative and not has_positive:
                negative_count += 1
            else:
                neutral_count += 1

        total = len(news_list)
        sentiment_score = (positive_count - negative_count) / total if total > 0 else 0.0

        # 判断整体情绪
        if sentiment_score > 0.2:
            sentiment = '正面'
        elif sentiment_score < -0.2:
            sentiment = '负面'
        else:
            sentiment = '中性'

        return {
            'sentiment': sentiment,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'score': sentiment_score
        }


# 单例模式
_news_provider_instance = None

def get_news_provider() -> NewsDataProvider:
    """获取新闻数据提供者实例（单例）"""
    global _news_provider_instance

    if _news_provider_instance is None:
        _news_provider_instance = NewsDataProvider()

    return _news_provider_instance


def test_news():
    """测试新闻数据获取"""
    print("="*80)
    print("🧪 测试新闻数据获取")
    print("="*80)

    provider = get_news_provider()

    print("\n📰 测试获取新闻:")
    news = provider.fetch_news('600519', count=5)

    print(f"\n获取到 {len(news)} 条新闻:\n")
    for i, item in enumerate(news, 1):
        print(f"  {i}. {item['title']}")
        print(f"     时间: {item['time']}")
        print(f"     来源: {item['source']}\n")

    print("🎭 测试情绪分析:")
    sentiment = provider.analyze_sentiment(news)
    print(f"  情绪: {sentiment['sentiment']}")
    print(f"  正面: {sentiment['positive_count']}")
    print(f"  负面: {sentiment['negative_count']}")
    print(f"  中性: {sentiment['neutral_count']}")
    print(f"  评分: {sentiment['score']:.2f}")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_news()
