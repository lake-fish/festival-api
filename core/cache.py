# core/cache.py
"""简易内存缓存，生产环境建议用Redis"""
import time
from typing import Any, Optional
from functools import wraps


class SimpleCache:
    def __init__(self, ttl: int = 3600):
        self._cache: dict[str, tuple[Any, float]] = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self._cache:
            return None
        value, expire_at = self._cache[key]
        if time.time() > expire_at:
            del self._cache[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存"""
        expire_at = time.time() + (ttl or self.ttl)
        self._cache[key] = (value, expire_at)

    def clear(self):
        """清空缓存"""
        self._cache.clear()


# 全局缓存实例
cache = SimpleCache()


def cached(key_prefix: str, ttl: Optional[int] = None):
    """缓存装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存key
            cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"

            # 尝试获取缓存
            result = cache.get(cache_key)
            if result is not None:
                return result

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator