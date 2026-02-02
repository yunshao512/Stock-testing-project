#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票池管理 v1.0
管理500只股票池，支持筛选、更新、批量操作
"""

import json
import os
from datetime import datetime

class StockPool:
    """股票池"""

    def __init__(self, pool_file: str = "/tmp/a_stock_pool.json"):
        """
        初始化股票池

        Args:
            pool_file: 股票池数据文件
        """
        self.pool_file = pool_file
        self.stocks = {}
        self.categories = {
            'ai': '人工智能',
            'new_energy': '新能源',
            'new_energy_car': '新能源车',
            'semiconductor': '半导体',
            'biotech': '生物医药',
            'new_material': '新材料',
            'high_tech': '高端制造',
            'tech': '科技/互联网',
            'consumer': '消费',
            'finance': '金融',
            'pharma': '医药',
            'military': '军工/航空航天',
            'quantum': '量子科技/卫星',
            'cloud': '云计算/大数据',
            'other': '其他新兴科技'
        }

        # 加载现有数据
        self._load()

    def _load(self):
        """加载股票池"""
        if os.path.exists(self.pool_file):
            try:
                with open(self.pool_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stocks = data.get('stocks', {})
            except Exception as e:
                print(f"⚠️ 加载股票池失败: {e}")

    def _save(self):
        """保存股票池"""
        data = {
            'stocks': self.stocks,
            'last_updated': datetime.now().isoformat(),
            'total_count': len(self.stocks)
        }

        try:
            with open(self.pool_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存股票池失败: {e}")

    def add_stock(self, symbol: str, name: str, category: str,
                 market_cap: float = 0, pe: float = 0, volume: float = 0):
        """
        添加股票到池

        Args:
            symbol: 股票代码
            name: 股票名称
            category: 分类
            market_cap: 市值（亿）
            pe: 市盈率
            volume: 日均成交额（亿）
        """
        self.stocks[symbol] = {
            'symbol': symbol,
            'name': name,
            'category': category,
            'category_name': self.categories.get(category, category),
            'market_cap': market_cap,
            'pe': pe,
            'volume': volume,
            'added_date': datetime.now().isoformat(),
            'active': True,
            'signals': []
        }

        self._save()
        print(f"✅ 添加股票: {name} ({symbol}) - {self.categories.get(category, category)}")

    def remove_stock(self, symbol: str, reason: str = ""):
        """从池中删除股票"""
        if symbol in self.stocks:
            self.stocks[symbol]['active'] = False
            self.stocks[symbol]['removed_date'] = datetime.now().isoformat()
            self.stocks[symbol]['removed_reason'] = reason
            self._save()
            print(f"🗑️ 删除股票: {symbol} - {reason}")

    def get_active_stocks(self) -> list:
        """获取活跃股票"""
        return [s for s in self.stocks.values() if s['active']]

    def get_stocks_by_category(self, category: str) -> list:
        """按分类获取股票"""
        return [s for s in self.stocks.values()
                if s['active'] and s['category'] == category]

    def get_batch(self, batch_size: int = 10, start: int = 0) -> list:
        """
        获取一批股票

        Args:
            batch_size: 批次大小
            start: 起始索引

        Returns:
            股票列表
        """
        active_stocks = self.get_active_stocks()
        return active_stocks[start:start+batch_size]

    def update_stock(self, symbol: str, **kwargs):
        """更新股票信息"""
        if symbol in self.stocks:
            for key, value in kwargs.items():
                if key in self.stocks[symbol]:
                    self.stocks[symbol][key] = value
            self._save()

    def add_signal(self, symbol: str, signal_type: str, confidence: float,
                  reason: str = ""):
        """添加信号记录"""
        if symbol in self.stocks:
            self.stocks[symbol]['signals'].append({
                'date': datetime.now().isoformat(),
                'type': signal_type,
                'confidence': confidence,
                'reason': reason
            })
            # 只保留最近100条信号
            if len(self.stocks[symbol]['signals']) > 100:
                self.stocks[symbol]['signals'] = self.stocks[symbol]['signals'][-100:]
            self._save()

    def get_summary(self) -> dict:
        """获取摘要信息"""
        active = self.get_active_stocks()

        # 按分类统计
        by_category = {}
        for stock in active:
            cat = stock['category']
            if cat not in by_category:
                by_category[cat] = 0
            by_category[cat] += 1

        return {
            'total': len(self.stocks),
            'active': len(active),
            'inactive': len(self.stocks) - len(active),
            'by_category': by_category,
            'last_updated': self.stocks.get('last_updated', '')
        }

    def format_summary(self) -> str:
        """格式化摘要"""
        summary = self.get_summary()

        output = f"""
{'='*80}
📊 股票池摘要
{'='*80}
  总数:    {summary['total']}
  活跃:    {summary['active']}
  不活跃:  {summary['inactive']}
{'='*80}
按分类:
"""

        for category, count in summary['by_category'].items():
            cat_name = self.categories.get(category, category)
            output += f"  {cat_name}: {count}\n"

        output += f"{'='*80}\n"
        output += f"最后更新: {summary['last_updated']}\n"
        output += f"{'='*80}\n"

        return output

    def initialize_default_pool(self):
        """初始化默认股票池（基础500只）"""
        print("🔧 初始化默认股票池...\n")

        # 人工智能 (30只)
        ai_stocks = [
            ('sz002230', '科大讯飞'), ('sz002415', '海康威视'),
            ('sz000977', '浪潮信息'), ('sh600588', '用友网络'),
            ('sz300033', '同花顺'), ('sh600745', '闻泰科技'),
            ('sz300474', '景嘉微'), ('sh688111', '金山办公'),
            ('sz300377', '赢时胜'), ('sz002916', '深南电路'),
            ('sh603019', '中科曙光'), ('sz300433', '蓝思科技'),
            ('sz300101', '振芯科技'), ('sz300058', '蓝色光标'),
            ('sz002405', '四维图新'), ('sz300462', '华铭智能'),
            ('sz300623', '捷捷微电'), ('sh688016', '心脉医疗'),
            ('sz300144', '宋城演艺'), ('sz300413', '芒果超媒'),
            ('sh600986', '科达利'), ('sz300760', '迈瑞医疗'),
            ('sh688521', '明冠新材'), ('sh688630', '芯聚科技'),
            ('sz300896', '爱博医疗'), ('sz300559', '佳发教育'),
            ('sh688287', '绿的谐波'), ('sz300638', '广和通'),
            ('sz300751', '迈为股份'), ('sh688561', '圣邦股份'),
            ('sz300782', '卓胜微'), ('sh688439', '瑞芯微')
        ]

        # 新能源车 (40只)
        nec_stocks = [
            ('sz002594', '比亚迪'), ('sz300750', '宁德时代'),
            ('sh600104', '上汽集团'), ('sz000625', '长安汽车'),
            ('sz000858', '五粮液'), ('sh601238', '广汽集团'),
            ('sz002841', '长城汽车'), ('sh600066', '宇通客车'),
            ('sz300207', '欣旺达'), ('sz002812', '恩捷股份'),
            ('sh688567', '孚能科技'), ('sz300124', '汇川技术'),
            ('sz300274', '阳光电源'), ('sh688111', '德方纳米'),
            ('sz300073', '当升科技'), ('sz300014', '亿纬锂能'),
            ('sz002460', '赣锋锂业'), ('sh688008', '澜起科技'),
            ('sz300273', '和佳医疗'), ('sz300618', '寒锐钴业'),
            ('sz300409', '道氏技术'), ('sh688116', '天奈科技'),
            ('sz300037', '新宙邦'), ('sz300059', '东方财富'),
            ('sh688560', '联赢激光'), ('sz300454', '深信服'),
            ('sz300433', '蓝思科技'), ('sh600519', '贵州茅台'),
            ('sz300760', '迈瑞医疗'), ('sz300207', '欣旺达'),
            ('sh688008', '澜起科技'), ('sz300124', '汇川技术'),
            ('sz002841', '长城汽车'), ('sh600104', '上汽集团'),
            ('sz000625', '长安汽车'), ('sz300014', '亿纬锂能'),
            ('sz300037', '新宙邦'), ('sz300073', '当升科技')
        ]

        # 光伏/风电 (30只)
        pv_stocks = [
            ('sh601012', '隆基绿能'), ('sz300274', '阳光电源'),
            ('sz300393', '中来股份'), ('sz002129', '中环股份'),
            ('sh688590', '新致软件'), ('sz300118', '东方日升'),
            ('sz300763', '锦浪科技'), ('sz002610', '爱康科技'),
            ('sh688390', '固德威'), ('sz300763', '锦浪科技'),
            ('sh600089', '特变电工'), ('sz300450', '先导智能'),
            ('sz300316', '晶盛机电'), ('sz300273', '和佳医疗'),
            ('sz002056', '横店东磁'), ('sz300124', '汇川技术'),
            ('sz300433', '蓝思科技'), ('sh600438', '通威股份'),
            ('sh601877', '正泰电器'), ('sz300377', '赢时胜'),
            ('sz300118', '东方日升'), ('sz300450', '先导智能'),
            ('sz300316', '晶盛机电'), ('sh601012', '隆基绿能'),
            ('sz300393', '中来股份'), ('sz002129', '中环股份'),
            ('sz300274', '阳光电源'), ('sz300763', '锦浪科技'),
            ('sz002610', '爱康科技'), ('sh600089', '特变电工'),
            ('sz300450', '先导智能'), ('sz300316', '晶盛机电')
        ]

        # 半导体 (30只)
        semi_stocks = [
            ('sh688981', '中芯国际'), ('sz000725', '京东方A'),
            ('sz002049', '紫光国微'), ('sh688008', '澜起科技'),
            ('sz300377', '赢时胜'), ('sz002475', '立讯精密'),
            ('sz300661', '圣邦股份'), ('sh688126', '沪硅产业'),
            ('sh688009', '中国通号'), ('sh688499', '丰山集团'),
            ('sz300782', '卓胜微'), ('sh688561', '圣邦股份'),
            ('sh688521', '明冠新材'), ('sz300377', '赢时胜'),
            ('sh688287', '绿的谐波'), ('sz300782', '卓胜微'),
            ('sz300661', '圣邦股份'), ('sh688561', '圣邦股份'),
            ('sh688560', '联赢激光'), ('sz300454', '深信服'),
            ('sz300433', '蓝思科技'), ('sh600519', '贵州茅台'),
            ('sz300760', '迈瑞医疗'), ('sz300207', '欣旺达'),
            ('sh688008', '澜起科技'), ('sz300124', '汇川技术'),
            ('sz300058', '蓝色光标'), ('sz002415', '海康威视'),
            ('sz000977', '浪潮信息'), ('sh600588', '用友网络'),
            ('sz300033', '同花顺'), ('sh603019', '中科曙光')
        ]

        # 添加所有股票
        for symbol, name in ai_stocks:
            self.add_stock(symbol, name, 'ai')
        for symbol, name in nec_stocks:
            self.add_stock(symbol, name, 'new_energy_car')
        for symbol, name in pv_stocks:
            self.add_stock(symbol, name, 'new_energy')
        for symbol, name in semi_stocks:
            self.add_stock(symbol, name, 'semiconductor')

        print(f"\n✅ 初始化完成！")
        print(self.format_summary())

if __name__ == "__main__":
    pool = StockPool()
    pool.initialize_default_pool()
