#!/usr/bin/env python3
"""
Test Professional Competitive Analysis
Detects business features: COD, Try & Buy, delivery options, etc.
"""

import requests
import json

print("=" * 70)
print("PROFESSIONAL COMPETITIVE ANALYSIS TEST")
print("Detecting Business Features (COD, Try & Buy, Delivery Options, etc.)")
print("=" * 70)
print()

print("Testing with BuggyCart vs Amazon/Flipkart/Myntra...")
print()

# Trigger professional analysis
response = requests.post(
    "http://localhost:8000/analyze-competitors?professional=true",
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    data = response.json()
    
    print(f"✅ Analysis Complete!")
    print(f"Analysis Type: {data.get('analysis_type')}")
    print(f"Total Gaps Found: {data.get('total_gaps')}")
    print(f"High Priority Gaps: {data.get('high_priority')}")
    print()
    
    # Show summary
    summary = data.get('summary', {})
    print(f"📊 Summary:")
    print(f"   {summary.get('message')}")
    print()
    
    # Show gaps by category
    print(f"📁 Gaps by Category:")
    for category, count in data.get('gaps_by_category', {}).items():
        print(f"   {category}: {count} features")
    print()
    
    # Show high priority gaps
    high_priority = data.get('high_priority_gaps', [])
    if high_priority:
        print(f"🔴 High Priority Business Features Missing:")
        print("-" * 70)
        for gap in high_priority[:10]:
            print(f"\n  Feature: {gap['feature_name']}")
            print(f"  Category: {gap['category']}")
            print(f"  Adoption: {gap['competitor_count']} competitors")
            print(f"  Priority Score: {gap['priority_score']}")
            if gap.get('evidence'):
                print(f"  Evidence: {gap['evidence'][0][:80]}...")
    
    print()
    
    # Show recommendations
    recommendations = data.get('recommendations', [])
    if recommendations:
        print(f"\n💡 Top Recommendations:")
        print("-" * 70)
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"\n{i}. {rec['feature']} ({rec['category']})")
            print(f"   Priority: {rec['priority'].upper()}")
            print(f"   Adoption: {rec['adoption_rate']}")
            print(f"   Why: {rec['why']}")
    
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

print()
print("=" * 70)
print("Test complete!")
print("=" * 70)
