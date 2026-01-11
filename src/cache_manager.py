"""
Cache Manager - Simple in-memory caching for competitive analysis results.
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import hashlib
import json


class CacheManager:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = timedelta(hours=24)  # 24 hours for competitive analysis
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if datetime.now() > entry["expires_at"]:
            # Expired, remove from cache
            del self._cache[key]
            return None
        
        print(f"[CACHE] Cache hit for key: {key[:16]}...")
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        """Set value in cache with TTL."""
        if ttl is None:
            ttl = self.default_ttl
        
        self._cache[key] = {
            "value": value,
            "expires_at": datetime.now() + ttl,
            "created_at": datetime.now()
        }
        print(f"[CACHE] Cached result for key: {key[:16]}... (TTL: {ttl})")
    
    def invalidate(self, key: str) -> None:
        """Invalidate a cache entry."""
        if key in self._cache:
            del self._cache[key]
            print(f"[CACHE] Invalidated key: {key[:16]}...")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        print(f"[CACHE] Cleared {count} cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        expired_entries = sum(
            1 for entry in self._cache.values()
            if datetime.now() > entry["expires_at"]
        )
        
        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_entries,
            "expired_entries": expired_entries
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if datetime.now() > entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            print(f"[CACHE] Cleaned up {len(expired_keys)} expired entries")
        
        return len(expired_keys)


# Global cache instance
cache_manager = CacheManager()
