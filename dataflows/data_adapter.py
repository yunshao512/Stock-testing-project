#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多数据源适配器
支持多个A股数据源，自动切换和降级
"""

import time
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class StockDataSource(ABC):
    """股票数据源抽象基类"""

    @abstractmethod
    def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """获取股票实时数据"""
        pass

    @abstractmethod
    def fetch_historical_data(self, symbol: str, period: str, days: int) -> List[Dict]:
        """获取历史数据"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查数据源是否可用"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """获取数据源名称"""
        pass


class TencentDataSource(StockDataSource):
    """腾讯财经数据源（默认）"""

    def __init__(self):
        self.name = "腾讯财经"
        self.base_url = "https://qt.gtimg.cn/q="
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """获取股票实时数据"""
        try:
            import requests

            # 构建请求URL
            symbol_list = []
            for symbol in symbols:
                # 转换股票代码格式
                if symbol.startswith('sh'):
                    symbol_list.append(f'sh{symbol[2:]}')
                elif symbol.startswith('sz'):
                    symbol_list.append(f'sz{symbol[2:]}')
                else:
                    # 默认为上海
                    symbol_list.append(f'sh{symbol}')

            url = f"{self.base_url}{','.join(symbol_list)}"

            # 请求数据
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'gbk'

            # 解析数据
            data = []
            lines = response.text.strip().split('\n')

            for i, line in enumerate(lines):
                if line.startswith('v_'):
                    parts = line.split('~')
                    if len(parts) > 40:
                        symbol = parts[0][2:]  # 去掉 'v_' 前缀
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
                            'volume': volume
                        }
                        data.append(stock_data)

            if data:
                print(f"🌐 [{self.name}] 成功获取 {len(data)} 只股票数据")

            return data

        except Exception as e:
            print(f"❌ [{self.name}] 获取数据失败: {e}")
            return []

    def fetch_historical_data(self, symbol: str, period: str, days: int) -> List[Dict]:
        """获取历史数据（腾讯财经不支持，返回空）"""
        # 腾讯财经API不支持历史数据，需要使用其他数据源
        return []

    def is_available(self) -> bool:
        """检查数据源是否可用"""
        try:
            import requests
            response = requests.get(self.base_url + 'sh600000', timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_name(self) -> str:
        return self.name


class AkShareDataSource(StockDataSource):
    """AkShare数据源（待安装）"""

    def __init__(self):
        self.name = "AkShare"
        self.available = False

        # 尝试导入akshare
        try:
            import akshare as ak
            self.ak = ak
            self.available = True
            print(f"✅ [{self.name}] 导入成功")
        except ImportError:
            print(f"⚠️ [{self.name}] 未安装，使用备用数据源")

    def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """获取股票实时数据"""
        if not self.available:
            return []

        try:
            data = []
            for symbol in symbols:
                # AkShare接口
                stock_data = self.ak.stock_zh_a_spot_em()

                # 查找对应的股票
                stock_info = stock_data[stock_data['代码'] == symbol]

                if not stock_info.empty:
                    row = stock_info.iloc[0]
                    stock = {
                        'symbol': symbol,
                        'name': row['名称'],
                        'price': row['最新价'],
                        'yesterday_close': row['昨收'],
                        'change_percent': row['涨跌幅'],
                        'volume': row['成交量']
                    }
                    data.append(stock)

            if data:
                print(f"🌐 [{self.name}] 成功获取 {len(data)} 只股票数据")

            return data

        except Exception as e:
            print(f"❌ [{self.name}] 获取数据失败: {e}")
            return []

    def fetch_historical_data(self, symbol: str, period: str, days: int) -> List[Dict]:
        """获取历史数据"""
        if not self.available:
            return []

        try:
            # AkShare历史数据接口
            if period == '1d':
                stock_hist = self.ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
            else:
                stock_hist = self.ak.stock_zh_a_hist(symbol=symbol, period=period, adjust="qfq")

            # 转换为统一格式
            candles = []
            for _, row in stock_hist.tail(days).iterrows():
                candles.append({
                    'date': row['日期'].strftime('%Y-%m-%d'),
                    'open': float(row['开盘']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'close': float(row['收盘']),
                    'volume': int(row['成交量']),
                    'amount': float(row['成交额'])
                })

            print(f"🌐 [{self.name}] 成功获取 {len(candles)} 条历史数据")
            return candles

        except Exception as e:
            print(f"❌ [{self.name}] 获取历史数据失败: {e}")
            return []

    def is_available(self) -> bool:
        """检查数据源是否可用"""
        return self.available

    def get_name(self) -> str:
        return self.name


class TushareDataSource(StockDataSource):
    """Tushare数据源（待安装+Token）"""

    def __init__(self, token: Optional[str] = None):
        self.name = "Tushare"
        self.token = token
        self.available = False

        if not token:
            print(f"⚠️ [{self.name}] 未配置Token，跳过")
            return

        # 尝试导入tushare
        try:
            import tushare as ts
            ts.set_token(token)
            self.ts = ts
            self.available = True
            print(f"✅ [{self.name}] 导入成功")
        except ImportError:
            print(f"⚠️ [{self.name}] 未安装，使用备用数据源")

    def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """获取股票实时数据"""
        if not self.available:
            return []

        try:
            # 转换股票代码格式
            ts_codes = [f"{symbol[2:]}.{symbol[:2]}" for symbol in symbols]

            pro = self.ts.pro_api()
            data = pro.daily(ts_code=','.join(ts_codes), start_date='', end_date='')

            stocks = []
            for _, row in data.iterrows():
                symbol = f"{row['ts_code'][3:]}{row['ts_code'][:2].upper()}"
                stocks.append({
                    'symbol': symbol,
                    'name': '',  # Tushare需要额外查询股票名称
                    'price': float(row['close']),
                    'yesterday_close': float(row['pre_close']),
                    'change_percent': float(row['pct_chg']),
                    'volume': int(row['vol'])
                })

            print(f"🌐 [{self.name}] 成功获取 {len(stocks)} 只股票数据")
            return stocks

        except Exception as e:
            print(f"❌ [{self.name}] 获取数据失败: {e}")
            return []

    def fetch_historical_data(self, symbol: str, period: str, days: int) -> List[Dict]:
        """获取历史数据"""
        if not self.available:
            return []

        try:
            ts_code = f"{symbol[2:]}.{symbol[:2]}"

            pro = self.ts.pro_api()
            data = pro.daily(ts_code=ts_code, limit=days)

            candles = []
            for _, row in data.iterrows():
                candles.append({
                    'date': row['trade_date'],
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['vol']),
                    'amount': float(row['amount'])
                })

            # 按日期排序
            candles.reverse()

            print(f"🌐 [{self.name}] 成功获取 {len(candles)} 条历史数据")
            return candles

        except Exception as e:
            print(f"❌ [{self.name}] 获取历史数据失败: {e}")
            return []

    def is_available(self) -> bool:
        """检查数据源是否可用"""
        return self.available

    def get_name(self) -> str:
        return self.name


class DataAdapterManager:
    """数据源适配器管理器"""

    def __init__(self, tushare_token: Optional[str] = None):
        """初始化数据源管理器"""
        self.sources: List[StockDataSource] = []

        # 添加数据源（优先级从高到低）
        self.sources.append(TencentDataSource())  # 默认数据源
        self.sources.append(AkShareDataSource())   # 待安装

        if tushare_token:
            self.sources.append(TushareDataSource(tushare_token))

        print(f"✅ 数据源管理器初始化完成，共 {len(self.sources)} 个数据源")

    def fetch_stock_data(self, symbols: List[str], use_cache: bool = True) -> List[Dict]:
        """
        获取股票实时数据（自动切换数据源）

        Args:
            symbols: 股票代码列表
            use_cache: 是否使用缓存

        Returns:
            股票数据列表
        """
        # 尝试各个数据源
        for source in self.sources:
            if source.is_available():
                print(f"📡 使用数据源: {source.get_name()}")

                data = source.fetch_stock_data(symbols)

                if data:
                    return data
                else:
                    print(f"⚠️ 数据源 {source.get_name()} 返回空数据，尝试下一个...")

        print(f"❌ 所有数据源均不可用")
        return []

    def fetch_historical_data(self, symbol: str, period: str = '1d', days: int = 30) -> List[Dict]:
        """
        获取历史数据（自动切换数据源）

        Args:
            symbol: 股票代码
            period: 周期（1d=日线, 1w=周线, 1m=月线）
            days: 天数

        Returns:
            历史数据列表
        """
        # 尝试各个数据源
        for source in self.sources:
            if source.is_available():
                print(f"📡 使用数据源: {source.get_name()}")

                data = source.fetch_historical_data(symbol, period, days)

                if data:
                    return data
                else:
                    print(f"⚠️ 数据源 {source.get_name()} 返回空数据，尝试下一个...")

        print(f"❌ 所有数据源均不可用")
        return []

    def get_available_sources(self) -> List[str]:
        """获取可用的数据源列表"""
        return [s.get_name() for s in self.sources if s.is_available()]


# 单例模式
_adapter_instance = None

def get_adapter(tushare_token: Optional[str] = None) -> DataAdapterManager:
    """获取数据源适配器实例（单例）"""
    global _adapter_instance

    if _adapter_instance is None:
        _adapter_instance = DataAdapterManager(tushare_token)

    return _adapter_instance


def test_adapter():
    """测试数据源适配器"""
    print("="*80)
    print("🧪 测试数据源适配器")
    print("="*80)

    adapter = get_adapter()

    print("\n📊 可用数据源:")
    for source_name in adapter.get_available_sources():
        print(f"  • {source_name}")

    print("\n📡 测试获取股票数据...")
    data = adapter.fetch_stock_data(['600519', '000858', '300750'])

    if data:
        for stock in data:
            print(f"  {stock['symbol']} {stock['name']}: ¥{stock['price']:.2f} ({stock['change_percent']:+.2f}%)")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_adapter()
