#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新浪财经数据源（独立版本）
"""

import requests
from typing import List, Dict


class SinaDataSource:
    """新浪财经数据源"""

    def __init__(self):
        self.name = "新浪财经"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 10

    def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """从新浪财经获取数据"""
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
                    parts = data_str.split(',')

                    if len(parts) >= 32:
                        # 提取股票代码
                        var_name = line.split('=')[0]
                        if len(var_name) > 9:
                            code = var_name[9:]
                            # 转换回标准格式
                            if code.startswith('6'):
                                symbol_std = f'sh{code}'
                            else:
                                symbol_std = f'sz{code}'

                        name = parts[0]
                        open_price = float(parts[1]) if parts[1] and parts[1] != '' else 0.0
                        yesterday_close = float(parts[2]) if parts[2] and parts[2] != '' else 0.0
                        current_price = float(parts[3]) if parts[3] and parts[3] != '' else 0.0
                        volume = float(parts[8]) if parts[8] and parts[8] != '' else 0.0

                        change_percent = 0.0
                        if yesterday_close > 0 and current_price > 0:
                            change_percent = ((current_price - yesterday_close) / yesterday_close) * 100

                        stock_data = {
                            'symbol': symbol_std,
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
                print(f"🌐 [新浪财经] 成功获取 {len(data)} 只股票数据")

            return data

        except Exception as e:
            print(f"❌ [新浪财经] 获取数据失败: {e}")
            return []

    def is_available(self) -> bool:
        """检查数据源是否可用"""
        try:
            response = requests.get("http://hq.sinajs.cn/list=sh600000", 
                                    headers=self.headers, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_name(self) -> str:
        return self.name


# 测试
if __name__ == "__main__":
    sina = SinaDataSource()
    data = sina.fetch_stock_data(['600519', '000063'])
    
    for stock in data:
        print(f"{stock['symbol']} {stock['name']}: ¥{stock['price']:.2f} ({stock['change_percent']:+.2f}%)")
