"""
AI Cache Manager - Caches AI API responses to reduce costs and improve performance.
"""

from typing import Optional, Any
from datetime import datetime, timedelta
import hashlib
import json


class AICacheManager:
    """Cache manager specifically for AI API responses."""
    
    def __init__(self):
        self._cache = {}
        self.default_ttl = timedelta(hours=6)  # 6 hours for AI responses
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0
        }
    
    def _generate_prompt_hash(self, prompt: str, model: str = "default") -> str:
        """Generate hash from prompt and model."""
        key_str = f"{model}:{prompt}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, prompt: str, model: str = "default") -> Optional[Any]:
        """Get cached AI response for a prompt."""
        self.stats["total_requests"] += 1
        
        key = self._generate_prompt_hash(prompt, model)
        
        if key not in self._cache:
            self.stats["misses"] += 1
            return None
        
        entry = self._cache[key]
        if datetime.now() > entry["expires_at"]:
            # Expired
            del self._cache[key]
            self.stats["misses"] += 1
            return None
        
        self.stats["hits"] += 1
        hit_rate = (self.stats["hits"] / self.stats["total_requests"]) * 100
        print(f"[AI_CACHE] Cache hit! (Hit rate: {hit_rate:.1f}%)")
        return entry["response"]
    
    def set(self, prompt: str, response: Any, model: str = "default", ttl: Optional[timedelta] = None) -> None:
        """Cache an AI response."""
        if ttl is None:
            ttl = self.default_ttl
        
        key = self._generate_prompt_hash(prompt, model)
        
        self._cache[key] = {
            "response": response,
            "expires_at": datetime.now() + ttl,
            "created_at": datetime.now(),
            "prompt_length": len(prompt),
            "model": model
        }
        
        print(f"[AI_CACHE] Cached AI response (TTL: {ttl})")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self.stats["total_requests"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "total_requests": total,
            "cache_hits": self.stats["hits"],
            "cache_misses": self.stats["misses"],
            "hit_rate_percentage": round(hit_rate, 2),
            "total_cached_entries": len(self._cache),
            "estimated_api_calls_saved": self.stats["hits"]
        }
    
    def clear(self) -> None:
        """Clear all cached responses."""
        count = len(self._cache)
        self._cache.clear()
        print(f"[AI_CACHE] Cleared {count} cached AI responses")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if datetime.now() > entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            print(f"[AI_CACHE] Cleaned up {len(expired_keys)} expired AI responses")
        
        return len(expired_keys)


# Global AI cache instance
ai_cache = AICacheManager()
