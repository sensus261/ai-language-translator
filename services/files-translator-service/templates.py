"""HTML templates for the Flask application."""

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
            <h2>📄 Basic Text File Translator</h2>
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
