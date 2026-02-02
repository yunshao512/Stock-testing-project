#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交易记录系统 v1.0
记录所有交易决策、执行结果和复盘分析
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# 数据文件路径
DATA_DIR = "/tmp/a_stock_trading"
TRADING_LOG_FILE = os.path.join(DATA_DIR, "trading_log.json")
POSITIONS_FILE = os.path.join(DATA_DIR, "positions.json")
PERFORMANCE_FILE = os.path.join(DATA_DIR, "performance.json")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

class TradingRecord:
    """交易记录"""

    def __init__(self, symbol: str, action: str, price: float, quantity: int,
                 stop_loss: float = None, take_profit: float = None,
                 reason: str = "", confidence: float = 0.0):
        """
        创建交易记录

        Args:
            symbol: 股票代码
            action: 买入/卖出
            price: 价格
            quantity: 数量
            stop_loss: 止损价
            take_profit: 止盈价
            reason: 交易理由
            confidence: 信心度（0-1）
        """
        self.timestamp = datetime.now().isoformat()
        self.symbol = symbol
        self.action = action  # 'buy' or 'sell'
        self.price = price
        self.quantity = quantity
        self.amount = price * quantity
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.reason = reason
        self.confidence = confidence

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'timestamp': self.timestamp,
            'symbol': self.symbol,
            'action': self.action,
            'price': self.price,
            'quantity': self.quantity,
            'amount': self.amount,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'reason': self.reason,
            'confidence': self.confidence
        }

class Position:
    """持仓"""

    def __init__(self, symbol: str, buy_price: float, quantity: int,
                 stop_loss: float, take_profit: float, reason: str = ""):
        """
        创建持仓

        Args:
            symbol: 股票代码
            buy_price: 买入价
            quantity: 数量
            stop_loss: 止损价
            take_profit: 止盈价
            reason: 买入理由
        """
        self.symbol = symbol
        self.buy_price = buy_price
        self.buy_time = datetime.now().isoformat()
        self.quantity = quantity
        self.cost = buy_price * quantity
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.reason = reason
        self.current_price = buy_price
        self.current_value = self.cost
        self.unrealized_pnl = 0.0
        self.unrealized_pnl_pct = 0.0
        self.highest_price = buy_price  # 最高价（用于移动止损）
        self.lowest_price = buy_price   # 最低价

    def update_price(self, current_price: float):
        """更新当前价格"""
        self.current_price = current_price
        self.current_value = current_price * self.quantity
        self.unrealized_pnl = self.current_value - self.cost
        self.unrealized_pnl_pct = (self.unrealized_pnl / self.cost) * 100

        # 更新最高最低价
        if current_price > self.highest_price:
            self.highest_price = current_price
        if current_price < self.lowest_price:
            self.lowest_price = current_price

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'buy_price': self.buy_price,
            'buy_time': self.buy_time,
            'quantity': self.quantity,
            'cost': self.cost,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'reason': self.reason,
            'current_price': self.current_price,
            'current_value': self.current_value,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_pct': self.unrealized_pnl_pct,
            'highest_price': self.highest_price,
            'lowest_price': self.lowest_price
        }

