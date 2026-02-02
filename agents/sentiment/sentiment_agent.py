#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
情绪分析智能体
负责新闻情绪、事件影响、市场热度分析
"""

import sys
import os
from typing import Dict, List
from dataclasses import dataclass, field

# 添加项目根目录到路径
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from dataflows.news_data import get_news_provider


@dataclass
class SentimentAnalysisResult:
    """情绪分析结果"""
    news_sentiment: str = ""  # 新闻情绪（正面/负面/中性）
    event_impact: str = ""  # 事件影响（利好/利空/无影响）
    market_heat: str = ""  # 市场热度（高/中/低）
    sentiment_score: float = 0.0  # 情绪评分 -1到1
    social_mentions: int = 0  # 社交媒体提及次数
    score: float = 0.0  # 评分 0-1
    signals: List[str] = field(default_factory=list)  # 信号列表


class SentimentAnalysisAgent:
    """情绪分析智能体"""

    def __init__(self, debug: bool = False):
        self.debug = debug

    def analyze(self, symbol: str, days: int = 30) -> SentimentAnalysisResult:
        """
        执行情绪分析

        使用真实新闻数据源（新浪财经、东方财富），如果不可用则使用模拟数据

        Args:
            symbol: 股票代码
            days: 分析天数

        Returns:
            SentimentAnalysisResult: 分析结果
        """
        result = SentimentAnalysisResult()

        # 获取新闻数据
        provider = get_news_provider()
        news_list = provider.fetch_news(symbol, count=10, use_cache=True)

        # 分析新闻情绪
        sentiment = provider.analyze_sentiment(news_list)

        # 填充数据
        result.news_sentiment = sentiment['sentiment']
        result.sentiment_score = sentiment['score']
        result.social_mentions = len(news_list)

        # 判断事件影响
        if sentiment['sentiment'] == '正面':
            result.event_impact = "利好"
        elif sentiment['sentiment'] == '负面':
            result.event_impact = "利空"
        else:
            result.event_impact = "无影响"

        # 判断市场热度
        if len(news_list) > 20:
            result.market_heat = "高"
        elif len(news_list) > 10:
            result.market_heat = "中"
        else:
            result.market_heat = "低"

        # 计算评分
        result.score = self._calculate_score(result)

        # 生成信号
        result.signals = self._generate_signals(result)

        if self.debug:
            source = news_list[0].get('source', 'N/A') if news_list else 'N/A'
            print(f"  ✅ 情绪分析完成，评分: {result.score*100:.0f}% (来源: {source})")
            print(f"     新闻情绪: {result.news_sentiment}, 市场热度: {result.market_heat}")

        return result

    def _calculate_score(self, result: SentimentAnalysisResult) -> float:
        """计算情绪评分"""
        # 将 -1 到 1 的情绪评分映射到 0 到 1
        score = (result.sentiment_score + 1) / 2

        # 根据市场热度调整
        if result.market_heat == "高":
            score *= 1.1
        elif result.market_heat == "低":
            score *= 0.9

        # 限制在0-1之间
        score = max(0.0, min(1.0, score))

        return score

    def _generate_signals(self, result: SentimentAnalysisResult) -> List[str]:
        """生成情绪信号"""
        signals = []

        if result.sentiment_score > 0.5:
            signals.append("情绪强烈看多")
        elif result.sentiment_score > 0.2:
            signals.append("情绪偏多")
        elif result.sentiment_score < -0.5:
            signals.append("情绪强烈看空")
        elif result.sentiment_score < -0.2:
            signals.append("情绪偏空")
        else:
            signals.append("情绪中性")

        if result.event_impact == "利好":
            signals.append("有利好消息")
        elif result.event_impact == "利空":
            signals.append("有利空消息")

        return signals
