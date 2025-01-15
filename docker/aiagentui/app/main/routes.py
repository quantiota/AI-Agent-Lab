from flask import render_template, current_app
from . import main

@main.route('/')
def index():
    api_key_exists = "Yes" if current_app.config.get('OPENAI_API_KEY') else "No"
    return render_template('index.html', api_key_exists=api_key_exists, domain=current_app.config.get('DOMAIN', 'Domain not set'))


