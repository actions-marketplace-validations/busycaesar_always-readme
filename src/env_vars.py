import os
import sys
from constants import DEFAULT_MODEL

# Prefix for input variales coming from action.yml.
INPUT_PREFIX = "INPUT"

def get_env(name, default=None, required=False):
    value = os.environ.get(name, default)

    if required and not value:
        print(f"::error:: Missing required input: {name}.")
        sys.exit(1)

    return value

openai_api_key = get_env(f"{INPUT_PREFIX}_OPENAI-API-KEY", required=True)
openai_org_id = get_env(f"{INPUT_PREFIX}_OPENAI-ORG-ID", required=True)
openai_project = get_env(f"{INPUT_PREFIX}_OPENAI-PROJECT", required=True)
model = get_env(f"{INPUT_PREFIX}_MODEL", default=DEFAULT_MODEL)
github_token = get_env(f"{INPUT_PREFIX}_GITHUB-TOKEN", required=True)

workspace = os.environ["GITHUB_WORKSPACE"]
output_file = os.environ.get("GITHUB_OUTPUT")
repository = os.environ.get("GITHUB_REPOSITORY")
gh_environment = {**os.environ, "GH_TOKEN": github_token}