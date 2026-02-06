# Actions approval policy (proposed)

Proposed default policy for GitHub Actions approval on pull requests from forks:

- **Approval requirement**: Require approval for all external contributors.
- **Workflow permissions**: Keep `GITHUB_TOKEN` minimal by default (read-only for contents/packages), grant write only to workflows that need it and explicitly pin those workflows.
- **Allowed actions**: Allow owner + selected Marketplace/verified actions; block untrusted third-party actions.

This file documents the recommended changes and provides the maintainers with an explicit policy to adopt from the Settings > Actions UI.
