#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据适配器 v3.0 - 简化版
直接使用新浪财经和腾讯财经，避免循环依赖
"""

import requests
from typing import List, Dict


class SimpleSinaDataSource:
    """新浪财经数据源（简化）"""

    def __init__(self):
        self.name = "新浪财经"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 10

    def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """从新浪财经获取数据"""
        try:
            symbol_list = []
            for symbol in symbols:
                if symbol.startswith('sh'):
                    symbol_list.append(f'sh{symbol[2:]}')
                elif symbol.startswith('sz'):
                    symbol_list.append(f'sz{symbol[2:]}')
                else:
                    symbol_list.append(f'sh{symbol}')

            symbols_str = ",".join(symbol_list)
            url = "http://hq.sinajs.cn/list=" + symbols_str

            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.encoding = 'gbk'

            data = []
            lines = response.text.strip().split('\n')

            for line in lines:
                if line.startswith('var hq_str_'):
                    data_str = line.split('"')[1]
                    parts = data_str.split(',')

                    if len(parts) >= 32:
                        var_name = line.split('=')[0]
                        if len(var_name) > 9:
                            code = var_name[9:]
                            if code.startswith('6'):
                                symbol = f'sh{code}'
                            else:
                                symbol = f'sz{code}'

                        name = parts[0]
                        current_price = float(parts[3]) if parts[3] and parts[3] != '' else 0.0
                        yesterday_close = float(parts[2]) if parts[2] and parts[2] != '' else 0.0
                        change_percent = 0.0

                        if yesterday_close > 0 and current_price > 0:
                            change_percent = ((current_price - yesterday_close) / yesterday_close) * 100

                        volume = float(parts[8]) if parts[8] and parts[8] != '' else 0.0

                        stock_data = {
                            'symbol': symbol,
                            'name': name,
                            'price': current_price,
                            'yesterday_close': yesterday_close,
                            'change_percent': change_percent,
                            'volume': volume,
                            'source': '新浪财经'
                        }
                        data.append(stock_data)

            if data:
                print(f"🌐 [新浪财经] 成功获取 {len(data)} 只股票数据")

            return data

        except Exception as e:
            print(f"❌ [新浪财经] 获取数据失败: {e}")
            return []


class SimpleTencentDataSource:
    """腾讯财经数据源（简化）"""

    def __init__(self):
        self.name = "腾讯财经"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 10

    def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """从腾讯财经获取数据"""
        try:
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

            if data:
                print(f"🌐 [腾讯财经] 成功获取 {len(data)} 只股票数据")

            return data

        except Exception as e:
            print(f"❌ [腾讯财经] 获取数据失败: {e}")
            return []


class SimpleDataAdapter:
    """简化版数据适配器"""

    def __init__(self):
        self.sources = [
            SimpleSinaDataSource(),
            SimpleTencentDataSource(),
        ]
        print(f"✅ 简化数据适配器初始化完成，共 {len(self.sources)} 个数据源")

    def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """获取股票实时数据"""
        for source in self.sources:
            data = source.fetch_stock_data(symbols)
            if data:
                return data

        print(f"❌ 所有数据源均不可用")
        return []


# 测试
if __name__ == "__main__":
    adapter = SimpleDataAdapter()
    data = adapter.fetch_stock_data(['600519', '000063', '000858'])

    for stock in data:
        print(f"{stock['symbol']} {stock['name']}: ¥{stock['price']:.2f} ({stock['change_percent']:+.2f}%) [来源: {stock['source']}]")
