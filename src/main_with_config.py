from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import time
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import traceback
import asyncio

# Load environment variables from .env file in parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Debug: Verify critical environment variables are loaded
print(f"[DEBUG] .env file path: {env_path}")
print(f"[DEBUG] .env file exists: {env_path.exists()}")
print(f"[DEBUG] COMPETITOR_URLS loaded: {bool(os.getenv('COMPETITOR_URLS'))}")

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

from github_handler import get_all_repo_files, submit_fix_pr, clone_or_pull_repo
from analyzer import analyze_data
from generator import prepare_fixes
from notification_service import notification_service
from rollback_manager import rollback_manager
from validator import CodeValidator
from configure_endpoint import router as config_router
from log_streamer import log_streamer, QueueLogStream
from log_summary import log_summarizer
from model_router import _query_gemini_api
from feature_implementation_manager import feature_implementation_manager
from chatbot_manager import chatbot_manager
from chatbot_executor import chatbot_executor
from chat_storage import chat_storage
from pydantic import BaseModel
from typing import List, Dict, Optional
import contextlib
import sys
from celery_app import celery_app
from tasks import task_maintenance_cycle, task_manual_rollback, task_analyze_competitors

# In-memory history for task tracking
task_history = []
MAX_TASK_HISTORY = 20

def track_task(task_id, task_name):
    """Add a task to the history tracking."""
    global task_history
    task_history.insert(0, {
        "id": task_id,
        "name": task_name,
        "timestamp": datetime.now().isoformat()
    })
    # Trim history
    if len(task_history) > MAX_TASK_HISTORY:
        task_history = task_history[:MAX_TASK_HISTORY]

app = FastAPI(
    title="AI Engine Microservice",
    description="Self-maintaining SaaS AI Engine with Google Analytics, Log Monitoring, Validation, and Rollback Protection",
    version="2.0.0"
)

@app.on_event("startup")
async def startup_event():
    # Start the log broadcasting task
    asyncio.create_task(log_streamer.broadcast_logs())
    
    # Start the queue processor for background bug fixing
    from queue_processor import queue_processor
    queue_processor.start()
    print("[INFO] Queue processor started for automated bug fixes")

# Add CORS middleware for the web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include configuration router
app.include_router(config_router)
app.include_router(log_streamer.router)

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

detected_issues = []

# Initialize safety components
# rollback_manager = RollbackManager() # This line is removed as rollback_manager is now imported directly
code_validator = CodeValidator()

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

@app.get("/api")
def api_root():
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
        # Test environment variables
        env_test = test_environment_variables()
        
        # Test dependencies
        deps_test = test_dependencies()
        
        all_healthy = env_test["all_healthy"] and deps_test["all_healthy"]
        
        health_status.update({
            "status": "healthy" if all_healthy else "degraded",
            "last_check": datetime.now().isoformat(),
            "dependencies": deps_test
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

@app.get("/log-summary")
def log_summary():
    """Compact error/warning/info summary for AI consumption."""
    return log_summarizer.summary()

@app.post("/run")
def run_engine():
    """Trigger AI maintenance cycle via Celery worker."""
    print("[INFO] AI maintenance cycle requested via Celery")
    task = task_maintenance_cycle.delay()
    track_task(task.id, "Maintenance Cycle")
    health_status["last_run"] = datetime.now().isoformat()
    return {
        "message": "AI maintenance cycle task queued", 
        "task_id": task.id,
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
                "has_ai_api": bool(os.getenv("GEMINI_API_KEY")),
                "has_ga_credentials": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
                "use_improved_fixer": os.getenv("USE_IMPROVED_FIXER", "false").lower() == "true",
                "test_fixes_before_apply": os.getenv("TEST_FIXES_BEFORE_APPLY", "true").lower() == "true",
                "code_analysis_enabled": True  # Code analysis is always enabled when available
            },
            "safety_systems": {
                "validation": validation_report,
                "rollback": rollback_history
            },
            "issues": detected_issues,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Status check failed: {str(e)}"}
        )

class GeminiRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str = None
    timeoutMs: int = 60000

@app.post("/api/gemini")
async def gemini_api_endpoint(request: GeminiRequest):
    """Backend endpoint for Gemini API calls (used by frontend model router)."""
    try:
        result = _query_gemini_api(
            messages=request.messages,
            model=request.model,
            timeout=int(request.timeoutMs / 1000) if request.timeoutMs else 60
        )
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Gemini API error: {str(e)}"}
        )

@app.post("/receive-frontend-data")
def receive_frontend_monitoring_data(data: dict):
    """Endpoint for receiving frontend monitoring data from your website."""
    print(f"[INFO] Received frontend monitoring data from: {data.get('url', 'unknown')}")
    return {"status": "received", "timestamp": datetime.now().isoformat()}

@app.post("/manual-rollback")
def manual_rollback():
    """Manually trigger rollback of recent AI changes via Celery."""
    print("[INFO] Manual rollback requested via Celery")
    task = task_manual_rollback.delay()
    track_task(task.id, "Manual Rollback")
    return {
        "message": "Manual rollback task queued", 
        "task_id": task.id,
        "timestamp": datetime.now().isoformat()
    }

# ================== BUG QUEUE MONITORING ENDPOINTS ==================

