#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
阶段1简化版：AkShare安装和配置
"""

import sys
import os
import json
from datetime import datetime


def check_environment():
    """检查环境"""
    print(f"\n[1/5] 检查Python环境")

    version = sys.version
    print(f"  Python版本: {version}")

    # 检查必要的库
    packages = ['pandas', 'numpy', 'requests', 'matplotlib']
    print(f"  必要库: {', '.join(packages)}")

    all_installed = True
    for package in packages:
        try:
            __import__(package)
            print(f"  ✅ {package}: 已安装")
        except ImportError:
            print(f"  ❌ {package}: 未安装")
            all_installed = False

    return all_installed


def install_akshare():
    """安装AkShare"""
    print(f"\n[2/5] 安装AkShare")

    import subprocess

    try:
        print("  正在安装...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "akshare", "-U"],
            check=True,
            timeout=300
        )

        if result.returncode == 0:
            print("  ✅ AkShare安装成功")
            return True
        else:
            print(f"  ❌ 安装失败: {result.returncode}")
            return False

    except Exception as e:
        print(f"  ❌ 出错: {e}")
        return False


def install_additional():
    """安装额外包"""
    print(f"\n[3/5] 安装额外包")

    import subprocess

    packages = ['pandas', 'numpy', 'matplotlib', 'requests']

    for package in packages:
        try:
            __import__(package.split('[')[0])
            print(f"  ✅ {package}: 已安装")
        except ImportError:
            try:
                print(f"  正在安装 {package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                    timeout=300
                )

                if result.returncode == 0:
                    print(f"  ✅ {package}: 安装成功")
                else:
                    print(f"  ❌ {package}: 安装失败")
            except Exception as e:
                print(f"  ❌ {package}: 出错 {e}")

    return True


def test_akshare():
    """测试AkShare"""
    print(f"\n[4/5] 测试AkShare")

    try:
        import akshare as ak

        print("  测试连接...")
        stock_list = ak.stock_info_a_code_name()

        if stock_list is not None and len(stock_list) > 0:
            print(f"  ✅ 成功连接")
            print(f"  获取到 {len(stock_list)} 只股票")
            return True
        else:
            print(f"  ⚠️ 未获取到股票数据")
            return False

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False


def save_config():
    """保存配置"""
    print(f"\n[5/5] 保存配置")

    config = {
        'installed_at': datetime.now().isoformat(),
        'status': 'completed'
    }

    try:
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        os.makedirs(config_dir, exist_ok=True)

        config_file = os.path.join(config_dir, 'stage1_config.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"  ✅ 配置已保存: {config_file}")
        return True

    except Exception as e:
        print(f"  ❌ 保存失败: {e}")
        return False


def main():
    """主函数"""
    print("="*80)
    print("🧪 阶段1：AkShare安装和配置")
    print("="*80)
    print()

    # 1. 检查环境
    env_ok = check_environment()

    # 2. 安装AkShare
    akshare_ok = install_akshare()

    # 3. 安装额外包
    extra_ok = install_additional()

    # 4. 测试AkShare
    test_ok = test_akshare()

    # 5. 保存配置
    config_ok = save_config()

    # 最终报告
    print(f"\n{'='*80}")
    print("📊 最终报告")
    print(f"{'='*80}")
    print(f"  环境检查: {'✅ 正常' if env_ok else '❌ 异常'}")
    print(f"  AkShare安装: {'✅ 成功' if akshare_ok else '❌ 失败'}")
    print(f"  测试结果: {'✅ 成功' if test_ok else '❌ 失败'}")
    print(f"  配置保存: {'✅ 成功' if config_ok else '❌ 失败'}")

    if akshare_ok and test_ok:
        print(f"\n✅ 阶段1完成：AkShare已安装和配置")
        print(f"  可以开始阶段2：接入真实历史数据")
    else:
        print(f"\n❌ 阶段1完成但存在问题")

    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()
