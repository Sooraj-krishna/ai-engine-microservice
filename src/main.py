from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
import time
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import traceback

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Debug: Print loaded environment variables (remove in production)
print(f"[DEBUG] Loading environment variables...")
print(f"[DEBUG] WEBSITE_URL: {os.getenv('WEBSITE_URL')}")
print(f"[DEBUG] GITHUB_REPO: {os.getenv('GITHUB_REPO')}")
print(f"[DEBUG] MONITORING_MODE: {os.getenv('MONITORING_MODE')}")

# Import modules after environment variables are loaded
try:
    from monitor_ga_logs import collect_site_data
except ImportError:
    print("[WARNING] monitor_ga_logs not found, trying fallback...")
    try:
        from monitor import collect_site_data
    except ImportError:
        print("[ERROR] No monitoring module found!")
        def collect_site_data():
            return {"error": "No monitoring module available"}

from github_handler import get_all_repo_files, submit_fix_pr
from analyzer import analyze_data
from generator import prepare_fixes
from rollback_manager import RollbackManager
from validator import CodeValidator

app = FastAPI(
    title="AI Engine Microservice",
    description="Self-maintaining SaaS AI Engine with Google Analytics, Log Monitoring, Validation, and Rollback Protection",
    version="2.0.0"
)

# Global state for monitoring
health_status = {
    "status": "healthy",
    "last_check": datetime.now().isoformat(),
    "last_run": None,
    "last_pr": None,
    "last_error": None,
    "last_rollback": None,
    "version": "2.0.0",
    "environment": os.getenv("ENVIRONMENT", "development"),
    "website_url": os.getenv("WEBSITE_URL"),
    "monitoring_mode": os.getenv("MONITORING_MODE", "simple"),
    "safety_features": {
        "validation_enabled": True,
        "rollback_enabled": True,
        "safe_mode_only": True
    }
}

# Initialize safety components
rollback_manager = RollbackManager()
code_validator = CodeValidator()

@app.get("/")
def root():
    """Main status endpoint for load balancer health checks."""
    return {
        "status": "AI Engine running", 
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0 - Enhanced Safety Edition",
        "website_monitored": os.getenv("WEBSITE_URL"),
        "monitoring_mode": os.getenv("MONITORING_MODE", "simple"),
        "safety_features": health_status["safety_features"]
    }

@app.get("/health")
def health_check():
    """Comprehensive health check endpoint with safety system status."""
    try:
        print("[INFO] Running comprehensive health check...")
        
        # Test external dependencies
        test_results = {
            "environment_variables": test_environment_variables(),
            "github_api": test_github_connection(),
            "ai_api": test_ai_api_connection(),
            "website_api": test_website_connection(),
            "google_analytics": test_google_analytics_connection(),
            "validation_system": test_validation_system(),
            "rollback_system": test_rollback_system()
        }
        
        all_healthy = all(test_results.values())
        
        health_status.update({
            "status": "healthy" if all_healthy else "degraded",
            "last_check": datetime.now().isoformat(),
            "dependencies": test_results
        })
        
        print(f"[INFO] Health check completed: {health_status['status']}")
        return health_status
        
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/run")
def run_engine(background_tasks: BackgroundTasks):
    """Trigger AI maintenance cycle with full safety protection."""
    print("[INFO] AI maintenance cycle requested with safety protection")
    background_tasks.add_task(start_enhanced_maintenance_cycle)
    health_status["last_run"] = datetime.now().isoformat()
    return {
        "message": "Enhanced AI maintenance cycle started", 
        "timestamp": health_status["last_run"],
        "website": os.getenv("WEBSITE_URL"),
        "monitoring_mode": os.getenv("MONITORING_MODE", "simple"),
        "safety_features": health_status["safety_features"]
    }

