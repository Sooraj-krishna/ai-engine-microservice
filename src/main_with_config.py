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

from github_handler import get_all_repo_files, submit_fix_pr, clone_or_pull_repo
from analyzer import analyze_data
from generator import prepare_fixes
from rollback_manager import RollbackManager
from validator import CodeValidator
from configure_endpoint import router as config_router
from log_streamer import log_streamer, QueueLogStream
from log_summary import log_summarizer
from model_router import _query_gemini_api
from pydantic import BaseModel
from typing import List, Dict
import contextlib
import sys

app = FastAPI(
    title="AI Engine Microservice",
    description="Self-maintaining SaaS AI Engine with Google Analytics, Log Monitoring, Validation, and Rollback Protection",
    version="2.0.0"
)

@app.on_event("startup")
async def startup_event():
    # Start the log broadcasting task
    asyncio.create_task(log_streamer.broadcast_logs())

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
def manual_rollback(background_tasks: BackgroundTasks):
    """Manually trigger rollback of recent AI changes."""
    print("[INFO] Manual rollback requested")
    background_tasks.add_task(perform_manual_rollback)
    return {"message": "Manual rollback initiated", "timestamp": datetime.now().isoformat()}

# Competitive Analysis Endpoints
@app.post("/analyze-competitors")
async def analyze_competitors(competitor_urls: list[str] = None, depth: str = None, premium: bool = False, ultra: bool = False, professional: bool = False):
    """
    Analyze competitor sites and generate feature recommendations.
    
    Args:
        competitor_urls: List of competitor URLs (uses COMPETITOR_URLS from .env if not provided)
        depth: Analysis depth - "basic", "standard", or "deep" (uses COMPETITIVE_ANALYSIS_DEPTH from .env if not provided)
        premium: Enable comprehensive analysis (UI + SEO + accessibility + tech stack)
        ultra: Enable ULTRA-COMPREHENSIVE mode - finds EVERY feature difference (colors, fonts, spacing, etc.)
        professional: Enable PROFESSIONAL mode - detects business features (COD, Try & Buy, delivery options, etc.)
    """
    # Determine analysis mode
    if professional:
        print(f"[INFO] 🎯 PROFESSIONAL mode - Business features (COD, Payment, Delivery, etc.)")
    elif premium:
        print(f"[INFO] ✨ COMPREHENSIVE mode - UI + SEO + Accessibility + Tech Stack")
    else:
        # Default: Standard is now comprehensive (premium=true for old analyzer)
        premium = True
        print(f"[INFO] 📊 STANDARD mode - Running comprehensive analysis (UI + SEO + Accessibility)")
    
    print(f"[INFO] Competitive analysis requested (premium: {premium}, ultra: {ultra}, professional: {professional})")
    
    # Get competitor URLs from request or environment
    if not competitor_urls:
        competitor_urls_str = os.getenv("COMPETITOR_URLS", "")
        competitor_urls = [url.strip() for url in competitor_urls_str.split(",") if url.strip()]
    
    if not competitor_urls:
        return JSONResponse(
            status_code=400,
            content={"error": "No competitor URLs provided. Add COMPETITOR_URLS to .env or pass URLs in request body"}
        )
    
    # Get depth from request or environment
    if not depth:
        depth = os.getenv("COMPETITIVE_ANALYSIS_DEPTH", "standard")
    
    # Validate depth
    if depth not in ["basic", "standard", "deep"]:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid depth '{depth}'. Must be 'basic', 'standard', or 'deep'"}
        )
    
    # Check if enabled
    if not os.getenv("ENABLE_COMPETITIVE_ANALYSIS", "true").lower() == "true":
        return JSONResponse(
            status_code=403,
            content={"error": "Competitive analysis is disabled. Set ENABLE_COMPETITIVE_ANALYSIS=true in .env"}
        )
    
    # Check if premium is enabled
    if premium and not os.getenv("ENABLE_PREMIUM_ANALYSIS", "true").lower() == "true":
        return JSONResponse(
            status_code=403,
            content={"error": "Premium analysis is disabled. Set ENABLE_PREMIUM_ANALYSIS=true in .env"}
        )
    
    own_site_url = os.getenv("WEBSITE_URL")
    if not own_site_url:
        return JSONResponse(
            status_code=400,
            content={"error": "WEBSITE_URL not configured in .env"}
        )
    
    try:
        # Declare global at the start
        global competitive_analysis_results
        
        # PROFESSIONAL MODE - Business Features (COD, Try & Buy, etc.)
        if professional:
            print(f"[INFO] 🎯 PROFESSIONAL MODE ENABLED")
            print(f"[INFO] Detecting business features: COD, Try & Buy, delivery options, payment methods...")
            
            from professional_competitive_analyzer import professional_analyzer
            analysis = await professional_analyzer.analyze_competitors_professional(own_site_url, competitor_urls)
            
            # Convert professional analysis format to match frontend expectations
            # UI expects: id, name, category, description, found_in, frequency, frequency_percentage,
            #             complexity, priority_score, estimated_effort, business_impact, implementation_notes
            
            feature_gaps_for_ui = []
            for idx, gap in enumerate(analysis.get("all_gaps", []), 1):
                # Generate UI-compatible format
                competitor_count = gap.get("competitor_count", 0)
                total_competitors = len(competitor_urls)
                frequency_percentage = f"{int((competitor_count / total_competitors) * 100)}%" if total_competitors > 0 else "0%"
                
                # Map priority_score (0-100) to priority_score (0-10) for UI
                priority_score_100 = gap.get("priority_score", 50)
                priority_score_10 = int(priority_score_100 / 10)
                
                # Determine complexity and effort
                complexity = "medium"  # Default
                estimated_effort = "Medium"
                if priority_score_100 >= 85:
                    estimated_effort = "High"
                    complexity = "high"
                elif priority_score_100 <= 60:
                    estimated_effort = "Low"
                    complexity = "low"
                
                # Determine business impact
                business_impact = "high" if priority_score_100 >= 80 else "medium" if priority_score_100 >= 60 else "low"
                
                # Generate description
                description = f"{gap.get('category', 'Feature')} feature found in {competitor_count} out of {total_competitors} competitors"
                
                # Implementation notes
                evidence_summary = ". ".join(gap.get("evidence", [])[:2])
                implementation_notes = f"Competitors: {', '.join([url.split('//')[1].split('/')[0] for url in gap.get('competitors_with', [])])}. Evidence: {evidence_summary[:150]}"
                
                feature_gaps_for_ui.append({
                    "id": f"gap_{idx}",
                    "name": gap.get("feature_name", "Unknown Feature"),
                    "category": gap.get("category", "General"),
                    "description": description,
                    "found_in": [url.split("//")[1].split("/")[0] for url in gap.get("competitors_with", [])],
                    "frequency": f"{competitor_count}/{total_competitors}",
                    "frequency_percentage": frequency_percentage,
                    "complexity": complexity,
                    "priority_score": priority_score_10,
                    "estimated_effort": estimated_effort,
                    "business_impact": business_impact,
                    "implementation_notes": implementation_notes
                })
            
            # Store analysis globally for /feature-recommendations endpoint
            competitive_analysis_results = {
                "analysis_date": analysis["analyzed_at"],
                "feature_gaps": feature_gaps_for_ui,
                "summary": {
                    "total_competitors": len(competitor_urls),
                    "total_gaps": analysis["total_gaps"],
                    "high_priority": len([g for g in feature_gaps_for_ui if g["priority_score"] >= 7]),
                    "medium_priority": len([g for g in feature_gaps_for_ui if 4 <= g["priority_score"] < 7]),
                    "low_priority": len([g for g in feature_gaps_for_ui if g["priority_score"] < 4])
                },
                "analysis_type": "professional"
            }
            
            return JSONResponse(content={
                "status": "success",
                "analysis_type": "professional",
                "total_gaps": analysis["total_gaps"],
                "high_priority": len([g for g in feature_gaps_for_ui if g["priority_score"] >= 7]),
                "gaps_by_category": analysis["gaps_by_category"],
                "high_priority_gaps": [g for g in feature_gaps_for_ui if g["priority_score"] >= 7],
                "feature_gaps": feature_gaps_for_ui,  # Include for UI
                "recommendations": analysis["recommendations"],
                "summary": competitive_analysis_results["summary"],
                "message": f"✅ Found {analysis['total_gaps']} business feature gaps using PROFESSIONAL analysis"
            })
        
        # ULTRA-COMPREHENSIVE MODE - Finds EVERY difference
        if ultra:
            print(f"[INFO] 🚀 ULTRA-COMPREHENSIVE MODE ENABLED")
            print(f"[INFO] This will detect EVERY feature difference including colors, fonts, spacing, etc.")
            
            from ultra_comprehensive_analyzer import ultra_analyzer
            analysis = await ultra_analyzer.analyze_ultra_comprehensive(own_site_url, competitor_urls)
            
            # Store analysis globally for /feature-recommendations endpoint
            # Convert ultra-comprehensive format to match frontend expectations
            competitive_analysis_results = {
                "analysis_date": datetime.now().isoformat(),
                "feature_gaps": analysis["feature_gaps"],
                "summary": {
                    "total_competitors": len(competitor_urls),
                    "total_gaps": analysis["total_gaps_found"],
                    "high_priority": len([g for g in analysis["feature_gaps"] if g.get("priority") in ["critical", "high"]]),
                    "medium_priority": len([g for g in analysis["feature_gaps"] if g.get("priority") == "medium"]),
                    "low_priority": len([g for g in analysis["feature_gaps"] if g.get("priority") == "low"])
                },
                "analysis_type": "ultra_comprehensive"
            }
            
            return JSONResponse(content={
                "status": "success",
                "analysis_type": "ultra_comprehensive",
                "total_features_found": analysis["total_gaps_found"],
                "recommendations": analysis["feature_gaps"],
                "message": f"✅ Found {analysis['total_gaps_found']} feature gaps using ULTRA-COMPREHENSIVE analysis"
            })
        
        # Standard analysis
        from competitive_analyzer import CompetitiveAnalyzer
        analyzer = CompetitiveAnalyzer(depth=depth)
        
        print(f"[INFO] Starting competitive analysis with depth: {depth}, premium: {premium}")
        analysis = await analyzer.analyze_competitors(own_site_url, competitor_urls, premium=premium)
        
        # Store analysis globally for /feature-recommendations endpoint
        competitive_analysis_results = analysis
        
        return JSONResponse(content=analysis)
        
    except Exception as e:
        print(f"[ERROR] Competitive analysis failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Competitive analysis failed: {str(e)}"}
        )

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
    User selects which feature to implement next.
    For MVP: Just logs the selection (no actual implementation).
    """
    global competitive_analysis_results
    
    feature_id = request.get("feature_id")
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
    
    # For MVP: Just log the selection
    print(f"[COMPETITIVE_ANALYSIS] User selected feature for implementation:")
    print(f"[COMPETITIVE_ANALYSIS] - ID: {feature_id}")
    print(f"[COMPETITIVE_ANALYSIS] - Name: {selected_feature.get('name')}")
    print(f"[COMPETITIVE_ANALYSIS] - Priority Score: {selected_feature.get('priority_score')}")
    print(f"[COMPETITIVE_ANALYSIS] - Estimated Effort: {selected_feature.get('estimated_effort')}")
    
    return JSONResponse(content={
        "message": f"Feature '{selected_feature.get('name')}' selected for future implementation",
        "feature": selected_feature,
        "note": "Feature selection logged. Implementation planning will be added in future updates."
    })

# Global variable to store competitive analysis results
competitive_analysis_results = None


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
    log_stream = QueueLogStream(log_streamer)
    with contextlib.redirect_stdout(log_stream):
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
            try:
                repo_files = get_all_repo_files()
                print(f"[SUCCESS] Retrieved {len(repo_files)} repository files")
            except Exception as e:
                print(f"[ERROR] Failed to get repository files: {e}")
                health_status["last_error"] = f"Repository access failed: {str(e)}"
                return
            
            # Step 4: Analyze data for issues
            print("[INFO] Step 4: Analyzing data for improvement opportunities...")
            
            # Get URL and local repo path for bug detection
            url = os.getenv("WEBSITE_URL")
            repo_path = clone_or_pull_repo()
            
            issues = asyncio.run(analyze_data(site_data, repo_files, url, repo_path))

            global detected_issues
            detected_issues = issues
            
            if issues:
                print(f"[SUCCESS] Detected {len(issues)} improvement opportunities:")
                for i, issue in enumerate(issues, 1):
                    print(f"[INFO] Issue {i}: {issue.get('type', 'unknown')} - {issue.get('description', 'no description')[:100]}...")
            
            # Step 5: Generate and validate fixes
            if issues:
                print("[INFO] Step 5: Generating and validating code fixes...")
                print(f"[INFO] All fixes will be validated for safety before application...")
                
                # This calls prepare_fixes which now includes validation and testing
                # Pass repo_path for improved fixer if available
                print("[INFO] Testing fixes in isolated environment before applying...")
                fixes = asyncio.run(prepare_fixes(issues, repo_path=repo_path))
                
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

if __name__ == "__main__":
    print("[INFO] Starting Enhanced AI Engine Microservice with Safety Features...")
    print(f"[INFO] Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"[INFO] Website: {os.getenv('WEBSITE_URL', 'Not configured')}")
    print(f"[INFO] Monitoring Mode: {os.getenv('MONITORING_MODE', 'simple')}")
    print(f"[INFO] Safety Features: Validation ✅ | Rollback Protection ✅")
    uvicorn.run("main_with_config:app", host="0.0.0.0", port=8000, reload=True)
