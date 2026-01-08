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
    app.register_blueprint(projects_bp, url_prefix='/api/v1')
    app.register_blueprint(settings_bp)
    app.register_blueprint(sources_bp)
    
    return app