"""File processing utilities for basic text files."""

import os
from services import ai_service

class FileProcessor:
    """Handles basic text file processing operations."""
    
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
    
    def read_first_line(self):
        """Read the first line from the input file."""
        try:
            if not os.path.exists(self.input_path):
                print(f"[FILE-PROCESSOR] Input file not found: {self.input_path}")
                return None
            
            with open(self.input_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if lines:
                    return lines[0].strip()
            
            return None
        except Exception as e:
            print(f"[FILE-PROCESSOR] Error reading from file {self.input_path}: {str(e)}")
            return None

    def remove_first_line(self):
        """Remove the first line from the input file."""
        try:
            if not os.path.exists(self.input_path):
                return False
            
            with open(self.input_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            if lines:
                # Remove the first line and write back
                with open(self.input_path, 'w', encoding='utf-8') as file:
                    file.writelines(lines[1:])
                return True
            return False
        except Exception as e:
            print(f"[FILE-PROCESSOR] Error removing line from file {self.input_path}: {str(e)}")
            return False

    def append_to_output(self, text):
        """Append translated text to the output file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            with open(self.output_path, 'a', encoding='utf-8') as file:
                file.write(text + '\n')
            return True
        except Exception as e:
            print(f"[FILE-PROCESSOR] Error writing to file {self.output_path}: {str(e)}")
            return False
    
    def count_lines(self, file_path):
        """Count lines in a file."""
        try:
            if not os.path.exists(file_path):
                return 0
            
            with open(file_path, 'r', encoding='utf-8') as file:
                return len(file.readlines())
        except Exception as e:
            print(f"[FILE-PROCESSOR] Error counting lines in {file_path}: {str(e)}")
            return 0
    
    def get_status(self):
        """Get the current status of translation files."""
        input_exists = os.path.exists(self.input_path)
        output_exists = os.path.exists(self.output_path)
        
        lines_remaining = self.count_lines(self.input_path) if input_exists else 0
        lines_translated = self.count_lines(self.output_path) if output_exists else 0
        
        return {
            "input_file_path": self.input_path,
            "input_file_exists": input_exists,
            "lines_remaining": lines_remaining,
            "output_file_path": self.output_path,
            "output_file_exists": output_exists,
            "lines_translated": lines_translated
        }
    
    def process_next_line(self):
        """Process the next line from input file."""
        english_text = self.read_first_line()
        
        if english_text is None:
            return {"status": "completed", "message": "No more lines to process"}
        
        if not english_text:  # Empty line
            self.remove_first_line()
            return {"status": "skipped", "message": "Skipped empty line"}
        
        print(f"[FILE-PROCESSOR] Processing line: {english_text}")
        
        # Translate the text
        romanian_text = ai_service.translate_text(english_text)
        
        if romanian_text is None:
            return {"status": "error", "error": "Translation failed", "input": english_text}
        
        print(f"[FILE-PROCESSOR] Translation: {romanian_text}")
        
        # Append to output file
        if not self.append_to_output(romanian_text):
            return {"status": "error", "error": "Failed to write to output file"}
        
        # Remove the processed line from input file
        if not self.remove_first_line():
            return {"status": "error", "error": "Failed to remove processed line from input file"}
        
        return {
            "status": "success",
            "input": english_text,
            "output": romanian_text,
            "input_file_path": self.input_path,
            "output_file_path": self.output_path
        }
    
    def process_all_lines(self):
        """Process all remaining lines in the input file."""
        processed_count = 0
        skipped_count = 0
        errors = []
        
        while True:
            result = self.process_next_line()
            
            if result["status"] == "completed":
                break
            elif result["status"] == "skipped":
                skipped_count += 1
            elif result["status"] == "success":
                processed_count += 1
                print(f"[FILE-PROCESSOR] Successfully processed {processed_count} lines")
            elif result["status"] == "error":
                errors.append(result.get("error", "Unknown error"))
                if "Failed to remove processed line" in result.get("error", ""):
                    break  # Stop on critical error
        
        return {
            "status": "completed",
            "processed_count": processed_count,
            "skipped_count": skipped_count,
            "errors": errors,
            "input_file_path": self.input_path,
            "output_file_path": self.output_path
        }
