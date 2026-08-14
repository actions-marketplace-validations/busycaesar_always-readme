import json
import os
import subprocess
import sys
from env_vars import output_file, github_token, repository, gh_environment
from constants import (
    DEFAULT_OUTPUT_NAME,
    BRANCH_NAME,
    COMMIT_AUTHOR_NAME,
    COMMIT_AUTHOR_EMAIL,
    COMMIT_MESSAGE,
    PR_TITLE,
    PR_BODY,
)

def configure_git_safe_directory(workspace):
    try:
        subprocess.run(
            ["git", "config", "--global", "--add", "safe.directory", workspace],
            check=True
        )
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"::error:: Failed to configure git safe directory: {e}.")
        sys.exit(1)

def configure_git_identity():
    try:
        subprocess.run(
            ["git", "config", "--global", "user.name", COMMIT_AUTHOR_NAME],
            check=True
        )
        subprocess.run(
            ["git", "config", "--global", "user.email", COMMIT_AUTHOR_EMAIL],
            check=True
        )
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"::error:: Failed to configure git commit identity: {e}.")
        sys.exit(1)

def get_diff(workspace, base_ref):
    diff_range = f"{base_ref}..HEAD" if base_ref else "HEAD^..HEAD"

    # Execute the git diff command using subprocess.
    result = subprocess.run(
        ["git", "diff", diff_range],
        cwd=workspace,
        capture_output=True,
        text=True
    )

    git_diff = result.stdout if result.returncode == 0 else ""

    return git_diff.strip()

def set_output(value):
    if not output_file:
        return

    with open(output_file, "a", encoding="utf-8") as f:
        f.write(f"{DEFAULT_OUTPUT_NAME}={value}\n")

def get_readme_content(readme_path):
    if not os.path.isfile(readme_path):
        return ""

    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()
    except OSError as e:
        print(f"::error:: Failed to read README.md at {readme_path}: {e}.")
        sys.exit(1)

    return readme_content if readme_content else ""

def build_prompt(git_diff, readme_content):
    if not readme_content:
        return (
            "You are creating a new README.md for a project based on its recent code changes.\n"
            "No README.md currently exists. Generate a complete, well-structured README.md from the diff below. "
            "Return the FULL README.md content and nothing else — no explanations, no code fences.\n\n"
            f"## Git diff\n{git_diff}"
        )

    return (
        "You are updating a project's README.md to reflect recent code changes.\n"
        "Rules:\n"
        "1. Only touch parts of the README that are now outdated or incorrect because of the diff below. "
        "If nothing in the diff affects the README, return it completely unchanged.\n"
        "2. Do not add any new section unless the diff introduces something that has no existing section to "
        "document it and clearly warrants one (e.g. a new feature, input, or command). When in doubt, don't add one.\n"
        "3. Do not fix, rewrite, or improve any existing wording, formatting, or structure that is unrelated to "
        "the diff — even if you think it could be better. Leave unrelated sections byte-for-byte untouched.\n"
        "Return the FULL updated README.md content and nothing else — no explanations, no code fences.\n\n"
        f"## Git diff\n{git_diff}\n\n"
        f"## Current README.md\n{readme_content}"
    )

def update_readme_file(readme_path, updated_readme_content):
    readme_dir = os.path.dirname(readme_path)

    try:
        if readme_dir:
            os.makedirs(readme_dir, exist_ok=True)

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_readme_content)
    except OSError as e:
        print(f"::error:: Failed to write README.md at {readme_path}: {e}.")
        sys.exit(1)

def create_or_reset_branch(workspace):
    try:
        subprocess.run(
            ["git", "checkout", "-B", BRANCH_NAME],
            cwd=workspace,
            check=True
        )
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"::error:: Failed to create/reset branch {BRANCH_NAME}: {e}.")
        sys.exit(1)

def commit_readme_change(workspace, readme_path):
    try:
        subprocess.run(
            ["git", "add", readme_path],
            cwd=workspace,
            check=True
        )
        subprocess.run(
            ["git", "commit", "-m", COMMIT_MESSAGE],
            cwd=workspace,
            check=True
        )
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"::error:: Failed to commit README change: {e}.")
        sys.exit(1)

def push_branch(workspace):
    if not repository:
        print("::error:: Missing required environment variable: GITHUB_REPOSITORY.")
        sys.exit(1)

    remote_url = f"https://x-access-token:{github_token}@github.com/{repository}.git"

    try:
        subprocess.run(
            ["git", "push", "--force", remote_url, f"HEAD:{BRANCH_NAME}"],
            cwd=workspace,
            check=True,
            capture_output=True,
            text=True
        )
    except (subprocess.CalledProcessError, OSError):
        print(f"::error:: Failed to push branch {BRANCH_NAME}.")
        sys.exit(1)

def get_default_branch(workspace):
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name"],
            cwd=workspace,
            check=True,
            capture_output=True,
            text=True,
            env=gh_environment
        )
    except (subprocess.CalledProcessError, OSError) as e:
        detail = e.stderr.strip() if isinstance(e, subprocess.CalledProcessError) and e.stderr else str(e)
        print(f"::error:: Failed to detect default branch: {detail}.")
        sys.exit(1)

    return result.stdout.strip()

def has_open_pr(workspace):
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--head", BRANCH_NAME, "--state", "open", "--json", "number"],
            cwd=workspace,
            check=True,
            capture_output=True,
            text=True,
            env=gh_environment
        )
    except (subprocess.CalledProcessError, OSError) as e:
        detail = e.stderr.strip() if isinstance(e, subprocess.CalledProcessError) and e.stderr else str(e)
        print(f"::error:: Failed to check for existing pull requests: {detail}.")
        sys.exit(1)

    return len(json.loads(result.stdout)) > 0

def create_pr(workspace, default_branch):
    try:
        subprocess.run(
            ["gh", "pr", "create", "--head", BRANCH_NAME, "--base", default_branch, "--title", PR_TITLE, "--body", PR_BODY],
            cwd=workspace,
            check=True,
            capture_output=True,
            text=True,
            env=gh_environment
        )
    except (subprocess.CalledProcessError, OSError) as e:
        detail = e.stderr.strip() if isinstance(e, subprocess.CalledProcessError) and e.stderr else str(e)
        print(f"::error:: Failed to create pull request: {detail}.")
        sys.exit(1)