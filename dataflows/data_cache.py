#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据缓存管理器
提高数据获取效率，减少API调用
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class DataCacheManager:
    """数据缓存管理器"""

    def __init__(self, cache_dir: str = None, cache_hours: int = 1):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录
            cache_hours: 缓存有效期（小时）
        """
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'cache'
        )

        self.cache_hours = cache_hours

        # 创建缓存目录
        os.makedirs(self.cache_dir, exist_ok=True)

        print(f"✅ 数据缓存管理器初始化完成")
        print(f"   缓存目录: {self.cache_dir}")
        print(f"   有效期: {cache_hours}小时")

    def _get_cache_key(self, key_type: str, **kwargs) -> str:
        """生成缓存键"""
        parts = [key_type]
        for k, v in sorted(kwargs.items()):
            parts.append(f"{k}={v}")
        return '_'.join(parts) + '.json'

    def _get_cache_path(self, cache_key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, cache_key)

    def _is_cache_valid(self, cache_path: str) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(cache_path):
            return False

        # 检查文件修改时间
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        expiry_time = datetime.now() - timedelta(hours=self.cache_hours)

        return file_time > expiry_time

    def get(self, key_type: str, **kwargs) -> Optional[Dict]:
        """
        从缓存获取数据

        Args:
            key_type: 缓存类型（如：stock_data, historical_data）
            **kwargs: 缓存键参数

        Returns:
            缓存数据，如果无效返回None
        """
        cache_key = self._get_cache_key(key_type, **kwargs)
        cache_path = self._get_cache_path(cache_key)

        # 检查缓存是否存在且有效
        if not self._is_cache_valid(cache_path):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查数据是否为空
            if not data:
                return None

            print(f"✅ [缓存] 命中: {cache_key}")
            return data

        except Exception as e:
            print(f"❌ [缓存] 读取失败: {e}")
            return None

    def set(self, key_type: str, data: Dict, **kwargs):
        """
        保存数据到缓存

        Args:
            key_type: 缓存类型
            data: 要缓存的数据
            **kwargs: 缓存键参数
        """
        cache_key = self._get_cache_key(key_type, **kwargs)
        cache_path = self._get_cache_path(cache_key)

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"💾 [缓存] 保存: {cache_key}")

        except Exception as e:
            print(f"❌ [缓存] 保存失败: {e}")

    def delete(self, key_type: str, **kwargs):
        """
        删除指定缓存

        Args:
            key_type: 缓存类型
            **kwargs: 缓存键参数
        """
        cache_key = self._get_cache_key(key_type, **kwargs)
        cache_path = self._get_cache_path(cache_key)

        if os.path.exists(cache_path):
            os.remove(cache_path)
            print(f"🗑️ [缓存] 删除: {cache_key}")

    def clear_all(self):
        """清空所有缓存"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)

            print(f"🗑️ [缓存] 已清空所有缓存")

        except Exception as e:
            print(f"❌ [缓存] 清空失败: {e}")

    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'valid_files': 0,
            'expired_files': 0
        }

        try:
            now = datetime.now()
            expiry_time = now - timedelta(hours=self.cache_hours)

            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    stats['total_files'] += 1

                    file_path = os.path.join(self.cache_dir, filename)
                    file_size = os.path.getsize(file_path)
                    stats['total_size'] += file_size

                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                    if file_time > expiry_time:
                        stats['valid_files'] += 1
                    else:
                        stats['expired_files'] += 1

        except Exception as e:
            print(f"❌ [缓存] 统计失败: {e}")

        return stats

    def cleanup_expired(self):
        """清理过期缓存"""
        try:
            now = datetime.now()
            expiry_time = now - timedelta(hours=self.cache_hours)

            cleaned = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                    if file_time <= expiry_time:
                        os.remove(file_path)
                        cleaned += 1

            if cleaned > 0:
                print(f"🗑️ [缓存] 已清理 {cleaned} 个过期文件")
            else:
                print(f"✅ [缓存] 没有过期文件")

        except Exception as e:
            print(f"❌ [缓存] 清理失败: {e}")


# 单例模式
_cache_instance = None

def get_cache(cache_dir: str = None, cache_hours: int = 1) -> DataCacheManager:
    """获取缓存管理器实例（单例）"""
    global _cache_instance

    if _cache_instance is None:
        _cache_instance = DataCacheManager(cache_dir, cache_hours)

    return _cache_instance


def test_cache():
    """测试缓存管理器"""
    print("="*80)
    print("🧪 测试数据缓存管理器")
    print("="*80)

    cache = get_cache(cache_hours=0.5)  # 30分钟过期

    print("\n📊 缓存统计:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n💾 测试缓存操作:")
    test_data = {
        'symbol': '600519',
        'price': 1438.00,
        'timestamp': datetime.now().isoformat()
    }

    cache.set('stock_data', test_data, symbol='600519')
    cached_data = cache.get('stock_data', symbol='600519')

    if cached_data:
        print(f"✅ 缓存读取成功: {cached_data['symbol']} = ¥{cached_data['price']:.2f}")
    else:
        print(f"❌ 缓存读取失败")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_cache()
