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
import sys
import importlib.util

# Load environment variables.
# Some environments block dotfiles; fall back to `config.env`.
env_path = Path(__file__).parent.parent / '.env'
fallback_env_path = Path(__file__).parent.parent / 'config.env'
load_dotenv(dotenv_path=env_path if env_path.exists() else fallback_env_path)

# Ensure the `src/` directory is on sys.path when Celery forks worker processes.
# (Without this, task-time imports like `import main_with_config` can fail depending on how the worker was launched.)
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _load_module_from_src(module_name: str):
    """
    Load a module by filename from the `src/` directory.
    This avoids brittle sys.path / working-directory issues in Celery forked workers.
    """
    module_path = SRC_DIR / f"{module_name}.py"
    # Ensure imports like `import github_handler` (also in src/) resolve while executing the loaded module.
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not spec or not spec.loader:
        raise ModuleNotFoundError(f"Could not load module '{module_name}' from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

@celery_app.task(name="tasks.maintenance_cycle", bind=True)
def task_maintenance_cycle(self):
    """Celery task for running the enhanced maintenance cycle."""
    main_with_config = _load_module_from_src("main_with_config")
    print(f"[CELERY] Starting maintenance cycle task {self.request.id}")
    
    # Run the existing logic
    # Note: start_enhanced_maintenance_cycle is synchronous but contains async calls via asyncio.run
    main_with_config.start_enhanced_maintenance_cycle()
    
    return {"status": "completed", "task_id": self.request.id}

@celery_app.task(name="tasks.manual_rollback", bind=True)
def task_manual_rollback(self):
    """Celery task for performing manual rollback."""
    main_with_config = _load_module_from_src("main_with_config")
    print(f"[CELERY] Starting manual rollback task {self.request.id}")
    
    main_with_config.perform_manual_rollback()
    
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
