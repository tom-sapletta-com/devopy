#!/usr/bin/env python3
"""
Example showing how to use the editor_sandbox decorator for automatic Docker sandbox setup
"""
import os
import sys
import json
from flask import Flask, jsonify, request, render_template_string

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the editor_sandbox decorator
from devopy.decorators.editor_sandbox import editor_sandbox

# Define required packages
REQUIRED_PACKAGES = [
    "flask==2.0.1",
    "requests==2.28.1"
]

# Simple HTML template for testing
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Docker Sandbox Example</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .container {
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .output {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            white-space: pre-wrap;
            font-family: monospace;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }
        input[type="text"] {
            padding: 8px;
            width: 70%;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <h1>Docker Sandbox Example</h1>
    
    <div class="container">
        <h2>Sandbox Status</h2>
        <div class="output" id="status">Loading...</div>
        <button onclick="checkStatus()">Refresh Status</button>
    </div>
    
    <div class="container">
        <h2>Execute Command</h2>
        <input type="text" id="command" placeholder="Enter command (e.g., ls -la)">
        <button onclick="executeCommand()">Execute</button>
        <div class="output" id="commandOutput"></div>
    </div>
    
    <div class="container">
        <h2>Python Code Execution</h2>
        <textarea id="pythonCode" rows="6" style="width: 100%; margin-bottom: 10px;">
import platform
import sys

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print("Hello from Docker sandbox!")</textarea>
        <button onclick="executePython()">Run Python</button>
        <div class="output" id="pythonOutput"></div>
    </div>
    
    <script>
        // Check sandbox status
        function checkStatus() {
            fetch('/api/docker-status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerText = JSON.stringify(data, null, 2);
                })
                .catch(error => {
                    document.getElementById('status').innerText = "Error: " + error;
                });
        }
        
        // Execute command in sandbox
        function executeCommand() {
            const command = document.getElementById('command').value;
            if (!command) return;
            
            fetch('/api/docker-execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    command: command
                })
            })
            .then(response => response.json())
            .then(data => {
                let output = "";
                if (data.success) {
                    output = data.stdout || "Command executed successfully (no output)";
                } else {
                    output = "Error: " + (data.stderr || data.error || "Unknown error");
                }
                document.getElementById('commandOutput').innerText = output;
            })
            .catch(error => {
                document.getElementById('commandOutput').innerText = "Error: " + error;
            });
        }
        
        // Execute Python code in sandbox
        function executePython() {
            const code = document.getElementById('pythonCode').value;
            if (!code) return;
            
            // Create a temporary Python file
            fetch('/api/execute-python', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: code
                })
            })
            .then(response => response.json())
            .then(data => {
                let output = "";
                if (data.success) {
                    output = data.stdout || "Code executed successfully (no output)";
                    if (data.stderr) {
                        output += "\n\nStderr:\n" + data.stderr;
                    }
                } else {
                    output = "Error: " + (data.stderr || data.error || "Unknown error");
                }
                document.getElementById('pythonOutput').innerText = output;
            })
            .catch(error => {
                document.getElementById('pythonOutput').innerText = "Error: " + error;
            });
        }
        
        // Initialize
        window.onload = function() {
            checkStatus();
        };
    </script>
</body>
</html>
"""

@editor_sandbox(
    base_image="python:3.12-slim",
    packages=REQUIRED_PACKAGES,
    ports={5001: 5001},
    volumes={os.path.dirname(os.path.dirname(os.path.abspath(__file__))): "/app"},
    env_vars={"FLASK_ENV": "development", "FLASK_DEBUG": "1"},
    auto_start=True
)
def create_app(sandbox=None):
    """
    Create a Flask application with Docker sandbox integration
    """
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/docker-status')
    def docker_status():
        """Return the status of the Docker sandbox"""
        if sandbox:
            return jsonify({
                'ready': sandbox.ready,
                'status': sandbox.status,
                'id': sandbox.sandbox_id,
                'container_id': sandbox.container_id,
                'base_image': sandbox.base_image,
                'packages': sandbox.packages
            })
        else:
            return jsonify({'ready': False, 'status': 'not_initialized'})
    
    @app.route('/api/docker-execute', methods=['POST'])
    def docker_execute():
        """Execute a command in the Docker sandbox"""
        if not sandbox or not sandbox.ready:
            return jsonify({'error': 'Docker sandbox not ready'}), 400
        
        data = request.json
        command = data.get('command')
        workdir = data.get('workdir', '/app')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Execute command in the container
        if isinstance(command, str):
            command = command.split()
        
        result = sandbox.execute(command, workdir)
        return jsonify(result)
    
    @app.route('/api/execute-python', methods=['POST'])
    def execute_python():
        """Execute Python code in the Docker sandbox"""
        if not sandbox or not sandbox.ready:
            return jsonify({'error': 'Docker sandbox not ready'}), 400
        
        data = request.json
        code = data.get('code')
        
        if not code:
            return jsonify({'error': 'No code provided'}), 400
        
        # Create a temporary Python file in the container
        code_escaped = code.replace("'", "'\\''")
        setup_result = sandbox.execute([
            "bash", "-c", f"echo '{code_escaped}' > /tmp/temp_code.py"
        ])
        
        if not setup_result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to create temporary file',
                'stderr': setup_result['stderr']
            })
        
        # Execute the Python code
        result = sandbox.execute(["python", "/tmp/temp_code.py"])
        
        # Clean up
        sandbox.execute(["rm", "/tmp/temp_code.py"])
        
        return jsonify(result)
    
    return app

if __name__ == '__main__':
    app = create_app()
    print(f"Starting Docker Sandbox Example on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
