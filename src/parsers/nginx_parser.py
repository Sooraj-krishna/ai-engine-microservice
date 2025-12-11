"""
Nginx access and error log parser.
Extracts performance metrics, error patterns, and traffic data from Nginx logs.
"""

import re
import os
from datetime import datetime, timedelta
from collections import defaultdict

class NginxLogParser:
    """
    Parser for Nginx access and error logs.
    Extracts metrics like response times, error rates, traffic patterns.
    """
    
    def __init__(self):
        """Initialize with common Nginx log patterns."""
        # Standard Nginx access log format pattern
        self.access_log_pattern = re.compile(
            r'(?P<ip>\S+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
            r'"(?P<method>\S+) (?P<url>\S+) (?P<protocol>\S+)" '
            r'(?P<status>\d+) (?P<size>\d+) '
            r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
            r'(?: "(?P<response_time>[\d.]+)")?'
        )
        
        # Error log pattern
        self.error_log_pattern = re.compile(
            r'(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) '
            r'\[(?P<level>\w+)\] (?P<pid>\d+)#(?P<tid>\d+): '
            r'(?P<message>.*)'
        )
    
    def parse_access_logs(self, log_path, hours_back=24):
        """
        Parse Nginx access logs to extract performance and traffic metrics.
        
        Args:
            log_path (str): Path to Nginx access log file
            hours_back (int): How many hours back to analyze
            
        Returns:
            dict: Parsed metrics including response times, status codes, traffic
        """
        if not os.path.exists(log_path):
            print(f"[WARNING] Access log file not found: {log_path}")
            return {"error": "Access log file not found"}
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        metrics = {
            "total_requests": 0,
            "status_codes": defaultdict(int),
            "response_times": [],
            "top_pages": defaultdict(int),
            "traffic_by_hour": defaultdict(int),
            "user_agents": defaultdict(int),
            "error_4xx": 0,
            "error_5xx": 0,
            "avg_response_time": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    match = self.access_log_pattern.match(line.strip())
                    if not match:
                        continue
                    
                    # Parse timestamp
                    timestamp_str = match.group('timestamp')
                    try:
                        log_time = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
                        log_time = log_time.replace(tzinfo=None)  # Remove timezone for comparison
                    except ValueError:
                        continue
                    
                    # Skip old entries
                    if log_time < cutoff_time:
                        continue
                    
                    # Extract data
                    status_code = int(match.group('status'))
                    url = match.group('url')
                    response_time = match.group('response_time')
                    user_agent = match.group('user_agent')
                    
                    # Aggregate metrics
                    metrics["total_requests"] += 1
                    metrics["status_codes"][status_code] += 1
                    metrics["top_pages"][url] += 1
                    metrics["traffic_by_hour"][log_time.hour] += 1
                    
                    # Track user agents (simplified)
                    if 'bot' in user_agent.lower():
                        metrics["user_agents"]["bot"] += 1
                    elif 'mobile' in user_agent.lower():
                        metrics["user_agents"]["mobile"] += 1
                    else:
                        metrics["user_agents"]["desktop"] += 1
                    
                    # Response time tracking
                    if response_time and response_time != '-':
                        try:
                            rt = float(response_time)
                            metrics["response_times"].append(rt)
                        except ValueError:
                            pass
                    
                    # Error tracking
                    if 400 <= status_code < 500:
                        metrics["error_4xx"] += 1
                    elif status_code >= 500:
                        metrics["error_5xx"] += 1
            
            # Calculate averages
            if metrics["response_times"]:
                metrics["avg_response_time"] = sum(metrics["response_times"]) / len(metrics["response_times"])
            
            # Convert defaultdicts to regular dicts for JSON serialization
            metrics["status_codes"] = dict(metrics["status_codes"])
            metrics["top_pages"] = dict(sorted(metrics["top_pages"].items(), key=lambda x: x[1], reverse=True)[:10])
            metrics["traffic_by_hour"] = dict(metrics["traffic_by_hour"])
            metrics["user_agents"] = dict(metrics["user_agents"])
            
            return metrics
            
        except Exception as e:
            print(f"[ERROR] Failed to parse access logs: {e}")
            return {"error": str(e)}
    
    def parse_error_logs(self, log_path, hours_back=24):
        """
        Parse Nginx error logs to identify issues and error patterns.
        
        Args:
            log_path (str): Path to Nginx error log file
            hours_back (int): How many hours back to analyze
            
        Returns:
            dict: Error metrics and patterns
        """
        if not os.path.exists(log_path):
            print(f"[WARNING] Error log file not found: {log_path}")
            return {"error": "Error log file not found"}
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        error_data = {
            "total_errors": 0,
            "error_levels": defaultdict(int),
            "error_messages": defaultdict(int),
            "recent_errors": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    match = self.error_log_pattern.match(line.strip())
                    if not match:
                        continue
                    
                    # Parse timestamp
                    timestamp_str = match.group('timestamp')
                    try:
                        log_time = datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S')
                    except ValueError:
                        continue
                    
                    # Skip old entries
                    if log_time < cutoff_time:
                        continue
                    
                    # Extract error data
                    level = match.group('level')
                    message = match.group('message')
                    
                    error_data["total_errors"] += 1
                    error_data["error_levels"][level] += 1
                    
                    # Categorize error messages (simplified)
                    if 'connection' in message.lower():
                        error_data["error_messages"]["connection_error"] += 1
                    elif 'timeout' in message.lower():
                        error_data["error_messages"]["timeout_error"] += 1
                    elif 'file' in message.lower() or 'directory' in message.lower():
                        error_data["error_messages"]["file_error"] += 1
                    else:
                        error_data["error_messages"]["other_error"] += 1
                    
                    # Keep recent errors for detailed analysis
                    if len(error_data["recent_errors"]) < 10:
                        error_data["recent_errors"].append({
                            "timestamp": timestamp_str,
                            "level": level,
                            "message": message[:200]  # Truncate long messages
                        })
            
            # Convert defaultdicts to regular dicts
            error_data["error_levels"] = dict(error_data["error_levels"])
            error_data["error_messages"] = dict(error_data["error_messages"])
            
            return error_data
            
        except Exception as e:
            print(f"[ERROR] Failed to parse error logs: {e}")
            return {"error": str(e)}
