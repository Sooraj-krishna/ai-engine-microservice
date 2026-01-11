"""
Premium Analyzer - Advanced competitive analysis with SEO, accessibility,
technical stack detection, user flows, content strategy, and pricing analysis.
"""

from playwright.async_api import async_playwright, Page
from ai_vision_api import query_gemini_vision_api
import json
import re
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import base64


class PremiumAnalyzer:
    """Premium-tier competitive analysis with advanced features."""
    
    def __init__(self):
        self.mobile_viewports = [
            {"width": 375, "height": 667, "name": "iPhone SE"},
            {"width": 414, "height": 896, "name": "iPhone 14 Pro Max"}
        ]
    
    async def analyze_premium(self, url: str) -> Dict:
        """
        Perform premium analysis on a website.
        
        Args:
            url: Website URL to analyze
            
        Returns:
            Comprehensive premium analysis results
        """
        print(f"[PREMIUM_ANALYZER] Starting premium analysis for: {url}")
        
        analysis = {
            "url": url,
            "analysis_date": datetime.now().isoformat(),
            "seo": {},
            "accessibility": {},
            "technical_stack": {},
            "user_flows": {},
            "content_strategy": {},
            "mobile": {},
            "pricing": {}
        }
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Navigate to site
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Take screenshot once for content strategy analysis
                screenshot = await page.screenshot(full_page=False)
                
                # Run all analyses IN PARALLEL for maximum performance
                print(f"[PREMIUM_ANALYZER] Running all analyses in parallel...")
                results = await asyncio.gather(
                    self._analyze_seo(page, url),
                    self._analyze_accessibility(page),
                    self._detect_tech_stack(page),
                    self._analyze_user_flows(page),
                    self._analyze_content_strategy(page, screenshot, url),
                    self._analyze_pricing(page),
                    return_exceptions=True  # Don't fail completely if one analysis fails
                )
                
                # Assign results (handle exceptions gracefully)
                seo_result, a11y_result, tech_result, flows_result, content_result, pricing_result = results
                
                analysis["seo"] = seo_result if not isinstance(seo_result, Exception) else {"error": str(seo_result)}
                analysis["accessibility"] = a11y_result if not isinstance(a11y_result, Exception) else {"error": str(a11y_result)}
                analysis["technical_stack"] = tech_result if not isinstance(tech_result, Exception) else {"error": str(tech_result)}
                analysis["user_flows"] = flows_result if not isinstance(flows_result, Exception) else {"error": str(flows_result)}
                analysis["content_strategy"] = content_result if not isinstance(content_result, Exception) else {"error": str(content_result)}
                analysis["pricing"] = pricing_result if not isinstance(pricing_result, Exception) else {"error": str(pricing_result)}
                
                # Mobile analysis requires new browser pages, run separately
                print(f"[PREMIUM_ANALYZER] Testing mobile experience...")
                analysis["mobile"] = await self._analyze_mobile(browser, url)
                
                await browser.close()
                
        except Exception as e:
            print(f"[ERROR] Premium analysis failed for {url}: {e}")
            analysis["error"] = str(e)
        
        print(f"[PREMIUM_ANALYZER] Premium analysis complete for {url}")
        return analysis
    
    async def _analyze_seo(self, page: Page, url: str) -> Dict:
        """Comprehensive SEO analysis."""
        seo = {
            "meta_tags": {},
            "open_graph": {},
            "twitter_cards": {},
            "structured_data": [],
            "heading_hierarchy": {},
            "canonical_url": None,
            "hreflang": [],
            "robots_meta": None,
            "sitemap_detected": False,
            "seo_score": 0
        }
        
        try:
            # Extract meta tags
            meta_data = await page.evaluate("""
                () => {
                    const meta = {
                        title: document.title,
                        description: document.querySelector('meta[name="description"]')?.content || '',
                        keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                        robots: document.querySelector('meta[name="robots"]')?.content || '',
                        canonical: document.querySelector('link[rel="canonical"]')?.href || '',
                        og: {},
                        twitter: {},
                        hreflang: []
                    };
                    
                    // Open Graph tags
                    document.querySelectorAll('meta[property^="og:"]').forEach(tag => {
                        const property = tag.getAttribute('property').replace('og:', '');
                        meta.og[property] = tag.content;
                    });
                    
                    // Twitter Card tags
                    document.querySelectorAll('meta[name^="twitter:"]').forEach(tag => {
                        const name = tag.getAttribute('name').replace('twitter:', '');
                        meta.twitter[name] = tag.content;
                    });
                    
                    // Hreflang tags
                    document.querySelectorAll('link[rel="alternate"][hreflang]').forEach(link => {
                        meta.hreflang.push({
                            lang: link.getAttribute('hreflang'),
                            href: link.href
                        });
                    });
                    
                    // Heading hierarchy
                    const headings = {h1: 0, h2: 0, h3: 0, h4: 0, h5: 0, h6: 0};
                    ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].forEach(tag => {
                        headings[tag] = document.querySelectorAll(tag).length;
                    });
                    meta.headings = headings;
                    
                    return meta;
                }
            """)
            
            seo["meta_tags"] = {
                "title": meta_data.get("title", ""),
                "description": meta_data.get("description", ""),
                "keywords": meta_data.get("keywords", ""),
                "title_length": len(meta_data.get("title", "")),
                "description_length": len(meta_data.get("description", ""))
            }
            
            seo["open_graph"] = meta_data.get("og", {})
            seo["twitter_cards"] = meta_data.get("twitter", {})
            seo["canonical_url"] = meta_data.get("canonical")
            seo["hreflang"] = meta_data.get("hreflang", [])
            seo["robots_meta"] = meta_data.get("robots")
            seo["heading_hierarchy"] = meta_data.get("headings", {})
            
            # Extract structured data (JSON-LD)
            structured_data = await page.evaluate("""
                () => {
                    const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
                    return scripts.map(script => {
                        try {
                            return JSON.parse(script.textContent);
                        } catch {
                            return null;
                        }
                    }).filter(data => data !== null);
                }
            """)
            seo["structured_data"] = structured_data
            
            # Check for sitemap
            try:
                sitemap_url = f"{url.rstrip('/')}/sitemap.xml"
                sitemap_response = await page.goto(sitemap_url, wait_until='networkidle', timeout=5000)
                seo["sitemap_detected"] = sitemap_response.status == 200
            except:
                seo["sitemap_detected"] = False
            
            # Calculate SEO score (0-100)
            score = 0
            if seo["meta_tags"]["title"]: score += 15
            if 30 <= seo["meta_tags"]["title_length"] <= 60: score += 10
            if seo["meta_tags"]["description"]: score += 15
            if 120 <= seo["meta_tags"]["description_length"] <= 160: score += 10
            if seo["open_graph"]: score += 15
            if seo["structured_data"]: score += 15
            if seo["canonical_url"]: score += 10
            if seo["heading_hierarchy"].get("h1", 0) == 1: score += 10  # Exactly one H1
            
            seo["seo_score"] = score
            
        except Exception as e:
            print(f"[ERROR] SEO analysis failed: {e}")
        
        return seo
    
    async def _analyze_accessibility(self, page: Page) -> Dict:
        """Accessibility audit."""
        accessibility = {
            "aria_usage": {},
            "semantic_html": {},
            "alt_text_coverage": {},
            "color_contrast": [],
            "keyboard_navigation": {},
            "accessibility_score": 0,
            "wcag_issues": []
        }
        
        try:
            a11y_data = await page.evaluate("""
                () => {
                    const data = {
                        aria: {
                            labels: document.querySelectorAll('[aria-label]').length,
                            describedby: document.querySelectorAll('[aria-describedby]').length,
                            hidden: document.querySelectorAll('[aria-hidden]').length,
                            live: document.querySelectorAll('[aria-live]').length,
                            roles: document.querySelectorAll('[role]').length
                        },
                        semantic: {
                            nav: document.querySelectorAll('nav').length,
                            header: document.querySelectorAll('header').length,
                            footer: document.querySelectorAll('footer').length,
                            main: document.querySelectorAll('main').length,
                            article: document.querySelectorAll('article').length,
                            section: document.querySelectorAll('section').length,
                            aside: document.querySelectorAll('aside').length
                        },
                        images: {
                            total: document.querySelectorAll('img').length,
                            with_alt: document.querySelectorAll('img[alt]').length,
                            with_empty_alt: document.querySelectorAll('img[alt=""]').length
                        },
                        forms: {
                            labels: document.querySelectorAll('label').length,
                            inputs: document.querySelectorAll('input, textarea, select').length,
                            required: document.querySelectorAll('[required]').length
                        },
                        keyboard: {
                            tabindex_positive: document.querySelectorAll('[tabindex]:not([tabindex="-1"]):not([tabindex="0"])').length,
                            focusable: document.querySelectorAll('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])').length
                        }
                    };
                    
                    // Sample text elements for contrast check
                    const textElements = [];
                    const samples = Array.from(document.querySelectorAll('p, h1, h2, h3, a, button, span')).slice(0, 20);
                    samples.forEach(el => {
                        const styles = window.getComputedStyle(el);
                        const color = styles.color;
                        const bgColor = styles.backgroundColor;
                        const fontSize = styles.fontSize;
                        
                        if (color && bgColor && bgColor !== 'rgba(0, 0, 0, 0)') {
                            textElements.push({
                                color: color,
                                backgroundColor: bgColor,
                                fontSize: fontSize,
                                tagName: el.tagName.toLowerCase()
                            });
                        }
                    });
                    data.textSamples = textElements;
                    
                    return data;
                }
            """)
            
            accessibility["aria_usage"] = a11y_data.get("aria", {})
            accessibility["semantic_html"] = a11y_data.get("semantic", {})
            
            # Alt text coverage
            images = a11y_data.get("images", {})
            total_images = images.get("total", 0)
            with_alt = images.get("with_alt", 0)
            alt_coverage = (with_alt / total_images * 100) if total_images > 0 else 100
            
            accessibility["alt_text_coverage"] = {
                "total_images": total_images,
                "images_with_alt": with_alt,
                "coverage_percentage": round(alt_coverage, 1)
            }
            
            # Keyboard navigation
            keyboard = a11y_data.get("keyboard", {})
            accessibility["keyboard_navigation"] = {
                "focusable_elements": keyboard.get("focusable", 0),
                "positive_tabindex_count": keyboard.get("tabindex_positive", 0),
                "has_skip_link": False  # Could be enhanced
            }
            
            # Color contrast (simplified - full calculation would need color parsing)
            text_samples = a11y_data.get("textSamples", [])
            accessibility["color_contrast"] = {
                "samples_checked": len(text_samples),
                "note": "Full contrast ratio calculation requires color parsing library"
            }
            
            # Calculate accessibility score
            score = 0
            if accessibility["aria_usage"].get("labels", 0) > 0: score += 15
            if accessibility["semantic_html"].get("main", 0) > 0: score += 10
            if accessibility["semantic_html"].get("nav", 0) > 0: score += 10
            if alt_coverage >= 90: score += 20
            elif alt_coverage >= 70: score += 10
            if accessibility["aria_usage"].get("roles", 0) > 5: score += 15
            if keyboard.get("positive_tabindex", 0) == 0: score += 10  # No positive tabindex is good
            if keyboard.get("focusable", 0) > 10: score += 10
            
            # WCAG issues
            issues = []
            if images.get("total", 0) > 0 and alt_coverage < 80:
                issues.append({"level": "A", "issue": f"Only {alt_coverage:.0f}% of images have alt text"})
            if keyboard.get("tabindex_positive", 0) > 0:
                issues.append({"level": "A", "issue": "Positive tabindex values detected (avoid using)"})
            if accessibility["semantic_html"].get("main", 0) == 0:
                issues.append({"level": "AA", "issue": "No <main> landmark found"})
            
            accessibility["wcag_issues"] = issues
            accessibility["accessibility_score"] = min(100, score)
            
        except Exception as e:
            print(f"[ERROR] Accessibility analysis failed: {e}")
        
        return accessibility
    
    async def _detect_tech_stack(self, page: Page) -> Dict:
        """Detect technical stack and frameworks."""
        tech_stack = {
            "frameworks": [],
            "libraries": [],
            "build_tools": [],
            "css_frameworks": [],
            "analytics": [],
            "cdn": [],
            "hosting": None,
            "server_info": {}
        }
        
        try:
            detection = await page.evaluate("""
                () => {
                    const detected = {
                        frameworks: [],
                        libraries: [],
                        css: [],
                        meta: []
                    };
                    
                    // Check window object for frameworks
                    if (window.React || document.querySelector('[data-reactroot], [data-react-root]')) {
                        detected.frameworks.push('React');
                    }
                    if (window.Vue || document.querySelector('[data-v-]')) {
                        detected.frameworks.push('Vue.js');
                    }
                    if (window.angular || document.querySelector('[ng-app], [ng-version]')) {
                        detected.frameworks.push('Angular');
                    }
                    if (window.Svelte) {
                        detected.frameworks.push('Svelte');
                    }
                    if (document.querySelector('meta[name="next-head-count"]')) {
                        detected.frameworks.push('Next.js');
                    }
                    if (document.querySelector('meta[name="nuxt-version"]')) {
                        detected.frameworks.push('Nuxt.js');
                    }
                    if (document.querySelector('[data-gatsby]')) {
                        detected.frameworks.push('Gatsby');
                    }
                    
                    // Check for libraries
                    if (window.jQuery || window.$) detected.libraries.push('jQuery');
                    if (window.gsap) detected.libraries.push('GSAP');
                    if (window.Swiper) detected.libraries.push('Swiper');
                    if (window.AOS) detected.libraries.push('AOS (Animate On Scroll)');
                    
                    // CSS frameworks
                    const html = document.documentElement.outerHTML;
                    if (html.includes('bootstrap') || document.querySelector('[class*="bootstrap"]')) {
                        detected.css.push('Bootstrap');
                    }
                    if (html.includes('tailwind') || document.querySelector('[class*="tw-"]')) {
                        detected.css.push('Tailwind CSS');
                    }
                    if (html.includes('material-ui') || html.includes('mui')) {
                        detected.css.push('Material-UI');
                    }
                    
                    // Get meta generator
                    const generator = document.querySelector('meta[name="generator"]')?.content;
                    if (generator) detected.meta.push(generator);
                    
                    return detected;
                }
            """)
            
            tech_stack["frameworks"] = detection.get("frameworks", [])
            tech_stack["libraries"] = detection.get("libraries", [])
            tech_stack["css_frameworks"] = detection.get("css", [])
            
            # Check for analytics and CDN from network requests
            # This would require monitoring network traffic, simplified here
            
        except Exception as e:
            print(f"[ERROR] Tech stack detection failed: {e}")
        
        return tech_stack
    
    async def _analyze_user_flows(self, page: Page) -> Dict:
        """Analyze user flows and conversion funnels."""
        flows = {
            "signup_flow": {},
            "cta_analysis": {},
            "forms": [],
            "conversion_elements": []
        }
        
        try:
            flow_data = await page.evaluate("""
                () => {
                    const data = {
                        ctas: [],
                        forms: [],
                        auth_elements: []
                    };
                    
                    // Find CTAs
                    const ctaSelectors = ['button', 'a[class*="btn"]', 'a[class*="cta"]', '[class*="button"]'];
                    ctaSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => {
                            const text = el.textContent.trim().toLowerCase();
                            if (text.includes('sign up') || text.includes('get started') || 
                                text.includes('try') || text.includes('buy') || text.includes('subscribe')) {
                                data.ctas.push({
                                    text: el.textContent.trim(),
                                    type: el.tagName.toLowerCase(),
                                    classes: el.className
                                });
                            }
                        });
                    });
                    
                    // Analyze forms
                    document.querySelectorAll('form').forEach(form => {
                        const inputs = form.querySelectorAll('input, textarea, select').length;
                        const hasEmail = !!form.querySelector('input[type="email"], input[name*="email"]');
                        const hasPassword = !!form.querySelector('input[type="password"]');
                        const hasSubmit = !!form.querySelector('button[type="submit"], input[type="submit"]');
                        
                        data.forms.push({
                            inputs: inputs,
                            hasEmail: hasEmail,
                            hasPassword: hasPassword,
                            hasSubmit: hasSubmit,
                            isAuthForm: hasEmail && hasPassword
                        });
                    });
                    
                    // Check for auth elements
                    if (document.querySelector('[class*="login"], [class*="signin"], [href*="login"]')) {
                        data.auth_elements.push('Login');
                    }
                    if (document.querySelector('[class*="signup"], [class*="register"], [href*="signup"]')) {
                        data.auth_elements.push('Signup');
                    }
                    
                    return data;
                }
            """)
            
            flows["cta_analysis"] = {
                "total_ctas": len(flow_data.get("ctas", [])),
                "ctas": flow_data.get("ctas", [])[:10]  # Top 10
            }
            
            flows["forms"] = flow_data.get("forms", [])
            
            auth_forms = [f for f in flows["forms"] if f.get("isAuthForm")]
            flows["signup_flow"] = {
                "has_signup": "Signup" in flow_data.get("auth_elements", []),
                "has_login": "Login" in flow_data.get("auth_elements", []),
                "auth_forms_count": len(auth_forms)
            }
            
        except Exception as e:
            print(f"[ERROR] User flow analysis failed: {e}")
        
        return flows
    
    async def _analyze_content_strategy(self, page: Page, screenshot: bytes, url: str) -> Dict:
        """AI-powered content strategy analysis."""
        strategy = {
            "tone": "",
            "value_propositions": [],
            "key_messages": [],
            "content_structure": {}
        }
        
        try:
            # Extract text content
            text_content = await page.evaluate("""
                () => {
                    const hero = document.querySelector('.hero, [class*="hero"], header');
                    const headings = Array.from(document.querySelectorAll('h1, h2, h3')).slice(0, 5);
                    
                    return {
                        hero_text: hero ? hero.textContent.trim().substring(0, 500) : '',
                        headings: headings.map(h => h.textContent.trim())
                    };
                }
            """)
            
            # Use AI to analyze tone and messaging
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            prompt = f"""
Analyze the content strategy of this website ({url}):

Hero text: {text_content.get('hero_text', '')}
Key headings: {', '.join(text_content.get('headings', []))}

Provide a JSON response with:
{{
    "tone": "professional/casual/playful/technical/friendly (choose one and explain briefly)",
    "value_propositions": ["main value prop 1", "value prop 2"],
    "key_messages": ["key message 1", "key message 2", "key message 3"]
}}

Focus on the primary messaging and positioning strategy.
"""
            
            response = await query_gemini_vision_api(prompt, screenshot_b64)
            
            if response:
                try:
                    analysis = json.loads(response)
                    strategy = analysis
                except json.JSONDecodeError:
                    if "```json" in response:
                        json_start = response.find("```json") + 7
                        json_end = response.find("```", json_start)
                        json_str = response[json_start:json_end].strip()
                        strategy = json.loads(json_str)
            
        except Exception as e:
            print(f"[WARNING] Content strategy analysis failed: {e}")
        
        return strategy
    
    async def _analyze_mobile(self, browser, url: str) -> Dict:
        """Mobile experience analysis."""
        mobile = {
            "viewports_tested": [],
            "mobile_specific_features": [],
            "responsive_breakpoints": [],
            "touch_targets": {},
            "mobile_performance": {}
        }
        
        try:
            for viewport in self.mobile_viewports:
                page = await browser.new_page(
                    viewport={"width": viewport["width"], "height": viewport["height"]}
                )
                
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Detect mobile-specific features
                mobile_features = await page.evaluate("""
                    () => {
                        const features = [];
                        
                        if (document.querySelector('.hamburger, [class*="hamburger"], [class*="menu-toggle"]')) {
                            features.push('Hamburger menu');
                        }
                        if (document.querySelector('[class*="bottom-nav"], [class*="tab-bar"]')) {
                            features.push('Bottom navigation');
                        }
                        if (document.querySelector('[class*="swipe"], [class*="carousel"]')) {
                            features.push('Swipeable elements');
                        }
                        
                        // Check for touch event listeners
                        const hasTouchEvents = 'ontouchstart' in window;
                        if (hasTouchEvents) features.push('Touch event support');
                        
                        return features;
                    }
                """)
                
                mobile["viewports_tested"].append({
                    "name": viewport["name"],
                    "width": viewport["width"],
                    "height": viewport["height"],
                    "features": mobile_features
                })
                
                # Aggregate mobile-specific features
                for feature in mobile_features:
                    if feature not in mobile["mobile_specific_features"]:
                        mobile["mobile_specific_features"].append(feature)
                
                await page.close()
                
        except Exception as e:
            print(f"[ERROR] Mobile analysis failed: {e}")
        
        return mobile
    
    async def _analyze_pricing(self, page: Page) -> Dict:
        """Extract and analyze pricing information."""
        pricing = {
            "has_pricing": False,
            "pricing_tiers": [],
            "pricing_strategy": "",
            "currency": ""
        }
        
        try:
            pricing_data = await page.evaluate("""
                () => {
                    const data = {
                        tiers: [],
                        hasPricing: false
                    };
                    
                    // Look for pricing sections
                    const pricingSection = document.querySelector('.pricing, [class*="pricing"], [class*="plan"]');
                    if (!pricingSection) return data;
                    
                    data.hasPricing = true;
                    
                    // Extract pricing cards/tiers
                    const tierElements = pricingSection.querySelectorAll('[class*="tier"], [class*="plan"], [class*="card"]');
                    tierElements.forEach(tier => {
                        const name = tier.querySelector('h2, h3, h4, [class*="title"]')?.textContent.trim();
                        const priceEl = tier.querySelector('[class*="price"], [class*="cost"]');
                        const price = priceEl ? priceEl.textContent.trim() : '';
                        
                        const features = [];
                        tier.querySelectorAll('li, [class*="feature"]').forEach(f => {
                            features.push(f.textContent.trim());
                        });
                        
                        if (name || price) {
                            data.tiers.push({
                                name: name || 'Unnamed',
                                price: price,
                                features: features.slice(0, 10)  // Top 10 features
                            });
                        }
                    });
                    
                    return data;
                }
            """)
            
            pricing["has_pricing"] = pricing_data.get("hasPricing", False)
            pricing["pricing_tiers"] = pricing_data.get("tiers", [])
            
            # Determine pricing strategy
            tier_count = len(pricing["pricing_tiers"])
            if tier_count == 0:
                pricing["pricing_strategy"] = "No pricing page detected"
            elif tier_count == 1:
                pricing["pricing_strategy"] = "Single tier"
            elif tier_count <= 3:
                pricing["pricing_strategy"] = "Tiered pricing"
            else:
                pricing["pricing_strategy"] = "Multiple tiers"
            
            # Try to detect currency
            if pricing["pricing_tiers"]:
                first_price = pricing["pricing_tiers"][0].get("price", "")
                if "$" in first_price:
                    pricing["currency"] = "USD"
                elif "€" in first_price:
                    pricing["currency"] = "EUR"
                elif "£" in first_price:
                    pricing["currency"] = "GBP"
            
        except Exception as e:
            print(f"[ERROR] Pricing analysis failed: {e}")
        
        return pricing
