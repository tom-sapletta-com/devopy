# Editor Sandbox Decorator

The `editor_sandbox` decorator provides an easy way to automatically set up a Docker sandbox environment for your devopy applications. This is particularly useful for editor applications and development environments where isolation and reproducibility are important.

## Features

- **Automatic Docker Sandbox Setup**: Creates and manages Docker containers with specified configurations
- **Package Management**: Automatically installs required Python packages in the sandbox
- **Port Mapping**: Maps host ports to container ports for web applications
- **Volume Mounting**: Mounts local directories into the container
- **Command Execution**: Provides an API to execute commands within the sandbox
- **Cleanup Management**: Automatically cleans up containers when the application exits

## Installation

The `editor_sandbox` decorator is included in the devopy package. Make sure you have Docker installed on your system.

```bash
# Install Docker if not already installed
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to the docker group (optional, for running without sudo)
sudo usermod -aG docker $USER
```

## Basic Usage

Here's a simple example of how to use the `editor_sandbox` decorator:

```python
from devopy import editor_sandbox

@editor_sandbox(
    base_image="python:3.12-slim",
    packages=["flask", "requests"],
    ports={5000: 5000},
    volumes={"/local/path": "/container/path"},
    env_vars={"DEBUG": "true"}
)
def my_app(sandbox=None):
    # Your application code here
    # The sandbox parameter is automatically injected
    
    # Example: Execute a command in the sandbox
    result = sandbox.execute(["ls", "-la"])
    print(result["stdout"])
    
    return "Application started with Docker sandbox"

if __name__ == "__main__":
    my_app()
```

## API Reference

### `editor_sandbox` Decorator

```python
@editor_sandbox(
    base_image="python:3.12-slim",
    packages=None,
    ports=None,
    volumes=None,
    env_vars=None,
    auto_start=True,
    auto_install=True
)
```

#### Parameters

- **base_image** (str): Base Docker image to use (default: "python:3.12-slim")
- **packages** (List[str]): List of Python packages to install in the sandbox
- **ports** (Dict[int, int]): Dictionary mapping host ports to container ports
- **volumes** (Dict[str, str]): Dictionary mapping host paths to container paths
- **env_vars** (Dict[str, str]): Dictionary of environment variables to set in the container
- **auto_start** (bool): Whether to start the sandbox automatically (default: True)
- **auto_install** (bool): Whether to automatically install required packages locally (default: True)

### `EditorDockerSandbox` Class

The `EditorDockerSandbox` class is automatically created by the decorator and passed to your function as the `sandbox` parameter.

#### Methods

- **start()**: Starts the Docker sandbox if not already running
- **execute(command, workdir="/app")**: Executes a command in the sandbox
- **cleanup()**: Stops and removes the Docker container

#### Properties

- **ready** (bool): Whether the sandbox is ready for use
- **status** (str): Current status of the sandbox
- **sandbox_id** (str): Unique ID for the sandbox
- **container_id** (str): Docker container ID
- **base_image** (str): Base Docker image used
- **packages** (List[str]): Python packages installed in the sandbox
- **ports** (Dict[int, int]): Port mappings
- **volumes** (Dict[str, str]): Volume mappings
- **env_vars** (Dict[str, str]): Environment variables

### Utility Functions

- **get_sandbox(func_id)**: Gets a sandbox by function ID
- **list_sandboxes()**: Lists all registered sandboxes and their status
- **cleanup_all_sandboxes()**: Stops and removes all Docker sandboxes

## Examples

### Web Application with Docker Sandbox

```python
from flask import Flask, jsonify
from devopy import editor_sandbox
import os

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
    
    @app.route('/sandbox-status')
    def status():
        return jsonify({
            'ready': sandbox.ready,
            'status': sandbox.status,
            'id': sandbox.sandbox_id,
            'container_id': sandbox.container_id
        })
    
    @app.route('/run-command/<command>')
    def run_command(command):
        result = sandbox.execute(command.split())
        return jsonify(result)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
```

