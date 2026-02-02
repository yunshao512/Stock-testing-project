#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
评分系统模块
综合评分和动态权重管理
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ScoreWeights:
    """评分权重配置"""
    trend: float = 0.25      # 趋势权重
    position: float = 0.20    # 位置权重
    pattern: float = 0.20     # 形态权重
    volume_price: float = 0.15 # 量价权重
    indicator: float = 0.20   # 指标权重

    def __post_init__(self):
        """验证权重总和为1"""
        total = self.trend + self.position + self.pattern + self.volume_price + self.indicator
        if abs(total - 1.0) > 0.01:
            # 归一化
            self.trend /= total
            self.position /= total
            self.pattern /= total
            self.volume_price /= total
            self.indicator /= total


@dataclass
class TechnicalScoreResult:
    """技术分析评分结果"""
    trend_score: float = 0.0      # 趋势评分
    position_score: float = 0.0   # 位置评分
    pattern_score: float = 0.0     # 形态评分
    volume_price_score: float = 0.0 # 量价评分
    indicator_score: float = 0.0   # 指标评分
    overall_score: float = 0.0     # 综合评分
    weights: ScoreWeights = field(default_factory=ScoreWeights)
    details: Dict = field(default_factory=dict)  # 详细评分


class ScoringSystem:
    """评分系统"""

    def __init__(self, weights: Optional[ScoreWeights] = None):
        """
        初始化评分系统

        Args:
            weights: 评分权重配置，如果为None使用默认权重
        """
        self.weights = weights or ScoreWeights()
        print(f"✅ 评分系统初始化完成")
        print(f"   权重配置: 趋势{self.weights.trend:.0%}, 位置{self.weights.position:.0%}, "
              f"形态{self.weights.pattern:.0%}, 量价{self.weights.volume_price:.0%}, "
              f"指标{self.weights.indicator:.0%}")

    def calculate_technical_score(self,
                                 trend: str,
                                 position: str,
                                 patterns: List[str],
                                 volume_price: str,
                                 indicators: Dict) -> TechnicalScoreResult:
        """
        计算技术分析综合评分

        Args:
            trend: 趋势（上升/下降/横盘）
            position: 位置（高位/中位/低位）
            patterns: 形态列表
            volume_price: 量价关系
            indicators: 技术指标

        Returns:
            TechnicalScoreResult: 评分结果
        """
        result = TechnicalScoreResult()
        result.weights = self.weights

        # 1. 趋势评分
        result.trend_score = self._score_trend(trend)

        # 2. 位置评分
        result.position_score = self._score_position(position)

        # 3. 形态评分
        result.pattern_score, pattern_details = self._score_patterns(patterns)
        result.details['patterns'] = pattern_details

        # 4. 量价评分
        result.volume_price_score = self._score_volume_price(volume_price)

        # 5. 指标评分
        result.indicator_score = self._score_indicators(indicators)

        # 6. 综合评分（加权平均）
        result.overall_score = (
            result.trend_score * self.weights.trend +
            result.position_score * self.weights.position +
            result.pattern_score * self.weights.pattern +
            result.volume_price_score * self.weights.volume_price +
            result.indicator_score * self.weights.indicator
        )

        # 限制在0-1之间
        result.overall_score = max(0.0, min(1.0, result.overall_score))

        return result

    def _score_trend(self, trend: str) -> float:
        """趋势评分"""
        if trend == "上升":
            return 0.85
        elif trend == "下降":
            return 0.15
        elif trend == "横盘":
            return 0.50
        else:
            return 0.0

    def _score_position(self, position: str) -> float:
        """位置评分"""
        if position == "低位":
            return 0.85
        elif position == "中位":
            return 0.50
        elif position == "高位":
            return 0.15
        else:
            return 0.0

    def _score_patterns(self, patterns: List[str]) -> tuple:
        """
        形态评分

        Returns:
            (score, details): 评分和详细分数
        """
        if not patterns:
            return 0.0, {}

        # 形态质量评分
        quality_scores = {
            "头肩顶": 0.90,
            "头肩底": 0.90,
            "双顶": 0.85,
            "双底": 0.85,
            "上升三角形": 0.80,
            "下降三角形": 0.80,
            "对称三角形": 0.75,
            "上升旗形": 0.80,
            "下降旗形": 0.80,
            "上升楔形": 0.70,
            "下降楔形": 0.70,
            "底部横盘": 0.75,
            "均线多头": 0.70,
            "均线空头": 0.30,
            "阳线吞没": 0.75,
            "阴线吞没": 0.25,
            "MA金叉": 0.70,
            "MA死叉": 0.30,
        }

        total_score = 0.0
        details = {}

        for pattern in patterns:
            score = quality_scores.get(pattern, 0.5)
            total_score += score
            details[pattern] = score

        # 平均分
        avg_score = total_score / len(patterns)

        # 如果有强烈看涨形态，额外加分
        bullish_patterns = ["头肩底", "双底", "底部横盘", "均线多头", "阳线吞没", "MA金叉"]
        if any(p in patterns for p in bullish_patterns):
            avg_score = min(1.0, avg_score + 0.1)

        # 如果有强烈看跌形态，额外减分
        bearish_patterns = ["头肩顶", "双顶", "均线空头", "阴线吞没", "MA死叉"]
        if any(p in patterns for p in bearish_patterns):
            avg_score = max(0.0, avg_score - 0.1)

        return avg_score, details

    def _score_volume_price(self, volume_price: str) -> float:
        """量价评分"""
        if "放量上涨" in volume_price:
            return 0.90
        elif "缩量下跌" in volume_price:
            return 0.80
        elif "放量下跌" in volume_price:
            return 0.15
        elif "缩量上涨" in volume_price:
            return 0.60
        else:  # 量价正常
            return 0.50

    def _score_indicators(self, indicators: Dict) -> float:
        """指标评分"""
        score = 0.5

        # RSI指标
        rsi = indicators.get('RSI', 50)
        if rsi < 30:  # 超卖
            score += 0.25
        elif rsi < 40:  # 偏低
            score += 0.10
        elif rsi > 70:  # 超买
            score -= 0.25
        elif rsi > 60:  # 偏高
            score -= 0.10

        # MACD指标
        macd = indicators.get('MACD', 0)
        if macd > 0:
            score += 0.15
        elif macd < 0:
            score -= 0.15

        # 限制在0-1之间
        score = max(0.0, min(1.0, score))

        return score

    def adjust_weights(self, market_condition: str):
        """
        根据市场条件调整权重

        Args:
            market_condition: 市场条件（trending/ranging/volatile）
        """
        if market_condition == "trending":
            # 趋势市场：趋势和位置权重更高
            self.weights.trend = 0.35
            self.weights.position = 0.25
            self.weights.pattern = 0.15
            self.weights.volume_price = 0.10
            self.weights.indicator = 0.15
        elif market_condition == "ranging":
            # 震荡市场：形态和量价权重更高
            self.weights.trend = 0.15
            self.weights.position = 0.15
            self.weights.pattern = 0.35
            self.weights.volume_price = 0.25
            self.weights.indicator = 0.10
        elif market_condition == "volatile":
            # 高波动市场：指标和量价权重更高
            self.weights.trend = 0.20
            self.weights.position = 0.20
            self.weights.pattern = 0.15
            self.weights.volume_price = 0.25
            self.weights.indicator = 0.20

        print(f"🔧 权重已根据市场条件调整: {market_condition}")

    def get_score_summary(self, result: TechnicalScoreResult) -> str:
        """获取评分摘要"""
        summary = f"""
技术分析评分摘要
{'='*60}
综合评分: {result.overall_score*100:.1f}%

各维度评分:
  • 趋势: {result.trend_score*100:.1f}% (权重: {result.weights.trend:.0%})
  • 位置: {result.position_score*100:.1f}% (权重: {result.weights.position:.0%})
  • 形态: {result.pattern_score*100:.1f}% (权重: {result.weights.pattern:.0%})
  • 量价: {result.volume_price_score*100:.1f}% (权重: {result.weights.volume_price:.0%})
  • 指标: {result.indicator_score*100:.1f}% (权重: {result.weights.indicator:.0%})
{'='*60}
"""
        return summary


