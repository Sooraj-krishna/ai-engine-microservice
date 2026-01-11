"""
Feature Store - SQLite database for tracking competitor features over time

Tracks:
- Feature detection history
- First seen / last seen timestamps
- Evidence and confidence scores
- Change detection
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class FeatureStore:
    """Manages feature storage and history in SQLite."""
    
    def __init__(self, db_path: str = "data/competitive_features.db"):
        """Initialize feature store with SQLite database."""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Competitor features table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS competitor_features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    competitor_url TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    feature_category TEXT NOT NULL,
                    first_seen TIMESTAMP NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    page_type TEXT,
                    confidence_score REAL,
                    evidence TEXT,
                    priority_score INTEGER DEFAULT 50,
                    UNIQUE(competitor_url, feature_name)
                )
            """)
            
            # Feature history table (tracks all detections)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feature_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    competitor_url TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    detected_at TIMESTAMP NOT NULL,
                    confidence_score REAL,
                    evidence TEXT,
                    page_snapshot_hash TEXT
                )
            """)
            
            # Your website features inventory
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS your_features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feature_name TEXT UNIQUE NOT NULL,
                    feature_category TEXT,
                    implemented BOOLEAN DEFAULT 0,
                    priority INTEGER DEFAULT 50,
                    notes TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Feature changes (for alerts)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feature_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    competitor_url TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                )
            """)
            
            conn.commit()
    
    def save_feature(self, competitor_url: str, feature_name: str, 
                    category: str, confidence: float, evidence: List[str],
                    page_type: str = "unknown", priority: int = 50):
        """
        Save or update a feature detection.
        
        Args:
            competitor_url: URL of competitor site
            feature_name: Name of the detected feature
            category: Feature category
            confidence: Confidence score (0-1)
            evidence: List of evidence strings
            page_type: Type of page where feature was found
            priority: Priority score (0-100)
        """
        now = datetime.now()
        evidence_json = json.dumps(evidence)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if feature already exists
            cursor.execute("""
                SELECT id, first_seen FROM competitor_features
                WHERE competitor_url = ? AND feature_name = ?
            """, (competitor_url, feature_name))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing feature
                feature_id, first_seen = existing
                cursor.execute("""
                    UPDATE competitor_features
                    SET last_seen = ?,
                        confidence_score = ?,
                        evidence = ?,
                        page_type = ?,
                        priority_score = ?
                    WHERE id = ?
                """, (now, confidence, evidence_json, page_type, priority, feature_id))
            else:
                # Insert new feature
                cursor.execute("""
                    INSERT INTO competitor_features
                    (competitor_url, feature_name, feature_category, first_seen, 
                     last_seen, page_type, confidence_score, evidence, priority_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (competitor_url, feature_name, category, now, now, 
                      page_type, confidence, evidence_json, priority))
                
                # Log as new feature in changes
                cursor.execute("""
                    INSERT INTO feature_changes
                    (competitor_url, feature_name, change_type, details)
                    VALUES (?, ?, 'new_feature', ?)
                """, (competitor_url, feature_name, evidence_json))
            
            # Always add to history
            cursor.execute("""
                INSERT INTO feature_history
                (competitor_url, feature_name, detected_at, confidence_score, evidence)
                VALUES (?, ?, ?, ?, ?)
            """, (competitor_url, feature_name, now, confidence, evidence_json))
            
            conn.commit()
    
    def get_competitor_features(self, competitor_url: str) -> List[Dict]:
        """Get all features for a competitor."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM competitor_features
                WHERE competitor_url = ?
                ORDER BY priority_score DESC, feature_category
            """, (competitor_url,))
            
            features = []
            for row in cursor.fetchall():
                features.append({
                    "feature_name": row["feature_name"],
                    "category": row["feature_category"],
                    "confidence": row["confidence_score"],
                    "evidence": json.loads(row["evidence"]),
                    "first_seen": row["first_seen"],
                    "last_seen": row["last_seen"],
                    "priority": row["priority_score"]
                })
            
            return features
    
    def get_all_competitor_features(self) -> Dict[str, List[Dict]]:
        """Get features grouped by competitor."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT competitor_url FROM competitor_features
            """)
            
            result = {}
            for row in cursor.fetchall():
                url = row["competitor_url"]
                result[url] = self.get_competitor_features(url)
            
            return result
    
    def save_your_features(self, features: List[str], category: str = "General"):
        """Save your website's features for comparison."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for feature in features:
                cursor.execute("""
                    INSERT OR IGNORE INTO your_features
                    (feature_name, feature_category, implemented)
                    VALUES (?, ?, 1)
                """, (feature, category))
            
            conn.commit()
    
    def get_your_features(self) -> List[str]:
        """Get list of your implemented features."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT feature_name FROM your_features
                WHERE implemented = 1
            """)
            
            return [row[0] for row in cursor.fetchall()]
    
    def get_feature_gaps(self) -> List[Dict]:
        """
        Get features that competitors have but you don't.
        Returns gaps with adoption rate and priority.
        """
        your_features = set(self.get_your_features())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all competitor features with count
            cursor.execute("""
                SELECT 
                    feature_name,
                    feature_category,
                    COUNT(DISTINCT competitor_url) as competitor_count,
                    AVG(confidence_score) as avg_confidence,
                    MAX(priority_score) as max_priority,
                    MIN(first_seen) as first_detected
                FROM competitor_features
                GROUP BY feature_name, feature_category
                ORDER BY competitor_count DESC, max_priority DESC
            """)
            
            gaps = []
            for row in cursor.fetchall():
                feature_name = row["feature_name"]
                
                # Skip if you already have it
                if feature_name in your_features:
                    continue
                
                # Get competitors who have this feature
                cursor.execute("""
                    SELECT competitor_url, evidence
                    FROM competitor_features
                    WHERE feature_name = ?
                """, (feature_name,))
                
                competitors_with = []
                all_evidence = []
                for comp_row in cursor.fetchall():
                    competitors_with.append(comp_row["competitor_url"])
                    all_evidence.extend(json.loads(comp_row["evidence"]))
                
                gaps.append({
                    "feature_name": feature_name,
                    "category": row["feature_category"],
                    "competitor_count": row["competitor_count"],
                    "avg_confidence": round(row["avg_confidence"], 2),
                    "priority_score": row["max_priority"],
                    "competitors_with": competitors_with,
                    "evidence": all_evidence[:5],  # Top 5 evidence
                    "first_detected": row["first_detected"]
                })
            
            return gaps
    
    def get_recent_changes(self, days: int = 7) -> List[Dict]:
        """Get features added by competitors in the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM feature_changes
                WHERE detected_at >= datetime('now', '-' || ? || ' days')
                ORDER BY detected_at DESC
            """, (days,))
            
            changes = []
            for row in cursor.fetchall():
                changes.append({
                    "competitor_url": row["competitor_url"],
                    "feature_name": row["feature_name"],
                    "change_type": row["change_type"],
                    "detected_at": row["detected_at"],
                    "details": json.loads(row["details"]) if row["details"] else None
                })
            
            return changes
    
    def clear_all_data(self):
        """Clear all feature data (for testing)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM competitor_features")
            cursor.execute("DELETE FROM feature_history")
            cursor.execute("DELETE FROM feature_changes")
            conn.commit()


# Global instance
feature_store = FeatureStore()
