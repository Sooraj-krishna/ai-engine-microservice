"""
Competitive Analyzer - Main module for comparing sites and identifying feature gaps.
Analyzes competitor sites and recommends features to implement.
"""

from feature_extractor import extract_features_from_site
from deep_feature_extractor import DeepFeatureExtractor
from cache_manager import cache_manager
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Literal
import json
import os
import hashlib


class CompetitiveAnalyzer:
    """Analyzes competitor sites and identifies feature gaps."""
    
    def __init__(self, depth: str = "standard"):
        """
        Initialize analyzer with depth mode.
        
        Args:
            depth: Analysis depth - "basic", "standard", or "deep"
        """
        self.analysis_results = None
        self.depth = depth
        self.deep_extractor = None
        
        if depth == "deep":
            max_pages = int(os.getenv("COMPETITIVE_MAX_PAGES_PER_SITE", "5"))
            enable_perf = os.getenv("COMPETITIVE_ENABLE_PERFORMANCE_METRICS", "true").lower() == "true"
            enable_design = os.getenv("COMPETITIVE_ENABLE_DESIGN_SYSTEM_ANALYSIS", "true").lower() == "true"
            self.deep_extractor = DeepFeatureExtractor(
                max_pages=max_pages,
                enable_performance=enable_perf,
                enable_design_system=enable_design
            )
        
    async def analyze_competitors(self, own_site_url: str, competitor_urls: List[str], premium: bool = False) -> Dict:
        """
        Analyze competitor sites and compare with own site.
        
        Args:
            own_site_url: URL of your own site
            competitor_urls: List of competitor site URLs
            premium: Enable premium analysis features
            
        Returns:
            Complete competitive analysis with recommendations
        """
        print(f"[COMPETITIVE_ANALYZER] Starting competitive analysis (depth: {self.depth}, premium: {premium})")
        print(f"[COMPETITIVE_ANALYZER] Your site: {own_site_url}")
        print(f"[COMPETITIVE_ANALYZER] Competitors: {len(competitor_urls)}")
        
        # Check cache first
        cache_key = self._generate_cache_key(own_site_url, competitor_urls, premium)
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            print(f"[COMPETITIVE_ANALYZER] ✅ Using cached analysis results")
            return cached_result
        
        # Extract features from own site
        print(f"[COMPETITIVE_ANALYZER] Analyzing your site...")
        own_features = await self._extract_features(own_site_url)
        
        # Add premium analysis if enabled
        if premium:
            print(f"[COMPETITIVE_ANALYZER] Running PREMIUM analysis on your site...")
            from premium_analyzer import PremiumAnalyzer
            premium_analyzer = PremiumAnalyzer()
            own_features["premium_analysis"] = await premium_analyzer.analyze_premium(own_site_url)
        
        # Extract features from competitor sites IN PARALLEL
        print(f"[COMPETITIVE_ANALYZER] Analyzing {len(competitor_urls)} competitors in parallel...")
        competitor_tasks = []
        for i, url in enumerate(competitor_urls, 1):
            competitor_tasks.append(self._analyze_single_competitor(url, i, len(competitor_urls), premium))
        
        # Run all competitor analyses concurrently
        competitor_features = await asyncio.gather(*competitor_tasks, return_exceptions=True)
        
        # Handle any exceptions from parallel execution
        processed_features = []
        for i, result in enumerate(competitor_features):
            if isinstance(result, Exception):
                print(f"[ERROR] Failed to analyze competitor {competitor_urls[i]}: {result}")
                processed_features.append({"url": competitor_urls[i], "error": str(result)})
            else:
                processed_features.append(result)
        
        competitor_features = processed_features
        
        # Compare and identify gaps
        print(f"[COMPETITIVE_ANALYZER] Comparing features...")
        feature_gaps = self.identify_feature_gaps(own_features, competitor_features)
        
        # Rank by priority
        print(f"[COMPETITIVE_ANALYZER] Ranking features by priority...")
        recommendations = self.rank_features(feature_gaps, len(competitor_urls))
        
        # Add design system comparison if in deep mode
        design_comparison = None
        if self.depth == "deep":
            design_comparison = self._compare_design_systems(own_features, competitor_features)
        
        # Add premium comparison if enabled
        premium_comparison = None
        if premium:
            print(f"[COMPETITIVE_ANALYZER] Generating premium comparison report...")
            premium_comparison = self._generate_premium_comparison(own_features, competitor_features)
        
        # Build complete analysis result
        analysis = {
            "analysis_date": datetime.now().isoformat(),
            "analysis_depth": self.depth,
            "is_premium": premium,
            "your_site": own_site_url,
            "your_features": own_features,
            "competitors_analyzed": [c.get("url") for c in competitor_features],
            "competitor_features": competitor_features,
            "feature_gaps": recommendations,
            "design_comparison": design_comparison,
            "premium_comparison": premium_comparison,
            "summary": {
                "total_competitors": len(competitor_urls),
                "total_gaps_identified": len(recommendations),
                "high_priority": len([r for r in recommendations if r.get("priority_score", 0) >= 7]),
                "medium_priority": len([r for r in recommendations if 4 <= r.get("priority_score", 0) < 7]),
                "low_priority": len([r for r in recommendations if r.get("priority_score", 0) < 4])
            }
        }
        
        # Cache the result for 24 hours
        cache_manager.set(cache_key, analysis, ttl=timedelta(hours=24))
        
        self.analysis_results = analysis
        
        print(f"[COMPETITIVE_ANALYZER] ========================================")
        print(f"[COMPETITIVE_ANALYZER] Analysis complete!")
        print(f"[COMPETITIVE_ANALYZER] - Feature gaps identified: {len(recommendations)}")
        print(f"[COMPETITIVE_ANALYZER] - High priority: {analysis['summary']['high_priority']}")
        print(f"[COMPETITIVE_ANALYZER] - Medium priority: {analysis['summary']['medium_priority']}")
        print(f"[COMPETITIVE_ANALYZER] - Low priority: {analysis['summary']['low_priority']}")
        print(f"[COMPETITIVE_ANALYZER] ========================================")
        
        return analysis
    
    async def _extract_features(self, url: str) -> Dict:
        """Extract features based on depth mode."""
        if self.depth == "deep" and self.deep_extractor:
            return await self.deep_extractor.extract_features_deep(url)
        else:
            # Use standard extractor (basic or standard mode)
            return await extract_features_from_site(url)
    
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
        """Generate detailed implementation notes for a feature."""
        feature_lower = feature_name.lower()
        
        if 'search' in feature_lower:
            return ("Implement with: 1) Search UI component (input + results dropdown), "
                   "2) Backend search API or use services like Algolia/ElasticSearch, "
                   "3) Debouncing for autocomplete. Libraries: react-instantsearch, fuse.js")
        elif 'filter' in feature_lower:
            return ("Add filter UI (checkboxes/dropdowns), state management for selected filters, "
                   "URL sync for shareable filtered views. Libraries: react-select, downshift")
        elif 'auth' in feature_lower or 'login' in feature_lower:
            return ("Implement: 1) Auth forms (login/signup), 2) JWT or session-based auth, "
                   "3) Protected routes, 4) Password reset flow. Services: Auth0, Firebase Auth, NextAuth.js")
        elif 'dark mode' in feature_lower or 'theme' in feature_lower:
            return ("Add theme context/provider, CSS variables for colors, localStorage persistence, "
                   "toggle component. Libraries: next-themes, use-dark-mode")
        elif 'chat' in feature_lower:
            return ("Integrate chat widget: Intercom ($), Drift ($), Crisp (free tier), or custom with Socket.io. "
                   "Requires backend WebSocket connection for real-time messaging")
        elif 'payment' in feature_lower:
            return ("Integrate payment gateway: Stripe Checkout (recommended), PayPal, or Square. "
                   "Requires: 1) Payment form UI, 2) Backend API integration, 3) Webhook handlers for payment events")
        elif 'blog' in feature_lower:
            return ("Options: 1) Headless CMS (Contentful, Sanity), 2) MDX files with frontmatter, "
                   "3) WordPress with REST API. Need: article templates, listing page, SEO optimization")
        elif 'carousel' in feature_lower or 'slider' in feature_lower:
            return ("Add carousel component with touch/swipe support, auto-play, indicators. "
                   "Libraries: swiper, react-slick, keen-slider")
        elif 'modal' in feature_lower or 'dialog' in feature_lower:
            return ("Create modal component with: backdrop, close on ESC, focus trap, scroll lock. "
                   "Libraries: react-modal, headlessui/dialog, radix-ui/dialog")
        elif 'tooltip' in feature_lower:
            return ("Add tooltip component with positioning logic (avoid viewport overflow). "
                   "Libraries: tippy.js, react-tooltip, radix-ui/tooltip")
        elif 'form' in feature_lower:
            return ("Implement with validation library: react-hook-form + zod/yup, Formik. "
                   "Add error states, loading states, success feedback")
        elif 'notification' in feature_lower or 'toast' in feature_lower:
            return ("Add toast notification system with queue, auto-dismiss, positioning. "
                   "Libraries: react-hot-toast, sonner, react-toastify")
        elif 'animation' in feature_lower:
            return ("Add animations using CSS transitions, Framer Motion, or GSAP. "
                   "Use intersection observer for scroll-triggered animations")
        elif 'accordion' in feature_lower:
            return ("Create accordion with: expand/collapse animation, single vs multiple open items. "
                   "Libraries: headlessui/disclosure, radix-ui/accordion")
        elif 'tabs' in feature_lower:
            return ("Implement tab component with: keyboard navigation, URL sync, animations. "
                   "Libraries: headlessui/tabs, radix-ui/tabs")
        elif 'pagination' in feature_lower:
            return ("Add pagination component with: page numbers, prev/next, URL params for page state. "
                   "Libraries: react-paginate, rc-pagination")
        elif 'skeleton' in feature_lower or 'loading' in feature_lower:
            return ("Create skeleton loaders matching content layout, show during data fetch. "
                   "Use CSS animations for shimmer effect")
        elif 'analytics' in feature_lower:
            return ("Integrate: Google Analytics 4, Mixpanel, or Plausible. "
                   "Track pageviews, custom events, user properties")
        elif 'rating' in feature_lower or 'review' in feature_lower:
            return ("Add star rating component, review submission form, display reviews with pagination. "
                   "Libraries: react-rating, react-simple-star-rating")
        elif 'breadcrumb' in feature_lower:
            return ("Generate breadcrumbs from route structure, add schema.org markup for SEO. "
                   "Auto-generate from Next.js router or custom navigation config")
        else:
            return "Implementation details depend on specific requirements. Research similar implementations and choose appropriate libraries."
    
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
    
    def _compare_design_systems(self, own_features: Dict, competitor_features: List[Dict]) -> Dict:
        """Compare design systems between your site and competitors (deep mode only)."""
        comparison = {
            "color_differences": [],
            "typography_differences": [],
            "spacing_differences": [],
            "common_patterns": [],
            "unique_patterns": []
        }
        
        try:
            own_design = own_features.get("design_system", {})
            
            # Analyze each competitor's design system
            for competitor in competitor_features:
                if "error" in competitor or "design_system" not in competitor:
                    continue
                
                comp_design = competitor.get("design_system", {})
                comp_url = competitor.get("url", "unknown")
                
                # Color palette comparison
                own_colors = set(own_design.get("colors", {}).get("backgrounds", []))
                comp_colors = set(comp_design.get("colors", {}).get("backgrounds", []))
                unique_comp_colors = comp_colors - own_colors
                
                if unique_comp_colors:
                    comparison["color_differences"].append({
                        "competitor": comp_url,
                        "unique_colors": list(unique_comp_colors)[:5],  # Show top 5
                        "note": "Competitor uses different color palette"
                    })
                
                # Typography comparison
                own_fonts = set(own_design.get("typography", {}).get("families", []))
                comp_fonts = set(comp_design.get("typography", {}).get("families", []))
                unique_comp_fonts = comp_fonts - own_fonts
                
                if unique_comp_fonts:
                    comparison["typography_differences"].append({
                        "competitor": comp_url,
                        "unique_fonts": list(unique_comp_fonts),
                        "note": "Different font families used"
                    })
            
            # Identify common patterns across competitors
            all_comp_features = []
            for competitor in competitor_features:
                if "error" not in competitor:
                    for category in ['ui_components', 'ux_patterns']:
                        features = competitor.get(category, [])
                        all_comp_features.extend([f.get('name') for f in features if f.get('name')])
            
            # Find features present in most competitors
            from collections import Counter
            feature_counts = Counter(all_comp_features)
            common_threshold = len([c for c in competitor_features if "error" not in c]) * 0.6
            
            for feature, count in feature_counts.most_common(10):
                if count >= common_threshold:
                    comparison["common_patterns"].append({
                        "feature": feature,
                        "frequency": f"{count}/{len(competitor_features)}",
                        "note": "Industry standard pattern"
                    })
            
        except Exception as e:
            print(f"[WARNING] Design system comparison failed: {e}")
        
        return comparison
    
    def _generate_premium_comparison(self, own_features: Dict, competitor_features: List[Dict]) -> Dict:
        """Generate premium comparison report (premium mode only)."""
        comparison = {
            "seo_comparison": {},
            "accessibility_comparison": {},
            "tech_stack_comparison": {},
            "pricing_comparison": {},
            "mobile_comparison": {},
            "insights": []
        }
        
        try:
            own_premium = own_features.get("premium_analysis", {})
            
            # SEO Comparison
            seo_scores = []
            for competitor in competitor_features:
                if "error" not in competitor and "premium_analysis" in competitor:
                    comp_seo = competitor.get("premium_analysis", {}).get("seo", {})
                    seo_scores.append({
                        "url": competitor.get("url"),
                        "score": comp_seo.get("seo_score", 0),
                        "has_og": bool(comp_seo.get("open_graph")),
                        "has_structured_data": bool(comp_seo.get("structured_data"))
                    })
            
            own_seo_score = own_premium.get("seo", {}).get("seo_score", 0)
            avg_competitor_seo = sum(s["score"] for s in seo_scores) / len(seo_scores) if seo_scores else 0
            
            comparison["seo_comparison"] = {
                "your_score": own_seo_score,
                "average_competitor_score": round(avg_competitor_seo, 1),
                "competitor_scores": seo_scores,
                "recommendation": "Improve SEO" if own_seo_score < avg_competitor_seo else "SEO is competitive"
            }
            
            # Accessibility Comparison
            a11y_scores = []
            for competitor in competitor_features:
                if "error" not in competitor and "premium_analysis" in competitor:
                    comp_a11y = competitor.get("premium_analysis", {}).get("accessibility", {})
                    a11y_scores.append({
                        "url": competitor.get("url"),
                        "score": comp_a11y.get("accessibility_score", 0),
                        "alt_coverage": comp_a11y.get("alt_text_coverage", {}).get("coverage_percentage", 0)
                    })
            
            own_a11y_score = own_premium.get("accessibility", {}).get("accessibility_score", 0)
            avg_competitor_a11y = sum(s["score"] for s in a11y_scores) / len(a11y_scores) if a11y_scores else 0
            
            comparison["accessibility_comparison"] = {
                "your_score": own_a11y_score,
                "average_competitor_score": round(avg_competitor_a11y, 1),
                "competitor_scores": a11y_scores,
                "recommendation": "Improve accessibility" if own_a11y_score < avg_competitor_a11y else "Accessibility is competitive"
            }
            
            # Tech Stack Comparison
            all_frameworks = set()
            all_css_frameworks = set()
            for competitor in competitor_features:
                if "error" not in competitor and "premium_analysis" in competitor:
                    tech = competitor.get("premium_analysis", {}).get("technical_stack", {})
                    all_frameworks.update(tech.get("frameworks", []))
                    all_css_frameworks.update(tech.get("css_frameworks", []))
            
            own_tech = own_premium.get("technical_stack", {})
            comparison["tech_stack_comparison"] = {
                "your_frameworks": own_tech.get("frameworks", []),
                "popular_frameworks": list(all_frameworks),
                "your_css": own_tech.get("css_frameworks", []),
                "popular_css": list(all_css_frameworks)
            }
            
            # Pricing Comparison
            pricing_strategies = []
            for competitor in competitor_features:
                if "error" not in competitor and "premium_analysis" in competitor:
                    pricing = competitor.get("premium_analysis", {}).get("pricing", {})
                    if pricing.get("has_pricing"):
                        pricing_strategies.append({
                            "url": competitor.get("url"),
                            "strategy": pricing.get("pricing_strategy"),
                            "tiers": len(pricing.get("pricing_tiers", []))
                        })
            
            own_pricing = own_premium.get("pricing", {})
            comparison["pricing_comparison"] = {
                "your_strategy": own_pricing.get("pricing_strategy", "Not detected"),
                "your_tiers": len(own_pricing.get("pricing_tiers", [])),
                "competitor_strategies": pricing_strategies
            }
            
            # Generate insights
            insights = []
            if own_seo_score < avg_competitor_seo:
                insights.append({
                    "category": "SEO",
                    "priority": "high",
                    "message": f"Your SEO score ({own_seo_score}) is below competitors' average ({avg_competitor_seo:.0f})"
                })
            if own_a11y_score < avg_competitor_a11y:
                insights.append({
                    "category": "Accessibility",
                    "priority": "high",
                    "message": f"Your accessibility score ({own_a11y_score}) is below competitors' average ({avg_competitor_a11y:.0f})"
                })
            
            comparison["insights"] = insights
            
        except Exception as e:
            print(f"[WARNING] Premium comparison failed: {e}")
        
        return comparison
    
    def _generate_cache_key(self, own_site_url: str, competitor_urls: List[str], premium: bool) -> str:
        """Generate cache key for analysis results."""
        key_data = {
            "own_site": own_site_url,
            "competitors": sorted(competitor_urls),  # Sort for consistent keys
            "depth": self.depth,
            "premium": premium
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def _analyze_single_competitor(self, url: str, index: int, total: int, premium: bool) -> Dict:
        """Analyze a single competitor (for parallel execution)."""
        print(f"[COMPETITIVE_ANALYZER] Analyzing competitor {index}/{total}: {url}")
        try:
            features = await self._extract_features(url)
            
            # Add premium analysis if enabled
            if premium:
                print(f"[COMPETITIVE_ANALYZER] Running PREMIUM analysis on competitor {index}...")
                from premium_analyzer import PremiumAnalyzer
                premium_analyzer = PremiumAnalyzer()
                features["premium_analysis"] = await premium_analyzer.analyze_premium(url)
            
            return features
        except Exception as e:
            print(f"[ERROR] Failed to analyze {url}: {e}")
            return {"url": url, "error": str(e)}
