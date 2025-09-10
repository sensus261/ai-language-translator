from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import ollama
import os
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, unescape
import threading
import time
import sys
from datetime import datetime

# Setup logging to file while keeping console output
class TeeOutput:
    def __init__(self, *files):
        self.files = files
    
    def write(self, obj):
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

app = Flask(__name__)

ollama_service_url = os.getenv('OLLAMA_SERVICE_URL', 'http://host.docker.internal:11434')
enhance_product_model = os.getenv('ENHANCE_PRODUCT_MODEL', 'aya:8b-23')
flask_env = os.getenv('OLLAMA_API_SERVICE_ENV', 'development')
flask_debug = os.getenv('OLLAMA_API_SERVICE_DEBUG', 'true').lower() == 'true'

# File paths configuration
input_file_path = os.getenv('INPUT_FILE_PATH', '/app/data/english_text.txt')
output_file_path = os.getenv('OUTPUT_FILE_PATH', '/app/data/romanian_text.txt')

# XML file paths configuration
xml_input_file_path = os.getenv('XML_INPUT_FILE_PATH', '/app/original_fallout_files/Fallout4_en_fr.xml')
xml_output_file_path = os.getenv('XML_OUTPUT_FILE_PATH', '/app/original_fallout_files/Fallout4_en_ro.xml')

app.config['ENV'] = flask_env
app.config['DEBUG'] = flask_debug

print(" ")
print(f"[FILES-TRANSLATOR] Using OLLAMA_SERVICE_URL: {ollama_service_url}")
print(f"[FILES-TRANSLATOR] Using ENHANCE_PRODUCT_MODEL: {enhance_product_model}")
print(f"[FILES-TRANSLATOR] Flask environment: {flask_env}")
print(f"[FILES-TRANSLATOR] Flask debug mode: {flask_debug}")
print(f"[FILES-TRANSLATOR] Input file path: {input_file_path}")
print(f"[FILES-TRANSLATOR] Output file path: {output_file_path}")
print(f"[FILES-TRANSLATOR] XML input file path: {xml_input_file_path}")
print(f"[FILES-TRANSLATOR] XML output file path: {xml_output_file_path}")
print(" ")

