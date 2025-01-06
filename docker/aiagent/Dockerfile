# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

# Switch to root user for permissions


WORKDIR /aiagent

COPY requirements.txt /aiagent
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /aiagent

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]


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