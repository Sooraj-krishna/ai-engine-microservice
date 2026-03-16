"""
Chat Storage Module

Handles persistent storage for chat sessions, messages, and pending changes.
Uses JSON file-based storage for simplicity and consistency with existing feature manager.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid


class ChatStorage:
    """Manages storage of chat sessions, messages, and pending changes."""
    
    def __init__(self, base_dir: str = "data/chatbot_sessions"):
        """
        Initialize chat storage.
        
        Args:
            base_dir: Base directory for chat data storage
        """
        self.base_dir = Path(base_dir)
        self.sessions_dir = self.base_dir / "sessions"
        self.pending_changes_dir = self.base_dir / "pending_changes"
        self.metadata_file = self.base_dir / "session_metadata.json"
        
        # Create directories if they don't exist
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.pending_changes_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metadata file if it doesn't exist
        if not self.metadata_file.exists():
            self._save_metadata({
                "sessions": {},
                "total_sessions": 0,
                "last_updated": datetime.now().isoformat()
            })
    
    def _save_metadata(self, metadata: Dict) -> None:
        """Save metadata index."""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_metadata(self) -> Dict:
        """Load metadata index."""
        with open(self.metadata_file, 'r') as f:
            return json.load(f)
    
    def create_session(self, user_id: str = "default") -> Dict:
        """
        Create a new chat session.
        
        Args:
            user_id: User identifier (default for single-user system)
            
        Returns:
            New session data
        """
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "conversation_history": [],
            "context": {
                "current_intent": None,
                "pending_changes": [],
                "related_features": []
            },
            "metadata": {
                "message_count": 0,
                "last_intent": None
            }
        }
        
        # Save session
        self.save_session(session_data)
        
        # Update metadata
        metadata = self._load_metadata()
        metadata["sessions"][session_id] = {
            "user_id": user_id,
            "created_at": session_data["created_at"],
            "updated_at": session_data["updated_at"],
            "message_count": 0
        }
        metadata["total_sessions"] = len(metadata["sessions"])
        metadata["last_updated"] = datetime.now().isoformat()
        self._save_metadata(metadata)
        
        print(f"[CHAT_STORAGE] Created new session: {session_id}")
        return session_data
    
    def save_session(self, session_data: Dict) -> None:
        """
        Save session data to file.
        
        Args:
            session_data: Complete session data to save
        """
        session_id = session_data["session_id"]
        session_file = self.sessions_dir / f"session_{session_id}.json"
        
        # Update timestamp
        session_data["updated_at"] = datetime.now().isoformat()
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Update metadata
        metadata = self._load_metadata()
        if session_id in metadata["sessions"]:
            metadata["sessions"][session_id]["updated_at"] = session_data["updated_at"]
            metadata["sessions"][session_id]["message_count"] = len(session_data["conversation_history"])
            metadata["last_updated"] = datetime.now().isoformat()
            self._save_metadata(metadata)
    
    def load_session(self, session_id: str) -> Optional[Dict]:
        """
        Load session data from file.
        
        Args:
            session_id: Session ID to load
            
        Returns:
            Session data if found, None otherwise
        """
        session_file = self.sessions_dir / f"session_{session_id}.json"
        
        if not session_file.exists():
            print(f"[CHAT_STORAGE] Session not found: {session_id}")
            return None
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        return session_data
    
    def get_all_sessions(self, user_id: Optional[str] = None) -> List[Dict]:
        """
        Get all sessions, optionally filtered by user_id.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of session summaries
        """
        metadata = self._load_metadata()
        sessions = []
        
        for session_id, session_info in metadata["sessions"].items():
            if user_id is None or session_info["user_id"] == user_id:
                sessions.append({
                    "session_id": session_id,
                    **session_info
                })
        
        # Sort by updated_at (most recent first)
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        session_file = self.sessions_dir / f"session_{session_id}.json"
        
        if not session_file.exists():
            return False
        
        # Delete session file
        session_file.unlink()
        
        # Update metadata
        metadata = self._load_metadata()
        if session_id in metadata["sessions"]:
            del metadata["sessions"][session_id]
            metadata["total_sessions"] = len(metadata["sessions"])
            metadata["last_updated"] = datetime.now().isoformat()
            self._save_metadata(metadata)
        
        print(f"[CHAT_STORAGE] Deleted session: {session_id}")
        return True
    
    def add_message(self, session_id: str, role: str, content: str, 
                    metadata: Optional[Dict] = None) -> bool:
        """
        Add a message to a session.
        
        Args:
            session_id: Session ID
            role: Message role ('user' or 'assistant')
            content: Message content
            metadata: Optional metadata for the message
            
        Returns:
            True if successful, False if session not found
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        session_data["conversation_history"].append(message)
        session_data["metadata"]["message_count"] = len(session_data["conversation_history"])
        
        self.save_session(session_data)
        return True
    
    def save_pending_change(self, session_id: str, change_data: Dict) -> str:
        """
        Save a pending change that requires user approval.
        
        Args:
            session_id: Session ID this change belongs to
            change_data: Change data including plan, code, preview, etc.
            
        Returns:
            Change ID
        """
        change_id = str(uuid.uuid4())
        change_file = self.pending_changes_dir / f"change_{change_id}.json"
        
        full_change_data = {
            "change_id": change_id,
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "status": "pending",  # pending, applied, rejected
            **change_data
        }
        
        with open(change_file, 'w') as f:
            json.dump(full_change_data, f, indent=2)
        
        # Update session context
        session_data = self.load_session(session_id)
        if session_data:
            session_data["context"]["pending_changes"].append(change_id)
            self.save_session(session_data)
        
        print(f"[CHAT_STORAGE] Saved pending change: {change_id}")
        return change_id
    
    def get_pending_change(self, change_id: str) -> Optional[Dict]:
        """
        Get pending change data.
        
        Args:
            change_id: Change ID
            
        Returns:
            Change data if found, None otherwise
        """
        change_file = self.pending_changes_dir / f"change_{change_id}.json"
        
        if not change_file.exists():
            return None
        
        with open(change_file, 'r') as f:
            return json.load(f)
    
    def get_session_pending_changes(self, session_id: str) -> List[Dict]:
        """
        Get all pending changes for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of pending changes
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return []
        
        pending_changes = []
        for change_id in session_data["context"]["pending_changes"]:
            change_data = self.get_pending_change(change_id)
            if change_data and change_data["status"] == "pending":
                pending_changes.append(change_data)
        
        return pending_changes
    
    def update_change_status(self, change_id: str, status: str, 
                            notes: Optional[str] = None) -> bool:
        """
        Update the status of a pending change.
        
        Args:
            change_id: Change ID
            status: New status ('applied', 'rejected')
            notes: Optional notes about the status change
            
        Returns:
            True if successful, False if change not found
        """
        change_data = self.get_pending_change(change_id)
        if not change_data:
            return False
        
        change_data["status"] = status
        change_data["updated_at"] = datetime.now().isoformat()
        if notes:
            change_data["status_notes"] = notes
        
        change_file = self.pending_changes_dir / f"change_{change_id}.json"
        with open(change_file, 'w') as f:
            json.dump(change_data, f, indent=2)
        
        print(f"[CHAT_STORAGE] Updated change {change_id} status to: {status}")
        return True


# Global instance
chat_storage = ChatStorage()