@app.get("/auto-fixes")
def get_auto_fixes(limit: int = 100):
    """View all auto-fixed bugs from history."""
    try:
        from bug_queue_manager import bug_queue_manager
        history = bug_queue_manager.get_history(limit=limit)
        
        # Filter for completed items
        auto_fixes = [h for h in history if h.get("status") == "completed"]
        
        return JSONResponse(content={
            "total": len(auto_fixes),
            "auto_fixes": auto_fixes
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get auto-fixes: {str(e)}"}
        )

@app.get("/auto-fixes/daily-digest")
def get_daily_digest():
    """Get summary of today's auto-fixes."""
    try:
        from auto_approval_manager import auto_approval_manager
        stats = auto_approval_manager.get_daily_stats()
        
        return JSONResponse(content={
            "date": stats.get("date"),
            "summary": stats,
            "message": f"Today: {stats.get('auto_approved', 0)} auto-approved, {stats.get('requires_approval', 0)} require approval"
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get daily digest: {str(e)}"}
        )

@app.get("/bug-queue/status")
def get_bug_queue_status():
    """Get current queue status."""
    try:
        from bug_queue_manager import bug_queue_manager
        from queue_processor import queue_processor
        
        queue_status = bug_queue_manager.get_queue_status()
        processor_status = queue_processor.get_status()
        
        return JSONResponse(content={
            "queue": queue_status,
            "processor": processor_status,
            "healthy": processor_status.get("running", False)
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get queue status: {str(e)}"}
        )

@app.post("/bug-queue/pause")
def pause_bug_queue():
    """Emergency pause - stops all auto-approvals and queue processing."""
    try:
        from bug_queue_manager import bug_queue_manager
        from auto_approval_manager import auto_approval_manager
        
        bug_queue_manager.pause()
        auto_approval_manager.emergency_pause()
        
        return JSONResponse(content={
            "message": "⚠️ Queue processing and auto-approvals PAUSED",
            "status": "paused"
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to pause queue: {str(e)}"}
        )

@app.post("/bug-queue/resume")
def resume_bug_queue():
    """Resume queue processing and auto-approvals."""
    try:
        from bug_queue_manager import bug_queue_manager
        from auto_approval_manager import auto_approval_manager
        
        bug_queue_manager.resume()
        auto_approval_manager.resume()
        
        return JSONResponse(content={
            "message": "✅ Queue processing and auto-approvals RESUMED",
            "status": "active"
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to resume queue: {str(e)}"}
        )

@app.get("/auto-approval/config")
def get_auto_approval_config():
    """Get current auto-approval configuration."""
    try:
        from auto_approval_manager import auto_approval_manager
        config = auto_approval_manager.get_config()
        
        return JSONResponse(content=config)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get config: {str(e)}"}
        )

@app.put("/auto-approval/config")
def update_auto_approval_config(updates: dict):
    """
    Update auto-approval configuration.
    
    Example request body:
    {
        "auto_approve_severities": ["medium", "low"],
        "silent_severities": ["low"],
        "max_auto_approvals_per_day": 100
    }
    """
    try:
        from auto_approval_manager import auto_approval_manager
        updated_config = auto_approval_manager.update_config(updates)
        
        return JSONResponse(content={
            "message": "Configuration updated",
            "config": updated_config
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to update config: {str(e)}"}
        )

# ================== END BUG QUEUE MONITORING ==================

# ================== NOTIFICATION ENDPOINTS ==================

@app.get("/notifications")
def get_notifications(limit: int = 50):
    """Get recent notifications."""
    try:
        notifications = notification_service.get_notifications(limit=limit)
        return JSONResponse(content={
            "notifications": notifications,
            "total": len(notifications)
        })
    except Exception as e:
        print(f"[API] Error getting notifications: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get notifications: {str(e)}"}
        )

@app.delete("/notifications")
def clear_all_notifications():
    """Clear all notifications (both general and critical)."""
    try:
        notification_service.clear_notifications(critical_only=False)
        notification_service.clear_notifications(critical_only=True)
        return JSONResponse(content={"message": "All notifications cleared"})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to clear notifications: {str(e)}"}
        )

@app.delete("/notifications/item")
def clear_notification_item(timestamp: str):
    """Clear a specific notification item by timestamp."""
    try:
        success = notification_service.clear_by_item(timestamp)
        if success:
            return JSONResponse(content={"message": "Notification cleared"})
        else:
            return JSONResponse(status_code=404, content={"error": "Notification not found"})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to clear notification: {str(e)}"}
        )

# ================== BUG REVIEW ENDPOINTS ==================

@app.get("/bugs/pending")
def get_pending_bugs():
    """Get all detected bugs awaiting approval, grouped by severity."""
    try:
        from bug_queue_manager import bug_queue_manager
        
        detected_bugs = bug_queue_manager.get_detected_bugs()
        
        # Group bugs by severity
        bugs_by_severity = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for item in detected_bugs:
            severity = item.get("severity", "low")
            bugs_by_severity.setdefault(severity, []).append({
                "id": item["id"],
                "type": item["bug"].get("type"),
                "description": item["bug"].get("description"),
                "severity": severity,
                "target_file": item["bug"].get("target_file"),
                "detected_at": item.get("detected_at"),
                "framework": item["bug"].get("framework"),
                "language": item["bug"].get("language")
            })
        
        total = sum(len(bugs) for bugs in bugs_by_severity.values())
        
        return JSONResponse(content={
            "bugs_by_severity": bugs_by_severity,
            "total": total,
            "summary": {
                "critical": len(bugs_by_severity["critical"]),
                "high": len(bugs_by_severity["high"]),
                "medium": len(bugs_by_severity["medium"]),
                "low": len(bugs_by_severity["low"])
            }
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get pending bugs: {str(e)}"}
        )

@app.post("/bugs/{bug_id}/approve")
def approve_bug(bug_id: str):
    """Approve a detected bug for processing (max 3 queued at once)."""
    try:
        from bug_queue_manager import bug_queue_manager
        
        # Use new approve_bug_to_queue method (enforces 3-bug limit)
        result = bug_queue_manager.approve_bug_to_queue(bug_id)
        
        if not result.get("success"):
            error_msg = result.get("error", "Approval failed")
            print(f"[API] Approval failed for {bug_id}: {error_msg}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": error_msg,
                    "bug_id": bug_id
                }
            )
        
        print(f"[API] Bug {bug_id} approved ({result.get('queued_count')}/3 queued)")
        
        return JSONResponse(content={
            "message": "Bug approved and queued for processing",
            "bug_id": bug_id,
            "queued_count": result.get("queued_count"),
            "max_queued": 3
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to approve bug: {str(e)}"}
        )

@app.delete("/bugs/failed")
def clear_failed_bugs():
    """Clear all failed bugs from the queue."""
    try:
        from bug_queue_manager import bug_queue_manager
        import json
        from pathlib import Path
        
        queue_file = Path("data/bug_queue/bug_queue.json")
        if not queue_file.exists():
            return JSONResponse(content={"message": "No queue found", "cleared": 0})
        
        with open(queue_file, 'r') as f:
            queue = json.load(f)
        
        # Remove failed bugs
        original_count = len(queue)
        queue = [item for item in queue if item.get("status") != "failed"]
        cleared_count = original_count - len(queue)
        
        # Save updated queue
        with open(queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
        
        return JSONResponse(content={
            "message": f"Cleared {cleared_count} failed bugs",
            "cleared": cleared_count,
            "remaining": len(queue)
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to clear bugs: {str(e)}"}
        )

@app.post("/bugs/approve-batch")
def approve_bugs_by_severity(request: dict):
    """
    Bulk approve bugs by severity levels.
    
    Body: {"severities": ["critical", "high"]}
    """
    try:
        from bug_queue_manager import bug_queue_manager
        import json
        from pathlib import Path
        
        severities = request.get("severities", [])
        if not severities:
            return JSONResponse(
                status_code=400,
                content={"error": "No severities specified"}
            )
        
        queue_file = Path("data/bug_queue/bug_queue.json")
        if not queue_file.exists():
            return JSONResponse(status_code=404, content={"error": "Bug queue not found"})
        
        with open(queue_file, 'r') as f:
            queue = json.load(f)
        
        # Approve all bugs matching severities
        approved_count = 0
        for item in queue:
            if item["status"] == "queued" and item.get("severity") in severities:
                item["status"] = "approved"
                item["approved_at"] = datetime.now().isoformat()
                approved_count += 1
        
        # Save updated queue
        with open(queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
        
        return JSONResponse(content={
            "message": f"Approved {approved_count} bugs",
            "approved": approved_count,
            "severities": severities
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to approve bugs: {str(e)}"}
        )

# ================== END BUG REVIEW ENDPOINTS ==================

# ================== BUG PROGRESS TRACKING ENDPOINTS ==================

@app.get("/bugs/{bug_id}/progress")
def get_bug_progress(bug_id: str):
    """Get real-time progress for a specific bug."""
    try:
        from bug_queue_manager import bug_queue_manager
        
        progress = bug_queue_manager.get_progress(bug_id)
        
        if not progress:
            return JSONResponse(
                status_code=404,
                content={"error": "Bug not found"}
            )
        
        return JSONResponse(content=progress)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get progress: {str(e)}"}
        )

@app.get("/bugs/in-progress")
def get_in_progress_bugs():
    """Get all bugs currently being processed with their progress."""
    try:
        from bug_queue_manager import bug_queue_manager
        
        bugs = bug_queue_manager.get_in_progress_bugs()
        
        return JSONResponse(content={
            "bugs": bugs,
            "total": len(bugs)
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get in-progress bugs: {str(e)}"}
        )

# ================== END BUG PROGRESS TRACKING ENDPOINTS ==================

@app.get("/notifications/critical")
def get_critical_notifications():
    """Get pending critical notifications."""
    try:
        notifications = notification_service.get_notifications(limit=50, critical_only=True)
        return JSONResponse(content={
            "notifications": notifications,
            "total": len(notifications)
        })
    except Exception as e:
        print(f"[API] Error getting critical notifications: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get critical notifications: {str(e)}"}
        )

@app.post("/notifications/critical/{index}/approve")
def approve_critical_bug(index: int):
    """Approve and execute a critical bug fix."""
    try:
        from pathlib import Path
        import json
        
        critical_file = Path("data/notifications/critical_notifications.json")
        
        if not critical_file.exists():
            return JSONResponse(
                status_code=404,
                content={"error": "No critical notifications found"}
            )
        
        with open(critical_file, 'r') as f:
            critical_bugs = json.load(f)
        
        if index < 0 or index >= len(critical_bugs):
            return JSONResponse(
                status_code=404,
                content={"error": "Invalid notification index"}
            )
        
        bug_notification = critical_bugs[index]
        bug_notification["resolved"] = True
        bug_notification["approved_at"] = datetime.now().isoformat()
        
        # Save updated notifications
        with open(critical_file, 'w') as f:
            json.dump(critical_bugs, f, indent=2)
        
        # Queue for execution
        # TODO: Execute the approved plan
        
        return JSONResponse(content={
            "message": "Bug fix approved and queued for execution",
            "bug": bug_notification
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to approve bug: {str(e)}"}
        )

# ================== END NOTIFICATION ENDPOINTS ==================

# ================== SETTINGS ENDPOINTS ==================

@app.get("/settings/ai-classification")
def get_ai_classification_setting():
    """Get current AI classification setting."""
    try:
        import os
        from dotenv import load_dotenv, set_key, find_dotenv
        
        # Reload to get latest value
        load_dotenv(override=True)
        
        use_ai = os.getenv("USE_AI_CLASSIFICATION", "false").lower() == "true"
        
        return JSONResponse(content={
            "use_ai_classification": use_ai,
            "description": "When enabled, uses AI (Gemini) for bug classification. When disabled, uses rule-based classification to save API tokens."
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get setting: {str(e)}"}
        )

@app.put("/settings/ai-classification")
def update_ai_classification_setting(request: dict):
    """
    Update AI classification setting.
    
    Body: {"use_ai_classification": true/false}
    """
    try:
        import os
        from dotenv import set_key, find_dotenv
        from pathlib import Path
        
        use_ai = request.get("use_ai_classification", False)
        
        # Find .env file
        env_file = find_dotenv()
        if not env_file:
            # Try common locations
            possible_paths = [
                Path(__file__).parent.parent / ".env",
                Path(__file__).parent / ".env",
                Path.cwd() / ".env"
            ]
            for path in possible_paths:
                if path.exists():
                    env_file = str(path)
                    break
        
        if not env_file:
            return JSONResponse(
                status_code=500,
                content={"error": ".env file not found"}
            )
        
        # Update .env file
        set_key(env_file, "USE_AI_CLASSIFICATION", "true" if use_ai else "false")
        
        # Update in current environment
        os.environ["USE_AI_CLASSIFICATION"] = "true" if use_ai else "false"
        
        # Reload the bug_classifier module to pick up new setting
        import importlib
        import sys
        if 'bug_classifier' in sys.modules:
            importlib.reload(sys.modules['bug_classifier'])
        
        return JSONResponse(content={
            "success": True,
            "use_ai_classification": use_ai,
            "message": f"AI classification {'enabled' if use_ai else 'disabled'}. " + 
                      ("Using AI for bug severity detection." if use_ai else "Using rule-based classification to save API tokens.")
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to update setting: {str(e)}"}
        )

# ================== END SETTINGS ENDPOINTS ==================

# Competitive Analysis Endpoints
@app.post("/analyze-competitors")
async def analyze_competitors(competitor_urls: list[str] = None, depth: str = None, premium: bool = False, ultra: bool = False, professional: bool = False):
    """
    Trigger competitive analysis via Celery worker.
    """
    # Determine analysis mode
    if professional:
        print(f"[INFO] 🎯 PROFESSIONAL mode - Business features")
    elif premium:
        print(f"[INFO] ✨ COMPREHENSIVE mode")
    else:
        premium = True
        print(f"[INFO] 📊 STANDARD mode")
    
    # Get competitor URLs from request or environment
    if not competitor_urls:
        competitor_urls_str = os.getenv("COMPETITOR_URLS", "")
        competitor_urls = [url.strip() for url in competitor_urls_str.split(",") if url.strip()]
    
    if not competitor_urls:
        return JSONResponse(
            status_code=400,
            content={"error": "No competitor URLs provided."}
        )
    
    # Get depth from request or environment
    if not depth:
        depth = os.getenv("COMPETITIVE_ANALYSIS_DEPTH", "standard")
    
    own_site_url = os.getenv("WEBSITE_URL")
    if not own_site_url:
        return JSONResponse(status_code=400, content={"error": "WEBSITE_URL not configured"})

    print(f"[INFO] Queuing competitive analysis task...")
    task = task_analyze_competitors.delay(
        own_site_url, competitor_urls, depth, premium, ultra, professional
    )
    track_task(task.id, f"Competitive Analysis ({'Professional' if professional else 'Standard'})")
    
    return JSONResponse(content={
        "status": "queued",
        "task_id": task.id,
        "message": "Competitive analysis started in background"
    })

@app.get("/tasks")
async def list_recent_tasks():
    """List recent trackable tasks with their statuses."""
    from celery.result import AsyncResult
    results = []
    
    for task_info in task_history:
        res = AsyncResult(task_info["id"], app=celery_app)
        results.append({
            "id": task_info["id"],
            "name": task_info["name"],
            "timestamp": task_info["timestamp"],
            "status": res.status,
            "ready": res.ready()
        })
    
    return JSONResponse(content={"tasks": results})

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Check status of a Celery task."""
    from celery.result import AsyncResult
    res = AsyncResult(task_id, app=celery_app)
    
    return JSONResponse(content={
        "task_id": task_id,
        "status": res.status,
        "ready": res.ready(),
        "info": str(res.info) if not res.ready() else None
    })

@app.get("/tasks/{task_id}/result")
async def get_task_result(task_id: str):
    """Retrieve result of a completed Celery task."""
    from celery.result import AsyncResult
    res = AsyncResult(task_id, app=celery_app)
    
    if not res.ready():
        return JSONResponse(status_code=202, content={"status": res.status, "message": "Task not ready"})
    
    if res.failed():
        return JSONResponse(status_code=500, content={"status": "FAILED", "error": str(res.result)})
    
    # For competitive analysis, results are stored in a file
    result_data = res.result
    if isinstance(result_data, dict) and "result_file" in result_data:
        import json
        file_path = result_data["result_file"]
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                analysis_result = json.load(f)
            
            # Update global for backward compatibility with /feature-recommendations
            global competitive_analysis_results
            competitive_analysis_results = analysis_result
            
            return JSONResponse(content=analysis_result)
            
    return JSONResponse(content={"status": "completed", "result": res.result})

@app.get("/feature-recommendations")
async def get_feature_recommendations():
    """Get prioritized feature recommendations from last competitive analysis."""
    global competitive_analysis_results
    
    if not competitive_analysis_results:
        return JSONResponse(
            status_code=404,
            content={"error": "No competitive analysis results available. Run /analyze-competitors first"}
        )
    
    return JSONResponse(content={
        "analysis_date": competitive_analysis_results.get("analysis_date"),
        "feature_gaps": competitive_analysis_results.get("feature_gaps", []),
        "summary": competitive_analysis_results.get("summary", {})
    })

@app.post("/select-feature")
async def select_feature_to_implement(request: dict):
    """
    User selects which feature to implement next from competitive analysis.
    Uses chatbot workflow for consistent implementation with plan generation and approval.
    
    Request body:
        - feature_id: ID of the feature to select
        - user_id: (optional, default='default') User identifier for session
    """
    global competitive_analysis_results
    
    feature_id = request.get("feature_id")
    user_id = request.get("user_id", "default")
    
    if not feature_id:
        return JSONResponse(
            status_code=400,
            content={"error": "feature_id is required in request body"}
        )
    
    if not competitive_analysis_results:
        return JSONResponse(
            status_code=404,
            content={"error": "No competitive analysis results available"}
        )
    
    # Find the selected feature
    feature_gaps = competitive_analysis_results.get("feature_gaps", [])
    selected_feature = next((f for f in feature_gaps if f.get("id") == feature_id), None)
    
    if not selected_feature:
        return JSONResponse(
            status_code=404,
            content={"error": f"Feature {feature_id} not found"}
        )
    
    try:
        print(f"[FEATURE_SELECT] Feature selected: {selected_feature.get('name')}")
        print(f"[FEATURE_SELECT] Using chatbot workflow for implementation")
        
        # Create or get existing session for this user
        session = chatbot_manager.create_session(user_id)
        session_id = session["session_id"]
        
        # Construct natural language request for the feature
        feature_name = selected_feature.get("name", "Unknown Feature")
        description = selected_feature.get("description", "")
        implementation_notes = selected_feature.get("implementation_notes", "")
        complexity = selected_feature.get("complexity", "medium")
        business_impact = selected_feature.get("business_impact", "medium")
        
        # Create detailed feature request message
        feature_request = f"""Implement the feature: {feature_name}

Description: {description}

Implementation Notes: {implementation_notes}

Complexity: {complexity}
Business Impact: {business_impact}

This feature was identified through competitive analysis and is present in competitor sites. Please create an implementation plan."""
        
        print(f"[FEATURE_SELECT] Processing feature through chatbot...")
        
        # Process through chatbot workflow
        chatbot_response = await chatbot_manager.process_message(
            session_id,
            feature_request
        )
        
        print(f"[FEATURE_SELECT] Chatbot response generated")
        print(f"[FEATURE_SELECT] Has plan: {chatbot_response.get('plan') is not None}")
        print(f"[FEATURE_SELECT] Requires approval: {chatbot_response.get('requires_approval', False)}")
        
        # Return chatbot session and response
        return JSONResponse(content={
            "success": True,
            "session_id": session_id,
            "feature_id": feature_id,
            "feature_name": feature_name,
            "chatbot_response": chatbot_response,
            "message": f"Feature '{feature_name}' sent to chatbot for implementation planning"
        })
        
    except Exception as e:
        print(f"[ERROR] Failed to select feature: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to select feature: {str(e)}"}
        )

# Global variable to store competitive analysis results
competitive_analysis_results = None

# Additional Feature Implementation Endpoints

@app.get("/selected-features")
async def get_selected_features(status: str = None):
    """
    Get all features selected for implementation.
    
    Query params:
        - status: Filter by status (pending/in_progress/completed/cancelled)
    """
    try:
        features = feature_implementation_manager.get_selected_features(status_filter=status)
        return JSONResponse(content={
            "total": len(features),
            "features": features,
            "filtered_by": status if status else "all"
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get selected features: {str(e)}"}
        )

@app.put("/feature-status/{feature_id}")
async def update_feature_status(feature_id: str, request: dict):
    """
    Update the implementation status of a feature.
    
    Request body:
        - status: New status (pending/in_progress/completed/cancelled)
        - notes: (optional) Notes about the status change
    """
    new_status = request.get("status")
    notes = request.get("notes", "")
    
    if not new_status:
        return JSONResponse(
            status_code=400,
            content={"error": "status is required in request body"}
        )
    
    try:
        # CRITICAL: If status is changing to in_progress, execute the implementation!
        if new_status == "in_progress":
            print(f"[FEATURE_STATUS] Starting implementation execution for {feature_id}")
            
            # Update status first
            updated_feature = feature_implementation_manager.update_feature_status(
                feature_id, new_status, notes or "Implementation started"
            )
            
            # Execute the actual implementation
            execution_result = await feature_implementation_manager.execute_implementation(
                feature_id
            )
            
            return JSONResponse(content={
                "message": execution_result.get("message", "Implementation completed"),
                "feature": updated_feature,
                "execution_result": execution_result,
                "success": execution_result.get("success", False)
            })
        else:
            # For other status changes, just update status
            updated_feature = feature_implementation_manager.update_feature_status(
                feature_id, new_status, notes
            )
            return JSONResponse(content={
                "message": f"Feature status updated to '{new_status}'",
                "feature": updated_feature
            })
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        print(f"[ERROR] Feature status update failed: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to update feature status: {str(e)}"}
        )


@app.get("/implementation-plan/{feature_id}")
async def get_implementation_plan(feature_id: str):
    """
    Get the implementation plan for a specific feature.
    """
    try:
        plan = feature_implementation_manager.get_implementation_plan(feature_id)
        
        if not plan:
            return JSONResponse(
                status_code=404,
                content={"error": f"No implementation plan found for feature {feature_id}"}
            )
        
        return JSONResponse(content=plan)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get implementation plan: {str(e)}"}
        )

@app.get("/implementation-summary")
async def get_implementation_summary():
    """
    Get a summary of all feature implementations.
    """
    try:
        summary = feature_implementation_manager.get_implementation_summary()
        return JSONResponse(content=summary)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get implementation summary: {str(e)}"}
        )

@app.post("/generate-implementation-plan/{feature_id}")
async def generate_plan_for_feature(feature_id: str):
    """
    Generate or regenerate an implementation plan for a selected feature.
    """
    global competitive_analysis_results
    
    if not competitive_analysis_results:
        return JSONResponse(
            status_code=404,
            content={"error": "No competitive analysis results available"}
        )
    
    # Find the feature
    feature_gaps = competitive_analysis_results.get("feature_gaps", [])
    feature = next((f for f in feature_gaps if f.get("id") == feature_id), None)
    
    if not feature:
        return JSONResponse(
            status_code=404,
            content={"error": f"Feature {feature_id} not found"}
        )
    
    try:
        plan = feature_implementation_manager.generate_implementation_plan(
            feature, competitive_analysis_results
        )
        
        if not plan:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to generate implementation plan"}
            )
        
        return JSONResponse(content={
            "message": "Implementation plan generated successfully",
            "plan": plan
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate plan: {str(e)}"}
        )


# ================== CHATBOT API ENDPOINTS ==================

class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatApprovalRequest(BaseModel):
    plan_id: str
    session_id: str

@app.post("/api/chatbot/message")
async def chatbot_message(request: ChatMessageRequest):
    """Send a message to the chatbot and get a response."""
    try:
        # Create or get session
        if request.session_id:
            session = chatbot_manager.get_session(request.session_id)
            if not session:
                return JSONResponse(
                    status_code=404,
                    content={"error": "Session not found"}
                )
            session_id = request.session_id
        else:
            # Create new session
            session = chatbot_manager.create_session()
            session_id = session["session_id"]
       
        # Process the message
        response = await chatbot_manager.process_message(session_id, request.message)
        
        # Add session_id to response
        response["session_id"] = session_id
        
        return JSONResponse(content=response)
        
    except Exception as e:
        print(f"[ERROR] Chatbot message failed: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Chat bot failed: {str(e)}"}
        )

@app.post("/api/chatbot/approve")
async def chatbot_approve_plan(request: ChatApprovalRequest):
    """Approve a chatbot-generated plan and queue it for feature implementation."""
    try:
        # Get the pending change
        pending_change = chat_storage.get_pending_change(request.plan_id)
        
        if not pending_change:
            return JSONResponse(
                status_code=404,
                content={"error": "Plan not found"}
            )
        
        # Instead of executing directly, add to feature implementation pipeline
        plan = pending_change.get("plan", {})
        intent = pending_change.get("intent", "unknown")
        user_request = pending_change.get("user_request", "")
        
        # Create a feature entry for the implementation system
        feature = {
            "id": request.plan_id,
            "name": plan.get("summary", user_request),
            "description": user_request,
            "category": _intent_to_category(intent),
            "complexity": plan.get("complexity", "medium"),
            "business_impact": "high" if intent == "feature_request" else "medium",
            "estimated_effort": plan.get("estimated_effort", "Medium"),
            "implementation_notes": f"Chatbot-generated plan\nIntent: {intent}\n\nSteps:\n" + 
                "\n".join([f"{i}. {step.get('description', '')}" for i, step in enumerate(plan.get("steps", []), 1)]),
            "priority_score": 8 if intent in ["bug_fix", "ui_change"] else 6
        }
        
        # Select feature for implementation (adds to dashboard)
        result = feature_implementation_manager.select_feature_for_implementation(
            feature=feature,
            analysis_results={},
            generate_plan=False  # We already have a plan from chatbot
        )
        
        # Save the chatbot plan to the feature implementation system
        plan_file = feature_implementation_manager.implementation_plans_dir / f"{request.plan_id}_plan.json"
        plan_with_metadata = {
            **plan,
            "feature_id": request.plan_id,
            "generated_at": datetime.now().isoformat(),
            "status": "pending",
            "source": "chatbot",
            "intent": intent,
            "original_request": user_request
        }
        
        with open(plan_file, 'w') as f:
            import json
            json.dump(plan_with_metadata, f, indent=2)
        
        # Update change status to "queued"
        chat_storage.update_change_status(request.plan_id, "queued_for_implementation")
        
        return JSONResponse(content={
            "success": True,
            "message": f"✅ Plan approved and added to Feature Implementation Status.\n\nYou can now start the implementation from the dashboard.",
            "feature_id": request.plan_id,
            "status": "pending",
            "dashboard_link": f"/implementation-summary"
        })
        
    except Exception as e:
        print(f"[ERROR] Plan approval failed: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Approval failed: {str(e)}"}
        )

def _intent_to_category(intent: str) -> str:
    """Map chatbot intent to feature category."""
    mapping = {
        "ui_change": "UI/UX",
        "feature_request": "Feature",
        "bug_fix": "Bug Fix",
        "competitive_analysis": "Analysis",
        "refinement": "Enhancement"
    }
    return mapping.get(intent, "General")

@app.get("/api/chatbot/session/{session_id}")
async def get_chatbot_session(session_id: str):
    """Get chatbot session history."""
    try:
        session = chatbot_manager.get_session(session_id)
        
        if not session:
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found"}
            )
        
        return JSONResponse(content=session)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get session: {str(e)}"}
        )

@app.get("/api/chatbot/sessions")
async def get_all_chatbot_sessions():
    """Get all chatbot sessions."""
    try:
        sessions = chatbot_manager.get_all_sessions()
        return JSONResponse(content={"sessions": sessions})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get sessions: {str(e)}"}
        )

# ================== END CHATBOT API ENDPOINTS ==================


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
    Refactored maintenance cycle - Detection and Classification Only.
    
    New Architecture:
    1. Detect bugs through analysis
    2. Classify bugs by severity (Critical/High/Medium/Low)
    3. Add bugs to queue for processing via chatbot pipeline
    4. Auto-approve and execute non-critical bugs silently
    5. Notify users only for critical/high severity issues
    """
    log_stream = QueueLogStream(log_streamer)
    with contextlib.redirect_stdout(log_stream):
        try:
            print(f"[INFO] ==========================================")
            print(f"[INFO] Starting Intelligent Maintenance Cycle at {datetime.now()}")
            print(f"[INFO] Website: {os.getenv('WEBSITE_URL')}")
            print(f"[INFO] Mode: Detection → Classification → Queue Processing")
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
            
            # Step 2: Check if rollback is needed BEFORE detecting new issues
            print("[INFO] Step 2: Checking if rollback is needed...")
            rollback_result = rollback_manager.perform_rollback_if_needed(site_data)
            
            if rollback_result.get("rollback_performed"):
                print(f"[ROLLBACK] Automatic rollback performed: {rollback_result.get('pr_url')}")
                health_status["last_rollback"] = datetime.now().isoformat()
                health_status["last_error"] = f"Auto-rollback: {rollback_result.get('reason')}"
                return  # Skip bug detection after rollback
            else:
                print("[INFO] No rollback needed, proceeding with bug detection...")
            
            # PHASE 2: BUG DETECTION (unchanged)
            print("[INFO] Phase 2: Bug detection and analysis...")
            
            # Step 3: Get repository files
            print("[INFO] Step 3: Accessing repository files...")
            try:
                repo_files = get_all_repo_files()
                print(f"[SUCCESS] Retrieved {len(repo_files)} repository files")
            except Exception as e:
                print(f"[ERROR] Failed to get repository files: {e}")
                health_status["last_error"] = f"Repository access failed: {str(e)}"
                return
            
            # Step 4: Analyze data for bugs
            print("[INFO] Step 4: Analyzing for bugs and issues...")
            
            # Get URL and local repo path for bug detection
            url = os.getenv("WEBSITE_URL")
            repo_path = clone_or_pull_repo()
            
            bugs = asyncio.run(analyze_data(site_data, repo_files, url, repo_path))

            global detected_issues
            detected_issues = bugs
            
            if not bugs:
                print("[INFO] ✅ No bugs detected - website appears healthy!")
                print(f"[INFO] Maintenance cycle completed at {datetime.now()}")
                print(f"[INFO] ==========================================")
                return
            
            print(f"[SUCCESS] Detected {len(bugs)} bugs/issues")
            for i, bug in enumerate(bugs, 1):
                print(f"[INFO] Bug {i}: {bug.get('type', 'unknown')} - {bug.get('description', 'no description')[:100]}...")
            
            # PHASE 3: NEW - BUG CLASSIFICATION AND ROUTING
            print("[INFO] Phase 3: Classifying bugs by severity...")
            
            from bug_classifier import bug_classifier
            from bug_queue_manager import bug_queue_manager
            
            # Classify bugs by severity
            classified_bugs = bug_classifier.classify_bugs(bugs)
            
            # CONSOLIDATE SIMILAR BUGS before queuing
            from bug_consolidator import bug_consolidator
            
            # Flatten classified bugs for consolidation
            all_classified = []
            for severity, bugs_list in classified_bugs.items():
                for bug in bugs_list:
                    bug["severity"] = severity  # Ensure severity is set
                    all_classified.append(bug)
            
            print(f"[MAINTENANCE] Before consolidation: {len(all_classified)} bugs")
            consolidated_bugs = bug_consolidator.consolidate(all_classified)
            print(f"[MAINTENANCE] After consolidation: {len(consolidated_bugs)} bugs")
            
            # Re-classify consolidated bugs
            reclassified = {"critical": [], "high": [], "medium": [], "low": []}
            for bug in consolidated_bugs:
                severity = bug.get("severity", "medium")
                reclassified[severity].append(bug)
            
            # Add consolidated bugs to detected list (awaiting approval)
            print("[INFO] Phase 4: Adding bugs to detected list...")
            queue_result = bug_queue_manager.add_detected_bugs(reclassified)
            
            # Summary of classification (now based on reclassified bugs)
            critical_count = len(reclassified["critical"])
            high_count = len(reclassified["high"])
            medium_count = len(reclassified["medium"])
            low_count = len(reclassified["low"])
            
            print(f"[INFO] Classification Results:")
            print(f"[INFO]   🔴 CRITICAL: {critical_count} (require user approval)")
            print(f"[INFO]   🟠 HIGH: {high_count} (require user approval)")
            print(f"[INFO]   🟡 MEDIUM: {medium_count} (require user approval)")
            print(f"[INFO]   🟢 LOW: {low_count} (require user approval)")
            
            print(f"[SUCCESS] Added {queue_result['total_added']} bugs to queue")
            print(f"[INFO] Current queue size: {queue_result['queue_size']}")
            print(f"[INFO] Currently processing: {queue_result['processing_count']}")
            
            # Update health status
            health_status["last_error"] = None
            health_status["bugs_detected"] = len(bugs)
            health_status["bugs_queued"] = queue_result['total_added']
            
            # Notify user only about critical/high severity bugs
            user_attention_count = critical_count + high_count
            if user_attention_count > 0:
                print(f"[INFO] ⚠️  {user_attention_count} bug(s) require user attention")
                print(f"[INFO] User will be notified via dashboard")
            else:
                print(f"[INFO] ✅ All bugs will be auto-fixed in background")
            
            print(f"[INFO] Maintenance cycle completed successfully at {datetime.now()}")
            print(f"[INFO] Queue processor will handle bug fixes via chatbot pipeline")
            print(f"[INFO] ==========================================")
            
        except Exception as e:
            error_msg = f"Maintenance cycle failed: {str(e)}"
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

# ============================================================================
# CHATBOT API ENDPOINTS
# ============================================================================

class ChatMessageRequest(BaseModel):
    session_id: str
    message: str

class CreateSessionRequest(BaseModel):
    user_id: Optional[str] = "default"

class ApplyChangeRequest(BaseModel):
    change_id: str
    session_id: str

class RejectChangeRequest(BaseModel):
    change_id: str
    session_id: str
    reason: Optional[str] = None

@app.post("/chat/session/new")
async def create_chat_session(request: CreateSessionRequest = None):
    """Create a new chat session."""
    try:
        user_id = "default"
        if request:
            user_id = request.user_id
        
        session = chatbot_manager.create_session(user_id)
        
        return JSONResponse(content={
            "success": True,
            "session": session,
            "message": "Chat session created successfully"
        })
    except Exception as e:
        print(f"[CHAT_API] Error creating session: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to create session: {str(e)}"}
        )

@app.get("/chat/sessions")
async def get_chat_sessions(user_id: Optional[str] = None):
    """Get all chat sessions, optionally filtered by user_id."""
    try:
        sessions = chatbot_manager.get_all_sessions(user_id)
        
        return JSONResponse(content={
            "success": True,
            "sessions": sessions,
            "total": len(sessions)
        })
    except Exception as e:
        print(f"[CHAT_API] Error getting sessions: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get sessions: {str(e)}"}
        )

@app.get("/chat/session/{session_id}")
async def get_chat_session(session_id: str):
    """Get a specific chat session by ID."""
    try:
        session = chatbot_manager.get_session(session_id)
        
        if not session:
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found"}
            )
        
        return JSONResponse(content={
            "success": True,
            "session": session
        })
    except Exception as e:
        print(f"[CHAT_API] Error getting session: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get session: {str(e)}"}
        )

@app.delete("/chat/session/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session."""
    try:
        result = chatbot_manager.delete_session(session_id)
        
        if not result:
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found"}
            )
        
        return JSONResponse(content={
            "success": True,
            "message": "Session deleted successfully"
        })
    except Exception as e:
        print(f"[CHAT_API] Error deleting session: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to delete session: {str(e)}"}
        )

@app.post("/chat/message")
async def send_chat_message(request: ChatMessageRequest):
    """Send a message to the chatbot and get response."""
    try:
        print(f"[CHAT_API] Processing message in session {request.session_id}")
        
        response = await chatbot_manager.process_message(
            request.session_id,
            request.message
        )
        
        return JSONResponse(content={
            "success": True,
            **response
        })
    except Exception as e:
        print(f"[CHAT_API] Error processing message: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process message: {str(e)}"}
        )

@app.get("/chat/pending-changes/{session_id}")
async def get_pending_changes(session_id: str):
    """Get all pending changes for a session."""
    try:
        pending_changes = chat_storage.get_session_pending_changes(session_id)
        
        return JSONResponse(content={
            "success": True,
            "pending_changes": pending_changes,
            "total": len(pending_changes)
        })
    except Exception as e:
        print(f"[CHAT_API] Error getting pending changes: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get pending changes: {str(e)}"}
        )

@app.post("/chat/apply-change")
async def apply_pending_change(request: ApplyChangeRequest):
    """Apply a pending change after user approval."""
    try:
        # Get the change data
        change_data = chat_storage.get_pending_change(request.change_id)
        
        if not change_data:
            return JSONResponse(
                status_code=404,
                content={"error": "Change not found"}
            )
        
        if change_data["status"] != "pending":
            return JSONResponse(
                status_code=400,
                content={"error": f"Change is already {change_data['status']}"}
            )
        
        print(f"[CHAT_API] Applying change {request.change_id}...")
        
        # Execute the change
        result = await chatbot_executor.execute_change(change_data)
        
        # Update change status
        chat_storage.update_change_status(
            request.change_id,
            "applied" if result.get("success") else "failed",
            result.get("message", "")
        )
        
        # Add result message to chat
        result_message = result.get("message", "Change applied successfully!")
        chat_storage.add_message(
            request.session_id,
            "assistant",
            f"✅ {result_message}",
            {"message_type": "execution_result", "result": result}
        )
        
        return JSONResponse(content={
            "success": True,
            "result": result,
            "message": result_message
        })
    except Exception as e:
        print(f"[CHAT_API] Error applying change: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to apply change: {str(e)}"}
        )

@app.post("/chat/reject-change")
async def reject_pending_change(request: RejectChangeRequest):
    """Reject a pending change."""
    try:
        # Get the change data
        change_data = chat_storage.get_pending_change(request.change_id)
        
        if not change_data:
            return JSONResponse(
                status_code=404,
                content={"error": "Change not found"}
            )
        
        # Update change status
        chat_storage.update_change_status(
            request.change_id,
            "rejected",
            request.reason or "Rejected by user"
        )
        
        # Add message to chat
        chat_storage.add_message(
            request.session_id,
            "assistant",
            "❌ Change rejected. Let me know if you'd like to try a different approach!",
            {"message_type": "change_rejected"}
        )
        
        return JSONResponse(content={
            "success": True,
            "message": "Change rejected successfully"
        })
    except Exception as e:
        print(f"[CHAT_API] Error rejecting change: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to reject change: {str(e)}"}
        )

