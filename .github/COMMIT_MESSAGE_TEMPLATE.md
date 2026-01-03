# NetworkBuster Commit Message Guidelines

Please use the Conventional Commits format for all commits. This helps with automation, changelogs, and clear history.

Format:

```
<type>(<scope>): <short summary>

<body>

<footer>
```

- type: feat, fix, docs, style, refactor, perf, test, chore, build, ci
- scope: optional, a component or file scope (e.g., api, ui, docs)
- short summary: imperative, max ~50 characters
- body: more detailed explanation, wrap at 72 characters
- footer: reference issues (e.g., Closes #123), BREAKING CHANGE notes

Examples:

- feat(api): add health-check endpoint
- fix(ui): correct overflow bug on dashboard
- docs: update installation instructions

To enable locally:

```bash
git config commit.template .gitmessage
```

Thank you for keeping commit history clean and useful!
