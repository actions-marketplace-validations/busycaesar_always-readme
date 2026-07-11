import os
import subprocess
import sys
from env_vars import output_file
from config import DEFAULT_OUTPUT_NAME

def configure_git_safe_directory(workspace):
    try:
        subprocess.run(
            ["git", "config", "--global", "--add", "safe.directory", workspace],
            check=True
        )
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"::error:: Failed to configure git safe directory: {e}.")
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
        "Only change sections that are outdated or incomplete because of the diff below. "
        "Keep the existing tone, structure, and any unaffected sections untouched. "
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