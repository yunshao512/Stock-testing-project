#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
每日工作流程 v1.0
定义完整的交易日工作流程
"""

import sys
sys.path.append('/home/parallels/.openclaw/workspace/skills/a-stock-fetcher/scripts')
from trading_system import TradingSystem
from analysis_model import AnalysisModel
from alert_watcher import AlertWatcher
from stock_api import fetch_stock_data
from historical_data import fetch_historical_data
from datetime import datetime
import time as time_module

class DailyWorkflow:
    """每日工作流程"""

    def __init__(self, initial_capital: float = 100000.0):
        """
        初始化工作流程

        Args:
            initial_capital: 初始资金
        """
        self.trading_system = TradingSystem(initial_capital)
        self.analysis_model = AnalysisModel(stop_loss_pct=0.05, take_profit_pct=0.10)
        self.watch_list = []  # 监控股票列表

    def set_watch_list(self, symbols: list):
        """设置监控列表"""
        self.watch_list = symbols

    def pre_market_analysis(self):
        """盘前分析（9:00-9:25）"""
        print("\n" + "="*80)
        print("🕘 09:00 - 盘前分析")
        print("="*80)

        # 1. 分析监控列表
        if self.watch_list:
            print(f"\n📊 分析监控列表 ({len(self.watch_list)}只股票)...")
            signals = self.analysis_model.batch_analyze(self.watch_list, days=30)

            print(self.analysis_model.format_batch_signals(signals))

            # 显示详细信号
            if signals and len(signals) > 0:
                print(f"\n📊 详细信号 (前3只):\n")
                for signal in signals[:3]:
                    print(self.analysis_model.format_signal(signal))

        # 2. 检查持仓
        if self.trading_system.positions:
            print(f"\n📊 检查持仓 ({len(self.trading_system.positions)}只)...")
            for symbol, position in self.trading_system.positions.items():
                print(f"  {symbol}: 买入¥{position.buy_price:.2f}, "
                      f"当前¥{position.current_price:.2f}, "
                      f"盈亏{position.unrealized_pnl_pct:+.2f}%")
                print(f"    止损: ¥{position.stop_loss:.2f} | "
                      f"止盈: ¥{position.take_profit:.2f}")

        # 3. 账户摘要
        print(self.trading_system.format_summary())

    def trading_session(self):
        """交易时段（9:30-15:00）"""
        print("\n" + "="*80)
        print("🕘 09:30 - 交易时段监控")
        print("="*80)

        check_count = 0

        while True:
            check_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")

            print(f"\n{'─'*80}")
            print(f"📊 [{check_count}] 时间: {current_time}")

            # 1. 更新持仓价格
            if self.trading_system.positions:
                symbols = list(self.trading_system.positions.keys())
                stocks = fetch_stock_data(symbols, use_cache=False)

                if stocks:
                    stock_data = {s['code']: s['price'] for s in stocks}
                    self.trading_system.update_positions(stock_data)

                    # 2. 检查止损止盈
                    signals = self.trading_system.check_stop_loss_take_profit(stock_data)

                    if signals:
                        print(f"\n🚨 触发信号 ({len(signals)}条):")
                        for signal in signals:
                            print(f"  {signal['symbol']}: {signal['reason']} @ ¥{signal['price']:.2f}")

                            # 自动执行
                            if signal['action'] == 'sell':
                                self.trading_system.sell(
                                    signal['symbol'],
                                    signal['price'],
                                    reason=signal['reason']
                                )

            # 3. 监控列表价格更新
            if self.watch_list:
                stocks = fetch_stock_data(self.watch_list, use_cache=False)
                if stocks:
                    print(f"\n📊 监控列表价格:")
                    for stock in stocks:
                        print(f"  {stock['name']} ({stock['code']}): "
                              f"¥{stock['price']:.2f} ({stock['change_percent']:+.2f}%)")

            # 4. 更新账户摘要
            print(self.trading_system.format_summary())

            # 5. 等待（实际环境中应该等待更长）
            print(f"\n⏳ 等待下一次检查...")
            time_module.sleep(30)  # 测试用30秒，实际应该是5-10分钟

            # 测试模式：只检查3次
            if check_count >= 3:
                print("\n⏹️ 测试模式，停止监控")
                break

    def post_market_review(self):
        """盘后复盘（15:00-15:30）"""
        print("\n" + "="*80)
        print("🕕 15:00 - 盘后复盘")
        print("="*80)

        # 1. 当日交易总结
        print("\n📊 当日交易总结:")
        print(self.trading_system.format_summary())

        # 2. 持仓详细分析
        if self.trading_system.positions:
            print("\n📊 持仓详细分析:\n")

            for symbol, position in self.trading_system.positions.items():
                print(f"{symbol}:")
                print(f"  买入价: ¥{position.buy_price:.2f}")
                print(f"  当前价: ¥{position.current_price:.2f}")
                print(f"  盈亏:   ¥{position.unrealized_pnl:+.2f} ({position.unrealized_pnl_pct:+.2f}%)")
                print(f"  止损:   ¥{position.stop_loss:.2f}")
                print(f"  止盈:   ¥{position.take_profit:.2f}")
                print(f"  最高:   ¥{position.highest_price:.2f}")
                print(f"  最低:   ¥{position.lowest_price:.2f}")

                # 获取技术分析
                candles = fetch_historical_data(symbol, '1d', 30)
                if candles:
                    from indicators_v2 import calculate_all_indicators, interpret_indicators
                    indicators = calculate_all_indicators(candles)
                    interpretation = interpret_indicators(indicators, -1)

                    print(f"\n  技术指标:")
                    for key, value in interpretation.items():
                        print(f"    {key}: {value}")

                print()

        # 3. 生成明日计划
        print("📊 明日计划:\n")

        if self.watch_list:
            signals = self.analysis_model.batch_analyze(self.watch_list, days=30)

            buy_signals = [s for s in signals if s.action == "买入"][:3]
            sell_signals = [s for s in signals if s.action == "卖出"][:3]

            if buy_signals:
                print("  关注买入机会:")
                for signal in buy_signals:
                    print(f"    • {signal.symbol}: ¥{signal.price:.2f} (信心{signal.confidence*100:.0f}%)")
                    print(f"      止损: ¥{signal.stop_loss:.2f} | 止盈: ¥{signal.take_profit:.2f}")

            if sell_signals:
                print("\n  关注卖出机会:")
                for signal in sell_signals:
                    print(f"    • {signal.symbol}: ¥{signal.price:.2f}")

    def daily_report(self) -> str:
        """生成日报"""
        report = f"""
{'='*80}
📊 每日交易报告 - {datetime.now().strftime("%Y-%m-%d")}
{'='*80}
"""

        summary = self.trading_system.get_summary()

        report += f"""
