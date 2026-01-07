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
    app.register_blueprint(projects_bp, url_prefix='/api/v1')
    
    return app