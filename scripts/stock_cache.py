#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

class StockDataCache:
    """股票数据缓存管理器"""

    def __init__(self, cache_dir="/tmp/a_stock_cache", cache_ttl=60):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录
            cache_ttl: 缓存有效期（秒），默认60秒
        """
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl
        self.cache_file = os.path.join(cache_dir, "stock_data.json")

        # 创建缓存目录
        os.makedirs(cache_dir, exist_ok=True)

        # 加载现有缓存
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        """从文件加载缓存"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            pass
        return {}

    def _save_cache(self):
        """保存缓存到文件"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存缓存失败: {e}")

    def get(self, key: str) -> Optional[Dict]:
        """获取缓存数据"""
        if key not in self.cache:
            return None

        cached_data = self.cache[key]
        cached_time = datetime.fromisoformat(cached_data.get('timestamp', ''))
        now = datetime.now()

        # 检查是否过期
        if (now - cached_time).total_seconds() > self.cache_ttl:
            del self.cache[key]
            return None

        return cached_data['data']

    def set(self, key: str, data: Any):
        """设置缓存数据"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()

    def clear(self):
        """清空缓存"""
        self.cache = {}
        self._save_cache()

    def clear_expired(self):
        """清理过期缓存"""
        now = datetime.now()
        expired_keys = []

        for key, cached_data in self.cache.items():
            cached_time = datetime.fromisoformat(cached_data.get('timestamp', ''))
            if (now - cached_time).total_seconds() > self.cache_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            self._save_cache()


class RateLimiter:
    """API请求频率限制器"""

    def __init__(self, max_requests=10, time_window=60):
        """
        初始化频率限制器

        Args:
            max_requests: 时间窗口内最大请求数
            time_window: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def can_request(self) -> bool:
        """检查是否可以发起请求"""
        now = time.time()

        # 清理过期的请求记录
        self.requests = [t for t in self.requests if now - t < self.time_window]

        # 检查是否超过限制
        if len(self.requests) >= self.max_requests:
            return False

        self.requests.append(now)
        return True

    def get_wait_time(self) -> float:
        """获取等待时间（秒）"""
        if len(self.requests) < self.max_requests:
            return 0

        now = time.time()
        oldest_request = min(self.requests)
        return self.time_window - (now - oldest_request)

    def get_status(self) -> Dict[str, Any]:
        """获取限流状态"""
        now = time.time()
        recent_requests = [t for t in self.requests if now - t < self.time_window]

        return {
            'total_requests': len(self.requests),
            'recent_requests': len(recent_requests),
            'max_requests': self.max_requests,
            'time_window': self.time_window,
            'can_request': self.can_request(),
            'wait_time': self.get_wait_time()
        }
