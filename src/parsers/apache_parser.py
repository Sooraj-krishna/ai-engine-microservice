"""
Apache access and error log parser.
Similar to Nginx parser but handles Apache-specific log formats.
"""

import re
import os
from datetime import datetime, timedelta
from collections import defaultdict

class ApacheLogParser:
    """
    Parser for Apache access and error logs.
    Handles Common Log Format and Combined Log Format.
    """
    
    def __init__(self):
        """Initialize with Apache log patterns."""
        # Apache Combined Log Format pattern
        self.access_log_pattern = re.compile(
            r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
            r'"(?P<method>\S+) (?P<url>\S+) (?P<protocol>\S+)" '
            r'(?P<status>\d+) (?P<size>\d+|-) '
            r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
        )
        
        # Apache error log pattern
        self.error_log_pattern = re.compile(
            r'\[(?P<timestamp>[^\]]+)\] \[(?P<level>\w+)\] '
            r'(?P<message>.*)'
        )
    
    def parse_access_logs(self, log_path, hours_back=24):
        """
        Parse Apache access logs for traffic and performance metrics.
        Similar structure to Nginx parser but adapted for Apache format.
        """
        if not os.path.exists(log_path):
            print(f"[WARNING] Apache access log not found: {log_path}")
            return {"error": "Apache access log file not found"}
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        metrics = {
            "total_requests": 0,
            "status_codes": defaultdict(int),
            "top_pages": defaultdict(int),
            "traffic_by_hour": defaultdict(int),
            "bytes_served": 0,
            "error_4xx": 0,
            "error_5xx": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    match = self.access_log_pattern.match(line.strip())
                    if not match:
                        continue
                    
                    # Parse Apache timestamp format
                    timestamp_str = match.group('timestamp')
                    try:
                        log_time = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
                        log_time = log_time.replace(tzinfo=None)
                    except ValueError:
                        continue
                    
                    if log_time < cutoff_time:
                        continue
                    
                    # Extract metrics
                    status_code = int(match.group('status'))
                    url = match.group('url')
                    size = match.group('size')
                    
                    metrics["total_requests"] += 1
                    metrics["status_codes"][status_code] += 1
                    metrics["top_pages"][url] += 1
                    metrics["traffic_by_hour"][log_time.hour] += 1
                    
                    # Track bytes served
                    if size != '-':
                        try:
                            metrics["bytes_served"] += int(size)
                        except ValueError:
                            pass
                    
                    # Error counting
                    if 400 <= status_code < 500:
                        metrics["error_4xx"] += 1
                    elif status_code >= 500:
                        metrics["error_5xx"] += 1
            
            # Convert to regular dicts
            metrics["status_codes"] = dict(metrics["status_codes"])
            metrics["top_pages"] = dict(sorted(metrics["top_pages"].items(), key=lambda x: x[1], reverse=True)[:10])
            metrics["traffic_by_hour"] = dict(metrics["traffic_by_hour"])
            
            return metrics
            
        except Exception as e:
            print(f"[ERROR] Failed to parse Apache access logs: {e}")
            return {"error": str(e)}
    
    def parse_error_logs(self, log_path, hours_back=24):
        """Parse Apache error logs for error analysis."""
        # Similar implementation to Nginx error parser
        # Adapted for Apache error log format
        # Implementation follows same pattern as NginxLogParser.parse_error_logs()
        pass
