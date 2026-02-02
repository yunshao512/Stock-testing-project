#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票池管理器 + 选股算法 + 交易跟踪系统
半年历史数据 + 每日选10只 + 交易记录 + 统计分析
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import random
import statistics


class StockPoolManager:
    """股票池管理器"""

    def __init__(self):
        self.pool: Dict[str, Dict] = {}  # 股票池
        self.selected_stocks: Set[str] = set()  # 已选股票
        self.tracking_records: List[Dict] = []  # 交易记录

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

    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """获取股票信息"""
        return self.pool.get(symbol, None)


class StockSelector:
    """选股算法"""

    def __init__(self, pool_manager: StockPoolManager):
        self.pool_manager = pool_manager
        print("✅ 选股算法初始化完成")

    def select_top_n(self, n: int = 10) -> List[Dict]:
        """
        从股票池选择top N只股票

        选股策略：
        1. 综合评分排序
        2. 市值适中（10-100亿优先）
        3. 行业分散（不超过3只同行业）
        4. 避免重复选择
        """
        print(f"\n📊 [选股] 从池中选择前{n}只股票")
        print(f"  池大小: {self.pool_manager.get_pool_size()}只")
        print(f"  已选数量: {len(self.pool_manager.selected_stocks)}只")

        # 获取股票池
        stocks = list(self.pool_manager.pool.values())

        # 1. 基础筛选（评分>50）
        stocks = [s for s in stocks if s.get('score', 0) > 0.5]

        if not stocks:
            print("  ❌ 池中无可用股票")
            return []

        # 2. 排序（综合评分）
        stocks_sorted = sorted(stocks, key=lambda x: x.get('score', 0), reverse=True)

        # 3. 行业分散（不选超过3只同行业）
        industry_count = {}
        selected_stocks = []

        for stock in stocks_sorted:
            industry = stock.get('industry', '未知')

            # 检查行业数量
            if industry_count.get(industry, 0) >= 3:
                continue

            # 避免重复选择
            if stock['symbol'] in self.pool_manager.selected_stocks:
                continue

            # 选入
            selected_stocks.append(stock)
            industry_count[industry] = industry_count.get(industry, 0) + 1

            # 记录已选
            self.pool_manager.selected_stocks.add(stock['symbol'])

            # 达到目标数量
            if len(selected_stocks) >= n:
                break

        print(f"  ✅ 选出{len(selected_stocks)}只股票")

        # 4. 行业分散统计
        print(f"  行业分布:")
        for industry, count in industry_count.items():
            print(f"    {industry}: {count}只")

        return selected_stocks


class HalfYearHistory:
    """半年历史数据生成器"""

    def __init__(self):
        print("✅ 半年历史数据生成器初始化完成")

    def generate_history(self, symbol: str, days: int = 180) -> List[Dict]:
        """
        生成半年历史数据（约120个交易日）
        """
        # 根据股票代码确定基准价格
        if symbol.startswith('6'):
            base_price = random.uniform(20, 100)
        elif symbol.startswith('3'):
            base_price = random.uniform(10, 50)
        elif symbol.startswith('0'):
            base_price = random.uniform(10, 50)
        else:
            base_price = random.uniform(10, 100)

        # 确定趋势
        trend_type = random.choice(['上涨', '上涨', '横盘', '下跌'])
        if trend_type == '上涨':
            trend_factor = 0.001  # 温和上涨
        elif trend_type == '下跌':
            trend_factor = -0.0008  # 温和下跌
        else:
            trend_factor = random.uniform(-0.0005, 0.0005)  # 震荡

        # 生成180天历史
        candles = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')

            # 添加趋势和波动
            price_change = base_price * trend_factor * (1 + random.uniform(-0.3, 0.5))
            open_price = base_price * (1 + random.uniform(-0.015, 0.015))
            close_price = open_price + price_change

            # 高开低走
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.01))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.01))

            volume = random.randint(5000000, 50000000)
            amount = round(volume * close_price, 2)

            candles.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'amount': amount
            })

            base_price = close_price

        return candles


