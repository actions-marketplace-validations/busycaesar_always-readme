from env_vars import get_env, INPUT_PREFIX, workspace
from constants import DEFAULT_README_PATH
import os
import sys
from utils import (
    configure_git_safe_directory,
    configure_git_identity,
    get_diff,
    set_output,
    get_readme_content,
    build_prompt,
    update_readme_file,
    create_or_reset_branch,
    commit_readme_change,
    push_branch,
    get_default_branch,
    has_open_pr,
    create_pr,
)
from agent import agent_ask

def main():
    base_ref = get_env(f"{INPUT_PREFIX}_BASE-REF", default="")

    configure_git_safe_directory(workspace)

    git_diff = get_diff(workspace, base_ref)

    if not git_diff:
        print("No code changes detected - skipping README.md update.")
        set_output("false")
        return
    
    readme_path = get_env(f"{INPUT_PREFIX}_README-PATH", default=DEFAULT_README_PATH)
    readme_file_path = os.path.join(workspace, readme_path)

    readme_content = get_readme_content(readme_file_path)

    if not readme_content:
        print(f"No README.md found at {readme_path} - generating a new one.")

    prompt = build_prompt(git_diff, readme_content)

    updated_readme = agent_ask(prompt)

    if updated_readme == readme_content:
        print("README already up to date.")
        set_output("false")
        return
    
    update_readme_file(readme_file_path, updated_readme)

    configure_git_identity()
    create_or_reset_branch(workspace)
    commit_readme_change(workspace, readme_file_path)
    push_branch(workspace)

    default_branch = get_default_branch(workspace)

    if not has_open_pr(workspace):
        create_pr(workspace, default_branch)

    set_output("true")

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"::error:: Unexpected error: {e}.")
        sys.exit(1)