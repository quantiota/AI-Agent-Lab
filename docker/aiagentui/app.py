from flask import Flask, render_template, abort
import os


domain = os.environ.get('DOMAIN', 'Domain not set')

# Print the domain to the console to verify it's loaded
# print(f"DOMAIN environment variable: {domain}")


app = Flask(__name__)

# Define the valid container names
valid_containers = {
    'docker-vscode-1': 'VSCode Container',
    'docker-questdb-1': 'QuestDB Container',
    'docker-grafana-1': 'Grafana Container'
}

@app.route('/')
def hello():
    api_key_exists = "Yes" if os.environ.get('OPENAI_API_KEY') else "No"
    return render_template('index.html', api_key_exists=api_key_exists, domain=domain)

@app.route('/restart/<container_name>', methods=['GET'])
def restart_container(container_name):
    # Check if the container name is valid
    if container_name in valid_containers:
        # Restart the specified container
        os.system(f'docker restart {container_name}')
        return f'{valid_containers[container_name]} ({container_name}) restarted successfully!', 200
    else:
        # If the container name is not valid, return a 404 error
        abort(404, description=f"Container {container_name} not found")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