class TradingSystem:
    """交易系统"""

    def __init__(self, initial_capital: float = 100000.0):
        """
        初始化交易系统

        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.available_capital = initial_capital
        self.positions = {}  # {symbol: Position}
        self.trading_log = []  # List[TradingRecord]
        self.completed_trades = []  # 已完成的交易

        # 加载历史数据
        self._load_data()

    def _load_data(self):
        """加载历史数据"""
        # 加载持仓
        if os.path.exists(POSITIONS_FILE):
            try:
                with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for symbol, pos_data in data.items():
                        position = Position(
                            symbol=pos_data['symbol'],
                            buy_price=pos_data['buy_price'],
                            quantity=pos_data['quantity'],
                            stop_loss=pos_data['stop_loss'],
                            take_profit=pos_data['take_profit'],
                            reason=pos_data.get('reason', '')
                        )
                        position.buy_time = pos_data['buy_time']
                        position.current_price = pos_data['current_price']
                        position.highest_price = pos_data['highest_price']
                        position.lowest_price = pos_data['lowest_price']
                        self.positions[symbol] = position

                    # 更新可用资金
                    total_invested = sum(p.cost for p in self.positions.values())
                    self.available_capital = self.current_capital - total_invested

            except Exception as e:
                print(f"⚠️ 加载持仓数据失败: {e}")

        # 加载交易日志
        if os.path.exists(TRADING_LOG_FILE):
            try:
                with open(TRADING_LOG_FILE, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                    for record in log_data:
                        trading_record = TradingRecord(
                            symbol=record['symbol'],
                            action=record['action'],
                            price=record['price'],
                            quantity=record['quantity'],
                            stop_loss=record.get('stop_loss'),
                            take_profit=record.get('take_profit'),
                            reason=record.get('reason', ''),
                            confidence=record.get('confidence', 0.0)
                        )
                        trading_record.timestamp = record['timestamp']
                        self.trading_log.append(trading_record)

            except Exception as e:
                print(f"⚠️ 加载交易日志失败: {e}")

    def _save_data(self):
        """保存数据"""
        # 保存持仓
        positions_data = {symbol: pos.to_dict() for symbol, pos in self.positions.items()}
        with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(positions_data, f, ensure_ascii=False, indent=2)

        # 保存交易日志
        log_data = [record.to_dict() for record in self.trading_log]
        with open(TRADING_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

    def buy(self, symbol: str, price: float, quantity: int,
            stop_loss_pct: float = 0.05, take_profit_pct: float = 0.10,
            reason: str = "", confidence: float = 0.0) -> bool:
        """
        买入

        Args:
            symbol: 股票代码
            price: 价格
            quantity: 数量
            stop_loss_pct: 止损百分比（默认5%）
            take_profit_pct: 止盈百分比（默认10%）
            reason: 买入理由
            confidence: 信心度

        Returns:
            是否成功
        """
        amount = price * quantity

        # 检查资金是否充足
        if amount > self.available_capital:
            print(f"❌ 资金不足: 需要 ¥{amount:.2f}, 可用 ¥{self.available_capital:.2f}")
            return False

        # 计算止损止盈价
        stop_loss = price * (1 - stop_loss_pct)
        take_profit = price * (1 + take_profit_pct)

        # 创建持仓
        position = Position(symbol, price, quantity, stop_loss, take_profit, reason)
        self.positions[symbol] = position

        # 记录交易
        record = TradingRecord(symbol, 'buy', price, quantity, stop_loss, take_profit,
                             reason, confidence)
        self.trading_log.append(record)

        # 更新资金
        self.available_capital -= amount

        # 保存数据
        self._save_data()

        print(f"✅ 买入 {symbol}: ¥{price:.2f} × {quantity} = ¥{amount:.2f}")
        print(f"   止损: ¥{stop_loss:.2f} | 止盈: ¥{take_profit:.2f}")
        print(f"   理由: {reason}")
        print(f"   信心: {confidence*100:.0f}%")

        return True

    def sell(self, symbol: str, price: float, reason: str = "") -> bool:
        """
        卖出

        Args:
            symbol: 股票代码
            price: 价格
            reason: 卖出理由

        Returns:
            是否成功
        """
        if symbol not in self.positions:
            print(f"❌ 未持有 {symbol}")
            return False

        position = self.positions[symbol]
        amount = price * position.quantity
        pnl = amount - position.cost
        pnl_pct = (pnl / position.cost) * 100

        # 记录交易
        record = TradingRecord(symbol, 'sell', price, position.quantity,
                             reason=reason, confidence=0.0)
        self.trading_log.append(record)

        # 记录完成交易
        self.completed_trades.append({
            'symbol': symbol,
            'buy_price': position.buy_price,
            'sell_price': price,
            'quantity': position.quantity,
            'cost': position.cost,
            'revenue': amount,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'hold_days': self._calculate_hold_days(position),
            'buy_reason': position.reason,
            'sell_reason': reason
        })

        # 更新资金
        self.available_capital += amount
        self.current_capital = self.available_capital + sum(
            p.current_value for p in self.positions.values() if p.symbol != symbol
        )

        # 删除持仓
        del self.positions[symbol]

        # 保存数据
        self._save_data()

        arrow = "↑" if pnl > 0 else "↓" if pnl < 0 else "→"
        print(f"✅ 卖出 {symbol}: ¥{price:.2f} × {position.quantity} = ¥{amount:.2f}")
        print(f"   盈亏: {arrow}¥{abs(pnl):.2f} ({pnl_pct:+.2f}%)")
        print(f"   理由: {reason}")

        return True

    def update_positions(self, stock_data: Dict):
        """
        更新持仓价格

        Args:
            stock_data: 股票数据 {symbol: price}
        """
        for symbol, position in self.positions.items():
            if symbol in stock_data:
                position.update_price(stock_data[symbol])

        self._save_data()

    def check_stop_loss_take_profit(self, stock_data: Dict) -> List[Dict]:
        """
        检查止损止盈

        Args:
            stock_data: 股票数据 {symbol: price}

        Returns:
            需要执行的卖出信号列表
        """
        signals = []

        for symbol, position in self.positions.items():
            if symbol not in stock_data:
                continue

            current_price = stock_data[symbol]

            # 检查止损
            if current_price <= position.stop_loss:
                signals.append({
                    'symbol': symbol,
                    'action': 'sell',
                    'reason': '止损',
                    'price': current_price
                })

            # 检查止盈
            elif current_price >= position.take_profit:
                signals.append({
                    'symbol': symbol,
                    'action': 'sell',
                    'reason': '止盈',
                    'price': current_price
                })

        return signals

    def _calculate_hold_days(self, position: Position) -> int:
        """计算持仓天数"""
        buy_time = datetime.fromisoformat(position.buy_time)
        now = datetime.now()
        return (now - buy_time).days

    def get_summary(self) -> Dict:
        """获取摘要信息"""
        # 计算持仓价值
        position_value = sum(p.current_value for p in self.positions.values())
        total_value = self.available_capital + position_value

        # 计算总盈亏
        total_pnl = total_value - self.initial_capital
        total_pnl_pct = (total_pnl / self.initial_capital) * 100

        # 统计已完成交易
        total_trades = len(self.completed_trades)
        profitable_trades = sum(1 for t in self.completed_trades if t['pnl'] > 0)
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0

        # 平均盈亏
        avg_pnl_pct = sum(t['pnl_pct'] for t in self.completed_trades) / total_trades if total_trades > 0 else 0

        # 最大盈利/亏损
        max_profit = max([t['pnl_pct'] for t in self.completed_trades]) if self.completed_trades else 0
        max_loss = min([t['pnl_pct'] for t in self.completed_trades]) if self.completed_trades else 0

        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'available_capital': self.available_capital,
            'position_value': position_value,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'position_count': len(self.positions),
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': win_rate,
            'avg_pnl_pct': avg_pnl_pct,
            'max_profit': max_profit,
            'max_loss': max_loss
        }

    def format_summary(self) -> str:
        """格式化摘要"""
        summary = self.get_summary()

        arrow = "↑" if summary['total_pnl'] > 0 else "↓" if summary['total_pnl'] < 0 else "→"
        color = "🟢" if summary['total_pnl'] > 0 else "🔴" if summary['total_pnl'] < 0 else "⚪"

        return f"""
💰 账户摘要
{'─'*60}
  初始资金: ¥{summary['initial_capital']:,.2f}
  当前总值: ¥{summary['total_value']:,.2f}
  可用资金: ¥{summary['available_capital']:,.2f}
  持仓价值: ¥{summary['position_value']:,.2f}
{'─'*60}
  总盈亏:   {color} {arrow}¥{abs(summary['total_pnl']):,.2f} ({summary['total_pnl_pct']:+.2f}%)
{'─'*60}
  持仓数量: {summary['position_count']}
  总交易数: {summary['total_trades']}
  盈利交易: {summary['profitable_trades']}
  胜率:     {summary['win_rate']:.1f}%
{'─'*60}
  平均收益: {summary['avg_pnl_pct']:+.2f}%
  最大盈利: +{summary['max_profit']:.2f}%
  最大亏损: {summary['max_loss']:.2f}%
{'─'*60}
"""
