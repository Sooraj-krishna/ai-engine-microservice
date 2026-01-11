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

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
from typing import List, Dict
from datetime import datetime
from rule_based_feature_detector import rule_detector
from feature_store import feature_store
from nlp_feature_discovery import nlp_discoverer
from change_detector import change_detector
from feature_prioritizer import feature_prioritizer


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
        
        # Analyze your site
        print(f"[PROFESSIONAL_ANALYZER] Analyzing YOUR site features...")
        own_features = await self._analyze_single_site(own_site_url)
        
        # Save your detected features
        for feature in own_features:
            feature_store.save_your_features([feature.feature_name], feature.category)
        
        # Analyze competitors in parallel
        print(f"[PROFESSIONAL_ANALYZER] Analyzing {len(competitor_urls)} competitors in parallel...")
        competitor_tasks = []
        for url in competitor_urls:
            competitor_tasks.append(self._analyze_single_site(url))
        
        competitor_features_list = await asyncio.gather(*competitor_tasks, return_exceptions=True)
        
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
            "summary": self._generate_summary(gaps, categorized_gaps)
        }
    
    async def _analyze_single_site(self, url: str) -> List:
        """
        Analyze a single website for business features.
        
        Args:
            url: Website URL to analyze
            
        Returns:
            List of detected features
        """
        try:
            # Fetch page content
            content = await self._fetch_page_content(url)
            
            # Detect features using rule-based patterns
            rule_features = rule_detector.detect_features(content, page_type="homepage")
            
            # Detect features using NLP (discovers features missed by rules)
            nlp_features = nlp_discoverer.discover_features(content, page_type="homepage")
            
            # Combine: Get NLP features that complement (don't overlap) rule-based features
            complementary_nlp = nlp_discoverer.get_complementary_features(nlp_features, rule_features)
            
            # Merge features
            all_features = list(rule_features) + list(complementary_nlp)
            
            print(f"[PROFESSIONAL_ANALYZER] {url}: {len(rule_features)} rule-based + {len(complementary_nlp)} NLP = {len(all_features)} total")
            
            return all_features
            
        except Exception as e:
            print(f"[ERROR] Failed to analyze {url}: {e}")
            return []
    
    async def _fetch_page_content(self, url: str) -> str:
        """
        Fetch page content using Playwright.
        
        Args:
            url: URL to fetch
            
        Returns:
            Page HTML content
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                print(f"[PROFESSIONAL_ANALYZER] Fetching {url}...")
                
                # Load page with reasonable timeout
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    await page.wait_for_timeout(3000)  # Wait for dynamic content
                except Exception as e:
                    print(f"[WARNING] Page load issue for {url}: {e}")
                
                # Get page content
                content = await page.content()
                
                # Also get visible text (better for feature detection)
                text_content = await page.evaluate("""
                    () => {
                        return document.body.innerText;
                    }
                """)
                
                await browser.close()
                
                # Combine HTML and text for better detection
                return content + "\n\n" + text_content
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            raise
    
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
    
    def _generate_summary(self, gaps: List[Dict], categorized: Dict[str, int]) -> Dict:
        """Generate executive summary."""
        total_gaps = len(gaps)
        critical_gaps = len([g for g in gaps if g['priority_score'] >= 85])
        
        # Top missing categories
        top_categories = sorted(categorized.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_gaps": total_gaps,
            "critical_gaps": critical_gaps,
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
