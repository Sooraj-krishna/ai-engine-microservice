import os
from dotenv import load_dotenv
from src.parsers.ga_client import GoogleAnalyticsClient

load_dotenv()

print("Testing Google Analytics connection...")
try:
    ga_client = GoogleAnalyticsClient()
    analytics_data = ga_client.get_website_analytics()
    
    if 'error' not in analytics_data:
        print("✅ Google Analytics connected successfully")
        print(f"   Total users: {analytics_data.get('total_users', 0)}")
        print(f"   Total pageviews: {analytics_data.get('total_pageviews', 0)}")
    else:
        print(f"❌ GA Error: {analytics_data['error']}")
        
except Exception as e:
    print(f"❌ Failed to connect to Google Analytics: {e}")
    print("   Make sure you have set up service account and GA4_PROPERTY_ID")
