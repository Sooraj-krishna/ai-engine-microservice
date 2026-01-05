"""
Feature Extractor - Analyzes websites to identify features using Playwright and AI.
Extracts UI components, functionality, content types, and UX patterns.
"""

from playwright.async_api import async_playwright
from ai_vision_api import query_gemini_vision_api
import json
import base64
from io import BytesIO


async def extract_features_from_site(url: str) -> dict:
    """
    Extract features from a website using Playwright and AI analysis.
    
    Args:
        url: The website URL to analyze
        
    Returns:
        dict: Extracted features categorized by type
    """
    print(f"[FEATURE_EXTRACTOR] Analyzing site: {url}")
    
    features = {
        "url": url,
        "ui_components": [],
        "functionality": [],
        "content_types": [],
        "ux_patterns": [],
        "integrations": [],
        "metadata": {}
    }
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Navigate to the site
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 1. Extract DOM structure and analyze
            dom_analysis = await analyze_dom_structure(page)
            features["ui_components"].extend(dom_analysis.get("ui_components", []))
            features["functionality"].extend(dom_analysis.get("functionality", []))
            
            # 2. Take screenshots for AI vision analysis
            screenshot = await page.screenshot(full_page=False)  # Above the fold
            
            # 3. Use AI to identify visual features
            ai_features = await analyze_with_ai_vision(screenshot, url)
            if ai_features:
                features["ui_components"].extend(ai_features.get("ui_components", []))
                features["ux_patterns"].extend(ai_features.get("ux_patterns", []))
            
            # 4. Detect content types
            content_analysis = await analyze_content_types(page)
            features["content_types"].extend(content_analysis)
            
            # 5. Identify integrations
            integrations = await detect_integrations(page)
            features["integrations"].extend(integrations)
            
            # 6. Extract metadata
            features["metadata"] = await extract_metadata(page)
            
            await browser.close()
            
    except Exception as e:
        print(f"[ERROR] Feature extraction failed for {url}: {e}")
        features["error"] = str(e)
    
    # Deduplicate features
    features = deduplicate_features(features)
    
    print(f"[FEATURE_EXTRACTOR] Extracted {len(features['ui_components'])} UI components, "
          f"{len(features['functionality'])} functionalities, "
          f"{len(features['content_types'])} content types")
    
    return features


async def analyze_dom_structure(page) -> dict:
    """Analyze DOM to identify UI components and functionality."""
    analysis = {
        "ui_components": [],
        "functionality": []
    }
    
    try:
        # Identify UI components
        components = await page.evaluate("""
            () => {
                const components = [];
                
                // Navigation
                if (document.querySelector('nav, header nav, [role="navigation"]')) {
                    components.push({
                        name: 'Navigation Bar',
                        category: 'ui_component',
                        type: 'navigation'
                    });
                }
                
                // Hero section
                if (document.querySelector('.hero, [class*="hero"], .banner, [class*="banner"]')) {
                    components.push({
                        name: 'Hero Section',
                        category: 'ui_component',
                        type: 'hero'
                    });
                }
                
                // Sidebar
                if (document.querySelector('aside, .sidebar, [class*="sidebar"]')) {
                    components.push({
                        name: 'Sidebar',
                        category: 'ui_component',
                        type: 'sidebar'
                    });
                }
                
                // Footer
                if (document.querySelector('footer')) {
                    components.push({
                        name: 'Footer',
                        category: 'ui_component',
                        type: 'footer'
                    });
                }
                
                // Search
                if (document.querySelector('input[type="search"], [role="search"], .search')) {
                    components.push({
                        name: 'Search Functionality',
                        category: 'functionality',
                        type: 'search'
                    });
                }
                
                // Filters
                if (document.querySelector('.filter, [class*="filter"], select[multiple]')) {
                    components.push({
                        name: 'Filters',
                        category: 'functionality',
                        type: 'filters'
                    });
                }
                
                // Forms
                const forms = document.querySelectorAll('form');
                if (forms.length > 0) {
                    components.push({
                        name: `Forms (${forms.length})`,
                        category: 'functionality',
                        type: 'forms',
                        count: forms.length
                    });
                }
                
                // Authentication
                if (document.querySelector('[class*="login"], [class*="signin"], [class*="auth"]')) {
                    components.push({
                        name: 'Authentication',
                        category: 'functionality',
                        type: 'authentication'
                    });
                }
                
                // Modals
                if (document.querySelector('.modal, [role="dialog"], [class*="modal"]')) {
                    components.push({
                        name: 'Modal Dialogs',
                        category: 'ui_component',
                        type: 'modal'
                    });
                }
                
                // Tabs
                if (document.querySelector('[role="tablist"], .tabs, [class*="tab"]')) {
                    components.push({
                        name: 'Tabs',
                        category: 'ui_component',
                        type: 'tabs'
                    });
                }
                
                // Carousel/Slider
                if (document.querySelector('.carousel, .slider, [class*="carousel"], [class*="slider"]')) {
                    components.push({
                        name: 'Carousel/Slider',
                        category: 'ui_component',
                        type: 'carousel'
                    });
                }
                
                // Cards
                const cards = document.querySelectorAll('.card, [class*="card"]');
                if (cards.length > 3) {
                    components.push({
                        name: `Card Grid (${cards.length} cards)`,
                        category: 'ui_component',
                        type: 'cards'
                    });
                }
                
                return components;
            }
        """)
        
        for component in components:
            if component['category'] == 'ui_component':
                analysis['ui_components'].append(component)
            elif component['category'] == 'functionality':
                analysis['functionality'].append(component)
                
    except Exception as e:
        print(f"[ERROR] DOM analysis failed: {e}")
    
    return analysis


