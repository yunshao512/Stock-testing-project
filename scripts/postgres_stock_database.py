#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PostgreSQL数据库管理 v1.0
使用PostgreSQL存储所有数据
"""

import psycopg2
from psycopg2 import sql
from datetime import datetime
from typing import List, Dict, Optional

class PostgresStockDatabase:
    """PostgreSQL股票数据库"""

    def __init__(self, db_name: str = "a_stock_data", host: str = "localhost",
                 port: int = 5432, user: str = "parallels",
                 password: str = "Zy511522@1"):
        """
        初始化数据库

        Args:
            db_name: 数据库名
            host: 主机
            port: 端口
            user: 用户
            password: 密码
        """
        self.db_name = db_name
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.conn = None
        self.cursor = None

        # 连接数据库
        self._connect()

        # 创建表
        self._create_tables()

    def _connect(self):
        """连接数据库"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.db_name,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()

            # 启用自动提交（简化操作）
            self.conn.autocommit = False

            print(f"✅ PostgreSQL连接成功: {self.db_name}")
        except Exception as e:
            print(f"❌ PostgreSQL连接失败: {e}")
            raise

    def _create_tables(self):
        """创建表"""
        print("📊 创建数据库表...")

        # 1. 股票池表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_pool (
                id SERIAL PRIMARY KEY,
                symbol TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                category_name TEXT,
                market_cap REAL,
                pe REAL,
                volume REAL,
                is_hot BOOLEAN DEFAULT FALSE,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. 信号历史表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_history (
                id SERIAL PRIMARY KEY,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stock_pool(symbol)
            )
        """)

        # 3. 交易记录表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
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
                closed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stock_pool(symbol)
            )
        """)

        # 4. 持仓表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id SERIAL PRIMARY KEY,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stock_pool(symbol)
            )
        """)

        # 5. 每日汇总表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_summary (
                id SERIAL PRIMARY KEY,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 6. 回测结果表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_results (
                id SERIAL PRIMARY KEY,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stock_pool(symbol)
            )
        """)

        # 创建索引
        self._create_indexes()

        # 提交
        self.conn.commit()

        print("✅ PostgreSQL表创建完成")

    def _create_indexes(self):
        """创建索引"""
        print("📊 创建索引...")

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_signal_history_date ON signal_history(date)",
            "CREATE INDEX IF NOT EXISTS idx_signal_history_symbol ON signal_history(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_signal_history_type ON signal_history(signal_type)",
            "CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(trade_date)",
            "CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol)",
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
                         is_hot: bool = False):
        """添加股票到池"""
        try:
            self.cursor.execute("""
                INSERT INTO stock_pool
                    (symbol, name, category, market_cap, pe, volume, is_hot, active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
                ON CONFLICT (symbol) DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    market_cap = EXCLUDED.market_cap,
                    pe = EXCLUDED.pe,
                    volume = EXCLUDED.volume,
                    is_hot = EXCLUDED.is_hot,
                    active = TRUE,
                    updated_at = CURRENT_TIMESTAMP
            """, (symbol, name, category, market_cap, pe, volume, is_hot))
            self.conn.commit()
            print(f"✅ 添加股票: {name} ({symbol}) - {category}")
        except Exception as e:
            print(f"❌ 添加股票失败: {e}")

    def get_active_stocks(self, limit: int = None) -> List[Dict]:
        """获取活跃股票"""
        sql = "SELECT * FROM stock_pool WHERE active = TRUE ORDER BY category"
        if limit:
            sql += f" LIMIT {limit}"

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        # 转换为字典
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def get_stock_count(self) -> int:
        """获取股票数量"""
        self.cursor.execute("SELECT COUNT(*) FROM stock_pool WHERE active = TRUE")
        return self.cursor.fetchone()[0]

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
                     position_pct, short_trend, mid_trend, reasons)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (date, symbol, signal_type, action, price, confidence,
                   rsi, kdj_k, kdj_d, macd_hist, volume_ratio,
                   position_pct, short_trend, mid_trend, reasons))
            self.conn.commit()
        except Exception as e:
            print(f"❌ 添加信号失败: {e}")

    def get_signal_stats(self, days: int = 30) -> Dict:
        """获取信号统计"""
        self.cursor.execute("""
            SELECT
                signal_type,
                action,
                COUNT(*) as total_count,
                AVG(confidence) as avg_confidence
            FROM signal_history
            WHERE date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY signal_type, action
        """ % (days,))

        rows = self.cursor.fetchall()

        stats = {}
        for row in rows:
            key = f"{row[0]}_{row[1]}"
            stats[key] = {
                'total_count': row[2],
                'avg_confidence': row[3]
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
                     stop_loss, take_profit, reason, confidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (trade_date, symbol, action, price, quantity, amount,
                   stop_loss, take_profit, reason, confidence))
            self.conn.commit()
        except Exception as e:
            print(f"❌ 添加交易失败: {e}")

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
            WHERE closed_at IS NOT NULL AND closed_at >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY action
        """ % (days,))

        rows = self.cursor.fetchall()

        stats = {}
        for row in rows:
            stats[row[0]] = {
                'total_trades': row[1],
                'profitable_trades': row[2],
                'win_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0,
                'total_profit': row[3] or 0,
                'avg_profit': row[4] or 0,
                'avg_profit_pct': row[5] or 0,
                'avg_hold_days': row[6] or 0
            }

        return stats

    # ===== 持仓操作 =====

    def add_position(self, symbol: str, buy_price: float, quantity: int,
                    stop_loss: float, take_profit: float, reason: str = ""):
        """添加持仓"""
        cost = buy_price * quantity

        try:
            self.cursor.execute("""
                INSERT INTO positions
                    (symbol, buy_price, quantity, cost, stop_loss, take_profit,
                     reason, buy_date, current_price, current_value,
                     unrealized_profit, unrealized_profit_pct,
                     highest_price, lowest_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol) DO UPDATE SET
                    current_price = EXCLUDED.current_price,
                    current_value = EXCLUDED.current_value,
                    unrealized_profit = EXCLUDED.unrealized_profit,
                    unrealized_profit_pct = EXCLUDED.unrealized_profit_pct,
                    highest_price = EXCLUDED.highest_price,
                    lowest_price = EXCLUDED.lowest_price,
                    updated_at = CURRENT_TIMESTAMP
            """, (symbol, buy_price, quantity, cost, stop_loss, take_profit,
                   reason, datetime.now().strftime("%Y-%m-%d"),
                   buy_price, cost, 0, 0,
                   buy_price, buy_price))
            self.conn.commit()
            print(f"✅ 添加持仓: {symbol}")
        except Exception as e:
            print(f"❌ 添加持仓失败: {e}")

    def get_positions(self) -> List[Dict]:
        """获取所有持仓"""
        self.cursor.execute("SELECT * FROM positions ORDER BY buy_date DESC")
        rows = self.cursor.fetchall()

        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in rows]

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
            WHERE date = %s
        """, (date,))

        row = self.cursor.fetchone()

        if not row:
            return

        stocks_tested = row[0] or 0
        total_signals = row[1] or 0
        buy_signals = row[2] or 0
        sell_signals = row[3] or 0

        # 获取交易数据
        self.cursor.execute("""
            SELECT
                COUNT(*) as trades_executed,
                SUM(CASE WHEN profit > 0 THEN profit ELSE 0 END) as realized_profit,
                SUM(unrealized_profit) as unrealized_profit
            FROM positions
            WHERE updated_at >= %s::date - INTERVAL '1 day'
        """, (date,))

        trade_row = self.cursor.fetchone()
        trades_executed = trade_row[0] or 0
        realized_profit = trade_row[1] or 0
        unrealized_profit = trade_row[2] or 0

        # 获取持仓数量
        self.cursor.execute("SELECT COUNT(*) FROM positions")
        pos_row = self.cursor.fetchone()
        position_count = pos_row[0] or 0

        # 计算总盈亏
        total_profit = realized_profit + unrealized_profit

        # 计算收益率
        self.cursor.execute("SELECT SUM(cost) as total_cost FROM positions")
        cost_row = self.cursor.fetchone()
        total_cost = cost_row[0] or 0

        total_profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0

        try:
            self.cursor.execute("""
                INSERT INTO daily_summary
                    (date, stocks_tested, total_signals, buy_signals, sell_signals,
                     trades_executed, realized_profit, unrealized_profit,
                     total_profit_pct, position_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date) DO UPDATE SET
                    stocks_tested = EXCLUDED.stocks_tested,
                    total_signals = EXCLUDED.total_signals,
                    buy_signals = EXCLUDED.buy_signals,
                    sell_signals = EXCLUDED.sell_signals,
                    trades_executed = EXCLUDED.trades_executed,
                    realized_profit = EXCLUDED.realized_profit,
                    unrealized_profit = EXCLUDED.unrealized_profit,
                    total_profit_pct = EXCLUDED.total_profit_pct,
                    position_count = EXCLUDED.position_count
            """, (date, stocks_tested, total_signals, buy_signals, sell_signals,
                   trades_executed, realized_profit, unrealized_profit,
                   total_profit_pct, position_count))
            self.conn.commit()
            print(f"✅ 添加每日汇总: {date}")
        except Exception as e:
            print(f"❌ 添加每日汇总失败: {e}")

    def get_database_summary(self) -> Dict:
        """获取数据库摘要"""
        summary = {}

        # 股票池
        self.cursor.execute("SELECT COUNT(*) FROM stock_pool WHERE active = TRUE")
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
💾 PostgreSQL数据库摘要
{'='*80}
  活跃股票:    {summary['active_stocks']}
  信号总数:    {summary['total_signals']}
  交易记录:    {summary['total_trades']}
  当前持仓:    {summary['position_count']}
  每日汇总:    {summary['daily_summaries']}
  回测结果:    {summary['backtest_results']}
{'='*80}
数据库: {self.db_name}
主机:   {self.host}:{self.port}
用户:   {self.user}
{'='*80}
"""

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("✅ PostgreSQL连接已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def test_postgres_database():
    """测试PostgreSQL数据库"""
    print("🧪 测试PostgreSQL数据库\n")

    with PostgresStockDatabase() as db:
        # 添加测试股票
        db.add_stock_to_pool('sz000001', '平安银行', 'finance',
                            market_cap=2000, pe=5.5, volume=10, is_hot=True)

        # 添加测试信号
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

        # 获取股票数量
        count = db.get_stock_count()
        print(f"\n股票池数量: {count}")

        # 显示摘要
        print(db.format_summary())

if __name__ == "__main__":
    test_postgres_database()
