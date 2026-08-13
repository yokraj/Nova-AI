"""Utility helper functions including Git repository profile detector.
"""

import os
import re
import subprocess
from typing import Dict, List, Optional
from app.agents.software_engineer.repository.models import GitInfo


def detect_git_info(workspace_path: str) -> Optional[GitInfo]:
    """Inspects workspace directory for active Git repositories and metadata.

    Args:
        workspace_path: Target directory.

    Returns:
        GitInfo instance if git repo is found, None otherwise.
    """
    curr = os.path.abspath(workspace_path)
    git_dir = None
    while True:
        potential = os.path.join(curr, ".git")
        if os.path.exists(potential) and os.path.isdir(potential):
            git_dir = potential
            break
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent

    if not git_dir:
        return None

    repo_root = os.path.dirname(git_dir)

    branch = None
    remotes: Dict[str, str] = {}
    tags: List[str] = []
    is_clean = True
    commit_count = None
    repo_size = 0

    # 1. Active Branch
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        branch = res.stdout.strip()
    except Exception:
        # Fallback pure Python HEAD parser
        try:
            head_path = os.path.join(git_dir, "HEAD")
            if os.path.exists(head_path):
                with open(head_path, "r", encoding="utf-8") as f:
                    line = f.read().strip()
                    if line.startswith("ref:"):
                        branch = line.split("/")[-1]
                    else:
                        branch = line[:7]
        except Exception:
            pass

    # 2. Configured Remotes
    try:
        res = subprocess.run(
            ["git", "remote", "-v"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        for line in res.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                remotes[parts[0]] = parts[1]
    except Exception:
        # Fallback pure Python git config parser
        try:
            config_path = os.path.join(git_dir, "config")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    matches = re.findall(r'\[remote\s+"([^"]+)"\]\s+url\s*=\s*([^\s]+)', content)
                    for r_name, r_url in matches:
                        remotes[r_name] = r_url
        except Exception:
            pass

    # 3. Tags
    try:
        res = subprocess.run(
            ["git", "tag"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        tags = [t.strip() for t in res.stdout.splitlines() if t.strip()]
    except Exception:
        # Fallback pure Python tags list
        try:
            tags_dir = os.path.join(git_dir, "refs", "tags")
            if os.path.exists(tags_dir):
                tags = os.listdir(tags_dir)
            packed_refs = os.path.join(git_dir, "packed-refs")
            if os.path.exists(packed_refs):
                with open(packed_refs, "r", encoding="utf-8") as f:
                    for line in f:
                        if "refs/tags/" in line:
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                tag_name = parts[1].replace("refs/tags/", "")
                                if tag_name not in tags:
                                    tags.append(tag_name)
        except Exception:
            pass

    # 4. Clean/Dirty State
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        is_clean = len(res.stdout.strip()) == 0
    except Exception:
        is_clean = True

    # 5. Commit Count
    try:
        res = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        commit_count = int(res.stdout.strip())
    except Exception:
        # Fallback pure Python commit logs counter
        try:
            head_logs = os.path.join(git_dir, "logs", "HEAD")
            if os.path.exists(head_logs):
                with open(head_logs, "r", encoding="utf-8") as f:
                    commit_count = sum(1 for _ in f)
        except Exception:
            pass

    # 6. Repository total size
    try:
        total_size = 0
        for root, dirs, files in os.walk(repo_root):
            for file in files:
                fp = os.path.join(root, file)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        repo_size = total_size
    except Exception:
        pass

    return GitInfo(
        repository_root=repo_root,
        branch=branch,
        remotes=remotes,
        tags=tags,
        is_clean=is_clean,
        repository_size=repo_size,
        commit_count=commit_count,
    )