class TradingTracker:
    """交易跟踪系统"""

    def __init__(self):
        self.trades: List[Dict] = []
        self.holdings: Dict[str, Dict] = {}  # 持仓
        self.performance_history: List[Dict] = []  # 绩效历史

        print("✅ 交易跟踪系统初始化完成")

    def record_selection(self, symbol: str, select_date: str, price: float, days: int):
        """
        记录选股
        """
        trade = {
            'type': 'select',
            'symbol': symbol,
            'date': select_date,
            'price': price,
            'days': days,
            'timestamp': datetime.now().isoformat()
        }

        self.trades.append(trade)
        print(f"  ✅ 记录选股: {symbol} @ ¥{price:.2f} ({days}天)")

    def record_sell(self, symbol: str, sell_date: str, price: float, buy_price: float):
        """
        记录卖股
        """
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
        print(f"\n📊 [分析] 选股和交易绩效分析")

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

        # 统计
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
        win_rate = len(profitable_trades) / len(sell_trades) if sell_trades else 0

        # 计算平均收益
        avg_profit = statistics.mean([t['profit_percent'] for t in sell_trades])
        total_profit = sum(t['profit_amount'] for t in sell_trades)

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

    def analyze_stock_selection_accuracy(self, tracker: TradingTracker, history_generator: HalfYearHistory) -> Dict:
        """
        分析选股准确度（预测股票未来3-5天的涨跌胜率）
        """
        print(f"\n📊 [分析] 选股准确度分析")

        # 模拟选股和预测
        selected_stocks = list(tracker.get_current_holdings().keys())
        symbol = selected_stocks[0] if selected_stocks else None

        if not symbol:
            return {
                'symbol': 'N/A',
                'predict_days': 0,
                'correct_days': 0,
                'accuracy': 0
            }

        # 获取半年历史
        history = history_generator.generate_history(symbol, days=180)

        if len(history) < 10:
            return {
                'symbol': symbol,
                'predict_days': 0,
                'correct_days': 0,
                'accuracy': 0
            }

        # 预测3-5天
        predict_days_list = [3, 5]
        results = {}

        for predict_days in predict_days_list:
            # 使用前180-预测天数的数据预测
            base_history = history[:-(predict_days)]

            if not base_history:
                continue

            # 计算趋势
            prices = [c['close'] for c in base_history]
            short_trend = (prices[-1] - prices[-6]) / prices[-6] if len(prices) > 6 else 0

            # 预测方向
            if short_trend > 0.02:
                predicted_directions = ['上涨'] * predict_days
            elif short_trend < -0.02:
                predicted_directions = ['下跌'] * predict_days
            else:
                predicted_directions = ['横盘'] * predict_days

            # 对比实际
            actual_data = history[-predict_days:]
            correct = 0

            for i in range(predict_days):
                prev_close = actual_data[i-1]['close'] if i > 0 else actual_data[i]['open']
                if actual_data[i]['close'] > prev_close:
                    actual_direction = '上涨'
                elif actual_data[i]['close'] < prev_close:
                    actual_direction = '下跌'
                else:
                    actual_direction = '横盘'

                # 预测正确或实际为横盘
                is_correct = (predicted_directions[i] == actual_direction) or (actual_direction == '横盘')

                if is_correct:
                    correct += 1

            accuracy = correct / predict_days

            results[predict_days] = {
                'correct_days': correct,
                'accuracy': accuracy
            }

            print(f"  {predict_days}天预测: 正确{correct}/{predict_days}天, 准确率{accuracy*100:.1f}%")

        return {
            'symbol': symbol,
            'predict_days': predict_days_list,
            'results': results
        }


def test_system():
    """测试完整系统"""
    print("="*80)
    print("🧪 测试半年数据+选股+跟踪系统")
    print("="*80)
    print()

    # 1. 生成股票池（使用前面的漏斗筛选结果）
    print(f"\n📊 [1/6] 生成股票池（500只，模拟漏斗筛选后）")
    pool_stocks = []

    # 模拟80只高质量股票
    for i in range(80):
        code_prefix = random.choice(['00', '6', '3', '688'])
        code = f"{code_prefix}{random.randint(100000, 999999):06d}"

        stock = {
            'symbol': code,
            'name': f"股票{i}",
            'board': random.choice(['深证', '沪证', '创业板', '科创板']),
            'market_cap': random.uniform(10, 200),
            'industry': random.choice(['科技', '消费', '医疗', '新能源', '金融']),
            'score': random.uniform(0.6, 0.8),  # 综合评分60-80
            'profit_growth': random.choice([0.1, 0.15, 0.2, 0.3]),
            'is_loss_3years': False
            'is_bad_rating': False
            'is_bubble': False
        }

        pool_stocks.append(stock)

    # 2. 创建管理器
    print(f"\n📊 [2/6] 创建管理器")
    pool_manager = StockPoolManager()
    pool_manager.update_pool(pool_stocks)

    # 3. 创建历史生成器
    print(f"\n📊 [3/6] 创建历史生成器")
    history_gen = HalfYearHistory()

    # 4. 模拟10个交易日的选股和跟踪
    print(f"\n📊 [4/6] 模拟10个交易日")

    selector = StockSelector(pool_manager)
    tracker = TradingTracker()
    analyzer = StatisticalAnalyzer()

    for day in range(10):
        print(f"\n{'='*80}")
        print(f"📅 第{day+1}个交易日")
        print(f"{'='*80}")

        # 每日选10只
        selected_stocks = selector.select_top_n(n=10)

        for stock in selected_stocks:
            # 模拟买入价格
            buy_price = random.uniform(10, 100)

            # 记录选股（持仓5天）
            select_date = (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d')
            tracker.record_selection(stock['symbol'], select_date, buy_price, days=5)

        # 模拟卖出（部分持仓到期）
        if day >= 5:
            # 随机卖出5天前选的股票
            old_selections = [t for t in tracker.trades if t['type'] == 'select' and t['days'] == 5]

            for trade in old_selections[:3]:  # 卖出3只
                # 模拟卖出价格
                sell_price = trade['price'] * random.uniform(0.95, 1.08)

                # 记录卖股
                sell_date = (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d')
                tracker.record_sell(trade['symbol'], sell_date, sell_price, trade['price'])

    # 5. 分析绩效
    print(f"\n📊 [5/6] 分析绩效")
    performance = analyzer.analyze_selection_performance(tracker)

    print(f"\n📊 [6/6] 分析选股准确度")
    accuracy = analyzer.analyze_stock_selection_accuracy(tracker, history_gen)

    # 6. 最终总结
    print(f"\n{'='*80}")
    print(f"📊 最终总结")
    print(f"{'='*80}")

    print(f"选股数量: {performance['select_trades']}次")
    print(f"交易数量: {performance['total_trades']}次")
    print(f"胜率: {performance['win_rate']*100:.1f}%")
    print(f"平均收益: {performance['avg_profit']:+.2f}%")
    print(f"总盈利: ¥{performance['total_profit']:,.2f}")

    if accuracy.get('results'):
        print(f"\n选股准确度:")
        for days, result in accuracy['results'].items():
            print(f"  {days}天预测: {result['accuracy']*100:.1f}%")

    print(f"\n✅ 测试完成")


if __name__ == "__main__":
    test_system()
