import os
import json
import httpx
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class NotificationService:
    """Service to handle system notifications and external alerts."""
    
    def __init__(self):
        self.notifications_dir = Path("data/notifications")
        self.notifications_dir.mkdir(parents=True, exist_ok=True)
        self.notifications_file = self.notifications_dir / "notifications.json"
        self.critical_file = self.notifications_dir / "critical_notifications.json"
        
        # External Webhooks
        self.slack_url = os.getenv("SLACK_WEBHOOK_URL")
        self.discord_url = os.getenv("DISCORD_WEBHOOK_URL")

    def _save_notification(self, notification: Dict, is_critical: bool = False):
        """Save notification to local JSON file."""
        target_file = self.critical_file if is_critical else self.notifications_file
        
        notifications = []
        if target_file.exists():
            try:
                with open(target_file, 'r') as f:
                    notifications = json.load(f)
            except Exception:
                notifications = []
        
        notifications.append(notification)
        
        # Keep last 500 notifications
        if len(notifications) > 500:
            notifications = notifications[-500:]
            
        try:
            with open(target_file, 'w') as f:
                json.dump(notifications, f, indent=2)
        except Exception as e:
            print(f"[NOTIFICATION] Error saving to {target_file}: {e}")

    async def _send_external(self, message: str, severity: str):
        """Send notification to external channels (Slack/Discord)."""
        # Prefix for external messages
        prefix = "🚨" if severity in ["critical", "high"] else "ℹ️"
        formatted_message = f"{prefix} *AI Engine Alert* ({severity.upper()}):\n{message}"
        
        # Slack
        if self.slack_url:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(self.slack_url, json={"text": formatted_message})
            except Exception as e:
                print(f"[NOTIFICATION] Slack error: {e}")
                
        # Discord
        if self.discord_url:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(self.discord_url, json={"content": formatted_message})
            except Exception as e:
                print(f"[NOTIFICATION] Discord error: {e}")

    async def notify(self, message: str, severity: str = "info", type: str = "general", data: Optional[Dict] = None):
        """Send a notification through all configured channels."""
        print(f"[NOTIFICATION] [{severity.upper()}] {message}")
        
        notification = {
            "type": type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        is_critical = severity in ["critical", "high"]
        
        # 1. Save locally
        self._save_notification(notification, is_critical)
        
        # 2. Send external
        await self._send_external(message, severity)
        
        return notification

    def get_notifications(self, limit: int = 50, critical_only: bool = False, include_critical: bool = True) -> List[Dict]:
        """Fetch recent notifications."""
        if critical_only:
            target_files = [self.critical_file]
        elif include_critical:
            target_files = [self.notifications_file, self.critical_file]
        else:
            target_files = [self.notifications_file]
        
        all_notifs = []
        for target_file in target_files:
            if target_file.exists():
                try:
                    with open(target_file, 'r') as f:
                        all_notifs.extend(json.load(f))
                except Exception:
                    continue
        
        # Sort by timestamp
        all_notifs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return all_notifs[:limit]
        
    def clear_notifications(self, index: Optional[int] = None, critical_only: bool = False):
        """Clear all or a specific notification."""
        target_file = self.critical_file if critical_only else self.notifications_file
        
        if not target_file.exists():
            return
            
        try:
            if index is None:
                # Clear all
                with open(target_file, 'w') as f:
                    json.dump([], f, indent=2)
                print(f"[NOTIFICATION] Cleared all {'critical ' if critical_only else ''}\
notifications")
            else:
                # Clear specific index
                with open(target_file, 'r') as f:
                    notifications = json.load(f)
                
                # Notifications are stored chronologically, UI shows reversed. 
                # Index from UI needs to be mapped or we use notification IDs.
                # Let's use reverse index for simplicity if passed from UI reversed list,
                # or just filter by timestamp/id if we had unique IDs.
                # For now, let's assume index is from the chronological list.
                if 0 <= index < len(notifications):
                    removed = notifications.pop(index)
                    with open(target_file, 'w') as f:
                        json.dump(notifications, f, indent=2)
                    print(f"[NOTIFICATION] Cleared notification at index {index}")
        except Exception as e:
            print(f"[NOTIFICATION] Error clearing notifications: {e}")

    def clear_by_item(self, timestamp: str):
        """Clear a specific notification by its timestamp."""
        for target_file in [self.notifications_file, self.critical_file]:
            if not target_file.exists():
                continue
            try:
                with open(target_file, 'r') as f:
                    notifications = json.load(f)
                
                new_notifs = [n for n in notifications if n.get('timestamp') != timestamp]
                
                if len(new_notifs) < len(notifications):
                    with open(target_file, 'w') as f:
                        json.dump(new_notifs, f, indent=2)
                    print(f"[NOTIFICATION] Item cleared from {target_file}")
                    return True
            except Exception as e:
                print(f"[NOTIFICATION] Error clearing item: {e}")
        return False

# Singleton instance
notification_service = NotificationService()
