# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory to /aiagentui
WORKDIR /aiagentui

# Install dependencies
COPY requirements.txt /aiagentui
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

# Copy the application code
COPY . /aiagentui

# Set the default entrypoint and command
ENTRYPOINT ["python3"]
CMD ["run.py"]

# Stage 2: Development environment
FROM builder as dev-envs

RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF
# install Docker tools (cli, buildx, compose)
#COPY --from=gloursdocker/docker / /
