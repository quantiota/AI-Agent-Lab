from flask import Flask, render_template, request, abort, jsonify
import os
import json
import openai
import requests
import docker

# Load domain.ltd from environment variable
domain = os.environ.get('DOMAIN', 'Domain not set')


app = Flask(__name__)

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

# Define the valid container names
valid_containers = {
    'docker-vscode-1': 'VSCode Container',
    'docker-questdb-1': 'QuestDB Container',
    'docker-grafana-1': 'Grafana Container'
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
        #os.system(f'docker restart {container_name}')
        return f'{valid_containers[container_name]} ({container_name}) restarted successfully!', 200
    else:
        # If the container name is not valid, return a 404 error
        abort(404, description=f"Container {container_name} not found")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)










