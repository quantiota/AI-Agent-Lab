from flask import request, jsonify, current_app
import os
import subprocess
from . import backups

# List Available Backups Route

@backups.route('/api/list-backups', methods=['GET'])
def list_backups():
    backup_dir = "/backup/rsnapshot"
    backup_types = ["hourly", "daily", "weekly", "monthly"]
    backups = []

    # Iterate over each backup type to list available snapshots
    for backup_type in backup_types:
        type_dir = os.path.join(backup_dir, backup_type)

        try:
            with os.scandir(backup_dir) as entries:
                subdirs = [entry.name for entry in entries if entry.is_dir() and entry.name.startswith(backup_type)]
                if subdirs:
                    for snapshot in subdirs:
                        snapshot_path = os.path.join(type_dir, snapshot)
                        # Get the timestamp from the snapshot name (assuming format like "hourly.0", "daily.1", etc.)
                        try:
                            # Get the modification time of the backup directory
                            mod_time = os.path.getmtime(os.path.join(backup_dir, snapshot))
                            backups.append({
                                "type": backup_type,
                                "timestamp": snapshot,
                                "path": snapshot_path,
                                "mod_time": mod_time
                            })
                        except OSError:
                            continue
        except FileNotFoundError:
            continue
        except PermissionError:
            continue

    # Sort backups by modification time, most recent first
    sorted_backups = sorted(backups, key=lambda x: x["mod_time"], reverse=True)
    
    # Remove mod_time from the response
    for backup in sorted_backups:
        del backup["mod_time"]

    return jsonify({"backups": sorted_backups}), 200


# Restore a Backup Route



@backups.route('/api/restore-backup', methods=['POST'])
def restore_backup():
    try:
        data = request.get_json()
        selected_backup = data.get("selectedBackup")

        if not selected_backup:
            return jsonify({"message": "No backup selected."}), 400

        # Check if the selected backup exists
        backup_path = f"/backup/rsnapshot/{selected_backup}"
        if not os.path.exists(backup_path):
            return jsonify({"message": f"Selected backup '{selected_backup}' does not exist."}), 400

        app.logger.info(f"Starting restore process for backup: {selected_backup}")

        # Add execute permission to the recovery script
        
        # subprocess.run(["chmod", "+x", "/recovery-microserver.sh"], check=True)


        # Execute the restore script
        result = subprocess.run(
            ["sh", "/recovery-microserver.sh"], 
            check=True, 
            env={"SELECTED_BACKUP": selected_backup, **os.environ},
            capture_output=True,
            text=True
        )

        app.logger.info(f"Restore process completed. Output: {result.stdout}")

        return jsonify({"message": "Restore completed successfully!", "details": result.stdout}), 200

    except subprocess.CalledProcessError as e:
        error_output = e.stderr if e.stderr else str(e)
        app.logger.error(f"Subprocess error during restore: {error_output}")
        return jsonify({"message": f"Restore failed: {error_output}"}), 500

    except Exception as e:
        app.logger.error(f"Unexpected error during restore: {str(e)}")
        return jsonify({"message": f"An unexpected error occurred: {str(e)}"}), 500
