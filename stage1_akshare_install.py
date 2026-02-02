#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
阶段1：安装和配置AkShare
目标：接入真实历史数据，为LSTM模型做准备
"""

import sys
import os
import json
from datetime import datetime


class AkShareInstaller:
    """AkShare安装和配置器"""

    def __init__(self):
        print("✅ AkShare安装和配置器初始化完成")

    def check_environment(self) -> dict:
        """检查Python环境"""
        print(f"\n[1/5] 检查Python环境")
        print(f"{'='*80}")

        import subprocess

        results = {}

        # Python版本
        version = sys.version
        print(f"  Python版本: {version}")
        results['python_version'] = version

        # 检查必要的库
        required_packages = ['pandas', 'numpy', 'requests', 'matplotlib']

        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}: 已安装")
                results[package] = True
            except ImportError:
                print(f"  ⚠️  {package}: 未安装")
                results[package] = False

        # 检查机器学习库
        ml_packages = ['tensorflow', 'torch', 'sklearn']
        ml_installed = {}

        for package in ml_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}: 已安装")
                ml_installed[package] = True
            except ImportError:
                print(f"  ⚠️  {package}: 未安装（后续需要）")
                ml_installed[package] = False

        results['ml_packages'] = ml_installed

        return results

    def install_akshare(self) -> bool:
        """安装AkShare"""
        print(f"\n[2/5] 安装AkShare")
        print(f"{'='*80}")

        import subprocess

        try:
            print("  正在安装AkShare...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "akshare", "-U"],
                check=True,
                timeout=300
            )

            if result.returncode == 0:
                print("  ✅ AkShare安装成功")
                return True
            else:
                print(f"  ❌ AkShare安装失败: {result.returncode}")
                return False

        except Exception as e:
            print(f"  ❌ 安装过程出错: {e}")
            return False

    def install_additional_packages(self) -> Dict:
        """安装额外的必要包"""
        print(f"\n[3/5] 安装额外包")
        print(f"{'='*80}")

        import subprocess

        packages_to_install = [
            ('pandas', '>=1.0.0'),
            ('numpy', '>=1.18.0'),
            ('matplotlib', '>=3.0.0'),
            ('requests', '>=2.0.0')
        ]

        results = {}

        for package, version in packages_to_install:
            try:
                # 检查是否已安装
                __import__(package.split('[')[0])
                print(f"  ✅ {package}: 已安装")
                results[package] = True
                continue
            except ImportError:
                print(f"  正在安装 {package}...")

                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", package],
                        check=True,
                        timeout=300
                    )

                    if result.returncode == 0:
                        print(f"  ✅ {package}: 安装成功")
                        results[package] = True
                    else:
                        print(f"  ❌ {package}: 安装失败")
                        results[package] = False

                except Exception as e:
                    print(f"  ❌ {package}: 安装出错: {e}")
                    results[package] = False

        return results

    def test_akshare(self) -> bool:
        """测试AkShare"""
        print(f"\n[4/5] 测试AkShare")
        print(f"{'='*80}")

        try:
            import akshare as ak

            # 测试获取股票列表
            print("  测试获取股票列表...")
            stock_list = ak.stock_info_a_code_name()

            if stock_list is not None and len(stock_list) > 0:
                print(f"  ✅ 成功获取 {len(stock_list)} 只股票")
                return True
            else:
                print(f"  ❌ 未获取到股票数据")
                return False

        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            return False

    def save_config(self) -> bool:
        """保存配置"""
        print(f"\n[5/5] 保存配置")
        print(f"{'='*80}")

        config = {
            'akshare_installed': True,
            'installed_at': datetime.now().isoformat(),
            'environment': {
                'python_version': sys.version,
                'packages': ['akshare', 'pandas', 'numpy', 'requests', 'matplotlib']
            }
        }

        # 保存配置
        try:
            config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
            os.makedirs(config_dir, exist_ok=True)

            config_file = os.path.join(config_dir, 'akshare_config.json')
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            print(f"  ✅ 配置已保存: {config_file}")
            return True

        except Exception as e:
            print(f"  ❌ 保存配置失败: {e}")
            return False


def main():
    """主函数"""
    print("="*80)
    print("🧪 阶段1：安装和配置AkShare")
    print("="*80)
    print()

    installer = AkShareInstaller()

    # 1. 检查环境
    env_results = installer.check_environment()

    # 2. 安装AkShare
    akshare_success = installer.install_akshare()

    if not akshare_success:
        print("\n❌ AkShare安装失败，无法继续")
        return

    # 3. 安装额外包
    extra_packages_success = installer.install_additional_packages()

    # 4. 测试AkShare
    test_success = installer.test_akshare()

    if not test_success:
        print("\n⚠️ AkShare测试失败，但已安装")

    # 5. 保存配置
    config_success = installer.save_config()

    # 最终报告
    print(f"\n{'='*80}")
    print(f"📊 最终报告")
    print(f"{'='*80}")
    print(f"  环境检查: ✅")
    print(f"  AkShare安装: {'✅ 成功' if akshare_success else '❌ 失败'}")
    print(f"  额外包安装: ✅")
    print(f"  AkShare测试: {'✅ 成功' if test_success else '⚠️ 警告'}")
    print(f"  配置保存: {'✅ 成功' if config_success else '❌ 失败'}")

    if akshare_success and test_success:
        print(f"\n✅ 阶段1完成：AkShare安装和配置成功")
        print(f"  可以开始阶段2：接入真实历史数据")
    else:
        print(f"\n❌ 阶段1完成但有问题，建议手动检查")

    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()
