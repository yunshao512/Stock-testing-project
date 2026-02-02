#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
备用数据源管理器
完善新浪财经、东方财富等数据源
"""

import sys
import os
from typing import List, Dict, Optional
import requests
import json

# 添加项目根目录到路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)


class SinaDataSource:
    """新浪财经数据源（改进版）"""

    def __init__(self):
        self.name = "新浪财经"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 10

    def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """从新浪财经获取数据"""
        try:
            # 新浪财经实时行情API
            symbol_list = []
            for symbol in symbols:
                # 转换为新浪格式
                if symbol.startswith('sh'):
                    symbol_list.append(f'sh{symbol[2:]}')
                elif symbol.startswith('sz'):
                    symbol_list.append(f'sz{symbol[2:]}')
                else:
                    symbol_list.append(f'sh{symbol}')

            # 构建请求URL
            symbols_str = ",".join(symbol_list)
            url = "http://hq.sinajs.cn/list=" + symbols_str
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.encoding = 'gbk'

            data = []
            lines = response.text.strip().split('\n')

            for line in lines:
                if line.startswith('var hq_str_'):
                    # 提取JSON数据
                    data_str = line.split('"')[1]

                    # 解析数据
                    # 格式: 股票名称, 开盘, 昨收, 当前, 最高, 最低, 买入, 卖出, 成交量, ...
                    parts = data_str.split(',')

                    if len(parts) >= 32:
                        # 提取股票代码
                        var_name = line.split('=')[0]  # var hq_str_sh600519
                        if len(var_name) > 9:
                            code = var_name[9:]
                            # 转换回标准格式
                            if code.startswith('6'):
                                symbol = f'sh{code}'
                            else:
                                symbol = f'sz{code}'

                        name = parts[0]
                        open_price = float(parts[1]) if parts[1] and parts[1] != '' else 0.0
                        yesterday_close = float(parts[2]) if parts[2] and parts[2] != '' else 0.0
                        current_price = float(parts[3]) if parts[3] and parts[3] != '' else 0.0
                        volume = float(parts[8]) if parts[8] and parts[8] != '' else 0.0

                        change_percent = 0.0
                        if yesterday_close > 0 and current_price > 0:
                            change_percent = ((current_price - yesterday_close) / yesterday_close) * 100

                        stock_data = {
                            'symbol': symbol,
                            'name': name,
                            'price': current_price,
                            'yesterday_close': yesterday_close,
                            'open_price': open_price,
                            'change_percent': change_percent,
                            'volume': volume,
                            'source': '新浪财经'
                        }
                        data.append(stock_data)

            if data:
                print(f"🌐 [{self.name}] 成功获取 {len(data)} 只股票数据")

            return data

        except Exception as e:
            print(f"❌ [{self.name}] 获取数据失败: {e}")
            return []


class EastmoneyDataSource:
    """东方财富数据源（简化版 - 仅实时数据）"""

    def __init__(self):
        self.name = "东方财富"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 10

    def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """从东方财富获取数据"""
        # 由于东方财富API较复杂，暂时跳过，只提供接口
        print(f"⚠️ [{self.name}] 暂未实现（API较复杂）")
        return []


class DataQualityScorer:
    """数据质量评分器"""

    @staticmethod
    def score_data(stock_data: Dict) -> float:
        """
        评分数据质量

        Args:
            stock_data: 股票数据

        Returns:
            质量评分 0-1
        """
        score = 1.0

        # 检查必要字段
        required_fields = ['symbol', 'name', 'price', 'yesterday_close', 'change_percent', 'volume']
        for field in required_fields:
            if field not in stock_data or stock_data[field] is None:
                score -= 0.3

        # 检查价格合理性
        if stock_data.get('price', 0) <= 0:
            score -= 0.2
        if stock_data.get('yesterday_close', 0) <= 0:
            score -= 0.1

        # 检查成交量
        if stock_data.get('volume', 0) <= 0:
            score -= 0.1

        # 限制在0-1之间
        return max(0.0, min(1.0, score))


def test_backup_sources():
    """测试备用数据源"""
    print("="*80)
    print("🧪 测试备用数据源")
    print("="*80)

    # 测试新浪财经
    print("\n📊 测试新浪财经:")
    sina = SinaDataSource()
    sina_data = sina.fetch_stock_data(['600519', '000063'])

    for stock in sina_data:
        quality = DataQualityScorer.score_data(stock)
        print(f"\n  {stock['symbol']} {stock['name']} [质量: {quality*100:.0f}%]")
        print(f"    价格: ¥{stock['price']:.2f}")
        print(f"    涨跌: {stock['change_percent']:+.2f}%")
        print(f"    成交量: {stock['volume']:,.0f}")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_backup_sources()
