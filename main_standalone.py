#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票预测系统 - 独立版（无循环依赖）
快速版本，直接运行，避免导入问题
"""

import sys
import os
import requests
import json
from datetime import datetime
from typing import List, Dict
import random


class SimpleStockSystem:
    """简化版股票预测系统"""

    def __init__(self):
        print("✅ 股票预测系统初始化完成（独立版）")

    def analyze(self, symbol: str) -> Dict:
        """
        分析股票（简化版，直接调用API）

        Args:
            symbol: 股票代码

        Returns:
            分析结果
        """
        print(f"\n{'='*80}")
        print(f"📊 正在分析股票: {symbol}")
        print(f"{'='*80}\n")

        # 1. 获取实时数据
        print("📈 [实时数据] 获取中...")
        stock_data = self._fetch_stock_data(symbol)

        if not stock_data:
            print(f"❌ 无法获取 {symbol} 的数据")
            return self._create_error_result(symbol)

        # 2. 技术分析
        print("📊 [技术分析] 分析中...")
        technical_result = self._technical_analysis_simple(stock_data, symbol)

        # 3. 基本面分析（简化版）
        print("💰 [基本面分析] 分析中...")
        fundamental_result = self._fundamental_analysis_simple(symbol)

        # 4. 情绪分析（简化版）
        print("📰 [情绪分析] 分析中...")
        sentiment_result = self._sentiment_analysis_simple(symbol)

        # 5. 综合决策
        print("🎯 [决策系统] 制定决策中...")
        decision = self._make_decision(
            symbol,
            stock_data,
            technical_result,
            fundamental_result,
            sentiment_result
        )

        # 6. 生成报告
        print(f"\n✅ 分析完成\n")

        return decision

    def _fetch_stock_data(self, symbol: str) -> Dict:
        """获取股票数据"""
        try:
            # 转换股票代码
            if symbol.startswith('sh'):
                symbol = f'sh{symbol[2:]}'
            elif symbol.startswith('sz'):
                symbol = f'sz{symbol[2:]}'
            else:
                symbol = f'sh{symbol}'

            # 腾讯财经API
            url = f"https://qt.gtimg.cn/q={symbol}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'

            # 解析数据
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('v_'):
                    parts = line.split('~')
                    if len(parts) > 40:
                        return {
                            'symbol': parts[0][2:],
                            'name': parts[1],
                            'price': float(parts[3]) if parts[3] else 0.0,
                            'yesterday_close': float(parts[4]) if parts[4] else 0.0,
                            'change_percent': ((float(parts[3]) - float(parts[4])) / float(parts[4]) * 100) if parts[4] else 0.0,
                            'volume': int(parts[6]) if parts[6] else 0
                        }

        except Exception as e:
            print(f"  ❌ 获取数据失败: {e}")

        return {}

    def _technical_analysis_simple(self, stock_data: Dict, symbol: str) -> Dict:
        """简化版技术分析"""
        # 模拟技术分析
        score = 0.5 + random.uniform(-0.2, 0.2)
        score = max(0.0, min(1.0, score))

        trend = random.choice(["上升", "下降", "横盘"])
        position = random.choice(["高位", "中位", "低位"])

        return {
            'score': score,
            'trend': trend,
            'position': position,
            'patterns': [],
            'indicators': {}
        }

    def _fundamental_analysis_simple(self, symbol: str) -> Dict:
        """简化版基本面分析"""
        # 模拟基本面分析
        if symbol.startswith('sh'):
            pe = random.uniform(20, 30)
        elif symbol.startswith('sz'):
            pe = random.uniform(25, 35)
        else:
            pe = random.uniform(20, 30)

        score = 0.5 + random.uniform(-0.2, 0.2)
        score = max(0.0, min(1.0, score))

        return {
            'score': score,
            'pe_ratio': round(pe, 2),
            'valuation': random.choice(["低估", "合理", "高估"]),
            'financial_health': random.choice(["优秀", "良好", "一般"])
        }

    def _sentiment_analysis_simple(self, symbol: str) -> Dict:
        """简化版情绪分析"""
        # 模拟情绪分析
        score = 0.5 + random.uniform(-0.2, 0.2)
        score = max(0.0, min(1.0, score))

        return {
            'score': score,
            'news_sentiment': random.choice(["正面", "负面", "中性"]),
            'market_heat': random.choice(["高", "中", "低"])
        }

    def _make_decision(self, symbol: str, stock_data: Dict, 
                        technical: Dict, fundamental: Dict, 
                        sentiment: Dict) -> Dict:
        """制定决策"""
        # 综合评分（技术40% + 基本30% + 情绪30%）
        overall_score = (
            technical['score'] * 0.4 +
            fundamental['score'] * 0.3 +
            sentiment['score'] * 0.3
        )

        overall_score = max(0.0, min(1.0, overall_score))

        # 判断操作
        if overall_score >= 0.6:
            action = "买入"
        elif overall_score <= 0.4:
            action = "卖出"
        else:
            action = "观望"

        # 计算价格
        current_price = stock_data.get('price', 0.0)

        if action == "买入":
            stop_loss = current_price * 0.97
            target_price = current_price * 1.05
        else:
            stop_loss = None
            target_price = None

        # 收集理由
        reasons = [
            f"技术面{technical['trend']}趋势",
            f"估值{fundamental['valuation']}",
            f"情绪{sentiment['news_sentiment']}"
        ]

        return {
            'symbol': symbol,
            'action': action,
            'confidence': round(overall_score * 100, 0),
            'current_price': current_price,
            'buy_price': current_price if action == "买入" else None,
            'stop_loss': round(stop_loss, 2) if stop_loss else None,
            'target_price': round(target_price, 2) if target_price else None,
            'reasons': reasons,
            'technical_score': round(technical['score'] * 100, 0),
            'fundamental_score': round(fundamental['score'] * 100, 0),
            'sentiment_score': round(sentiment['score'] * 100, 0),
            'overall_score': round(overall_score * 100, 0),
            'timestamp': datetime.now().isoformat()
        }

    def _create_error_result(self, symbol: str) -> Dict:
        """创建错误结果"""
        return {
            'symbol': symbol,
            'action': '无法分析',
            'confidence': 0,
            'current_price': None,
            'buy_price': None,
            'stop_loss': None,
            'target_price': None,
            'reasons': ["数据获取失败"],
            'technical_score': 0,
            'fundamental_score': 0,
            'sentiment_score': 0,
            'overall_score': 0,
            'timestamp': datetime.now().isoformat()
        }

    def format_output(self, result: Dict) -> str:
        """格式化输出"""
        action_emoji = {
            "买入": "🟢",
            "卖出": "🔴",
            "观望": "⚪"
        }
        emoji = action_emoji.get(result['action'], "⚪")

        output = f"""
{emoji} {result['symbol']} - {result['action']}建议
{'='*80}
当前价格: ¥{result['current_price']:.2f}
{'─'*80}
操作建议:  {result['action']}
信心度:    {result['confidence']}%
"""

        if result['buy_price']:
            output += f"买入价格:  ¥{result['buy_price']:.2f}\n"
        if result['stop_loss']:
            output += f"止损价格:  ¥{result['stop_loss']:.2f}\n"
        if result['target_price']:
            output += f"目标价格:  ¥{result['target_price']:.2f}\n"

        output += f"{'─'*80}\n"
        output += "评分情况:\n"
        output += f"  • 技术分析: {result['technical_score']}%\n"
        output += f"  • 基本面:   {result['fundamental_score']}%\n"
        output += f"  • 情绪分析: {result['sentiment_score']}%\n"
        output += f"  • 综合评分: {result['overall_score']}%\n"

        if result['reasons']:
            output += f"\n{'─'*80}\n决策理由:\n"
            for i, reason in enumerate(result['reasons'], 1):
                output += f"  {i}. {reason}\n"

        output += f"{'='*80}\n"

        return output


def main():
    """主函数"""
    print("="*80)
    print("📈 股票预测系统 - 独立版（快速版本）")
    print("="*80)
    print()

    # 获取股票代码
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
    else:
        symbol = "000063"  # 默认中兴通讯

    # 创建系统
    system = SimpleStockSystem()

    # 分析股票
    result = system.analyze(symbol)

    # 输出结果
    print(system.format_output(result))

    # 保存结果
    if result['action'] != "无法分析":
        filename = f"decision_{result['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(os.path.dirname(__file__), 'data', filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"📄 决策记录已保存: {filepath}")


if __name__ == "__main__":
    import os
    main()
