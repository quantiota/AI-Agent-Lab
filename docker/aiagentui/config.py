import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    UPLOAD_EXTENSIONS = ['.csv', '.sql', '.pdf', '.txt']
    UPLOAD_PATH = '/aiagentui/uploads'
    DOMAIN = os.environ.get('DOMAIN', 'Domain not set')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
