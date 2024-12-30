from flask import Flask
from dotenv import load_dotenv
import logging
from datetime import datetime
import os
from routes.chat_routes import chat_bp
from routes.health_routes import health_bp
from routes.admin_routes import admin_bp
from routes.queue_routes import queue_bp
from middlewares.auth import auth_middleware
from utils.logging_config import setup_logging
from utils.config_manager import config_manager

load_dotenv()

def create_app() -> Flask:
    """
    Creates and configures the Flask application.
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    setup_logging(log_dir)

    app.before_request(auth_middleware)

    app.register_blueprint(chat_bp,   url_prefix='/api/chat')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(admin_bp,  url_prefix='/api/admin')
    app.register_blueprint(queue_bp,  url_prefix='/api/queue')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(
        host=config_manager.get('HOST'),
        port=config_manager.get('PORT'),
        debug=config_manager.get_bool('DEBUG')
    )
