#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
决策智能体
负责综合分析、交易建议、止盈止损
"""

import sys
import os
from typing import Dict, List, Optional

# 添加scripts目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from stock_api import fetch_stock_data

# 添加项目根目录到路径
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from graph.trading_graph import TradingDecision


class DecisionAgent:
    """决策智能体"""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.stop_loss_pct = 0.03  # 止损 3%
        self.take_profit_pct = 0.05  # 止盈 5%

    def make_decision(self, symbol: str,
                      technical_result,
                      fundamental_result,
                      sentiment_result,
                      debate_result) -> TradingDecision:
        """
        综合分析并制定决策

        Args:
            symbol: 股票代码
            technical_result: 技术分析结果
            fundamental_result: 基本面分析结果
            sentiment_result: 情绪分析结果
            debate_result: 辩论结果

        Returns:
            TradingDecision: 交易决策
        """
        # 获取实时价格
        stocks = fetch_stock_data([symbol], use_cache=False)
        if not stocks:
            current_price = 0.0
        else:
            current_price = stocks[0]['price']

        # 计算综合评分（技术面40%，基本面30%，情绪面30%）
        overall_score = (
            technical_result.score * 0.4 +
            fundamental_result.score * 0.3 +
            sentiment_result.score * 0.3
        )

        # 根据综合评分和辩论共识制定决策
        action, confidence = self._determine_action(
            overall_score,
            debate_result.consensus
        )

        # 计算价格
        buy_price, sell_price, stop_loss, target_price = self._calculate_prices(
            action,
            current_price,
            technical_result
        )

        # 收集决策理由
        reasons = self._collect_reasons(
            technical_result,
            fundamental_result,
            sentiment_result,
            debate_result
        )

        # 创建决策对象
        decision = TradingDecision(
            symbol=symbol,
            action=action,
            confidence=confidence,
            buy_price=buy_price if action == "买入" else current_price,
            sell_price=sell_price if action == "卖出" else None,
            stop_loss=stop_loss,
            target_price=target_price,
            reasons=reasons,
            technical_score=technical_result.score,
            fundamental_score=fundamental_result.score,
            sentiment_score=sentiment_result.score,
            overall_score=overall_score
        )

        if self.debug:
            print(f"  ✅ 决策制定完成")
            print(f"     操作: {action}, 信心度: {confidence*100:.0f}%")

        return decision

    def _determine_action(self, overall_score: float, consensus: str) -> tuple:
        """
        确定操作和信心度

        Args:
            overall_score: 综合评分 0-1
            consensus: 辩论共识

        Returns:
            (action, confidence): 操作和信心度
        """
        action = "观望"
        confidence = 0.0

        # 根据综合评分和共识判断
        if overall_score >= 0.7 and consensus == "看多":
            action = "买入"
            confidence = min(0.9, overall_score + 0.1)
        elif overall_score >= 0.5 and consensus == "看多":
            action = "买入"
            confidence = overall_score
        elif overall_score <= 0.3 and consensus == "看空":
            action = "卖出"
            confidence = min(0.9, (1.0 - overall_score) + 0.1)
        elif overall_score <= 0.4 and consensus == "看空":
            action = "卖出"
            confidence = 1.0 - overall_score
        else:
            action = "观望"
            confidence = 0.5

        return action, confidence

    def _calculate_prices(self, action: str, current_price: float, technical_result) -> tuple:
        """
        计算价格

        Args:
            action: 操作（买入/卖出/观望）
            current_price: 当前价格
            technical_result: 技术分析结果

        Returns:
            (buy_price, sell_price, stop_loss, target_price): 各种价格
        """
        buy_price = None
        sell_price = None
        stop_loss = None
        target_price = None

        if action == "买入":
            # 买入价格：当前价格
            buy_price = current_price

            # 止损价格：-3%
            stop_loss = current_price * (1 - self.stop_loss_pct)

            # 目标价格：+5%
            target_price = current_price * (1 + self.take_profit_pct)

            # 如果是低位，可以适当放宽止盈
            if technical_result.position == "低位":
                target_price = current_price * (1 + self.take_profit_pct + 0.02)

        elif action == "卖出":
            # 卖出价格：当前价格
            sell_price = current_price

        return buy_price, sell_price, stop_loss, target_price

    def _collect_reasons(self, technical_result, fundamental_result, sentiment_result, debate_result) -> List[str]:
        """收集决策理由"""
        reasons = []

        # 技术面理由
        if technical_result.trend != "横盘":
            reasons.append(f"技术面呈{technical_result.trend}趋势")
        if technical_result.position != "中位":
            reasons.append(f"股价处于{technical_result.position}")
        if technical_result.volume_price:
            reasons.append(f"{technical_result.volume_price}")

        # 基本面理由
        if fundamental_result.valuation != "合理":
            reasons.append(f"估值{fundamental_result.valuation}")
        if fundamental_result.financial_health != "一般":
            reasons.append(f"财务状况{fundamental_result.financial_health}")

        # 情绪面理由
        if sentiment_result.news_sentiment != "中性":
            reasons.append(f"新闻情绪{sentiment_result.news_sentiment}")
        if sentiment_result.event_impact != "无影响":
            reasons.append(sentiment_result.event_impact)

        # 辩论共识
        if debate_result.consensus != "中性":
            reasons.append(f"多空辩论{debate_result.consensus}")

        return reasons
