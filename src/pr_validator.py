"""
Unified PR Validation Pipeline

Orchestrates all validation checks before PR creation to catch:
- Build issues
- Deployment problems
- Routing errors
- File naming/location issues
- Security vulnerabilities
- File overwrites/conflicts

Author: AI Engine
Created: 2026-01-19
"""

import os
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

# Import existing validators
from validator import CodeValidator
from build_validator import BuildValidator
from routing_validator import RoutingValidator

# Import new validators (will create these)
try:
    from enhanced_syntax_validator import SyntaxValidator
    SYNTAX_VALIDATOR_AVAILABLE = True
except ImportError:
    SYNTAX_VALIDATOR_AVAILABLE = False
    print("[PR_VALIDATOR] Enhanced syntax validator not available, using basic validation")

try:
    from security_validator import SecurityValidator
    SECURITY_VALIDATOR_AVAILABLE = True
except ImportError:
    SECURITY_VALIDATOR_AVAILABLE = False
    print("[PR_VALIDATOR] Security validator not available, skipping security checks")

try:
    from file_conflict_detector import FileConflictDetector
    FILE_CONFLICT_DETECTOR_AVAILABLE = True
except ImportError:
    FILE_CONFLICT_DETECTOR_AVAILABLE = False
    print("[PR_VALIDATOR] File conflict detector not available, skipping conflict checks")


class ValidationLevel(Enum):
    """Validation strictness levels"""
    STRICT = "strict"      # Block on any warning or error
    STANDARD = "standard"  # Block on errors only, allow warnings
    RELAXED = "relaxed"    # Allow warnings and non-critical errors


class IssueSeverity(Enum):
    """Issue severity levels"""
    BLOCKING = "blocking"    # Must fix before PR
    ERROR = "error"          # Should fix before PR
    WARNING = "warning"      # Good to fix but not required
    INFO = "info"            # Informational only


