# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

# Set working directory for the AI Agent UI application
WORKDIR /aiagentui

# Copy dependencies and install with caching
COPY requirements.txt /aiagentui
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /aiagentui

# Set the default entry point and command
ENTRYPOINT ["python3"]
CMD ["app.py"]

# Development environment stage
FROM builder AS dev-envs

# Install development tools
RUN apk add --no-cache git

# Create a non-root user for development
RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF

# Optionally, add Docker CLI tools
# COPY --from=gloursdocker/docker / /















