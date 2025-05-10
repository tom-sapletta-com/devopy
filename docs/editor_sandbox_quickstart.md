# Editor Sandbox Decorator - Quick Start Guide

## Overview

The `editor_sandbox` decorator automatically sets up a Docker sandbox environment for your devopy applications, making it easier to develop, test, and run your code in an isolated environment.

## Installation

Ensure you have Docker installed on your system:

```bash
# Check Docker installation
docker --version

# If not installed, install Docker (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

## Basic Usage

### 1. Import the decorator

```python
from devopy import editor_sandbox
```

### 2. Apply the decorator to your application function

```python
@editor_sandbox(
    base_image="python:3.12-slim",
    packages=["flask", "requests"],
    ports={5000: 5000}
)
def create_app(sandbox=None):
    # Your application code here
    # The sandbox parameter is automatically injected
    return app
```

### 3. Use the sandbox in your application

```python
@editor_sandbox(
    base_image="python:3.12-slim",
    packages=["flask", "requests"],
    ports={5000: 5000}
)
def create_app(sandbox=None):
    app = Flask(__name__)
    
    @app.route('/sandbox-status')
    def status():
        return jsonify({
            'ready': sandbox.ready,
            'status': sandbox.status,
            'id': sandbox.sandbox_id
        })
    
    @app.route('/run-command/<command>')
    def run_command(command):
        result = sandbox.execute(command.split())
        return jsonify(result)
    
    return app
```

## Common Parameters

- **base_image**: Base Docker image to use (default: "python:3.12-slim")
- **packages**: List of Python packages to install in the sandbox
- **ports**: Dictionary mapping host ports to container ports
- **volumes**: Dictionary mapping host paths to container paths
- **env_vars**: Dictionary of environment variables to set in the container
- **auto_start**: Whether to start the sandbox automatically (default: True)

## Example: Web Application with Docker Sandbox

```python
import os
from flask import Flask, jsonify
from devopy import editor_sandbox

@editor_sandbox(
    base_image="python:3.12-slim",
    packages=["flask==2.0.1", "requests==2.28.1"],
    ports={5000: 5000},
    volumes={os.path.dirname(os.path.abspath(__file__)): "/app"},
    env_vars={"FLASK_ENV": "development"}
)
def create_app(sandbox=None):
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "Hello from Docker sandbox!"
    
    @app.route('/execute-python', methods=['POST'])
    def execute_python():
        code = request.json.get('code')
        if not code:
            return jsonify({'error': 'No code provided'})
        
        # Create a temporary Python file in the container
        code_escaped = code.replace("'", "'\\''")
        setup_result = sandbox.execute([
            "bash", "-c", f"echo '{code_escaped}' > /tmp/temp_code.py"
        ])
        
        # Execute the Python code
        result = sandbox.execute(["python", "/tmp/temp_code.py"])
        
        # Clean up
        sandbox.execute(["rm", "/tmp/temp_code.py"])
        
        return jsonify(result)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
```

## Sandbox Methods

- **start()**: Starts the Docker sandbox if not already running
- **execute(command, workdir="/app")**: Executes a command in the sandbox
- **cleanup()**: Stops and removes the Docker container

## Utility Functions

```python
from devopy import list_sandboxes, get_sandbox, cleanup_all_sandboxes

# List all sandboxes
all_sandboxes = list_sandboxes()
print(all_sandboxes)

# Get a specific sandbox
sandbox = get_sandbox("module.function_name")

# Clean up all sandboxes
cleanup_all_sandboxes()
```

For more detailed documentation, see [editor_sandbox.md](editor_sandbox.md).
