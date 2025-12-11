import os
import requests

def collect_site_data():
    url = os.getenv("WEBSITE_URL")
    headers = {"x-api-key": os.getenv("INTERNAL_API_KEY")}
    # Get metrics, errors, analytics from site APIs
    try:
        metrics = requests.get(f"{url}/metrics", headers=headers).json()
        errors = requests.get(f"{url}/errors", headers=headers).json()
        analytics = requests.get(f"{url}/analytics", headers=headers).json()
    except Exception as e:
        metrics, errors, analytics = {}, {}, {}
        print(f"[ERROR] Data collection failed: {e}")
    return {"metrics": metrics, "errors": errors, "analytics": analytics}
