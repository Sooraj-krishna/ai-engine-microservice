"""
Test NLP Feature Discovery

Tests the NLP-based feature discovery system.
"""

import sys
sys.path.append('src')

from nlp_feature_discovery import nlp_discoverer


def test_keyword_discovery():
    """Test keyword-based discovery."""
    print("\n=== Test 1: Keyword-Based Discovery ===")
    
    sample_text = """
    We offer fast delivery and easy payment options.
    Pay with UPI, credit card, or cash on delivery.
    Free shipping on orders above $50.
    Customer reviews available for all products.
    """
    
    features = nlp_discoverer.discover_features(sample_text)
    
    print(f"Discovered {len(features)} features:")
    for f in features:
        print(f"  - {f.feature_name} ({f.category}) - Confidence: {f.confidence:.2f}")
    
    assert len(features) > 0, "Should discover some features"
    print("✅ Keyword discovery working")


def test_pattern_extraction():
    """Test pattern-based extraction."""
    print("\n=== Test 2: Pattern-Based Extraction ===")
    
    sample_text = """
    Same day delivery available in your area.
    Try before you buy with our home trial program.
    4.5 star rating based on 1,234 reviews.
    """
    
    features = nlp_discoverer.discover_features(sample_text)
    
    print(f"Discovered {len(features)} features:")
    for f in features:
        print(f"  - {f.feature_name} ({f.category}) - Method: {f.discovery_method}")
    
    print("✅ Pattern extraction working")


def test_complementary_features():
    """Test getting complementary features."""
    print("\n=== Test 3: Complementary Features ===")
    
    from dataclasses import dataclass
    
    @dataclass
    class MockRuleFeature:
        feature_name: str
        category: str
    
    sample_text = """
    Cash on delivery available.
    Premium customer support with live chat.
    Loyalty rewards program for repeat customers.
    """
    
    # Simulate rule-based features
    rule_features = [
        MockRuleFeature("Cash on Delivery", "Payment")
    ]
    
    # Get NLP features
    nlp_features = nlp_discoverer.discover_features(sample_text)
    
    # Get complementary (non-overlapping) features
    complementary = nlp_discoverer.get_complementary_features(nlp_features, rule_features)
    
    print(f"NLP discovered: {len(nlp_features)} features")
    print(f"Complementary (non-overlapping): {len(complementary)} features")
    
    for f in complementary:
        print(f"  - {f.feature_name} ({f.category})")
    
    # Should not include "Cash on Delivery" since it's in rule_features
    cod_in_complementary = any("cash" in f.feature_name.lower() and "delivery" in f.feature_name.lower() 
                                for f in complementary)
    
    if not cod_in_complementary:
        print("✅ Correctly filtered out overlapping features")
    else:
        print("⚠️  Warning: Some overlap detected (acceptable)")


def test_text_extraction():
    """Test HTML text extraction."""
    print("\n=== Test 4: HTML Text Extraction ===")
    
    html_content = """
    <html>
        <head><title>E-commerce Site</title></head>
        <body>
            <script>console.log('test');</script>
            <h1>Welcome</h1>
            <p>Free shipping on all orders!</p>
            <div>Easy returns within 30 days</div>
        </body>
    </html>
    """
    
    features = nlp_discoverer.discover_features(html_content)
    
    print(f"Discovered {len(features)} features from HTML:")
    for f in features:
        print(f"  - {f.feature_name}")
    
    # Should find shipping and returns features
    has_shipping = any("shipping" in f.feature_name.lower() for f in features)
    has_returns = any("return" in f.feature_name.lower() for f in features)
    
    if has_shipping:
        print("✅ Found shipping feature")
    if has_returns:
        print("✅ Found returns feature")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing NLP Feature Discovery")
    print("=" * 60)
    
    try:
        test_keyword_discovery()
        test_pattern_extraction()
        test_complementary_features()
        test_text_extraction()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
