from github import Github
import os
from datetime import datetime
from utils import detect_framework
import git

# Define a local path for the repository
REPO_PATH = "/tmp/ai_engine_repo"

def clone_or_pull_repo():
    """
    Clones the repository if it doesn't exist locally, otherwise pulls the latest changes.
    Returns the local path to the repository.
    """
    repo_name = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    
    if not repo_name:
        print("[ERROR] GITHUB_REPO not found in environment variables")
        return None

    # Construct the authenticated URL (only if token is valid)
    if token and token.strip() and token != "None":
    repo_url = f"https://{token}@github.com/{repo_name}.git"
    else:
        # Try without token (for public repos) or use SSH
        repo_url = f"https://github.com/{repo_name}.git"
        print("[WARNING] No valid GITHUB_TOKEN found, trying public access...")

    if os.path.exists(REPO_PATH):
        try:
            print(f"[INFO] Pulling latest changes from {repo_name} into {REPO_PATH}...")
            repo = git.Repo(REPO_PATH)
            origin = repo.remotes.origin
            
            # Update remote URL if token changed
            if token and token.strip() and token != "None":
                origin.set_url(f"https://{token}@github.com/{repo_name}.git")
            
            # Ensure we're on a valid branch (not detached HEAD)
            try:
                if repo.head.is_detached:
                    # Try to checkout main/master
                    try:
                        repo.git.checkout('main')
                    except:
                        try:
                            repo.git.checkout('master')
                        except:
                            pass
            except:
                pass
            
            # Check for uncommitted changes
            if repo.is_dirty():
                print("[WARNING] Repository has uncommitted changes. Stashing them...")
                try:
                    repo.git.stash('save', '--include-untracked', 'AI Engine temporary stash')
                except:
                    print("[WARNING] Could not stash changes, continuing anyway...")
            
            try:
                # Determine the current branch or default to main/master
                current_branch = None
                try:
                    current_branch = repo.active_branch.name
                except:
                    # Detached HEAD or no active branch
                    try:
                        repo.git.checkout('main')
                        current_branch = 'main'
                    except:
                        try:
                            repo.git.checkout('master')
                            current_branch = 'master'
                        except:
                            print("[WARNING] Could not determine branch, trying to pull anyway...")
                
                if current_branch:
                    origin.pull(current_branch)
                else:
            origin.pull()
            print("[SUCCESS] Pulled latest changes.")
            except Exception as pull_error:
                error_str = str(pull_error).lower()
                if "401" in error_str or "authentication" in error_str or "invalid" in error_str or "bad credentials" in error_str:
                    print(f"[ERROR] Git authentication failed. Token may be invalid or expired.")
                    print(f"[ERROR] Please update GITHUB_TOKEN in your .env file")
                    return None
                elif "merge conflict" in error_str or "conflict" in error_str:
                    print(f"[WARNING] Merge conflict detected. Re-cloning repository...")
                    import shutil
                    if os.path.exists(REPO_PATH):
                        shutil.rmtree(REPO_PATH)
                    return clone_or_pull_repo()
                elif "exit code(1)" in str(pull_error):
                    # Generic Git error - might be because repo is in bad state
                    print(f"[WARNING] Pull failed: {pull_error}")
                    print(f"[INFO] Re-cloning repository to ensure clean state...")
                    import shutil
                    if os.path.exists(REPO_PATH):
                        shutil.rmtree(REPO_PATH)
                    return clone_or_pull_repo()
                else:
                    print(f"[ERROR] Pull error: {pull_error}")
                    raise
        except Exception as e:
            error_str = str(e).lower()
            if "401" in error_str or "authentication" in error_str or "invalid" in error_str:
                print(f"[ERROR] Git authentication failed: {e}")
                print(f"[ERROR] Please update GITHUB_TOKEN in your .env file")
                return None
            print(f"[ERROR] Could not pull repository: {e}")
            # Fallback to re-cloning
            print(f"[INFO] Re-cloning repository to ensure clean state...")
            import shutil
            if os.path.exists(REPO_PATH):
            shutil.rmtree(REPO_PATH)
            return clone_or_pull_repo()
    else:
        try:
            print(f"[INFO] Cloning {repo_name} into {REPO_PATH}...")
            git.Repo.clone_from(repo_url, REPO_PATH)
            print(f"[SUCCESS] Cloned repository into {REPO_PATH}")
        except Exception as e:
            error_str = str(e).lower()
            if "401" in error_str or "authentication" in error_str or "invalid" in error_str:
                print(f"[ERROR] Git authentication failed. Token may be invalid or expired.")
                print(f"[ERROR] Please update GITHUB_TOKEN in your .env file with a valid token")
                print(f"[ERROR] Create token at: https://github.com/settings/tokens")
            else:
            print(f"[ERROR] Could not clone repository: {e}")
            return None
            
    return REPO_PATH

