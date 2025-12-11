import os
from dotenv import load_dotenv
from src.parsers.nginx_parser import NginxLogParser

load_dotenv()

print("Testing log file parsing...")

# Test if log files exist
access_log_path = os.getenv("ACCESS_LOG_PATH", "/var/log/nginx/access.log")
error_log_path = os.getenv("ERROR_LOG_PATH", "/var/log/nginx/error.log")

print(f"Access log path: {access_log_path}")
print(f"Error log path: {error_log_path}")

# Test parsing
parser = NginxLogParser()

if os.path.exists(access_log_path):
    print("✅ Access log file found")
    try:
        metrics = parser.parse_access_logs(access_log_path, hours_back=1)
        print(f"   Parsed {metrics.get('total_requests', 0)} requests")
    except Exception as e:
        print(f"❌ Error parsing access logs: {e}")
else:
    print("⚠️  Access log file not found - will use sample data")

if os.path.exists(error_log_path):
    print("✅ Error log file found")
    try:
        errors = parser.parse_error_logs(error_log_path, hours_back=1)
        print(f"   Found {errors.get('total_errors', 0)} errors")
    except Exception as e:
        print(f"❌ Error parsing error logs: {e}")
else:
    print("⚠️  Error log file not found - will use sample data")
