"""
Main Flask application for the Resume Reviewer.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from app.core.config import Config
from app.api.routes import api_bp

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Enable CORS for all routes
    CORS(app, origins=Config.CORS_ORIGINS)
    
    # Create upload folder if it doesn't exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Add a simple root route
    @app.route('/')
    def index():
        return {
            'message': 'Resume Reviewer API',
            'version': '1.0.0',
            'status': 'running'
        }
    
    logger.info("Flask application created successfully")
    return app


# Create the application instance
app = create_app()


if __name__ == '__main__':
    logger.info("Starting Resume Reviewer API server")
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=Config.DEBUG
    )

