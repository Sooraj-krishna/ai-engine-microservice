"""
Queue Processor

Background worker that processes bugs from the queue through the chatbot pipeline.
Handles auto-approval, execution, and result tracking.
"""

import asyncio
import threading
import time
from typing import Dict, Optional
from datetime import datetime

from bug_queue_manager import bug_queue_manager
from auto_approval_manager import auto_approval_manager
from chatbot_manager import chatbot_manager
from chatbot_executor import chatbot_executor
from notification_service import notification_service


class QueueProcessor:
    """Background worker for processing bug queue."""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.process_interval = 5  # Check queue every 5 seconds
        self.session_id = None  # Chatbot session for auto-fixes
        
        # Circuit breaker for API quota exhaustion
        self.quota_error_count = 0
        self.max_quota_errors = 3
        self.consecutive_failures = 0  # Track ANY consecutive failures
        self.max_consecutive_failures = 5  # Pause after 5 failures
        self.last_quota_error = None
        self.quota_exhausted = False
    
    def start(self):
        """Start the queue processor thread."""
        if self.running:
            print("[QUEUE_PROCESSOR] Already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        print("[QUEUE_PROCESSOR] Started background worker")
    
    def stop(self):
        """Stop the queue processor thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        
        print("[QUEUE_PROCESSOR] Stopped")
    
    def _run_loop(self):
        """Main processing loop (runs in background thread)."""
        print("[QUEUE_PROCESSOR] Processing loop started")
        
        # Create a chatbot session for auto-fixes
        session = chatbot_manager.create_session(user_id="auto_fix_system")
        self.session_id = session["session_id"]
        
        while self.running:
            try:
                if bug_queue_manager.is_paused():
                    print("[QUEUE_PROCESSOR] Queue is paused, skipping...")
                    time.sleep(self.process_interval)
                    continue
                
                # CONCURRENCY CONTROL: Only 1 bug at a time
                processing_count = bug_queue_manager.get_processing_count()
                if processing_count > 0:
                    print(f"[QUEUE_PROCESSOR] {processing_count} bug(s) currently processing, waiting...")
                    time.sleep(self.process_interval)
                    continue
                
                # QUEUE LIMITS: Check queue size before processing
                queue_status = bug_queue_manager.get_queue_status()
                queued_count = queue_status.get("queued", 0)
                
                # For now, simplified: just check if queue has items
                # The actual severity-based limits require parsing queue_items
                total_queued = queued_count
                if total_queued > 3:  # Max 3 bugs in queue at once
                    print(f"[QUEUE_PROCESSOR] Queue full ({total_queued} bugs), waiting...")
                    time.sleep(self.process_interval)
                    continue
                
                # Get next bug to process
                bug_item = bug_queue_manager.get_next_bug()
                if bug_item:
                    asyncio.run(self._process_bug(bug_item))
                else:
                    # No bugs in queue
                    time.sleep(self.process_interval)
                    
            except Exception as e:
                print(f"[QUEUE_PROCESSOR] Error in processing loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(self.process_interval)
    
    async def _process_bug(self, bug_item: Dict):
        """
        Process a single bug through the chatbot pipeline.
        
        Args:
            bug_item: Bug item from queue
        """
        bug_id = bug_item["id"]
        bug = bug_item["bug"]
        severity = bug_item["severity"]
        
        print(f"[QUEUE_PROCESSOR] Processing bug {bug_id} ({severity})")
        
        try:
            # Step 1: Check if should auto-approve
            approval_decision = auto_approval_manager.should_auto_approve(bug_item)
            
            auto_approve = approval_decision["auto_approve"]
            silent = approval_decision["silent"]
            reason = approval_decision["reason"]
            
            print(f"[QUEUE_PROCESSOR] Approval decision: auto_approve={auto_approve}, silent={silent}")
            print(f"[QUEUE_PROCESSOR] Reason: {reason}")
            
            # Step 2: Generate implementation plan via chatbot
            plan_result = await self._generate_plan(bug)
            
            if not plan_result or "error" in plan_result:
                error_msg = plan_result.get("error", "Plan generation failed") if plan_result else "Plan generation failed"
                print(f"[QUEUE_PROCESSOR] Plan generation failed: {error_msg}")
                
                # Enhanced quota error detection (catches wrapped errors)
                is_quota_error = any([
                    "429" in error_msg,
                    "quota" in error_msg.lower(),
                    "exceeded" in error_msg.lower(),
                    "retry" in error_msg.lower() and "limit" in error_msg.lower(),
                    "Plan generation failed. Please try rephrasing" in error_msg,  # Wrapped quota error
                ])
                
                if is_quota_error:
                    print(f"[QUEUE_PROCESSOR] ⚠️ Detected quota error (wrapped): {error_msg[:100]}")
                    # Requeue the bug so it's not stuck in processing
                    bug_queue_manager.requeue(bug_id)
                    self._handle_quota_error()
                    return
                
                # Track consecutive failures (ANY error type)
                self.consecutive_failures += 1
                print(f"[QUEUE_PROCESSOR] Consecutive failures: {self.consecutive_failures}/{self.max_consecutive_failures}")
                
                if self.consecutive_failures >= self.max_consecutive_failures:
                    self._emergency_pause(f"Too many consecutive failures ({self.consecutive_failures})")
                    return
                
                # RETRY LOGIC: Check if should retry or mark as failed
                retry_count = bug_item.get("retry_count", 0)
                max_retries = bug_item.get("max_retries", 3)
                
                if retry_count < max_retries:
                    # Retry
                    print(f"[QUEUE_PROCESSOR] Retrying bug {bug_id} (attempt {retry_count + 1}/{max_retries})")
                    bug_queue_manager.increment_retry(bug_id, error_msg)
                    bug_queue_manager.requeue(bug_id)
                else:
                    # Max retries reached
                    final_error = f"Failed after {max_retries} attempts. Last error: {error_msg}"
                    print(f"[QUEUE_PROCESSOR] ❌ Bug {bug_id} failed permanently: {final_error}")
                    bug_queue_manager.mark_failed(bug_id, final_error)
                
                return
            
            # SUCCESS - Reset failure counter
            self.consecutive_failures = 0
            
            plan = plan_result.get("plan")
            if not plan:
                bug_queue_manager.mark_failed(bug_id, "No plan generated")
                return
            
            print(f"[QUEUE_PROCESSOR] Plan generated successfully")
            
            # Step 3: Execute based on approval decision
            if auto_approve:
                # Auto-approve and execute
                print(f"[QUEUE_PROCESSOR] Auto-approving and executing (silent={silent})")
                
                execution_result = await self._execute_plan(plan, bug, silent)
                
                if execution_result.get("success"):
                    bug_queue_manager.mark_completed(bug_id, execution_result)
                    
                    # Log based on silent mode
                    if silent:
                        print(f"[QUEUE_PROCESSOR] ✅ Bug {bug_id} auto-fixed silently")
                    else:
                        print(f"[QUEUE_PROCESSOR] ✅ Bug {bug_id} auto-fixed (user notified)")
                        # Store notification for user
                        await self._notify_user_of_auto_fix(bug, execution_result)
                else:
                    error = execution_result.get("error", "Execution failed")
                    bug_queue_manager.mark_failed(bug_id, error)
                    print(f"[QUEUE_PROCESSOR] ❌ Bug {bug_id} execution failed: {error}")
            else:
                # Requires user approval - store for user review
                print(f"[QUEUE_PROCESSOR] Bug requires user approval - storing for user review")
                
                # Store the plan for user review
                result = {
                    "status": "pending_approval",
                    "plan": plan,
                    "reason": reason,
                    "severity": severity,
                    "bug_id": bug_id,
                    "bug": bug
                }
                
                bug_queue_manager.mark_completed(bug_id, result)
                
                # Notify user via notification system
                await self._notify_user_of_critical_bug(bug, plan, severity)
                
                print(f"[QUEUE_PROCESSOR] ⚠️ Bug {bug_id} ({severity}) requires user approval")
        
        except Exception as e:
            print(f"[QUEUE_PROCESSOR] Error processing bug {bug_id}: {e}")
            import traceback
            traceback.print_exc()
            bug_queue_manager.mark_failed(bug_id, str(e))
    
    def _create_minimal_context(self, bug: Dict) -> Dict:
        """
        Extract only essential bug data for AI to reduce token usage.
        
        BEFORE: ~1200 tokens (full bug object with verbose details)
        AFTER: ~200 tokens (essential data only)
        SAVINGS: 83% reduction!
        
        Args:
            bug: Full bug object
            
        Returns:
            Minimal context dict with only essential fields
        """
        # Extract rule_id from data if available
        bug_data = bug.get("data", {})
        rule_id = bug_data.get("rule_id", bug.get("type", "unknown"))
        
        # Build minimal context
        minimal = {
            "category": bug.get("type", "unknown"),  # accessibility, performance, etc.
            "severity": bug.get("severity", "medium"),
            "issue": rule_id,  # button-name, color-contrast, etc.
            "description": bug_data.get("description", bug.get("description", "No description")),
            "instances": bug_data.get("nodes_affected", 1),
        }
        
        # Add file information (single file or list)
        if "affected_files" in bug:
            minimal["affected_files"] = bug["affected_files"][:5]  # Limit to 5 files max
        else:
            target = bug.get("target_file", "unknown")
            minimal["affected_files"] = [target] if target != "unknown" else []
        
        # Add fix guide URL if available
        if "help_url" in bug_data:
            minimal["fix_guide"] = bug_data["help_url"]
        
        return minimal
    
    async def _notify_user_of_auto_fix(self, bug: Dict, result: Dict):
        """Store notification for user about auto-fixed bug."""
        try:
            message = f"Auto-fixed {bug.get('severity', 'unknown')} severity bug: {bug.get('description', 'N/A')[:100]}"
            await notification_service.notify(
                message=message,
                severity=bug.get("severity", "info"),
                type="auto_fix",
                data={
                    "bug": bug,
                    "pr_url": result.get("pr_url")
                }
            )
        except Exception as e:
            print(f"[QUEUE_PROCESSOR] Failed to store notification: {e}")
    
    async def _notify_user_of_critical_bug(self, bug: Dict, plan: Dict, severity: str):
        """Notify user about critical/high severity bug requiring approval."""
        try:
            message = f"🚨 {severity.upper()} severity bug requires your attention: {bug.get('description', 'N/A')[:100]}"
            await notification_service.notify(
                message=message,
                severity=severity,
                type="critical_bug",
                data={
                    "bug": bug,
                    "plan": plan,
                    "requires_approval": True
                }
            )
        except Exception as e:
            print(f"[QUEUE_PROCESSOR] Failed to store critical notification: {e}")
    
    async def _generate_plan(self, bug: Dict) -> Dict:
        """
        Generate implementation plan for bug fix.
        
        Args:
            bug: Bug details (full object)
            
        Returns:
            Plan result from chatbot
        """
        try:
            # Create minimal context to save tokens
            minimal_bug = self._create_minimal_context(bug)
            
            # Build concise message
            files_str = ", ".join(minimal_bug["affected_files"][:3])  # Max 3 files in message
            if len(minimal_bug["affected_files"]) > 3:
                files_str += f" and {len(minimal_bug['affected_files']) - 3} more"
            
            message = (
                f"Fix this {minimal_bug['category']} issue:\n\n"
                f"**Problem**: {minimal_bug['issue']}\n"
                f"**Description**: {minimal_bug['description']}\n"
                f"**Severity**: {minimal_bug['severity']}\n"
                f"**Affected files**: {files_str}\n"
                f"**Instances**: {minimal_bug['instances']}\n"
            )
            
            # Add fix guide if available
            if "fix_guide" in minimal_bug:
                message += f"**Reference**: {minimal_bug['fix_guide']}\n"
            
            print(f"[QUEUE_PROCESSOR] Generating plan with minimal context ({len(message)} chars)")
            
            # Call chatbot to generate plan
            from chatbot_manager import chatbot_manager
            result = await chatbot_manager.process_message(self.session_id, message)
            return result
            
        except Exception as e:
            print(f"[QUEUE_PROCESSOR] Plan generation error: {e}")
            return {"error": str(e)}
    
    async def _execute_plan(self, plan: Dict, bug: Dict, silent: bool = False) -> Dict:
        """
        Execute the implementation plan.
        
        Args:
            plan: Implementation plan
            bug: Original bug
            silent: Whether to execute silently
            
        Returns:
            Execution result
        """
        try:
            # Prepare change data for executor
            change_data = {
                "plan": plan,
                "intent": "bug_fix",
                "user_request": bug.get("description", ""),
                "silent": silent
            }
            
            # Execute via chatbot executor
            result = await chatbot_executor.execute_change(change_data)
            
            return result
            
        except Exception as e:
            print(f"[QUEUE_PROCESSOR] Execution error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _handle_quota_error(self):
        """Handle API quota exhaustion - circuit breaker pattern."""
        self.quota_error_count += 1
        self.last_quota_error = datetime.now()
        
        print(f"[QUEUE_PROCESSOR] ⚠️ Quota error detected ({self.quota_error_count}/{self.max_quota_errors})")
        
        if self.quota_error_count >= self.max_quota_errors:
            print(f"[QUEUE_PROCESSOR] 🛑 CIRCUIT BREAKER TRIGGERED - Pausing queue due to quota exhaustion")
            self.quota_exhausted = True
            self.running = False
            
            # Pause the queue
            bug_queue_manager.pause()
            auto_approval_manager.emergency_pause()
            
            # Notify user
            try:
                notification_service.notify(
                    message="🚨 Queue processor paused due to API quota exhaustion. Please check your Gemini API limits.",
                    severity="critical",
                    type="quota_exhausted",
                    data={
                        "quota_errors": self.quota_error_count,
                        "last_error": self.last_quota_error.isoformat(),
                        "action_required": "Review quota limits and resume queue manually"
                    }
                )
            except Exception as e:
                print(f"[QUEUE_PROCESSOR] Failed to send quota notification: {e}")
    
    def reset_quota_errors(self):
        """Reset the quota error counter (call this after resolving quota issues)."""
        self.quota_error_count = 0
        self.quota_exhausted = False
        self.last_quota_error = None
        self.consecutive_failures = 0  # Also reset consecutive failures
        print("[QUEUE_PROCESSOR] ✅ Quota error counter reset")
    
    def _emergency_pause(self, reason: str):
        """Emergency pause for non-quota consecutive failures."""
        print(f"[QUEUE_PROCESSOR] 🛑 EMERGENCY PAUSE: {reason}")
        self.running = False
        
        # Pause the queue
        bug_queue_manager.pause()
        auto_approval_manager.emergency_pause()
        
        # Notify user
        try:
            notification_service.notify(
                message=f"🚨 Queue processor paused: {reason}",
                severity="critical",
                type="emergency_pause",
                data={
                    "reason": reason,
                    "consecutive_failures": self.consecutive_failures,
                    "action_required": "Review logs and resume queue manually"
                }
            )
        except Exception as e:
            print(f"[QUEUE_PROCESSOR] Failed to send emergency pause notification: {e}")
    
    def _pause_for_review(self, reason: str):
        """Pause queue for user review (e.g., too many high-priority bugs)."""
        print(f"[QUEUE_PROCESSOR] ⏸️ PAUSING FOR REVIEW: {reason}")
        bug_queue_manager.pause()
        
        try:
            notification_service.notify(
                message=f"⏸️ Queue paused for review: {reason}",
                severity="warning",
                type="queue_paused",
                data={"reason": reason}
            )
        except Exception as e:
            print(f"[QUEUE_PROCESSOR] Failed to send pause notification: {e}")
    
    def get_status(self) -> Dict:
        """Get processor status."""
        return {
            "running": self.running,
            "session_id": self.session_id,
            "process_interval": self.process_interval,
            "quota_exhausted": self.quota_exhausted,
            "quota_error_count": self.quota_error_count,
            "last_quota_error": self.last_quota_error.isoformat() if self.last_quota_error else None
        }


# Global instance
queue_processor = QueueProcessor()
