from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import ollama
import os

app = Flask(__name__)

ollama_service_url = os.getenv('OLLAMA_SERVICE_URL', 'http://host.docker.internal:11434')
enhance_product_model = os.getenv('ENHANCE_PRODUCT_MODEL', 'aya:8b-23')
flask_env = os.getenv('OLLAMA_API_SERVICE_ENV', 'development')
flask_debug = os.getenv('OLLAMA_API_SERVICE_DEBUG', 'true').lower() == 'true'

# File paths configuration
input_file_path = os.getenv('INPUT_FILE_PATH', '/app/data/english_text.txt')
output_file_path = os.getenv('OUTPUT_FILE_PATH', '/app/data/romanian_text.txt')

app.config['ENV'] = flask_env
app.config['DEBUG'] = flask_debug

print(" ")
print(f"[FILES-TRANSLATOR] Using OLLAMA_SERVICE_URL: {ollama_service_url}")
print(f"[FILES-TRANSLATOR] Using ENHANCE_PRODUCT_MODEL: {enhance_product_model}")
print(f"[FILES-TRANSLATOR] Flask environment: {flask_env}")
print(f"[FILES-TRANSLATOR] Flask debug mode: {flask_debug}")
print(f"[FILES-TRANSLATOR] Input file path: {input_file_path}")
print(f"[FILES-TRANSLATOR] Output file path: {output_file_path}")
print(" ")

enhance_product_client = None

def get_ai_client():
    global enhance_product_client
    if enhance_product_client is None:
        try:
            enhance_product_client = ollama.Client(host=ollama_service_url)
            enhance_product_client.pull(enhance_product_model)
        except Exception as e:
            print(f"[FILES-TRANSLATOR] Error while connecting to Ollama service: {str(e)}")
            print(f"[FILES-TRANSLATOR] OLLAMA_SERVICE_URL: {ollama_service_url}")
            exit(1)
    return enhance_product_client


