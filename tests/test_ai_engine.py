from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app, health_check, start_maintenance_cycle
from analyzer import analyze_data
from generator import prepare_fixes
from fastapi.testclient import TestClient

client = TestClient(app)

class TestAIEngine:
    """Comprehensive test suite for AI Engine."""
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "last_check" in data
    
    def test_root_endpoint(self):
        """Test root status endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "AI Engine running"
    
    @patch('main.collect_site_data')
    @patch('main.get_all_repo_files')
    def test_analyzer_integration(self, mock_repo_files, mock_site_data):
        """Test data analysis integration."""
        # Mock data
        mock_site_data.return_value = {
            "metrics": {"avg_response_time": 5.0},
            "errors": {"errors": ["error1", "error2"]},
            "analytics": {"bounce_rate": 0.7}
        }
        mock_repo_files.return_value = ["src/main.py", "package.json"]
        
        # Test analysis
        issues = analyze_data(mock_site_data.return_value, mock_repo_files.return_value)
        assert len(issues) > 0
        assert any(issue["type"] == "performance" for issue in issues)
    
    @patch('generator.query_codegen_api')
    def test_code_generation(self, mock_ai_api):
        """Test AI code generation."""
        mock_ai_api.return_value = "// Generated code\nconsole.log('test');"
        
        issues = [{
            "type": "performance",
            "description": "Add caching to improve performance",
            "framework": "react",
            "language": "javascript",
            "target_file": "src/cache.js"
        }]
        
        fixes = prepare_fixes(issues)
        assert len(fixes) == 1
        assert "Generated code" in fixes[0]["content"]
    
    def test_run_endpoint(self):
        """Test maintenance cycle trigger."""
        response = client.post("/run")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "timestamp" in data

class TestSecurityAndCompliance:
    """Test security aspects of AI-generated code."""
    
    def test_input_validation(self):
        """Test input validation and sanitization."""
        # Test malicious input handling
        pass
    
    def test_ai_output_security(self):
        """Test AI-generated code for security issues."""
        # Test for injection vulnerabilities, unsafe practices
        pass
    
    def test_secrets_handling(self):
        """Test proper secrets management."""
        # Ensure no secrets in generated code
        pass
