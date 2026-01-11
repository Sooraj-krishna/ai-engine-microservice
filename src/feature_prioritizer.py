"""
Feature Prioritizer - Advanced prioritization for discovered features

Prioritizes features based on:
- Competitor adoption rate (how many have it)
- Category importance (Payment > Delivery > Trust > etc.)
- Implementation complexity estimation
- Business impact potential
- Trend momentum (recently added features)
- User base relevance
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import re


@dataclass
class PrioritizedFeature:
    feature_name: str
    category: str
    priority_score: int  # 0-100
    adoption_rate: float  # 0-1
    complexity_estimate: str  # 'low', 'medium', 'high'
    business_impact: str  # 'critical', 'high', 'medium', 'low'
    urgency: str  # 'urgent', 'high', 'medium', 'low'
    reasoning: str
    competitor_count: int
    recommendation: str


class FeaturePrioritizer:
    """Advanced feature prioritization system."""
    
    # Category importance weights (0-100)
    CATEGORY_WEIGHTS = {
        "Payment": 95,          # Most critical - directly affects revenue
        "Delivery": 90,         # Very important - key differentiator
        "Trust": 85,            # High importance - affects conversion
        "Shopping Experience": 80,  # Important - affects satisfaction
        "Support": 75,          # Important - affects retention
        "Discovery": 70,        # Moderate - affects engagement
        "Loyalty": 65,          # Moderate - affects retention
        "Services": 60          # Lower - nice to have
    }
    
    # Complexity estimation patterns
    COMPLEXITY_PATTERNS = {
        "low": [
            r"free shipping",
            r"gift wrap",
            r"size chart",
            r"color",
            r"filter",
            r"sort",
            r"wishlist",
            r"compare"
        ],
        "medium": [
            r"cod|cash on delivery",
            r"reviews?",
            r"ratings?",
            r"live chat",
            r"track",
            r"returns?",
            r"rewards?"
        ],
        "high": [
            r"upi|payment",
            r"emi",
            r"ar view",
            r"virtual try",
            r"same day delivery",
            r"try.{1,5}buy",
            r"subscription"
        ]
    }
    
    def prioritize_features(self, gaps: List[Dict], 
                           competitor_count: int,
                           trending_features: Optional[List[Dict]] = None) -> List[PrioritizedFeature]:
        """
        Prioritize feature gaps using multiple factors.
        
        Args:
            gaps: List of feature gaps from feature_store
            competitor_count: Total number of competitors analyzed
            trending_features: Optional list of trending features
            
        Returns:
            List of prioritized features with scores and recommendations
        """
        prioritized = []
        trending_names = set()
        
        if trending_features:
            trending_names = {f["feature_name"] for f in trending_features}
        
        for gap in gaps:
            # Calculate adoption rate
            adoption_rate = gap["competitor_count"] / max(competitor_count, 1)
            
            # Calculate priority score
            priority_score = self._calculate_priority_score(
                feature_name=gap["feature_name"],
                category=gap["category"],
                adoption_rate=adoption_rate,
                is_trending=(gap["feature_name"] in trending_names)
            )
            
            # Estimate complexity
            complexity = self._estimate_complexity(gap["feature_name"])
            
            # Determine business impact
            impact = self._determine_business_impact(
                category=gap["category"],
                adoption_rate=adoption_rate
            )
            
            # Determine urgency
            urgency = self._determine_urgency(
                adoption_rate=adoption_rate,
                category=gap["category"],
                is_trending=(gap["feature_name"] in trending_names)
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                feature_name=gap["feature_name"],
                category=gap["category"],
                adoption_rate=adoption_rate,
                competitor_count=gap["competitor_count"],
                total_competitors=competitor_count,
                is_trending=(gap["feature_name"] in trending_names)
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                feature_name=gap["feature_name"],
                complexity=complexity,
                impact=impact,
                urgency=urgency
            )
            
            prioritized.append(PrioritizedFeature(
                feature_name=gap["feature_name"],
                category=gap["category"],
                priority_score=priority_score,
                adoption_rate=adoption_rate,
                complexity_estimate=complexity,
                business_impact=impact,
                urgency=urgency,
                reasoning=reasoning,
                competitor_count=gap["competitor_count"],
                recommendation=recommendation
            ))
        
        # Sort by priority score
        prioritized.sort(key=lambda x: x.priority_score, reverse=True)
        
        return prioritized
    
    def _calculate_priority_score(self, feature_name: str, category: str,
                                  adoption_rate: float, is_trending: bool) -> int:
        """
        Calculate priority score (0-100) based on multiple factors.
        
        Factors:
        - Category importance: 40%
        - Adoption rate: 35%
        - Trending bonus: 15%
        - Complexity penalty: 10%
        """
        score = 0
        
        # 1. Category importance (40 points max)
        category_weight = self.CATEGORY_WEIGHTS.get(category, 50)
        score += (category_weight / 100) * 40
        
        # 2. Adoption rate (35 points max)
        # Higher adoption = higher priority
        score += adoption_rate * 35
        
        # 3. Trending bonus (15 points max)
        if is_trending:
            score += 15
        
        # 4. Complexity penalty (up to -10 points)
        complexity = self._estimate_complexity(feature_name)
        if complexity == "high":
            score -= 10
        elif complexity == "medium":
            score -= 5
        # Low complexity: no penalty
        
        # Ensure score is in valid range
        score = max(0, min(100, score))
        
        return int(score)
    
    def _estimate_complexity(self, feature_name: str) -> str:
        """
        Estimate implementation complexity based on feature name.
        
        Returns:
            'low', 'medium', or 'high'
        """
        feature_lower = feature_name.lower()
        
        # Check patterns from high to low
        for pattern in self.COMPLEXITY_PATTERNS["high"]:
            if re.search(pattern, feature_lower):
                return "high"
        
        for pattern in self.COMPLEXITY_PATTERNS["medium"]:
            if re.search(pattern, feature_lower):
                return "medium"
        
        # Default to low if no complex patterns matched
        return "low"
    
    def _determine_business_impact(self, category: str, adoption_rate: float) -> str:
        """
        Determine business impact level.
        
        Returns:
            'critical', 'high', 'medium', or 'low'
        """
        category_weight = self.CATEGORY_WEIGHTS.get(category, 50)
        
        # Critical: High-priority category + high adoption
        if category_weight >= 90 and adoption_rate >= 0.7:
            return "critical"
        
        # High: High-priority category OR high adoption
        if category_weight >= 80 or adoption_rate >= 0.6:
            return "high"
        
        # Medium: Moderate category or moderate adoption
        if category_weight >= 65 or adoption_rate >= 0.3:
            return "medium"
        
        # Low: Everything else
        return "low"
    
    def _determine_urgency(self, adoption_rate: float, category: str, 
                          is_trending: bool) -> str:
        """
        Determine implementation urgency.
        
        Returns:
            'urgent', 'high', 'medium', or 'low'
        """
        category_weight = self.CATEGORY_WEIGHTS.get(category, 50)
        
        # Urgent: Industry standard (>70% adoption) in critical category
        if adoption_rate >= 0.7 and category_weight >= 85:
            return "urgent"
        
        # High: Trending OR widely adopted OR critical category
        if is_trending or adoption_rate >= 0.6 or category_weight >= 90:
            return "high"
        
        # Medium: Moderate adoption
        if adoption_rate >= 0.3:
            return "medium"
        
        # Low: Experimental features
        return "low"
    
    def _generate_reasoning(self, feature_name: str, category: str,
                           adoption_rate: float, competitor_count: int,
                           total_competitors: int, is_trending: bool) -> str:
        """Generate human-readable reasoning for priority."""
        reasons = []
        
        # Adoption reasoning
        if adoption_rate >= 0.8:
            reasons.append(f"Industry standard - {competitor_count}/{total_competitors} competitors have it")
        elif adoption_rate >= 0.5:
            reasons.append(f"Common feature - adopted by {competitor_count}/{total_competitors} competitors")
        elif competitor_count >= 2:
            reasons.append(f"Emerging - {competitor_count} competitors offer this")
        else:
            reasons.append(f"Experimental - only {competitor_count} competitor has it")
        
        # Category reasoning
        category_weight = self.CATEGORY_WEIGHTS.get(category, 50)
        if category_weight >= 90:
            reasons.append(f"{category} features are critical for conversion")
        elif category_weight >= 75:
            reasons.append(f"{category} features significantly impact user experience")
        
        # Trending bonus
        if is_trending:
            reasons.append("Recently added by competitors - momentum is building")
        
        return ". ".join(reasons)
    
    def _generate_recommendation(self, feature_name: str, complexity: str,
                                impact: str, urgency: str) -> str:
        """Generate actionable recommendation."""
        
        # Urgent + High Impact = Immediate action
        if urgency in ["urgent", "high"] and impact in ["critical", "high"]:
            if complexity == "low":
                return f"✅ Quick win! Implement {feature_name} immediately - high impact, low effort"
            elif complexity == "medium":
                return f"🚀 High priority. Schedule {feature_name} for next sprint - significant competitive advantage"
            else:
                return f"🎯 Strategic priority. Plan {feature_name} implementation - essential for competitiveness despite complexity"
        
        # Medium urgency/impact
        elif urgency in ["medium", "high"] or impact in ["medium", "high"]:
            if complexity == "low":
                return f"👍 Good opportunity. Add {feature_name} to backlog - easy improvement"
            else:
                return f"📋 Consider {feature_name} for roadmap - evaluate ROI vs. complexity"
        
        # Low priority
        else:
            return f"💡 Nice to have. Monitor {feature_name} adoption - implement if it gains traction"
    
    def get_quick_wins(self, prioritized_features: List[PrioritizedFeature],
                      max_results: int = 5) -> List[PrioritizedFeature]:
        """
        Get quick win features (high impact, low complexity).
        
        Args:
            prioritized_features: List of prioritized features
            max_results: Maximum number of results to return
            
        Returns:
            Top quick win opportunities
        """
        quick_wins = [
            f for f in prioritized_features
            if f.complexity_estimate == "low" and f.business_impact in ["high", "critical"]
        ]
        
        # Sort by priority score
        quick_wins.sort(key=lambda x: x.priority_score, reverse=True)
        
        return quick_wins[:max_results]
    
    def get_strategic_priorities(self, prioritized_features: List[PrioritizedFeature],
                                max_results: int = 5) -> List[PrioritizedFeature]:
        """
        Get strategic priorities (high impact, worth the complexity).
        
        Args:
            prioritized_features: List of prioritized features
            max_results: Maximum number of results to return
            
        Returns:
            Top strategic priorities
        """
        strategic = [
            f for f in prioritized_features
            if f.business_impact == "critical" and f.urgency in ["urgent", "high"]
        ]
        
        # Sort by priority score
        strategic.sort(key=lambda x: x.priority_score, reverse=True)
        
        return strategic[:max_results]
    
    def generate_implementation_roadmap(self, prioritized_features: List[PrioritizedFeature]) -> Dict:
        """
        Generate a phased implementation roadmap.
        
        Args:
            prioritized_features: List of prioritized features
            
        Returns:
            Roadmap with features grouped by phase
        """
        roadmap = {
            "phase_1_immediate": [],  # Urgent + Low/Medium complexity
            "phase_2_short_term": [],  # High priority
            "phase_3_medium_term": [],  # Medium priority
            "phase_4_long_term": []  # Low priority or experimental
        }
        
        for feature in prioritized_features:
            # Phase 1: Immediate (urgent + not too complex)
            if feature.urgency == "urgent" and feature.complexity_estimate != "high":
                roadmap["phase_1_immediate"].append(feature)
            
            # Phase 2: Short-term (high urgency or critical impact)
            elif feature.urgency == "high" or feature.business_impact == "critical":
                roadmap["phase_2_short_term"].append(feature)
            
            # Phase 3: Medium-term (medium priority)
            elif feature.urgency == "medium" or feature.business_impact == "medium":
                roadmap["phase_3_medium_term"].append(feature)
            
            # Phase 4: Long-term (low priority)
            else:
                roadmap["phase_4_long_term"].append(feature)
        
        # Add metadata
        roadmap["summary"] = {
            "total_features": len(prioritized_features),
            "phase_1_count": len(roadmap["phase_1_immediate"]),
            "phase_2_count": len(roadmap["phase_2_short_term"]),
            "phase_3_count": len(roadmap["phase_3_medium_term"]),
            "phase_4_count": len(roadmap["phase_4_long_term"])
        }
        
        return roadmap


# Global instance
feature_prioritizer = FeaturePrioritizer()
