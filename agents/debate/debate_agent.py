#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
辩论智能体（多空辩论）
负责看涨看跌辩论，平衡各方观点
"""

from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class DebateResult:
    """辩论结果"""
    bull_score: float = 0.0  # 看涨得分
    bear_score: float = 0.0  # 看跌得分
    bull_arguments: List[str] = field(default_factory=list)  # 看涨理由
    bear_arguments: List[str] = field(default_factory=list)  # 看跌理由
    consensus: str = ""  # 共识（看多/看空/中性）
    score: float = 0.0  # 评分 0-1
    signals: List[str] = field(default_factory=list)  # 信号列表


class DebateAgent:
    """辩论智能体"""

    def __init__(self, debug: bool = False):
        self.debug = debug

    def debate(self, technical_result, fundamental_result, sentiment_result) -> DebateResult:
        """
        执行多空辩论

        Args:
            technical_result: 技术分析结果
            fundamental_result: 基本面分析结果
            sentiment_result: 情绪分析结果

        Returns:
            DebateResult: 辩论结果
        """
        result = DebateResult()

        # 收集看涨论据
        result.bull_arguments = self._collect_bull_arguments(
            technical_result,
            fundamental_result,
            sentiment_result
        )

        # 收集看跌论据
        result.bear_arguments = self._collect_bear_arguments(
            technical_result,
            fundamental_result,
            sentiment_result
        )

        # 计算看涨得分
        result.bull_score = self._calculate_bull_score(
            technical_result.score,
            fundamental_result.score,
            sentiment_result.score
        )

        # 计算看跌得分
        result.bear_score = self._calculate_bear_score(
            technical_result.score,
            fundamental_result.score,
            sentiment_result.score
        )

        # 达成共识
        result.consensus = self._reach_consensus(result.bull_score, result.bear_score)

        # 计算评分
        result.score = result.bull_score / (result.bull_score + result.bear_score)

        # 生成信号
        result.signals = self._generate_signals(result)

        if self.debug:
            print(f"  ✅ 辩论完成，看涨: {result.bull_score*100:.0f}%, 看跌: {result.bear_score*100:.0f}%")
            print(f"     共识: {result.consensus}")

        return result

    def _collect_bull_arguments(self, technical_result, fundamental_result, sentiment_result) -> List[str]:
        """收集看涨论据"""
        arguments = []

        # 技术面
        if technical_result.trend == "上升":
            arguments.append(f"技术面呈{technical_result.trend}趋势")
        if technical_result.position == "低位":
            arguments.append(f"股价处于{technical_result.position}")

        # 基本面
        if fundamental_result.valuation == "低估":
            arguments.append("估值偏低，安全边际高")
        if fundamental_result.financial_health in ["优秀", "良好"]:
            arguments.append(f"财务状况{fundamental_result.financial_health}")

        # 情绪面
        if sentiment_result.news_sentiment == "正面":
            arguments.append("新闻面偏正面")
        if sentiment_result.event_impact == "利好":
            arguments.append("有利好消息刺激")

        return arguments

    def _collect_bear_arguments(self, technical_result, fundamental_result, sentiment_result) -> List[str]:
        """收集看跌论据"""
        arguments = []

        # 技术面
        if technical_result.trend == "下降":
            arguments.append(f"技术面呈{technical_result.trend}趋势")
        if technical_result.position == "高位":
            arguments.append(f"股价处于{technical_result.position}")

        # 基本面
        if fundamental_result.valuation == "高估":
            arguments.append("估值偏高，存在泡沫")
        if fundamental_result.financial_health == "一般":
            arguments.append("财务状况一般")

        # 情绪面
        if sentiment_result.news_sentiment == "负面":
            arguments.append("新闻面偏负面")
        if sentiment_result.event_impact == "利空":
            arguments.append("有利空消息压制")

        return arguments

    def _calculate_bull_score(self, technical_score: float, fundamental_score: float, sentiment_score: float) -> float:
        """计算看涨得分"""
        # 技术面权重 40%，基本面 30%，情绪面 30%
        score = (
            technical_score * 0.4 +
            fundamental_score * 0.3 +
            sentiment_score * 0.3
        )

        return score

    def _calculate_bear_score(self, technical_score: float, fundamental_score: float, sentiment_score: float) -> float:
        """计算看跌得分"""
        # 看跌得分与看涨得分相反
        bull_score = self._calculate_bull_score(technical_score, fundamental_score, sentiment_score)
        return 1.0 - bull_score

    def _reach_consensus(self, bull_score: float, bear_score: float) -> str:
        """达成共识"""
        diff = abs(bull_score - bear_score)

        if diff < 0.1:
            return "中性"
        elif bull_score > bear_score:
            return "看多"
        else:
            return "看空"

    def _generate_signals(self, result: DebateResult) -> List[str]:
        """生成辩论信号"""
        signals = []

        if result.consensus == "看多":
            signals.append("多方占优")
        elif result.consensus == "看空":
            signals.append("空方占优")
        else:
            signals.append("多空平衡")

        return signals
