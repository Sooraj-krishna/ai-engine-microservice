"""
Rate Limiting for CodeAnalyzer
Prevents abuse by limiting analyses per user/IP.
"""

import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional
import os

# Configuration
MAX_REQUESTS_PER_HOUR = int(os.getenv('CODE_ANALYZER_MAX_REQUESTS_HOUR', 10))
MAX_REQUESTS_PER_DAY = int(os.getenv('CODE_ANALYZER_MAX_REQUESTS_DAY', 50))
RATE_LIMIT_WINDOW_SECONDS = 3600  # 1 hour


class RateLimiter:
    """Rate limiter for code analysis requests."""
    
    def __init__(self, max_per_hour: int = MAX_REQUESTS_PER_HOUR, 
                 max_per_day: int = MAX_REQUESTS_PER_DAY):
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.requests = defaultdict(list)  # user_id -> list of timestamps
    
    def check_rate_limit(self, user_id: str) -> Dict:
        """
        Check if user has exceeded rate limit.
        
        Args:
            user_id: User identifier (email, API key, IP, etc.)
            
        Returns:
            {
                'allowed': bool,
                'remaining_hour': int,
                'remaining_day': int,
                'reset_at': str (ISO timestamp)
            }
        """
        now = time.time()
        
        # Clean old requests
        self._cleanup_old_requests(user_id, now)
        
        # Get request counts
        requests_last_hour = self._count_requests(user_id, now, 3600)
        requests_last_day = self._count_requests(user_id, now, 86400)
        
        # Check limits
        allowed = (
            requests_last_hour < self.max_per_hour and
            requests_last_day < self.max_per_day
        )
        
        # Calculate reset time
        if self.requests[user_id]:
            oldest_request = min(self.requests[user_id])
            reset_at = datetime.fromtimestamp(oldest_request + 3600).isoformat()
        else:
            reset_at = datetime.now().isoformat()
        
        return {
            'allowed': allowed,
            'remaining_hour': max(0, self.max_per_hour - requests_last_hour),
            'remaining_day': max(0, self.max_per_day - requests_last_day),
            'reset_at': reset_at,
            'current_hour': requests_last_hour,
            'current_day': requests_last_day
        }
    
    def record_request(self, user_id: str):
        """Record a request for rate limiting."""
        self.requests[user_id].append(time.time())
    
    def _cleanup_old_requests(self, user_id: str, now: float):
        """Remove requests older than 24 hours."""
        if user_id in self.requests:
            self.requests[user_id] = [
                ts for ts in self.requests[user_id]
                if now - ts < 86400  # 24 hours
            ]
    
    def _count_requests(self, user_id: str, now: float, window_seconds: int) -> int:
        """Count requests within time window."""
        if user_id not in self.requests:
            return 0
        
        return sum(1 for ts in self.requests[user_id] if now - ts < window_seconds)
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get rate limit statistics for a user."""
        now = time.time()
        self._cleanup_old_requests(user_id, now)
        
        return {
            'user_id': user_id,
            'requests_last_hour': self._count_requests(user_id, now, 3600),
            'requests_last_day': self._count_requests(user_id, now, 86400),
            'total_requests': len(self.requests[user_id]),
            'max_per_hour': self.max_per_hour,
            'max_per_day': self.max_per_day
        }


# Global rate limiter instance
rate_limiter = RateLimiter()
