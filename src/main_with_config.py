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
from feature_implementation_manager import feature_implementation_manager
from chatbot_manager import chatbot_manager
from chatbot_executor import chatbot_executor
from chat_storage import chat_storage
from pydantic import BaseModel
from typing import List, Dict, Optional
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

if __name__ == "__main__":
    print("[INFO] Starting Enhanced AI Engine Microservice with Safety Features...")
    print(f"[INFO] Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"[INFO] Website: {os.getenv('WEBSITE_URL', 'Not configured')}")
    print(f"[INFO] Monitoring Mode: {os.getenv('MONITORING_MODE', 'simple')}")
    print(f"[INFO] Safety Features: Validation ✅ | Rollback Protection ✅")
    uvicorn.run("main_with_config:app", host="0.0.0.0", port=8000, reload=True)
