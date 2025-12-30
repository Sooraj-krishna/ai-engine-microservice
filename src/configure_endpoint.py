"""
Configuration endpoint for the AI Engine Microservice
Handles configuration updates from the web UI
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path

router = APIRouter()

class ConfigurationRequest(BaseModel):
    websiteUrl: str
    githubRepo: str
    monitoringMode: str
    # Tokens/keys are now optional; we prefer existing env values
    githubToken: str | None = None
    geminiApiKey: str | None = None
    gaPropertyId: str | None = None
    useImprovedFixer: bool = False
    testFixesBeforeApply: bool = True

@router.post("/configure")
async def configure_engine(config: ConfigurationRequest):
    """
    Update the AI Engine configuration with new settings from the UI.
    """
    try:
        # Use provided values or fall back to existing environment
        github_token = config.githubToken or os.getenv("GITHUB_TOKEN", "")
        gemini_api_key = config.geminiApiKey or os.getenv("GEMINI_API_KEY", "")
        ga_property_id = config.gaPropertyId or os.getenv("GA4_PROPERTY_ID", "")

        # Create .env content
        env_content = f"""# AI Engine Configuration
# Generated from Web UI

# Website configuration
WEBSITE_URL={config.websiteUrl}
MONITORING_MODE={config.monitoringMode}

# Google Analytics configuration
GA4_PROPERTY_ID={ga_property_id}
GOOGLE_APPLICATION_CREDENTIALS=/home/devils_hell/ai-engine-microservice/ai-engine-468315-d97caaac7f70.json

# GitHub and AI configuration
GITHUB_TOKEN={github_token}
GITHUB_REPO={config.githubRepo}
GEMINI_API_KEY={gemini_api_key}
GEMINI_MODEL=gemini-1.5-flash-latest
GEMINI_PRO_MODEL=gemini-1.5-pro-latest

# Advanced options
USE_IMPROVED_FIXER={'true' if config.useImprovedFixer else 'false'}
TEST_FIXES_BEFORE_APPLY={'true' if config.testFixesBeforeApply else 'false'}
"""

        # Write to .env file
        env_path = Path('.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        # Update environment variables
        os.environ['WEBSITE_URL'] = config.websiteUrl
        os.environ['GITHUB_REPO'] = config.githubRepo
        os.environ['GITHUB_TOKEN'] = github_token
        os.environ['GEMINI_API_KEY'] = gemini_api_key
        os.environ['GA4_PROPERTY_ID'] = ga_property_id
        os.environ['MONITORING_MODE'] = config.monitoringMode
        os.environ['USE_IMPROVED_FIXER'] = 'true' if config.useImprovedFixer else 'false'
        os.environ['TEST_FIXES_BEFORE_APPLY'] = 'true' if config.testFixesBeforeApply else 'false'

        return {
            "status": "success",
            "message": "Configuration updated successfully",
            "config": {
                "website_url": config.websiteUrl,
                "github_repo": config.githubRepo,
                "monitoring_mode": config.monitoringMode,
                "has_github_token": bool(github_token),
                "has_gemini_token": bool(gemini_api_key),
                "has_ai_api": bool(gemini_api_key),
                "has_ga_property": bool(ga_property_id),
                "use_improved_fixer": config.useImprovedFixer,
                "test_fixes_before_apply": config.testFixesBeforeApply
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update configuration: {str(e)}"
        )

@router.get("/config")
async def get_configuration():
    """
    Get current configuration status.
    """
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    
    return {
        "website_url": os.getenv("WEBSITE_URL"),
        "github_repo": os.getenv("GITHUB_REPO"),
        "monitoring_mode": os.getenv("MONITORING_MODE"),
        "has_github_token": bool(os.getenv("GITHUB_TOKEN")),
        "has_gemini_token": has_gemini,
        "has_ai_api": has_gemini,
        "has_ga_property": bool(os.getenv("GA4_PROPERTY_ID")),
        "use_improved_fixer": os.getenv("USE_IMPROVED_FIXER", "false").lower() == "true",
        "test_fixes_before_apply": os.getenv("TEST_FIXES_BEFORE_APPLY", "true").lower() == "true"
    }
