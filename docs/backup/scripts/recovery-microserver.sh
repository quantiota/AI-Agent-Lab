#!/bin/bash

# Step 1: Remove old directories
rm -rf /home /opt

# Step 2: Restore from the latest hourly backup
cp -pr /backup/rsnapshot/hourly.0/localhost/home /
cp -pr /backup/rsnapshot/hourly.0/localhost/opt /

# Step 3: Get the invoking user's home directory
USER_HOME=$(eval echo "~$SUDO_USER")

# Step 4: Change directory to where docker-compose.yml is located
cd "$USER_HOME/AI-Agent-Lab/docker" || exit

# Step 5: Rebuild and start Docker containers
docker compose up --build -d

# Step 6: Update the file database (if needed)
updatedb
