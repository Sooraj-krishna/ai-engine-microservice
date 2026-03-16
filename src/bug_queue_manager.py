"""
Bug Queue Manager

Manages the priority queue of bugs to be processed through the chatbot pipeline.
Handles rate limiting, prioritization, and status tracking.
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from collections import deque
import threading
import time
import shutil


class BugQueueManager:
    """Manages bug queue with priority and status tracking."""
    
    def __init__(self, queue_dir: str = "data/bug_queue"):
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        
        self.queue_file = self.queue_dir / "bug_queue.json"
        self.processing_file = self.queue_dir / "processing.json"
        self.detected_file = self.queue_dir / "detected_bugs.json"  # NEW: Detected but not approved
        
        # In-memory queue for performance
        self.queue = self._load_queue()
        self.processing = self._load_processing()
        self.detected_bugs = self._load_detected_bugs()  # NEW: Load detected bugs
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
        # Rate limiting
        self.max_concurrent = 1  # Max bugs processing at once (strict 1-at-a-time)
        self.max_queued = 3  # Max bugs that can be approved/queued at once
        self.paused = False
        self.last_sync = 0
        self.last_mtimes = {}
    
    def _has_file_changed(self, file_path: Path) -> bool:
        """Check if file has changed since last read."""
        if not file_path.exists():
            return False
        try:
            mtime = file_path.stat().st_mtime
            last_mtime = self.last_mtimes.get(str(file_path), 0)
            if mtime > last_mtime:
                self.last_mtimes[str(file_path)] = mtime
                return True
            return False
        except OSError:
            return False

    def _sync_with_disk(self):
        """Reload data from disk if files have changed."""
        if self._has_file_changed(self.queue_file):
            self.queue = self._load_queue()
            
        if self._has_file_changed(self.processing_file):
            self.processing = self._load_processing()
            
        if self._has_file_changed(self.detected_file):
            self.detected_bugs = self._load_detected_bugs()
    
    def _robust_read(self, file_path: Path, default_value=None) -> any:
        """Read a JSON file robustly with retries."""
        if default_value is None:
            default_value = []
            
        if not file_path.exists():
            return default_value
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # File might be partially written or empty
                if attempt == max_retries - 1:
                    print(f"[BUG_QUEUE] JSON decode error reading {file_path}, returning default")
                    return default_value
                time.sleep(0.1)
            except Exception as e:
                print(f"[BUG_QUEUE] Error reading {file_path}: {e}")
                if attempt == max_retries - 1:
                    return default_value
                time.sleep(0.1)
        return default_value

    def _atomic_write(self, file_path: Path, data: any):
        """Write JSON data atomically using a temp file."""
        temp_file = file_path.with_suffix('.tmp')
        try:
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
                f.flush()
                
            # Atomic rename
            os.replace(temp_file, file_path)
        except Exception as e:
            print(f"[BUG_QUEUE] Error writing to {file_path}: {e}")
            if temp_file.exists():
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def add_bugs(self, bugs: Dict[str, List[Dict]]) -> Dict:
        """
        Add classified bugs to the queue.
        
        Args:
            bugs: Dictionary mapping severity to list of bugs
            
        Returns:
            Summary of added bugs
        """
        with self.lock:
            total_added = 0
            
            # Add bugs in priority order: critical > high > medium > low
            for severity in ["critical", "high", "medium", "low"]:
                bug_list = bugs.get(severity, [])
                
                for bug in bug_list:
                    bug_id = self._generate_bug_id()
                    
                    queue_item = {
                        "id": bug_id,
                        "bug": bug,
                        "severity": severity,
                        "requires_approval": bug.get("requires_approval", False),
                        "status": "queued",  # queued, approved, processing, completed, failed
                        "added_at": datetime.now().isoformat(),
                        "processing_started_at": None,
                        "completed_at": None,
                        "error": None,
                        "retry_count": 0,  # Track retry attempts
                        "max_retries": 3,  # Max attempts before marking as failed
                        "last_error": None,  # Last error message
                        "progress": {
                            "stage": "queued",
                            "percentage": 0,
                            "current_step": "Waiting for approval...",
                            "started_at": None,
                            "pr_url": None,
                            "stages": {
                                "plan_generation": {"status": "pending", "started_at": None, "completed_at": None},
                                "validation": {"status": "pending", "started_at": None, "completed_at": None},
                                "execution": {"status": "pending", "started_at": None, "completed_at": None},
                                "git_push": {"status": "pending", "started_at": None, "completed_at": None}
                            }
                        }
                    }
                    
                    self.queue.append(queue_item)
                    total_added += 1
            
            # Save to disk
            self._save_queue()
            
            print(f"[BUG_QUEUE] Added {total_added} bugs to queue")
            print(f"[BUG_QUEUE] Current queue size: {len(self.queue)}")
            
            return {
                "total_added": total_added,
                "queue_size": len(self.queue),
                "processing_count": len(self.processing)
            }
    
    def add_detected_bugs(self, bugs: Dict[str, List[Dict]]) -> Dict:
        """Add detected bugs (awaiting user approval), NOT to processing queue."""
        with self.lock:
            total_added = 0
            for severity, bug_list in bugs.items():
                for bug in bug_list:
                    bug_id = f"bug_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                    detected_item = {
                        "id": bug_id, "bug": bug, "severity": severity,
                        "requires_approval": True, "status": "detected",
                        "detected_at": datetime.now().isoformat(),
                        "approved_at": None, "processing_started_at": None,
                        "completed_at": None, "error": None
                    }
                    self.detected_bugs.append(detected_item)
                    total_added += 1
            self._save_detected_bugs()
            print(f"[BUG_QUEUE] Added {total_added} bugs to detection list (awaiting approval)")
            return {"total_detected": total_added, "awaiting_approval": len(self.detected_bugs)}
    
    def get_detected_bugs(self) -> List[Dict]:
        """Get all detected bugs awaiting approval."""
        self._sync_with_disk()
        with self.lock:
            return [b for b in self.detected_bugs if b.get("status") == "detected"]
    
    def approve_bug_to_queue(self, bug_id: str) -> Dict:
        """Approve a detected bug and move it to processing queue (max 3)."""
        self._sync_with_disk()
        with self.lock:
            current_queued = len([b for b in self.queue if b.get("status") == "queued"])
            if current_queued >= self.max_queued:
                return {"success": False, "error": f"Queue full: {current_queued}/{self.max_queued} bugs queued"}
            bug_item = None
            for i, detected in enumerate(self.detected_bugs):
                if detected["id"] == bug_id and detected.get("status") == "detected":
                    bug_item = self.detected_bugs.pop(i)
                    break
            if not bug_item:
                return {"success": False, "error": "Bug not found or already approved"}
            bug_item["status"] = "queued"
            bug_item["approved_at"] = datetime.now().isoformat()
            bug_item["requires_approval"] = False
            
            # Initialize progress state for UI
            bug_item["progress"] = {
                "stage": "queued",
                "current_step": "Waiting to start processing...",
                "percentage": 0,
                "stages": {
                    "plan_generation": {"status": "pending"},
                    "validation": {"status": "pending"},
                    "execution": {"status": "pending"},
                    "git_push": {"status": "pending"}
                }
            }
            
            self.queue.append(bug_item)
            self._save_detected_bugs()
            self._save_queue()
            print(f"[BUG_QUEUE] Bug {bug_id} approved and queued ({current_queued + 1}/{self.max_queued})")
            return {"success": True, "bug_id": bug_id, "queued_count": current_queued + 1}
    
    def get_next_bug(self) -> Optional[Dict]:
        """
        Get the next bug from the queue (highest priority first).
        
        Returns:
            Bug item or None if queue is empty or paused
        """
        self._sync_with_disk()
        with self.lock:
            if self.paused:
                print("[BUG_QUEUE] Queue is paused, not returning bugs")
                return None
            
            if len(self.processing) >= self.max_concurrent:
                print(f"[BUG_QUEUE] Max concurrent limit reached ({self.max_concurrent})")
                return None
            
            if not self.queue:
                return None
            
            # Get next bug (already in priority order)
            bug_item = self.queue.popleft()
            
            # Move to processing
            bug_item["status"] = "processing"
            bug_item["processing_started_at"] = datetime.now().isoformat()
            bug_item["requires_approval"] = False  # Already approved, no need to ask again
            
            self.processing[bug_item["id"]] = bug_item
            
            # Save state
            self._save_queue()
            self._save_processing()
            
            print(f"[BUG_QUEUE] Retrieved bug {bug_item['id']} ({bug_item['severity']})")
            
            return bug_item
    
    def mark_completed(self, bug_id: str, result: Dict):
        """
        Mark a bug as completed.
        
        Args:
            bug_id: Bug ID
            result: Execution result
        """
        with self.lock:
            if bug_id not in self.processing:
                print(f"[BUG_QUEUE] Bug {bug_id} not found in processing")
                return
            
            bug_item = self.processing.pop(bug_id)
            bug_item["status"] = "completed"
            bug_item["completed_at"] = datetime.now().isoformat()
            bug_item["result"] = result
            
            # Save to history
            self._save_to_history(bug_item)
            
            # Update processing state
            self._save_processing()
            
            print(f"[BUG_QUEUE] Bug {bug_id} marked as completed")
    
    def mark_failed(self, bug_id: str, error: str):
        """
        Mark a bug as failed.
        
        Args:
            bug_id: Bug ID
            error: Error message
        """
        with self.lock:
            if bug_id not in self.processing:
                print(f"[BUG_QUEUE] Bug {bug_id} not found in processing")
                return
            
            bug_item = self.processing.pop(bug_id)
            bug_item["status"] = "failed"
            bug_item["completed_at"] = datetime.now().isoformat()
            bug_item["error"] = error
            
            # Save to history
            self._save_to_history(bug_item)
            
            # Update processing state
            self._save_processing()
            
            print(f"[BUG_QUEUE] Bug {bug_id} marked as failed: {error}")
    
    def get_queue_status(self) -> Dict:
        """
        Get current queue status.
        
        Returns:
            Status dictionary
        """
        self._sync_with_disk()
        with self.lock:
            return {
                "queued": len(self.queue),
                "processing": len(self.processing),
                "paused": self.paused,
                "max_concurrent": self.max_concurrent,
                "queue_items": list(self.queue),
                "processing_items": list(self.processing.values())
            }
    
    def pause(self):
        """Pause queue processing."""
        with self.lock:
            self.paused = True
            print("[BUG_QUEUE] Queue paused")
    
    def is_paused(self) -> bool:
        """Check if queue is currently paused."""
        with self.lock:
            return self.paused
    
    def resume(self):
        """Resume queue processing."""
        with self.lock:
            self.paused = False
            print("[BUG_QUEUE] Queue resumed")
    
    def clear_queue(self):
        """Clear all queued bugs (not processing ones)."""
        with self.lock:
            cleared_count = len(self.queue)
            self.queue.clear()
            self._save_queue()
            print(f"[BUG_QUEUE] Cleared {cleared_count} queued bugs")
            return cleared_count
    
    def _generate_bug_id(self) -> str:
        """Generate unique bug ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"bug_{timestamp}"
    
    def _load_queue(self) -> deque:
        """Load queue from disk."""
        data = self._robust_read(self.queue_file, default_value=[])
        return deque(data)
    
    def _save_queue(self):
        """Save queue to disk."""
        self._atomic_write(self.queue_file, list(self.queue))
    
    def _load_processing(self) -> Dict:
        """Load processing items from disk."""
        data = self._robust_read(self.processing_file, default_value={})
        if isinstance(data, list):
             print("[BUG_QUEUE] Warning: processing.json contains a list, resetting to dict")
             return {}
        return data
    
    def _save_processing(self):
        """Save processing items to disk."""
        self._atomic_write(self.processing_file, self.processing)
    
    def _load_detected_bugs(self) -> List[Dict]:
        """Load detected bugs from disk."""
        detected = self._robust_read(self.detected_file, default_value=[])
        # Silent load to avoid log spam
        return detected
    
    def _save_detected_bugs(self):
        """Save detected bugs to disk."""
        self._atomic_write(self.detected_file, self.detected_bugs)
    
    def _save_to_history(self, bug_item: Dict):
        """Save completed/failed bug to history."""
        history_file = self.queue_dir / "history.json"
        
        try:
            history = []
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)
            
            history.append(bug_item)
            
            # Keep last 1000 items
            if len(history) > 1000:
                history = history[-1000:]
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"[BUG_QUEUE] Error saving to history: {e}")
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """
        Get bug processing history.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of historical bug items
        """
        history_file = self.queue_dir / "history.json"
        
        history = self._robust_read(history_file, default_value=[])
        return history[-limit:]
    
    def increment_retry(self, bug_id: str, error_msg: str):
        """
        Increment retry count for a bug and store the error.
        
        Args:
            bug_id: Bug identifier
            error_msg: Error message from failure
        """
        with self.lock:
            # Check if bug is in processing (shouldn't be, but for safety)
            if bug_id in self.processing:
                bug_item = self.processing.pop(bug_id)
                self._save_processing()
            else:
                # Find in queue (convert to list to remove by index)
                bug_item = None
                queue_list = list(self.queue)
                for i, item in enumerate(queue_list):
                    if item["id"] == bug_id:
                        bug_item = queue_list.pop(i)
                        self.queue = deque(queue_list)  # Rebuild deque
                        break
            
            if bug_item:
                bug_item["retry_count"] = bug_item.get("retry_count", 0) + 1
                bug_item["last_error"] = error_msg
                bug_item["status"] = "queued"  # Put back in queue for retry
                bug_item["processing_started_at"] = None # Reset processing start time
                
                # Re-add to queue, maintaining priority if possible, or just append
                # For simplicity, append for now, assuming priority is handled by get_next_bug
                self.queue.append(bug_item)
                self._save_queue()
                print(f"[BUG_QUEUE] Bug {bug_id} retry count: {bug_item['retry_count']}/{bug_item.get('max_retries', 3)}")
            else:
                print(f"[BUG_QUEUE] Bug {bug_id} not found in processing or queue for retry")
    
    def requeue(self, bug_id: str):
        """
        Requeue a bug for retry (reset to queued status).
        
        Args:
            bug_id: Bug identifier
        """
        with self.lock:
            # Check if bug is in processing (shouldn't be, but for safety)
            if bug_id in self.processing:
                bug_item = self.processing.pop(bug_id)
                self._save_processing()
            else:
                # Find in queue (convert to list to remove by index)
                bug_item = None
                queue_list = list(self.queue)
                for i, item in enumerate(queue_list):
                    if item["id"] == bug_id:
                        bug_item = queue_list.pop(i)
                        self.queue = deque(queue_list)  # Rebuild deque
                        break
            
            if bug_item:
                bug_item["status"] = "queued"
                bug_item["processing_started_at"] = None
                bug_item["last_error"] = None # Clear last error on explicit requeue
                
                # Re-add to queue
                self.queue.append(bug_item)
                self._save_queue()
                print(f"[BUG_QUEUE] Bug {bug_id} requeued for retry")
            else:
                print(f"[BUG_QUEUE] Bug {bug_id} not found in processing or queue for requeue")
    
    def get_processing_count(self) -> int:
        """
        Get count of bugs currently being processed.
        
        Returns:
            Number of bugs with status 'processing'
        """
        with self.lock:
            return len(self.processing)
    
    def update_progress(self, bug_id: str, stage: str, percentage: int, step_description: str, pr_url: str = None):
        """
        Update progress for a bug being processed.
        
        Args:
            bug_id: Bug ID
            stage: Current stage (plan_generation, validation, execution, git_push, completed)
            percentage: Progress percentage (0-100)
            step_description: Human-readable description of current step
            pr_url: Optional PR URL when available
        """
        with self.lock:
            # Check if bug is in processing
            if bug_id not in self.processing:
                # Maybe it's still in queue and was just approved
                for item in self.queue:
                    if item["id"] == bug_id:
                        self._update_progress_item(item, stage, percentage, step_description, pr_url)
                        self._save_queue()
                        return
                print(f"[BUG_QUEUE] Bug {bug_id} not found in processing or queue")
                return
            
            bug_item = self.processing[bug_id]
            self._update_progress_item(bug_item, stage, percentage, step_description, pr_url)
            self._save_processing()
            
            print(f"[BUG_QUEUE] Progress updated for {bug_id}: {stage} ({percentage}%) - {step_description}")
    
    def _update_progress_item(self, item: Dict, stage: str, percentage: int, step_description: str, pr_url: str = None):
        """Update progress fields in a bug item."""
        if "progress" not in item:
            # Initialize progress if missing
            item["progress"] = {
                "stage": "queued",
                "percentage": 0,
                "current_step": "",
                "started_at": None,
                "pr_url": None,
                "stages": {
                    "plan_generation": {"status": "pending", "started_at": None, "completed_at": None},
                    "validation": {"status": "pending", "started_at": None, "completed_at": None},
                    "execution": {"status": "pending", "started_at": None, "completed_at": None},
                    "git_push": {"status": "pending", "started_at": None, "completed_at": None}
                }
            }
        
        progress = item["progress"]
        progress["stage"] = stage
        progress["percentage"] = percentage
        progress["current_step"] = step_description
        
        if pr_url:
            progress["pr_url"] = pr_url
        
        # Update stage status
        if stage in progress["stages"]:
            if progress["stages"][stage]["status"] == "pending":
                progress["stages"][stage]["status"] = "in_progress"
                progress["stages"][stage]["started_at"] = datetime.now().isoformat()
                if progress["started_at"] is None:
                    progress["started_at"] = datetime.now().isoformat()
            
            # If moving to next stage, mark previous as completed
            if percentage == 100 or stage == "completed":
                progress["stages"][stage]["status"] = "completed"
                progress["stages"][stage]["completed_at"] = datetime.now().isoformat()
    
    def get_progress(self, bug_id: str) -> Optional[Dict]:
        """
        Get progress for a specific bug.
        
        Args:
            bug_id: Bug ID
            
        Returns:
            Progress dictionary or None if not found
        """
        self._sync_with_disk()
        with self.lock:
            # Check processing
            if bug_id in self.processing:
                bug_item = self.processing[bug_id]
                return {
                    "bug_id": bug_id,
                    "severity": bug_item.get("severity"),
                    "status": bug_item.get("status"),
                    "progress": bug_item.get("progress", {}),
                    "bug": bug_item.get("bug", {})
                }
            
            # Check queue
            for item in self.queue:
                if item["id"] == bug_id:
                    return {
                        "bug_id": bug_id,
                        "severity": item.get("severity"),
                        "status": item.get("status"),
                        "progress": item.get("progress", {}),
                        "bug": item.get("bug", {})
                    }
            
            # Check history
            history = self.get_history(limit=1000)
            for item in reversed(history):
                if item["id"] == bug_id:
                    return {
                        "bug_id": bug_id,
                        "severity": item.get("severity"),
                        "status": item.get("status"),
                        "progress": item.get("progress", {}),
                        "bug": item.get("bug", {}),
                        "result": item.get("result", {})
                    }
            
            return None
    
    def get_in_progress_bugs(self) -> List[Dict]:
        """
        Get all bugs currently being processed.
        
        Returns:
            List of bugs with their progress
        """
        self._sync_with_disk()
        with self.lock:
            in_progress = []
            
            for bug_id, bug_item in self.processing.items():
                in_progress.append({
                    "bug_id": bug_id,
                    "severity": bug_item.get("severity"),
                    "status": bug_item.get("status"),
                    "progress": bug_item.get("progress", {}),
                    "bug": bug_item.get("bug", {}),
                    "processing_started_at": bug_item.get("processing_started_at")
                })
            
            return in_progress


# Global instance
bug_queue_manager = BugQueueManager()
