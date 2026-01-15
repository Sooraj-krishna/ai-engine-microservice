"""
Feature Implementation Manager - Manages feature selection and implementation planning
from competitive analysis results.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from model_router import _query_gemini_api


class FeatureImplementationManager:
    """Manages feature selection, implementation planning, and tracking."""
    
    def __init__(self, storage_dir: str = "./feature_implementations"):
        """
        Initialize the feature implementation manager.
        
        Args:
            storage_dir: Directory to store implementation data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.selected_features_file = self.storage_dir / "selected_features.json"
        self.implementation_plans_dir = self.storage_dir / "plans"
        self.implementation_plans_dir.mkdir(parents=True, exist_ok=True)
    
    def select_feature_for_implementation(
        self, 
        feature: Dict, 
        analysis_results: Dict,
        generate_plan: bool = True
    ) -> Dict:
        """
        Select a feature for future implementation.
        
        Args:
            feature: The selected feature data
            analysis_results: Full competitive analysis results
            generate_plan: Whether to generate implementation plan
            
        Returns:
            Selection result with status and next steps
        """
        feature_id = feature.get("id")
        feature_name = feature.get("name")
        
        # Load existing selections
        selected_features = self._load_selected_features()
        
        # Check if already selected
        if any(f["id"] == feature_id for f in selected_features):
            return {
                "status": "already_selected",
                "message": f"Feature '{feature_name}' is already in the implementation queue",
                "feature": feature
            }
        
        # Create selection record
        selection = {
            "id": feature_id,
            "feature_name": feature_name,
            "category": feature.get("category"),
            "priority_score": feature.get("priority_score"),
            "estimated_effort": feature.get("estimated_effort"),
            "business_impact": feature.get("business_impact"),
            "selected_at": datetime.now().isoformat(),
            "status": "selected",
            "implementation_status": "pending",
            "full_feature_data": feature
        }
        
        # Add to selected features
        selected_features.append(selection)
        self._save_selected_features(selected_features)
        
        result = {
            "status": "success",
            "message": f"Feature '{feature_name}' selected for implementation",
            "feature": feature,
            "selection_id": feature_id,
            "next_steps": []
        }
        
        # Generate implementation plan if requested
        if generate_plan:
            plan = self.generate_implementation_plan(feature, analysis_results)
            if plan:
                result["implementation_plan"] = plan
                result["next_steps"].append("Review generated implementation plan")
        else:
            result["next_steps"].append("Generate implementation plan")
        
        return result
    
    def generate_implementation_plan(self, feature: Dict, analysis_results: Dict) -> Optional[Dict]:
        """
        Generate an AI-powered implementation plan for the selected feature.
        
        Args:
            feature: The feature to implement
            analysis_results: Competitive analysis results for context
            
        Returns:
            Implementation plan or None if generation fails
        """
        feature_id = feature.get("id")
        feature_name = feature.get("name")
        
        print(f"[FEATURE_IMPL] Generating implementation plan for: {feature_name}")
        
        # Build context from competitive analysis
        competitors_context = ""
        if feature.get("found_in"):
            competitors_context = f"This feature is found in: {', '.join(feature['found_in'])}"
        
        implementation_notes = feature.get("implementation_notes", "")
        
        # Create prompt for AI
        prompt = f"""
Generate a detailed implementation plan for adding this feature to our website:

Feature: {feature_name}
Category: {feature.get('category')}
Priority: {feature.get('priority_score')}/10
Estimated Effort: {feature.get('estimated_effort')}
Business Impact: {feature.get('business_impact')}

Context:
{competitors_context}

Implementation Notes from Analysis:
{implementation_notes}

Please provide a JSON response with the following structure:
{{
    "feature_name": "{feature_name}",
    "overview": "Brief overview of what needs to be implemented",
    "requirements": [
        {{"id": 1, "requirement": "requirement description", "type": "functional/technical/ui"}}
    ],
    "implementation_steps": [
        {{"step": 1, "task": "task description", "estimated_hours": 2, "dependencies": []}}
    ],
    "technical_considerations": [
        "consideration 1",
        "consideration 2"
    ],
    "files_to_modify": [
        {{"file": "path/to/file.ext", "changes": "description of changes needed"}}
    ],
    "testing_strategy": [
        {{"test_type": "unit/integration/e2e", "description": "what to test"}}
    ],
    "rollout_plan": {{
        "phases": ["phase 1", "phase 2"],
        "estimated_timeline": "time estimate",
        "success_metrics": ["metric 1", "metric 2"]
    }}
}}

Make the plan practical and actionable.
"""
        
        try:
            # Query AI for implementation plan
            response = _query_gemini_api(
                messages=[{"role": "user", "content": prompt}],
                model=None,
                timeout=60
            )
            
            if not response or "error" in response:
                print(f"[ERROR] Failed to generate implementation plan: {response}")
                return None
            
            # Parse AI response
            ai_text = response.get("text", "")
            
            # Try to extract JSON from response
            plan_data = None
            if "```json" in ai_text:
                json_start = ai_text.find("```json") + 7
                json_end = ai_text.find("```", json_start)
                json_str = ai_text[json_start:json_end].strip()
                plan_data = json.loads(json_str)
            else:
                # Try to parse as direct JSON
                plan_data = json.loads(ai_text)
            
            if plan_data:
                # Enhance plan with metadata
                plan_data["feature_id"] = feature_id
                plan_data["generated_at"] = datetime.now().isoformat()
                plan_data["status"] = "draft"
                
                # Save plan to file
                plan_file = self.implementation_plans_dir / f"{feature_id}_plan.json"
                with open(plan_file, 'w') as f:
                    json.dump(plan_data, f, indent=2)
                
                print(f"[SUCCESS] Implementation plan generated and saved to {plan_file}")
                return plan_data
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse AI response as JSON: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to generate implementation plan: {e}")
        
        return None
    
    def get_selected_features(self, status_filter: Optional[str] = None) -> List[Dict]:
        """
        Get all selected features, optionally filtered by status.
        
        Args:
            status_filter: Filter by implementation_status (pending/in_progress/completed/cancelled)
            
        Returns:
            List of selected features
        """
        features = self._load_selected_features()
        
        if status_filter:
            features = [f for f in features if f.get("implementation_status") == status_filter]
        
        return features
    
    def update_feature_status(self, feature_id: str, new_status: str, notes: str = "") -> Dict:
        """
        Update the implementation status of a feature.
        
        Args:
            feature_id: ID of the feature
            new_status: New status (pending/in_progress/completed/cancelled)
            notes: Optional notes about the status change
            
        Returns:
            Updated feature data
        """
        valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        features = self._load_selected_features()
        
        # Find and update feature
        updated_feature = None
        for feature in features:
            if feature["id"] == feature_id:
                feature["implementation_status"] = new_status
                feature["status_updated_at"] = datetime.now().isoformat()
                
                if notes:
                    if "status_history" not in feature:
                        feature["status_history"] = []
                    feature["status_history"].append({
                        "status": new_status,
                        "notes": notes,
                        "timestamp": datetime.now().isoformat()
                    })
                
                updated_feature = feature
                break
        
        if not updated_feature:
            raise ValueError(f"Feature {feature_id} not found")
        
        self._save_selected_features(features)
        return updated_feature
    
    def get_implementation_plan(self, feature_id: str) -> Optional[Dict]:
        """
        Retrieve the implementation plan for a feature.
        
        Args:
            feature_id: ID of the feature
            
        Returns:
            Implementation plan or None if not found
        """
        plan_file = self.implementation_plans_dir / f"{feature_id}_plan.json"
        
        if plan_file.exists():
            with open(plan_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def prioritize_features(self, features: List[Dict]) -> List[Dict]:
        """
        Prioritize features based on multiple factors.
        
        Args:
            features: List of selected features
            
        Returns:
            Sorted list of features by priority
        """
        def calculate_priority_score(feature):
            # Weight different factors
            priority = feature.get("priority_score", 5) * 10  # 0-100
            
            # Business impact multiplier
            impact_multipliers = {"high": 1.3, "medium": 1.0, "low": 0.7}
            impact = feature.get("business_impact", "medium")
            priority *= impact_multipliers.get(impact, 1.0)
            
            # Effort divisor (lower effort = higher priority)
            effort_divisors = {"Low": 1.0, "Medium": 0.8, "High": 0.6}
            effort = feature.get("estimated_effort", "Medium")
            priority *= effort_divisors.get(effort, 0.8)
            
            return priority
        
        return sorted(features, key=calculate_priority_score, reverse=True)
    
    def get_implementation_summary(self) -> Dict:
        """
        Get a summary of all feature implementations.
        
        Returns:
            Summary statistics
        """
        features = self._load_selected_features()
        
        summary = {
            "total_selected": len(features),
            "by_status": {
                "pending": len([f for f in features if f.get("implementation_status") == "pending"]),
                "in_progress": len([f for f in features if f.get("implementation_status") == "in_progress"]),
                "completed": len([f for f in features if f.get("implementation_status") == "completed"]),
                "cancelled": len([f for f in features if f.get("implementation_status") == "cancelled"])
            },
            "by_priority": {
                "high": len([f for f in features if f.get("priority_score", 0) >= 7]),
                "medium": len([f for f in features if 4 <= f.get("priority_score", 0) < 7]),
                "low": len([f for f in features if f.get("priority_score", 0) < 4])
            },
            "by_effort": {
                "Low": len([f for f in features if f.get("estimated_effort") == "Low"]),
                "Medium": len([f for f in features if f.get("estimated_effort") == "Medium"]),
                "High": len([f for f in features if f.get("estimated_effort") == "High"])
            },
            "features": features
        }
        
        return summary
    
    # Private helper methods
    
    def _load_selected_features(self) -> List[Dict]:
        """Load selected features from storage."""
        if self.selected_features_file.exists():
            with open(self.selected_features_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_selected_features(self, features: List[Dict]):
        """Save selected features to storage."""
        with open(self.selected_features_file, 'w') as f:
            json.dump(features, f, indent=2)


# Global instance
feature_implementation_manager = FeatureImplementationManager()
