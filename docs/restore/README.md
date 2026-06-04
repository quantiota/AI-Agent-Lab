# Restore a Backup — Host Setup

Install the host-side files (in this folder) onto the server.

First, in `recovery-microserver.sh`, set `TARGET_USER` to the host user that owns the checkout (e.g. `devbox`).

Then run on the server as root — `root@server:~#`

```bash
# scripts → /usr/local/bin (executable)
sudo cp recovery-microserver.sh recovery-agent.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/recovery-microserver.sh /usr/local/bin/recovery-agent.sh
```

```bash
# systemd service → start the agent
sudo cp recovery-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now recovery-agent
```

Verify:
```bash
sudo systemctl status recovery-agent     # active (running)
ls -la /run/recovery/                     # request.pipe exists
```