def test_scoring():
    """测试评分系统"""
    print("="*80)
    print("🧪 测试评分系统")
    print("="*80)

    scorer = ScoringSystem()

    # 测试1：上升趋势
    print("\n📊 测试1: 上升趋势，低位，看涨形态")
    result = scorer.calculate_technical_score(
        trend="上升",
        position="低位",
        patterns=["底部横盘", "均线多头", "MA金叉"],
        volume_price="放量上涨",
        indicators={"RSI": 25, "MACD": 10}
    )

    print(scorer.get_score_summary(result))

    # 测试2：下降趋势
    print("\n📊 测试2: 下降趋势，高位，看跌形态")
    result = scorer.calculate_technical_score(
        trend="下降",
        position="高位",
        patterns=["头肩顶", "均线空头", "MA死叉"],
        volume_price="放量下跌",
        indicators={"RSI": 75, "MACD": -10}
    )

    print(scorer.get_score_summary(result))

    # 测试3：动态权重调整
    print("\n🔧 测试3: 动态权重调整")
    scorer.adjust_weights("trending")

    result = scorer.calculate_technical_score(
        trend="上升",
        position="低位",
        patterns=["底部横盘"],
        volume_price="放量上涨",
        indicators={"RSI": 30, "MACD": 5}
    )

    print(scorer.get_score_summary(result))

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_scoring()
