#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from stock_api import fetch_stock_data, format_stock, get_rate_limiter_status, clear_cache

def search_stock(keyword):
    """股票代码搜索（简版）"""
    # 常用股票映射
    stock_map = {
        '茅台': 'sh600519',
        '贵州茅台': 'sh600519',
        '平安': 'sz000001',
        '平安银行': 'sz000001',
        '腾讯': 'hk00700',
        '腾讯控股': 'hk00700',
        '招行': 'sh600036',
        '招商银行': 'sh600036',
        '万科': 'sz000002',
        '万科A': 'sz000002',
        '五粮液': 'sz000858',
        '比亚迪': 'sz002594',
        '宁德时代': 'sz300750',
        '格力': 'sz000651',
        '格力电器': 'sz000651',
        '美的': 'sz000333',
        '美的集团': 'sz000333',
        '中芯国际': 'sh688981',
        '工商银行': 'sh601398',
        '建设银行': 'sh601939',
        '中国银行': 'sh601988',
        '农业银行': 'sh601288',
        '中国移动': 'sh600941',
        '中国石油': 'sh601857',
        '中国石化': 'sh600028',
        '浦发银行': 'sh600000',
        '民生银行': 'sh600016',
        '华夏银行': 'sh600015',
        '兴业银行': 'sh601166',
        '中信证券': 'sh600030',
        '海通证券': 'sh600837',
        '中国平安': 'sh601318',
        '中国人寿': 'sh601628',
        '新华保险': 'sh601336',
    }

    # 精确匹配
    if keyword in stock_map:
        return stock_map[keyword]

    # 模糊匹配
    for name, code in stock_map.items():
        if keyword in name:
            return code

    # 直接返回（假设用户输入的是代码）
    return keyword

def main():
    if len(sys.argv) < 2:
        print("📊 A股数据查询工具 v2.0")
        print("\n用法:")
        print("  python3 a_stock.py <股票代码>     # 查询单股")
        print("  python3 a_stock.py <代码1>,<代码2>  # 查询多股")
        print("  python3 a_stock.py --status        # 查看API状态")
        print("  python3 a_stock.py --clear        # 清空缓存")
        print("\n示例:")
        print("  python3 a_stock.py sh600519")
        print("  python3 a_stock.py 茅台")
        print("  python3 a_stock.py sh600519,sz000001,hk00700")
        print("\n支持搜索:")
        print("  茅台, 平安, 腾讯, 招行, 万科, 五粮液, 比亚迪, 宁德时代, 格力, 美的等")
        sys.exit(0)

    # 特殊命令
    if sys.argv[1] == '--status':
        print("📊 API限流状态:")
        status = get_rate_limiter_status()
        print(f"  已用请求: {status['recent_requests']}/{status['max_requests']} (每{status['time_window']}秒)")
        print(f"  是否可请求: {'是' if status['can_request'] else '否'}")
        if not status['can_request']:
            print(f"  需等待: {status['wait_time']:.1f}秒")
        sys.exit(0)

    if sys.argv[1] == '--clear':
        clear_cache()
        sys.exit(0)

    # 解析股票代码
    input_codes = sys.argv[1]
    stock_codes = []

    # 处理多股查询
    if ',' in input_codes:
        codes = input_codes.split(',')
        for code in codes:
            code = code.strip()
            # 如果是中文名，搜索代码
            if not code.startswith(('sh', 'sz', 'hk')):
                code = search_stock(code)
            stock_codes.append(code)
    else:
        # 单股查询
        code = input_codes
        if not code.startswith(('sh', 'sz', 'hk')):
            code = search_stock(code)
        stock_codes = [code]

    print(f"📊 正在查询: {', '.join(stock_codes)}\n")

    # 获取数据
    stocks = fetch_stock_data(stock_codes)

    if not stocks:
        print("❌ 获取数据失败，请稍后重试")
        print("\n💡 提示:")
        print("  - 检查股票代码是否正确")
        print("  - 可能触发频率限制，请等待1-2分钟")
        print("  - 使用 --status 查看API状态")
        sys.exit(1)

    if len(stocks) == 0:
        print("❌ 未找到股票数据")
        sys.exit(1)

    # 输出格式化信息
    for stock in stocks:
        print(format_stock(stock))

    # 显示API状态
    print(f"\n📊 API状态: {get_rate_limiter_status()['recent_requests']}/{get_rate_limiter_status()['max_requests']} 请求/分钟")

if __name__ == "__main__":
    main()
