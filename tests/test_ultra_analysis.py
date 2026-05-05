#!/usr/bin/env python3
"""
Test script for Ultra-Comprehensive Competitive Analysis
Demonstrates finding ALL feature differences between sites
"""

import requests
import json

# Test ultra-comprehensive analysis
print("=" * 60)
print("ULTRA-COMPREHENSIVE COMPETITIVE ANALYSIS TEST")
print("=" * 60)
print()

print("Testing with BuggyCart vs Major E-commerce Sites...")
print()

# Trigger ultra-comprehensive analysis
response = requests.post(
    "http://localhost:8000/analyze-competitors?ultra=true",
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    data = response.json()
    
    print(f"✅ Analysis Complete!")
    print(f"Analysis Type: {data.get('analysis_type')}")
    print(f"Total Features Found: {data.get('total_features_found')}")
    print()
    
    recommendations = data.get('recommendations', [])
    
    if recommendations:
        print(f"Found {len(recommendations)} Feature Gaps:")
        print()
        
        # Group by category
        by_category = {}
        for rec in recommendations:
            category = rec.get('category', 'Other')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(rec)
        
        # Display by category
        for category, items in sorted(by_category.items()):
            print(f"\n📁 {category} ({len(items)} features)")
            print("-" * 60)
            for item in items[:10]:  # Show first 10 per category
                priority = item.get('priority', 'medium')
                emoji = "🔴" if priority == "critical" else "🟡" if priority == "high" else "🟢"
                print(f"{emoji} {item.get('feature_name')}")
                print(f"   {item.get('description', '')[:100]}")
                if item.get('competitor_count'):
                    print(f"   Found on {item.get('competitor_count')} competitors")
                print()
    else:
        print("No feature gaps found (unlikely with ultra mode!)")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

print()
print("=" * 60)
print("Test complete!")
print("=" * 60)
