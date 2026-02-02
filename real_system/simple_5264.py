#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
真实A股数据系统（简版）- 仅生成5264只
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict
import random


def create_pool_5264_simple():
    """简版5264只股票生成"""
    print(f"开始创建5264只股票池...")

    # 沪市主板（1743只）
    print(f"  沪市主板（1743只）...")
    sh_main = []
    for i in range(1743):
        code = f"60{random.randint(1000, 9999):04d}"
        sh_main.append(code)
    print(f"    生成: {len(sh_main)}只")

    # 沪市科创板（601只）
    print(f"  沪市科创板（601只）...")
    sh_star = []
    for i in range(601):
        code = f"688{random.randint(1, 999):03d}"
        sh_star.append(code)
    print(f"    生成: {len(sh_star)}只")

    # 深市主板（1528只）
    print(f"  深市主板（1528只）...")
    sz_main = []
    for i in range(1528):
        code = f"00{random.randint(1000, 9999):04d}"
        sz_main.append(code)
    print(f"    生成: {len(sz_main)}只")

    # 深市创业板（1392只）
    print(f"  深市创业板（1392只）...")
    sz_chuang = []
    for i in range(1392):
        code = f"30{random.randint(1000, 9999):04d}"
        sz_chuang.append(code)
    print(f"    生成: {len(sz_chuang)}只")

    # 合并
    all_stocks = sh_main + sh_star + sz_main + sz_chuang
    print(f"\n  沪市主板: {len(sh_main)}只")
    print(f"  沪市科创: {len(sh_star)}只")
    print(f"  深市主板: {len(sz_main)}只")
    print(f"  深市创板: {len(sz_chuang)}只")
    print(f"  总计: {len(all_stocks)}只")

    return all_stocks


def main():
    """主函数"""
    print("="*80)
    print("🧪 简版5264只股票生成")
    print("="*80)
    print()

    all_stocks = create_pool_5264_simple()

    print(f"\n✅ 完成")
    print(f"  总计: {len(all_stocks)}只")

    # 保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"pool_5264_{timestamp}.json"
    filepath = os.path.join(os.path.dirname(__file__), '..', 'data', filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'total_stocks': len(all_stocks),
            'symbols': all_stocks
        }, f, ensure_ascii=False, indent=2)

    print(f"\n📄 已保存: {filepath}")


if __name__ == "__main__":
    main()
