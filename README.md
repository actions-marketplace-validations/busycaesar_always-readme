# Always-Readme

A GitHub Action that uses AI to keep your `README.md` up to date automatically. On every push, it diffs your recent code changes, hands them to an LLM along with the current README, and commits back an updated (or brand new) README — so documentation never goes stale.

## Features

- Automatically updates `README.md` based on the latest git diff.
- Generates a brand new `README.md` from scratch if one doesn't exist yet.
- Only touches sections that are actually outdated or incomplete — preserves existing tone and structure.
- Skips the update entirely when there are no code changes or the README is already accurate (keeps the `updated` output as `"false"`).
- Commits any real change to a `readme-update` branch and opens (or updates) a pull request into your default branch for review — it never merges automatically.
- Configurable README path, diff base ref, and OpenAI model.

## How It Works

1. Configures git to treat the workspace as a safe directory.
2. Computes the diff between `base-ref` (or the previous commit, by default) and `HEAD`.
3. If there's no diff, exits early without changes.
4. Reads the existing README (if any) at `readme-path`.
5. Builds a prompt combining the diff and current README content.
6. Sends the prompt to OpenAI's chat completions API and receives the full, updated README content.
7. Writes the result back to disk. If it's unchanged from the current README, sets the `updated` output to `"false"` and stops.
8. Otherwise, commits the change to a `readme-update` branch (as `Always Readme Bot`), force-pushes it, and opens a pull request into the repo's default branch — or updates the existing open PR on that branch, if there is one. The action never merges the PR itself; a human always reviews and merges it.
9. Sets the `updated` output to `"true"`.

## Usage

```yaml
name: Update README

on:
  push:
    branches: [main]

jobs:
  update-readme:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Always-Readme
        id: always-readme
        uses: busycaesar/always-readme@v1
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          openai-org-id: ${{ secrets.OPENAI_ORG_ID }}
          openai-project: ${{ secrets.OPENAI_PROJECT }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

## Inputs

| Name             | Required | Default       | Description                                                               |
| ---------------- | -------- | ------------- | ------------------------------------------------------------------------- |
| `openai-api-key` | Yes      | —             | OpenAI API key.                                                           |
| `openai-org-id`  | Yes      | —             | OpenAI organization ID.                                                   |
| `openai-project` | Yes      | —             | OpenAI project ID.                                                        |
| `github-token`   | Yes      | —             | GitHub token used to push the README branch and open a PR.                |
| `readme-path`    | No       | `README.md`   | Path to the README file to check and update.                              |
| `model`          | No       | `gpt-4o-mini` | OpenAI model used to generate the README content.                         |
| `base-ref`       | No       | _(empty)_     | Git ref to diff against. Defaults to the previous commit (`HEAD^..HEAD`). |

## Outputs

| Name      | Description                                              |
| --------- | -------------------------------------------------------- |
| `updated` | Whether `README.md` was modified (`"true"` / `"false"`). |

## Requirements

- Python 3.11 (bundled in the action's Docker image — no local setup needed to use the action).
- `contents: write` and `pull-requests: write` permissions and `fetch-depth: 0` on checkout, so the action has full git history to diff against, can push a `readme-update` branch, and can open a pull request for it.

## Local Development

```bash
pip install -r req.txt

# Input env vars contain hyphens (see src/env_vars.py), so set them via `env`
# rather than `export`, which doesn't accept hyphenated names.
env \
  INPUT_OPENAI-API-KEY=... \
  INPUT_OPENAI-ORG-ID=... \
  INPUT_OPENAI-PROJECT=... \
  INPUT_GITHUB-TOKEN=... \
  GITHUB_WORKSPACE="$(pwd)" \
  GITHUB_REPOSITORY="owner/repo" \
  python src/update_readme.py
```

Or via Docker:

```bash
docker build -t always-readme .
docker run --rm always-readme
```

## License

[MIT](LICENSE)

## Author

[Dev J. Shah](https://github.com/busycaesar)
