#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分析模型 v1.0
基于技术指标和基本面分析给出交易建议
"""

import sys
sys.path.append('/home/parallels/.openclaw/workspace/skills/a-stock-fetcher/scripts')
from indicators_v2 import calculate_all_indicators, interpret_indicators
from stock_api import fetch_stock_data
from historical_data import fetch_historical_data
from typing import Dict, List, Optional, Tuple

class SignalStrength:
    """信号强度"""
    VERY_STRONG = 5
    STRONG = 4
    MODERATE = 3
    WEAK = 2
    VERY_WEAK = 1

class TradingSignal:
    """交易信号"""

    def __init__(self, symbol: str, action: str, price: float,
                 stop_loss: float, take_profit: float,
                 confidence: float, reasons: List[str]):
        """
        创建交易信号

        Args:
            symbol: 股票代码
            action: 买入/卖出/观望
            price: 价格
            stop_loss: 止损价
            take_profit: 止盈价
            confidence: 信心度（0-1）
            reasons: 信号原因列表
        """
        self.symbol = symbol
        self.action = action
        self.price = price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.confidence = confidence
        self.reasons = reasons
        self.strength = self._calculate_strength()

    def _calculate_strength(self) -> int:
        """计算信号强度"""
        if self.confidence >= 0.9:
            return SignalStrength.VERY_STRONG
        elif self.confidence >= 0.7:
            return SignalStrength.STRONG
        elif self.confidence >= 0.5:
            return SignalStrength.MODERATE
        elif self.confidence >= 0.3:
            return SignalStrength.WEAK
        else:
            return SignalStrength.VERY_WEAK

    def get_strength_label(self) -> str:
        """获取强度标签"""
        labels = {
            SignalStrength.VERY_STRONG: "⭐⭐⭐⭐⭐ 极强",
            SignalStrength.STRONG: "⭐⭐⭐⭐ 强",
            SignalStrength.MODERATE: "⭐⭐⭐ 中等",
            SignalStrength.WEAK: "⭐⭐ 弱",
            SignalStrength.VERY_WEAK: "⭐ 极弱"
        }
        return labels.get(self.strength, "")

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'action': self.action,
            'price': self.price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'confidence': self.confidence,
            'strength': self.strength,
            'strength_label': self.get_strength_label(),
            'reasons': self.reasons
        }

class AnalysisModel:
    """分析模型"""

    def __init__(self, stop_loss_pct: float = 0.05, take_profit_pct: float = 0.10):
        """
        初始化分析模型

        Args:
            stop_loss_pct: 止损百分比
            take_profit_pct: 止盈百分比
        """
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    def analyze(self, symbol: str, days: int = 30) -> Optional[TradingSignal]:
        """
        分析股票，给出交易信号

        Args:
            symbol: 股票代码
            days: 分析天数

        Returns:
            交易信号
        """
        print(f"\n📊 正在分析 {symbol}...")

        # 1. 获取历史数据
        candles = fetch_historical_data(symbol, '1d', days)
        if not candles or len(candles) < 20:
            print(f"❌ 数据不足，无法分析")
            return None

        # 2. 获取实时数据
        stocks = fetch_stock_data([symbol], use_cache=False)
        if not stocks:
            print(f"❌ 获取实时数据失败")
            return None

        stock = stocks[0]
        current_price = stock['price']

        # 3. 计算技术指标
        indicators = calculate_all_indicators(candles)
        interpretation = interpret_indicators(indicators, -1)

        # 4. 综合分析
        signal = self._generate_signal(symbol, stock, indicators, interpretation)
        return signal

    def _generate_signal(self, symbol: str, stock: Dict,
                         indicators: Dict, interpretation: Dict) -> TradingSignal:
        """生成交易信号"""
        reasons = []
        confidence = 0.0
        action = "观望"

        current_price = stock['price']
        change_pct = stock['change_percent']

        # ===== 买入信号判断 =====

        buy_signals = 0
        buy_confidence = 0.0

        # 1. RSI超卖
        rsi = indicators.get('rsi', [])
        if rsi and rsi[-1] and rsi[-1] < 30:
            buy_signals += 1
            buy_confidence += 0.2
            reasons.append(f"RSI超卖 ({rsi[-1]:.2f})")

        # 2. MACD金叉
        macd = indicators.get('macd', {})
        if macd.get('histogram'):
            hist = macd['histogram']
            # 过滤None值
            valid_hist = [h for h in hist if h is not None]
            if len(valid_hist) >= 2 and valid_hist[-1] > 0 and valid_hist[-2] <= 0:
                buy_signals += 1
                buy_confidence += 0.25
                reasons.append("MACD金叉")

        # 3. KDJ金叉
        kdj = indicators.get('kdj', {})
        if kdj.get('K') and kdj.get('D'):
            k, d = kdj['K'][-1], kdj['D'][-1]
            if k and d and k > d:
                buy_signals += 1
                buy_confidence += 0.2
                reasons.append("KDJ金叉")

        # 4. 均线多头排列
        sma5 = indicators.get('sma_5', [])
        sma10 = indicators.get('sma_10', [])
        sma20 = indicators.get('sma_20', [])

        if sma5 and sma10 and sma20:
            if sma5[-1] > sma10[-1] > sma20[-1]:
                buy_signals += 1
                buy_confidence += 0.15
                reasons.append("均线多头排列")

        # 5. 价格接近支撑位
        bollinger = indicators.get('bollinger', {})
        if bollinger.get('lower'):
            lower = bollinger['lower'][-1]
            if lower and current_price <= lower * 1.02:  # 接近下轨2%
                buy_signals += 1
                buy_confidence += 0.2
                reasons.append("接近布林带下轨（支撑位）")

        # ===== 卖出信号判断 =====

        sell_signals = 0
        sell_confidence = 0.0

        # 1. RSI超买
        if rsi and rsi[-1] and rsi[-1] > 70:
            sell_signals += 1
            sell_confidence += 0.2
            reasons.append(f"RSI超买 ({rsi[-1]:.2f})")

        # 2. MACD死叉
        if macd.get('histogram'):
            hist = macd['histogram']
            # 过滤None值
            valid_hist = [h for h in hist if h is not None]
            if len(valid_hist) >= 2 and valid_hist[-1] < 0 and valid_hist[-2] >= 0:
                sell_signals += 1
                sell_confidence += 0.25
                reasons.append("MACD死叉")

        # 3. KDJ死叉
        if kdj.get('K') and kdj.get('D'):
            k, d = kdj['K'][-1], kdj['D'][-1]
            if k and d and k < d:
                sell_signals += 1
                sell_confidence += 0.2
                reasons.append("KDJ死叉")

        # 4. 均线空头排列
        if sma5 and sma10 and sma20:
            if sma5[-1] < sma10[-1] < sma20[-1]:
                sell_signals += 1
                sell_confidence += 0.15
                reasons.append("均线空头排列")

        # 5. 价格接近阻力位
        if bollinger.get('upper'):
            upper = bollinger['upper'][-1]
            if upper and current_price >= upper * 0.98:  # 接近上轨2%
                sell_signals += 1
                sell_confidence += 0.2
                reasons.append("接近布林带上轨（阻力位）")

        # ===== 综合判断 =====

        if buy_signals >= 4 and buy_confidence >= 0.7:
            action = "买入"
            confidence = min(buy_confidence, 0.9)
        elif sell_signals >= 4 and sell_confidence >= 0.7:
            action = "卖出"
            confidence = min(sell_confidence, 0.9)
        elif buy_signals >= 3 and sell_signals <= 2:
            action = "买入"
            confidence = min(buy_confidence, 0.7)
        elif sell_signals >= 3 and buy_signals <= 2:
            action = "卖出"
            confidence = min(sell_confidence, 0.7)
        elif buy_signals > sell_signals:
            action = "偏多"
            confidence = buy_confidence * 0.5
        elif sell_signals > buy_signals:
            action = "偏空"
            confidence = sell_confidence * 0.5
        else:
            action = "观望"
            confidence = 0.0

        # 计算止损止盈
        if action == "买入":
            stop_loss = current_price * (1 - self.stop_loss_pct)
            take_profit = current_price * (1 + self.take_profit_pct)
        elif action == "卖出":
            stop_loss = None
            take_profit = None
        else:
            stop_loss = None
            take_profit = None

        return TradingSignal(
            symbol=symbol,
            action=action,
            price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            reasons=reasons
        )

    def batch_analyze(self, symbols: List[str], days: int = 30) -> List[TradingSignal]:
        """
        批量分析股票

        Args:
            symbols: 股票代码列表
            days: 分析天数

        Returns:
            交易信号列表（按信心度排序）
        """
        signals = []

        for symbol in symbols:
            signal = self.analyze(symbol, days)
            if signal and signal.action in ["买入", "卖出"]:
                signals.append(signal)

        # 按信心度排序
        signals.sort(key=lambda x: x.confidence, reverse=True)

        return signals

    def format_signal(self, signal: TradingSignal) -> str:
        """格式化交易信号"""
        action_emoji = {
            "买入": "🟢",
            "卖出": "🔴",
            "偏多": "🟡",
            "偏空": "🟠",
            "观望": "⚪"
        }

        emoji = action_emoji.get(signal.action, "⚪")

        output = f"""
{emoji} {signal.symbol} - {signal.action}信号
{'─'*60}
  当前价格: ¥{signal.price:.2f}
  信心度:   {signal.confidence*100:.0f}% ({signal.get_strength_label()})
{'─'*60}
"""

        if signal.stop_loss:
            output += f"  止损价:   ¥{signal.stop_loss:.2f} ({self.stop_loss_pct*100:.1f}%)\n"
        if signal.take_profit:
            output += f"  止盈价:   ¥{signal.take_profit:.2f} ({self.take_profit_pct*100:.1f}%)\n"

        if signal.reasons:
            output += f"{'─'*60}\n  信号原因:\n"
            for reason in signal.reasons:
                output += f"    • {reason}\n"

        output += f"{'─'*60}\n"

        return output

    def format_batch_signals(self, signals: List[TradingSignal]) -> str:
        """格式化批量信号"""
        if not signals:
            return "无交易信号"

        buy_signals = [s for s in signals if s.action == "买入"]
        sell_signals = [s for s in signals if s.action == "卖出"]

        output = f"""
📊 批量分析结果
{'='*60}
买入信号: {len(buy_signals)}只
卖出信号: {len(sell_signals)}只
{'='*60}
"""

        if buy_signals:
            output += "\n🟢 买入信号:\n"
            for signal in buy_signals[:5]:  # 只显示前5个
                output += f"  {signal.symbol}: ¥{signal.price:.2f} (信心{signal.confidence*100:.0f}%)\n"

        if sell_signals:
            output += "\n🔴 卖出信号:\n"
            for signal in sell_signals[:5]:  # 只显示前5个
                output += f"  {signal.symbol}: ¥{signal.price:.2f} (信心{signal.confidence*100:.0f}%)\n"

        output += f"{'='*60}\n"

        return output
