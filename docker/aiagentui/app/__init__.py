from flask import Flask
from dotenv import load_dotenv
from config import Config

def create_app():
    app = Flask(__name__)
    load_dotenv() 
    app.config.from_object(Config)

    with app.app_context():
        from .main import main as main_blueprint
        app.register_blueprint(main_blueprint)

        from .chat import chat as chat_blueprint
        app.register_blueprint(chat_blueprint, url_prefix='/chat')

        from .containers import containers as containers_blueprint
        app.register_blueprint(containers_blueprint, url_prefix='/containers')

        from .files import files as files_blueprint
        app.register_blueprint(files_blueprint, url_prefix='/files')

        from .backups import backups as backups_blueprint
        app.register_blueprint(backups_blueprint, url_prefix='/backups')

    return app
