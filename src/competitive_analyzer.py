"""
Competitive Analyzer - Main module for comparing sites and identifying feature gaps.
Analyzes competitor sites and recommends features to implement.
"""

from feature_extractor import extract_features_from_site
import asyncio
from datetime import datetime
from typing import List, Dict
import json


class CompetitiveAnalyzer:
    """Analyzes competitor sites and identifies feature gaps."""
    
    def __init__(self):
        self.analysis_results = None
        
    async def analyze_competitors(self, own_site_url: str, competitor_urls: List[str]) -> Dict:
        """
        Analyze competitor sites and compare with own site.
        
        Args:
            own_site_url: URL of your own site
            competitor_urls: List of competitor site URLs
            
        Returns:
            Complete competitive analysis with recommendations
        """
        print(f"[COMPETITIVE_ANALYZER] Starting competitive analysis")
        print(f"[COMPETITIVE_ANALYZER] Your site: {own_site_url}")
        print(f"[COMPETITIVE_ANALYZER] Competitors: {len(competitor_urls)}")
        
        # Extract features from own site
        print(f"[COMPETITIVE_ANALYZER] Analyzing your site...")
        own_features = await extract_features_from_site(own_site_url)
        
        # Extract features from competitor sites
        competitor_features = []
        for i, url in enumerate(competitor_urls, 1):
            print(f"[COMPETITIVE_ANALYZER] Analyzing competitor {i}/{len(competitor_urls)}: {url}")
            try:
                features = await extract_features_from_site(url)
                competitor_features.append(features)
            except Exception as e:
                print(f"[ERROR] Failed to analyze {url}: {e}")
                competitor_features.append({"url": url, "error": str(e)})
        
        # Compare and identify gaps
        print(f"[COMPETITIVE_ANALYZER] Comparing features...")
        feature_gaps = self.identify_feature_gaps(own_features, competitor_features)
        
        # Rank by priority
        print(f"[COMPETITIVE_ANALYZER] Ranking features by priority...")
        recommendations = self.rank_features(feature_gaps, len(competitor_urls))
        
        # Build complete analysis result
        analysis = {
            "analysis_date": datetime.now().isoformat(),
            "your_site": own_site_url,
            "your_features": own_features,
            "competitors_analyzed": [c.get("url") for c in competitor_features],
            "competitor_features": competitor_features,
            "feature_gaps": recommendations,
            "summary": {
                "total_competitors": len(competitor_urls),
                "total_gaps_identified": len(recommendations),
                "high_priority": len([r for r in recommendations if r.get("priority_score", 0) >= 7]),
                "medium_priority": len([r for r in recommendations if 4 <= r.get("priority_score", 0) < 7]),
                "low_priority": len([r for r in recommendations if r.get("priority_score", 0) < 4])
            }
        }
        
        self.analysis_results = analysis
        
        print(f"[COMPETITIVE_ANALYZER] ========================================")
        print(f"[COMPETITIVE_ANALYZER] Analysis complete!")
        print(f"[COMPETITIVE_ANALYZER] - Feature gaps identified: {len(recommendations)}")
        print(f"[COMPETITIVE_ANALYZER] - High priority: {analysis['summary']['high_priority']}")
        print(f"[COMPETITIVE_ANALYZER] - Medium priority: {analysis['summary']['medium_priority']}")
        print(f"[COMPETITIVE_ANALYZER] - Low priority: {analysis['summary']['low_priority']}")
        print(f"[COMPETITIVE_ANALYZER] ========================================")
        
        return analysis
    
    def identify_feature_gaps(self, own_features: Dict, competitor_features: List[Dict]) -> List[Dict]:
        """
        Identify features that competitors have but you don't.
        
        Args:
            own_features: Features from your site
            competitor_features: List of features from competitor sites
            
        Returns:
            List of missing features with metadata
        """
        gaps = []
        
        # Combine all features from all categories
        own_feature_set = self._build_feature_set(own_features)
        
        # Track which features appear in competitors
        competitor_feature_tracker = {}
        
        for competitor in competitor_features:
            if "error" in competitor:
                continue
                
            competitor_url = competitor.get("url", "unknown")
            competitor_set = self._build_feature_set(competitor)
            
            for feature in competitor_set:
                if feature not in competitor_feature_tracker:
                    competitor_feature_tracker[feature] = {
                        "feature": feature,
                        "found_in": [],
                        "count": 0
                    }
                competitor_feature_tracker[feature]["found_in"].append(competitor_url)
                competitor_feature_tracker[feature]["count"] += 1
        
        # Identify gaps (features competitors have but you don't)
        for feature_name, data in competitor_feature_tracker.items():
            if feature_name not in own_feature_set:
                # This is a gap!
                gaps.append({
                    "feature_name": feature_name,
                    "found_in": data["found_in"],
                    "frequency": len(data["found_in"]),
                    "frequency_percentage": (len(data["found_in"]) / len(competitor_features)) * 100
                })
        
        return gaps
    
    def _build_feature_set(self, features: Dict) -> set:
        """Build a set of all feature names from a features dict."""
        feature_set = set()
        
        categories = ['ui_components', 'functionality', 'content_types', 'ux_patterns', 'integrations']
        for category in categories:
            if category in features:
                for item in features[category]:
                    name = item.get('name', '')
                    if name:
                        feature_set.add(name)
        
        return feature_set
    
    def rank_features(self, gaps: List[Dict], total_competitors: int) -> List[Dict]:
        """
        Rank features by priority score.
        
        Priority score = (frequency × impact_multiplier) / complexity_multiplier
        """
        ranked = []
        
        for gap in gaps:
            feature_name = gap["feature_name"]
            frequency = gap["frequency"]
            frequency_pct = gap["frequency_percentage"]
            
            # Estimate complexity based on feature type
            complexity = self._estimate_complexity(feature_name)
            complexity_multiplier = {"low": 1, "medium": 2, "high": 3}[complexity]
            
            # Estimate business impact based on frequency
            if frequency_pct >= 75:
                impact = "high"
                impact_multiplier = 3
            elif frequency_pct >= 50:
                impact = "medium"
                impact_multiplier = 2
            else:
                impact = "low"
                impact_multiplier = 1
            
            # Calculate priority score (0-10 scale)
            priority_score = min(10, (frequency * impact_multiplier * 2) / complexity_multiplier)
            
            # Estimate effort
            effort = self._estimate_effort(complexity)
            
            ranked.append({
                "id": f"feature_{len(ranked) + 1:03d}",
                "name": feature_name,
                "category": self._categorize_feature(feature_name),
                "description": self._generate_description(feature_name),
                "found_in": gap["found_in"],
                "frequency": f"{frequency}/{total_competitors}",
                "frequency_percentage": f"{frequency_pct:.0f}%",
                "complexity": complexity,
                "priority_score": round(priority_score, 1),
                "estimated_effort": effort,
                "business_impact": impact,
                "implementation_notes": self._generate_implementation_notes(feature_name)
            })
        
        # Sort by priority score (descending)
        ranked.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return ranked
    
    def _estimate_complexity(self, feature_name: str) -> str:
        """Estimate implementation complexity."""
        feature_lower = feature_name.lower()
        
        # High complexity features
        high_complexity = ['search', 'filter', 'authentication', 'payment', 'chat', 'analytics']
        if any(term in feature_lower for term in high_complexity):
            return "high"
        
        # Low complexity features
        low_complexity = ['footer', 'sidebar', 'modal', 'tooltip', 'dark mode', 'toggle']
        if any(term in feature_lower for term in low_complexity):
            return "low"
        
        # Default to medium
        return "medium"
    
    def _estimate_effort(self, complexity: str) -> str:
        """Estimate implementation effort."""
        effort_map = {
            "low": "3-5 days",
            "medium": "1-2 weeks",
            "high": "2-4 weeks"
        }
        return effort_map.get(complexity, "1-2 weeks")
    
    def _categorize_feature(self, feature_name: str) -> str:
        """Categorize a feature."""
        feature_lower = feature_name.lower()
        
        if any(term in feature_lower for term in ['nav', 'footer', 'sidebar', 'hero', 'card', 'modal', 'tab', 'carousel']):
            return "ui_component"
        elif any(term in feature_lower for term in ['search', 'filter', 'form', 'auth', 'login']):
            return "functionality"
        elif any(term in feature_lower for term in ['blog', 'product', 'pricing', 'testimonial', 'faq', 'gallery']):
            return "content_type"
        elif any(term in feature_lower for term in ['dark mode', 'animation', 'tooltip']):
            return "ux_pattern"
        elif any(term in feature_lower for term in ['facebook', 'twitter', 'instagram', 'analytics', 'chat', 'payment']):
            return "integration"
        else:
            return "other"
    
    def _generate_description(self, feature_name: str) -> str:
        """Generate a description for a feature."""
        descriptions = {
            "Search Functionality": "Search bar allowing users to find content quickly",
            "Filters": "Filtering options to narrow down search results or product listings",
            "Authentication": "User login and registration system",
            "Forms": "Contact forms, newsletter signup, or other data collection forms",
            "Modal Dialogs": "Popup windows for displaying content or collecting user input",
            "Dark Mode Toggle": "Option to switch between light and dark themes",
            "Carousel/Slider": "Image or content carousel for showcasing multiple items",
            "Testimonials": "Customer reviews and testimonials section",
            "Pricing Tables": "Structured pricing information for products or services",
            "Blog": "Blog section with articles and posts",
            "FAQ": "Frequently asked questions section",
            "Live Chat": "Real-time customer support chat widget",
            "Newsletter": "Email newsletter signup form"
        }
        
        # Try exact match first
        if feature_name in descriptions:
            return descriptions[feature_name]
        
        # Try partial match
        for key, desc in descriptions.items():
            if key.lower() in feature_name.lower() or feature_name.lower() in key.lower():
                return desc
        
        # Generate generic description
        return f"Feature: {feature_name}"
    
    def _generate_implementation_notes(self, feature_name: str) -> str:
        """Generate implementation notes for a feature."""
        feature_lower = feature_name.lower()
        
        if 'search' in feature_lower:
            return "Requires search backend, UI components, and possibly indexing system"
        elif 'filter' in feature_lower:
            return "Needs filter UI, state management, and possibly backend filtering logic"
        elif 'auth' in feature_lower or 'login' in feature_lower:
            return "Requires authentication system, user database, session management"
        elif 'dark mode' in feature_lower:
            return "CSS theming system, user preference storage, theme toggle component"
        elif 'chat' in feature_lower:
            return "Integration with chat service (Intercom, Drift, etc.) or custom implementation"
        elif 'payment' in feature_lower:
            return "Payment gateway integration (Stripe, PayPal, etc.)"
        elif 'blog' in feature_lower:
            return "CMS or blog system, article templates, potentially admin interface"
        else:
            return "Implementation details to be determined based on specific requirements"
    
    def get_recommendations_summary(self) -> str:
        """Get a human-readable summary of recommendations."""
        if not self.analysis_results:
            return "No analysis performed yet"
        
        gaps = self.analysis_results.get("feature_gaps", [])
        if not gaps:
            return "No feature gaps identified - your site has all features found in competitors!"
        
        summary = f"Found {len(gaps)} feature gaps:\n\n"
        
        # Show top 5 high-priority features
        high_pri = [g for g in gaps if g.get("priority_score", 0) >= 7][:5]
        if high_pri:
            summary += "High Priority Features:\n"
            for feature in high_pri:
                summary += f"  • {feature['name']} (Priority: {feature['priority_score']}/10, Found in: {feature['frequency_percentage']})\n"
            summary += "\n"
        
        return summary
