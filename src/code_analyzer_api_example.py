"""
Production-Ready FastAPI Integration Example
Demonstrates CodeAnalyzer with monitoring, rate limiting, and async support.
"""

from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import asyncio

# Import our production-ready components
from code_analyzer import CodeAnalyzer, analyze_repository_async_quick
from code_analyzer_metrics import analysis_metrics
from code_analyzer_rate_limiter import rate_limiter

app = FastAPI(title="CodeAnalyzer SaaS API", version="1.0.0")


class AnalysisRequest(BaseModel):
    repo_path: str
    use_cache: bool = True
    max_files: Optional[int] = None


class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    metrics: Optional[dict] = None


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_repository(
    request: AnalysisRequest,
    x_user_id: str = Header(..., description="User ID for rate limiting")
):
    """
    Analyze a repository with rate limiting and monitoring.
    
    Headers:
        X-User-ID: User identifier for rate limiting
    """
    
    # Check rate limit
    rate_check = rate_limiter.check_rate_limit(x_user_id)
    if not rate_check['allowed']:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "remaining_hour": rate_check['remaining_hour'],
                "remaining_day": rate_check['remaining_day'],
                "reset_at": rate_check['reset_at']
            }
        )
    
    # Record request for rate limiting
    rate_limiter.record_request(x_user_id)
    
    try:
        import time
        start_time = time.time()
        
        # Perform analysis (async, non-blocking)
        analyzer = CodeAnalyzer(
            request.repo_path,
            use_cache=request.use_cache,
            max_files=request.max_files
        )
        
        result = await analyzer.analyze_repository_async()
        
        duration = time.time() - start_time
        files_analyzed = len(result.get('file_structure', {}))
        cache_hit = duration < 0.1  # Heuristic
        
        # Record metrics
        analysis_metrics.record_analysis(
            repo_path=request.repo_path,
            duration=duration,
            files_analyzed=files_analyzed,
            cache_hit=cache_hit
        )
        
        # Monitor resources
        resource_info = analysis_metrics.monitor_memory()
        
        return AnalysisResponse(
            success=True,
            data=result,
            metrics={
                "duration": round(duration, 2),
                "files_analyzed": files_analyzed,
                "cache_hit": cache_hit,
                "memory_mb": resource_info['memory_mb'],
                "rate_limit": rate_check
            }
        )
    
    except Exception as e:
        # Record error metrics
        analysis_metrics.record_analysis(
            repo_path=request.repo_path,
            duration=0,
            files_analyzed=0,
            error=str(e)
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get analysis metrics and statistics."""
    return {
        "stats": analysis_metrics.get_stats(),
        "resources": analysis_metrics.monitor_memory()
    }


@app.get("/rate-limit/{user_id}")
async def get_rate_limit(user_id: str):
    """Get rate limit status for a user."""
    return rate_limiter.get_user_stats(user_id)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    resources = analysis_metrics.monitor_memory()
    
    # Check if resources are healthy
    healthy = (
        resources['memory_mb'] < 1500 and
        resources['cpu_percent'] < 90
    )
    
    status_code = 200 if healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if healthy else "degraded",
            "resources": resources
        }
    )


# Background task example
@app.post("/analyze-background")
async def analyze_background(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    x_user_id: str = Header(...)
):
    """Queue analysis as background task."""
    
    # Check rate limit
    rate_check = rate_limiter.check_rate_limit(x_user_id)
    if not rate_check['allowed']:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    rate_limiter.record_request(x_user_id)
    
    # Add to background tasks
    background_tasks.add_task(
        analyze_in_background,
        request.repo_path,
        x_user_id
    )
    
    return {"message": "Analysis queued", "status": "pending"}


async def analyze_in_background(repo_path: str, user_id: str):
    """Background task for analysis."""
    import time
    start_time = time.time()
    
    try:
        result = await analyze_repository_async_quick(repo_path)
        duration = time.time() - start_time
        
        analysis_metrics.record_analysis(
            repo_path=repo_path,
            duration=duration,
            files_analyzed=len(result.get('file_structure', {})),
            cache_hit=duration < 0.1
        )
        
        print(f"[BACKGROUND] Analysis complete for user {user_id}")
        
    except Exception as e:
        analysis_metrics.record_analysis(
            repo_path=repo_path,
            duration=0,
            files_analyzed=0,
            error=str(e)
        )
        print(f"[BACKGROUND] Analysis failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
