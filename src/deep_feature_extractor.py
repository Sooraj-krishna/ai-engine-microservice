"""
Deep Feature Extractor - Advanced website analysis with multi-page crawling,
design system analysis, performance metrics, and detailed UX pattern detection.
"""

from playwright.async_api import async_playwright, Page
from ai_vision_api import query_gemini_vision_api
import json
import base64
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import re


class DeepFeatureExtractor:
    """Advanced feature extractor with deep analysis capabilities."""
    
    def __init__(self, max_pages: int = 5, enable_performance: bool = True, 
                 enable_design_system: bool = True):
        self.max_pages = max_pages
        self.enable_performance = enable_performance
        self.enable_design_system = enable_design_system
        
    async def extract_features_deep(self, url: str) -> Dict:
        """
        Perform deep feature extraction with multi-page analysis.
        
        Args:
            url: Base URL to analyze
            
        Returns:
            Comprehensive feature analysis
        """
        print(f"[DEEP_EXTRACTOR] Starting deep analysis for: {url}")
        
        features = {
            "url": url,
            "analysis_depth": "deep",
            "analysis_date": datetime.now().isoformat(),
            "pages_analyzed": [],
            "ui_components": [],
            "functionality": [],
            "content_types": [],
            "ux_patterns": [],
            "integrations": [],
            "design_system": {},
            "performance_metrics": {},
            "technical_details": {},
            "seo_accessibility": {},
            "metadata": {}
        }
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Discover pages to analyze
                pages_to_analyze = await self._discover_pages(page, url)
                print(f"[DEEP_EXTRACTOR] Discovered {len(pages_to_analyze)} pages to analyze")
                
                # Analyze each page
                for page_url in pages_to_analyze[:self.max_pages]:
                    print(f"[DEEP_EXTRACTOR] Analyzing page: {page_url}")
                    page_features = await self._analyze_single_page(page, page_url)
                    
                    # Aggregate features
                    features["pages_analyzed"].append(page_url)
                    self._merge_features(features, page_features)
                
                # Extract design system (from homepage)
                if self.enable_design_system:
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    features["design_system"] = await self._extract_design_system(page)
                
                # Get performance metrics
                if self.enable_performance:
                    features["performance_metrics"] = await self._collect_performance_metrics(page, url)
                
                await browser.close()
                
        except Exception as e:
            print(f"[ERROR] Deep feature extraction failed for {url}: {e}")
            features["error"] = str(e)
        
        # Deduplicate aggregated features
        features = self._deduplicate_features(features)
        
        print(f"[DEEP_EXTRACTOR] Analysis complete. Analyzed {len(features['pages_analyzed'])} pages.")
        print(f"[DEEP_EXTRACTOR] Found {len(features['ui_components'])} UI components, "
              f"{len(features['ux_patterns'])} UX patterns")
        
        return features
    
    async def _discover_pages(self, page: Page, base_url: str) -> List[str]:
        """Discover important pages to analyze."""
        pages = [base_url]  # Always analyze homepage
        
        try:
            await page.goto(base_url, wait_until='networkidle', timeout=30000)
            
            # Common important pages
            potential_paths = [
                '/pricing', '/price', '/plans',
                '/features', '/product',
                '/about', '/about-us',
                '/contact', '/contact-us',
                '/blog', '/news',
                '/demo', '/get-started',
                '/services', '/solutions'
            ]
            
            # Extract links from navigation
            nav_links = await page.evaluate("""
                () => {
                    const links = [];
                    const navElements = document.querySelectorAll('nav a, header a, [role="navigation"] a');
                    navElements.forEach(link => {
                        const href = link.href;
                        if (href && !href.startsWith('#') && !href.includes('javascript:')) {
                            links.push(href);
                        }
                    });
                    return links;
                }
            """)
            
            # Normalize base URL
            base_domain = base_url.rstrip('/')
            
            # Add discovered nav links (same domain only)
            for link in nav_links:
                if link.startswith(base_domain) and link not in pages:
                    pages.append(link)
            
            # Add common paths if they exist
            for path in potential_paths:
                potential_url = f"{base_domain}{path}"
                if potential_url not in pages:
                    pages.append(potential_url)
                    
        except Exception as e:
            print(f"[WARNING] Page discovery failed: {e}")
        
        return pages
    
    async def _analyze_single_page(self, page: Page, url: str) -> Dict:
        """Analyze a single page in detail."""
        page_features = {
            "ui_components": [],
            "functionality": [],
            "content_types": [],
            "ux_patterns": [],
            "integrations": []
        }
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 1. Enhanced DOM analysis
            dom_features = await self._analyze_dom_deep(page)
            page_features["ui_components"].extend(dom_features.get("ui_components", []))
            page_features["functionality"].extend(dom_features.get("functionality", []))
            page_features["ux_patterns"].extend(dom_features.get("ux_patterns", []))
            
            # 2. Take screenshot for AI analysis
            screenshot = await page.screenshot(full_page=True)
            
            # 3. Deep AI vision analysis
            ai_features = await self._analyze_with_ai_deep(screenshot, url)
            if ai_features:
                page_features["ui_components"].extend(ai_features.get("ui_components", []))
                page_features["ux_patterns"].extend(ai_features.get("ux_patterns", []))
                page_features["content_types"].extend(ai_features.get("content_types", []))
            
            # 4. Detect interactions and behaviors
            behaviors = await self._detect_behaviors(page)
            page_features["ux_patterns"].extend(behaviors)
            
            # 5. Content type analysis
            content = await self._analyze_content_deep(page)
            page_features["content_types"].extend(content)
            
            # 6. Integration detection
            integrations = await self._detect_integrations_deep(page)
            page_features["integrations"].extend(integrations)
            
        except Exception as e:
            print(f"[ERROR] Failed to analyze page {url}: {e}")
        
        return page_features
    
    async def _analyze_dom_deep(self, page: Page) -> Dict:
        """Deep DOM analysis including micro-interactions and advanced patterns."""
        analysis = {
            "ui_components": [],
            "functionality": [],
            "ux_patterns": []
        }
        
        try:
            features = await page.evaluate("""
                () => {
                    const components = [];
                    const functionality = [];
                    const ux_patterns = [];
                    
                    // ========== UI Components ==========
                    
                    // Navigation with details
                    const nav = document.querySelector('nav, header nav, [role="navigation"]');
                    if (nav) {
                        const navLinks = nav.querySelectorAll('a').length;
                        components.push({
                            name: 'Navigation Bar',
                            type: 'navigation',
                            details: `${navLinks} links`,
                            has_dropdown: !!nav.querySelector('.dropdown, [aria-haspopup]')
                        });
                    }
                    
                    // Hero section with CTA analysis
                    const hero = document.querySelector('.hero, [class*="hero"], .banner, [class*="banner"]');
                    if (hero) {
                        const ctas = hero.querySelectorAll('button, a[class*="btn"], a[class*="cta"]').length;
                        components.push({
                            name: 'Hero Section',
                            type: 'hero',
                            details: `${ctas} CTA buttons`
                        });
                    }
                    
                    // Advanced button detection
                    const buttons = document.querySelectorAll('button, [role="button"], input[type="submit"]');
                    const buttonStyles = new Set();
                    buttons.forEach(btn => {
                        const classList = Array.from(btn.classList).join(' ');
                        if (classList.includes('primary')) buttonStyles.add('primary');
                        if (classList.includes('secondary')) buttonStyles.add('secondary');
                        if (classList.includes('ghost') || classList.includes('outline')) buttonStyles.add('outline');
                    });
                    if (buttonStyles.size > 1) {
                        components.push({
                            name: 'Button System',
                            type: 'buttons',
                            details: `Multiple variants: ${Array.from(buttonStyles).join(', ')}`
                        });
                    }
                    
                    // Sidebar
                    if (document.querySelector('aside, .sidebar, [class*="sidebar"]')) {
                        components.push({name: 'Sidebar', type: 'sidebar'});
                    }
                    
                    // Footer with sections
                    const footer = document.querySelector('footer');
                    if (footer) {
                        const footerSections = footer.querySelectorAll('div[class*="col"], section, nav').length;
                        components.push({
                            name: 'Footer',
                            type: 'footer',
                            details: `${footerSections} sections`
                        });
                    }
                    
                    // Cards with count
                    const cards = document.querySelectorAll('.card, [class*="card"]');
                    if (cards.length > 2) {
                        components.push({
                            name: 'Card Grid',
                            type: 'cards',
                            details: `${cards.length} cards`
                        });
                    }
                    
                    // Modals
                    if (document.querySelector('.modal, [role="dialog"], [class*="modal"]')) {
                        components.push({name: 'Modal Dialogs', type: 'modal'});
                    }
                    
                    // Tabs
                    if (document.querySelector('[role="tablist"], .tabs, [class*="tab"]')) {
                        components.push({name: 'Tabs', type: 'tabs'});
                    }
                    
                    // Accordion
                    if (document.querySelector('[role="accordion"], .accordion, details')) {
                        components.push({name: 'Accordion', type: 'accordion'});
                    }
                    
                    // Carousel/Slider
                    if (document.querySelector('.carousel, .slider, [class*="carousel"], [class*="slider"], .swiper')) {
                        components.push({name: 'Carousel/Slider', type: 'carousel'});
                    }
                    
                    // Breadcrumbs
                    if (document.querySelector('nav[aria-label*="breadcrumb"], .breadcrumb, [class*="breadcrumb"]')) {
                        components.push({name: 'Breadcrumbs', type: 'breadcrumbs'});
                    }
                    
                    // Badge/Label system
                    if (document.querySelectorAll('.badge, .label, .tag, [class*="badge"]').length > 3) {
                        components.push({name: 'Badge System', type: 'badges'});
                    }
                    
                    // Avatar system
                    if (document.querySelectorAll('.avatar, [class*="avatar"]').length > 0) {
                        components.push({name: 'Avatar Components', type: 'avatars'});
                    }
                    
                    // Progress bars
                    if (document.querySelector('progress, .progress, [role="progressbar"]')) {
                        components.push({name: 'Progress Indicators', type: 'progress'});
                    }
                    
                    // ========== Functionality ==========
                    
                    // Search with autocomplete detection
                    const searchInput = document.querySelector('input[type="search"], [role="search"], .search input');
                    if (searchInput) {
                        const hasAutocomplete = !!document.querySelector('[role="combobox"], .autocomplete, [class*="suggestion"]');
                        functionality.push({
                            name: 'Search Functionality',
                            type: 'search',
                            details: hasAutocomplete ? 'with autocomplete' : 'basic'
                        });
                    }
                    
                    // Filters with count
                    const filters = document.querySelectorAll('.filter, [class*="filter"], select, input[type="checkbox"][class*="filter"]');
                    if (filters.length > 0) {
                        functionality.push({
                            name: 'Filters',
                            type: 'filters',
                            details: `${filters.length} filter controls`
                        });
                    }
                    
                    // Sorting
                    if (document.querySelector('select[class*="sort"], [class*="sort"]')) {
                        functionality.push({name: 'Sorting', type: 'sorting'});
                    }
                    
                    // Pagination
                    const pagination = document.querySelector('.pagination, [class*="pagination"], nav[aria-label*="page"]');
                    if (pagination) {
                        functionality.push({name: 'Pagination', type: 'pagination'});
                    }
                    
                    // Forms with validation
                    const forms = document.querySelectorAll('form');
                    if (forms.length > 0) {
                        const hasValidation = !!document.querySelector('input[required], [aria-invalid]');
                        functionality.push({
                            name: `Forms`,
                            type: 'forms',
                            count: forms.length,
                            details: hasValidation ? 'with validation' : 'basic'
                        });
                    }
                    
                    // Authentication
                    if (document.querySelector('[class*="login"], [class*="signin"], [class*="auth"], [href*="login"]')) {
                        functionality.push({name: 'Authentication', type: 'authentication'});
                    }
                    
                    // Comments/Discussion
                    if (document.querySelector('.comment, [class*="comment"], .discussion')) {
                        functionality.push({name: 'Comments System', type: 'comments'});
                    }
                    
                    // Rating/Review
                    if (document.querySelector('.rating, [class*="rating"], .stars, [class*="star"]')) {
                        functionality.push({name: 'Rating System', type: 'rating'});
                    }
                    
                    // Share buttons
                    if (document.querySelector('[class*="share"], [aria-label*="share"]')) {
                        functionality.push({name: 'Social Sharing', type: 'sharing'});
                    }
                    
                    // ========== UX Patterns ==========
                    
                    // Dark mode toggle
                    if (document.querySelector('[class*="dark"], [class*="theme"], [aria-label*="theme"]')) {
                        ux_patterns.push({name: 'Dark Mode Toggle', type: 'theme_toggle'});
                    }
                    
                    // Tooltips
                    if (document.querySelector('[role="tooltip"], .tooltip, [class*="tooltip"]')) {
                        ux_patterns.push({name: 'Tooltips', type: 'tooltips'});
                    }
                    
                    // Notifications/Toasts
                    if (document.querySelector('.notification, .toast, [role="alert"], [class*="notification"]')) {
                        ux_patterns.push({name: 'Notifications/Toasts', type: 'notifications'});
                    }
                    
                    // Skeleton loaders
                    if (document.querySelector('.skeleton, [class*="skeleton"], .placeholder')) {
                        ux_patterns.push({name: 'Skeleton Loaders', type: 'loading_state'});
                    }
                    
                    // Scroll to top button
                    if (document.querySelector('[class*="scroll-top"], [aria-label*="scroll to top"]')) {
                        ux_patterns.push({name: 'Scroll to Top Button', type: 'navigation_aid'});
                    }
                    
                    // Sticky header
                    const header = document.querySelector('header, nav');
                    if (header) {
                        const styles = window.getComputedStyle(header);
                        if (styles.position === 'sticky' || styles.position === 'fixed') {
                            ux_patterns.push({name: 'Sticky Header', type: 'sticky_nav'});
                        }
                    }
                    
                    // Infinite scroll detection
                    if (document.querySelector('[class*="infinite"], [data-infinite-scroll]')) {
                        ux_patterns.push({name: 'Infinite Scroll', type: 'infinite_scroll'});
                    }
                    
                    // Lazy loading images
                    if (document.querySelector('img[loading="lazy"], img[data-src]')) {
                        ux_patterns.push({name: 'Lazy Loading Images', type: 'lazy_loading'});
                    }
                    
                    // Animations detection
                    const hasAnimations = Array.from(document.querySelectorAll('*')).some(el => {
                        const styles = window.getComputedStyle(el);
                        return styles.animationName !== 'none' || styles.transition !== 'none';
                    });
                    if (hasAnimations) {
                        ux_patterns.push({name: 'CSS Animations/Transitions', type: 'animations'});
                    }
                    
                    return {components, functionality, ux_patterns};
                }
            """)
            
            analysis["ui_components"] = features["components"]
            analysis["functionality"] = features["functionality"]
            analysis["ux_patterns"] = features["ux_patterns"]
            
        except Exception as e:
            print(f"[ERROR] Deep DOM analysis failed: {e}")
        
        return analysis
    
    async def _analyze_with_ai_deep(self, screenshot: bytes, url: str) -> Optional[Dict]:
        """Enhanced AI vision analysis with detailed prompts."""
        try:
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            prompt = f"""
Analyze this website screenshot from {url} in DETAIL. Identify:

1. **UI Components**: All visible components including:
   - Navigation patterns (mega-menu, hamburger, tabs)
   - Hero section design (background type, CTA placement)
   - Cards/tiles and their styling
   - Form elements and input styles
   - Button variants and styles
   - Any unique or custom components

2. **UX Patterns**: Micro-interactions and patterns like:
   - Hover effects on buttons/links
   - Animation styles (fade, slide, scale)
   - Loading states or placeholders
   - Error states or validation feedback
   - Empty states
   - Progressive disclosure patterns
   - Micro-interactions (tooltips on hover, etc.)

3. **Content Types**: What kind of content is displayed:
   - Blog posts, articles
   - Products/e-commerce
   - Testimonials/reviews
   - Pricing tables
   - Case studies
   - FAQ sections
   - Gallery/portfolio items

4. **Design Details**: Note specific design choices:
   - Color scheme (primary, secondary, accent colors)
   - Typography style (modern, classic, playful)
   - Spacing patterns (compact, spacious)
   - Border radius style (sharp, rounded, pill-shaped)
   - Shadow usage (flat, subtle, pronounced)

Return ONLY a JSON object with this structure:
{{
    "ui_components": [
        {{"name": "component name", "type": "component_type", "description": "specific details about styling or behavior"}}
    ],
    "ux_patterns": [
        {{"name": "pattern name", "type": "pattern_type", "description": "how it works or appears"}}
    ],
    "content_types": [
        {{"name": "content type", "type": "content_category", "description": "brief description"}}
    ]
}}

Focus on MINUTE DETAILS and unique implementations that differentiate this site.
"""
            
            response = await query_gemini_vision_api(prompt, screenshot_b64)
            
            if response:
                try:
                    features = json.loads(response)
                    return features
                except json.JSONDecodeError:
                    if "```json" in response:
                        json_start = response.find("```json") + 7
                        json_end = response.find("```", json_start)
                        json_str = response[json_start:json_end].strip()
                        features = json.loads(json_str)
                        return features
                        
        except Exception as e:
            print(f"[WARNING] Deep AI vision analysis failed: {e}")
        
        return None
    
    async def _detect_behaviors(self, page: Page) -> List[Dict]:
        """Detect interactive behaviors and JavaScript-driven features."""
        behaviors = []
        
        try:
            detected = await page.evaluate("""
                () => {
                    const behaviors = [];
                    
                    // Check for scroll-triggered animations
                    if (window.IntersectionObserver) {
                        behaviors.push({
                            name: 'Scroll-triggered Animations',
                            type: 'scroll_animation',
                            description: 'Elements animate when scrolled into view'
                        });
                    }
                    
                    // Check for parallax scrolling
                    const parallax = Array.from(document.querySelectorAll('*')).some(el => {
                        return el.style.transform && el.style.transform.includes('translateY');
                    });
                    if (parallax) {
                        behaviors.push({
                            name: 'Parallax Scrolling',
                            type: 'parallax',
                            description: 'Background layers move at different speeds'
                        });
                    }
                    
                    // Check for real-time features
                    if (window.WebSocket || window.EventSource) {
                        behaviors.push({
                            name: 'Real-time Updates',
                            type: 'realtime',
                            description: 'WebSocket or Server-Sent Events detected'
                        });
                    }
                    
                    // Check for single-page application
                    const isSPA = !!(window.React || window.Vue || window.Angular || 
                                    document.querySelector('[data-reactroot], [data-react-root], [ng-app]'));
                    if (isSPA) {
                        behaviors.push({
                            name: 'Single Page Application',
                            type: 'spa',
                            description: 'Client-side routing detected'
                        });
                    }
                    
                    // Check for service worker (PWA)
                    if ('serviceWorker' in navigator) {
                        behaviors.push({
                            name: 'Progressive Web App',
                            type: 'pwa',
                            description: 'Service worker support detected'
                        });
                    }
                    
                    return behaviors;
                }
            """)
            
            behaviors.extend(detected)
            
        except Exception as e:
            print(f"[WARNING] Behavior detection failed: {e}")
        
        return behaviors
    
    async def _analyze_content_deep(self, page: Page) -> List[Dict]:
        """Deep content type analysis."""
        content_types = []
        
        try:
            detected = await page.evaluate("""
                () => {
                    const types = [];
                    
                    // Blog/Articles
                    if (document.querySelector('article, .blog, [class*="blog"], .post, [class*="post"]')) {
                        const articleCount = document.querySelectorAll('article').length;
                        types.push({
                            name: 'Blog/Articles',
                            type: 'blog',
                            details: `${articleCount} articles visible`
                        });
                    }
                    
                    // Products
                    const products = document.querySelectorAll('.product, [class*="product"], [data-product]');
                    if (products.length > 0) {
                        types.push({
                            name: 'Products',
                            type: 'products',
                            details: `${products.length} products visible`
                        });
                    }
                    
                    // Pricing tables
                    if (document.querySelector('.pricing, [class*="pricing"], [class*="plan"]')) {
                        const plans = document.querySelectorAll('[class*="plan"], [class*="pricing"]').length;
                        types.push({
                            name: 'Pricing Tables',
                            type: 'pricing',
                            details: `${plans} pricing tiers`
                        });
                    }
                    
                    // Testimonials
                    const testimonials = document.querySelectorAll('.testimonial, [class*="testimonial"], .review, [class*="review"]');
                    if (testimonials.length > 0) {
                        types.push({
                            name: 'Testimonials',
                            type: 'testimonials',
                            details: `${testimonials.length} reviews visible`
                        });
                    }
                    
                    // FAQ
                    if (document.querySelector('.faq, [class*="faq"]')) {
                        const faqItems = document.querySelectorAll('.faq-item, details').length;
                        types.push({
                            name: 'FAQ Section',
                            type: 'faq',
                            details: `${faqItems} questions`
                        });
                    }
                    
                    // Gallery
                    if (document.querySelector('.gallery, [class*="gallery"]')) {
                        types.push({name: 'Gallery', type: 'gallery'});
                    }
                    
                    // Team members
                    if (document.querySelector('.team, [class*="team"], [class*="member"]')) {
                        types.push({name: 'Team Section', type: 'team'});
                    }
                    
                    // Case studies / Portfolio
                    if (document.querySelector('.case-study, [class*="portfolio"], .project')) {
                        types.push({name: 'Case Studies/Portfolio', type: 'portfolio'});
                    }
                    
                    // Contact form
                    if (document.querySelector('form[class*="contact"], input[name*="email"]')) {
                        types.push({name: 'Contact Form', type: 'contact'});
                    }
                    
                    // Newsletter signup
                    if (document.querySelector('[class*="newsletter"], input[placeholder*="email"]')) {
                        types.push({name: 'Newsletter Signup', type: 'newsletter'});
                    }
                    
                    return types;
                }
            """)
            
            content_types.extend(detected)
            
        except Exception as e:
            print(f"[ERROR] Content analysis failed: {e}")
        
        return content_types
    
    async def _detect_integrations_deep(self, page: Page) -> List[Dict]:
        """Deep third-party integration detection."""
        integrations = []
        
        try:
            detected = await page.evaluate("""
                () => {
                    const integrations = [];
                    const html = document.documentElement.outerHTML;
                    const scripts = Array.from(document.querySelectorAll('script')).map(s => s.src || s.textContent);
                    const allText = scripts.join(' ') + ' ' + html;
                    
                    // Social media
                    if (allText.includes('facebook.com') || allText.includes('fb.')) {
                        integrations.push({name: 'Facebook', type: 'social_media', category: 'social'});
                    }
                    if (allText.includes('twitter.com') || allText.includes('t.co')) {
                        integrations.push({name: 'Twitter/X', type: 'social_media', category: 'social'});
                    }
                    if (allText.includes('instagram.com')) {
                        integrations.push({name: 'Instagram', type: 'social_media', category: 'social'});
                    }
                    if (allText.includes('linkedin.com')) {
                        integrations.push({name: 'LinkedIn', type: 'social_media', category: 'social'});
                    }
                    
                    // Analytics
                    if (allText.includes('google-analytics') || allText.includes('gtag') || allText.includes('ga.js')) {
                        integrations.push({name: 'Google Analytics', type: 'analytics', category: 'tracking'});
                    }
                    if (allText.includes('mixpanel')) {
                        integrations.push({name: 'Mixpanel', type: 'analytics', category: 'tracking'});
                    }
                    if (allText.includes('segment')) {
                        integrations.push({name: 'Segment', type: 'analytics', category: 'tracking'});
                    }
                    if (allText.includes('hotjar')) {
                        integrations.push({name: 'Hotjar', type: 'heatmap', category: 'tracking'});
                    }
                    
                    // Chat
                    if (allText.includes('intercom')) {
                        integrations.push({name: 'Intercom', type: 'chat', category: 'support'});
                    }
                    if (allText.includes('drift')) {
                        integrations.push({name: 'Drift', type: 'chat', category: 'support'});
                    }
                    if (allText.includes('crisp')) {
                        integrations.push({name: 'Crisp Chat', type: 'chat', category: 'support'});
                    }
                    if (allText.includes('tawk')) {
                        integrations.push({name: 'Tawk.to', type: 'chat', category: 'support'});
                    }
                    if (allText.includes('zendesk')) {
                        integrations.push({name: 'Zendesk', type: 'support', category: 'support'});
                    }
                    
                    // Payment
                    if (allText.includes('stripe')) {
                        integrations.push({name: 'Stripe', type: 'payment', category: 'commerce'});
                    }
                    if (allText.includes('paypal')) {
                        integrations.push({name: 'PayPal', type: 'payment', category: 'commerce'});
                    }
                    
                    // Email marketing
                    if (allText.includes('mailchimp')) {
                        integrations.push({name: 'Mailchimp', type: 'email_marketing', category: 'marketing'});
                    }
                    
                    // CMS
                    if (allText.includes('wp-content') || allText.includes('wordpress')) {
                        integrations.push({name: 'WordPress', type: 'cms', category: 'platform'});
                    }
                    if (allText.includes('shopify')) {
                        integrations.push({name: 'Shopify', type: 'ecommerce', category: 'platform'});
                    }
                    
                    // CDN
                    if (allText.includes('cdn.')) {
                        integrations.push({name: 'CDN', type: 'cdn', category: 'infrastructure'});
                    }
                    
                    return integrations;
                }
            """)
            
            integrations.extend(detected)
            
        except Exception as e:
            print(f"[ERROR] Integration detection failed: {e}")
        
        return integrations
    
    async def _extract_design_system(self, page: Page) -> Dict:
        """Extract design system tokens (colors, typography, spacing)."""
        design_system = {
            "colors": {},
            "typography": {},
            "spacing": {},
            "borders": {},
            "shadows": {}
        }
        
        try:
            ds = await page.evaluate("""
                () => {
                    const designSystem = {
                        colors: {primary: [], secondary: [], backgrounds: [], text: []},
                        typography: {families: new Set(), sizes: new Set(), weights: new Set()},
                        spacing: new Set(),
                        borders: {radii: new Set()},
                        shadows: new Set()
                    };
                    
                    // Sample elements to extract styles
                    const elements = document.querySelectorAll('*');
                    const sampledElements = Array.from(elements).slice(0, 200); // Sample first 200
                    
                    sampledElements.forEach(el => {
                        const styles = window.getComputedStyle(el);
                        
                        // Colors
                        const bgColor = styles.backgroundColor;
                        const color = styles.color;
                        if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') {
                            if (!designSystem.colors.backgrounds.includes(bgColor)) {
                                designSystem.colors.backgrounds.push(bgColor);
                            }
                        }
                        if (color && color !== 'rgb(0, 0, 0)') {
                            if (!designSystem.colors.text.includes(color)) {
                                designSystem.colors.text.push(color);
                            }
                        }
                        
                        // Typography
                        const fontFamily = styles.fontFamily.split(',')[0].replace(/['"]/g, '').trim();
                        const fontSize = styles.fontSize;
                        const fontWeight = styles.fontWeight;
                        if (fontFamily && fontFamily !== 'serif' && fontFamily !== 'sans-serif') {
                            designSystem.typography.families.add(fontFamily);
                        }
                        if (fontSize) designSystem.typography.sizes.add(fontSize);
                        if (fontWeight) designSystem.typography.weights.add(fontWeight);
                        
                        // Spacing (margins, paddings)
                        const margin = styles.margin;
                        const padding = styles.padding;
                        if (margin !== '0px') designSystem.spacing.add(margin);
                        if (padding !== '0px') designSystem.spacing.add(padding);
                        
                        // Border radius
                        const borderRadius = styles.borderRadius;
                        if (borderRadius && borderRadius !== '0px') {
                            designSystem.borders.radii.add(borderRadius);
                        }
                        
                        // Box shadow
                        const boxShadow = styles.boxShadow;
                        if (boxShadow && boxShadow !== 'none') {
                            designSystem.shadows.add(boxShadow);
                        }
                    });
                    
                    // Convert Sets to Arrays
                    return {
                        colors: designSystem.colors,
                        typography: {
                            families: Array.from(designSystem.typography.families).slice(0, 10),
                            sizes: Array.from(designSystem.typography.sizes).slice(0, 15),
                            weights: Array.from(designSystem.typography.weights)
                        },
                        spacing: Array.from(designSystem.spacing).slice(0, 20),
                        borders: {
                            radii: Array.from(designSystem.borders.radii).slice(0, 10)
                        },
                        shadows: Array.from(designSystem.shadows).slice(0, 10)
                    };
                }
            """)
            
            design_system = ds
            
        except Exception as e:
            print(f"[WARNING] Design system extraction failed: {e}")
        
        return design_system
    
    async def _collect_performance_metrics(self, page: Page, url: str) -> Dict:
        """Collect performance metrics."""
        metrics = {}
        
        try:
            # Performance timing
            perf = await page.evaluate("""
                () => {
                    const perfData = window.performance.timing;
                    const paintEntries = performance.getEntriesByType('paint');
                    
                    return {
                        loadTime: perfData.loadEventEnd - perfData.navigationStart,
                        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.navigationStart,
                        firstPaint: paintEntries.find(e => e.name === 'first-paint')?.startTime || 0,
                        firstContentfulPaint: paintEntries.find(e => e.name === 'first-contentful-paint')?.startTime || 0
                    };
                }
            """)
            
            # Resource counts
            resources = await page.evaluate("""
                () => {
                    const resources = performance.getEntriesByType('resource');
                    let totalSize = 0;
                    let jsSize = 0;
                    let cssSize = 0;
                    let imageSize = 0;
                    
                    resources.forEach(r => {
                        const size = r.transferSize || 0;
                        totalSize += size;
                        
                        if (r.name.includes('.js')) jsSize += size;
                        else if (r.name.includes('.css')) cssSize += size;
                        else if (r.name.match(/\\.(jpg|jpeg|png|gif|webp|svg)/)) imageSize += size;
                    });
                    
                    return {
                        totalRequests: resources.length,
                        totalSize: Math.round(totalSize / 1024) + ' KB',
                        jsSize: Math.round(jsSize / 1024) + ' KB',
                        cssSize: Math.round(cssSize / 1024) + ' KB',
                        imageSize: Math.round(imageSize / 1024) + ' KB'
                    };
                }
            """)
            
            metrics = {
                "load_time_ms": perf.get("loadTime", 0),
                "dom_content_loaded_ms": perf.get("domContentLoaded", 0),
                "first_paint_ms": perf.get("firstPaint", 0),
                "first_contentful_paint_ms": perf.get("firstContentfulPaint", 0),
                "total_requests": resources.get("totalRequests", 0),
                "total_size": resources.get("totalSize", "0 KB"),
                "js_size": resources.get("jsSize", "0 KB"),
                "css_size": resources.get("cssSize", "0 KB"),
                "image_size": resources.get("imageSize", "0 KB")
            }
            
        except Exception as e:
            print(f"[WARNING] Performance metrics collection failed: {e}")
        
        return metrics
    
    def _merge_features(self, target: Dict, source: Dict):
        """Merge features from source into target."""
        for category in ['ui_components', 'functionality', 'content_types', 'ux_patterns', 'integrations']:
            if category in source:
                target[category].extend(source[category])
    
    def _deduplicate_features(self, features: Dict) -> Dict:
        """Remove duplicate features."""
        for category in ['ui_components', 'functionality', 'content_types', 'ux_patterns', 'integrations']:
            if category in features:
                seen = set()
                unique = []
                for item in features[category]:
                    name = item.get('name', '')
                    if name and name not in seen:
                        seen.add(name)
                        unique.append(item)
                features[category] = unique
        
        return features