enhance_product_client = None
xml_batch_processing = False
xml_batch_stop_requested = False

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
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .translator-section { margin-bottom: 40px; padding: 20px; border-radius: 10px; background: #f8f9fa; }
        .translator-section h2 { color: #007bff; margin-top: 0; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .route-card { background: white; padding: 20px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #007bff; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .route-card h3 { margin-top: 0; color: #007bff; }
        .route-card p { color: #666; margin-bottom: 15px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px; }
        .btn:hover { background: #0056b3; }
        .btn-success { background: #28a745; }
        .btn-success:hover { background: #1e7e34; }
        .btn-warning { background: #ffc107; color: #212529; }
        .btn-warning:hover { background: #e0a800; }
        .btn-purple { background: #6f42c1; }
        .btn-purple:hover { background: #5a32a3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Files Translator Service</h1>
        
        <div class="translator-section">
            <h2>� Basic Text File Translator</h2>
            <p>Translate plain text files line by line from English to Romanian.</p>
            <a href="/basic-file-translator" class="btn">Access Text Translator</a>
        </div>
        
        <div class="translator-section">
            <h2>🎮 Fallout 4 XML Translator</h2>
            <p>Specialized translator for Fallout 4 XML language files. Translates game content while preserving XML structure and IDs.</p>
            <a href="/fallout4-xml-translator" class="btn btn-purple">Access XML Translator</a>
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
                {% if result.batch_processing_status is defined %}
                <div class="status-item">
                    <div class="status-number">
                        {% if result.batch_processing_status %}
                            🔄
                        {% else %}
                            ⏸️
                        {% endif %}
                    </div>
                    <div>
                        {% if result.batch_processing_status %}
                            Batch Processing
                        {% else %}
                            Ready
                        {% endif %}
                    </div>
                </div>
                {% endif %}
            </div>
            <div class="result-box info">
                <p><strong>Input File:</strong> {{ result.input_file_path }} 
                   {% if result.input_file_exists %}✅{% else %}❌{% endif %}</p>
                <p><strong>Output File:</strong> {{ result.output_file_path }} 
                   {% if result.output_file_exists %}✅{% else %}❌{% endif %}</p>
                {% if result.batch_processing_status is defined %}
                <p><strong>Batch Processing Status:</strong> 
                   {% if result.batch_processing_status %}
                       <span style="color: #28a745;">🔄 Currently running "Process All XML Entries"</span>
                   {% else %}
                       <span style="color: #6c757d;">⏸️ No batch processing active</span>
                   {% endif %}
                </p>
                {% endif %}
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
        
        {% if back_link %}
            <a href="{{ back_link }}" class="btn">⬅️ Back to {{ back_text or 'Previous' }}</a>
        {% endif %}
        {% if show_refresh %}
            <a href="javascript:location.reload()" class="btn btn-success">🔄 Translate next line</a>
        {% endif %}
        {% if show_refresh_status %}
            <a href="javascript:location.reload()" class="btn btn-success">🔄 Refresh Status</a>
        {% endif %}
        {% if show_stop_batch %}
            <a href="/xml-stop-batch-processing" class="btn" style="background: #dc3545; margin-left: 10px;">🛑 Stop processing</a>
        {% endif %}
    </div>
</body>
</html>
'''

BASIC_TRANSLATOR_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Basic File Translator</title>
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
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #545b62; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 Basic File Translator</h1>
        
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
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/" class="btn btn-secondary">🏠 Back to Home</a>
        </div>
    </div>
</body>
</html>
'''

XML_TRANSLATOR_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Fallout 4 XML Translator</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .route-card { background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #6f42c1; }
        .route-card h3 { margin-top: 0; color: #6f42c1; }
        .route-card p { color: #666; margin-bottom: 15px; }
        .btn { background: #6f42c1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px; }
        .btn:hover { background: #5a32a3; }
        .btn-success { background: #28a745; }
        .btn-success:hover { background: #1e7e34; }
        .btn-warning { background: #ffc107; color: #212529; }
        .btn-warning:hover { background: #e0a800; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #545b62; }
        .info-box { background: #e7f3ff; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 20px 0; }
        .status-banner { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; border-radius: 5px; padding: 15px; margin: 20px 0; text-align: center; font-weight: bold; }
        .status-banner.processing { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Fallout 4 XML Translator</h1>
        
        <div class="info-box">
            <h4>ℹ️ About this translator</h4>
            <p>This tool translates Fallout 4 XML language files from English to Romanian while preserving the XML structure, IDs, and formatting. It processes one entry at a time to handle large files efficiently.</p>
        </div>
        
        {% if batch_processing_status %}
        <div class="status-banner processing">
            🔄 Batch processing is currently running - translating all XML entries automatically
        </div>
        {% else %}
        <div class="status-banner">
            ⏸️ No batch processing active - ready for manual translation
        </div>
        {% endif %}
        
        <div class="route-card">
            <h3>📊 Check XML Status</h3>
            <p>View the current status of XML translation files, including entries remaining and translated.</p>
            <a href="/xml-status-view" class="btn">View XML Status</a>
        </div>
        
        <div class="route-card">
            <h3>⚡ Process Next XML Entry</h3>
            <p>Translate the next XML string entry from the input file and move it to the output file.</p>
            {% if batch_processing_status %}
                <span class="btn" style="background: #6c757d; cursor: not-allowed;">⚡ Process Next Entry (Disabled - Batch Running)</span>
            {% else %}
                <a href="/xml-trigger-processing-view" class="btn btn-success">Process Next Entry</a>
            {% endif %}
        </div>
        
        <div class="route-card">
            <h3>🚀 Process All XML Entries</h3>
            <p>Translate all remaining XML entries in the input file. This may take some time for large files.</p>
            {% if batch_processing_status %}
                <span class="btn" style="background: #6c757d; cursor: not-allowed;">🚀 Process All Entries (Already Running)</span>
            {% else %}
                <a href="/xml-process-all-view" class="btn btn-warning">Process All Entries</a>
            {% endif %}
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/" class="btn btn-secondary">🏠 Back to Home</a>
        </div>
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

# XML Processing Functions
def find_next_xml_string_entry(file_path):
    """Find the next <String> entry in the XML file and return its details."""
    try:
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Look for the first <String> entry
        string_pattern = re.compile(r'(<String[^>]*>.*?</String>)', re.DOTALL)
        match = string_pattern.search(content)
        
        if not match:
            return None
        
        string_entry = match.group(1)
        
        # Extract the source text
        source_match = re.search(r'<Source>(.*?)</Source>', string_entry, re.DOTALL)
        if not source_match:
            return None
        
        source_text = source_match.group(1).strip()
        
        # Extract attributes from the String tag
        string_tag_match = re.search(r'<String([^>]*)>', string_entry)
        attributes = string_tag_match.group(1) if string_tag_match else ''
        
        return {
            'full_entry': string_entry,
            'source_text': unescape(source_text),
            'attributes': attributes,
            'start_pos': match.start(),
            'end_pos': match.end()
        }
        
    except Exception as e:
        print(f"[XML-TRANSLATOR] Error finding next XML entry: {str(e)}")
        return None

def remove_xml_string_entry(file_path, start_pos, end_pos):
    """Remove a specific XML string entry from the file."""
    try:
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Remove the entry and any trailing newline
        new_content = content[:start_pos] + content[end_pos:]
        new_content = re.sub(r'\n\s*\n', '\n', new_content)  # Remove extra empty lines
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"[XML-TRANSLATOR] Error removing XML entry: {str(e)}")
        return False

def append_xml_string_entry(file_path, attributes, source_text, dest_text):
    """Append a translated XML string entry to the output file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Check if file exists and has proper structure
        if not os.path.exists(file_path):
            # Create new XML file with proper structure
            xml_header = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<SSTXMLRessources>
  <Params>
    <Addon>Fallout4</Addon>
    <Source>en</Source>
    <Dest>ro</Dest>
    <Version>2</Version>
  </Params>
  <Content>
  </Content>
</SSTXMLRessources>'''
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(xml_header)
        
        # Read current content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Prepare the new string entry
        escaped_source = escape(source_text)
        escaped_dest = escape(dest_text)
        
        new_entry = f'''    <String{attributes}>
      <Source>{escaped_source}</Source>
      <Dest>{escaped_dest}</Dest>
    </String>'''
        
        # Find the </Content> tag and insert before it
        content_end_pos = content.find('  </Content>')
        if content_end_pos != -1:
            new_content = content[:content_end_pos] + new_entry + '\n' + content[content_end_pos:]
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            return True
        
        return False
        
    except Exception as e:
        print(f"[XML-TRANSLATOR] Error appending XML entry: {str(e)}")
        return False

def count_xml_string_entries(file_path):
    """Count the number of <String> entries in an XML file."""
    try:
        if not os.path.exists(file_path):
            return 0
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Count <String> entries
        string_pattern = re.compile(r'<String[^>]*>', re.DOTALL)
        matches = string_pattern.findall(content)
        
        return len(matches)
        
    except Exception as e:
        print(f"[XML-TRANSLATOR] Error counting XML entries: {str(e)}")
        return 0

def process_all_xml_entries_background():
    """Background function to process all XML entries."""
    global xml_batch_processing, xml_batch_stop_requested
    
    try:
        processed_count = 0
        skipped_count = 0
        errors = []
        
        print(f"[XML-TRANSLATOR] Starting background batch processing...")
        
        while True:
            # Check if stop was requested
            if xml_batch_stop_requested:
                print(f"[XML-TRANSLATOR] Batch processing stopped by user request after {processed_count} entries")
                break
            
            xml_entry = find_next_xml_string_entry(xml_input_file_path)
            
            if xml_entry is None:
                print(f"[XML-TRANSLATOR] Batch processing completed - no more entries found")
                break  # No more entries
            
            source_text = xml_entry['source_text']
            
            if not source_text.strip():  # Empty entry
                remove_xml_string_entry(xml_input_file_path, xml_entry['start_pos'], xml_entry['end_pos'])
                append_xml_string_entry(xml_output_file_path, xml_entry['attributes'], source_text, source_text)
                skipped_count += 1
                continue
            
            # Translate the text
            romanian_text = translate_text(source_text)
            
            if romanian_text is None:
                errors.append(f"Translation failed for: {source_text}")
                remove_xml_string_entry(xml_input_file_path, xml_entry['start_pos'], xml_entry['end_pos'])
                continue
            
            # Append to output XML file
            if not append_xml_string_entry(xml_output_file_path, xml_entry['attributes'], source_text, romanian_text):
                errors.append(f"Failed to write translation for: {source_text}")
                continue
            
            # Remove the processed entry from input file
            if not remove_xml_string_entry(xml_input_file_path, xml_entry['start_pos'], xml_entry['end_pos']):
                errors.append(f"Failed to remove processed XML entry: {source_text}")
                break
            
            processed_count += 1
            
            # Log progress every 10 entries
            if processed_count % 10 == 0:
                print(f"[XML-TRANSLATOR] Progress: {processed_count} XML entries processed")
        
        print(f"[XML-TRANSLATOR] Background batch processing finished. Processed: {processed_count}, Skipped: {skipped_count}, Errors: {len(errors)}")
        
    except Exception as e:
        print(f"[XML-TRANSLATOR] Error in background batch processing: {str(e)}")
    
    finally:
        # Always reset the flags when processing is done
        xml_batch_processing = False
        xml_batch_stop_requested = False
        print(f"[XML-TRANSLATOR] Background batch processing flags reset")

@app.route('/', methods=['GET'])
def home():
    """Home page with links to all available routes."""
    return render_template_string(HOME_TEMPLATE)

@app.route('/basic-file-translator', methods=['GET'])
def basic_file_translator():
    """Basic file translator interface."""
    return render_template_string(BASIC_TRANSLATOR_TEMPLATE)

@app.route('/fallout4-xml-translator', methods=['GET'])
def fallout4_xml_translator():
    """Fallout 4 XML translator interface."""
    global xml_batch_processing
    return render_template_string(XML_TRANSLATOR_TEMPLATE, batch_processing_status=xml_batch_processing)

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
                                        result=error_data,
                                        back_link="/basic-file-translator",
                                        back_text="Text Translator")
        
        # Read the first line from input file
        english_text = read_first_line_from_file(input_file_path)
        
        if english_text is None:
            completed_data = {
                "message": "No more lines to process"
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="Processing Complete", 
                                        result_type="completed", 
                                        result=completed_data,
                                        back_link="/basic-file-translator",
                                        back_text="Text Translator")
        
        if not english_text:  # Empty line
            # Remove the empty line and try next
            remove_first_line_from_file(input_file_path)
            skipped_data = {
                "message": "Skipped empty line"
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="Line Skipped", 
                                        result_type="skipped", 
                                        result=skipped_data,
                                        back_link="/basic-file-translator",
                                        back_text="Text Translator")
        
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

# XML Translator Routes
@app.route('/xml-status-view', methods=['GET'])
def xml_status_view():
    """View XML status with HTML interface."""
    try:
        global xml_batch_processing
        
        input_exists = os.path.exists(xml_input_file_path)
        output_exists = os.path.exists(xml_output_file_path)
        
        entries_remaining = 0
        if input_exists:
            entries_remaining = count_xml_string_entries(xml_input_file_path)
        
        entries_translated = 0
        if output_exists:
            entries_translated = count_xml_string_entries(xml_output_file_path)
        
        status_data = {
            "input_file_path": xml_input_file_path,
            "input_file_exists": input_exists,
            "lines_remaining": entries_remaining,
            "output_file_path": xml_output_file_path,
            "output_file_exists": output_exists,
            "lines_translated": entries_translated,
            "batch_processing_status": xml_batch_processing
        }
        
        return render_template_string(RESULT_TEMPLATE, 
                                    title="XML Translation Status", 
                                    result_type="status", 
                                    result=status_data,
                                    back_link="/fallout4-xml-translator",
                                    back_text="XML Translator",
                                    show_refresh_status=True,
                                    show_stop_batch=xml_batch_processing)
        
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

@app.route('/xml-trigger-processing-view', methods=['GET'])
def xml_trigger_processing_view():
    """Process next XML entry with HTML interface."""
    try:
        global xml_batch_processing
        
        # Check if batch processing is running
        if xml_batch_processing:
            error_data = {
                "error": "Batch processing is currently running",
                "details": "Please wait for batch processing to complete or stop it before processing individual entries."
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Processing Blocked", 
                                        result_type="error", 
                                        result=error_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
        # Check if input file exists
        if not os.path.exists(xml_input_file_path):
            error_data = {
                "error": "XML input file not found",
                "details": xml_input_file_path
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Processing Error", 
                                        result_type="error", 
                                        result=error_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
        # Find the next XML string entry
        xml_entry = find_next_xml_string_entry(xml_input_file_path)
        
        if xml_entry is None:
            completed_data = {
                "message": "No more XML entries to process"
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Processing Complete", 
                                        result_type="completed", 
                                        result=completed_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator",
                                        show_refresh=True)
        
        source_text = xml_entry['source_text']
        
        if not source_text.strip():  # Empty source
            # Remove the empty entry and skip
            remove_xml_string_entry(xml_input_file_path, xml_entry['start_pos'], xml_entry['end_pos'])
            # Also add it to output with empty translation
            append_xml_string_entry(xml_output_file_path, xml_entry['attributes'], source_text, source_text)
            
            skipped_data = {
                "message": "Skipped empty XML entry"
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Entry Skipped", 
                                        result_type="skipped", 
                                        result=skipped_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator",
                                        show_refresh=True)
        
        print(f"[XML-TRANSLATOR] Processing XML entry: {source_text}")
        
        # Translate the text
        romanian_text = translate_text(source_text)
        
        if romanian_text is None:
            error_data = {
                "error": "XML translation failed",
                "details": f"Input: {source_text}"
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Translation Error", 
                                        result_type="error", 
                                        result=error_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
        print(f"[XML-TRANSLATOR] Translation: {romanian_text}")
        
        # Append to output XML file
        if not append_xml_string_entry(xml_output_file_path, xml_entry['attributes'], source_text, romanian_text):
            error_data = {
                "error": "Failed to write to XML output file",
                "details": xml_output_file_path
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML File Write Error", 
                                        result_type="error", 
                                        result=error_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
        # Remove the processed entry from input file
        if not remove_xml_string_entry(xml_input_file_path, xml_entry['start_pos'], xml_entry['end_pos']):
            error_data = {
                "error": "Failed to remove processed XML entry from input file"
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML File Update Error", 
                                        result_type="error", 
                                        result=error_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
        success_data = {
            "input": source_text,
            "output": romanian_text,
            "input_file_path": xml_input_file_path,
            "output_file_path": xml_output_file_path
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

@app.route('/xml-process-all-view', methods=['GET'])
def xml_process_all_view():
    """Start processing all XML entries in background."""
    try:
        global xml_batch_processing, xml_batch_stop_requested
        
        # Check if batch processing is already running
        if xml_batch_processing:
            error_data = {
                "error": "Batch processing already in progress",
                "details": "Please wait for the current batch processing to complete before starting a new one."
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Processing Already Running", 
                                        result_type="error", 
                                        result=error_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
        if not os.path.exists(xml_input_file_path):
            error_data = {
                "error": "XML input file not found",
                "details": xml_input_file_path
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Processing Error", 
                                        result_type="error", 
                                        result=error_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
        # Count remaining entries for user info
        remaining_entries = count_xml_string_entries(xml_input_file_path)
        
        if remaining_entries == 0:
            completed_data = {
                "message": "No XML entries found to process."
            }
            return render_template_string(RESULT_TEMPLATE, 
                                        title="XML Processing Complete", 
                                        result_type="completed", 
                                        result=completed_data,
                                        back_link="/fallout4-xml-translator",
                                        back_text="XML Translator")
        
        # Set the flags to indicate batch processing is starting
        xml_batch_processing = True
        xml_batch_stop_requested = False
        
        # Start the background processing thread
        processing_thread = threading.Thread(target=process_all_xml_entries_background)
        processing_thread.daemon = True  # Thread will die when main program exits
        processing_thread.start()
        
        success_data = {
            "message": f"Batch processing started successfully! Processing {remaining_entries} XML entries in the background. You can check the status or stop the process using the buttons below.",
            "entries_to_process": remaining_entries
        }
        
        return render_template_string(RESULT_TEMPLATE, 
                                    title="XML Batch Processing Started", 
                                    result_type="success", 
                                    result=success_data,
                                    back_link="/fallout4-xml-translator",
                                    back_text="XML Translator")
        
    except Exception as e:
        # Make sure to reset the flags if an exception occurs during startup
        xml_batch_processing = False
        xml_batch_stop_requested = False
        
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

@app.route('/xml-stop-batch-processing', methods=['GET'])
def xml_stop_batch_processing():
    """Stop the running XML batch processing."""
    global xml_batch_stop_requested
    
    if not xml_batch_processing:
        error_data = {
            "error": "No batch processing is currently running",
            "details": "There is no active batch processing to stop."
        }
        return render_template_string(RESULT_TEMPLATE, 
                                    title="No Processing to Stop", 
                                    result_type="error", 
                                    result=error_data,
                                    back_link="/fallout4-xml-translator",
                                    back_text="XML Translator")
    
    # Set the stop flag
    xml_batch_stop_requested = True
    
    success_data = {
        "message": "Stop request sent. The batch processing will stop after completing the current entry."
    }
    
    return render_template_string(RESULT_TEMPLATE, 
                                title="Stop Request Sent", 
                                result_type="success", 
                                result=success_data,
                                back_link="/fallout4-xml-translator",
                                back_text="XML Translator")

if __name__ == '__main__':
    try:
        # Run Flask with environment-specific settings
        app.run(host='0.0.0.0', port=5000, debug=flask_debug)
    except KeyboardInterrupt:
        print(f"[FILES-TRANSLATOR] Application interrupted by user")
    finally:
        # Cleanup: restore stdout and close log file
        print(f"[FILES-TRANSLATOR] Logging ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.stdout = original_stdout
        log_file.close()
        print(f"Log file saved: {log_filename}")