# ============================================================================
# END CHATBOT API ENDPOINTS
# ============================================================================

# Enhanced helper functions for health checks
def test_environment_variables():
    """Test if critical environment variables are loaded."""
    required_vars = ["WEBSITE_URL", "GITHUB_REPO", "GITHUB_TOKEN", "GEMINI_API_KEY"]
    results = {}
    all_healthy = True
    
    for var in required_vars:
        value = os.getenv(var)
        results[var] = {
            "loaded": bool(value),
            "value": value[:10] + "..." if value and len(value) > 10 else value
        }
        if not value:
            all_healthy = False
    
    results["all_healthy"] = all_healthy
    return results

def test_dependencies():
    """Test if all dependencies are working."""
    results = {
        "github_api": False,
        "gemini_api": False,
        "all_healthy": False
    }
    
    # Test GitHub API
    try:
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPO")
        if token and repo:
            from github import Github
            g = Github(token)
            g.get_repo(repo)
            results["github_api"] = True
    except Exception as e:
        print(f"[WARNING] GitHub API test failed: {e}")
    
    # Test Gemini API
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            results["gemini_api"] = True
    except Exception as e:
        print(f"[WARNING] Gemini API test failed: {e}")
    
    results["all_healthy"] = results["github_api"] and results["gemini_api"]
    return results

