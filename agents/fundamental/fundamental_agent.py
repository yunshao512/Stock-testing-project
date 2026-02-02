#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基本面分析智能体
负责财务数据、估值模型、行业分析
"""

import sys
import os
from typing import Dict, List
from dataclasses import dataclass, field

# 添加项目根目录到路径
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from dataflows.fundamental_data import get_fundamental_provider


@dataclass
class FundamentalAnalysisResult:
    """基本面分析结果"""
    pe_ratio: float = 0.0  # 市盈率
    pb_ratio: float = 0.0  # 市净率
    roe: float = 0.0  # 净资产收益率
    revenue_growth: float = 0.0  # 营收增长
    profit_growth: float = 0.0  # 利润增长
    debt_ratio: float = 0.0  # 负债率
    valuation: str = ""  # 估值（低估/合理/高估）
    financial_health: str = ""  # 财务健康度
    score: float = 0.0  # 评分 0-1
    signals: List[str] = field(default_factory=list)  # 信号列表


class FundamentalAnalysisAgent:
    """基本面分析智能体"""

    def __init__(self, debug: bool = False):
        self.debug = debug

    def analyze(self, symbol: str, days: int = 30) -> FundamentalAnalysisResult:
        """
        执行基本面分析

        使用真实财务数据源（Tushare、AkShare），如果不可用则使用模拟数据

        Args:
            symbol: 股票代码
            days: 分析天数

        Returns:
            FundamentalAnalysisResult: 分析结果
        """
        result = FundamentalAnalysisResult()

        # 获取基本面数据
        provider = get_fundamental_provider()
        financial_data = provider.fetch_financial_data(symbol, use_cache=True)

        # 填充数据
        result.pe_ratio = financial_data.get('pe_ratio', 0.0)
        result.pb_ratio = financial_data.get('pb_ratio', 0.0)
        result.roe = financial_data.get('roe', 0.0)
        result.revenue_growth = financial_data.get('revenue_growth', 0.0)
        result.profit_growth = financial_data.get('profit_growth', 0.0)
        result.debt_ratio = financial_data.get('debt_ratio', 0.0)

        # 判断估值
        if result.pe_ratio < 20:
            result.valuation = "低估"
        elif result.pe_ratio < 35:
            result.valuation = "合理"
        else:
            result.valuation = "高估"

        # 判断财务健康度
        if result.roe > 0.15 and result.debt_ratio < 0.5:
            result.financial_health = "优秀"
        elif result.roe > 0.10 and result.debt_ratio < 0.6:
            result.financial_health = "良好"
        else:
            result.financial_health = "一般"

        # 计算评分
        result.score = self._calculate_score(result)

        # 生成信号
        result.signals = self._generate_signals(result)

        if self.debug:
            source = financial_data.get('source', 'N/A')
            print(f"  ✅ 基本面分析完成，评分: {result.score*100:.0f}% (来源: {source})")
            print(f"     估值: {result.valuation}, 财务健康: {result.financial_health}")

        return result

    def _calculate_score(self, result: FundamentalAnalysisResult) -> float:
        """计算基本面评分"""
        score = 0.0

        # PE评分
        if result.pe_ratio < 20:
            score += 0.20
        elif result.pe_ratio < 30:
            score += 0.10
        else:
            score -= 0.10

        # ROE评分
        if result.roe > 0.15:
            score += 0.25
        elif result.roe > 0.10:
            score += 0.15
        else:
            score += 0.05

        # 增长评分
        avg_growth = (result.revenue_growth + result.profit_growth) / 2
        if avg_growth > 0.15:
            score += 0.25
        elif avg_growth > 0.10:
            score += 0.15
        elif avg_growth > 0.05:
            score += 0.05

        # 负债评分
        if result.debt_ratio < 0.4:
            score += 0.15
        elif result.debt_ratio < 0.6:
            score += 0.10
        else:
            score -= 0.10

        # 限制在0-1之间
        score = max(0.0, min(1.0, score))

        return score

    def _generate_signals(self, result: FundamentalAnalysisResult) -> List[str]:
        """生成基本面信号"""
        signals = []

        if result.valuation == "低估" and result.financial_health in ["优秀", "良好"]:
            signals.append("基本面强烈看好")
        elif result.valuation == "低估":
            signals.append("估值偏低")
        elif result.valuation == "高估":
            signals.append("估值偏高")
        else:
            signals.append("基本面中性")

        return signals
