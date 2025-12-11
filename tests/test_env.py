import os
from dotenv import load_dotenv

load_dotenv()

# Test required environment variables
required_vars = [
    'GITHUB_TOKEN',
    'GITHUB_REPO', 
    'HF_API_TOKEN',
    'GA4_PROPERTY_ID'
]

print("Environment Variables Test:")
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Show first 10 chars for security
        masked_value = value[:10] + '...' if len(value) > 10 else value
        print(f"✅ {var}: {masked_value}")
    else:
        print(f"❌ {var}: Not set")
