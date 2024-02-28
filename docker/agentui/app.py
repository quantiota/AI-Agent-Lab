from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def hello():
    api_key_exists = "Yes" if os.environ.get('OPENAI_API_KEY') else "No"
    # Pass the message as a variable to the template
    return render_template('index.html', api_key_exists=api_key_exists)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
