from flask import Flask, render_template, request, abort, jsonify, redirect, url_for, abort, flash, Response
from flask_wtf.csrf import CSRFProtect
import os
import json
import requests
import anthropic
import docker
from werkzeug.utils import secure_filename
import time
import subprocess
import re


# Load domain.ltd from environment variable
domain = os.environ.get('DOMAIN', 'Domain not set')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50*1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.csv', '.sql', '.pdf', '.txt']
app.config['UPLOAD_PATH'] = '/aiagentui/uploads'
app.config['UPLOAD_MAX_BYTES'] = 800 * 1024   # 800K — matches the upload UI
app.secret_key = os.environ.get('APP_SECRET_KEY', 'dev-only-change-me')
csrf = CSRFProtect(app)

# Claude API key: UI-set store file takes precedence, else the ANTHROPIC_API_KEY env (.env).
CLAUDE_KEY_FILE = os.environ.get('CLAUDE_KEY_FILE', os.path.join(app.instance_path, 'claude_api_key'))

# Conversations are persisted server-side here (the instance volume survives rebuild +
# restore), so chats outlast a browser wipe and follow the user across browsers/devices.
CHATS_FILE = os.environ.get('CHATS_FILE', os.path.join(app.instance_path, 'chats.json'))

def get_claude_key():
    try:
        with open(CLAUDE_KEY_FILE) as f:
            key = f.read().strip()
            if key:
                return key
    except OSError:
        pass
    return os.environ.get('ANTHROPIC_API_KEY')

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

# Define the valid container names
valid_containers = {
    'docker-vscode-1': 'VSCode Container',
    'docker-questdb-1': 'QuestDB Container',
    'docker-grafana-1': 'Grafana Container',
   # 'docker-nginx-1': 'Nginx Container'
}

@app.route('/')
def index():
    api_key_exists = "Yes" if get_claude_key() else "No"
    return render_template('index.html', api_key_exists=api_key_exists, domain=domain)


@app.route('/save-key', methods=['POST'])
def save_key():
    data = request.get_json(silent=True) or {}
    key = (data.get('apiKey') or '').strip()
    if not key:
        return jsonify({'message': 'Please enter an API key.'}), 400
    try:
        os.makedirs(os.path.dirname(CLAUDE_KEY_FILE), exist_ok=True)
        with open(CLAUDE_KEY_FILE, 'w') as f:
            f.write(key)
        os.chmod(CLAUDE_KEY_FILE, 0o600)
    except OSError as e:
        app.logger.error(f"Could not save Claude key: {e}")
        return jsonify({'message': 'Could not save the key (storage not writable).'}), 500
    return jsonify({'message': 'API key saved.'}), 200




@app.route('/chats', methods=['GET'])
def get_chats():
    """Return the saved conversations (server-side store)."""
    try:
        with open(CHATS_FILE) as f:
            return jsonify(json.load(f)), 200
    except FileNotFoundError:
        return jsonify([]), 200
    except (OSError, ValueError):
        # Unreadable / corrupt store: start clean rather than 500 the UI.
        return jsonify([]), 200


@app.route('/chats', methods=['POST'])
def save_chats():
    """Persist the full conversations array sent by the frontend."""
    data = request.get_json(silent=True)
    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list of chats.'}), 400
    try:
        os.makedirs(os.path.dirname(CHATS_FILE), exist_ok=True)
        with open(CHATS_FILE, 'w') as f:
            json.dump(data, f)
    except OSError as e:
        app.logger.error(f"Could not save chats: {e}")
        return jsonify({'error': 'Could not save (storage not writable).'}), 500
    return jsonify({'ok': True}), 200


