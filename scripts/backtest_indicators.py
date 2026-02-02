#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
技术指标回测系统
验证技术指标在当前市场下的有效性
"""

import sys
sys.path.append('/home/parallels/.openclaw/workspace/skills/a-stock-fetcher/scripts')
from historical_data import fetch_historical_data
from indicators_v2 import calculate_all_indicators
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json

class SignalEvent:
    """信号事件"""
    def __init__(self, date: str, signal_type: str, price: float,
                 rsi: float, macd_hist: float, k: float, d: float):
        self.date = date
        self.signal_type = signal_type
        self.price = price
        self.rsi = rsi
        self.macd_hist = macd_hist
        self.k = k
        self.d = d

class BacktestResult:
    """回测结果"""
    def __init__(self):
        self.total_signals = 0
        self.profitable_signals = 0
        self.win_rate = 0.0
        self.total_profit = 0.0
        self.total_loss = 0.0
        self.avg_profit = 0.0
        self.avg_loss = 0.0
        self.profit_loss_ratio = 0.0
        self.profits_3d = []
        self.profits_5d = []
        self.profits_10d = []
        self.signals = []

    def add_signal(self, signal: SignalEvent, profit_3d: float,
                   profit_5d: float, profit_10d: float):
        """添加信号"""
        self.signals.append({
            'date': signal.date,
            'type': signal.signal_type,
            'price': signal.price,
            'rsi': signal.rsi,
            'macd_hist': signal.macd_hist,
            'k': signal.k,
            'd': signal.d,
            'profit_3d': profit_3d,
            'profit_5d': profit_5d,
            'profit_10d': profit_10d
        })

        self.profits_3d.append(profit_3d)
        self.profits_5d.append(profit_5d)
        self.profits_10d.append(profit_10d)

        self.total_signals += 1
        if profit_5d > 0:
            self.profitable_signals += 1
            self.total_profit += profit_5d
        else:
            self.total_loss += abs(profit_5d)

    def calculate_metrics(self):
        """计算指标"""
        if self.total_signals == 0:
            return

        self.win_rate = (self.profitable_signals / self.total_signals) * 100

        if self.profitable_signals > 0:
            self.avg_profit = self.total_profit / self.profitable_signals
        if (self.total_signals - self.profitable_signals) > 0:
            self.avg_loss = self.total_loss / (self.total_signals - self.profitable_signals)

        if self.avg_loss > 0:
            self.profit_loss_ratio = self.avg_profit / self.avg_loss
        else:
            self.profit_loss_ratio = float('inf')

def identify_signals(candles: List[Dict], indicators: Dict) -> Dict[str, List[SignalEvent]]:
    """
    识别技术指标信号

    Returns:
        {
            'rsi_oversold_buy': [],      # RSI超卖买入
            'rsi_overbought_sell': [],    # RSI超买卖出
            'macd_golden_cross': [],      # MACD金叉
            'kdj_golden_cross': []        # KDJ金叉
        }
    """
    signals = {
        'rsi_oversold_buy': [],
        'rsi_overbought_sell': [],
        'macd_golden_cross': [],
        'kdj_golden_cross': []
    }

    if len(candles) < 2:
        return signals

    # RSI
    rsi = indicators.get('rsi', [])
    # MACD
    macd_hist = indicators.get('macd', {}).get('histogram', [])
    # KDJ
    k = indicators.get('kdj', {}).get('K', [])
    d = indicators.get('kdj', {}).get('D', [])

    for i in range(len(candles)):
        # 确保至少有1天前数据
        if i < 1:
            continue

        # 确保所有指标都有足够的数据
        if (i >= len(rsi) or i >= len(k) or i >= len(d) or
            not rsi[i] or not k[i] or not d[i] or
            not rsi[i-1] or not k[i-1] or not d[i-1]):
            continue

        # 信号1: RSI超卖+金叉
        # RSI超卖：RSI < 30
        # 金叉：K线上穿D线
        rsi_oversold = rsi[i] < 30
        kdj_golden = k[i] > d[i] and k[i-1] <= d[i-1]

        if rsi_oversold and kdj_golden:
            signals['rsi_oversold_buy'].append(
                SignalEvent(
                    date=candles[i]['date'],
                    signal_type='rsi_oversold_buy',
                    price=candles[i]['close'],
                    rsi=rsi[i],
                    macd_hist=macd_hist[i] if macd_hist and i < len(macd_hist) else None,
                    k=k[i],
                    d=d[i]
                )
            )

        # 信号2: RSI超买+死叉
        # RSI超买：RSI > 70
        # 死叉：K线下穿D线
        rsi_overbought = rsi[i] > 70
        kdj_death = k[i] < d[i] and k[i-1] >= d[i-1]

        if rsi_overbought and kdj_death:
            signals['rsi_overbought_sell'].append(
                SignalEvent(
                    date=candles[i]['date'],
                    signal_type='rsi_overbought_sell',
                    price=candles[i]['close'],
                    rsi=rsi[i],
                    macd_hist=macd_hist[i] if i < len(macd_hist) and macd_hist[i] is not None else None,
                    k=k[i],
                    d=d[i]
                )
            )

        # 信号3: MACD金叉
        # MACD柱状图从负变正
        if (i < len(macd_hist) and macd_hist[i] is not None and
            i >= 1 and macd_hist[i-1] is not None):
            if macd_hist[i] > 0 and macd_hist[i-1] <= 0:
                signals['macd_golden_cross'].append(
                    SignalEvent(
                        date=candles[i]['date'],
                        signal_type='macd_golden_cross',
                        price=candles[i]['close'],
                        rsi=rsi[i] if i < len(rsi) else None,
                        macd_hist=macd_hist[i],
                        k=k[i] if i < len(k) else None,
                        d=d[i] if i < len(d) else None
                    )
                )

        # 信号4: KDJ金叉
        # K线上穿D线
        if k[i] > d[i] and k[i-1] <= d[i-1]:
            signals['kdj_golden_cross'].append(
                SignalEvent(
                    date=candles[i]['date'],
                    signal_type='kdj_golden_cross',
                    price=candles[i]['close'],
                    rsi=rsi[i] if i < len(rsi) else None,
                    macd_hist=macd_hist[i] if i < len(macd_hist) and macd_hist[i] is not None else None,
                    k=k[i],
                    d=d[i]
                )
            )

    return signals

def calculate_future_returns(candles: List[Dict], signal_index: int) -> Tuple[float, float, float]:
    """
    计算信号后的收益

    Returns:
        (3天收益, 5天收益, 10天收益)
    """
    signal_price = candles[signal_index]['close']

    profit_3d = 0.0
    profit_5d = 0.0
    profit_10d = 0.0

    # 3天后
    if signal_index + 3 < len(candles):
        future_price = candles[signal_index + 3]['close']
        profit_3d = (future_price - signal_price) / signal_price * 100

    # 5天后
    if signal_index + 5 < len(candles):
        future_price = candles[signal_index + 5]['close']
        profit_5d = (future_price - signal_price) / signal_price * 100

    # 10天后
    if signal_index + 10 < len(candles):
        future_price = candles[signal_index + 10]['close']
        profit_10d = (future_price - signal_price) / signal_price * 100

    return profit_3d, profit_5d, profit_10d

def backtest_stock(symbol: str, days: int = 120) -> Dict[str, BacktestResult]:
    """
    回测单只股票

    Args:
        symbol: 股票代码
        days: 回测天数（约6个月）

    Returns:
        各信号的回测结果
    """
    print(f"\n📊 回测 {symbol} ({days}天日K)...")

    # 获取历史数据
    candles = fetch_historical_data(symbol, '1d', days)
    if not candles or len(candles) < 30:
        print(f"❌ 数据不足")
        return {}

    # 计算技术指标
    indicators = calculate_all_indicators(candles)

    # 识别信号
    signals = identify_signals(candles, indicators)

    # 回测各信号
    results = {}

    for signal_type, signal_events in signals.items():
        result = BacktestResult()

        for event in signal_events:
            # 找到信号对应的索引
            signal_index = None
            for i, candle in enumerate(candles):
                if candle['date'] == event.date:
                    signal_index = i
                    break

            if signal_index is None:
                continue

            # 计算未来收益
            profit_3d, profit_5d, profit_10d = calculate_future_returns(
                candles, signal_index
            )

            # 只添加有足够数据的信号
            if signal_index + 10 < len(candles):
                result.add_signal(event, profit_3d, profit_5d, profit_10d)

        # 计算指标
        result.calculate_metrics()
        results[signal_type] = result

        # 打印结果
        if result.total_signals > 0:
            signal_name = {
                'rsi_oversold_buy': 'RSI超卖+金叉买入',
                'rsi_overbought_sell': 'RSI超买+死叉卖出',
                'macd_golden_cross': 'MACD金叉',
                'kdj_golden_cross': 'KDJ金叉'
            }.get(signal_type, signal_type)

            print(f"  {signal_name}:")
            print(f"    信号次数: {result.total_signals}")
            print(f"    胜率: {result.win_rate:.1f}%")
            print(f"    平均盈亏比: {result.profit_loss_ratio:.2f}")
            print(f"    5天平均收益: {sum(result.profits_5d)/len(result.profits_5d) if result.profits_5d else 0:.2f}%")
        else:
            print(f"  {signal_type}: 无信号")

    return results

def backtest_multiple_stocks(symbols: List[str], days: int = 120) -> Dict[str, Dict]:
    """
    批量回测

    Args:
        symbols: 股票代码列表
        days: 回测天数

    Returns:
        {symbol: {signal_type: BacktestResult}}
    """
    all_results = {}

    for symbol in symbols:
        results = backtest_stock(symbol, days)
        if results:
            all_results[symbol] = results

    return all_results

def aggregate_results(all_results: Dict) -> Dict:
    """
    汇总所有结果

    Args:
        all_results: {symbol: {signal_type: BacktestResult}}

    Returns:
        各信号的汇总统计
    """
    aggregated = {
        'rsi_oversold_buy': BacktestResult(),
        'rsi_overbought_sell': BacktestResult(),
        'macd_golden_cross': BacktestResult(),
        'kdj_golden_cross': BacktestResult()
    }

    for symbol, results in all_results.items():
        for signal_type, result in results.items():
            aggregated[signal_type].total_signals += result.total_signals
            aggregated[signal_type].profitable_signals += result.profitable_signals
            aggregated[signal_type].total_profit += result.total_profit
            aggregated[signal_type].total_loss += result.total_loss
            aggregated[signal_type].profits_3d.extend(result.profits_3d)
            aggregated[signal_type].profits_5d.extend(result.profits_5d)
            aggregated[signal_type].profits_10d.extend(result.profits_10d)

    # 计算指标
    for signal_type, result in aggregated.items():
        result.calculate_metrics()

    return aggregated

def format_aggregated_results(aggregated: Dict) -> str:
    """格式化汇总结果"""
    output = f"""
{'='*80}
📊 技术指标回测汇总结果
{'='*80}
"""

    signal_names = {
        'rsi_oversold_buy': 'RSI超卖+金叉 (买入)',
        'rsi_overbought_sell': 'RSI超买+死叉 (卖出)',
        'macd_golden_cross': 'MACD金叉 (多头)',
        'kdj_golden_cross': 'KDJ金叉 (买入)'
    }

    for signal_type, result in aggregated.items():
        if result.total_signals == 0:
            continue

        signal_name = signal_names.get(signal_type, signal_type)

        output += f"""
{signal_name}
{'─'*80}
  信号次数:      {result.total_signals}
  盈利次数:      {result.profitable_signals}
  胜率:          {result.win_rate:.1f}%
{'─'*80}
  3天平均收益:   {sum(result.profits_3d)/len(result.profits_3d) if result.profits_3d else 0:.2f}%
  5天平均收益:   {sum(result.profits_5d)/len(result.profits_5d) if result.profits_5d else 0:.2f}%
  10天平均收益:  {sum(result.profits_10d)/len(result.profits_10d) if result.profits_10d else 0:.2f}%
{'─'*80}
  平均盈利:      ¥{result.avg_profit:.2f}
  平均亏损:      ¥{result.avg_loss:.2f}
  盈亏比:        {result.profit_loss_ratio:.2f}
{'─'*80}
"""

    return output

if __name__ == "__main__":
    # 测试样本
    symbols = [
        # 热门股
        'sz300750',  # 宁德时代
        'sz002594',  # 比亚迪
        'sh600036',  # 招商银行
        'sz300059',  # 东方财富
        'sh600519',  # 茅台
        'sz000858',  # 五粮液
        # 冷门股
        'sh600019',  # 宝钢股份
        'sh601088',  # 中国神华
        'sh601009',  # 南京银行
        'sz000728',  # 国元证券
        # 题材股
        'sh688981',  # 中芯国际
        'sz002230'   # 科大讯飞
    ]

    print("="*80)
    print("🧪 技术指标回测系统")
    print("="*80)

    # 回测
    all_results = backtest_multiple_stocks(symbols, days=120)

    # 汇总
    aggregated = aggregate_results(all_results)

    # 输出结果
    print(format_aggregated_results(aggregated))

    # 保存结果
    output_data = {
        'backtest_date': datetime.now().isoformat(),
        'symbols': symbols,
        'signals': {}
    }

    for signal_type, result in aggregated.items():
        if result.total_signals > 0:
            output_data['signals'][signal_type] = {
                'total_signals': result.total_signals,
                'profitable_signals': result.profitable_signals,
                'win_rate': result.win_rate,
                'avg_profit_3d': sum(result.profits_3d)/len(result.profits_3d) if result.profits_3d else 0,
                'avg_profit_5d': sum(result.profits_5d)/len(result.profits_5d) if result.profits_5d else 0,
                'avg_profit_10d': sum(result.profits_10d)/len(result.profits_10d) if result.profits_10d else 0,
                'avg_profit': result.avg_profit,
                'avg_loss': result.avg_loss,
                'profit_loss_ratio': result.profit_loss_ratio
            }

    output_file = "/tmp/a_stock_backtest_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 回测结果已保存至: {output_file}")