@dataclass
class ValidationIssue:
    """Represents a validation issue found in generated code"""
    severity: IssueSeverity
    category: str  # e.g., "syntax", "security", "routing", "conflict"
    file_path: str
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    details: Dict = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of PR validation"""
    valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info_messages: List[str] = field(default_factory=list)
    validation_time: float = 0.0
    validators_run: List[str] = field(default_factory=list)
    
    def get_blocking_issues(self) -> List[ValidationIssue]:
        """Get all blocking issues"""
        return [i for i in self.issues if i.severity == IssueSeverity.BLOCKING]
    
    def get_errors(self) -> List[ValidationIssue]:
        """Get all errors"""
        return [i for i in self.issues if i.severity == IssueSeverity.ERROR]
    
    def get_warnings(self) -> List[ValidationIssue]:
        """Get all warnings"""
        return [i for i in self.issues if i.severity == IssueSeverity.WARNING]
    
    def has_blocking_issues(self) -> bool:
        """Check if there are any blocking issues"""
        return len(self.get_blocking_issues()) > 0
    
    def summary(self) -> str:
        """Get a summary of validation results"""
        blocking = len(self.get_blocking_issues())
        errors = len(self.get_errors())
        warnings = len(self.get_warnings())
        return f"Blocking: {blocking}, Errors: {errors}, Warnings: {warnings}"


class PRValidator:
    """
    Unified PR validation orchestrator.
    Runs comprehensive validation checks before PR creation.
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.validation_level = validation_level
        
        # Initialize validators
        self.code_validator = CodeValidator()
        self.build_validator = BuildValidator()
        self.routing_validator = RoutingValidator()
        
        # Optional validators
        self.syntax_validator = SyntaxValidator() if SYNTAX_VALIDATOR_AVAILABLE else None
        self.security_validator = SecurityValidator() if SECURITY_VALIDATOR_AVAILABLE else None
        self.file_conflict_detector = FileConflictDetector() if FILE_CONFLICT_DETECTOR_AVAILABLE else None
        
        print(f"[PR_VALIDATOR] Initialized with {validation_level.value} validation level")
    
    async def validate_pr(
        self,
        generated_files: Dict[str, str],
        repo_path: str,
        tech_stack: Optional[Dict] = None
    ) -> ValidationResult:
        """
        Comprehensive validation before PR creation.
        
        Args:
            generated_files: Dict of {filepath: content}
            repo_path: Path to repository
            tech_stack: Technology stack information
            
        Returns:
            ValidationResult with all issues found
        """
        start_time = datetime.now()
        print(f"[PR_VALIDATOR] ========================================")
        print(f"[PR_VALIDATOR] Starting PR validation for {len(generated_files)} files")
        print(f"[PR_VALIDATOR] Validation level: {self.validation_level.value}")
        print(f"[PR_VALIDATOR] ========================================")
        
        result = ValidationResult(valid=True)
        
        # Run all validations in parallel for speed
        validation_tasks = []
        
        # 1. Syntax validation
        if self.syntax_validator:
            validation_tasks.append(
                self._run_syntax_validation(generated_files, result)
            )
        
        # 2. Build validation (imports, dependencies, naming)
        validation_tasks.append(
            self._run_build_validation(generated_files, repo_path, result)
        )
        
        # 3. Routing validation
        if tech_stack:
            validation_tasks.append(
                self._run_routing_validation(generated_files, repo_path, tech_stack, result)
            )
        
        # 4. Security validation
        if self.security_validator:
            validation_tasks.append(
                self._run_security_validation(generated_files, result)
            )
        
        # 5. File conflict detection
        if self.file_conflict_detector:
            validation_tasks.append(
                self._run_conflict_detection(generated_files, repo_path, result)
            )
        
        # 6. Code quality validation (existing validator)
        validation_tasks.append(
            self._run_code_validation(generated_files, result)
        )
        
        # Run all validations concurrently
        await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Determine if PR is valid based on validation level
        result.valid = self._determine_validity(result)
        
        # Calculate validation time
        end_time = datetime.now()
        result.validation_time = (end_time - start_time).total_seconds()
        
        # Print summary
        self._print_summary(result)
        
        return result
    
    async def _run_syntax_validation(
        self,
        generated_files: Dict[str, str],
        result: ValidationResult
    ):
        """Run syntax validation on all files"""
        print(f"[PR_VALIDATOR] Running syntax validation...")
        result.validators_run.append("syntax")
        
        try:
            for filepath, content in generated_files.items():
                syntax_result = await self.syntax_validator.validate(filepath, content)
                
                if not syntax_result['valid']:
                    for error in syntax_result.get('errors', []):
                        result.issues.append(ValidationIssue(
                            severity=IssueSeverity.BLOCKING,
                            category="syntax",
                            file_path=filepath,
                            message=error.get('message', 'Syntax error'),
                            line_number=error.get('line'),
                            suggestion=error.get('suggestion')
                        ))
            
            print(f"[PR_VALIDATOR] ✅ Syntax validation complete")
        except Exception as e:
            print(f"[PR_VALIDATOR] ⚠️ Syntax validation error: {e}")
            result.warnings.append(f"Syntax validation failed: {e}")
    
    async def _run_build_validation(
        self,
        generated_files: Dict[str, str],
        repo_path: str,
        result: ValidationResult
    ):
        """Run build validation (imports, dependencies, naming)"""
        print(f"[PR_VALIDATOR] Running build validation...")
        result.validators_run.append("build")
        
        try:
            # Validate imports
            import_result = self.build_validator.validate_imports(generated_files, repo_path)
            
            if not import_result['valid']:
                for issue in import_result.get('issues', []):
                    result.issues.append(ValidationIssue(
                        severity=IssueSeverity.ERROR,
                        category="build",
                        file_path=issue.get('file', ''),
                        message=issue.get('message', 'Build issue'),
                        line_number=issue.get('line'),
                        suggestion=issue.get('suggestion'),
                        auto_fixable=issue.get('fixable', False)
                    ))
            
            # Add warnings
            for warning in import_result.get('warnings', []):
                result.warnings.append(f"Build: {warning.get('message', str(warning))}")
            
            print(f"[PR_VALIDATOR] ✅ Build validation complete")
        except Exception as e:
            print(f"[PR_VALIDATOR] ⚠️ Build validation error: {e}")
            result.warnings.append(f"Build validation failed: {e}")
    
    async def _run_routing_validation(
        self,
        generated_files: Dict[str, str],
        repo_path: str,
        tech_stack: Dict,
        result: ValidationResult
    ):
        """Run routing validation for new pages"""
        print(f"[PR_VALIDATOR] Running routing validation...")
        result.validators_run.append("routing")
        
        try:
            routing_result = self.routing_validator.validate_routing(
                generated_files, repo_path, tech_stack
            )
            
            if not routing_result['valid']:
                for issue in routing_result.get('issues', []):
                    result.issues.append(ValidationIssue(
                        severity=IssueSeverity.ERROR,
                        category="routing",
                        file_path=issue.get('page', ''),
                        message=issue.get('message', 'Routing issue'),
                        suggestion=issue.get('suggestion'),
                        auto_fixable=True  # Routing fixes can be auto-generated
                    ))
            
            print(f"[PR_VALIDATOR] ✅ Routing validation complete")
        except Exception as e:
            print(f"[PR_VALIDATOR] ⚠️ Routing validation error: {e}")
            result.warnings.append(f"Routing validation failed: {e}")
    
    async def _run_security_validation(
        self,
        generated_files: Dict[str, str],
        result: ValidationResult
    ):
        """Run security validation"""
        print(f"[PR_VALIDATOR] Running security validation...")
        result.validators_run.append("security")
        
        try:
            for filepath, content in generated_files.items():
                security_result = await self.security_validator.validate(filepath, content)
                
                for vulnerability in security_result.get('vulnerabilities', []):
                    severity = IssueSeverity.BLOCKING if vulnerability.get('critical', False) else IssueSeverity.ERROR
                    
                    result.issues.append(ValidationIssue(
                        severity=severity,
                        category="security",
                        file_path=filepath,
                        message=vulnerability.get('message', 'Security issue'),
                        line_number=vulnerability.get('line'),
                        suggestion=vulnerability.get('fix'),
                        details=vulnerability
                    ))
            
            print(f"[PR_VALIDATOR] ✅ Security validation complete")
        except Exception as e:
            print(f"[PR_VALIDATOR] ⚠️ Security validation error: {e}")
            result.warnings.append(f"Security validation failed: {e}")
    
    async def _run_conflict_detection(
        self,
        generated_files: Dict[str, str],
        repo_path: str,
        result: ValidationResult
    ):
        """Run file conflict detection"""
        print(f"[PR_VALIDATOR] Running conflict detection...")
        result.validators_run.append("conflict")
        
        try:
            conflict_result = await self.file_conflict_detector.detect_conflicts(
                generated_files, repo_path
            )
            
            for conflict in conflict_result.get('conflicts', []):
                result.issues.append(ValidationIssue(
                    severity=IssueSeverity.BLOCKING,
                    category="conflict",
                    file_path=conflict.get('file', ''),
                    message=conflict.get('message', 'File conflict'),
                    suggestion=conflict.get('resolution'),
                    details=conflict
                ))
            
            print(f"[PR_VALIDATOR] ✅ Conflict detection complete")
        except Exception as e:
            print(f"[PR_VALIDATOR] ⚠️ Conflict detection error: {e}")
            result.warnings.append(f"Conflict detection failed: {e}")
    
    async def _run_code_validation(
        self,
        generated_files: Dict[str, str],
        result: ValidationResult
    ):
        """Run existing code validator"""
        print(f"[PR_VALIDATOR] Running code quality validation...")
        result.validators_run.append("code_quality")
        
        try:
            # Convert to fixes format for existing validator
            fixes = [
                {'path': path, 'content': content, 'description': f'Generated file: {path}'}
                for path, content in generated_files.items()
            ]
            
            safe_fixes = self.code_validator.validate_all_fixes(fixes)
            
            # Files that didn't pass become issues
            unsafe_count = len(fixes) - len(safe_fixes)
            if unsafe_count > 0:
                result.warnings.append(
                    f"{unsafe_count} files flagged by code quality validator"
                )
            
            print(f"[PR_VALIDATOR] ✅ Code quality validation complete")
        except Exception as e:
            print(f"[PR_VALIDATOR] ⚠️ Code quality validation error: {e}")
            result.warnings.append(f"Code quality validation failed: {e}")
    
    def _determine_validity(self, result: ValidationResult) -> bool:
        """
        Determine if PR is valid based on validation level and issues found.
        """
        blocking_count = len(result.get_blocking_issues())
        error_count = len(result.get_errors())
        warning_count = len(result.get_warnings())
        
        if self.validation_level == ValidationLevel.STRICT:
            # Strict: No issues of any kind allowed
            return blocking_count == 0 and error_count == 0 and warning_count == 0
        
        elif self.validation_level == ValidationLevel.STANDARD:
            # Standard: Blocking issues and errors not allowed
            return blocking_count == 0 and error_count == 0
        
        else:  # RELAXED
            # Relaxed: Only blocking issues prevent PR
            return blocking_count == 0
    
    def _print_summary(self, result: ValidationResult):
        """Print validation summary"""
        print(f"[PR_VALIDATOR] ========================================")
        print(f"[PR_VALIDATOR] VALIDATION SUMMARY")
        print(f"[PR_VALIDATOR] ========================================")
        print(f"[PR_VALIDATOR] Valid: {'✅ YES' if result.valid else '❌ NO'}")
        print(f"[PR_VALIDATOR] Time: {result.validation_time:.2f}s")
        print(f"[PR_VALIDATOR] Validators run: {', '.join(result.validators_run)}")
        print(f"[PR_VALIDATOR] {result.summary()}")
        
        # Print blocking issues
        blocking = result.get_blocking_issues()
        if blocking:
            print(f"[PR_VALIDATOR] ")
            print(f"[PR_VALIDATOR] ❌ BLOCKING ISSUES ({len(blocking)}):")
            for issue in blocking:
                print(f"[PR_VALIDATOR]   - [{issue.category}] {issue.file_path}: {issue.message}")
                if issue.suggestion:
                    print(f"[PR_VALIDATOR]     💡 Fix: {issue.suggestion}")
        
        # Print errors
        errors = result.get_errors()
        if errors:
            print(f"[PR_VALIDATOR] ")
            print(f"[PR_VALIDATOR] ⚠️ ERRORS ({len(errors)}):")
            for issue in errors[:5]:  # Show first 5
                print(f"[PR_VALIDATOR]   - [{issue.category}] {issue.file_path}: {issue.message}")
        
        # Print warnings summary
        if result.warnings:
            print(f"[PR_VALIDATOR] ")
            print(f"[PR_VALIDATOR] ⚠️ WARNINGS ({len(result.warnings)}):")
            for warning in result.warnings[:3]:  # Show first 3
                print(f"[PR_VALIDATOR]   - {warning}")
        
        print(f"[PR_VALIDATOR] ========================================")
    
    def generate_report(self, result: ValidationResult) -> str:
        """Generate a detailed validation report"""
        report_lines = [
            "# PR Validation Report",
            f"Generated: {datetime.now().isoformat()}",
            f"",
            f"## Summary",
            f"- **Status**: {'✅ PASS' if result.valid else '❌ FAIL'}",
            f"- **Validation Time**: {result.validation_time:.2f}s",
            f"- **Validators**: {', '.join(result.validators_run)}",
            f"- **Issues**: {result.summary()}",
            f""
        ]
        
        # Blocking issues
        blocking = result.get_blocking_issues()
        if blocking:
            report_lines.append("## ❌ Blocking Issues")
            report_lines.append("")
            for issue in blocking:
                report_lines.append(f"### {issue.file_path}")
                report_lines.append(f"- **Category**: {issue.category}")
                report_lines.append(f"- **Message**: {issue.message}")
                if issue.line_number:
                    report_lines.append(f"- **Line**: {issue.line_number}")
                if issue.suggestion:
                    report_lines.append(f"- **Suggestion**: {issue.suggestion}")
                report_lines.append("")
        
        # Errors
        errors = result.get_errors()
        if errors:
            report_lines.append("## ⚠️ Errors")
            report_lines.append("")
            for issue in errors:
                report_lines.append(f"### {issue.file_path}")
                report_lines.append(f"- **Category**: {issue.category}")
                report_lines.append(f"- **Message**: {issue.message}")
                if issue.suggestion:
                    report_lines.append(f"- **Suggestion**: {issue.suggestion}")
                report_lines.append("")
        
        # Warnings
        warnings = result.get_warnings()
        if warnings:
            report_lines.append("## ℹ️ Warnings")
            report_lines.append("")
            for issue in warnings:
                report_lines.append(f"- {issue.message}")
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def save_report(self, result: ValidationResult, output_path: str):
        """Save validation report to file"""
        report = self.generate_report(result)
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"[PR_VALIDATOR] Report saved to: {output_path}")
        except Exception as e:
            print(f"[PR_VALIDATOR] Failed to save report: {e}")


# Global instance with standard validation level
pr_validator = PRValidator(ValidationLevel.STANDARD)
