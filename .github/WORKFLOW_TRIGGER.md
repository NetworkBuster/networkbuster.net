# Triggering a Workflow in Another Repository (GH CLI)

This repo contains `.github/workflows/trigger-remote-workflow.yml` — a manual workflow that uses the GitHub CLI to trigger a workflow in a different repository.

Requirements
- **Secret:** `GH_CLI_TOKEN` (Personal Access Token)
  - Scopes: `repo` plus `workflow` permissions (PAT must be able to trigger workflows in the target repo). `GITHUB_TOKEN` of this repo cannot be used to trigger workflows in other repositories; a PAT is required.
  - Add it to this repo's Settings → Secrets → Actions as `GH_CLI_TOKEN`.

Usage
1. Go to Actions → "Trigger Remote Workflow (via GH CLI)" → Run workflow. Set inputs:
   - `target_repo`: `owner/repo` (e.g. `octocat/hello-world`)
   - `workflow_file`: workflow filename in the target repo (e.g. `ci.yml`)
   - `ref`: branch or tag to run the workflow on (e.g. `main`)

Notes
- The workflow uses `cli/gh-action@v2` and authenticates with `GH_CLI_TOKEN` via the action's `token` input, so no manual `gh auth login` step is required.
- The workflow runs `gh workflow run` against the target repo and shows recent runs. Ensure the token has access to the target repository (organization policies may require additional scopes or approvals).
