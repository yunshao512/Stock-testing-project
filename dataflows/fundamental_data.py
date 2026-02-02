#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基本面数据获取模块
接入真实财务数据源
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataflows import get_cache
from typing import Dict, List, Optional


class FundamentalDataProvider:
    """基本面数据提供者"""

    def __init__(self):
        self.cache = get_cache(cache_hours=24)  # 财务数据缓存24小时
        self.sources = {}

        # 尝试初始化数据源
        self._init_sources()

    def _init_sources(self):
        """初始化数据源"""
        # 尝试Tushare
        try:
            import tushare as ts
            # 检查是否有token
            token = os.getenv('TUSHARE_TOKEN')
            if token:
                self.sources['tushare'] = ts
                print(f"✅ [基本面] Tushare已配置")
        except ImportError:
            print(f"⚠️ [基本面] Tushare未安装")

        # 尝试AkShare
        try:
            import akshare as ak
            self.sources['akshare'] = ak
            print(f"✅ [基本面] AkShare已配置")
        except ImportError:
            print(f"⚠️ [基本面] AkShare未安装")

        if not self.sources:
            print(f"⚠️ [基本面] 无可用数据源，使用模拟数据")

    def fetch_financial_data(self, symbol: str, use_cache: bool = True) -> Dict:
        """
        获取财务数据

        Args:
            symbol: 股票代码
            use_cache: 是否使用缓存

        Returns:
            财务数据字典
        """
        # 尝试从缓存获取
        if use_cache:
            cached_data = self.cache.get('financial_data', symbol=symbol)
            if cached_data:
                print(f"✅ [基本面] 使用缓存的财务数据")
                return cached_data

        # 尝试从各数据源获取
        for source_name, source in self.sources.items():
            try:
                data = self._fetch_from_source(source_name, source, symbol)
                if data:
                    # 保存到缓存
                    if use_cache:
                        self.cache.set('financial_data', data, symbol=symbol)
                    return data
            except Exception as e:
                print(f"❌ [基本面] {source_name}获取失败: {e}")
                continue

        # 使用模拟数据
        return self._get_mock_data(symbol)

    def _fetch_from_source(self, source_name: str, source, symbol: str) -> Optional[Dict]:
        """从指定数据源获取数据"""
        if source_name == 'tushare':
            return self._fetch_from_tushare(source, symbol)
        elif source_name == 'akshare':
            return self._fetch_from_akshare(source, symbol)
        return None

    def _fetch_from_tushare(self, ts, symbol: str) -> Optional[Dict]:
        """从Tushare获取财务数据"""
        ts_code = f"{symbol[2:]}.{symbol[:2]}"

        pro = ts.pro_api()

        # 获取最新的财务指标
        df = pro.fina_indicator(
            ts_code=ts_code,
            start_date='20240101',
            end_date='20241231'
        )

        if df.empty:
            return None

        # 获取最新一期数据
        latest = df.iloc[0]

        data = {
            'symbol': symbol,
            'source': 'tushare',
            'pe_ratio': float(latest.get('pe', 0)),
            'pb_ratio': float(latest.get('pb', 0)),
            'roe': float(latest.get('roe', 0)) / 100,
            'revenue_growth': 0,  # 需要从income表获取
            'profit_growth': 0,    # 需要从income表获取
            'debt_ratio': float(latest.get('debt_to_assets', 0)) / 100,
            'report_date': str(latest.get('end_date', ''))
        }

        return data

    def _fetch_from_akshare(self, ak, symbol: str) -> Optional[Dict]:
        """从AkShare获取财务数据"""
        try:
            # 获取个股财务指标
            df = ak.stock_financial_analysis_indicator(symbol=symbol)

            if df.empty:
                return None

            # 获取最新一期数据
            latest = df.iloc[0]

            data = {
                'symbol': symbol,
                'source': 'akshare',
                'pe_ratio': float(latest.get('市盈率-动态', 0)),
                'pb_ratio': float(latest.get('市净率', 0)),
                'roe': float(latest.get('净资产收益率', 0)) / 100,
                'revenue_growth': 0,
                'profit_growth': 0,
                'debt_ratio': 0,
                'report_date': str(latest.get('日期', ''))
            }

            return data

        except Exception as e:
            print(f"❌ [基本面] AkShare获取失败: {e}")
            return None

    def _get_mock_data(self, symbol: str) -> Dict:
        """获取模拟数据（备用方案）"""
        # 根据股票板块返回不同的模拟数据
        if symbol.startswith('60'):  # 上海主板
            return {
                'symbol': symbol,
                'source': 'mock',
                'pe_ratio': 25.0,
                'pb_ratio': 3.5,
                'roe': 0.12,
                'revenue_growth': 0.08,
                'profit_growth': 0.10,
                'debt_ratio': 0.45,
                'report_date': '2024-12-31'
            }
        elif symbol.startswith('00'):  # 深圳主板
            return {
                'symbol': symbol,
                'source': 'mock',
                'pe_ratio': 30.0,
                'pb_ratio': 4.0,
                'roe': 0.15,
                'revenue_growth': 0.12,
                'profit_growth': 0.15,
                'debt_ratio': 0.50,
                'report_date': '2024-12-31'
            }
        elif symbol.startswith('30'):  # 创业板
            return {
                'symbol': symbol,
                'source': 'mock',
                'pe_ratio': 40.0,
                'pb_ratio': 5.0,
                'roe': 0.18,
                'revenue_growth': 0.20,
                'profit_growth': 0.25,
                'debt_ratio': 0.40,
                'report_date': '2024-12-31'
            }
        else:
            return {
                'symbol': symbol,
                'source': 'mock',
                'pe_ratio': 20.0,
                'pb_ratio': 2.5,
                'roe': 0.10,
                'revenue_growth': 0.05,
                'profit_growth': 0.06,
                'debt_ratio': 0.55,
                'report_date': '2024-12-31'
            }


# 单例模式
_provider_instance = None

def get_fundamental_provider() -> FundamentalDataProvider:
    """获取基本面数据提供者实例（单例）"""
    global _provider_instance

    if _provider_instance is None:
        _provider_instance = FundamentalDataProvider()

    return _provider_instance


def test_fundamental():
    """测试基本面数据获取"""
    print("="*80)
    print("🧪 测试基本面数据获取")
    print("="*80)

    provider = get_fundamental_provider()

    print("\n📊 测试获取财务数据:")
    test_symbols = ['600519', '000858', '300750']

    for symbol in test_symbols:
        data = provider.fetch_financial_data(symbol)

        print(f"\n  {symbol}:")
        print(f"    来源: {data.get('source', 'N/A')}")
        print(f"    市盈率: {data.get('pe_ratio', 0):.2f}")
        print(f"    市净率: {data.get('pb_ratio', 0):.2f}")
        print(f"    净资产收益率: {data.get('roe', 0)*100:.2f}%")
        print(f"    营收增长: {data.get('revenue_growth', 0)*100:.2f}%")
        print(f"    利润增长: {data.get('profit_growth', 0)*100:.2f}%")
        print(f"    负债率: {data.get('debt_ratio', 0)*100:.2f}%")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_fundamental()
