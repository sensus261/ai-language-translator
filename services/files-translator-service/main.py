"""Main Flask application factory and entry point."""

from flask import Flask, render_template_string
from config import Config
from templates import HOME_TEMPLATE
from routes import basic_bp, xml_bp

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    config = Config()
    
    # Configure Flask
    app.config['ENV'] = config.FLASK_ENV
    app.config['DEBUG'] = config.FLASK_DEBUG
    
    # Print configuration
    config.print_config()
    
    # Register blueprints
    app.register_blueprint(basic_bp)
    app.register_blueprint(xml_bp)
    
    # Home route
    @app.route('/', methods=['GET'])
    def home():
        """Home page with links to all available routes."""
        return render_template_string(HOME_TEMPLATE)
    
    return app

if __name__ == '__main__':
    app = create_app()
    config = Config()
    
    # Run Flask with environment-specific settings
    app.run(host='0.0.0.0', port=5000, debug=config.FLASK_DEBUG)