async def analyze_with_ai_vision(screenshot: bytes, url: str) -> dict:
    """Use AI vision to analyze screenshot and identify features."""
    try:
        # Convert screenshot to base64
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        
        prompt = f"""
Analyze this website screenshot from {url} and identify:

1. UI Components (navigation, hero, sections, cards, etc.)
2. UX Patterns (dark mode toggle, animations, tooltips, etc.)

Return a JSON object with this structure:
{{
    "ui_components": [
        {{"name": "component name", "type": "component type", "description": "brief description"}}
    ],
    "ux_patterns": [
        {{"name": "pattern name", "type": "pattern type", "description": "brief description"}}
    ]
}}

Focus on identifying features that enhance user experience or functionality.
"""
        
        # Query AI vision API
        response = await query_gemini_vision_api(prompt, screenshot_b64)
        
        if response:
            # Parse JSON from response
            try:
                features = json.loads(response)
                return features
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                if "```json" in response:
                    json_start = response.find("```json") + 7
                    json_end = response.find("```", json_start)
                    json_str = response[json_start:json_end].strip()
                    features = json.loads(json_str)
                    return features
                    
    except Exception as e:
        print(f"[WARNING] AI vision analysis failed: {e}")
    
    return {"ui_components": [], "ux_patterns": []}


async def analyze_content_types(page) -> list:
    """Identify content types on the site."""
    content_types = []
    
    try:
        detected = await page.evaluate("""
            () => {
                const types = [];
                
                // Blog
                if (document.querySelector('article, .blog, [class*="blog"], .post, [class*="post"]')) {
                    types.push({name: 'Blog', type: 'blog'});
                }
                
                // Products
                if (document.querySelector('.product, [class*="product"], [data-product]')) {
                    types.push({name: 'Products', type: 'products'});
                }
                
                // Pricing
                if (document.querySelector('.pricing, [class*="pricing"], [class*="plan"]')) {
                    types.push({name: 'Pricing Tables', type: 'pricing'});
                }
                
                // Testimonials
                if (document.querySelector('.testimonial, [class*="testimonial"], .review, [class*="review"]')) {
                    types.push({name: 'Testimonials', type: 'testimonials'});
                }
                
                // FAQ
                if (document.querySelector('.faq, [class*="faq"]')) {
                    types.push({name: 'FAQ', type: 'faq'});
                }
                
                // Gallery
                if (document.querySelector('.gallery, [class*="gallery"]')) {
                    types.push({name: 'Gallery', type: 'gallery'});
                }
                
                // Contact Form
                if (document.querySelector('form[class*="contact"], input[name*="email"][name*="message"]')) {
                    types.push({name: 'Contact Form', type: 'contact'});
                }
                
                return types;
            }
        """)
        
        content_types.extend(detected)
        
    except Exception as e:
        print(f"[ERROR] Content type analysis failed: {e}")
    
    return content_types


async def detect_integrations(page) -> list:
    """Detect third-party integrations."""
    integrations = []
    
    try:
        detected = await page.evaluate("""
            () => {
                const integrations = [];
                const html = document.documentElement.outerHTML;
                
                // Social media
                if (html.includes('facebook.com') || html.includes('fb.')) {
                    integrations.push({name: 'Facebook', type: 'social_media'});
                }
                if (html.includes('twitter.com') || html.includes('t.co')) {
                    integrations.push({name: 'Twitter/X', type: 'social_media'});
                }
                if (html.includes('instagram.com')) {
                    integrations.push({name: 'Instagram', type: 'social_media'});
                }
                if (html.includes('linkedin.com')) {
                    integrations.push({name: 'LinkedIn', type: 'social_media'});
                }
                
                // Analytics
                if (html.includes('google-analytics') || html.includes('gtag') || html.includes('ga.js')) {
                    integrations.push({name: 'Google Analytics', type: 'analytics'});
                }
                
                // Chat
                if (html.includes('intercom') || html.includes('drift') || html.includes('crisp') || html.includes('tawk')) {
                    integrations.push({name: 'Live Chat', type: 'chat'});
                }
                
                // Payment
                if (html.includes('stripe') || html.includes('paypal')) {
                    integrations.push({name: 'Payment Gateway', type: 'payment'});
                }
                
                return integrations;
            }
        """)
        
        integrations.extend(detected)
        
    except Exception as e:
        print(f"[ERROR] Integration detection failed: {e}")
    
    return integrations


async def extract_metadata(page) -> dict:
    """Extract site metadata."""
    try:
        metadata = await page.evaluate("""
            () => ({
                title: document.title,
                description: document.querySelector('meta[name="description"]')?.content || '',
                viewport: document.querySelector('meta[name="viewport"]')?.content || '',
                has_mobile_viewport: !!document.querySelector('meta[name="viewport"]')
            })
        """)
        return metadata
    except:
        return {}


def deduplicate_features(features: dict) -> dict:
    """Remove duplicate features from each category."""
    for category in ['ui_components', 'functionality', 'content_types', 'ux_patterns', 'integrations']:
        if category in features:
            # Create unique list based on 'name' field
            seen = set()
            unique = []
            for item in features[category]:
                name = item.get('name', '')
                if name and name not in seen:
                    seen.add(name)
                    unique.append(item)
            features[category] = unique
    
    return features
