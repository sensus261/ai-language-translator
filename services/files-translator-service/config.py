import os

class Config:
    """Application configuration."""
    
    # Ollama service configuration
    OLLAMA_SERVICE_URL = os.getenv('OLLAMA_SERVICE_URL', 'http://host.docker.internal:11434')
    ENHANCE_PRODUCT_MODEL = os.getenv('ENHANCE_PRODUCT_MODEL', 'aya:8b-23')
    
    # Flask configuration
    FLASK_ENV = os.getenv('OLLAMA_API_SERVICE_ENV', 'development')
    FLASK_DEBUG = os.getenv('OLLAMA_API_SERVICE_DEBUG', 'true').lower() == 'true'
    
    # File paths configuration
    INPUT_FILE_PATH = os.getenv('INPUT_FILE_PATH', '/app/data/english_text.txt')
    OUTPUT_FILE_PATH = os.getenv('OUTPUT_FILE_PATH', '/app/data/romanian_text.txt')
    
    # XML file paths configuration
    XML_INPUT_FILE_PATH = os.getenv('XML_INPUT_FILE_PATH', '/app/original_fallout_files/Fallout4_en_fr.xml')
    XML_OUTPUT_FILE_PATH = os.getenv('XML_OUTPUT_FILE_PATH', '/app/original_fallout_files/Fallout4_en_ro.xml')
    
    def print_config(self):
        """Print configuration for debugging."""
        print(" ")
        print(f"[FILES-TRANSLATOR] Using OLLAMA_SERVICE_URL: {self.OLLAMA_SERVICE_URL}")
        print(f"[FILES-TRANSLATOR] Using ENHANCE_PRODUCT_MODEL: {self.ENHANCE_PRODUCT_MODEL}")
        print(f"[FILES-TRANSLATOR] Flask environment: {self.FLASK_ENV}")
        print(f"[FILES-TRANSLATOR] Flask debug mode: {self.FLASK_DEBUG}")
        print(f"[FILES-TRANSLATOR] Input file path: {self.INPUT_FILE_PATH}")
        print(f"[FILES-TRANSLATOR] Output file path: {self.OUTPUT_FILE_PATH}")
        print(f"[FILES-TRANSLATOR] XML input file path: {self.XML_INPUT_FILE_PATH}")
        print(f"[FILES-TRANSLATOR] XML output file path: {self.XML_OUTPUT_FILE_PATH}")
        print(" ")
