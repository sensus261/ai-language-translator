"""Main Flask application using modular structure."""

from flask import Flask, render_template_string
import os
import sys
from datetime import datetime

# Import your modular components
from config import Config
from services import ai_service
from templates import HOME_TEMPLATE
from routes.basic_routes import basic_bp
from routes.xml_routes import xml_bp

# Setup logging to file while keeping console output
class TeeOutput:
    def __init__(self, *files):
        self.files = files
    
    def write(self, obj):
        # Add timestamp to each line if it's not just whitespace
        if obj.strip():
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            obj = f"[{timestamp}] {obj}"
        
        for f in self.files:
            f.write(obj)
            f.flush()
    
    def flush(self):
        for f in self.files:
            f.flush()

# Create logs directory if it doesn't exist
log_dir = '/app/logs'
os.makedirs(log_dir, exist_ok=True)

# Open log file with timestamp
log_filename = f"{log_dir}/files-translator-{datetime.now().strftime('%Y%m%d')}.log"
log_file = open(log_filename, 'a', encoding='utf-8')

# Redirect stdout to both console and log file
original_stdout = sys.stdout
sys.stdout = TeeOutput(original_stdout, log_file)

# Log startup message
print(f"[FILES-TRANSLATOR] Logging started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"[FILES-TRANSLATOR] Log file: {log_filename}")

# Initialize Flask app
app = Flask(__name__)

# Initialize configuration
config = Config()

# Configure Flask
app.config['ENV'] = config.FLASK_ENV
app.config['DEBUG'] = config.FLASK_DEBUG

# Print configuration
config.print_config()

# Initialize AI service
try:
    ai_service.get_client()
    print("[FILES-TRANSLATOR] AI service initialized successfully")
except Exception as e:
    print(f"[FILES-TRANSLATOR] Failed to initialize AI service: {str(e)}")
    sys.exit(1)

# Register blueprints
app.register_blueprint(basic_bp)
app.register_blueprint(xml_bp)

@app.route('/')
def home():
    """Home page showing available translators."""
    return render_template_string(HOME_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == '__main__':
    print("[FILES-TRANSLATOR] Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=config.FLASK_DEBUG)
