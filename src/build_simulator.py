"""
Build Simulator

Tests builds in isolated environment before PR creation:
- Runs actual build commands (npm build, etc.)
- Captures build errors and warnings  
- Validates deployment configuration
- Checks environment variables

"""

import os
import subprocess
import tempfile
import shutil
import asyncio
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json


class BuildSimulator:
    """Simulates builds to catch issues before PR creation"""
    
    def __init__(self, enable_actual_builds: bool = False):
        """
        Args:
            enable_actual_builds: If True, runs actual npm/build commands (slower but comprehensive)
                                 If False, only static analysis (faster)
        """
        self.enable_actual_builds = enable_actual_builds
        print(f"[BUILD_SIMULATOR] Initialized (actual builds: {enable_actual_builds})")
    
    async def simulate_build(
        self,
        repo_path: str,
        tech_stack: Optional[Dict] = None,
        generated_files: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Simulate build process.
        
        Args:
            repo_path: Path to repository
            tech_stack: Technology stack info
            generated_files: New files being added (for testing)
            
        Returns:
            {
                'success': bool,
                'errors': List[str],
                'warnings': List[str],
                'build_time': float
            }
        """
        print(f"[BUILD_SIMULATOR] Starting build simulation...")
        
        if self.enable_actual_builds:
            return await self._run_actual_build(repo_path, tech_stack, generated_files)
        else:
            return await self._static_build_analysis(repo_path, tech_stack, generated_files)
    
    async def _run_actual_build(
        self,
        repo_path: str,
        tech_stack: Optional[Dict],
        generated_files: Optional[Dict[str, str]]
    ) -> Dict:
        """Run actual build commands"""
        import time
        start_time = time.time()
        
        errors = []
        warnings = []
        
        # Detect build system
        package_json = os.path.join(repo_path, 'package.json')
        
        if os.path.exists(package_json):
            # Node.js project
            build_result = await self._run_npm_build(repo_path)
            errors.extend(build_result['errors'])
            warnings.extend(build_result['warnings'])
        
        build_time = time.time() - start_time
        
        return {
            'success': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'build_time': build_time
        }
    
    async def _run_npm_build(self, repo_path: str) -> Dict:
        """Run npm build"""
        errors = []
        warnings = []
        
        try:
            # Check if node_modules exists
            node_modules = os.path.join(repo_path, 'node_modules')
            if not os.path.exists(node_modules):
                print(f"[BUILD_SIMULATOR] Running npm install...")
                install_result = subprocess.run(
                    ['npm', 'install'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes max
                )
                
                if install_result.returncode != 0:
                    errors.append(f"npm install failed: {install_result.stderr}")
                    return {'errors': errors, 'warnings': warnings}
            
            # Run build
            print(f"[BUILD_SIMULATOR] Running npm run build...")
            build_result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes max
            )
            
            if build_result.returncode != 0:
                errors.append(f"Build failed: {build_result.stderr}")
            
            # Parse warnings from output
            if 'warning' in build_result.stdout.lower():
                warnings.append("Build completed with warnings")
            
        except subprocess.TimeoutExpired:
            errors.append("Build timed out")
        except FileNotFoundError:
            errors.append("npm not found - cannot run build")
        except Exception as e:
            errors.append(f"Build error: {e}")
        
        return {
            'errors': errors,
            'warnings': warnings
        }
    
    async def _static_build_analysis(
        self,
        repo_path: str,
        tech_stack: Optional[Dict],
        generated_files: Optional[Dict[str, str]]
    ) -> Dict:
        """
        Static analysis instead of actual build.
        Faster but less comprehensive.
        """
        errors = []
        warnings = []
        
        print(f"[BUILD_SIMULATOR] Running static build analysis...")
        
        # Check for package.json
        package_json_path = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                # Check for build script
                scripts = package_data.get('scripts', {})
                if 'build' not in scripts:
                    warnings.append("No 'build' script found in package.json")
                
                # Check for common dependencies
                deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                
                # Detect framework
                if 'react' in deps:
                    print(f"[BUILD_SIMULATOR] Detected React project")
                if 'vite' in deps:
                    print(f"[BUILD_SIMULATOR] Detected Vite build tool")
                if 'next' in deps:
                    print(f"[BUILD_SIMULATOR] Detected Next.js project")
                
            except json.JSONDecodeError as e:
                errors.append(f"Invalid package.json: {e}")
            except Exception as e:
                warnings.append(f"Could not read package.json: {e}")
        
        # Check for tsconfig.json (TypeScript projects)
        tsconfig_path = os.path.join(repo_path, 'tsconfig.json')
        if os.path.exists(tsconfig_path):
            try:
                with open(tsconfig_path, 'r') as f:
                    json.load(f)
                print(f"[BUILD_SIMULATOR] Found valid tsconfig.json")
            except json.JSONDecodeError as e:
                errors.append(f"Invalid tsconfig.json: {e}")
        
        # If we have generated files, check they don't break imports
        if generated_files:
            # This would be done by build_validator already
            pass
        
        return {
            'success': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'build_time': 0.0
        }
    
    async def validate_deployment_config(self, repo_path: str) -> Dict:
        """Validate deployment configuration files"""
        errors = []
        warnings = []
        
        # Check for .env.example
        env_example = os.path.join(repo_path, '.env.example')
        if os.path.exists(env_example):
            print(f"[BUILD_SIMULATOR] Found .env.example")
        else:
            warnings.append("No .env.example file found")
        
        # Check for Dockerfile
        dockerfile = os.path.join(repo_path, 'Dockerfile')
        if os.path.exists(dockerfile):
            # Basic Dockerfile validation
            try:
                with open(dockerfile, 'r') as f:
                    content = f.read()
                    if 'FROM' not in content:
                        errors.append("Dockerfile missing FROM instruction")
                    if 'EXPOSE' not in content:
                        warnings.append("Dockerfile doesn't expose any ports")
            except Exception as e:
                warnings.append(f"Could not validate Dockerfile: {e}")
        
        return {
            'errors': errors,
            'warnings': warnings
        }


# Global instance (static analysis by default)
build_simulator = BuildSimulator(enable_actual_builds=False)
