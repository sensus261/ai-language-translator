"""Blueprint for basic text file translation routes."""

from flask import Blueprint, render_template_string, jsonify
from templates import BASIC_TRANSLATOR_TEMPLATE, RESULT_TEMPLATE
from file_processor import FileProcessor
from config import Config

basic_bp = Blueprint('basic', __name__)
config = Config()

# Initialize file processor
file_processor = FileProcessor(config.INPUT_FILE_PATH, config.OUTPUT_FILE_PATH)

@basic_bp.route('/basic-file-translator', methods=['GET'])
def basic_file_translator():
    """Basic file translator interface."""
    return render_template_string(BASIC_TRANSLATOR_TEMPLATE)

@basic_bp.route('/status-view', methods=['GET'])
def status_view():
    """View status with HTML interface."""
    try:
        status_data = file_processor.get_status()
        
        return render_template_string(RESULT_TEMPLATE, 
                                    title="Translation Status", 
                                    result_type="status", 
                                    result=status_data,
                                    back_link="/basic-file-translator",
                                    back_text="Text Translator")
        
    except Exception as e:
        error_data = {
            "error": "Failed to get status",
            "details": str(e)
        }
        return render_template_string(RESULT_TEMPLATE, 
                                    title="Status Error", 
                                    result_type="error", 
                                    result=error_data,
                                    back_link="/basic-file-translator",
                                    back_text="Text Translator")

@basic_bp.route('/trigger-processing-view', methods=['GET'])
def trigger_processing_view():
    """Process next line with HTML interface."""
    try:
        result = file_processor.process_next_line()
        
        if result["status"] == "completed":
            return render_template_string(RESULT_TEMPLATE, 
                                        title="Processing Complete", 
                                        result_type="completed", 
                                        result={"message": result["message"]},
                                        back_link="/basic-file-translator",
                                        back_text="Text Translator")
        
        elif result["status"] == "skipped":
            return render_template_string(RESULT_TEMPLATE, 
                                        title="Line Skipped", 
                                        result_type="skipped", 
                                        result={"message": result["message"]},
                                        back_link="/basic-file-translator",
                                        back_text="Text Translator",
                                        show_refresh=True)
        
        elif result["status"] == "error":
            error_data = {
                "error": result["error"],
                "details": result.get("input", "")
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="Translation Error", 
                                        result_type="error", 
                                        result=error_data,
                                        back_link="/basic-file-translator",
                                        back_text="Text Translator")
        
        elif result["status"] == "success":
            success_data = {
                "input": result["input"],
                "output": result["output"],
                "input_file_path": result["input_file_path"],
                "output_file_path": result["output_file_path"]
            }
            
            return render_template_string(RESULT_TEMPLATE, 
                                        title="Translation Success", 
                                        result_type="success", 
                                        result=success_data,
                                        back_link="/basic-file-translator",
                                        back_text="Text Translator",
                                        show_refresh=True)
        
    except Exception as e:
        error_data = {
            "error": "An error occurred while processing",
            "details": str(e)
        }
        return render_template_string(RESULT_TEMPLATE, 
                                    title="Processing Error", 
                                    result_type="error", 
                                    result=error_data,
                                    back_link="/basic-file-translator",
                                    back_text="Text Translator")

@basic_bp.route('/process-all-view', methods=['GET'])
def process_all_view():
    """Process all lines with HTML interface."""
    try:
        result = file_processor.process_all_lines()
        
        success_data = {
            "message": f"Processing completed! Processed {result['processed_count']} lines, skipped {result['skipped_count']} empty lines.",
            "processed_count": result["processed_count"],
            "skipped_count": result["skipped_count"],
            "errors": result["errors"],
            "input_file_path": result["input_file_path"],
            "output_file_path": result["output_file_path"]
        }
        
        return render_template_string(RESULT_TEMPLATE, 
                                    title="Batch Processing Complete", 
                                    result_type="success", 
                                    result=success_data,
                                    back_link="/basic-file-translator",
                                    back_text="Text Translator")
        
    except Exception as e:
        error_data = {
            "error": "An error occurred while processing all lines",
            "details": str(e)
        }
        return render_template_string(RESULT_TEMPLATE, 
                                    title="Batch Processing Error", 
                                    result_type="error", 
                                    result=error_data,
                                    back_link="/basic-file-translator",
                                    back_text="Text Translator")

# API routes (for JSON responses)
@basic_bp.route('/trigger-processing', methods=['GET'])
def trigger_processing():
    """Process the next line from the input file - translate and move to output file."""
    try:
        result = file_processor.process_next_line()
        
        if result["status"] == "success":
            return jsonify(result), 200
        elif result["status"] == "completed":
            return jsonify(result), 200
        elif result["status"] == "skipped":
            return jsonify(result), 200
        else:  # error
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({
            "error": "An error occurred while processing",
            "details": str(e)
        }), 500

@basic_bp.route('/status', methods=['GET'])
def get_status():
    """Get the current status of translation files."""
    try:
        status_data = file_processor.get_status()
        return jsonify(status_data), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to get status",
            "details": str(e)
        }), 500

@basic_bp.route('/process-all', methods=['POST'])
def process_all():
    """Process all remaining lines in the input file."""
    try:
        result = file_processor.process_all_lines()
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "error": "An error occurred while processing all lines",
            "details": str(e)
        }), 500
