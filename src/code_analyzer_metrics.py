"""
Monitoring and Metrics for CodeAnalyzer
Tracks analysis time, alerts on timeouts, and monitors resource usage.
"""

import time
import psutil
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
from pathlib import Path

# Configuration
METRICS_DIR = os.getenv('CODE_ANALYZER_METRICS_DIR', '/tmp/code_analyzer_metrics')
ALERT_THRESHOLD_SECONDS = int(os.getenv('CODE_ANALYZER_ALERT_THRESHOLD', 30))
MEMORY_ALERT_MB = int(os.getenv('CODE_ANALYZER_MEMORY_ALERT_MB', 500))


class AnalysisMetrics:
    """Track and monitor code analysis metrics."""
    
    def __init__(self):
        self.metrics_dir = Path(METRICS_DIR)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.metrics_dir / 'metrics.json'
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict:
        """Load existing metrics from disk."""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return {
            'total_analyses': 0,
            'total_time_seconds': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'timeouts': 0,
            'errors': 0,
            'analyses_by_repo': {},
            'recent_analyses': []
        }
    
    def _save_metrics(self):
        """Save metrics to disk."""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"[METRICS] Failed to save metrics: {e}")
    
    def record_analysis(self, repo_path: str, duration: float, 
                       files_analyzed: int, cache_hit: bool = False, 
                       timed_out: bool = False, error: Optional[str] = None):
        """
        Record analysis metrics.
        
        Args:
            repo_path: Repository path
            duration: Analysis duration in seconds
            files_analyzed: Number of files analyzed
            cache_hit: Whether result came from cache
            timed_out: Whether analysis timed out
            error: Error message if analysis failed
        """
        self.metrics['total_analyses'] += 1
        self.metrics['total_time_seconds'] += duration
        
        if cache_hit:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
        
        if timed_out:
            self.metrics['timeouts'] += 1
        
        if error:
            self.metrics['errors'] += 1
        
        # Track per-repository
        repo_key = os.path.basename(repo_path)
        if repo_key not in self.metrics['analyses_by_repo']:
            self.metrics['analyses_by_repo'][repo_key] = {
                'count': 0,
                'total_time': 0.0,
                'avg_time': 0.0
            }
        
        repo_metrics = self.metrics['analyses_by_repo'][repo_key]
        repo_metrics['count'] += 1
        repo_metrics['total_time'] += duration
        repo_metrics['avg_time'] = repo_metrics['total_time'] / repo_metrics['count']
        
        # Keep recent analyses (last 100)
        analysis_record = {
            'timestamp': datetime.now().isoformat(),
            'repo': repo_key,
            'duration': round(duration, 2),
            'files': files_analyzed,
            'cache_hit': cache_hit,
            'timed_out': timed_out,
            'error': error
        }
        
        self.metrics['recent_analyses'].append(analysis_record)
        self.metrics['recent_analyses'] = self.metrics['recent_analyses'][-100:]  # Keep last 100
        
        # Alert if slow
        if duration > ALERT_THRESHOLD_SECONDS and not cache_hit:
            self._alert_slow_analysis(repo_key, duration)
        
        # Save metrics
        self._save_metrics()
    
    def _alert_slow_analysis(self, repo: str, duration: float):
        """Alert on slow analysis."""
        alert_msg = f"[ALERT] Slow analysis detected! Repo: {repo}, Duration: {duration:.2f}s (threshold: {ALERT_THRESHOLD_SECONDS}s)"
        print(alert_msg)
        
        # Write to alert log
        alert_file = self.metrics_dir / 'alerts.log'
        with open(alert_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {alert_msg}\n")
    
    def get_stats(self) -> Dict:
        """Get current statistics."""
        total = self.metrics['total_analyses']
        if total == 0:
            return {'message': 'No analyses recorded yet'}
        
        stats = {
            'total_analyses': total,
            'average_duration': round(self.metrics['total_time_seconds'] / total, 2),
            'cache_hit_rate': round(self.metrics['cache_hits'] / total * 100, 1),
            'timeout_rate': round(self.metrics['timeouts'] / total * 100, 1),
            'error_rate': round(self.metrics['errors'] / total * 100, 1),
            'top_repositories': sorted(
                self.metrics['analyses_by_repo'].items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:10]
        }
        
        return stats
    
    def monitor_memory(self) -> Dict:
        """Monitor current memory usage."""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # Alert if high memory
        if memory_mb > MEMORY_ALERT_MB:
            alert_msg = f"[ALERT] High memory usage: {memory_mb:.1f}MB (threshold: {MEMORY_ALERT_MB}MB)"
            print(alert_msg)
            
            alert_file = self.metrics_dir / 'alerts.log'
            with open(alert_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - {alert_msg}\n")
        
        return {
            'memory_mb': round(memory_mb, 1),
            'memory_percent': round(process.memory_percent(), 1),
            'cpu_percent': round(process.cpu_percent(), 1)
        }


# Global metrics instance
analysis_metrics = AnalysisMetrics()