@app.get("/status")
def get_detailed_status():
    """Get detailed status including validation and rollback history."""
    try:
        validation_report = code_validator.get_validation_report()
        rollback_history = rollback_manager.get_rollback_history()
        
        return {
            "health": health_status,
            "environment": {
                "website_url": os.getenv("WEBSITE_URL"),
                "github_repo": os.getenv("GITHUB_REPO"),
                "monitoring_mode": os.getenv("MONITORING_MODE"),
                "has_github_token": bool(os.getenv("GITHUB_TOKEN")),
                "has_gemini_token": bool(os.getenv("GEMINI_API_KEY")),
                "has_ga_credentials": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
            },
            "safety_systems": {
                "validation": validation_report,
                "rollback": rollback_history
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Status check failed: {str(e)}"}
        )

@app.post("/receive-frontend-data")
def receive_frontend_monitoring_data(data: dict):
    """Endpoint for receiving frontend monitoring data from your website."""
    print(f"[INFO] Received frontend monitoring data from: {data.get('url', 'unknown')}")
    return {"status": "received", "timestamp": datetime.now().isoformat()}

@app.post("/manual-rollback")
def manual_rollback(background_tasks: BackgroundTasks):
    """Manually trigger rollback of recent AI changes."""
    print("[INFO] Manual rollback requested")
    background_tasks.add_task(perform_manual_rollback)
    return {"message": "Manual rollback initiated", "timestamp": datetime.now().isoformat()}

def perform_manual_rollback():
    """Perform manual rollback of recent changes."""
    try:
        pr_url = rollback_manager.create_rollback_pr("Manual rollback requested by administrator", "manual")
        if pr_url:
            health_status["last_rollback"] = datetime.now().isoformat()
            print(f"[SUCCESS] Manual rollback PR created: {pr_url}")
        else:
            print("[ERROR] Manual rollback failed")
    except Exception as e:
        print(f"[ERROR] Manual rollback exception: {e}")

def start_enhanced_maintenance_cycle():
    """
    Enhanced maintenance cycle with comprehensive safety features:
    - Pre-change rollback checks
    - Validation of all generated code
    - Post-change monitoring
    - Automatic rollback protection
    """
    try:
        print(f"[INFO] ==========================================")
        print(f"[INFO] Starting ENHANCED maintenance cycle at {datetime.now()}")
        print(f"[INFO] Website: {os.getenv('WEBSITE_URL')}")
        print(f"[INFO] Monitoring Mode: {os.getenv('MONITORING_MODE', 'simple')}")
        print(f"[INFO] Safety Features: Validation + Rollback Protection")
        print(f"[INFO] ==========================================")
        
        # PHASE 1: PRE-CHANGE SAFETY CHECKS
        print("[INFO] Phase 1: Pre-change safety checks...")
        
        # Step 1: Collect site data
        print("[INFO] Step 1: Collecting comprehensive site data...")
        site_data = collect_site_data()
        
        if not site_data or "error" in str(site_data):
            print(f"[WARNING] Site data collection issues: {site_data}")
        else:
            print(f"[SUCCESS] Site data collected from sources: {site_data.get('data_sources', ['unknown'])}")
        
        # Step 2: Check if rollback is needed BEFORE making new changes
        print("[INFO] Step 2: Checking if rollback is needed...")
        rollback_result = rollback_manager.perform_rollback_if_needed(site_data)
        
        if rollback_result.get("rollback_performed"):
            print(f"[ROLLBACK] Automatic rollback performed: {rollback_result.get('pr_url')}")
            health_status["last_rollback"] = datetime.now().isoformat()
            health_status["last_error"] = f"Auto-rollback: {rollback_result.get('reason')}"
            return  # Skip normal maintenance cycle
        else:
            print("[INFO] No rollback needed, proceeding with maintenance...")
        
        # PHASE 2: ANALYSIS AND CODE GENERATION
        print("[INFO] Phase 2: Analysis and safe code generation...")
        
        # Step 3: Get repository files
        print("[INFO] Step 3: Accessing repository files...")
        repo_files = get_all_repo_files()
        
        if not repo_files:
            print("[ERROR] Failed to access repository - check GitHub token and repo name")
            raise Exception("Failed to access repository")
        else:
            print(f"[SUCCESS] Repository accessed: {len(repo_files)} files found")
        
        # Step 4: Analyze issues (conservative approach)
        print("[INFO] Step 4: Analyzing data for safe improvement opportunities...")
        issues = analyze_data(site_data, repo_files)
        print(f"[INFO] Analysis complete: {len(issues)} safe issues detected")
        
        if issues:
            for i, issue in enumerate(issues, 1):
                print(f"[INFO] Issue {i}: {issue.get('type', 'unknown')} - {issue.get('description', 'no description')[:100]}...")
        
        # Step 5: Generate and validate fixes
        if issues:
            print("[INFO] Step 5: Generating and validating code fixes...")
            print(f"[INFO] All fixes will be validated for safety before application...")
            
            # This calls prepare_fixes which now includes validation
            fixes = prepare_fixes(issues)
            
            if fixes:
                print(f"[SUCCESS] Generated and validated {len(fixes)} safe code fixes")
                
                # PHASE 3: SAFE APPLICATION OF CHANGES
                print("[INFO] Phase 3: Safely applying validated changes...")
                
                # Step 6: Submit PR with validated fixes
                print("[INFO] Step 6: Creating pull request with validated fixes...")
                pr_url = submit_fix_pr(fixes)
                
                if pr_url:
                    print(f"[SUCCESS] Created PR: {pr_url}")
                    health_status["last_pr"] = pr_url
                    health_status["last_error"] = None  # Clear previous errors
                    
                    # Record change for potential future rollback
                    change_id = rollback_manager.record_change(
                        pr_url=pr_url,
                        notes=f"AI maintenance cycle - {len(fixes)} validated fixes applied"
                    )
                    print(f"[INFO] Change recorded for rollback protection: ID {change_id}")
                    
                else:
                    print("[WARNING] PR creation failed")
                    health_status["last_error"] = "PR creation failed"
            else:
                print("[INFO] No safe fixes could be generated/validated from detected issues")
        else:
            print("[INFO] No improvement opportunities detected - website appears to be running well!")
        
        print(f"[INFO] Enhanced maintenance cycle completed successfully at {datetime.now()}")
        print(f"[INFO] ==========================================")
        
        # Save validation log for audit
        code_validator.save_validation_log()
        
    except Exception as e:
        error_msg = f"Enhanced maintenance cycle failed: {str(e)}"
        print(f"[ERROR] {error_msg}")
        health_status["last_error"] = str(e)
        
        # Log the full error for debugging
        print(f"[DEBUG] Full error traceback:")
        print(traceback.format_exc())
        
        # In case of critical errors, consider emergency rollback
        if "critical" in str(e).lower():
            try:
                print("[EMERGENCY] Attempting emergency rollback due to critical error...")
                emergency_rollback = rollback_manager.create_rollback_pr(
                    f"Emergency rollback due to critical error: {str(e)}", 
                    "critical"
                )
                if emergency_rollback:
                    health_status["last_rollback"] = datetime.now().isoformat()
                    print(f"[EMERGENCY] Emergency rollback created: {emergency_rollback}")
            except Exception as rollback_error:
                print(f"[EMERGENCY] Emergency rollback also failed: {rollback_error}")

# Enhanced helper functions for health checks
def test_environment_variables():
    """Test if critical environment variables are loaded."""
    try:
        required_vars = ['WEBSITE_URL', 'GITHUB_TOKEN', 'GITHUB_REPO', 'GEMINI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value or value == 'None':
                missing_vars.append(var)
        
        if missing_vars:
            print(f"[WARNING] Missing environment variables: {missing_vars}")
            return False
        
        print("[SUCCESS] All required environment variables loaded")
        return True
        
    except Exception as e:
        print(f"[ERROR] Environment variable test failed: {e}")
        return False

def test_github_connection():
    """Test GitHub API connectivity."""
    try:
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPO")
        
        if not token or token == 'None':
            print("[WARNING] GitHub token not configured")
            return False
        
        if not repo or repo == 'None':
            print("[WARNING] GitHub repository not configured")
            return False
        
        headers = {"Authorization": f"token {token}"}
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("[SUCCESS] GitHub API connection successful")
            return True
        else:
            print(f"[ERROR] GitHub API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] GitHub connection test failed: {e}")
        return False

def test_ai_api_connection():
    """Test Google Gemini API connectivity."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key or api_key == 'None':
            print("[WARNING] Gemini API key not configured")
            return False
        
        # Test basic Gemini API connectivity
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content('Hello')
        
        if response and response.text:
            print("[SUCCESS] Gemini API connection successful")
            return True
        else:
            print("[ERROR] Gemini API returned empty response")
            return False
            
    except Exception as e:
        print(f"[ERROR] Gemini API test failed: {e}")
        return False

def test_website_connection():
    """Test main website connectivity."""
    try:
        website_url = os.getenv("WEBSITE_URL")
        
        if not website_url or website_url == 'None':
            print("[ERROR] Website URL not configured")
            return False
        
        response = requests.get(website_url, timeout=15)
        
        if response.status_code == 200:
            print(f"[SUCCESS] Website {website_url} is accessible")
            return True
        else:
            print(f"[WARNING] Website returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Website connection test failed: {e}")
        return False

def test_google_analytics_connection():
    """Test Google Analytics connectivity."""
    try:
        ga_property_id = os.getenv("GA4_PROPERTY_ID")
        ga_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if not ga_property_id:
            print("[INFO] Google Analytics not configured (optional)")
            return True
        
        if not ga_credentials or not os.path.exists(ga_credentials):
            print("[WARNING] Google Analytics credentials file not found")
            return False
        
        print("[SUCCESS] Google Analytics configuration appears valid")
        return True
        
    except Exception as e:
        print(f"[ERROR] Google Analytics test failed: {e}")
        return False

def test_validation_system():
    """Test the code validation system."""
    try:
        # Test validator with a simple safe fix
        test_fix = {
            "path": "utils/ai-test-validation.js",
            "content": "// AI-Generated test\n// SAFE TO USE\nexport default class TestHelper {}",
            "description": "Test validation"
        }
        
        is_safe, warnings, errors = code_validator.validate_fix(test_fix)
        
        if is_safe:
            print("[SUCCESS] Validation system working correctly")
            return True
        else:
            print(f"[WARNING] Validation system issues: {errors}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Validation system test failed: {e}")
        return False

def test_rollback_system():
    """Test the rollback management system."""
    try:
        # Test rollback system initialization
        test_data = {
            "system": {"memory_percent": 85, "cpu_percent": 70},
            "metrics": {"combined": {"overall_health_score": 80}},
            "errors": {}
        }
        
        should_rollback, reason, severity = rollback_manager.should_rollback(test_data)
        
        print(f"[SUCCESS] Rollback system working - Decision: {should_rollback}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Rollback system test failed: {e}")
        return False

if __name__ == "__main__":
    print("[INFO] Starting Enhanced AI Engine Microservice with Safety Features...")
    print(f"[INFO] Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"[INFO] Website: {os.getenv('WEBSITE_URL', 'Not configured')}")
    print(f"[INFO] Monitoring Mode: {os.getenv('MONITORING_MODE', 'simple')}")
    print(f"[INFO] Safety Features: Validation ✅ | Rollback Protection ✅")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
