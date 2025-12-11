"""
Google Analytics Data API client for collecting website analytics data.
This module connects to GA4 to fetch real-time website performance metrics.
"""

import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from datetime import datetime, timedelta

class GoogleAnalyticsClient:
    """
    Client for fetching data from Google Analytics 4 API.
    Provides website traffic, user behavior, and performance metrics.
    """
    
    def __init__(self):
        """Initialize GA4 client with service account credentials."""
        self.property_id = os.getenv("GA4_PROPERTY_ID")
        self.client = BetaAnalyticsDataClient()
        
        if not self.property_id:
            raise ValueError("GA4_PROPERTY_ID environment variable is required")
    
    def get_website_analytics(self):
        """
        Fetch comprehensive website analytics data from GA4.
        Returns metrics for bounce rate, page views, user engagement, etc.
        """
        try:
            # Get data for the last 24 hours
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Request basic website metrics
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[
                    Dimension(name="pagePath"),      # Which pages users visit
                    Dimension(name="deviceCategory"), # Desktop/Mobile/Tablet
                ],
                metrics=[
                    Metric(name="activeUsers"),
                    Metric(name="bounceRate"),
                    Metric(name="averageSessionDuration"),
                    Metric(name="screenPageViews"),      # Changed from "pageviews"
                    Metric(name="sessions"),
                ],
                date_ranges=[DateRange(start_date=yesterday, end_date=today)],
            )
            
            response = self.client.run_report(request)
            
            # Process response into usable format
            analytics_data = {
                "total_users": 0,
                "total_pageviews": 0,
                "total_sessions": 0,
                "avg_bounce_rate": 0,
                "avg_session_duration": 0,
                "top_pages": [],
                "device_breakdown": {},
                "timestamp": datetime.now().isoformat()
            }
            
            total_bounce_rate = 0
            total_duration = 0
            row_count = 0
            
            for row in response.rows:
                # Extract dimensions
                page_path = row.dimension_values[0].value
                device_category = row.dimension_values[1].value
                
                # Extract metrics
                users = int(row.metric_values[0].value or 0)
                bounce_rate = float(row.metric_values[1].value or 0)
                session_duration = float(row.metric_values[2].value or 0)
                pageviews = int(row.metric_values[3].value or 0)
                sessions = int(row.metric_values[4].value or 0)
                
                # Aggregate data
                analytics_data["total_users"] += users
                analytics_data["total_pageviews"] += pageviews
                analytics_data["total_sessions"] += sessions
                
                total_bounce_rate += bounce_rate
                total_duration += session_duration
                row_count += 1
                
                # Track top pages
                analytics_data["top_pages"].append({
                    "page": page_path,
                    "pageviews": pageviews,
                    "users": users
                })
                
                # Device breakdown
                if device_category not in analytics_data["device_breakdown"]:
                    analytics_data["device_breakdown"][device_category] = 0
                analytics_data["device_breakdown"][device_category] += users
            
            # Calculate averages
            if row_count > 0:
                analytics_data["avg_bounce_rate"] = total_bounce_rate / row_count
                analytics_data["avg_session_duration"] = total_duration / row_count
            
            # Sort top pages by pageviews
            analytics_data["top_pages"] = sorted(
                analytics_data["top_pages"], 
                key=lambda x: x["pageviews"], 
                reverse=True
            )[:10]  # Top 10 pages
            
            return analytics_data
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch GA4 data: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def get_realtime_metrics(self):
        """
        Get real-time website metrics from GA4.
        Shows current active users and live activity.
        """
        try:
            # Real-time metrics use different API call
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[Dimension(name="country")],
                metrics=[Metric(name="activeUsers")],
                date_ranges=[DateRange(start_date="today", end_date="today")],
            )
            
            response = self.client.run_report(request)
            
            active_users = sum(int(row.metric_values[0].value or 0) for row in response.rows)
            
            return {
                "active_users_now": active_users,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch real-time GA4 data: {e}")
            return {"error": str(e)}
