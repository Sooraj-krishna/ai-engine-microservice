"""
Professional Competitive Analyzer - Production-grade competitive intelligence

Focuses on BUSINESS FEATURES not UI components:
- Payment options (COD, UPI, EMI)
- Delivery features (Same Day, Free Shipping)
- Shopping experience (Try & Buy, Easy Returns)
- Trust signals (Reviews, Q&A)
- Discovery (Wishlist, Recommendations)

Architecture:
1. Fetch pages with Playwright
2. Extract text content
3. Detect features using rule-based patterns + NLP discovery
4. Store in database with history
5. Track changes over time
6. Analyze gaps with advanced prioritization
"""

from playwright.async_api import async_playwright, Browser
from bs4 import BeautifulSoup
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from rule_based_feature_detector import rule_detector
from feature_store import feature_store
from nlp_feature_discovery import nlp_discoverer
from change_detector import change_detector
from feature_prioritizer import feature_prioritizer

# Per-site page fetch timeout (seconds)
SITE_FETCH_TIMEOUT = 30
# Total analysis timeout (seconds) — safety net for the whole task
ANALYSIS_TIMEOUT = 600


class ProfessionalCompetitiveAnalyzer:
    """Production-grade competitive analysis focusing on business features."""
    
    async def analyze_competitors_professional(
        self, 
        own_site_url: str, 
        competitor_urls: List[str],
        your_features: List[str] = None
    ) -> Dict:
        """
        Analyze competitor sites for business features.
        
        Args:
            own_site_url: Your website URL
            competitor_urls: List of competitor URLs
            your_features: List of features you already have (optional)
            
        Returns:
            Comprehensive analysis with prioritized gaps
        """
        print(f"[PROFESSIONAL_ANALYZER] Starting analysis...")
        print(f"[PROFESSIONAL_ANALYZER] Your site: {own_site_url}")
        print(f"[PROFESSIONAL_ANALYZER] Competitors: {len(competitor_urls)}")
        
        # Save your features to database
        if your_features:
            feature_store.save_your_features(your_features)
        
        # Launch a SINGLE shared browser for the entire analysis (much faster)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            try:
                # Analyze your site
                print(f"[PROFESSIONAL_ANALYZER] Analyzing YOUR site features...")
                own_features = await self._analyze_single_site_with_browser(own_site_url, browser)

                # Save your detected features
                for feature in own_features:
                    feature_store.save_your_features([feature.feature_name], feature.category)

                # Analyze competitors in parallel using the shared browser
                print(f"[PROFESSIONAL_ANALYZER] Analyzing {len(competitor_urls)} competitors in parallel...")
                competitor_tasks = [
                    self._analyze_single_site_with_browser(url, browser)
                    for url in competitor_urls
                ]
                competitor_features_list = await asyncio.gather(*competitor_tasks, return_exceptions=True)
            finally:
                await browser.close()
        
        # Store competitor features in database
        for i, features in enumerate(competitor_features_list):
            if isinstance(features, Exception):
                print(f"[ERROR] Failed to analyze {competitor_urls[i]}: {features}")
                continue
            
            url = competitor_urls[i]
            print(f"[PROFESSIONAL_ANALYZER] Found {len(features)} features on {url}")
            
            for feature in features:
                feature_store.save_feature(
                    competitor_url=url,
                    feature_name=feature.feature_name,
                    category=feature.category,
                    confidence=feature.confidence,
                    evidence=feature.evidence,
                    page_type='homepage',  # NLPFeature uses 'industry' not 'page_type'
                    priority=rule_detector.get_feature_priority(feature.feature_name)
                )\
        
        # Generate gap analysis
        print(f"[PROFESSIONAL_ANALYZER] Analyzing feature gaps...")
        gaps = feature_store.get_feature_gaps()
        
        # Detect trending features (recently added by multiple competitors)
        print(f"[PROFESSIONAL_ANALYZER] Detecting trending features...")
        trending_features = change_detector.get_trending_features(days=30)
        
        # Advanced prioritization
        print(f"[PROFESSIONAL_ANALYZER] Prioritizing features with advanced algorithm...")
        prioritized = feature_prioritizer.prioritize_features(
            gaps=gaps,
            competitor_count=len(competitor_urls),
            trending_features=trending_features
        )
        
        # Get quick wins and strategic priorities
        quick_wins = feature_prioritizer.get_quick_wins(prioritized, max_results=5)
        strategic = feature_prioritizer.get_strategic_priorities(prioritized, max_results=5)
        
        # Generate implementation roadmap
        roadmap = feature_prioritizer.generate_implementation_roadmap(prioritized)
        
        # Categorize gaps
        categorized_gaps = self._categorize_gaps(gaps)
        
        # Generate recommendations (legacy method for compatibility)
        recommendations = self._generate_recommendations(gaps)
        
        # Get change alerts
        change_alerts = change_detector.get_change_alerts(priority_threshold=70)
        
        print(f"[PROFESSIONAL_ANALYZER] ✅ Analysis complete!")
        print(f"[PROFESSIONAL_ANALYZER] Total gaps found: {len(gaps)}")
        print(f"[PROFESSIONAL_ANALYZER] High priority: {len([g for g in gaps if g['priority_score'] >= 80])}")
        print(f"[PROFESSIONAL_ANALYZER] Trending features: {len(trending_features)}")
        print(f"[PROFESSIONAL_ANALYZER] Quick wins identified: {len(quick_wins)}")
        
        return {
            "status": "success",
            "analysis_type": "professional",
            "analyzed_at": datetime.now().isoformat(),
            
            # Gap analysis
            "total_gaps": len(gaps),
            "gaps_by_category": categorized_gaps,
            "all_gaps": gaps,
            
            # Advanced prioritization
            "prioritized_features": [
                {
                    "feature_name": f.feature_name,
                    "category": f.category,
                    "priority_score": f.priority_score,
                    "adoption_rate": f.adoption_rate,
                    "complexity": f.complexity_estimate,
                    "business_impact": f.business_impact,
                    "urgency": f.urgency,
                    "reasoning": f.reasoning,
                    "recommendation": f.recommendation
                }
                for f in prioritized[:20]  # Top 20
            ],
            
            # Quick wins and strategic priorities
            "quick_wins": [
                {
                    "feature_name": f.feature_name,
                    "category": f.category,
                    "priority_score": f.priority_score,
                    "recommendation": f.recommendation
                }
                for f in quick_wins
            ],
            "strategic_priorities": [
                {
                    "feature_name": f.feature_name,
                    "category": f.category,
                    "priority_score": f.priority_score,
                    "business_impact": f.business_impact,
                    "recommendation": f.recommendation
                }
                for f in strategic
            ],
            
            # Implementation roadmap
            "roadmap": {
                "phase_1_immediate": [f.feature_name for f in roadmap["phase_1_immediate"]],
                "phase_2_short_term": [f.feature_name for f in roadmap["phase_2_short_term"]],
                "phase_3_medium_term": [f.feature_name for f in roadmap["phase_3_medium_term"]],
                "phase_4_long_term": [f.feature_name for f in roadmap["phase_4_long_term"]],
                "summary": roadmap["summary"]
            },
            
            # Trending and change detection
            "trending_features": [
                {
                    "feature_name": t["feature_name"],
                    "adoption_count": t["adoption_count"],
                    "adopters": t["adopters"],
                    "latest_adoption": t["latest_adoption"]
                }
                for t in trending_features
            ],
            "change_alerts": change_alerts,
            
            # Legacy format (for backward compatibility)
            "high_priority_gaps": [g for g in gaps if g['priority_score'] >= 80],
            "medium_priority_gaps": [g for g in gaps if 60 <= g['priority_score'] < 80],
            "low_priority_gaps": [g for g in gaps if g['priority_score'] < 60],
            "recommendations": recommendations,
            "summary": self._generate_summary(gaps, categorized_gaps, len(competitor_urls)),
            
            # Frontend Schema Compatibility (Fix for dashboard display)
            "feature_gaps": [
                {
                    "id": f"prof_feature_{i}",
                    "name": f.feature_name,
                    "description": f.reasoning,  # Use reasoning as description
                    "category": f.category,
                    "priority_score": round(f.priority_score / 10, 1), # Scale 0-100 to 0-10 for UI
                    "frequency_percentage": f.adoption_rate, # Already formatted string? no, it's "x/y" usually. Let's keep it simple.
                    "found_in": [], # detailed competitor list might be missing in prioritized object, strictly.
                    "estimated_effort": f.complexity_estimate, # "High", "Medium", "Low"
                    "complexity": f.complexity_estimate.lower(),
                    "business_impact": f.business_impact.lower(),
                    "implementation_notes": f.recommendation
                }
                for i, f in enumerate(prioritized)
            ]
        }
    
    async def _analyze_single_site_with_browser(self, url: str, browser: Browser) -> List:
        """
        Analyze a single website using a shared browser instance.
        Wraps the fetch in a per-site timeout so one hanging site never blocks the task.
        """
        try:
            content = await asyncio.wait_for(
                self._fetch_page_content_with_browser(url, browser),
                timeout=SITE_FETCH_TIMEOUT
            )
        except asyncio.TimeoutError:
            print(f"[WARNING] Timeout after {SITE_FETCH_TIMEOUT}s fetching {url} — skipping.")
            return []
        except Exception as e:
            print(f"[ERROR] Failed to analyze {url}: {e}")
            return []

        # Detect features using rule-based patterns
        rule_features = rule_detector.detect_features(content, page_type="homepage")

        # Detect features using NLP
        nlp_features = nlp_discoverer.discover_features(content, page_type="homepage")
        complementary_nlp = nlp_discoverer.get_complementary_features(nlp_features, rule_features)

        all_features = list(rule_features) + list(complementary_nlp)
        print(f"[PROFESSIONAL_ANALYZER] {url}: {len(rule_features)} rule-based + {len(complementary_nlp)} NLP = {len(all_features)} total")
        return all_features

    # Keep old method signature for backward compatibility
    async def _analyze_single_site(self, url: str) -> List:
        """Fallback: launches its own browser (used only if called without a shared browser)."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            try:
                return await self._analyze_single_site_with_browser(url, browser)
            finally:
                await browser.close()

    async def _fetch_page_content_with_browser(self, url: str, browser: Browser) -> str:
        """
        Fetch page content using a shared Playwright browser.
        Uses a new isolated context per URL to avoid cookie/session bleed.
        """
        print(f"[PROFESSIONAL_ANALYZER] Fetching {url}...")
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            java_script_enabled=True,
        )
        page = await context.new_page()
        try:
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=25000)
                await page.wait_for_timeout(2000)  # Let JS settle
            except Exception as e:
                print(f"[WARNING] Page load issue for {url}: {e}")

            content = await page.content()
            try:
                text_content = await page.evaluate("() => document.body?.innerText || ''")
            except Exception:
                text_content = ""

            return content + "\n\n" + text_content
        finally:
            await context.close()

    # Legacy method kept for external callers
    async def _fetch_page_content(self, url: str) -> str:
        """Fallback fetch that creates its own browser (slow — prefer _fetch_page_content_with_browser)."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            try:
                return await self._fetch_page_content_with_browser(url, browser)
            finally:
                await browser.close()
    
    def _categorize_gaps(self, gaps: List[Dict]) -> Dict[str, int]:
        """Group gaps by category with counts."""
        categorized = {}
        for gap in gaps:
            category = gap["category"]
            categorized[category] = categorized.get(category, 0) + 1
        return categorized
    
    def _generate_recommendations(self, gaps: List[Dict]) -> List[Dict]:
        """
        Generate actionable recommendations from gaps.
        
        Args:
            gaps: List of feature gaps
            
        Returns:
            List of prioritized recommendations
        """
        recommendations = []
        
        for gap in gaps[:20]:  # Top 20 gaps
            recommendation = {
                "feature": gap["feature_name"],
                "category": gap["category"],
                "priority": "critical" if gap["priority_score"] >= 85 else 
                           "high" if gap["priority_score"] >= 70 else "medium",
                "adoption_rate": f"{gap['competitor_count']}/{len(gap['competitors_with'])} competitors",
                "competitor_count": gap["competitor_count"],
                "why": self._generate_reason(gap),
                "evidence": gap["evidence"][:2]  # Top 2 evidence
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_reason(self, gap: Dict) -> str:
        """Generate reasoning for why this feature is important."""
        count = gap["competitor_count"]
        category = gap["category"]
        feature = gap["feature_name"]
        
        if count >= 3:
            return f"All {count} competitors offer {feature}. Industry standard for {category}."
        elif count == 2:
            return f"2 out of 3 competitors have {feature}. Becoming a common expectation."
        elif category == "Payment":
            return f"Payment feature that improves checkout conversion."
        elif category == "Delivery":
            return f"Delivery option that enhances customer satisfaction."
        elif category == "Trust":
            return f"Trust signal that increases buyer confidence."
        else:
            return f"Competitive feature in {category} category."
    
    def _generate_summary(self, gaps: List[Dict], categorized: Dict[str, int], competitor_count: int) -> Dict:
        """Generate executive summary."""
        total_gaps = len(gaps)
        critical_gaps = len([g for g in gaps if g['priority_score'] >= 85])
        
        # Top missing categories
        top_categories = sorted(categorized.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_gaps": total_gaps,
            "critical_gaps": critical_gaps,
            "total_competitors": competitor_count,
            "top_missing_categories": [
                {"category": cat, "count": count} 
                for cat, count in top_categories
            ],
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"Found {total_gaps} feature gaps across {len(categorized)} categories. "
                      f"{critical_gaps} are high priority."
        }


# Global instance
professional_analyzer = ProfessionalCompetitiveAnalyzer()
