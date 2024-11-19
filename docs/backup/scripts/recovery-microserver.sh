#!/bin/bash

# Step 1: Remove old directories
rm -rf /home /opt

# Step 2: Restore from the latest hourly backup
cp -pr /backup/rsnapshot/hourly.1/localhost/home /
cp -pr /backup/rsnapshot/hourly.1/localhost/opt /
