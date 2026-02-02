#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
半年数据+选股+跟踪系统（修复版）
"""

import sys
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Set
import statistics


class StockPoolManager:
    """股票池管理器"""

    def __init__(self):
        self.pool: Dict[str, Dict] = {}
        self.selected_stocks: Set[str] = set()
        print("✅ 股票池管理器初始化完成")

    def update_pool(self, stocks: List[Dict]):
        """更新股票池"""
        print(f"  更新股票池：{len(stocks)}只")
        for stock in stocks:
            self.pool[stock['symbol']] = stock
        print(f"  当前池大小：{len(self.pool)}只")

    def get_pool_size(self) -> int:
        """获取池大小"""
        return len(self.pool)

    def is_in_pool(self, symbol: str) -> bool:
        """检查股票是否在池中"""
        return symbol in self.pool

    def get_stock_info(self, symbol: str) -> Dict:
        """获取股票信息"""
        return self.pool.get(symbol, {})

    def mark_selected(self, symbol: str):
        """标记为已选"""
        self.selected_stocks.add(symbol)


class StockSelector:
    """选股算法"""

    def __init__(self, pool_manager: StockPoolManager):
        self.pool_manager = pool_manager
        print("✅ 选股算法初始化完成")

    def select_top_n(self, n: int = 10) -> List[Dict]:
        """选择top N只股票"""
        print(f"\n📊 [选股] 从池中选择前{n}只股票")
        print(f"  池大小: {self.pool_manager.get_pool_size()}只")
        print(f"  已选数量: {len(self.pool_manager.selected_stocks)}只")

        # 获取股票池
        stocks = list(self.pool_manager.pool.values())

        # 排序（综合评分）
        stocks_sorted = sorted(stocks, key=lambda x: x.get('score', 0), reverse=True)

        # 选择未选过的股票
        selected = []
        for stock in stocks_sorted:
            if stock['symbol'] not in self.pool_manager.selected_stocks:
                selected.append(stock)
                self.pool_manager.mark_selected(stock['symbol'])

                if len(selected) >= n:
                    break

        print(f"  ✅ 选出{len(selected)}只股票")

        return selected


class HalfYearHistory:
    """半年历史数据生成器"""

    def __init__(self):
        print("✅ 半年历史数据生成器初始化完成")

    def generate_history(self, symbol: str, days: int = 180) -> List[Dict]:
        """生成半年历史数据（6个月，约120个交易日）"""
        # 根据股票代码确定基准价格
        if symbol.startswith('6'):
            base_price = random.uniform(20, 100)
        elif symbol.startswith('3'):
            base_price = random.uniform(10, 50)
        elif symbol.startswith('0'):
            base_price = random.uniform(10, 50)
        else:
            base_price = random.uniform(10, 100)

        # 确定趋势类型
        trend_type = random.choice(['上涨', '上涨', '横盘', '横盘', '下跌'])
        if trend_type == '上涨':
            trend_factor = 0.0015
        elif trend_type == '横盘':
            trend_factor = 0.0002
        elif trend_type == '下跌':
            trend_factor = -0.001
        else:
            trend_factor = random.uniform(-0.001, 0.0015)

        candles = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')

            # 价格变化（趋势+波动）
            volatility = random.uniform(0.5, 2.0)
            price_change = base_price * trend_factor * (1 + random.uniform(-0.3, 0.7)) + random.uniform(-0.5, 0.5)
            open_price = base_price * (1 + random.uniform(-0.01, 0.01))
            close_price = open_price + price_change
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.003))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.003))
            volume = random.randint(5000000, 50000000)

            candles.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'amount': round(volume * close_price, 2)
            })

            base_price = close_price

        return candles


class TradingTracker:
    """交易跟踪系统"""

    def __init__(self):
        self.trades: List[Dict] = []
        self.holdings: Dict[str, Dict] = {}
        self.performance_history: List[Dict] = []
        print("✅ 交易跟踪系统初始化完成")

    def record_selection(self, symbol: str, select_date: str, price: float):
        """记录选股"""
        trade = {
            'type': 'select',
            'symbol': symbol,
            'date': select_date,
            'price': price,
            'timestamp': datetime.now().isoformat()
        }

        self.trades.append(trade)
        print(f"  ✅ 记录选股: {symbol} @ ¥{price:.2f}")

    def record_sell(self, symbol: str, sell_date: str, price: float, buy_price: float):
        """记录卖股"""
        profit_percent = ((price - buy_price) / buy_price) * 100
        profit_amount = price - buy_price

        trade = {
            'type': 'sell',
            'symbol': symbol,
            'date': sell_date,
            'price': price,
            'buy_price': buy_price,
            'profit_percent': round(profit_percent, 2),
            'profit_amount': round(profit_amount, 2),
            'timestamp': datetime.now().isoformat()
        }

        self.trades.append(trade)
        print(f"  ✅ 记录卖股: {symbol} ¥{price:.2f} (买入¥{buy_price:.2f}) 盈利{profit_percent:+.2f}%")

        # 从持仓中移除
        if symbol in self.holdings:
            del self.holdings[symbol]

    def get_current_holdings(self) -> Dict[str, Dict]:
        """获取当前持仓"""
        return self.holdings

    def get_trade_history(self, symbol: str = None) -> List[Dict]:
        """获取交易历史"""
        if symbol:
            return [t for t in self.trades if t['symbol'] == symbol]
        return self.trades


class StatisticalAnalyzer:
    """统计分析系统"""

    def __init__(self):
        print("✅ 统计分析系统初始化完成")

    def analyze_selection_performance(self, tracker: TradingTracker) -> Dict:
        """分析选股和交易绩效"""
        print(f"\n📊 [统计] 选股和交易绩效分析")

        trades = tracker.trades

        if not trades:
            return {
                'total_trades': 0,
                'select_trades': 0,
                'sell_trades': 0,
                'avg_profit': 0,
                'win_rate': 0,
                'total_profit': 0
            }

        select_trades = [t for t in trades if t['type'] == 'select']
        sell_trades = [t for t in trades if t['type'] == 'sell']

        if not sell_trades:
            return {
                'total_trades': len(trades),
                'select_trades': len(select_trades),
                'sell_trades': 0,
                'avg_profit': 0,
                'win_rate': 0,
                'total_profit': 0
            }

        # 计算胜率
        profitable_trades = [t for t in sell_trades if t['profit_percent'] > 0]
        win_rate = len(profitable_trades) / len(sell_trades)

        # 计算平均收益
        avg_profit = statistics.mean([t['profit_percent'] for t in sell_trades])
        total_profit = sum([t['profit_amount'] for t in sell_trades])

        print(f"  总交易数: {len(trades)}")
        print(f"  选股次数: {len(select_trades)}")
        print(f"  卖股次数: {len(sell_trades)}")
        print(f"  盈利次数: {len(profitable_trades)}")
        print(f"  胜率: {win_rate*100:.1f}%")
        print(f"  平均收益: {avg_profit:+.2f}%")
        print(f"  总盈利: ¥{total_profit:,.2f}")

        return {
            'total_trades': len(trades),
            'select_trades': len(select_trades),
            'sell_trades': len(sell_trades),
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'total_profit': total_profit
        }

    def analyze_selection_accuracy(self, tracker: TradingTracker, history_generator: HalfYearHistory) -> Dict:
        """分析选股准确度（预测未来3-5天）"""
        print(f"\n📊 [统计] 选股准确度分析")

        selected_stocks = list(tracker.get_current_holdings().keys())

        if not selected_stocks:
            return {
                'symbol': 'N/A',
                'predict_days_3': {'accuracy': 0},
                'predict_days_5': {'accuracy': 0}
            }

        symbol = selected_stocks[0]
        history = history_generator.generate_history(symbol, days=180)

        if len(history) < 10:
            return {
                'symbol': symbol,
                'predict_days_3': {'accuracy': 0},
                'predict_days_5': {'accuracy': 0}
            }

        # 预测3天和5天
        results = {}
        for predict_days in [3, 5]:
            prices = [c['close'] for c in history]
            short_trend = (prices[-1] - prices[-6]) / prices[-6] if len(prices) > 6 else 0

            if short_trend > 0.01:
                predicted_directions = ['上涨'] * predict_days
            elif short_trend < -0.01:
                predicted_directions = ['下跌'] * predict_days
            else:
                predicted_directions = ['横盘'] * predict_days

            actual_data = history[-predict_days:]
            correct = 0

            for i in range(predict_days):
                if i == 0:
                    prev_close = actual_data[i-1]['close']
                else:
                    prev_close = actual_data[i-1]['close']

                if actual_data[i]['close'] > prev_close:
                    actual_direction = '上涨'
                elif actual_data[i]['close'] < prev_close:
                    actual_direction = '下跌'
                else:
                    actual_direction = '横盘'

                if predicted_directions[i] == actual_direction or actual_direction == '横盘':
                    correct += 1

            accuracy = correct / predict_days
            results[f'predict_days_{predict_days}'] = {'accuracy': accuracy, 'correct_days': correct}

        return {
            'symbol': symbol,
            'predict_days_3': results.get('predict_days_3', {'accuracy': 0}),
            'predict_days_5': results.get('predict_days_5', {'accuracy': 0})
        }


def test_system():
    """测试完整系统"""
    print("="*80)
    print("🧪 测试半年数据+选股+跟踪系统")
    print("="*80)
    print()

    # 1. 创建股票池（模拟500只股票）
    print(f"\n📊 [1/6] 创建股票池（500只高质量股票）")
    pool_manager = StockPoolManager()

    for i in range(500):
        code_prefix = random.choice(['00', '6', '3', '688'])
        code = f"{code_prefix}{random.randint(100000, 999999):06d}"

        name_parts = [
            ['科技', '智能', '新能源', '芯片', '生物'],
            ['股份', '集团', '科技', '控股', '动力'],
            ['中', '华', '国', '东', '西']
        ]
        name = ''.join(random.choice(part) for part in name_parts)

        stock = {
            'symbol': code,
            'name': name,
            'board': random.choice(['深证', '沪证', '创业板', '科创板']),
            'market_cap': random.uniform(10, 200),
            'industry': random.choice(['科技', '消费', '医疗', '新能源', '金融']),
            'score': random.uniform(0.6, 0.9),  # 高质量
            'profit_growth': random.choice([0.1, 0.15, 0.2, 0.25, 0.3]),
            'is_loss_3years': False,
            'is_bad_rating': False,
            'is_bubble': False
        }
        pool_manager.update_pool([stock])

    # 2. 模拟10个交易日的选股和跟踪
    print(f"\n📊 [2/6] 模拟10个交易日")
    print(f"{'='*80}")

    selector = StockSelector(pool_manager)
    tracker = TradingTracker()
    history_gen = HalfYearHistory()

    for day in range(10):
        print(f"\n{'='*80}")
        print(f"📅 第{day+1}个交易日")
        print(f"{'='*80}")

        # 每日选10只
        selected_stocks = selector.select_top_n(n=10)

        # 记录选股
        for stock in selected_stocks:
            select_date = (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d')
            buy_price = stock.get('score', 0) * 50 + 50  # 模拟买入价格
            tracker.record_selection(stock['symbol'], select_date, buy_price)

        # 模拟卖出（随机卖出5只）
        holdings = list(tracker.get_current_holdings().keys())
        if holdings:
            stocks_to_sell = random.sample(holdings, min(5, len(holdings)))

            for symbol in stocks_to_sell:
                sell_date = (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d')
                buy_price = tracker.trades[-1]['price']  # 简化取最新价格
                sell_price = buy_price * random.uniform(0.95, 1.10)  # 模拟卖出价格

                tracker.record_sell(symbol, sell_date, sell_price, buy_price)

    # 3. 分析绩效
    print(f"\n📊 [3/6] 分析绩效")
    print(f"{'='*80}")

    analyzer = StatisticalAnalyzer()
    performance = analyzer.analyze_selection_performance(tracker)

    # 4. 分析选股准确度
    print(f"\n📊 [4/6] 分析选股准确度")
    print(f"{'='*80}")

    accuracy = analyzer.analyze_selection_accuracy(tracker, history_gen)

    # 5. 最终总结
    print(f"\n📊 [5/6] 最终总结")
    print(f"{'='*80}")

    print(f"选股数量: {performance['select_trades']}")
    print(f"交易数量: {performance['total_trades']}")
    print(f"胜率: {performance['win_rate']*100:.1f}%")
    print(f"平均收益: {performance['avg_profit']:+.2f}%")
    print(f"总盈利: ¥{performance['total_profit']:,.2f}")

    if accuracy.get('predict_days_3'):
        print(f"\n3天预测准确度: {accuracy['predict_days_3']['accuracy']*100:.1f}%")
    if accuracy.get('predict_days_5'):
        print(f"5天预测准确度: {accuracy['predict_days_5']['accuracy']*100:.1f}%")

    print(f"\n✅ 测试完成")


if __name__ == "__main__":
    test_system()