@app.route('/chat', methods=['POST'])
def chat():
    anthropic_api_key = get_claude_key()
    if not anthropic_api_key:
        return jsonify({'error': 'Anthropic API key is not configured.'}), 500

    # Get the conversation from the request.
    # Accept either a full conversation ("messages") or a single "message".
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Please provide a message.'}), 400

    messages = data.get('messages')
    if not messages:
        user_message = data.get('message')
        if not user_message:
            return jsonify({'error': 'Please provide a message.'}), 400
        messages = [{"role": "user", "content": user_message}]

    # Pick the model from the request, restricted to the allowed set.
    # Default to Haiku 4.5 for testing.
    allowed_models = {
        "claude-sonnet-4-6",
        "claude-opus-4-8",
        "claude-haiku-4-5-20251001",
    }
    default_model = "claude-haiku-4-5-20251001"
    model = data.get('model')
    if model not in allowed_models:
        model = default_model

    client = anthropic.Anthropic(api_key=anthropic_api_key)

    system_prompt = (
        "You are the assistant built into the AI Agent Lab dashboard — a single-user "
        "research environment running QuestDB (time-series database), Grafana "
        "(dashboards), VSCode/code-server (which includes Claude Code for agentic "
        "coding), and nginx, all in Docker.\n\n"
        "Your role is read-only: you explain, analyze, and answer questions about the "
        "lab, its data, code, and research. You do not run commands, edit files, or "
        "change the system — that is done by the user or by Claude Code inside "
        "code-server. When a task needs execution, give the exact command or steps to "
        "run there instead of saying you cannot access the system.\n\n"
        "When the user attaches a file, its full contents are included inline in their "
        "message; treat that text as the attached file and work with it directly.\n\n"
        "Be concise and technical. No filler, no emoji. Use markdown for structure and "
        "code blocks for commands and code.\n\n"
        "The chat renders markdown only, not LaTeX. Write math as plain text using "
        "unicode symbols (e.g. H(X) = -Σ p(i)·log p(i)), not LaTeX delimiters like "
        "$$…$$ or \\frac — they would show as raw text."
    )

    # Adaptive thinking is supported on Opus/Sonnet (not Haiku). When it's on, give the
    # answer more headroom since thinking tokens count toward max_tokens.
    thinking_models = {"claude-opus-4-8", "claude-sonnet-4-6"}
    stream_kwargs = {
        "model": model,
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": messages,
    }
    if model in thinking_models:
        stream_kwargs["thinking"] = {"type": "adaptive"}
        stream_kwargs["max_tokens"] = 4096

    # Stream the reply as plain-text chunks (the frontend reads response.body and
    # renders markdown as it arrives). text_stream yields only the visible answer —
    # any thinking blocks are excluded. One user per instance, so holding a worker
    # for the duration of the stream is fine.
    def generate():
        try:
            with client.messages.stream(**stream_kwargs) as stream:
                for text in stream.text_stream:
                    yield text
        except anthropic.APIStatusError as e:
            yield f"\n\n[error: {e}]"
        except Exception as e:
            yield f"\n\n[error: {e}]"

    return Response(generate(), mimetype='text/plain; charset=utf-8')



# Service controle

@app.route('/restart/<container_name>', methods=['POST'])
def restart_container(container_name):
    # Check if the container name is valid
    if container_name in valid_containers:
        # Restart the specified container
        container = client.containers.get(container_name)
        container.restart()
        # Flash a success message to the user
        flash(f'{valid_containers[container_name]} ({container_name}) is restarting. Please wait a few moments.', 'info')

        # Redirect back to the index page (or dashboard)
        return redirect(url_for('index'))
    else:
        # If the container name is not valid, return a 404 error
        abort(404, description=f"Container {container_name} not found")





@app.route('/restart/nginx', methods=['POST'])
def restart_nginx():
    # Restart the Nginx container
    container = client.containers.get('docker-nginx-1')
    container.restart()

    # Return a simple response since the user doesn't need to see it
    return 'Nginx restart initiated', 200



# Uploading File

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:

            abort(400, description=f"Invalid file extension: {file_ext}. Allowed extensions are {', '.join(app.config['UPLOAD_EXTENSIONS'])}.")

        # Enforce the 800K size limit server-side (matches the upload UI).
        uploaded_file.seek(0, os.SEEK_END)
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)
        if file_size > app.config['UPLOAD_MAX_BYTES']:
            abort(400, description="File too large. Max size of 800K.")

        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        flash('File uploaded successfully!', 'success')  # Flash success message
    return redirect(url_for('index'))


#  Delete Files

@app.route('/delete-file', methods=['POST'])
def delete_file():
    # Get the filename from the form data
    filename = request.form.get('filename')
    
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400

    # Create the full path to the file
    file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
    
    try:
        # Check if the file exists and delete it
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'success': f'File {filename} deleted successfully'}), 200
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# List the Files in the Server

@app.route('/list-files', methods=['GET'])
def list_files():
    try:
        files = os.listdir(app.config['UPLOAD_PATH'])
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500     





# List Available Backups Route

@app.route('/api/list-backups', methods=['GET'])
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



# Only allow snapshot names like hourly.0 / daily.1 — also blocks path traversal.
SAFE_BACKUP = re.compile(r'^(hourly|daily|weekly|monthly)\.\d+$')

@app.route('/api/restore-backup', methods=['POST'])
def restore_backup():
    data = request.get_json(silent=True) or {}
    selected = data.get("selectedBackup", "")

    if not SAFE_BACKUP.match(selected):
        return jsonify({"message": "Invalid backup name."}), 400
    if not os.path.isdir(f"/backup/rsnapshot/{selected}"):
        return jsonify({"message": f"Backup '{selected}' not found."}), 404

    # Hand the restore off to the host-side recovery agent. The container never
    # runs the destructive restore itself — it can only push a validated name
    # into the pipe. Fire-and-forget: the restore rebuilds this very container,
    # so a synchronous response could not reliably return anyway.
    try:
        with open("/run/recovery/request.pipe", "w") as pipe:
            pipe.write(selected + "\n")
    except OSError as e:
        app.logger.error(f"Could not queue restore: {e}")
        return jsonify({"message": "Restore agent unavailable."}), 503

    app.logger.info(f"Restore queued for backup: {selected}")
    return jsonify({"message": "Restore queued. Please wait ~3 minutes for the stack to rebuild, then reload the page."}), 202






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)