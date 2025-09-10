"""Blueprint for XML translation routes."""

from flask import Blueprint, render_template_string, jsonify
from templates import XML_TRANSLATOR_TEMPLATE, RESULT_TEMPLATE
from xml_processor import XMLProcessor, get_batch_processing_status
from config import Config

xml_bp = Blueprint('xml', __name__)
config = Config()

# Initialize XML processor
xml_processor = XMLProcessor(config.XML_INPUT_FILE_PATH, config.XML_OUTPUT_FILE_PATH)

@xml_bp.route('/fallout4-xml-translator', methods=['GET'])
def fallout4_xml_translator():
    """Fallout 4 XML translator interface."""
    batch_status = get_batch_processing_status()
    return render_template_string(XML_TRANSLATOR_TEMPLATE, batch_processing_status=batch_status)

@xml_bp.route('/xml-status-view', methods=['GET'])
def xml_status_view():
    """View XML status with HTML interface."""
    try:
        status_data = xml_processor.get_status()
        
        return render_template_string(RESULT_TEMPLATE, 
                                    title="XML Translation Status", 
                                    result_type="status", 
                                    result=status_data,
                                    back_link="/fallout4-xml-translator",
                                    back_text="XML Translator",
                                    show_refresh_status=True,
                                    show_stop_batch=status_data["batch_processing_status"])
        
    except Exception as e:
        error_data = {
            "error": "Failed to get XML status",
            "details": str(e)
        }
        return render_template_string(RESULT_TEMPLATE, 
                                    title="XML Status Error", 
                                    result_type="error", 
                                    result=error_data,
                                    back_link="/fallout4-xml-translator",
                                    back_text="XML Translator")

@xml_bp.route('/xml-trigger-processing-view', methods=['GET'])
def xml_trigger_processing_view():
    """Process next XML entry with HTML interface."""
    try:
        result = xml_processor.process_next_entry()
        
        if result["status"] == "completed":
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Processing Complete", 
                                        result_type="completed", 
                                        result={"message": result["message"]},
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator",
                                        show_refresh=True)
        
        elif result["status"] == "skipped":
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Entry Skipped", 
                                        result_type="skipped", 
                                        result={"message": result["message"]},
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator",
                                        show_refresh=True)
        
        elif result["status"] == "error":
            error_data = {
                "error": result["error"],
                "details": result.get("details", result.get("input", ""))
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Processing Error", 
                                        result_type="error", 
                                        result=error_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
        elif result["status"] == "success":
            success_data = {
                "input": result["input"],
                "output": result["output"],
                "input_file_path": result["input_file_path"],
                "output_file_path": result["output_file_path"]
            }
            
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Translation Success", 
                                        result_type="success", 
                                        result=success_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator",
                                        show_refresh=True)
        
    except Exception as e:
        error_data = {
            "error": "An error occurred while processing XML",
            "details": str(e)
        }
        return render_template_string(RESULT_TEMPLATE, 
                                    title="XML Processing Error", 
                                    result_type="error", 
                                    result=error_data,
                                    back_link="/fallout4-xml-translator",
                                    back_text="XML Translator")

@xml_bp.route('/xml-process-all-view', methods=['GET'])
def xml_process_all_view():
    """Start processing all XML entries in background."""
    try:
        result = xml_processor.start_batch_processing()
        
        if result["status"] == "error":
            error_data = {
                "error": result["error"],
                "details": result.get("details", "")
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Processing Error", 
                                        result_type="error", 
                                        result=error_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
        elif result["status"] == "completed":
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Processing Complete", 
                                        result_type="completed", 
                                        result={"message": result["message"]},
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
        elif result["status"] == "success":
            success_data = {
                "message": result["message"],
                "entries_to_process": result["entries_to_process"]
            }
            
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Batch Processing Started", 
                                        result_type="success", 
                                        result=success_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
    except Exception as e:
        error_data = {
            "error": "An error occurred while starting XML batch processing",
            "details": str(e)
        }
        return render_template_string(RESULT_TEMPLATE, 
                                    title="XML Batch Processing Error", 
                                    result_type="error", 
                                    result=error_data,
                                    back_link="/fallout4-xml-translator",
                                    back_text="XML Translator")

@xml_bp.route('/xml-stop-batch-processing', methods=['GET'])
def xml_stop_batch_processing():
    """Stop the running XML batch processing."""
    try:
        result = xml_processor.stop_batch_processing()
        
        if result["status"] == "error":
            error_data = {
                "error": result["error"],
                "details": result.get("details", "")
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="No Processing to Stop", 
                                        result_type="error", 
                                        result=error_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
        elif result["status"] == "success":
            success_data = {
                "message": result["message"]
            }
            
            return render_template_string(RESULT_TEMPLATE, 
                                        title="Stop Request Sent", 
                                        result_type="success", 
                                        result=success_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
    except Exception as e:
        error_data = {
            "error": "An error occurred while stopping batch processing",
            "details": str(e)
        }
        return render_template_string(RESULT_TEMPLATE, 
                                    title="Stop Error", 
                                    result_type="error", 
                                    result=error_data,
                                    back_link="/fallout4-xml-translator",
                                    back_text="XML Translator")
