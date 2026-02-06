# Approving workflow runs from forks

This document summarizes recommended repository settings and the manual steps maintainers can take to approve workflow runs triggered by pull requests from forks.

## Recommended repository settings

1. Go to **Settings → Actions → General**.
2. Under **Approval for running fork pull request workflows from contributors**, select **Require approval for all external contributors** (or one of the stricter options depending on your risk profile).
3. Under **Workflow permissions**, choose the policy appropriate for your repository (e.g., **read and write** if you require workflows to be able to create or approve PRs; otherwise keep **read**).
4. Under **Allowing select actions and reusable workflows to run**, restrict third-party actions where possible.
5. Save changes.

> Rationale: Requiring maintainer approval for fork PR workflows reduces accidental or malicious consumption of runner resources and helps protect self-hosted infrastructure. Reviewers should pay close attention to changes in `.github/workflows/` before approving.

## How to approve an individual run

1. Open the Pull Request on GitHub.
2. Inspect the **Files changed** tab; ensure workflows in `.github/workflows/` look safe.
3. On the **Conversation** tab, click **Approve workflows to run** in the banner that appears for pending runs.
4. Alternatively: open the **Actions** tab → the specific run → click **Approve and run** (if available).

## Notes and best practices

- Workflows triggered by `pull_request_target` run with the context of the base branch and should be treated carefully; prefer `pull_request` where possible.
- For public forks, first-time contributors typically require approval by default; adjust policy if you want to change this behavior.
- Document the team members who are authorized to approve runs.
