"""
Celery Tasks for AI Engine

Defines background tasks for maintenance cycles, rollbacks, and competitive analysis.
"""

import os
import asyncio
from datetime import datetime
from celery_app import celery_app
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

@celery_app.task(name="tasks.maintenance_cycle", bind=True)
def task_maintenance_cycle(self):
    """Celery task for running the enhanced maintenance cycle."""
    from main_with_config import start_enhanced_maintenance_cycle
    print(f"[CELERY] Starting maintenance cycle task {self.request.id}")
    
    # Run the existing logic
    # Note: start_enhanced_maintenance_cycle is synchronous but contains async calls via asyncio.run
    start_enhanced_maintenance_cycle()
    
    return {"status": "completed", "task_id": self.request.id}

@celery_app.task(name="tasks.manual_rollback", bind=True)
def task_manual_rollback(self):
    """Celery task for performing manual rollback."""
    from main_with_config import perform_manual_rollback
    print(f"[CELERY] Starting manual rollback task {self.request.id}")
    
    perform_manual_rollback()
    
    return {"status": "completed", "task_id": self.request.id}

@celery_app.task(name="tasks.analyze_competitors", bind=True)
def task_analyze_competitors(self, own_site_url, competitor_urls, depth, premium, ultra, professional):
    """Celery task for running competitive analysis."""
    # We need a new event loop for the async analyzer call
    async def run_analysis():
        if professional:
            from professional_competitive_analyzer import professional_analyzer
            analysis = await professional_analyzer.analyze_competitors_professional(own_site_url, competitor_urls)
            # Need to transform this for UI if needed, but here we just return the raw analysis
            # and let the endpoint/frontend handle storage or retrieval.
            # Actually, main_with_config stores it in a global. Celery tasks should store it in a persistent way (Redis or file).
            return analysis
        elif ultra:
            from ultra_comprehensive_analyzer import ultra_analyzer
            analysis = await ultra_analyzer.analyze_ultra_comprehensive(own_site_url, competitor_urls)
            return analysis
        else:
            from competitive_analyzer import CompetitiveAnalyzer
            analyzer = CompetitiveAnalyzer(depth=depth)
            analysis = await analyzer.analyze_competitors(own_site_url, competitor_urls, premium=premium)
            return analysis

    print(f"[CELERY] Starting competitive analysis task {self.request.id}")
    # Run the async function synchronously
    try:
        result = asyncio.run(run_analysis())
    except RuntimeError:
        # Fallback if an event loop is already running (unlikely in Celery worker but possible)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_analysis())
        loop.close()
    
    # Store results in a file or Redis for the frontend to pick up
    # For now, let's use a JSON file in a 'data/analysis' directory
    import json
    results_dir = Path("data/analysis")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    result_file = results_dir / f"results_{self.request.id}.json"
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)
        
    return {
        "status": "completed", 
        "task_id": self.request.id, 
        "result_file": str(result_file)
    }