# Mount static files if the directory exists (Production mode)
# IMPORTANT: This must be the LAST route defined to avoid shadowing API endpoints
ui_dist_path = Path("/app/ui_dist")
if ui_dist_path.exists():
    print(f"[INFO] Mounting static files from {ui_dist_path}")
    
    # Mount static assets
    app.mount("/", StaticFiles(directory=str(ui_dist_path), html=True), name="ui")

    # SPA Fallback for 404s (Let frontend handle routing)
    @app.exception_handler(404)
    async def custom_404_handler(request, exc):
        # Only for GET requests that accept HTML
        if request.method == "GET" and "text/html" in request.headers.get("accept", ""):
            index_path = ui_dist_path / "index.html"
            if index_path.exists():
                return HTMLResponse(content=index_path.read_text(), status_code=200)
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

if __name__ == "__main__":
    print("[INFO] Starting Enhanced AI Engine Microservice with Safety Features...")
    print(f"[INFO] Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"[INFO] Website: {os.getenv('WEBSITE_URL', 'Not configured')}")
    print(f"[INFO] Monitoring Mode: {os.getenv('MONITORING_MODE', 'simple')}")
    print(f"[INFO] Safety Features: Validation ✅ | Rollback Protection ✅")
    uvicorn.run("main_with_config:app", host="0.0.0.0", port=8000, reload=True)
