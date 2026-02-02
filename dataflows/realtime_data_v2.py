#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票实时数据API v2.0
修复数据解析问题，增加多个数据源
"""

import sys
import os
from typing import List, Dict, Optional

# 添加项目根目录到路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

import requests
import json


class RealTimeDataSource:
    """实时数据源"""

    def __init__(self):
        self.timeout = 10
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_from_tencent(self, symbols: List[str]) -> List[Dict]:
        """从腾讯财经获取数据"""
        try:
            # 转换股票代码格式
            symbol_list = []
            for symbol in symbols:
                if symbol.startswith('sh'):
                    symbol_list.append(f'sh{symbol[2:]}')
                elif symbol.startswith('sz'):
                    symbol_list.append(f'sz{symbol[2:]}')
                else:
                    symbol_list.append(f'sh{symbol}')

            url = f"https://qt.gtimg.cn/q={','.join(symbol_list)}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.encoding = 'gbk'

            data = []
            lines = response.text.strip().split('\n')

            for line in lines:
                if line.startswith('v_'):
                    parts = line.split('~')
                    if len(parts) > 40:
                        symbol = parts[0][2:]
                        name = parts[1]
                        price = float(parts[3]) if parts[3] and parts[3] != '' else 0.0
                        yesterday_close = float(parts[4]) if parts[4] and parts[4] != '' else 0.0
                        change_percent = 0.0

                        if yesterday_close > 0 and price > 0:
                            change_percent = ((price - yesterday_close) / yesterday_close) * 100

                        volume = int(parts[6]) if parts[6] and parts[6] != '' else 0

                        stock_data = {
                            'symbol': symbol,
                            'name': name,
                            'price': price,
                            'yesterday_close': yesterday_close,
                            'change_percent': change_percent,
                            'volume': volume,
                            'source': '腾讯财经'
                        }
                        data.append(stock_data)

            print(f"🌐 [腾讯财经] 成功获取 {len(data)} 只股票数据")
            return data

        except Exception as e:
            print(f"❌ [腾讯财经] 获取失败: {e}")
            return []

    def fetch_from_sina(self, symbols: List[str]) -> List[Dict]:
        """从新浪财经获取数据"""
        try:
            # 新浪财经API（JSON格式）
            symbol_list = []
            for symbol in symbols:
                # 转换为新浪格式
                if symbol.startswith('sh'):
                    symbol_list.append(f'sh{symbol[2:]}')
                elif symbol.startswith('sz'):
                    symbol_list.append(f'sz{symbol[2:]}')
                else:
                    symbol_list.append(f'sh{symbol}')

            url = "http://hq.sinajs.cn/list=" + ",".join(symbol_list)
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
                        symbol = line.split('=')[0].replace('var hq_str_', '')
                        name = parts[0]
                        open_price = float(parts[1]) if parts[1] else 0.0
                        yesterday_close = float(parts[2]) if parts[2] else 0.0
                        current_price = float(parts[3]) if parts[3] else 0.0
                        volume = float(parts[8]) if parts[8] else 0.0

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

            print(f"🌐 [新浪财经] 成功获取 {len(data)} 只股票数据")
            return data

        except Exception as e:
            print(f"❌ [新浪财经] 获取失败: {e}")
            return []

    def fetch_from_eastmoney(self, symbols: List[str]) -> List[Dict]:
        """从东方财富获取数据"""
        try:
            # 东方财富API
            symbol_list = []
            for symbol in symbols:
                # 转换为东方财富格式
                if symbol.startswith('sh'):
                    code = f"{int(symbol[2:])}.SH"
                elif symbol.startswith('sz'):
                    code = f"{int(symbol[2:])}.SZ"
                else:
                    code = f"{int(symbol)}.SH"
                symbol_list.append(code)

            url = f"http://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': '1',
                'pz': str(len(symbols)),
                'po': '1',
                'np': '1',
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': '2',
                'invt': '2',
                'fid': 'f3',
                'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
                'fields': 'f12,f13,f14,f2,f3,f4,f5,f6',
                'secids': ','.join([f"1.{s}" for s in symbol_list])
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            json_data = response.json()

            data = []
            if 'data' in json_data and 'diff' in json_data['data']:
                for item in json_data['data']['diff']:
                    symbol = f"{'sh' if item['f13'] == 6 else 'sz'}{str(item['f12']).zfill(6)}"
                    name = item['f14']
                    price = float(item['f2']) if item['f2'] else 0.0
                    yesterday_close = float(item['f3']) if item['f3'] else 0.0
                    open_price = float(item['f17']) if item['f17'] else 0.0
                    high_price = float(item['f15']) if item['f15'] else 0.0
                    low_price = float(item['f16']) if item['f16'] else 0.0
                    volume = float(item['f5']) if item['f5'] else 0.0

                    change_percent = float(item['f4']) if item['f4'] else 0.0

                    stock_data = {
                        'symbol': symbol,
                        'name': name,
                        'price': price,
                        'yesterday_close': yesterday_close,
                        'open_price': open_price,
                        'high_price': high_price,
                        'low_price': low_price,
                        'change_percent': change_percent,
                        'volume': volume,
                        'source': '东方财富'
                    }
                    data.append(stock_data)

            print(f"🌐 [东方财富] 成功获取 {len(data)} 只股票数据")
            return data

        except Exception as e:
            print(f"❌ [东方财富] 获取失败: {e}")
            return []


class RealTimeDataManager:
    """实时数据管理器"""

    def __init__(self):
        self.sources = [
            RealTimeDataSource(),
        ]
        print(f"✅ 实时数据管理器初始化完成，共 {len(self.sources)} 个数据源")

    def fetch_data(self, symbols: List[str]) -> List[Dict]:
        """
        获取股票实时数据（自动降级）

        Args:
            symbols: 股票代码列表

        Returns:
            股票数据列表
        """
        all_data = []

        # 尝试各个数据源
        data_source = RealTimeDataSource()

        # 1. 尝试东方财富（数据最全）
        data = data_source.fetch_from_eastmoney(symbols)
        if data:
            all_data.extend(data)
            return all_data

        # 2. 尝试新浪财经
        data = data_source.fetch_from_sina(symbols)
        if data:
            all_data.extend(data)
            return all_data

        # 3. 尝试腾讯财经
        data = data_source.fetch_from_tencent(symbols)
        if data:
            all_data.extend(data)
            return all_data

        print(f"❌ 所有数据源均不可用")
        return all_data


def test_realtime():
    """测试实时数据获取"""
    print("="*80)
    print("🧪 测试实时数据获取")
    print("="*80)

    manager = RealTimeDataManager()

    print("\n📊 测试获取股票数据:")
    test_symbols = ['000063', '600519', '000858', '300750']

    for symbol in test_symbols:
        data = manager.fetch_data([symbol])

        if data:
            for stock in data:
                print(f"\n  {stock['symbol']} {stock['name']} [{stock['source']}]")
                print(f"    当前价格: ¥{stock['price']:.2f}")
                print(f"    涨跌幅:   {stock['change_percent']:+.2f}%")
                print(f"    成交量:   {stock['volume']:,.0f}")
        else:
            print(f"\n  {symbol}: 数据获取失败")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_realtime()
