"""
Change Detector - Tracks feature changes over time

Detects:
- Newly added features by competitors
- Removed features
- Feature adoption trends
- Competitive intelligence alerts
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from feature_store import feature_store


@dataclass
class FeatureChange:
    competitor_url: str
    feature_name: str
    change_type: str  # 'added', 'removed', 'modified', 'stable'
    category: str
    detected_at: datetime
    details: Dict
    impact_score: int  # 0-100, how important is this change


class ChangeDetector:
    """Detects and tracks changes in competitor features over time."""
    
    # Change types
    CHANGE_ADDED = "added"
    CHANGE_REMOVED = "removed"
    CHANGE_MODIFIED = "modified"
    CHANGE_STABLE = "stable"
    
    def detect_changes(self, competitor_url: str, 
                      current_features: List[Dict]) -> List[FeatureChange]:
        """
        Detect changes in competitor features since last analysis.
        
        Args:
            competitor_url: URL of competitor being analyzed
            current_features: Currently detected features
            
        Returns:
            List of detected changes
        """
        changes = []
        
        # Get historical features for this competitor
        historical_features = feature_store.get_competitor_features(competitor_url)
        
        # Convert to sets for comparison
        historical_names = {f["feature_name"] for f in historical_features}
        current_names = {f.feature_name for f in current_features}
        
        # Detect new features (added)
        new_features = current_names - historical_names
        for feature_name in new_features:
            feature = next(f for f in current_features if f.feature_name == feature_name)
            
            change = FeatureChange(
                competitor_url=competitor_url,
                feature_name=feature_name,
                change_type=self.CHANGE_ADDED,
                category=feature.category,
                detected_at=datetime.now(),
                details={
                    "confidence": feature.confidence,
                    "evidence": feature.evidence[:2]  # Top 2 evidence
                },
                impact_score=self._calculate_impact(feature_name, feature.category, "added")
            )
            changes.append(change)
        
        # Detect removed features
        removed_features = historical_names - current_names
        for feature_name in removed_features:
            historical = next(f for f in historical_features if f["feature_name"] == feature_name)
            
            change = FeatureChange(
                competitor_url=competitor_url,
                feature_name=feature_name,
                change_type=self.CHANGE_REMOVED,
                category=historical["category"],
                detected_at=datetime.now(),
                details={
                    "last_seen": historical["last_seen"],
                    "was_confidence": historical["confidence"]
                },
                impact_score=self._calculate_impact(feature_name, historical["category"], "removed")
            )
            changes.append(change)
        
        # Detect stable features (no change)
        stable_features = current_names & historical_names
        for feature_name in stable_features:
            current = next(f for f in current_features if f.feature_name == feature_name)
            historical = next(f for f in historical_features if f["feature_name"] == feature_name)
            
            # Check if confidence changed significantly
            if abs(current.confidence - historical["confidence"]) > 0.2:
                change = FeatureChange(
                    competitor_url=competitor_url,
                    feature_name=feature_name,
                    change_type=self.CHANGE_MODIFIED,
                    category=current.category,
                    detected_at=datetime.now(),
                    details={
                        "old_confidence": historical["confidence"],
                        "new_confidence": current.confidence,
                        "change": "increased" if current.confidence > historical["confidence"] else "decreased"
                    },
                    impact_score=self._calculate_impact(feature_name, current.category, "modified")
                )
                changes.append(change)
        
        return changes
    
    def get_trending_features(self, days: int = 30) -> List[Dict]:
        """
        Get features that are trending (recently added by multiple competitors).
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of trending features with adoption metrics
        """
        recent_changes = feature_store.get_recent_changes(days)
        
        # Count feature additions
        added_features = {}
        for change in recent_changes:
            if change["change_type"] == "new_feature":
                feature_name = change["feature_name"]
                
                if feature_name not in added_features:
                    added_features[feature_name] = {
                        "feature_name": feature_name,
                        "adopters": [],
                        "adoption_count": 0,
                        "first_adoption": change["detected_at"],
                        "latest_adoption": change["detected_at"]
                    }
                
                added_features[feature_name]["adopters"].append(change["competitor_url"])
                added_features[feature_name]["adoption_count"] += 1
                added_features[feature_name]["latest_adoption"] = max(
                    added_features[feature_name]["latest_adoption"],
                    change["detected_at"]
                )
        
        # Filter for trending (adopted by 2+ competitors)
        trending = [
            feat for feat in added_features.values()
            if feat["adoption_count"] >= 2
        ]
        
        # Sort by adoption count and recency
        trending.sort(
            key=lambda x: (x["adoption_count"], x["latest_adoption"]),
            reverse=True
        )
        
        return trending
    
    def analyze_adoption_trends(self, feature_name: str) -> Dict:
        """
        Analyze how a specific feature has been adopted over time.
        
        Args:
            feature_name: Name of the feature to analyze
            
        Returns:
            Trend analysis with timeline
        """
        import sqlite3
        
        with sqlite3.connect(feature_store.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get adoption timeline
            cursor.execute("""
                SELECT competitor_url, first_seen
                FROM competitor_features
                WHERE feature_name = ?
                ORDER BY first_seen ASC
            """, (feature_name,))
            
            adoptions = []
            for row in cursor.fetchall():
                adoptions.append({
                    "competitor": row["competitor_url"],
                    "adopted_at": row["first_seen"]
                })
            
            if not adoptions:
                return {
                    "feature_name": feature_name,
                    "status": "not_found",
                    "adoption_count": 0
                }
            
            # Calculate trend metrics
            first_adoption = adoptions[0]["adopted_at"]
            latest_adoption = adoptions[-1]["adopted_at"]
            adoption_count = len(adoptions)
            
            # Parse dates for duration calculation
            try:
                first_dt = datetime.fromisoformat(first_adoption)
                latest_dt = datetime.fromisoformat(latest_adoption)
                days_since_first = (datetime.now() - first_dt).days
                
                if adoption_count > 1:
                    days_between = (latest_dt - first_dt).days
                    adoption_velocity = adoption_count / max(days_between, 1)  # adoptions per day
                else:
                    adoption_velocity = 0
                    
            except:
                days_since_first = 0
                adoption_velocity = 0
            
            # Determine trend status
            if adoption_count >= 3:
                trend = "widespread"
            elif adoption_count == 2:
                trend = "emerging"
            else:
                trend = "experimental"
            
            return {
                "feature_name": feature_name,
                "status": trend,
                "adoption_count": adoption_count,
                "first_adoption": first_adoption,
                "latest_adoption": latest_adoption,
                "days_active": days_since_first,
                "adoption_velocity": round(adoption_velocity, 4),
                "adoption_timeline": adoptions
            }
    
    def get_change_alerts(self, priority_threshold: int = 70) -> List[Dict]:
        """
        Get high-priority change alerts that require attention.
        
        Args:
            priority_threshold: Minimum impact score to include (0-100)
            
        Returns:
            List of important changes to act on
        """
        recent_changes = feature_store.get_recent_changes(days=7)
        
        alerts = []
        for change in recent_changes:
            feature_name = change["feature_name"]
            
            # Calculate impact
            impact = self._calculate_impact(
                feature_name, 
                change.get("category", "Unknown"),
                change["change_type"]
            )
            
            if impact >= priority_threshold:
                alerts.append({
                    "feature_name": feature_name,
                    "competitor": change["competitor_url"],
                    "change_type": change["change_type"],
                    "detected_at": change["detected_at"],
                    "impact_score": impact,
                    "alert_level": "critical" if impact >= 90 else "high",
                    "recommendation": self._get_change_recommendation(change)
                })
        
        # Sort by impact
        alerts.sort(key=lambda x: x["impact_score"], reverse=True)
        
        return alerts
    
    def compare_with_competitors(self, your_features: Set[str]) -> Dict:
        """
        Compare your features with all competitors to identify gaps and leads.
        
        Args:
            your_features: Set of feature names you have implemented
            
        Returns:
            Competitive positioning analysis
        """
        # Get all competitor features
        all_competitors = feature_store.get_all_competitor_features()
        
        # Collect all unique features across competitors
        competitor_features = {}
        for url, features in all_competitors.items():
            for feature in features:
                name = feature["feature_name"]
                if name not in competitor_features:
                    competitor_features[name] = {
                        "feature_name": name,
                        "category": feature["category"],
                        "competitors_with": [],
                        "adoption_rate": 0
                    }
                competitor_features[name]["competitors_with"].append(url)
        
        # Calculate adoption rates
        total_competitors = len(all_competitors)
        for feature in competitor_features.values():
            feature["adoption_rate"] = len(feature["competitors_with"]) / total_competitors
        
        # Identify gaps and leads
        gaps = []  # Features competitors have but you don't
        leads = []  # Features you have but competitors don't
        parity = []  # Features both you and competitors have
        
        for name, info in competitor_features.items():
            if name in your_features:
                parity.append({
                    "feature_name": name,
                    "category": info["category"],
                    "adoption_rate": info["adoption_rate"],
                    "position": "leader" if info["adoption_rate"] < 0.5 else "parity"
                })
            else:
                gaps.append({
                    "feature_name": name,
                    "category": info["category"],
                    "adoption_rate": info["adoption_rate"],
                    "urgency": "high" if info["adoption_rate"] > 0.7 else "medium" if info["adoption_rate"] > 0.3 else "low"
                })
        
        # Find your unique features
        all_competitor_names = set(competitor_features.keys())
        for feature_name in your_features:
            if feature_name not in all_competitor_names:
                leads.append({
                    "feature_name": feature_name,
                    "competitive_advantage": "exclusive"
                })
        
        return {
            "total_competitors_analyzed": total_competitors,
            "gaps": sorted(gaps, key=lambda x: x["adoption_rate"], reverse=True),
            "leads": leads,
            "parity": parity,
            "competitive_score": self._calculate_competitive_score(your_features, competitor_features),
            "summary": {
                "gap_count": len(gaps),
                "lead_count": len(leads),
                "parity_count": len(parity)
            }
        }
    
    def _calculate_impact(self, feature_name: str, category: str, change_type: str) -> int:
        """
        Calculate impact score for a change (0-100).
        
        Higher scores for:
        - Payment/Delivery features
        - added changes (new features)
        - Features in critical categories
        """
        base_score = 50
        
        # Category weight
        category_weights = {
            "Payment": 25,
            "Delivery": 20,
            "Trust": 15,
            "Shopping Experience": 15,
            "Discovery": 10,
            "Support": 10,
            "Loyalty": 5,
            "Services": 5
        }
        base_score += category_weights.get(category, 5)
        
        # Change type weight
        if change_type == "added":
            base_score += 20
        elif change_type == "removed":
            base_score += 10
        elif change_type == "modified":
            base_score += 5
        
        return min(100, base_score)
    
    def _get_change_recommendation(self, change: Dict) -> str:
        """Generate recommendation based on change."""
        change_type = change["change_type"]
        feature_name = change["feature_name"]
        
        if change_type == "new_feature":
            return f"Consider implementing {feature_name} to stay competitive"
        elif change_type == "removed":
            return f"Competitor removed {feature_name}. Investigate if it's still valuable"
        else:
            return f"Monitor {feature_name} for further changes"
    
    def _calculate_competitive_score(self, your_features: Set[str], 
                                    competitor_features: Dict) -> int:
        """
        Calculate competitive score (0-100) based on feature coverage.
        
        100 = You have all features competitors have + more
        50 = Parity with competitors
        0 = You have none of the competitor features
        """
        if not competitor_features:
            return 100
        
        # Weight features by adoption rate
        total_weighted = 0
        covered_weighted = 0
        
        for name, info in competitor_features.items():
            weight = info["adoption_rate"]
            total_weighted += weight
            
            if name in your_features:
                covered_weighted += weight
        
        if total_weighted == 0:
            return 100
        
        coverage_score = (covered_weighted / total_weighted) * 100
        
        return int(coverage_score)


# Global instance
change_detector = ChangeDetector()
