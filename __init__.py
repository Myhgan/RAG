from flask import Flask
from flask_cors import CORS
import os

def create_app():
    main = Flask(__name__)
    if os.environ.get('FLASK_ENV') == 'development':
        CORS(main)
    from src.controllers.rag_controller import api_blueprint
    main.register_blueprint(api_blueprint)
    return main