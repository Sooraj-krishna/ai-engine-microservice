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

@celery_app.task(
    name="tasks.maintenance_cycle",
    bind=True,
    soft_time_limit=3300,   # 55 min SIGTERM — gives graceful cleanup
    time_limit=3600,        # 60 min hard SIGKILL safety net
)
def task_maintenance_cycle(self):
    """Run the AI maintenance cycle (bug detection → classification → queue).

    Fixes vs original:
    - Time-limits prevent infinite hangs (mirrors competitive analysis fix).
    - Imports only the target function, not the full module (avoids re-running
      FastAPI startup, DB connections, middleware, etc. in the Celery process).
    - Graceful error result stored so the UI can display it.
    - asyncio.run() collision guard (Celery may already have a loop).
    """
    from celery.exceptions import SoftTimeLimitExceeded
    import traceback

    print(f"[CELERY] Starting maintenance cycle task {self.request.id}")

    try:
        # Import only the function — avoids re-executing all of main_with_config's
        # module-level code (FastAPI app creation, middleware, DB init, etc.)
        if "main_with_config" in sys.modules:
            main_mod = sys.modules["main_with_config"]
        else:
            main_mod = _load_module_from_src("main_with_config")

        cycle_fn = main_mod.start_enhanced_maintenance_cycle

        # start_enhanced_maintenance_cycle is synchronous but internally calls
        # asyncio.run(analyze_data(...)). Guard against an already-running loop.
        try:
            cycle_fn()
        except RuntimeError as re:
            if "cannot be called from a running event loop" in str(re).lower():
                # Running inside an existing event loop — execute in a fresh thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(cycle_fn)
                    future.result(timeout=3290)  # just under soft_time_limit
            else:
                raise

        print(f"[CELERY] Maintenance cycle task {self.request.id} completed.")
        return {"status": "completed", "task_id": self.request.id}

    except SoftTimeLimitExceeded:
        msg = "Maintenance cycle exceeded soft time limit (55 min) and was terminated."
        print(f"[CELERY] {msg}")
        return {"status": "timeout", "task_id": self.request.id, "error": msg}

    except Exception as exc:
        tb = traceback.format_exc()
        print(f"[CELERY] Maintenance cycle task {self.request.id} FAILED:\n{tb}")
        # Re-raise so Celery marks the task FAILED (visible in the UI)
        raise

@celery_app.task(
    name="tasks.manual_rollback",
    bind=True,
    soft_time_limit=300,
    time_limit=360,
)
def task_manual_rollback(self):
    """Celery task for performing manual rollback."""
    from celery.exceptions import SoftTimeLimitExceeded
    import traceback

    print(f"[CELERY] Starting manual rollback task {self.request.id}")
    try:
        if "main_with_config" in sys.modules:
            main_mod = sys.modules["main_with_config"]
        else:
            main_mod = _load_module_from_src("main_with_config")

        main_mod.perform_manual_rollback()
        print(f"[CELERY] Manual rollback task {self.request.id} completed.")
        return {"status": "completed", "task_id": self.request.id}
    except SoftTimeLimitExceeded:
        return {"status": "timeout", "task_id": self.request.id, "error": "Rollback timed out."}
    except Exception as exc:
        print(f"[CELERY] Manual rollback FAILED: {traceback.format_exc()}")
        raise

@celery_app.task(
    name="tasks.analyze_competitors",
    bind=True,
    soft_time_limit=660,   # Send SIGTERM after 11 min → triggers SoftTimeLimitExceeded
    time_limit=720,        # Send SIGKILL after 12 min → hard kill
)
def task_analyze_competitors(self, own_site_url, competitor_urls, depth, premium, ultra, professional):
    """Celery task for running competitive analysis.

    Hard limits prevent 50-minute zombie runs caused by Playwright browser hangs.
    Per-site fetch timeout is handled inside professional_competitive_analyzer.py.
    """
    from celery.exceptions import SoftTimeLimitExceeded
    import json

    ASYNC_TIMEOUT = 600  # 10 minutes — matches ANALYSIS_TIMEOUT in the analyzer

    async def run_analysis():
        if professional:
            from professional_competitive_analyzer import professional_analyzer
            return await professional_analyzer.analyze_competitors_professional(own_site_url, competitor_urls)
        elif ultra:
            from ultra_comprehensive_analyzer import ultra_analyzer
            return await ultra_analyzer.analyze_ultra_comprehensive(own_site_url, competitor_urls)
        else:
            from competitive_analyzer import CompetitiveAnalyzer
            analyzer = CompetitiveAnalyzer(depth=depth)
            return await analyzer.analyze_competitors(own_site_url, competitor_urls, premium=premium)

    print(f"[CELERY] Starting competitive analysis task {self.request.id} (professional={professional})")

    try:
        try:
            result = asyncio.run(asyncio.wait_for(run_analysis(), timeout=ASYNC_TIMEOUT))
        except RuntimeError:
            # Fallback: running inside an existing event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(asyncio.wait_for(run_analysis(), timeout=ASYNC_TIMEOUT))
            finally:
                loop.close()
    except asyncio.TimeoutError:
        print(f"[CELERY] Task {self.request.id} timed out after {ASYNC_TIMEOUT}s.")
        result = {"status": "timeout", "error": "Analysis timed out. Try fewer competitor URLs."}
    except SoftTimeLimitExceeded:
        print(f"[CELERY] Task {self.request.id} hit Celery soft time limit.")
        result = {"status": "timeout", "error": "Task exceeded time limit."}
    except Exception as e:
        print(f"[CELERY] Task {self.request.id} failed: {e}")
        result = {"status": "error", "error": str(e)}

    # Persist results for frontend polling
    results_dir = Path("data/analysis")
    results_dir.mkdir(parents=True, exist_ok=True)

    result_file = results_dir / f"results_{self.request.id}.json"
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"[CELERY] Task {self.request.id} done → {result_file}")
    return {
        "status": result.get("status", "completed"),
        "task_id": self.request.id,
        "result_file": str(result_file)
    }

@celery_app.task(
    name="tasks.execute_implementation",
    bind=True,
    soft_time_limit=600,
    time_limit=660,
)
def task_execute_implementation(self, feature_id):
    """Celery task for executing a feature implementation."""
    import asyncio
    import traceback
    
    print(f"[CELERY] Starting implementation task {self.request.id} for feature {feature_id}")
    
    async def run_impl():
        from feature_implementation_manager import FeatureImplementationManager
        manager = FeatureImplementationManager()
        return await manager.execute_implementation(feature_id)
        
    try:
        # Run async function in sync task
        try:
            result = asyncio.run(run_impl())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(run_impl())
            finally:
                loop.close()
                
        print(f"[CELERY] Implementation task {self.request.id} completed.")
        return {"status": "completed", "result": result}
    except Exception as e:
        print(f"[CELERY] Implementation task {self.request.id} failed: {e}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}
