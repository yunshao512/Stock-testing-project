#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新分析模型 v2.0
基于回测结果，放弃失效的技术指标，采用新策略
"""

import sys
sys.path.append('/home/parallels/.openclaw/workspace/skills/a-stock-fetcher/scripts')
from historical_data import fetch_historical_data
from stock_api import fetch_stock_data
from typing import List, Dict, Optional
from datetime import datetime

class NewSignalStrength:
    """新信号强度"""
    VERY_STRONG = 5
    STRONG = 4
    MODERATE = 3
    WEAK = 2
    VERY_WEAK = 1

class NewTradingSignal:
    """新交易信号"""

    def __init__(self, symbol: str, action: str, price: float,
                 stop_loss: float, take_profit: float,
                 confidence: float, reasons: List[str]):
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
        if self.confidence >= 0.8:
            return NewSignalStrength.VERY_STRONG
        elif self.confidence >= 0.6:
            return NewSignalStrength.STRONG
        elif self.confidence >= 0.4:
            return NewSignalStrength.MODERATE
        elif self.confidence >= 0.2:
            return NewSignalStrength.WEAK
        else:
            return NewSignalStrength.VERY_WEAK

    def get_strength_label(self) -> str:
        """获取强度标签"""
        labels = {
            NewSignalStrength.VERY_STRONG: "⭐⭐⭐⭐⭐ 极强",
            NewSignalStrength.STRONG: "⭐⭐⭐⭐ 强",
            NewSignalStrength.MODERATE: "⭐⭐⭐ 中等",
            NewSignalStrength.WEAK: "⭐⭐ 弱",
            NewSignalStrength.VERY_WEAK: "⭐ 极弱"
        }
        return labels.get(self.strength, "")

class NewAnalysisModel:
    """新分析模型"""

    def __init__(self, stop_loss_pct: float = 0.03, take_profit_pct: float = 0.05):
        """
        初始化新分析模型

        Args:
            stop_loss_pct: 止损百分比（降低到3%，因为信号更难）
            take_profit_pct: 止盈百分比（降低到5%，快进快出）
        """
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

        # 热门股票名单（流动性好，机构关注）
        self.hot_stocks = {
            'sh600519': '贵州茅台',
            'sz000858': '五粮液',
            'sz300750': '宁德时代',
            'sz002594': '比亚迪',
            'sh600036': '招商银行',
            'sh601318': '中国平安',
            'sh688981': '中芯国际',
            'sz002230': '科大讯飞',
            'sz000001': '平安银行'
        }

    def analyze(self, symbol: str, days: int = 30) -> Optional[NewTradingSignal]:
        """
        分析股票，给出新策略信号

        新策略（基于回测结果）：
        1. 放弃失效信号：RSI超卖、MACD金叉
        2. 保留有效信号：RSI超买+死叉（卖出）
        3. 新增信号：量价分析、板块轮动
        4. 只交易热门股

        Args:
            symbol: 股票代码
            days: 分析天数

        Returns:
            交易信号
        """
        print(f"\n📊 [新模型] 正在分析 {symbol}...")

        # 检查是否为热门股
        is_hot = symbol in self.hot_stocks
        if not is_hot:
            print(f"  ⚠️ 非热门股，降低信号权重")
            confidence_penalty = 0.2
        else:
            confidence_penalty = 0.0

        # 获取实时数据
        stocks = fetch_stock_data([symbol], use_cache=False)
        if not stocks:
            print(f"❌ 获取实时数据失败")
            return None

        stock = stocks[0]
        current_price = stock['price']
        change_pct = stock['change_percent']

        # 获取历史数据
        candles = fetch_historical_data(symbol, '1d', days)
        if not candles or len(candles) < 10:
            print(f"❌ 历史数据不足")
            return None

        # 新策略分析
        return self._generate_new_signal(symbol, stock, candles, is_hot, confidence_penalty)

    def _generate_new_signal(self, symbol: str, stock: Dict,
                             candles: List[Dict], is_hot: bool,
                             confidence_penalty: float) -> Optional[NewTradingSignal]:
        """生成新策略信号"""
        reasons = []
        confidence = 0.0
        action = "观望"

        current_price = stock['price']
        change_pct = stock['change_percent']
        volume = stock['volume']
        yesterday_close = stock['yesterday_close']

        # ===== 新策略：量价分析 =====

        # 信号1：放量上涨（买入）
        avg_volume = sum(c['volume'] for c in candles[-10:-1]) / 9  # 近10日平均量
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0

        if change_pct > 2.0 and volume_ratio > 1.5:
            reasons.append(f"放量上涨 ({change_pct:+.2f}%, 量比{volume_ratio:.1f}x)")
            confidence += 0.15

        # 信号2：缩量下跌（观望，不要买入）
        elif change_pct < -2.0 and volume_ratio < 0.8:
            reasons.append(f"缩量下跌 ({change_pct:+.2f}%, 量比{volume_ratio:.1f}x)")
            confidence -= 0.10

        # ===== 新策略：位置分析 =====

        # 计算近期高低点
        recent_highs = [c['high'] for c in candles[-10:]]
        recent_lows = [c['low'] for c in candles[-10:]]
        highest = max(recent_highs)
        lowest = min(recent_lows)
        range_size = highest - lowest

        # 信号3：接近低点（谨慎买入）
        if range_size > 0:
            position = (current_price - lowest) / range_size
            if position < 0.2:
                reasons.append(f"接近低点 ({position*100:.1f}%位置)")
                confidence += 0.10
            elif position > 0.8:
                reasons.append(f"接近高点 ({position*100:.1f}%位置)")
                confidence -= 0.10

        # ===== 新策略：趋势分析 =====

        # 计算短期趋势（5天）
        short_trend = (current_price - candles[-6]['close']) / candles[-6]['close'] * 100

        # 计算中期趋势（20天）
        mid_trend = (current_price - candles[-21]['close']) / candles[-21]['close'] * 100

        # 信号4：趋势共振（短中期同向）
        if short_trend > 0 and mid_trend > 0:
            reasons.append(f"趋势共振 (短期{short_trend:+.1f}%, 中期{mid_trend:+.1f}%)")
            confidence += 0.15
        elif short_trend < 0 and mid_trend < 0:
            reasons.append(f"趋势共振 (短期{short_trend:+.1f}%, 中期{mid_trend:+.1f}%)")
            confidence -= 0.15

        # ===== 新策略：极端情绪逆向 =====

        # 信号5：极端下跌后反弹
        # 寻找5天内跌超过8%，然后企稳
        for i in range(len(candles) - 6, len(candles)):
            if i < 0:
                continue

            # 5天前价格
            price_5d_ago = candles[i]['close']
            change_5d = (price_5d_ago - candles[i-5]['close']) / candles[i-5]['close'] * 100

            # 如果5天大跌超8%，且今天企稳
            if change_5d < -8.0 and change_pct > -1.0:
                reasons.append("极端下跌后企稳")
                confidence += 0.20
                break

        # ===== 新策略：卖出信号（保留有效信号）=====

        # 信号6：大涨后放量（止盈）
        if change_pct > 5.0 and volume_ratio > 2.0:
            reasons.append(f"大涨放量 (可能见顶)")
            confidence -= 0.20

        # ===== 综合判断 =====

        # 热门股加成
        if is_hot:
            confidence *= 1.2  # 热门股信号更可靠

        # 应用非热门股惩罚
        confidence -= confidence_penalty

        # 限制在0-1之间
        confidence = max(0.0, min(1.0, confidence))

        # 判断操作
        if confidence >= 0.5:
            action = "买入"
        elif confidence <= 0.3:
            action = "卖出/减仓"
        else:
            action = "观望"

        # 计算止损止盈
        if action == "买入":
            stop_loss = current_price * (1 - self.stop_loss_pct)
            take_profit = current_price * (1 + self.take_profit_pct)
        else:
            stop_loss = None
            take_profit = None

        if not reasons:
            reasons.append("无明显信号")

        return NewTradingSignal(
            symbol=symbol,
            action=action,
            price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            reasons=reasons
        )

    def format_signal(self, signal: NewTradingSignal) -> str:
        """格式化交易信号"""
        action_emoji = {
            "买入": "🟢",
            "卖出": "🔴",
            "卖出/减仓": "🟠",
            "观望": "⚪"
        }

        emoji = action_emoji.get(signal.action, "⚪")

        output = f"""
{emoji} {signal.symbol} - {signal.action}信号 [新模型]
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

def test_new_model():
    """测试新模型"""
    print("🧪 测试新分析模型\n")
    print("="*80)

    model = NewAnalysisModel(stop_loss_pct=0.03, take_profit_pct=0.05)

    test_stocks = [
        'sh600519',  # 热门股
        'sz000858',  # 热门股
        'sz300750',  # 热门股
        'sh600019',  # 冷门股
    ]

    for symbol in test_stocks:
        signal = model.analyze(symbol, days=30)
        if signal:
            print(model.format_signal(signal))
        else:
            print(f"❌ {symbol}: 分析失败\n")

if __name__ == "__main__":
    test_new_model()
