"""
Example/Test script for Feature Implementation Manager
Demonstrates how to use the feature selection and planning system.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def run_feature_implementation_demo():
    """Demonstrate the feature implementation workflow."""
    
    print("=" * 80)
    print("Feature Implementation System Demo")
    print("=" * 80)
    
    # Step 1: Run competitive analysis (professional mode)
    print("\n1. Running professional competitive analysis...")
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-competitors",
            params={"professional": True}
        )
        if response.status_code == 200:
            analysis = response.json()
            print(f"✅ Found {analysis.get('total_gaps', 0)} feature gaps")
            print(f"   High priority: {analysis.get('high_priority', 0)}")
        else:
            print(f"❌ Analysis failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 2: Get feature recommendations
    print("\n2. Getting feature recommendations...")
    try:
        response = requests.get(f"{BASE_URL}/feature-recommendations")
        if response.status_code == 200:
            features = response.json()
            gaps = features.get("feature_gaps", [])
            print(f"✅ Retrieved {len(gaps)} feature recommendations")
            
            if gaps:
                print("\n   Top 3 features:")
                for i, gap in enumerate(gaps[:3], 1):
                    print(f"   {i}. {gap.get('name')} (Priority: {gap.get('priority_score')}/10)")
        else:
            print(f"❌ Failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 3: Select first feature for implementation
    if gaps:
        feature_id = gaps[0]["id"]
        feature_name = gaps[0]["name"]
        
        print(f"\n3. Selecting feature '{feature_name}' for implementation...")
        try:
            response = requests.post(
                f"{BASE_URL}/select-feature",
                json={"feature_id": feature_id, "generate_plan": True}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result.get('message')}")
                
                plan = result.get("implementation_plan")
                if plan:
                    print(f"\n   Implementation Plan Generated:")
                    print(f"   - Overview: {plan.get('overview', 'N/A')[:100]}...")
                    print(f"   - Requirements: {len(plan.get('requirements', []))}")
                    print(f"   - Implementation Steps: {len(plan.get('implementation_steps', []))}")
                    print(f"   - Files to Modify: {len(plan.get('files_to_modify', []))}")
            else:
                print(f"❌ Selection failed: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Step 4: Get implementation plan details
        print(f"\n4. Retrieving detailed implementation plan...")
        try:
            response = requests.get(f"{BASE_URL}/implementation-plan/{feature_id}")
            if response.status_code == 200:
                plan = response.json()
                print(f"✅ Plan retrieved")
                
                if plan.get("implementation_steps"):
                    print(f"\n   Implementation Steps:")
                    for step in plan["implementation_steps"][:3]:
                        print(f"   - Step {step.get('step')}: {step.get('task')}")
                        print(f"     Estimated: {step.get('estimated_hours')} hours")
            else:
                print(f"❌ Failed: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Step 5: Update feature status
        print(f"\n5. Updating feature status to 'in_progress'...")
        try:
            response = requests.put(
                f"{BASE_URL}/feature-status/{feature_id}",
                json={
                    "status": "in_progress",
                    "notes": "Starting implementation - demo run"
                }
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result.get('message')}")
            else:
                print(f"❌ Failed: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Step 6: Get implementation summary
    print(f"\n6. Getting implementation summary...")
    try:
        response = requests.get(f"{BASE_URL}/implementation-summary")
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Summary retrieved:")
            print(f"   Total selected: {summary.get('total_selected')}")
            print(f"   By status: {summary.get('by_status')}")
            print(f"   By priority: {summary.get('by_priority')}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 7: Get all selected features
    print(f"\n7. Getting all selected features...")
    try:
        response = requests.get(f"{BASE_URL}/selected-features")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result.get('total')} selected features")
            
            for feature in result.get("features", []):
                print(f"   - {feature.get('feature_name')} ({feature.get('implementation_status')})")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("Demo Complete!")
    print("=" * 80)


if __name__ == "__main__":
    print("\nMake sure the API server is running on http://localhost:8000")
    print("Starting in 3 seconds...\n")
    
    import time
    time.sleep(3)
    
    run_feature_implementation_demo()
