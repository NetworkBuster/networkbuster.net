# Multi-stage Dockerfile for a simple Python CLI
# Assumptions:
# - Your CLI entrypoint is a script at /app/cli.py (update ENTRYPOINT as needed)
# - Dependencies are listed in requirements.txt (optional)
# - Image will be tagged and pushed to the registry you provide

########################################
# Build stage
########################################
FROM python:3.12-slim AS build
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Install build/runtime dependencies (no-op if no requirements.txt exists)
COPY requirements.txt /app/requirements.txt
RUN set -eux; \
    pip install --upgrade pip setuptools wheel || true; \
    if [ -s /app/requirements.txt ]; then pip install --no-cache-dir -r /app/requirements.txt; fi

# Copy project files
COPY . /app

########################################
# Final runtime image
########################################
FROM python:3.12-slim
LABEL maintainer="preciseliens@gmail.com"
WORKDIR /app

# Copy installed packages from build stage (best-effort)
COPY --from=build /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=build /app /app

# Ensure the CLI script is executable; default entrypoint runs /app/cli.py
# If your CLI is a package, change ENTRYPOINT accordingly (e.g., ["python", "-m", "mycli"])
ENTRYPOINT ["python", "/app/cli.py"]

# Default command prints help — override by passing args to the container
CMD ["--help"]
