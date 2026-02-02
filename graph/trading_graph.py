#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票预测系统 - 智能体协作图
基于多智能体协作架构的A股预测系统
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# 添加scripts目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

@dataclass
class TradingDecision:
    """交易决策"""
    symbol: str
    action: str  # 买入/卖出/观望
    confidence: float  # 信心度 0-1
    buy_price: Optional[float] = None  # 买入价格
    sell_price: Optional[float] = None  # 卖出价格
    stop_loss: Optional[float] = None  # 止损价格
    target_price: Optional[float] = None  # 目标价格
    reasons: List[str] = field(default_factory=list)  # 决策理由
    technical_score: float = 0.0  # 技术分析评分
    fundamental_score: float = 0.0  # 基本面评分
    sentiment_score: float = 0.0  # 情绪分析评分
    overall_score: float = 0.0  # 综合评分

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'action': self.symbol,
            'confidence': self.confidence,
            'buy_price': self.buy_price,
            'sell_price': self.sell_price,
            'stop_loss': self.stop_loss,
            'target_price': self.target_price,
            'reasons': self.reasons,
            'technical_score': self.technical_score,
            'fundamental_score': self.fundamental_score,
            'sentiment_score': self.sentiment_score,
            'overall_score': self.overall_score,
            'timestamp': datetime.now().isoformat()
        }

    def format_output(self) -> str:
        """格式化输出"""
        action_emoji = {
            "买入": "🟢",
            "卖出": "🔴",
            "观望": "⚪"
        }
        emoji = action_emoji.get(self.action, "⚪")

        current_price_display = f"¥{self.buy_price:.2f}" if self.buy_price else "N/A"

        output = f"""
{emoji} {self.symbol} - {self.action}建议
{'='*60}
当前价格: {current_price_display}
{'─'*60}
操作建议:  {self.action}
信心度:    {self.confidence*100:.0f}%
"""

        if self.buy_price:
            output += f"买入价格:  ¥{self.buy_price:.2f}\n"
        if self.sell_price:
            output += f"卖出价格:  ¥{self.sell_price:.2f}\n"
        if self.stop_loss:
            output += f"止损价格:  ¥{self.stop_loss:.2f}\n"
        if self.target_price:
            output += f"目标价格:  ¥{self.target_price:.2f}\n"

        output += f"{'─'*60}\n"

        output += "评分情况:\n"
        output += f"  • 技术分析: {self.technical_score*100:.0f}%\n"
        output += f"  • 基本面:   {self.fundamental_score*100:.0f}%\n"
        output += f"  • 情绪分析: {self.sentiment_score*100:.0f}%\n"
        output += f"  • 综合评分: {self.overall_score*100:.0f}%\n"

        if self.reasons:
            output += f"\n{'─'*60}\n决策理由:\n"
            for i, reason in enumerate(self.reasons, 1):
                output += f"  {i}. {reason}\n"

        output += f"{'='*60}\n"

        return output


class TradingAgentsGraph:
    """智能体协作图 - 主流程编排"""

    def __init__(self, debug: bool = False, config: Dict = None):
        """
        初始化智能体协作系统

        Args:
            debug: 是否启用调试模式
            config: 配置字典
        """
        self.debug = debug
        self.config = config or {}

        # 导入各个智能体
        from agents.technical.technical_agent import TechnicalAnalysisAgent
        from agents.fundamental.fundamental_agent import FundamentalAnalysisAgent
        from agents.sentiment.sentiment_agent import SentimentAnalysisAgent
        from agents.debate.debate_agent import DebateAgent
        from agents.decision.decision_agent import DecisionAgent

        # 初始化智能体
        self.technical_agent = TechnicalAnalysisAgent(debug=debug)
        self.fundamental_agent = FundamentalAnalysisAgent(debug=debug)
        self.sentiment_agent = SentimentAnalysisAgent(debug=debug)
        self.debate_agent = DebateAgent(debug=debug)
        self.decision_agent = DecisionAgent(debug=debug)

        if debug:
            print("✅ 智能体协作系统初始化完成")

    def propagate(self, symbol: str, days: int = 30) -> TradingDecision:
        """
        传播信号并生成决策

        Args:
            symbol: 股票代码
            days: 分析天数

        Returns:
            TradingDecision: 交易决策
        """
        if self.debug:
            print(f"\n{'='*60}")
            print(f"📊 开始分析股票: {symbol}")
            print(f"{'='*60}\n")

        # Step 1: 技术分析
        if self.debug:
            print("📈 [技术分析智能体] 分析中...")
        technical_result = self.technical_agent.analyze(symbol, days)

        # Step 2: 基本面分析
        if self.debug:
            print("💰 [基本面分析智能体] 分析中...")
        fundamental_result = self.fundamental_agent.analyze(symbol, days)

        # Step 3: 情绪分析
        if self.debug:
            print("📰 [情绪分析智能体] 分析中...")
        sentiment_result = self.sentiment_agent.analyze(symbol, days)

        # Step 4: 多空辩论
        if self.debug:
            print("🐂🐻 [辩论智能体] 辩论中...")
        debate_result = self.debate_agent.debate(
            technical_result,
            fundamental_result,
            sentiment_result
        )

        # Step 5: 综合决策
        if self.debug:
            print("🎯 [决策智能体] 制定决策中...")
        decision = self.decision_agent.make_decision(
            symbol,
            technical_result,
            fundamental_result,
            sentiment_result,
            debate_result
        )

        if self.debug:
            print(f"\n{'='*60}")
            print(f"✅ 分析完成")
            print(f"{'='*60}\n")

        return decision

    def batch_analyze(self, symbols: List[str], days: int = 30) -> List[TradingDecision]:
        """
        批量分析股票

        Args:
            symbols: 股票代码列表
            days: 分析天数

        Returns:
            List[TradingDecision]: 决策列表
        """
        decisions = []
        for symbol in symbols:
            try:
                decision = self.propagate(symbol, days)
                decisions.append(decision)
            except Exception as e:
                print(f"❌ {symbol} 分析失败: {e}")

        return decisions


def main():
    """主函数 - 测试"""
    import sys

    # 创建系统
    system = TradingAgentsGraph(debug=True)

    # 测试股票
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
    else:
        symbol = "600519"  # 贵州茅台

    # 分析股票
    decision = system.propagate(symbol, days=30)

    # 输出结果
    print(decision.format_output())


if __name__ == "__main__":
    main()