### Running Python Code in the Sandbox

```python
from devopy import editor_sandbox

@editor_sandbox(
    packages=["numpy", "pandas"]
)
def run_data_analysis(code, sandbox=None):
    # Save code to a temporary file in the sandbox
    code_escaped = code.replace("'", "'\\''")
    sandbox.execute([
        "bash", "-c", f"echo '{code_escaped}' > /tmp/analysis.py"
    ])
    
    # Run the code
    result = sandbox.execute(["python", "/tmp/analysis.py"])
    
    # Clean up
    sandbox.execute(["rm", "/tmp/analysis.py"])
    
    return result

if __name__ == '__main__':
    code = """
import numpy as np
import pandas as pd

# Create a sample dataframe
df = pd.DataFrame({
    'A': np.random.rand(5),
    'B': np.random.rand(5)
})

print(df)
print("\\nMean values:")
print(df.mean())
"""
    
    result = run_data_analysis(code)
    print(result["stdout"])
```

## Best Practices

1. **Specify Package Versions**: Always specify exact versions of packages to ensure reproducibility
2. **Mount Only Necessary Directories**: Only mount directories that are needed by your application
3. **Use Auto-Remove**: Set `auto_remove=True` to automatically remove containers when they're no longer needed
4. **Handle Errors**: Always check the `success` field in the result of `execute()` to handle errors
5. **Clean Up Resources**: Use `cleanup_all_sandboxes()` when your application exits to ensure all resources are freed

## Troubleshooting

### Common Issues

1. **Docker Not Running**: Make sure Docker is installed and running on your system
2. **Permission Denied**: You may need to run your application with sudo or add your user to the docker group
3. **Port Already in Use**: If a port is already in use, specify a different port mapping
4. **Container Not Starting**: Check the Docker logs for more information

### Debugging

To debug issues with the Docker sandbox, you can:

1. Check the sandbox status: `print(sandbox.status)`
2. List all sandboxes: `from devopy import list_sandboxes; print(list_sandboxes())`
3. Execute a diagnostic command: `print(sandbox.execute(["cat", "/etc/os-release"]))`

## Advanced Usage

### Custom Docker Images

You can use custom Docker images with the `editor_sandbox` decorator:

```python
@editor_sandbox(
    base_image="my-custom-image:latest",
    auto_start=True
)
def my_app(sandbox=None):
    # Your code here
    pass
```

### Running Long-Lived Services

To run long-lived services in the sandbox:

```python
@editor_sandbox(
    base_image="python:3.12-slim",
    packages=["flask", "gunicorn"]
)
def run_web_service(sandbox=None):
    # Copy application files to the container
    sandbox.execute(["mkdir", "-p", "/app/web"])
    
    # Start the service in the background
    sandbox.execute([
        "bash", "-c", 
        "cd /app/web && gunicorn app:app -b 0.0.0.0:8000 &"
    ])
    
    print("Web service started in Docker sandbox")
    
    # Keep the main process running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
```

### Multiple Sandboxes

You can create and manage multiple sandboxes:

```python
from devopy import editor_sandbox, EditorDockerSandbox

@editor_sandbox(base_image="python:3.12-slim")
def main_app(sandbox=None):
    # Create additional sandboxes
    data_sandbox = EditorDockerSandbox(
        base_image="python:3.12-slim",
        packages=["pandas", "numpy"],
        ports={8501: 8501}
    )
    data_sandbox.start()
    
    # Use both sandboxes
    sandbox.execute(["echo", "Hello from main sandbox"])
    data_sandbox.execute(["echo", "Hello from data sandbox"])
    
    # Clean up the additional sandbox when done
    data_sandbox.cleanup()
```

## Contributing

Contributions to improve the `editor_sandbox` decorator are welcome! Please submit issues and pull requests to the devopy GitHub repository.

## License

The `editor_sandbox` decorator is part of the devopy package and is licensed under the same terms.
