# Use the specified base image
FROM codercom/code-server:4.113.0

# Switch to root user for permissions
USER root

# Update system and install Python
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    curl \
    tmux \
    poppler-utils \
    pandoc \
    texlive \
    texlive-latex-extra \
    imagemagick \
    libimage-exiftool-perl \
    librsvg2-bin \
    && rm -rf /var/lib/apt/lists/*

# ---- Python virtual environment (PEP 668 compliant) ----
RUN python3 -m venv /opt/venv

# Make venv the default Python
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip inside venv
RUN pip install --upgrade pip

# Copy requirements and install them
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt



# Create and set permissions for Claude directories
RUN mkdir -p /home/coder/.claude /home/coder/.config/claude-code && \
    chown -R coder:coder /home/coder/.claude /home/coder/.config && \
    chmod -R u+rwX /home/coder/.claude /home/coder/.config

# Auto-start Claude in a tmux session at container boot via code-server's ENTRYPOINTD
# hook (=/entrypoint.d, runs as coder before code-server) so the email IDLE listener +
# heartbeat can send-keys into the LIVE agent, and the session survives disconnects.
COPY entrypoint.d/ /entrypoint.d/
RUN chmod -R a+rx /entrypoint.d

# Keep-alive wrapper the boot hook launches: runs claude in a respawn loop so the
# tmux session survives claude exiting (crash/exit) and stays attachable.
COPY claude-session.sh /usr/local/bin/claude-session
RUN chmod a+rx /usr/local/bin/claude-session

# Switch to coder user
USER coder

# jh-exec reads ~/.env — point it at the shared jh-config volume (mounted at /home/coder/jh
# at runtime, written by the aiagentui "JupyterHub API Key" box). Dangling until the volume mounts.
RUN ln -sf /home/coder/jh/.env /home/coder/.env

# Install Claude Code via native installer
RUN curl -fsSL https://claude.ai/install.sh | bash

# Auto-attach interactive terminals to the live `claude` tmux session (created by the
# ENTRYPOINTD boot hook) so opening a terminal drops you straight into the live agent.
# Guarded to interactive shells ($- contains 'i') so it NEVER blocks tool/non-tty shells.
RUN printf '%s\n' \
    '' \
    '# --- auto-attach to the live `claude` agent tmux session (interactive only) ---' \
    'case $- in' \
    '  *i*)' \
    '    if [ -z "$TMUX" ] && command -v tmux >/dev/null 2>&1; then' \
    '      tmux attach -t claude 2>/dev/null' \
    '    fi' \
    '    ;;' \
    'esac' \
    >> /home/coder/.bashrc


# Install VS Code extensions

RUN code-server --install-extension ms-toolsai.jupyter@2025.9.1 \
    		--install-extension ms-toolsai.vscode-jupyter-powertoys \
    		--install-extension ms-python.python