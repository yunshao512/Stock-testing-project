#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
诊断系统模块
综合诊断报告生成
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    VERY_LOW = "极低风险"
    LOW = "低风险"
    MEDIUM = "中等风险"
    HIGH = "高风险"
    VERY_HIGH = "极高风险"


class OpportunityLevel(Enum):
    """机会等级"""
    EXCELLENT = "极佳机会"
    GOOD = "较好机会"
    MODERATE = "一般机会"
    POOR = "较差机会"
    VERY_POOR = "极差机会"


@dataclass
class DiagnosisResult:
    """诊断结果"""
    risk_level: str = "未知"
    opportunity_level: str = "未知"
    trend_health: str = ""
    position_health: str = ""
    pattern_health: str = ""
    overall_health: str = ""
    risk_factors: List[str] = field(default_factory=list)
    opportunity_factors: List[str] = field(default_factory=list)
    recommendation: str = ""
    diagnosis_report: str = ""


class DiagnosisSystem:
    """诊断系统"""

    def __init__(self):
        print(f"✅ 诊断系统初始化完成")

    def diagnose(self,
                technical_result,
                fundamental_result,
                sentiment_result) -> DiagnosisResult:
        """
        综合诊断

        Args:
            technical_result: 技术分析结果
            fundamental_result: 基本面分析结果
            sentiment_result: 情绪分析结果

        Returns:
            DiagnosisResult: 诊断结果
        """
        result = DiagnosisResult()

        # 1. 趋势健康度
        result.trend_health = self._diagnose_trend(technical_result.trend)

        # 2. 位置健康度
        result.position_health = self._diagnose_position(technical_result.position)

        # 3. 形态健康度
        result.pattern_health = self._diagnose_patterns(technical_result.patterns)

        # 4. 风险等级
        result.risk_level, result.risk_factors = self._assess_risk(
            technical_result,
            fundamental_result,
            sentiment_result
        )

        # 5. 机会等级
        result.opportunity_level, result.opportunity_factors = self._assess_opportunity(
            technical_result,
            fundamental_result,
            sentiment_result
        )

        # 6. 整体健康度
        result.overall_health = self._assess_overall_health(
            result.trend_health,
            result.position_health,
            result.pattern_health
        )

        # 7. 生成建议
        result.recommendation = self._generate_recommendation(
            result.risk_level,
            result.opportunity_level,
            result.overall_health
        )

        # 8. 生成诊断报告
        result.diagnosis_report = self._generate_diagnosis_report(result)

        return result

    def _diagnose_trend(self, trend: str) -> str:
        """诊断趋势健康度"""
        if trend == "上升":
            return "健康（上升趋势）"
        elif trend == "下降":
            return "不健康（下降趋势）"
        elif trend == "横盘":
            return "一般（横盘整理）"
        else:
            return "未知"

    def _diagnose_position(self, position: str) -> str:
        """诊断位置健康度"""
        if position == "低位":
            return "安全（低位）"
        elif position == "中位":
            return "一般（中位）"
        elif position == "高位":
            return "风险（高位）"
        else:
            return "未知"

    def _diagnose_patterns(self, patterns: List[str]) -> str:
        """诊断形态健康度"""
        if not patterns:
            return "一般（无明显形态）"

        # 看涨形态
        bullish_patterns = ["头肩底", "双底", "底部横盘", "均线多头", "阳线吞没", "MA金叉",
                          "上升三角形", "上升旗形"]

        # 看跌形态
        bearish_patterns = ["头肩顶", "双顶", "均线空头", "阴线吞没", "MA死叉",
                          "下降三角形", "下降旗形"]

        bullish_count = sum(1 for p in patterns if p in bullish_patterns)
        bearish_count = sum(1 for p in patterns if p in bearish_patterns)

        if bullish_count > bearish_count:
            return "健康（看涨形态占优）"
        elif bearish_count > bullish_count:
            return "不健康（看跌形态占优）"
        else:
            return "一般（形态中性）"

    def _assess_risk(self,
                     technical_result,
                     fundamental_result,
                     sentiment_result) -> tuple:
        """
        评估风险等级

        Returns:
            (risk_level, risk_factors): 风险等级和风险因素
        """
        risk_score = 0
        risk_factors = []

        # 技术面风险
        if technical_result.trend == "下降":
            risk_score += 2
            risk_factors.append("技术面呈下降趋势")
        if technical_result.position == "高位":
            risk_score += 2
            risk_factors.append("股价处于高位")

        # 基本面风险
        if fundamental_result.valuation == "高估":
            risk_score += 2
            risk_factors.append("估值偏高")
        if fundamental_result.financial_health == "一般":
            risk_score += 1
            risk_factors.append("财务状况一般")

        # 情绪面风险
        if sentiment_result.news_sentiment == "负面":
            risk_score += 1
            risk_factors.append("新闻情绪负面")

        # 如果没有风险因素，添加提示
        if not risk_factors:
            risk_factors.append("无明显风险因素")

        # 确定风险等级
        if risk_score >= 5:
            risk_level = RiskLevel.VERY_HIGH.value
        elif risk_score >= 4:
            risk_level = RiskLevel.HIGH.value
        elif risk_score >= 3:
            risk_level = RiskLevel.MEDIUM.value
        elif risk_score >= 1:
            risk_level = RiskLevel.LOW.value
        else:
            risk_level = RiskLevel.VERY_LOW.value

        return risk_level, risk_factors

    def _assess_opportunity(self,
                            technical_result,
                            fundamental_result,
                            sentiment_result) -> tuple:
        """
        评估机会等级

        Returns:
            (opportunity_level, opportunity_factors): 机会等级和机会因素
        """
        opportunity_score = 0
        opportunity_factors = []

        # 技术面机会
        if technical_result.trend == "上升":
            opportunity_score += 2
            opportunity_factors.append("技术面呈上升趋势")
        if technical_result.position == "低位":
            opportunity_score += 2
            opportunity_factors.append("股价处于低位")

        # 基本面机会
        if fundamental_result.valuation == "低估":
            opportunity_score += 2
            opportunity_factors.append("估值偏低")
        if fundamental_result.financial_health == "优秀":
            opportunity_score += 1
            opportunity_factors.append("财务状况优秀")

        # 情绪面机会
        if sentiment_result.news_sentiment == "正面":
            opportunity_score += 1
            opportunity_factors.append("新闻情绪正面")

        # 如果没有机会因素，添加提示
        if not opportunity_factors:
            opportunity_factors.append("无明显机会因素")

        # 确定机会等级
        if opportunity_score >= 5:
            opportunity_level = OpportunityLevel.EXCELLENT.value
        elif opportunity_score >= 4:
            opportunity_level = OpportunityLevel.GOOD.value
        elif opportunity_score >= 3:
            opportunity_level = OpportunityLevel.MODERATE.value
        elif opportunity_score >= 1:
            opportunity_level = OpportunityLevel.POOR.value
        else:
            opportunity_level = OpportunityLevel.VERY_POOR.value

        return opportunity_level, opportunity_factors

    def _assess_overall_health(self,
                               trend_health: str,
                               position_health: str,
                               pattern_health: str) -> str:
        """
        评估整体健康度

        Args:
            trend_health: 趋势健康度
            position_health: 位置健康度
            pattern_health: 形态健康度

        Returns:
            整体健康度
        """
        health_scores = []

        if "健康" in trend_health:
            health_scores.append(1)
        elif "不健康" in trend_health:
            health_scores.append(0)
        else:
            health_scores.append(0.5)

        if "安全" in position_health:
            health_scores.append(1)
        elif "风险" in position_health:
            health_scores.append(0)
        else:
            health_scores.append(0.5)

        if "健康" in pattern_health:
            health_scores.append(1)
        elif "不健康" in pattern_health:
            health_scores.append(0)
        else:
            health_scores.append(0.5)

        avg_health = sum(health_scores) / len(health_scores)

        if avg_health >= 0.75:
            return "非常健康"
        elif avg_health >= 0.50:
            return "健康"
        elif avg_health >= 0.25:
            return "一般"
        else:
            return "不健康"

    def _generate_recommendation(self,
                                risk_level: str,
                                opportunity_level: str,
                                overall_health: str) -> str:
        """
        生成投资建议

        Args:
            risk_level: 风险等级
            opportunity_level: 机会等级
            overall_health: 整体健康度

        Returns:
            投资建议
        """
        # 高风险 + 低机会 = 卖出
        if ("高" in risk_level or "极高风险" == risk_level) and "差" in opportunity_level:
            return "建议卖出/减仓"

        # 低风险 + 高机会 = 买入
        elif ("低" in risk_level or "极低风险" == risk_level) and ("好" in opportunity_level or "佳" in opportunity_level):
            return "建议买入"

        # 中等风险 + 中等机会 = 观望
        else:
            return "建议观望"

    def _generate_diagnosis_report(self, result: DiagnosisResult) -> str:
        """生成诊断报告"""
        report = f"""
{'='*80}
                          📊 股票诊断报告
{'='*80}

【整体诊断】
  健康度: {result.overall_health}
  风险等级: {result.risk_level}
  机会等级: {result.opportunity_level}

【各维度诊断】
  趋势健康度: {result.trend_health}
  位置健康度: {result.position_health}
  形态健康度: {result.pattern_health}

【风险因素】
"""
        for i, factor in enumerate(result.risk_factors, 1):
            report += f"  {i}. {factor}\n"

        report += f"""
【机会因素】
"""
        for i, factor in enumerate(result.opportunity_factors, 1):
            report += f"  {i}. {factor}\n"

        report += f"""
【投资建议】
  {result.recommendation}

{'='*80}
"""
        return report


def test_diagnosis():
    """测试诊断系统"""
    print("="*80)
    print("🧪 测试诊断系统")
    print("="*80)

    from agents.technical.technical_agent import TechnicalAnalysisResult
    from agents.fundamental.fundamental_agent import FundamentalAnalysisResult
    from agents.sentiment.sentiment_agent import SentimentAnalysisResult

    # 创建测试数据
    tech_result = TechnicalAnalysisResult(
        trend="上升",
        position="低位",
        patterns=["底部横盘", "均线多头"],
        indicators={"RSI": 25, "MACD": 10},
        volume_price="放量上涨",
        score=0.86
    )

    fund_result = FundamentalAnalysisResult(
        pe_ratio=15.0,
        valuation="低估",
        financial_health="优秀",
        score=0.85
    )

    sent_result = SentimentAnalysisResult(
        news_sentiment="正面",
        event_impact="利好",
        sentiment_score=0.8,
        score=0.65
    )

    # 执行诊断
    system = DiagnosisSystem()
    diagnosis = system.diagnose(tech_result, fund_result, sent_result)

    print(diagnosis.diagnosis_report)

    print("✅ 测试完成")


if __name__ == "__main__":
    test_diagnosis()
