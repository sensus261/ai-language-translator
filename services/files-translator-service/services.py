"""Services for AI client and translation."""

import ollama
from config import Config

class AIService:
    """Service for managing AI client and translations."""
    
    def __init__(self):
        self.client = None
        self.config = Config()
        
    def get_client(self):
        """Get or initialize the AI client."""
        if self.client is None:
            try:
                self.client = ollama.Client(host=self.config.OLLAMA_SERVICE_URL)
                self.client.pull(self.config.ENHANCE_PRODUCT_MODEL)
                print(f"[AI-SERVICE] Connected to Ollama at {self.config.OLLAMA_SERVICE_URL}")
            except Exception as e:
                print(f"[AI-SERVICE] Error while connecting to Ollama service: {str(e)}")
                raise e
        return self.client
    
    def translate_text(self, text):
        """Translate English text to Romanian using AI."""
        prompt = f'''Translate the following English text to Romanian. Return only the Romanian translation, no additional text or formatting:

{text}'''
        
        try:
            client = self.get_client()
            
            response = client.generate(
                model=self.config.ENHANCE_PRODUCT_MODEL, 
                prompt=prompt,
            )
            
            # Clean up the response
            translated_text = response['response'].strip()
            translated_text = translated_text.replace("```", "").replace("json", "")
            
            return translated_text
        except Exception as e:
            print(f"[AI-SERVICE] Error during translation: {str(e)}")
            return None

# Global AI service instance
ai_service = AIService()
