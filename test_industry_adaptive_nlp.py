"""
Test Industry-Adaptive NLP Discovery

Tests the industry detection and adaptive feature discovery system.
"""

import sys
sys.path.append('src')

from industry_detector import industry_detector
from nlp_feature_discovery import nlp_discoverer


def test_ecommerce_detection():
    """Test e-commerce site detection."""
    print("\n=== Test 1: E-commerce Detection ===")
    
    ecommerce_content = """
    <h1>Online Store</h1>
    <div>Free shipping on orders over $50</div>
    <button>Add to cart</button>
    <p>Cash on delivery available</p>
    <div>Product price: $29.99</div>
    <span>In stock - Order now!</span>
    """
    
    industry, confidence, scores = industry_detector.detect_industry(ecommerce_content)
    
    print(f"Detected: {industry} (confidence: {confidence:.2f})")
    print(f"Top 3 scores: {sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]}")
    
    assert industry == "ecommerce", f"Should detect e-commerce, got {industry}"
    print("✅ E-commerce detected correctly")


def test_restaurant_detection():
    """Test restaurant site detection."""
    print("\n=== Test 2: Restaurant Detection ===")
    
    restaurant_content = """
    <h1>Welcome to Our Restaurant</h1>
    <a href="/menu">View our menu</a>
    <p>Reservations: Book your table online</p>
    <div>Delivery and takeout available</div>
    <p>Our chef prepares authentic Italian cuisine</p>
    <div>Open hours: Mon-Sun 11am-10pm</div>
    """
    
    industry, confidence, scores = industry_detector.detect_industry(restaurant_content)
    
    print(f"Detected: {industry} (confidence: {confidence:.2f})")
    print(f"Top 3 scores: {sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]}")
    
    assert industry == "restaurant", f"Should detect restaurant, got {industry}"
    print("✅ Restaurant detected correctly")


def test_blog_detection():
    """Test blog site detection."""
    print("\n=== Test 3: Blog Detection ===")
    
    blog_content = """
    <article>
        <h1>Latest Blog Post</h1>
        <p>Posted by John Doe on January 10, 2026</p>
        <div>Read more about this trending topic...</div>
        <p>125 comments | Share on social media</p>
        <button>Subscribe to our newsletter</button>
        <div>Tags: technology, ai, programming</div>
    </article>
    """
    
    industry, confidence, scores = industry_detector.detect_industry(blog_content)
    
    print(f"Detected: {industry} (confidence: {confidence:.2f})")
    print(f"Top 3 scores: {sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]}")
    
    assert industry == "blog", f"Should detect blog, got {industry}"
    print("✅ Blog detected correctly")


def test_saas_detection():
    """Test SaaS site detection."""
    print("\n=== Test 4: SaaS Detection ===")
    
    saas_content = """
    <h1>Project Management Software</h1>
    <div>Pricing plans starting at $9/month</div>
    <a>Start your free trial</a>
    <p>Integrations with Slack, GitHub, and more</p>
    <div>API documentation for developers</div>
    <p>Cloud-based analytics dashboard</p>
    <button>Upgrade to premium plan</button>
    """
    
    industry, confidence, scores = industry_detector.detect_industry(saas_content)
    
    print(f"Detected: {industry} (confidence: {confidence:.2f})")
    print(f"Top 3 scores: {sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]}")
    
    assert industry == "saas", f"Should detect SaaS, got {industry}"
    print("✅ SaaS detected correctly")


def test_adaptive_nlp_ecommerce():
    """Test NLP adapts to e-commerce."""
    print("\n=== Test 5: Adaptive NLP for E-commerce ===")
    
    content = """
    We offer free shipping on all orders.
    Cash on delivery available in select areas.
    Easy returns within 30 days, no questions asked.
    24/7 customer support via live chat.
    """
    
    features = nlp_discoverer.discover_features(content)
    detected_industry, conf = nlp_discoverer.get_detected_industry()
    
    print(f"Detected industry: {detected_industry}")
    print(f"Discovered {len(features)} features:")
    for f in features[:5]:
        print(f"  - {f.feature_name} ({f.category})")
    
    assert detected_industry == "ecommerce", "Should detect e-commerce"
    print("✅ NLP adapted to e-commerce")


def test_adaptive_nlp_restaurant():
    """Test NLP adapts to restaurant."""
    print("\n=== Test 6: Adaptive NLP for Restaurant ===")
    
    content = """
    Reserve your table online today.
    View our full menu of Italian dishes.
    Order delivery through our website.
    Chef's special changes daily.
    """
    
    features = nlp_discoverer.discover_features(content)
    detected_industry, conf = nlp_discoverer.get_detected_industry()
    
    print(f"Detected industry: {detected_industry}")
    print(f"Discovered {len(features)} features:")
    for f in features[:5]:
        print(f"  - {f.feature_name} ({f.category})")
    
    assert detected_industry == "restaurant", "Should detect restaurant"
    print("✅ NLP adapted to restaurant")


def test_industry_metadata():
    """Test industry metadata retrieval."""
    print("\n=== Test 7: Industry Metadata ===")
    
    details = industry_detector.get_industry_details("ecommerce")
    print(f"E-commerce: {details['name']}")
    print(f"Description: {details['description']}")
    print(f"Key features: {details['key_features']}")
    
    assert details['name'] == "E-commerce"
    print("✅ Industry metadata working")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Industry-Adaptive NLP System")
    print("=" * 60)
    
    try:
        # Test industry detection
        test_ecommerce_detection()
        test_restaurant_detection()
        test_blog_detection()
        test_saas_detection()
        
        # Test adaptive NLP
        test_adaptive_nlp_ecommerce()
        test_adaptive_nlp_restaurant()
        
        # Test metadata
        test_industry_metadata()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n🎉 Industry-adaptive NLP system is working!")
        print("Supports: E-commerce, Restaurant, Blog, SaaS, and 6 more industries")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
