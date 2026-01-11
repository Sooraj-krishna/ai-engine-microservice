"""
Progress Tracker - Real-time progress updates for long-running operations.
"""

from typing import Dict, Callable, Optional
from datetime import datetime
import asyncio


class ProgressTracker:
    """Tracks and broadcasts progress for long-running operations."""
    
    def __init__(self):
        self.current_operation = None
        self.callbacks = []
    
    def register_callback(self, callback: Callable):
        """Register a callback to receive progress updates."""
        self.callbacks.append(callback)
    
    def start_operation(self, operation_name: str, total_steps: int):
        """Start tracking a new operation."""
        self.current_operation = {
            "name": operation_name,
            "total_steps": total_steps,
            "current_step": 0,
            "status": "Starting...",
            "started_at": datetime.now(),
            "progress_percentage": 0
        }
        self._emit_progress()
    
    def update_step(self, step_number: int, status: str):
        """Update the current step and status."""
        if not self.current_operation:
            return
        
        self.current_operation["current_step"] = step_number
        self.current_operation["status"] = status
        self.current_operation["progress_percentage"] = int(
            (step_number / self.current_operation["total_steps"]) * 100
        )
        self._emit_progress()
    
    def complete_operation(self, final_status: str = "Complete"):
        """Mark the operation as complete."""
        if not self.current_operation:
            return
        
        self.current_operation["current_step"] = self.current_operation["total_steps"]
        self.current_operation["status"] = final_status
        self.current_operation["progress_percentage"] = 100
        self.current_operation["completed_at"] = datetime.now()
        
        # Calculate duration
        duration = (
            self.current_operation["completed_at"] - 
            self.current_operation["started_at"]
        ).total_seconds()
        self.current_operation["duration_seconds"] = round(duration, 2)
        
        self._emit_progress()
        self.current_operation = None
    
    def fail_operation(self, error_message: str):
        """Mark the operation as failed."""
        if not self.current_operation:
            return
        
        self.current_operation["status"] = f"Failed: {error_message}"
        self.current_operation["failed"] = True
        self._emit_progress()
        self.current_operation = None
    
    def get_current_progress(self) -> Optional[Dict]:
        """Get the current operation progress."""
        return self.current_operation
    
    def _emit_progress(self):
        """Emit progress to all registered callbacks."""
        if not self.current_operation:
            return
        
        # Print to console
        progress = self.current_operation
        print(f"[PROGRESS] {progress['name']}: Step {progress['current_step']}/{progress['total_steps']} - {progress['status']} ({progress['progress_percentage']}%)")
        
        # Call registered callbacks
        for callback in self.callbacks:
            try:
                callback(self.current_operation.copy())
            except Exception as e:
                print(f"[PROGRESS] Callback error: {e}")


# Global progress tracker instance
progress_tracker = ProgressTracker()


# Decorator for tracking function progress
def track_progress(operation_name: str, total_steps: int):
    """Decorator to automatically track function progress."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            progress_tracker.start_operation(operation_name, total_steps)
            try:
                result = await func(*args, **kwargs)
                progress_tracker.complete_operation()
                return result
            except Exception as e:
                progress_tracker.fail_operation(str(e))
                raise
        return wrapper
    return decorator
