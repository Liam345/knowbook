from flask import Flask
from flask_cors import CORS

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Enable CORS for frontend communication
    CORS(app, origins=['http://localhost:5173'])
    
    # Register blueprints
    from app.api.projects import bp as projects_bp
    from app.api.settings import settings_bp
    from app.api.sources import sources_bp
    from app.api.chats import chats_bp
    from app.api.messages import messages_bp
    from app.api.transcription import transcription_bp
    from app.api.studio import studio_bp
    app.register_blueprint(projects_bp, url_prefix='/api/v1')
    app.register_blueprint(settings_bp)
    app.register_blueprint(sources_bp)
    app.register_blueprint(chats_bp, url_prefix='/api/v1')
    app.register_blueprint(messages_bp, url_prefix='/api/v1')
    app.register_blueprint(transcription_bp, url_prefix='/api/v1')
    app.register_blueprint(studio_bp, url_prefix='/api/v1')
    
    return app