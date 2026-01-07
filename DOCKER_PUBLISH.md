# Docker image build & publish (networkbuster.org)

This folder contains a basic Dockerfile and helper scripts to build and publish a Python-based CLI image to `networkbuster.org`.

Files added:

- `Dockerfile` — multi-stage image for a Python CLI (expects `/app/cli.py` by default)
- `scripts/build-cli.sh` — Bash helper to build and optionally push
- `scripts/build-cli.ps1` — PowerShell helper to build and optionally push
- `.github/workflows/publish.yml` — GitHub Actions workflow to build & push on tag or manual dispatch
- `.dockerignore` — common ignores

How to use

Local build (no push):

```bash
REGISTRY=networkbuster.org IMAGE_NAME=networkbuster-optimizations TAG=v7.5.0 ./scripts/build-cli.sh
```

Local build & push (requires Docker Desktop running and logged in):

```bash
REGISTRY=networkbuster.org IMAGE_NAME=networkbuster-optimizations TAG=v7.5.0 ./scripts/build-cli.sh --push
# or, in PowerShell
./scripts/build-cli.ps1 -Registry "networkbuster.org" -Image "networkbuster-optimizations" -Tag "v7.5.0" -Push
```

CI (GitHub Actions)

1. Go to your repository Settings → Secrets and variables → Actions → New repository secret.
2. Add these secrets:
   - `DOCKER_REGISTRY` — e.g., `networkbuster.org`
   - `DOCKER_USERNAME` — registry username
   - `DOCKER_PASSWORD` — registry password or token
   - `IMAGE_NAME` — e.g., `networkbuster-optimizations`
3. Trigger the workflow via a push to `main` with a `vX.Y.Z` tag or run it manually via "Run workflow".

Notes / Next steps

- Update `ENTRYPOINT` in the `Dockerfile` if your CLI has a different entrypoint (package/console script).
- If your CLI is not Python, replace the `Dockerfile` base images and install steps accordingly — tell me the language and I can swap it.
- I can run a local build & push for you when your Docker Desktop is running and you provide credentials (or I can prompt you interactively).