get_ai_client()

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Files Translator Service</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .route-card { background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #007bff; }
        .route-card h3 { margin-top: 0; color: #007bff; }
        .route-card p { color: #666; margin-bottom: 15px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px; }
        .btn:hover { background: #0056b3; }
        .btn-success { background: #28a745; }
        .btn-success:hover { background: #1e7e34; }
        .btn-warning { background: #ffc107; color: #212529; }
        .btn-warning:hover { background: #e0a800; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Files Translator Service</h1>
        
        <div class="route-card">
            <h3>📊 Check Status</h3>
            <p>View the current status of translation files, including lines remaining and translated.</p>
            <a href="/status-view" class="btn">View Status</a>
        </div>
        
        <div class="route-card">
            <h3>⚡ Process Next Line</h3>
            <p>Translate the next line from the input file and move it to the output file.</p>
            <a href="/trigger-processing-view" class="btn btn-success">Process Next</a>
        </div>
        
        <div class="route-card">
            <h3>🚀 Process All Lines</h3>
            <p>Translate all remaining lines in the input file. This may take some time.</p>
            <a href="/process-all-view" class="btn btn-warning">Process All</a>
        </div>
    </div>
</body>
</html>
'''

RESULT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Files Translator Service - Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .result-box { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .success { border-left: 4px solid #28a745; }
        .error { border-left: 4px solid #dc3545; }
        .warning { border-left: 4px solid #ffc107; }
        .info { border-left: 4px solid #17a2b8; }
        .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }
        .btn:hover { background: #0056b3; }
        pre { background: #f1f1f1; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .status-item { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }
        .status-number { font-size: 24px; font-weight: bold; color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        
        {% if result_type == 'success' %}
            <div class="result-box success">
                <h3>✅ Success!</h3>
                {% if result.input %}
                    <p><strong>Input:</strong> {{ result.input }}</p>
                {% endif %}
                {% if result.output %}
                    <p><strong>Translation:</strong> {{ result.output }}</p>
                {% endif %}
                {% if result.processed_count is defined %}
                    <p><strong>Lines processed:</strong> {{ result.processed_count }}</p>
                {% endif %}
                {% if result.skipped_count is defined %}
                    <p><strong>Lines skipped:</strong> {{ result.skipped_count }}</p>
                {% endif %}
            </div>
        {% elif result_type == 'error' %}
            <div class="result-box error">
                <h3>❌ Error</h3>
                <p>{{ result.error }}</p>
                {% if result.details %}
                    <p><strong>Details:</strong> {{ result.details }}</p>
                {% endif %}
            </div>
        {% elif result_type == 'skipped' %}
            <div class="result-box warning">
                <h3>⚠️ Skipped</h3>
                <p>{{ result.message }}</p>
            </div>
        {% elif result_type == 'completed' %}
            <div class="result-box info">
                <h3>✅ All Processing Complete</h3>
                <p>{{ result.message }}</p>
            </div>
        {% elif result_type == 'status' %}
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-number">{{ result.lines_remaining }}</div>
                    <div>Lines Remaining</div>
                </div>
                <div class="status-item">
                    <div class="status-number">{{ result.lines_translated }}</div>
                    <div>Lines Translated</div>
                </div>
            </div>
            <div class="result-box info">
                <p><strong>Input File:</strong> {{ result.input_file_path }} 
                   {% if result.input_file_exists %}✅{% else %}❌{% endif %}</p>
                <p><strong>Output File:</strong> {{ result.output_file_path }} 
                   {% if result.output_file_exists %}✅{% else %}❌{% endif %}</p>
            </div>
        {% endif %}
        
        {% if result.errors %}
            <div class="result-box error">
                <h3>⚠️ Errors encountered:</h3>
                <ul>
                    {% for error in result.errors %}
                        <li>{{ error }}</li>
                    {% endfor %}
                </ul>
            </div>
        {% endif %}
        
        <a href="/" class="btn">🏠 Back to Home</a>
    </div>
</body>
</html>
'''

def read_first_line_from_file(file_path):
    """Read the first line from the input file."""
    try:
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if lines:
                return lines[0].strip()
        return None
    except Exception as e:
        print(f"[FILES-TRANSLATOR] Error reading from file {file_path}: {str(e)}")
        return None

def remove_first_line_from_file(file_path):
    """Remove the first line from the input file."""
    try:
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        if lines:
            # Remove the first line and write back
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines[1:])
            return True
        return False
    except Exception as e:
        print(f"[FILES-TRANSLATOR] Error removing line from file {file_path}: {str(e)}")
        return False

def append_to_output_file(file_path, text):
    """Append translated text to the output file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(text + '\n')
        return True
    except Exception as e:
        print(f"[FILES-TRANSLATOR] Error writing to file {file_path}: {str(e)}")
        return False

def translate_text(text):
    """Translate English text to Romanian using AI."""
    prompt = f'''Translate the following English text to Romanian. Return only the Romanian translation, no additional text or formatting:

{text}'''
    
    try:
        client = get_ai_client()
        
        response = client.generate(
            model=enhance_product_model, 
            prompt=prompt,
        )
        
        # Clean up the response
        translated_text = response['response'].strip()
        translated_text = translated_text.replace("```", "").replace("json", "")
        
        return translated_text
    except Exception as e:
        print(f"[FILES-TRANSLATOR] Error during translation: {str(e)}")
        return None

@app.route('/', methods=['GET'])
def home():
    """Home page with links to all available routes."""
    return render_template_string(HOME_TEMPLATE)

@app.route('/status-view', methods=['GET'])
def status_view():
    """View status with HTML interface."""
    try:
        input_exists = os.path.exists(input_file_path)
        output_exists = os.path.exists(output_file_path)
        
        lines_remaining = 0
        if input_exists:
            with open(input_file_path, 'r', encoding='utf-8') as file:
                lines_remaining = len(file.readlines())
        
        lines_translated = 0
        if output_exists:
            with open(output_file_path, 'r', encoding='utf-8') as file:
                lines_translated = len(file.readlines())
        
        status_data = {
            "input_file_path": input_file_path,
            "input_file_exists": input_exists,
            "lines_remaining": lines_remaining,
            "output_file_path": output_file_path,
            "output_file_exists": output_exists,
            "lines_translated": lines_translated
        }
        
        return render_template_string(RESULT_TEMPLATE, 
                                    title="Translation Status", 
                                    result_type="status", 
                                    result=status_data)
        
    except Exception as e:
        error_data = {
            "error": "Failed to get status",
            "details": str(e)
        }
        return render_template_string(RESULT_TEMPLATE, 
                                    title="Status Error", 
                                    result_type="error", 
                                    result=error_data)

@app.route('/trigger-processing-view', methods=['GET'])
def trigger_processing_view():
    """Process next line with HTML interface."""
    try:
        # Check if input file exists
        if not os.path.exists(input_file_path):
            error_data = {
                "error": "Input file not found",
                "details": input_file_path
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="Processing Error", 
                                        result_type="error", 
                                        result=error_data)
        
        # Read the first line from input file
        english_text = read_first_line_from_file(input_file_path)
        
        if english_text is None:
            completed_data = {
                "message": "No more lines to process"
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="Processing Complete", 
                                        result_type="completed", 
                                        result=completed_data)
        
        if not english_text:  # Empty line
            # Remove the empty line and try next
            remove_first_line_from_file(input_file_path)
            skipped_data = {
                "message": "Skipped empty line"
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="Line Skipped", 
                                        result_type="skipped", 
                                        result=skipped_data)
        
        print(f"[FILES-TRANSLATOR] Processing line: {english_text}")
        
        # Translate the text
        romanian_text = translate_text(english_text)
        
        if romanian_text is None:
            error_data = {
                "error": "Translation failed",
                "details": f"Input: {english_text}"
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="Translation Error", 
                                        result_type="error", 
                                        result=error_data)
        
        print(f"[FILES-TRANSLATOR] Translation: {romanian_text}")
        
        # Append to output file
        if not append_to_output_file(output_file_path, romanian_text):
            error_data = {
                "error": "Failed to write to output file",
                "details": output_file_path
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="File Write Error", 
                                        result_type="error", 
                                        result=error_data)
        
        # Remove the processed line from input file
        if not remove_first_line_from_file(input_file_path):
            error_data = {
                "error": "Failed to remove processed line from input file"
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="File Update Error", 
                                        result_type="error", 
                                        result=error_data)
        
        success_data = {
            "input": english_text,
            "output": romanian_text,
            "input_file_path": input_file_path,
            "output_file_path": output_file_path
        }
        
        return render_template_string(RESULT_TEMPLATE, 
                                    title="Translation Success", 
                                    result_type="success", 
                                    result=success_data)
        
    except Exception as e:
        error_data = {
            "error": "An error occurred while processing",
            "details": str(e)
        }
        return render_template_string(RESULT_TEMPLATE, 
                                    title="Processing Error", 
                                    result_type="error", 
                                    result=error_data)

@app.route('/process-all-view', methods=['GET'])
def process_all_view():
    """Process all lines with HTML interface."""
    try:
        if not os.path.exists(input_file_path):
            error_data = {
                "error": "Input file not found",
                "details": input_file_path
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="Processing Error", 
                                        result_type="error", 
                                        result=error_data)
        
        processed_count = 0
        skipped_count = 0
        errors = []
        
        while True:
            english_text = read_first_line_from_file(input_file_path)
            
            if english_text is None:
                break  # No more lines
            
            if not english_text:  # Empty line
                remove_first_line_from_file(input_file_path)
                skipped_count += 1
                continue
            
            print(f"[FILES-TRANSLATOR] Processing line {processed_count + 1}: {english_text}")
            
            # Translate the text
            romanian_text = translate_text(english_text)
            
            if romanian_text is None:
                errors.append(f"Translation failed for: {english_text}")
                remove_first_line_from_file(input_file_path)  # Remove even if translation failed
                continue
            
            # Append to output file
            if not append_to_output_file(output_file_path, romanian_text):
                errors.append(f"Failed to write translation for: {english_text}")
                continue
            
            # Remove the processed line from input file
            if not remove_first_line_from_file(input_file_path):
                errors.append(f"Failed to remove processed line: {english_text}")
                break
            
            processed_count += 1
            print(f"[FILES-TRANSLATOR] Successfully processed {processed_count} lines")
        
        success_data = {
            "message": f"Processing completed! Processed {processed_count} lines, skipped {skipped_count} empty lines.",
            "processed_count": processed_count,
            "skipped_count": skipped_count,
            "errors": errors,
            "input_file_path": input_file_path,
            "output_file_path": output_file_path
        }
        
        return render_template_string(RESULT_TEMPLATE, 
                                    title="Batch Processing Complete", 
                                    result_type="success", 
                                    result=success_data)
        
    except Exception as e:
        error_data = {
            "error": "An error occurred while processing all lines",
            "details": str(e)
        }
        return render_template_string(RESULT_TEMPLATE, 
                                    title="Batch Processing Error", 
                                    result_type="error", 
                                    result=error_data)

@app.route('/trigger-processing', methods=['GET'])
def trigger_processing():
    """Process the next line from the input file - translate and move to output file."""
    
    try:
        # Check if input file exists
        if not os.path.exists(input_file_path):
            return jsonify({
                "error": "Input file not found",
                "input_file_path": input_file_path
            }), 404
        
        # Read the first line from input file
        english_text = read_first_line_from_file(input_file_path)
        
        if english_text is None:
            return jsonify({
                "message": "No more lines to process",
                "status": "completed"
            }), 200
        
        if not english_text:  # Empty line
            # Remove the empty line and try next
            remove_first_line_from_file(input_file_path)
            return jsonify({
                "message": "Skipped empty line",
                "status": "skipped"
            }), 200
        
        print(f"[FILES-TRANSLATOR] Processing line: {english_text}")
        
        # Translate the text
        romanian_text = translate_text(english_text)
        
        if romanian_text is None:
            return jsonify({
                "error": "Translation failed",
                "input": english_text
            }), 500
        
        print(f"[FILES-TRANSLATOR] Translation: {romanian_text}")
        
        # Append to output file
        if not append_to_output_file(output_file_path, romanian_text):
            return jsonify({
                "error": "Failed to write to output file",
                "output_file_path": output_file_path
            }), 500
        
        # Remove the processed line from input file
        if not remove_first_line_from_file(input_file_path):
            return jsonify({
                "error": "Failed to remove processed line from input file"
            }), 500
        
        return jsonify({
            "status": "success",
            "input": english_text,
            "output": romanian_text,
            "input_file_path": input_file_path,
            "output_file_path": output_file_path
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "An error occurred while processing",
            "details": str(e)
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get the current status of translation files."""
    try:
        input_exists = os.path.exists(input_file_path)
        output_exists = os.path.exists(output_file_path)
        
        lines_remaining = 0
        if input_exists:
            with open(input_file_path, 'r', encoding='utf-8') as file:
                lines_remaining = len(file.readlines())
        
        lines_translated = 0
        if output_exists:
            with open(output_file_path, 'r', encoding='utf-8') as file:
                lines_translated = len(file.readlines())
        
        return jsonify({
            "input_file_path": input_file_path,
            "input_file_exists": input_exists,
            "lines_remaining": lines_remaining,
            "output_file_path": output_file_path,
            "output_file_exists": output_exists,
            "lines_translated": lines_translated
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to get status",
            "details": str(e)
        }), 500

@app.route('/process-all', methods=['POST'])
def process_all():
    """Process all remaining lines in the input file."""
    try:
        if not os.path.exists(input_file_path):
            return jsonify({
                "error": "Input file not found",
                "input_file_path": input_file_path
            }), 404
        
        processed_count = 0
        skipped_count = 0
        errors = []
        
        while True:
            english_text = read_first_line_from_file(input_file_path)
            
            if english_text is None:
                break  # No more lines
            
            if not english_text:  # Empty line
                remove_first_line_from_file(input_file_path)
                skipped_count += 1
                continue
            
            print(f"[FILES-TRANSLATOR] Processing line {processed_count + 1}: {english_text}")
            
            # Translate the text
            romanian_text = translate_text(english_text)
            
            if romanian_text is None:
                errors.append(f"Translation failed for: {english_text}")
                remove_first_line_from_file(input_file_path)  # Remove even if translation failed
                continue
            
            # Append to output file
            if not append_to_output_file(output_file_path, romanian_text):
                errors.append(f"Failed to write translation for: {english_text}")
                continue
            
            # Remove the processed line from input file
            if not remove_first_line_from_file(input_file_path):
                errors.append(f"Failed to remove processed line: {english_text}")
                break
            
            processed_count += 1
            print(f"[FILES-TRANSLATOR] Successfully processed {processed_count} lines")
        
        return jsonify({
            "status": "completed",
            "processed_count": processed_count,
            "skipped_count": skipped_count,
            "errors": errors,
            "input_file_path": input_file_path,
            "output_file_path": output_file_path
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "An error occurred while processing all lines",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    # Run Flask with environment-specific settings
    app.run(host='0.0.0.0', port=5000, debug=flask_debug)