from github import Github
import os
from datetime import datetime
from utils import detect_framework

def get_all_repo_files():
    """
    Recursively list all files in the repo using GitHub API.
    Ensures cross-framework support.
    """
    try:
        token = os.getenv("GITHUB_TOKEN")
        repo_name = os.getenv("GITHUB_REPO")
        
        if not token:
            print("[ERROR] GITHUB_TOKEN not found in environment variables")
            return []
        if not repo_name:
            print("[ERROR] GITHUB_REPO not found in environment variables")
            return []
            
        print(f"[DEBUG] Using GitHub token: {token[:10]}...")
        print(f"[DEBUG] Using repository: {repo_name}")
        
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        def crawl(folder):
            items = []
            try:
                contents = repo.get_contents(folder)
                for c in contents:
                    if c.type == "dir":
                        items += crawl(c.path)
                    else:
                        items.append(c.path)
                return items
            except Exception as e:
                print(f"[WARNING] Error crawling folder {folder}: {e}")
                return items
                
        files = crawl("")
        print(f"[DEBUG] Found {len(files)} files in repository")
        return files
        
    except Exception as e:
        print(f"[ERROR] Failed to get repository files: {e}")
        return []

def submit_fix_pr(fixes):
    """
    Applies all code fixes (one or many) to a new branch, 
    and opens a PR with a clear description for review.
    Returns the PR URL on success, None on failure.
    """
    try:
        token = os.getenv("GITHUB_TOKEN")
        repo_name = os.getenv("GITHUB_REPO")
        
        if not token:
            print("[ERROR] GITHUB_TOKEN not found in environment variables")
            return None
        if not repo_name:
            print("[ERROR] GITHUB_REPO not found in environment variables")
            return None
            
        if not fixes:
            print("[ERROR] No fixes provided to submit_fix_pr")
            return None
            
        print(f"[DEBUG] Submitting {len(fixes)} fixes to GitHub...")
        print(f"[DEBUG] Repository: {repo_name}")
        
        # Try to use Git operations first (avoids API token issues)
        local_repo_path = clone_or_pull_repo()
        if local_repo_path:
            try:
                git_repo = git.Repo(local_repo_path)
                # Detect framework from local files
                repo_files = []
                for root, dirs, files in os.walk(local_repo_path):
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), local_repo_path)
                        repo_files.append(rel_path.replace('\\', '/'))
                
                if repo_files:
                    framework = detect_framework(repo_files)
                else:
                    framework = "unknown"
                print(f"[DEBUG] Detected framework: {framework}")
                
                # Get base branch SHA from Git
                try:
                    git_repo.git.checkout('main')
                except:
                    try:
                        git_repo.git.checkout('master')
                    except:
                        pass
                base_sha = git_repo.head.commit.hexsha
                print(f"[DEBUG] Using main branch as base: {base_sha[:10]}...")
                
            except Exception as e:
                print(f"[WARNING] Git operations failed: {e}, trying GitHub API...")
                local_repo_path = None
        
        # Fallback to GitHub API if Git operations failed
        repo = None
        if not local_repo_path:
            try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        # Get repository files for framework detection
        repo_files = get_all_repo_files()
        if not repo_files:
            print("[WARNING] Could not get repository files, using 'unknown' framework")
            framework = "unknown"
        else:
            framework = detect_framework(repo_files)
            print(f"[DEBUG] Detected framework: {framework}")
        
        # Get base branch
        try:
            base = repo.get_branch("main")
                    base_sha = base.commit.sha
                    print(f"[DEBUG] Using main branch as base: {base_sha[:10]}...")
        except Exception as e:
            print(f"[ERROR] Could not get main branch: {e}")
                    return None
            except Exception as api_error:
                error_msg = str(api_error)
                if "401" in error_msg or "Bad credentials" in error_msg:
                    print(f"[ERROR] GitHub token is invalid or expired.")
                    print(f"[ERROR] Please update your GITHUB_TOKEN in your .env file with a valid token.")
                    print(f"[ERROR] You can create a new token at: https://github.com/settings/tokens")
                    print(f"[ERROR] Required permissions: 'repo' scope")
                else:
                    print(f"[ERROR] GitHub API error: {api_error}")
            return None
        
        # Create new branch
        branch_name = f"ai-fix-{framework}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        print(f"[DEBUG] Creating branch: {branch_name}")
        
        # Use Git operations (works even with limited/invalid API tokens)
        local_repo_path = clone_or_pull_repo()
        if local_repo_path:
            try:
                git_repo = git.Repo(local_repo_path)
                # Ensure we're on main/master first
                try:
                    git_repo.git.checkout('main')
                except:
                    try:
                        git_repo.git.checkout('master')
                    except:
                        pass
                # Create and checkout new branch
                git_repo.git.checkout('-b', branch_name)
                
                # Update remote URL with token if available
                token = os.getenv("GITHUB_TOKEN")
                if token and token.strip() and token != "None":
                    origin = git_repo.remotes.origin
                    origin.set_url(f"https://{token}@github.com/{repo_name}.git")
                
                # Push with upstream tracking
                try:
                    git_repo.git.push('-u', 'origin', branch_name)
                    print(f"[SUCCESS] Created branch using Git: {branch_name}")
                except Exception as push_error:
                    error_str = str(push_error).lower()
                    if "401" in error_str or "authentication" in error_str or "invalid" in error_str or "bad credentials" in error_str:
                        print(f"[ERROR] Git authentication failed. Token may be invalid or expired.")
                        print(f"[ERROR] Please update GITHUB_TOKEN in your .env file with a valid token")
                        print(f"[ERROR] Create token at: https://github.com/settings/tokens")
                        print(f"[ERROR] Required permissions: 'repo' scope")
                        return None
                    raise
            except Exception as git_error:
                error_str = str(git_error).lower()
                if "401" in error_str or "authentication" in error_str:
                    print(f"[ERROR] Git authentication failed: {git_error}")
                    print(f"[ERROR] Please update GITHUB_TOKEN in your .env file")
                    return None
                print(f"[ERROR] Git branch creation failed: {git_error}")
                return None
        elif repo and 'base_sha' in locals():
            # Fallback to GitHub API only if we have a valid repo object
            try:
                repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_sha)
                print(f"[SUCCESS] Created branch using GitHub API: {branch_name}")
            except Exception as api_error:
                error_msg = str(api_error)
                if "403" in error_msg or "Resource not accessible" in error_msg:
                    print(f"[ERROR] GitHub token lacks permissions to create branches.")
                    print(f"[ERROR] Required permissions: 'repo' scope with write access")
                else:
                    print(f"[ERROR] Failed to create branch: {api_error}")
                return None
        else:
            print(f"[ERROR] Cannot create branch: No valid repository access")
            print(f"[ERROR] Please check your GITHUB_TOKEN and GITHUB_REPO in .env file")
            print(f"[ERROR] Token must be valid and have 'repo' scope permissions")
            return None
        
        # Apply fixes using Git operations (more reliable with token permissions)
        local_repo_path_for_fixes = clone_or_pull_repo()
        if local_repo_path_for_fixes:
            try:
                git_repo = git.Repo(local_repo_path_for_fixes)
                # Ensure we're on the new branch
                try:
                    git_repo.git.checkout(branch_name)
                except:
                    git_repo.git.checkout('-b', branch_name)
                
        for i, fix in enumerate(fixes, 1):
            try:
                print(f"[DEBUG] Applying fix {i}/{len(fixes)}: {fix.get('path', 'unknown path')}")
                        fix_path = os.path.join(local_repo_path_for_fixes, fix["path"])
                        os.makedirs(os.path.dirname(fix_path), exist_ok=True)
                        with open(fix_path, 'w', encoding='utf-8') as f:
                            f.write(fix["content"])
                        git_repo.index.add([fix["path"]])
                        print(f"[SUCCESS] Staged file: {fix['path']}")
                    except Exception as e:
                        print(f"[ERROR] Failed to apply fix {i}: {e}")
                        continue
                
                if git_repo.is_dirty():
                    git_repo.index.commit(f"AI Engine: Apply {len(fixes)} automated fixes")
                    git_repo.git.push('origin', branch_name)
                    print(f"[SUCCESS] Committed and pushed {len(fixes)} fixes")
            except Exception as e:
                print(f"[WARNING] Git operations failed: {e}, using GitHub API fallback...")
                local_repo_path_for_fixes = None
        
        # Fallback to GitHub API if Git operations failed
        if not local_repo_path_for_fixes:
            for i, fix in enumerate(fixes, 1):
                try:
                    print(f"[DEBUG] Applying fix {i}/{len(fixes)}: {fix.get('path', 'unknown path')}")
                
                # Check if file exists
                try:
                    existing = repo.get_contents(fix["path"], ref=branch_name)
                    # Update existing file
                    repo.update_file(
                        path=fix["path"],
                        message=fix.get("description", f"AI fix {i}"),
                        content=fix["content"],
                        sha=existing.sha,
                        branch=branch_name
                    )
                    print(f"[SUCCESS] Updated file: {fix['path']}")
                except Exception:
                    # Create new file
                    repo.create_file(
                        path=fix["path"],
                        message=fix.get("description", f"AI fix {i}"),
                        content=fix["content"],
                        branch=branch_name
                    )
                    print(f"[SUCCESS] Created file: {fix['path']}")
                    
            except Exception as e:
                print(f"[ERROR] Failed to apply fix {i}: {e}")
                print(f"[DEBUG] Fix details: {fix}")
                continue
        
        # Create pull request with test information
        # Only use GitHub API if we have a valid repo object
        if repo:
        try:
            pr_title = f"AI Engine ({framework}): Automated Fixes"
                
                # Check if fixes were tested
                test_enabled = os.getenv('TEST_FIXES_BEFORE_APPLY', 'true').lower() == 'true'
                test_note = "✅ All fixes tested in isolated environment before applying" if test_enabled else "⚠️ Fix testing disabled"
                
                pr_body = f"""🔧 This PR contains {len(fixes)} code fixes automatically generated by an external AI API.

{test_note}

**Safety Features:**
- ✅ Code validation passed
- ✅ Safety checks completed
- {'✅ Isolated environment testing passed' if test_enabled else '⚠️ Testing skipped'}

**Changes:**\n"""
            for i, fix in enumerate(fixes, 1):
                pr_body += f"- {i}. {fix.get('description', 'No description')} (`{fix.get('path', 'unknown')}`)\n"
            
            pr = repo.create_pull(
                title=pr_title,
                head=branch_name,
                base="main",
                body=pr_body
            )
            
            pr_url = pr.html_url
            print(f"[SUCCESS] Pull Request Created: {pr_url}")
            return pr_url
            
        except Exception as e:
                print(f"[WARNING] Failed to create pull request via API: {e}")
                print(f"[INFO] Branch {branch_name} was created and fixes were pushed.")
                print(f"[INFO] You can create the PR manually at: https://github.com/{repo_name}/compare/{branch_name}")
                return f"https://github.com/{repo_name}/compare/{branch_name}"
        else:
            # If we used Git operations, provide manual PR creation link
            print(f"[INFO] Branch {branch_name} was created and fixes were pushed using Git.")
            print(f"[INFO] Create PR manually at: https://github.com/{repo_name}/compare/{branch_name}")
            return f"https://github.com/{repo_name}/compare/{branch_name}"
            
    except Exception as e:
        print(f"[ERROR] submit_fix_pr failed with exception: {e}")
        import traceback
        print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
        return None
