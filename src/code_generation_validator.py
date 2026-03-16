"""
Code Generation Validator

Validates affected file paths BEFORE code generation starts.
This provides an early safety check to catch invalid paths and suggest corrections.
"""

import os
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class CodeGenerationValidator:
    """Validates code generation plans before execution."""
    
    def __init__(self, repo_path: str):
        """
        Initialize validator.
        
        Args:
            repo_path: Path to repository root
        """
        self.repo_path = repo_path
    
    def validate_affected_files(self, affected_files: List[str], 
                                project_structure: Dict = None) -> Dict:
        """
        Validate file paths before code generation.
        
        Args:
            affected_files: List of file paths from the plan
            project_structure: Project structure info from CodeAnalyzer
            
        Returns:
            {
                'valid': bool,
                'existing_files': List[str],  # Files that exist and will be modified
                'new_files': List[str],       # New files with valid paths
                'invalid_files': List[str],   # Invalid file paths
                'suggestions': Dict[str, str] # Corrections for invalid files
            }
        """
        existing_files = []
        new_files = []
        invalid_files = []
        suggestions = {}
        
        for filepath in affected_files:
            full_path = os.path.join(self.repo_path, filepath)
            
            if os.path.exists(full_path):
                # File exists - will be modified
                existing_files.append(filepath)
            else:
                # File doesn't exist - check if path structure is valid
                if self._is_valid_new_file_path(filepath, project_structure):
                    new_files.append(filepath)
                else:
                    invalid_files.append(filepath)
                    # Try to suggest a correction
                    suggestion = self._suggest_path_correction(filepath, project_structure)
                    if suggestion:
                        suggestions[filepath] = suggestion
        
        return {
            'valid': len(invalid_files) == 0,
            'existing_files': existing_files,
            'new_files': new_files,
            'invalid_files': invalid_files,
            'suggestions': suggestions
        }
    
    def _is_valid_new_file_path(self, filepath: str, project_structure: Dict = None) -> bool:
        """
        Check if a new file path is valid based on project structure.
        
        Args:
            filepath: Path for new file
            project_structure: Discovered project structure
            
        Returns:
            True if the path is valid for new file creation
        """
        if not project_structure:
            # Without structure info, be permissive
            return True
        
        # Get directory structure info
        directories = project_structure.get('directories', {})
        
        # Extract directory from filepath
        file_dir = os.path.dirname(filepath)
        
        # Check if parent directory exists or is a logical extension
        if not file_dir:
            # File in root directory
            return True
        
        # Check if directory exists or matches discovered patterns
        for discovered_dir in directories.keys():
            if file_dir == discovered_dir or file_dir.startswith(discovered_dir + os.sep):
                return True
        
        # Check if it follows common patterns
        common_patterns = [
            'src', 'client/src', 'pages', 'components',
            'client/src/pages', 'client/src/components',
            'src/pages', 'src/components'
        ]
        
        for pattern in common_patterns:
            if file_dir == pattern or file_dir.startswith(pattern + os.sep):
                # Directory follows common patterns
                return True
        
        return False
    
    def _suggest_path_correction(self, invalid_path: str, 
                                 project_structure: Dict = None) -> Optional[str]:
        """
        Suggest a correction for an invalid file path.
        
        Args:
            invalid_path: The invalid path
            project_structure: Project structure info
            
        Returns:
            Suggested corrected path or None
        """
        if not project_structure:
            return None
        
        filename = os.path.basename(invalid_path)
        invalid_dir = os.path.dirname(invalid_path)
        
        directories = project_structure.get('directories', {})
        
        # Try to find a similar directory
        best_match = None
        best_similarity = 0
        
        for dir_path in directories.keys():
            # Calculate simple similarity score
            similarity = self._calculate_path_similarity(invalid_dir, dir_path)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = dir_path
        
        if best_match and best_similarity > 0.5:
            return os.path.join(best_match, filename)
        
        return None
    
    def _calculate_path_similarity(self, path1: str, path2: str) -> float:
        """
        Calculate similarity between two paths.
        
        Returns:
            Similarity score from 0.0 to 1.0
        """
        # Normalize paths
        parts1 = set(path1.lower().split(os.sep))
        parts2 = set(path2.lower().split(os.sep))
        
        if not parts1 or not parts2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(parts1 & parts2)
        union = len(parts1 | parts2)
        
        return intersection / union if union > 0 else 0.0
    
    def check_import_feasibility(self, file_list: List[str]) -> Dict:
        """
        Verify that all files can import each other using available aliases.
        
        Args:
            file_list: List of file paths
            
        Returns:
            {
                'feasible': bool,
                'issues': List[str]  # Import feasibility issues
            }
        """
        issues = []
        
        # Check for tsconfig.json to verify import aliases exist
        tsconfig_paths = [
            os.path.join(self.repo_path, "tsconfig.json"),
            os.path.join(self.repo_path, "jsconfig.json"),
            os.path.join(self.repo_path, "client", "tsconfig.json"),
        ]
        
        has_import_alias = False
        for path in tsconfig_paths:
            if os.path.exists(path):
                has_import_alias = True
                break
        
        if not has_import_alias:
            # Check if files are in different directories
            dirs = set(os.path.dirname(f) for f in file_list)
            
            if len(dirs) > 1:
                issues.append(
                    "Files are in different directories but no import aliases configured. "
                    "Imports may fail without aliases like @/ or ~/."
                )
        
        # Check for circular dependencies potential
        if len(file_list) > 1:
            # Simple check: if multiple files in same category, warn about potential circular deps
            page_files = [f for f in file_list if 'page' in f.lower()]
            component_files = [f for f in file_list if 'component' in f.lower()]
            
            if len(page_files) > 1:
                issues.append(
                    f"Multiple page files ({len(page_files)}) being created. "
                    "Ensure they don't have circular import dependencies."
                )
        
        return {
            'feasible': len(issues) == 0,
            'issues': issues
        }


# Global instance factory
def create_validator(repo_path: str) -> CodeGenerationValidator:
    """Create a validator instance."""
    return CodeGenerationValidator(repo_path)
