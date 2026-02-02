#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库管理 v1.0
使用SQLite存储所有数据
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import json

class StockDatabase:
    """股票数据库"""

    def __init__(self, db_path: str = "/tmp/a_stock_data.db"):
        """
        初始化数据库

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None

        # 连接数据库
        self._connect()

        # 创建表
        self._create_tables()

    def _connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # 支持字典访问
            self.cursor = self.conn.cursor()

            # 启用外键约束
            self.cursor.execute("PRAGMA foreign_keys = ON")

            # 优化性能
            self.cursor.execute("PRAGMA journal_mode = WAL")
            self.cursor.execute("PRAGMA synchronous = NORMAL")

            print(f"✅ 数据库连接成功: {self.db_path}")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise

    def _create_tables(self):
        """创建表"""
        print("📊 创建数据库表...")

        # 1. 股票池表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_pool (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                category_name TEXT,
                market_cap REAL,
                pe REAL,
                volume REAL,
                is_hot INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # 2. 信号历史表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                action TEXT NOT NULL,
                price REAL NOT NULL,
                confidence REAL NOT NULL,
                rsi REAL,
                kdj_k REAL,
                kdj_d REAL,
                macd_hist REAL,
                volume_ratio REAL,
                position_pct REAL,
                short_trend REAL,
                mid_trend REAL,
                reasons TEXT,
                created_at TEXT,
                FOREIGN KEY (symbol) REFERENCES stock_pool(symbol)
            )
        """)

        # 3. 交易记录表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                amount REAL NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                reason TEXT,
                confidence REAL,
                profit REAL,
                profit_pct REAL,
                hold_days INTEGER,
                closed_at TEXT,
                created_at TEXT,
                FOREIGN KEY (symbol) REFERENCES stock_pool(symbol)
            )
        """)

        # 4. 持仓表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                buy_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                cost REAL NOT NULL,
                stop_loss REAL NOT NULL,
                take_profit REAL NOT NULL,
                reason TEXT,
                buy_date TEXT NOT NULL,
                current_price REAL,
                current_value REAL,
                unrealized_profit REAL,
                unrealized_profit_pct REAL,
                highest_price REAL,
                lowest_price REAL,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (symbol) REFERENCES stock_pool(symbol)
            )
        """)

        # 5. 每日汇总表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                stocks_tested INTEGER DEFAULT 0,
                total_signals INTEGER DEFAULT 0,
                buy_signals INTEGER DEFAULT 0,
                sell_signals INTEGER DEFAULT 0,
                trades_executed INTEGER DEFAULT 0,
                realized_profit REAL DEFAULT 0,
                unrealized_profit REAL DEFAULT 0,
                total_profit_pct REAL DEFAULT 0,
                position_count INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)

        # 6. 回测结果表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                test_period INTEGER NOT NULL,
                total_signals INTEGER NOT NULL,
                profitable_signals INTEGER NOT NULL,
                win_rate REAL NOT NULL,
                avg_profit_3d REAL,
                avg_profit_5d REAL,
                avg_profit_10d REAL,
                avg_profit REAL,
                avg_loss REAL,
                profit_loss_ratio REAL,
                test_date TEXT,
                created_at TEXT,
                FOREIGN KEY (symbol) REFERENCES stock_pool(symbol)
            )
        """)

        # 创建索引
        self._create_indexes()

        # 提交
        self.conn.commit()

        print("✅ 数据库表创建完成")

    def _create_indexes(self):
        """创建索引"""
        print("📊 创建索引...")

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_signal_history_date ON signal_history(date)",
            "CREATE INDEX IF NOT EXISTS idx_signal_history_symbol ON signal_history(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_signal_history_type ON signal_history(signal_type)",
            "CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(trade_date)",
            "CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_backtest_symbol ON backtest_results(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_backtest_type ON backtest_results(signal_type)"
        ]

        for index_sql in indexes:
            try:
                self.cursor.execute(index_sql)
            except Exception as e:
                print(f"⚠️ 创建索引失败: {e}")

    # ===== 股票池操作 =====

    def add_stock_to_pool(self, symbol: str, name: str, category: str,
                         market_cap: float = 0, pe: float = 0, volume: float = 0,
                         is_hot: int = 0):
        """添加股票到池"""
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO stock_pool
                (symbol, name, category, market_cap, pe, volume, is_hot, active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, datetime('now'), datetime('now'))
            """, (symbol, name, category, market_cap, pe, volume, is_hot))
            self.conn.commit()
            print(f"✅ 添加股票: {name} ({symbol})")
        except Exception as e:
            print(f"❌ 添加股票失败: {e}")

    def get_active_stocks(self, limit: int = None) -> List[Dict]:
        """获取活跃股票"""
        sql = "SELECT * FROM stock_pool WHERE active = 1 ORDER BY category"
        if limit:
            sql += f" LIMIT {limit}"

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        return [dict(row) for row in rows]

    def get_stock(self, symbol: str) -> Optional[Dict]:
        """获取单只股票"""
        self.cursor.execute("SELECT * FROM stock_pool WHERE symbol = ?", (symbol,))
        row = self.cursor.fetchone()

        if row:
            return dict(row)
        return None

    # ===== 信号历史操作 =====

    def add_signal(self, date: str, symbol: str, signal_type: str,
                  action: str, price: float, confidence: float,
                  rsi: float = None, kdj_k: float = None, kdj_d: float = None,
                  macd_hist: float = None, volume_ratio: float = None,
                  position_pct: float = None, short_trend: float = None,
                  mid_trend: float = None, reasons: str = ""):
        """添加信号"""
        try:
            self.cursor.execute("""
                INSERT INTO signal_history
                (date, symbol, signal_type, action, price, confidence,
                 rsi, kdj_k, kdj_d, macd_hist, volume_ratio,
                 position_pct, short_trend, mid_trend, reasons, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (date, symbol, signal_type, action, price, confidence,
                   rsi, kdj_k, kdj_d, macd_hist, volume_ratio,
                   position_pct, short_trend, mid_trend, reasons))
            self.conn.commit()
        except Exception as e:
            print(f"❌ 添加信号失败: {e}")

    def get_signals_by_date(self, date: str) -> List[Dict]:
        """按日期获取信号"""
        self.cursor.execute("SELECT * FROM signal_history WHERE date = ?", (date,))
        rows = self.cursor.fetchall()

        return [dict(row) for row in rows]

    def get_signals_by_symbol(self, symbol: str, days: int = 30) -> List[Dict]:
        """按股票获取信号"""
        self.cursor.execute("""
            SELECT * FROM signal_history
            WHERE symbol = ? AND date >= date('now', '-{} days')
            ORDER BY date DESC
        """.format(days), (symbol,))
        rows = self.cursor.fetchall()

        return [dict(row) for row in rows]

    def get_signal_stats(self, days: int = 30) -> Dict:
        """获取信号统计"""
        self.cursor.execute("""
            SELECT
                signal_type,
                action,
                COUNT(*) as total_count,
                AVG(confidence) as avg_confidence
            FROM signal_history
            WHERE date >= date('now', '-{} days')
            GROUP BY signal_type, action
        """.format(days))

        rows = self.cursor.fetchall()

        stats = {}
        for row in rows:
            key = f"{row['signal_type']}_{row['action']}"
            stats[key] = {
                'total_count': row['total_count'],
                'avg_confidence': row['avg_confidence']
            }

        return stats

    # ===== 交易记录操作 =====

    def add_trade(self, trade_date: str, symbol: str, action: str,
                   price: float, quantity: int, stop_loss: float = None,
                   take_profit: float = None, reason: str = "",
                   confidence: float = 0):
        """添加交易"""
        amount = price * quantity

        try:
            self.cursor.execute("""
                INSERT INTO trades
                (trade_date, symbol, action, price, quantity, amount,
                 stop_loss, take_profit, reason, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (trade_date, symbol, action, price, quantity, amount,
                   stop_loss, take_profit, reason, confidence))
            self.conn.commit()
        except Exception as e:
            print(f"❌ 添加交易失败: {e}")

    def close_trade(self, symbol: str, close_price: float, closed_date: str = None):
        """平仓"""
        if closed_date is None:
            closed_date = datetime.now().strftime("%Y-%m-%d")

        # 获取持仓信息
        position = self.get_position(symbol)
        if not position:
            print(f"❌ 未找到持仓: {symbol}")
            return

        # 计算盈亏
        quantity = position['quantity']
        cost = position['cost']
        revenue = close_price * quantity
        profit = revenue - cost
        profit_pct = (profit / cost) * 100 if cost > 0 else 0

        # 计算持仓天数
        buy_date = position['buy_date']
        buy_dt = datetime.strptime(buy_date, "%Y-%m-%d")
        close_dt = datetime.strptime(closed_date, "%Y-%m-%d")
        hold_days = (close_dt - buy_dt).days

        # 更新交易记录
        try:
            self.cursor.execute("""
                UPDATE trades
                SET profit = ?,
                    profit_pct = ?,
                    hold_days = ?,
                    closed_at = ?
                WHERE symbol = ? AND closed_at IS NULL
            """, (profit, profit_pct, hold_days, closed_date, symbol))

            # 删除持仓
            self._delete_position(symbol)

            self.conn.commit()

            print(f"✅ 平仓: {symbol} - 盈亏: {profit:+.2f} ({profit_pct:+.2f}%)")
        except Exception as e:
            print(f"❌ 平仓失败: {e}")

    def get_trades(self, symbol: str = None, days: int = 90) -> List[Dict]:
        """获取交易记录"""
        sql = "SELECT * FROM trades WHERE 1=1"

        if symbol:
            sql += f" AND symbol = '{symbol}'"

        sql += f" AND trade_date >= date('now', '-{days} days')"

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        return [dict(row) for row in rows]

    def get_trade_stats(self, days: int = 90) -> Dict:
        """获取交易统计"""
        self.cursor.execute("""
            SELECT
                action,
                COUNT(*) as total_trades,
                COUNT(CASE WHEN profit > 0 THEN 1 END) as profitable_trades,
                SUM(profit) as total_profit,
                AVG(profit) as avg_profit,
                AVG(profit_pct) as avg_profit_pct,
                AVG(hold_days) as avg_hold_days
            FROM trades
            WHERE closed_at IS NOT NULL AND closed_at >= date('now', '-{} days')
            GROUP BY action
        """.format(days))

        rows = self.cursor.fetchall()

        stats = {}
        for row in rows:
            stats[row['action']] = {
                'total_trades': row['total_trades'],
                'profitable_trades': row['profitable_trades'],
                'win_rate': (row['profitable_trades'] / row['total_trades'] * 100) if row['total_trades'] > 0 else 0,
                'total_profit': row['total_profit'],
                'avg_profit': row['avg_profit'],
                'avg_profit_pct': row['avg_profit_pct'],
                'avg_hold_days': row['avg_hold_days']
            }

        return stats

    # ===== 持仓操作 =====

    def add_position(self, symbol: str, buy_price: float, quantity: int,
                    stop_loss: float, take_profit: float, reason: str = ""):
        """添加持仓"""
        cost = buy_price * quantity
        buy_date = datetime.now().strftime("%Y-%m-%d")

        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO positions
                (symbol, buy_price, quantity, cost, stop_loss, take_profit,
                 reason, buy_date, current_price, current_value,
                 unrealized_profit, unrealized_profit_pct,
                 highest_price, lowest_price, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (symbol, buy_price, quantity, cost, stop_loss, take_profit,
                   reason, buy_date, buy_price, cost, 0, 0, buy_price, buy_price))
            self.conn.commit()
            print(f"✅ 添加持仓: {symbol}")
        except Exception as e:
            print(f"❌ 添加持仓失败: {e}")

    def get_positions(self) -> List[Dict]:
        """获取所有持仓"""
        self.cursor.execute("SELECT * FROM positions ORDER BY created_at DESC")
        rows = self.cursor.fetchall()

        return [dict(row) for row in rows]

    def get_position(self, symbol: str) -> Optional[Dict]:
        """获取单只持仓"""
        self.cursor.execute("SELECT * FROM positions WHERE symbol = ?", (symbol,))
        row = self.cursor.fetchone()

        if row:
            return dict(row)
        return None

    def update_position_price(self, symbol: str, current_price: float):
        """更新持仓价格"""
        position = self.get_position(symbol)
        if not position:
            return

        quantity = position['quantity']
        cost = position['cost']
        current_value = current_price * quantity
        unrealized_profit = current_value - cost
        unrealized_profit_pct = (unrealized_profit / cost) * 100 if cost > 0 else 0

        highest_price = position['highest_price']
        lowest_price = position['lowest_price']

        if current_price > highest_price:
            highest_price = current_price
        if current_price < lowest_price:
            lowest_price = current_price

        try:
            self.cursor.execute("""
                UPDATE positions
                SET current_price = ?,
                    current_value = ?,
                    unrealized_profit = ?,
                    unrealized_profit_pct = ?,
                    highest_price = ?,
                    lowest_price = ?,
                    updated_at = datetime('now')
                WHERE symbol = ?
            """, (current_price, current_value, unrealized_profit,
                   unrealized_profit_pct, highest_price, lowest_price, symbol))
            self.conn.commit()
        except Exception as e:
            print(f"❌ 更新持仓价格失败: {e}")

    def _delete_position(self, symbol: str):
        """删除持仓"""
        try:
            self.cursor.execute("DELETE FROM positions WHERE symbol = ?", (symbol,))
            self.conn.commit()
        except Exception as e:
            print(f"❌ 删除持仓失败: {e}")

    # ===== 每日汇总操作 =====

    def add_daily_summary(self, date: str = None):
        """添加每日汇总"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # 获取当日数据
        self.cursor.execute("""
            SELECT
                COUNT(DISTINCT symbol) as stocks_tested,
                COUNT(*) as total_signals,
                SUM(CASE WHEN action = '买入' THEN 1 ELSE 0 END) as buy_signals,
                SUM(CASE WHEN action = '卖出/减仓' OR action = '卖出' THEN 1 ELSE 0 END) as sell_signals
            FROM signal_history
            WHERE date = ?
        """, (date,))

        row = self.cursor.fetchone()

        if not row:
            return

        stocks_tested = row['stocks_tested'] or 0
        total_signals = row['total_signals'] or 0
        buy_signals = row['buy_signals'] or 0
        sell_signals = row['sell_signals'] or 0

        # 获取交易数据
        self.cursor.execute("""
            SELECT
                COUNT(*) as trades_executed,
                SUM(CASE WHEN profit > 0 THEN profit ELSE 0 END) as realized_profit,
                SUM(unrealized_profit) as unrealized_profit
            FROM trades
            WHERE trade_date = ?
        """, (date,))

        trade_row = self.cursor.fetchone()
        trades_executed = trade_row['trades_executed'] or 0
        realized_profit = trade_row['realized_profit'] or 0
        unrealized_profit = trade_row['unrealized_profit'] or 0

        # 获取持仓数量
        self.cursor.execute("SELECT COUNT(*) as position_count FROM positions")
        pos_row = self.cursor.fetchone()
        position_count = pos_row['position_count'] or 0

        # 计算总盈亏
        total_profit = realized_profit + unrealized_profit

        # 计算收益率
        self.cursor.execute("SELECT SUM(cost) as total_cost FROM positions")
        cost_row = self.cursor.fetchone()
        total_cost = cost_row['total_cost'] or 0

        total_profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0

        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO daily_summary
                (date, stocks_tested, total_signals, buy_signals, sell_signals,
                 trades_executed, realized_profit, unrealized_profit,
                 total_profit_pct, position_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (date, stocks_tested, total_signals, buy_signals, sell_signals,
                   trades_executed, realized_profit, unrealized_profit,
                   total_profit_pct, position_count))
            self.conn.commit()
            print(f"✅ 添加每日汇总: {date}")
        except Exception as e:
            print(f"❌ 添加每日汇总失败: {e}")

    def get_daily_summary(self, days: int = 30) -> List[Dict]:
        """获取每日汇总"""
        self.cursor.execute("""
            SELECT * FROM daily_summary
            WHERE date >= date('now', '-{} days')
            ORDER BY date DESC
        """.format(days))

        rows = self.cursor.fetchall()

        return [dict(row) for row in rows]

    # ===== 回测结果操作 =====

    def add_backtest_result(self, symbol: str, signal_type: str,
                             test_period: int, total_signals: int,
                             profitable_signals: int, win_rate: float,
                             avg_profit_3d: float, avg_profit_5d: float,
                             avg_profit_10d: float, avg_profit: float,
                             avg_loss: float, profit_loss_ratio: float):
        """添加回测结果"""
        try:
            self.cursor.execute("""
                INSERT INTO backtest_results
                (symbol, signal_type, test_period, total_signals,
                 profitable_signals, win_rate, avg_profit_3d, avg_profit_5d,
                 avg_profit_10d, avg_profit, avg_loss, profit_loss_ratio,
                 test_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'), datetime('now'))
            """, (symbol, signal_type, test_period, total_signals,
                   profitable_signals, win_rate, avg_profit_3d, avg_profit_5d,
                   avg_profit_10d, avg_profit, avg_loss, profit_loss_ratio))
            self.conn.commit()
        except Exception as e:
            print(f"❌ 添加回测结果失败: {e}")

    def get_backtest_results(self, symbol: str = None,
                            signal_type: str = None) -> List[Dict]:
        """获取回测结果"""
        sql = "SELECT * FROM backtest_results WHERE 1=1"

        if symbol:
            sql += f" AND symbol = '{symbol}'"
        if signal_type:
            sql += f" AND signal_type = '{signal_type}'"

        self.cursor.execute(sql + " ORDER BY created_at DESC")
        rows = self.cursor.fetchall()

        return [dict(row) for row in rows]

    # ===== 综合查询 =====

    def get_database_summary(self) -> Dict:
        """获取数据库摘要"""
        summary = {}

        # 股票池
        self.cursor.execute("SELECT COUNT(*) FROM stock_pool WHERE active = 1")
        summary['active_stocks'] = self.cursor.fetchone()[0]

        # 信号历史
        self.cursor.execute("SELECT COUNT(*) FROM signal_history")
        summary['total_signals'] = self.cursor.fetchone()[0]

        # 交易记录
        self.cursor.execute("SELECT COUNT(*) FROM trades")
        summary['total_trades'] = self.cursor.fetchone()[0]

        # 持仓
        self.cursor.execute("SELECT COUNT(*) FROM positions")
        summary['position_count'] = self.cursor.fetchone()[0]

        # 每日汇总
        self.cursor.execute("SELECT COUNT(*) FROM daily_summary")
        summary['daily_summaries'] = self.cursor.fetchone()[0]

        # 回测结果
        self.cursor.execute("SELECT COUNT(*) FROM backtest_results")
        summary['backtest_results'] = self.cursor.fetchone()[0]

        return summary

    def format_summary(self) -> str:
        """格式化摘要"""
        summary = self.get_database_summary()

        return f"""
{'='*80}
💾 数据库摘要
{'='*80}
  活跃股票:    {summary['active_stocks']}
  信号总数:    {summary['total_signals']}
  交易记录:    {summary['total_trades']}
  当前持仓:    {summary['position_count']}
  每日汇总:    {summary['daily_summaries']}
  回测结果:    {summary['backtest_results']}
{'='*80}
数据库文件:  {self.db_path}
{'='*80}
"""

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("✅ 数据库连接已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def test_database():
    """测试数据库"""
    print("🧪 测试数据库\n")

    with StockDatabase() as db:
        # 添加股票
        db.add_stock_to_pool('sz000001', '平安银行', 'finance',
                            market_cap=2000, pe=5.5, volume=10, is_hot=1)

        # 添加信号
        db.add_signal(
            date='2026-02-01',
            symbol='sz000001',
            signal_type='new_model',
            action='买入',
            price=10.83,
            confidence=0.6,
            rsi=50.0,
            kdj_k=45.0,
            kdj_d=40.0,
            reasons='量价共振'
        )

        # 获取信号
        signals = db.get_signals_by_date('2026-02-01')
        print(f"\n信号记录: {len(signals)}")

        # 显示摘要
        print(db.format_summary())

if __name__ == "__main__":
    test_database()
