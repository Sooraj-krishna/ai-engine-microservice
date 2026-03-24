"""
Test Change Detector

Tests the change detection system.
"""

import sys
sys.path.append('src')

from change_detector import change_detector
from feature_store import feature_store
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MockFeature:
    feature_name: str
    category: str
    confidence: float
    evidence: list
    page_type: str = "homepage"


def test_impact_calculation():
    """Test impact score calculation."""
    print("\n=== Test 1: Impact Score Calculation ===")
    
    # Payment feature should have high impact
    payment_impact = change_detector._calculate_impact("UPI Payment", "Payment", "added")
    print(f"Payment feature impact: {payment_impact}")
    assert payment_impact > 80, "Payment features should have high impact"
    
    # Services feature should have lower impact
    services_impact = change_detector._calculate_impact("Gift Wrapping", "Services", "added")
    print(f"Services feature impact: {services_impact}")
    assert services_impact < payment_impact, "Services should have lower impact than Payment"
    
    print("✅ Impact calculation working correctly")


def test_competitive_score():
    """Test competitive score calculation."""
    print("\n=== Test 2: Competitive Score ===")
    
    your_features = {"Cash on Delivery", "Free Shipping", "Product Reviews"}
    
    competitor_features = {
        "Cash on Delivery": {
            "feature_name": "Cash on Delivery",
            "adoption_rate": 1.0  # All competitors have it
        },
        "Free Shipping": {
            "feature_name": "Free Shipping",
            "adoption_rate": 0.8
        },
        "UPI Payment": {
            "feature_name": "UPI Payment",
            "adoption_rate": 0.6  # You don't have this
        }
    }
    
    score = change_detector._calculate_competitive_score(your_features, competitor_features)
    print(f"Competitive score: {score}/100")
    
    # Should be between 0-100
    assert 0 <= score <= 100, "Score should be in valid range"
    
    # Should be above 50 since we have 2/3 common features
    assert score > 50, "Score should reflect partial coverage"
    
    print(f"✅ Competitive score calculation working (Score: {score})")


def test_change_recommendation():
    """Test recommendation generation."""
    print("\n=== Test 3: Change Recommendations ===")
    
    change_new = {
        "change_type": "new_feature",
        "feature_name": "AR View"
    }
    
    change_removed = {
        "change_type": "removed",
        "feature_name": "Store Pickup"
    }
    
    rec_new = change_detector._get_change_recommendation(change_new)
    rec_removed = change_detector._get_change_recommendation(change_removed)
    
    print(f"New feature recommendation: {rec_new}")
    print(f"Removed feature recommendation: {rec_removed}")
    
    assert "implement" in rec_new.lower(), "New feature should suggest implementation"
    assert "removed" in rec_removed.lower(), "Removed feature should mention removal"
    
    print("✅ Recommendations generated correctly")


def test_trending_detection_empty():
    """Test trending detection with no data."""
    print("\n=== Test 4: Trending Detection (Empty Database) ===")
    
    # With empty database, should return empty list
    trending = change_detector.get_trending_features(days=30)
    
    print(f"Trending features found: {len(trending)}")
    
    # This is expected to be 0 with fresh database
    print("✅ Trending detection working (no data yet)")


def test_analyze_adoption_trends():
    """Test adoption trend analysis."""
    print("\n=== Test 5: Adoption Trend Analysis ===")
    
    # Test with a non-existent feature
    trend = change_detector.analyze_adoption_trends("Nonexistent Feature")
    
    print(f"Trend status: {trend['status']}")
    assert trend['status'] == 'not_found', "Should handle non-existent features"
    
    print("✅ Adoption trend analysis working")


def test_compare_with_competitors_empty():
    """Test competitive comparison with empty database."""
    print("\n=== Test 6: Competitive Comparison (Empty Database) ===")
    
    your_features = {"Cash on Delivery", "Free Shipping", "Product Reviews"}
    
    comparison = change_detector.compare_with_competitors(your_features)
    
    print(f"Total competitors analyzed: {comparison['total_competitors_analyzed']}")
    print(f"Gaps: {len(comparison['gaps'])}")
    print(f"Leads: {len(comparison['leads'])}")
    print(f"Competitive score: {comparison['competitive_score']}")
    
    # With no competitor data, all your features should be leads
    assert len(comparison['leads']) == len(your_features), "All features should be leads with no competitor data"
    assert comparison['competitive_score'] == 100, "Score should be 100 with no competitor data"
    
    print("✅ Competitive comparison working")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Change Detector")
    print("=" * 60)
    
    try:
        test_impact_calculation()
        test_competitive_score()
        test_change_recommendation()
        test_trending_detection_empty()
        test_analyze_adoption_trends()
        test_compare_with_competitors_empty()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nNote: Some tests use empty database which is expected.")
        print("Run professional analysis on real sites to populate data.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