💰 账户状况
{'─'*80}
  初始资金: ¥{summary['initial_capital']:,.2f}
  当前总值: ¥{summary['total_value']:,.2f}
  总盈亏:   ¥{summary['total_pnl']:+,.2f} ({summary['total_pnl_pct']:+.2f}%)
  可用资金: ¥{summary['available_capital']:,.2f}
  持仓数量: {summary['position_count']}
{'─'*80}
📈 交易统计
{'─'*80}
  总交易数: {summary['total_trades']}
  盈利交易: {summary['profitable_trades']}
  胜率:     {summary['win_rate']:.1f}%
  平均收益: {summary['avg_pnl_pct']:+.2f}%
  最大盈利: +{summary['max_profit']:.2f}%
  最大亏损: {summary['max_loss']:.2f}%
{'─'*80}
"""

        return report

def run_daily_workflow(watch_list: list = None, initial_capital: float = 100000.0,
                     mode: str = "simulation"):
    """
    运行每日工作流程

    Args:
        watch_list: 监控股票列表
        initial_capital: 初始资金
        mode: 模式（simulation=模拟交易，live=实盘）
    """
    print(f"\n{'='*80}")
    print(f"🚀 启动每日交易流程")
    print(f"{'='*80}")
    print(f"  模式: {mode}")
    print(f"  初始资金: ¥{initial_capital:,.2f}")
    if watch_list:
        print(f"  监控股票: {len(watch_list)}只")
    print(f"{'='*80}")

    workflow = DailyWorkflow(initial_capital)

    if watch_list:
        workflow.set_watch_list(watch_list)

    try:
        # 盘前分析
        workflow.pre_market_analysis()

        # 交易时段
        if mode == "simulation":
            print("\n⚠️ 模拟交易模式，跳过实时监控")
        else:
            workflow.trading_session()

        # 盘后复盘
        workflow.post_market_review()

        # 生成日报
        print(workflow.daily_report())

    except KeyboardInterrupt:
        print("\n\n⏸️ 用户中断，保存数据...")
        workflow.trading_system._save_data()
        print("✅ 数据已保存")

    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 测试工作流程
    watch_list = ['sh600519', 'sz000001', 'sz000858']
    run_daily_workflow(watch_list, mode="simulation")
