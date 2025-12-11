import requests
import os
from datetime import datetime, timedelta
import json

class DeploymentMonitor:
    """Monitor deployment health and trigger rollbacks if needed."""
    
    def __init__(self):
        self.alert_webhook = os.getenv("ALERT_WEBHOOK_URL")
        self.rollback_threshold = 5  # Number of failures before rollback
        
    def monitor_deployment(self, deployment_url):
        """Monitor deployment and check for issues."""
        try:
            # Health checks
            health_response = requests.get(f"{deployment_url}/health", timeout=30)
            
            if health_response.status_code != 200:
                self.alert_deployment_issue("Health check failed", health_response.status_code)
                return False
                
            # Performance checks
            start_time = datetime.now()
            app_response = requests.get(f"{deployment_url}/", timeout=30)
            response_time = (datetime.now() - start_time).total_seconds()
            
            if response_time > 5.0:  # 5 second threshold
                self.alert_deployment_issue("Slow response time", response_time)
                
            # Check error rates
            error_rate = self.check_error_rate(deployment_url)
            if error_rate > 0.1:  # 10% error rate threshold
                self.alert_deployment_issue("High error rate", error_rate)
                return False
                
            return True
            
        except Exception as e:
            self.alert_deployment_issue("Deployment monitoring failed", str(e))
            return False
    
    def check_error_rate(self, deployment_url):
        """Check application error rate."""
        # Implement error rate checking logic
        return 0.0
    
    def alert_deployment_issue(self, issue, details):
        """Send alert about deployment issues."""
        if self.alert_webhook:
            alert_data = {
                "issue": issue,
                "details": details,
                "timestamp": datetime.now().isoformat(),
                "deployment": "ai-engine"
            }
            try:
                requests.post(self.alert_webhook, json=alert_data)
            except Exception as e:
                print(f"Failed to send alert: {e}")
        
        print(f"[ALERT] {issue}: {details}")
    
    def trigger_rollback(self):
        """Trigger automatic rollback if issues persist."""
        print("[ROLLBACK] Triggering automatic rollback...")
        # Implement rollback logic here
        # This could call your deployment platform's API to rollback
