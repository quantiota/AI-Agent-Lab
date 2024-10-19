from flask import Flask, render_template, request, abort, jsonify, redirect, url_for, abort, flash
import os
import json
import openai
import requests
import docker
from werkzeug.utils import secure_filename
import time


# Load domain.ltd from environment variable
domain = os.environ.get('DOMAIN', 'Domain not set')
secret_key = os.environ.get('SECRET_KEY', 'default_secret_key') 

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50*1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.csv', '.sql', '.pdf', '.txt']
app.config['UPLOAD_PATH'] = '/aiagentui/uploads'
app.secret_key = 'your_secret_key'

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
    api_key_exists = "Yes" if os.environ.get('OPENAI_API_KEY') else "No"
    return render_template('index.html', api_key_exists=api_key_exists, domain=domain)




@app.route('/chat', methods=['POST'])
def chat():
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        return jsonify({'error': 'OpenAI API key is not configured.'}), 500

    # Get the user's message from the request
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Please provide a message.'}), 400

    user_message = data['message']

    try:
        # Create a chat completion using the OpenAI REST API
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {openai_api_key}',
        }

        json_data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        }

        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=json_data,
            timeout=15  # Timeout after 15 seconds
        )

        if response.status_code != 200:
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            return jsonify({'error': error_message}), response.status_code

        assistant_message = response.json()['choices'][0]['message']['content']

        return jsonify({'response': assistant_message}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Service controle

@app.route('/restart/<container_name>', methods=['GET'])
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





@app.route('/restart/nginx', methods=['GET'])
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




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
