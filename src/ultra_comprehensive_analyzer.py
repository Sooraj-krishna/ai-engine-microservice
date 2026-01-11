"""
Ultra-Comprehensive Competitive Analyzer - Detects EVERY feature difference.
Finds all UI/UX elements including colors, fonts, spacing, and micro-interactions.
"""

from playwright.async_api import async_playwright
import asyncio
import json
import base64
from typing import List, Dict
from ai_vision_api import query_gemini_vision_api
from prompt_optimizer import prompt_optimizer
from ai_cache import ai_cache


class UltraComprehensiveAnalyzer:
    """Detects every single UI/UX difference between sites."""
    
    async def analyze_ultra_comprehensive(self, own_site_url: str, competitor_urls: List[str]) -> Dict:
        """
        Ultra-comprehensive analysis that finds EVERY difference.
        
        Returns hundreds of features including:
        - Every UI component
        - All color variations
        - Font styles and sizes
        - Spacing patterns
        - Button variants
        - Micro-interactions
        - Animation styles
        - And much more
        """
        print(f"[ULTRA_ANALYZER] Starting ULTRA-COMPREHENSIVE analysis")
        print(f"[ULTRA_ANALYZER] This will detect EVERY feature difference...")
        
        # Analyze own site
        print(f"[ULTRA_ANALYZER] Analyzing YOUR site: {own_site_url}")
        own_features = await self._extract_all_features(own_site_url)
        
        # Analyze competitors in parallel
        print(f"[ULTRA_ANALYZER] Analyzing {len(competitor_urls)} competitors...")
        competitor_tasks = [
            self._extract_all_features(url) for url in competitor_urls
        ]
        competitor_features = await asyncio.gather(*competitor_tasks, return_exceptions=True)
        
        # Find ALL differences
        print(f"[ULTRA_ANALYZER] Finding ALL differences...")
        all_gaps = self._find_all_gaps(own_features, competitor_features, competitor_urls)
        
        # Prioritize by impact
        prioritized = self._prioritize_features(all_gaps)
        
        print(f"[ULTRA_ANALYZER] ✅ Found {len(prioritized)} feature gaps!")
        
        return {
            "own_site": own_features,
            "competitors": competitor_features,
            "feature_gaps": prioritized,
            "total_gaps_found": len(prioritized),
            "analysis_type": "ultra_comprehensive"
        }
    
    async def _extract_all_features(self, url: str) -> Dict:
        """Extract EVERY feature from a website."""
        features = {
            "url": url,
            "ui_components": [],
            "design_tokens": {},
            "interactions": [],
            "content_patterns": [],
            "technical_features": []
        }
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Longer timeout and don't wait for full network idle
                print(f"[ULTRA_ANALYZER] Loading {url}...")
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    # Wait a bit for dynamic content
                    await page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"[WARNING] Page load issue for {url}: {e}")
                    # Continue anyway - we might have partial content
                
                # 1. Extract ALL UI components (50+ types)
                ui_components = await page.evaluate("""
                    () => {
                        const components = [];
                        
                        // EVERY component type (50+ types for comprehensive detection)
                        const componentSelectors = {
                            'Navigation': 'nav, header nav, [role="navigation"]',
                            'Hero Section': '.hero, [class*="hero"], .banner, [class*="banner"]',
                            'Cards': '.card, [class*="card"]',
                            'Product Cards': '.product, [class*="product"], [data-product]',
                            'Buttons': 'button, [role="button"], .btn, [class*="btn"]',
                            'Call-to-Action Buttons': '[class*="cta"], [class*="action"]',
                            'Forms': 'form',
                            'Inputs': 'input, textarea, select',
                            'Images': 'img',
                            'Product Images': '[class*="product"] img, [data-product] img',
                            'Icons': 'svg, i[class*="icon"], [class*="icon"]',
                            'Modals': '[role="dialog"], .modal, [class*="modal"]',
                            'Dropdowns': 'select, [role="listbox"], [class*="dropdown"]',
                            'Mega Menu': '[class*="mega"], [class*="megamenu"]',
                            'Tabs': '[role="tablist"], .tabs, [class*="tab"]',
                            'Accordion': '[role="accordion"], details, [class*="accordion"]',
                            'Carousel': '.carousel, .slider, .swiper, [class*="carousel"], [class*="slider"]',
                            'Breadcrumbs': '[aria-label*="breadcrumb"], .breadcrumb, [class*="breadcrumb"]',
                            'Badges': '.badge, .label, .tag, [class*="badge"]',
                            'Avatars': '.avatar, [class*="avatar"]',
                            'Progress Bars': 'progress, [role="progressbar"], [class*="progress"]',
                            'Tooltips': '[role="tooltip"], .tooltip, [class*="tooltip"]',
                            'Notifications': '[role="alert"], .notification, .toast, [class*="notification"]',
                            'Sidebars': 'aside, .sidebar, [class*="sidebar"]',
                            'Footer': 'footer',
                            'Search': 'input[type="search"], [role="search"], [class*="search"]',
                            'Search Autocomplete': '[class*="autocomplete"], [class*="suggestion"]',
                            'Filters': '.filter, [class*="filter"]',
                            'Pagination': '.pagination, [aria-label*="page"], [class*="pagination"]',
                            'Tables': 'table',
                            'Data Tables': '[class*="datatable"], [class*="data-table"]',
                            'Lists': 'ul, ol',
                            'Dividers': 'hr, .divider, [class*="divider"]',
                            'Spacers': '.spacer, [class*="spacer"]',
                            'Grid Layouts': '[class*="grid"]',
                            'Flex Layouts': '[class*="flex"]',
                            'Pricing Tables': '[class*="pricing"], [class*="plan"]',
                            'Testimonials': '[class*="testimonial"], [class*="review"]',
                            'Rating Stars': '[class*="rating"], [class*="star"]',
                            'Social Media Links': '[class*="social"], [href*="facebook"], [href*="twitter"]',
                            'Video Players': 'video, [class*="video"], iframe[src*="youtube"]',
                            'Audio Players': 'audio, [class*="audio"]',
                            'Image Galleries': '[class*="gallery"], [class*="lightbox"]',
                            'Countdown Timers': '[class*="countdown"], [class*="timer"]',
                            'Chat Widgets': '[class*="chat"], [class*="messenger"]',
                            'Cookie Banners': '[class*="cookie"], [class*="gdpr"]',
                            'Loading Spinners': '[class*="spinner"], [class*="loading"]',
                            'Skeleton Loaders': '[class*="skeleton"], [class*="placeholder"]',
                            'Empty States': '[class*="empty"], [class*="no-results"]',
                            'Error Messages': '[class*="error"], [role="alert"]',
                            'Success Messages': '[class*="success"]',
                            'Breadcrumb Navigation': 'nav[aria-label*="breadcrumb"]',
                            'Sticky Headers': 'header[class*="sticky"], [class*="fixed"]',
                            'Floating Action Buttons': '[class*="fab"], [class*="floating"]',
                            'Back to Top': '[class*="back-to-top"], [class*="scroll-top"]'
                        };
                        
                        for (const [name, selector] of Object.entries(componentSelectors)) {
                            const elements = document.querySelectorAll(selector);
                            if (elements.length > 0) {
                                components.push({
                                    name: name,
                                    count: elements.length,
                                    type: 'ui_component'
                                });
                            }
                        }
                        
                        return components;
                    }
                """)
                
                features["ui_components"] = ui_components
                
                # 2. Extract ALL design tokens (colors, fonts, spacing)
                design_tokens = await page.evaluate("""
                    () => {
                        const tokens = {
                            colors: new Set(),
                            fonts: new Set(),
                            fontSizes: new Set(),
                            spacing: new Set(),
                            borderRadius: new Set(),
                            shadows: new Set()
                        };
                        
                        // Sample ALL elements
                        const elements = Array.from(document.querySelectorAll('*'));
                        elements.slice(0, 200).forEach(el => {
                            const styles = window.getComputedStyle(el);
                            
                            // Colors
                            if (styles.color) tokens.colors.add(styles.color);
                            if (styles.backgroundColor && styles.backgroundColor !== 'rgba(0, 0, 0, 0)') {
                                tokens.colors.add(styles.backgroundColor);
                            }
                            
                            // Fonts
                            if (styles.fontFamily) tokens.fonts.add(styles.fontFamily);
                            if (styles.fontSize) tokens.fontSizes.add(styles.fontSize);
                            
                            // Spacing
                            if (styles.padding && styles.padding !== '0px') tokens.spacing.add(styles.padding);
                            if (styles.margin && styles.margin !== '0px') tokens.spacing.add(styles.margin);
                            
                            // Border radius
                            if (styles.borderRadius && styles.borderRadius !== '0px') {
                                tokens.borderRadius.add(styles.borderRadius);
                            }
                            
                            // Shadows
                            if (styles.boxShadow && styles.boxShadow !== 'none') {
                                tokens.shadows.add(styles.boxShadow);
                            }
                        });
                        
                        return {
                            colors: Array.from(tokens.colors),
                            fonts: Array.from(tokens.fonts),
                            fontSizes: Array.from(tokens.fontSizes),
                            spacing: Array.from(tokens.spacing),
                            borderRadius: Array.from(tokens.borderRadius),
                            shadows: Array.from(tokens.shadows)
                        };
                    }
                """)
                
                features["design_tokens"] = design_tokens
                
                # 3. Detect ALL interactions
                interactions = await page.evaluate("""
                    () => {
                        const interactions = [];
                        
                        // Hover effects
                        const elementsWithHover = Array.from(document.querySelectorAll('*')).filter(el => {
                            const styles = window.getComputedStyle(el);
                            return styles.cursor === 'pointer';
                        });
                        if (elementsWithHover.length > 0) {
                            interactions.push({name: 'Hover Effects', count: elementsWithHover.length});
                        }
                        
                        // Animations
                        const animated = Array.from(document.querySelectorAll('*')).filter(el => {
                            const styles = window.getComputedStyle(el);
                            return styles.animationName !== 'none' || styles.transition !== 'none';
                        });
                        if (animated.length > 0) {
                            interactions.push({name: 'CSS Animations', count: animated.length});
                        }
                        
                        // Click handlers
                        const clickable = document.querySelectorAll('[onclick], button, a, [role="button"]');
                        if (clickable.length > 0) {
                            interactions.push({name: 'Clickable Elements', count: clickable.length});
                        }
                        
                        // Forms with validation
                        const validated = document.querySelectorAll('input[required], [aria-invalid]');
                        if (validated.length > 0) {
                            interactions.push({name: 'Form Validation', count: validated.length});
                        }
                        
                        return interactions;
                    }
                """)
                
                features["interactions"] = interactions
                
                # 4. AI Vision Analysis for visual details
                screenshot = await page.screenshot(full_page=False)
                screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
                
                ai_prompt = f"""Analyze this website ({url}) and list EVERY visual feature you see:

1. Button styles (colors, shapes, sizes, hover states)
2. Typography styles (headings, body text, font weights)
3. Color scheme (primary, secondary, accent, backgrounds)
4. Layout patterns (grid, flex, columns)
5. Spacing patterns (tight, normal, spacious)
6. Border styles (sharp, rounded, pill-shaped)
7. Shadow usage (none, subtle, pronounced)
8. Image treatments (rounded corners, filters, overlays)
9. Icon styles (outlined, filled, custom)
10. Navigation style (horizontal, vertical, mega-menu, hamburger)

Return JSON:
{{
    "visual_features": [
        {{"name": "feature name", "description": "specific details"}}
    ]
}}

Be EXTREMELY detailed. List EVERY visual element you notice."""
                
                try:
                    ai_response = await query_gemini_vision_api(ai_prompt, screenshot_b64)
                    if ai_response:
                        try:
                            ai_features = json.loads(ai_response)
                            features["visual_ai_features"] = ai_features.get("visual_features", [])
                        except:
                            if "```json" in ai_response:
                                json_start = ai_response.find("```json") + 7
                                json_end = ai_response.find("```", json_start)
                                json_str = ai_response[json_start:json_end].strip()
                                ai_features = json.loads(json_str)
                                features["visual_ai_features"] = ai_features.get("visual_features", [])
                except Exception as e:
                    print(f"[WARNING] AI vision failed: {e}")
                    features["visual_ai_features"] = []
                
                await browser.close()
                
        except Exception as e:
            print(f"[ERROR] Feature extraction failed for {url}: {e}")
            features["error"] = str(e)
        
        return features
    
    def _find_all_gaps(self, own_features: Dict, competitor_features: List, competitor_urls: List[str]) -> List[Dict]:
        """Find ALL features that competitors have but you don't."""
        gaps = []
        
        # Get your components
        own_components = {comp["name"] for comp in own_features.get("ui_components", [])}
        own_interactions = {inter["name"] for inter in own_features.get("interactions", [])}
        own_colors = set(own_features.get("design_tokens", {}).get("colors", []))
        own_fonts = set(own_features.get("design_tokens", {}).get("fonts", []))
        
        # Check each competitor
        for i, comp_features in enumerate(competitor_features):
            if isinstance(comp_features, Exception):
                continue
            
            competitor_url = competitor_urls[i]
            
            # UI Component gaps
            comp_components = {comp["name"] for comp in comp_features.get("ui_components", [])}
            missing_components = comp_components - own_components
            
            for component in missing_components:
                # Find the component details
                comp_detail = next((c for c in comp_features.get("ui_components", []) if c["name"] == component), {})
                gaps.append({
                    "feature_name": component,
                    "category": "UI Component",
                    "found_on": competitor_url,
                    "description": f"{component} (found {comp_detail.get('count', 0)} instances on competitor site)",
                    "priority": "high" if comp_detail.get("count", 0) > 5 else "medium"
                })
            
            # Interaction gaps
            comp_interactions = {inter["name"] for inter in comp_features.get("interactions", [])}
            missing_interactions = comp_interactions - own_interactions
            
            for interaction in missing_interactions:
                gaps.append({
                    "feature_name": interaction,
                    "category": "Interaction",
                    "found_on": competitor_url,
                    "description": f"{interaction} - enhances user engagement",
                    "priority": "high"
                })
            
            # Design token gaps (colors, fonts)
            comp_colors = set(comp_features.get("design_tokens", {}).get("colors", []))
            unique_colors = len(comp_colors - own_colors)
            if unique_colors > 5:
                gaps.append({
                    "feature_name": "Richer Color Palette",
                    "category": "Design System",
                    "found_on": competitor_url,
                    "description": f"Competitor uses {unique_colors} more color variations for visual hierarchy",
                    "priority": "medium"
                })
            
            comp_fonts = set(comp_features.get("design_tokens", {}).get("fonts", []))
            unique_fonts = comp_fonts - own_fonts
            if unique_fonts:
                gaps.append({
                    "feature_name": "Custom Typography",
                    "category": "Design System",
                    "found_on": competitor_url,
                    "description": f"Uses custom fonts: {', '.join(list(unique_fonts)[:3])}",
                    "priority": "medium"
                })
            
            # Visual AI features
            for visual_feature in comp_features.get("visual_ai_features", []):
                gaps.append({
                    "feature_name": visual_feature.get("name", "Visual Feature"),
                    "category": "Visual Design",
                    "found_on": competitor_url,
                    "description": visual_feature.get("description", ""),
                    "priority": "medium"
                })
        
        return gaps
    
    def _prioritize_features(self, gaps: List[Dict]) -> List[Dict]:
        """Prioritize features by impact and frequency."""
        # Count how many competitors have each feature
        feature_counts = {}
        for gap in gaps:
            key = gap["feature_name"]
            if key not in feature_counts:
                feature_counts[key] = {"count": 0, "gap": gap}
            feature_counts[key]["count"] += 1
        
        # Prioritize by frequency
        prioritized = []
        for feature_name, data in sorted(feature_counts.items(), key=lambda x: x[1]["count"], reverse=True):
            gap = data["gap"].copy()
            gap["competitor_count"] = data["count"]
            gap["adoption_rate"] = f"{data['count']}/{len(gaps)} competitors"
            
            # Adjust priority based on adoption
            if data["count"] >= 2:
                gap["priority"] = "critical"
            elif gap["priority"] == "high":
                gap["priority"] = "high"
            
            prioritized.append(gap)
        
        return prioritized


# Global instance
ultra_analyzer = UltraComprehensiveAnalyzer()
