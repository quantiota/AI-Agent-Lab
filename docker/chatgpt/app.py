# app.py

from flask import Flask, request
import openai

openai.api_key = 'your-openai-api-key'

app = Flask(__name__)

@app.route('/', methods=['POST'])
def home():
    message = request.form['message']
    response = openai.ChatCompletion.create(
      model="gpt-4.0-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message['content']

