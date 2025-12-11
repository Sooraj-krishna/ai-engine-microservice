"""
Combined monitoring module that integrates Google Analytics and log file data.
This is the main monitoring interface that collects data from multiple sources.
"""

import os
import psutil
from datetime import datetime
from parsers.ga_client import GoogleAnalyticsClient
from parsers.nginx_parser import NginxLogParser
from parsers.apache_parser import ApacheLogParser

class CombinedMonitor:
    """
    Main monitoring class that combines Google Analytics data with server log analysis.
    Provides comprehensive website performance metrics from multiple data sources.
    """
    
    def __init__(self):
        """Initialize monitoring clients and parsers."""
        self.monitoring_mode = os.getenv("MONITORING_MODE", "ga_logs")
        
        # Initialize Google Analytics client
        try:
            self.ga_client = GoogleAnalyticsClient()
            self.ga_enabled = True
        except Exception as e:
            print(f"[WARNING] Google Analytics not available: {e}")
            self.ga_enabled = False
        
        # Initialize log parsers
        self.nginx_parser = NginxLogParser()
        self.apache_parser = ApacheLogParser()
        
        # Get log file paths from environment
        self.access_log_path = os.getenv("ACCESS_LOG_PATH")
        self.error_log_path = os.getenv("ERROR_LOG_PATH")
        self.app_log_path = os.getenv("APP_LOG_PATH")
        
    def collect_site_data(self):
        """
        Main data collection method that combines multiple monitoring sources.
        Returns comprehensive monitoring data for AI analysis.
        """
        print(f"[INFO] Starting data collection at {datetime.now()}")
        
        monitoring_data = {
            "timestamp": datetime.now().isoformat(),
            "data_sources": [],
            "metrics": {},
            "analytics": {},
            "errors": {},
            "system": {}
        }
        
        # 1. Collect Google Analytics data
        if self.ga_enabled:
            try:
                print("[INFO] Collecting Google Analytics data...")
                ga_data = self.ga_client.get_website_analytics()
                realtime_data = self.ga_client.get_realtime_metrics()
                
                monitoring_data["analytics"] = {
                    **ga_data,
                    **realtime_data
                }
                monitoring_data["data_sources"].append("google_analytics")
                print(f"[SUCCESS] GA data collected: {ga_data.get('total_users', 0)} users")
                
            except Exception as e:
                print(f"[ERROR] Failed to collect GA data: {e}")
                monitoring_data["analytics"]["ga_error"] = str(e)
        
        # 2. Collect server log data
        log_data = self.collect_log_data()
        monitoring_data["metrics"].update(log_data.get("metrics", {}))
        monitoring_data["errors"].update(log_data.get("errors", {}))
        monitoring_data["data_sources"].extend(log_data.get("sources", []))
        
        # 3. Collect system metrics
        system_data = self.collect_system_metrics()
        monitoring_data["system"] = system_data
        monitoring_data["data_sources"].append("system_metrics")
        
        # 4. Calculate combined metrics
        combined_metrics = self.calculate_combined_metrics(monitoring_data)
        monitoring_data["metrics"]["combined"] = combined_metrics
        
        print(f"[SUCCESS] Data collection completed from sources: {monitoring_data['data_sources']}")
        return monitoring_data
    
    def collect_log_data(self):
        """
        Collect and parse data from various log files.
        Handles both Nginx and Apache log formats automatically.
        """
        log_data = {
            "metrics": {},
            "errors": {},
            "sources": []
        }
        
        # Parse access logs (try Nginx first, then Apache)
        if self.access_log_path and os.path.exists(self.access_log_path):
            try:
                print(f"[INFO] Parsing access logs: {self.access_log_path}")
                
                # Detect log format by trying Nginx parser first
                access_metrics = self.nginx_parser.parse_access_logs(self.access_log_path)
                
                if "error" in access_metrics:
                    # Try Apache parser if Nginx fails
                    access_metrics = self.apache_parser.parse_access_logs(self.access_log_path)
                
                if "error" not in access_metrics:
                    log_data["metrics"]["access_logs"] = access_metrics
                    log_data["sources"].append("access_logs")
                    print(f"[SUCCESS] Parsed {access_metrics.get('total_requests', 0)} access log entries")
                
            except Exception as e:
                print(f"[ERROR] Failed to parse access logs: {e}")
                log_data["errors"]["access_logs"] = str(e)
        
        # Parse error logs
        if self.error_log_path and os.path.exists(self.error_log_path):
            try:
                print(f"[INFO] Parsing error logs: {self.error_log_path}")
                
                error_metrics = self.nginx_parser.parse_error_logs(self.error_log_path)
                
                if "error" not in error_metrics:
                    log_data["errors"]["server_errors"] = error_metrics
                    log_data["sources"].append("error_logs")
                    print(f"[SUCCESS] Parsed {error_metrics.get('total_errors', 0)} error log entries")
                
            except Exception as e:
                print(f"[ERROR] Failed to parse error logs: {e}")
                log_data["errors"]["error_logs"] = str(e)
        
        # Parse application logs (if available)
        if self.app_log_path and os.path.exists(self.app_log_path):
            try:
                print(f"[INFO] Parsing application logs: {self.app_log_path}")
                app_metrics = self.parse_application_logs(self.app_log_path)
                log_data["metrics"]["application_logs"] = app_metrics
                log_data["sources"].append("application_logs")
                
            except Exception as e:
                print(f"[ERROR] Failed to parse application logs: {e}")
                log_data["errors"]["application_logs"] = str(e)
        
        return log_data
    
    def collect_system_metrics(self):
        """
        Collect system-level performance metrics using psutil.
        Provides CPU, memory, disk, and network usage data.
        """
        try:
            system_metrics = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "network_io": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv
                },
                "process_count": len(psutil.pids()),
                "boot_time": psutil.boot_time(),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"[SUCCESS] System metrics: CPU {system_metrics['cpu_percent']}%, Memory {system_metrics['memory_percent']}%")
            return system_metrics
            
        except Exception as e:
            print(f"[ERROR] Failed to collect system metrics: {e}")
            return {"error": str(e)}
    
    def parse_application_logs(self, log_path):
        """
        Parse custom application logs for app-specific metrics.
        This can be customized based on your application's log format.
        """
        # Simple example - customize based on your app's log format
        app_metrics = {
            "total_entries": 0,
            "error_count": 0,
            "warning_count": 0,
            "info_count": 0
        }
        
        try:
            with open(log_path, 'r') as f:
                for line in f:
                    app_metrics["total_entries"] += 1
                    
                    line_lower = line.lower()
                    if 'error' in line_lower:
                        app_metrics["error_count"] += 1
                    elif 'warning' in line_lower:
                        app_metrics["warning_count"] += 1
                    elif 'info' in line_lower:
                        app_metrics["info_count"] += 1
            
            return app_metrics
            
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_combined_metrics(self, monitoring_data):
        """
        Calculate combined metrics from multiple data sources.
        Creates unified metrics for AI analysis.
        """
        combined = {
            "overall_health_score": 100,  # Start with perfect score
            "performance_issues": [],
            "user_experience_score": 100,
            "error_rate": 0
        }
        
        # Factor in Google Analytics data
        analytics = monitoring_data.get("analytics", {})
        if analytics.get("avg_bounce_rate"):
            bounce_rate = analytics["avg_bounce_rate"]
            if bounce_rate > 0.7:  # High bounce rate
                combined["user_experience_score"] -= 20
                combined["performance_issues"].append("high_bounce_rate")
        
        # Factor in server log data
        access_logs = monitoring_data.get("metrics", {}).get("access_logs", {})
        if access_logs.get("avg_response_time"):
            response_time = access_logs["avg_response_time"]
            if response_time > 2.0:  # Slow response
                combined["overall_health_score"] -= 15
                combined["performance_issues"].append("slow_response_time")
        
        # Factor in error rates
        server_errors = monitoring_data.get("errors", {}).get("server_errors", {})
        if server_errors.get("total_errors"):
            error_count = server_errors["total_errors"]
            total_requests = access_logs.get("total_requests", 1)
            combined["error_rate"] = error_count / total_requests
            
            if combined["error_rate"] > 0.05:  # >5% error rate
                combined["overall_health_score"] -= 25
                combined["performance_issues"].append("high_error_rate")
        
        # Factor in system metrics
        system = monitoring_data.get("system", {})
        if system.get("cpu_percent", 0) > 80:
            combined["overall_health_score"] -= 10
            combined["performance_issues"].append("high_cpu_usage")
        
        if system.get("memory_percent", 0) > 85:
            combined["overall_health_score"] -= 10
            combined["performance_issues"].append("high_memory_usage")
        
        return combined

# Main function used by the AI engine
def collect_site_data():
    """
    Main function called by the AI engine to collect monitoring data.
    This is the interface function that the rest of the AI engine uses.
    """
    monitor = CombinedMonitor()
    return monitor.collect_site_data()
