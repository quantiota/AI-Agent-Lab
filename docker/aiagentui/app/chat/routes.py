from flask import request, jsonify, current_app
import requests
import openai
from . import chat

@chat.route('', methods=['POST'])
def chat():
    openai_api_key = current_app.config['OPENAI_API_KEY']
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



