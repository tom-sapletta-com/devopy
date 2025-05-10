#!/usr/bin/env python3
"""
Docker sandbox implementation without Flask integration
"""
import os
import sys
import subprocess
import json
import tempfile
import uuid
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('docker_sandbox')

class DockerSandbox:
    """Docker sandbox for isolated code execution"""
    
    def __init__(
        self,
        base_image: str = "python:3.12-slim",
        packages: List[str] = None,
        ports: Dict[int, int] = None,
        volumes: Dict[str, str] = None,
        env_vars: Dict[str, str] = None
    ):
        """Initialize Docker sandbox"""
        self.base_image = base_image
        self.packages = packages or []
        self.ports = ports or {}
        self.volumes = volumes or {}
        self.env_vars = env_vars or {}
        self.container_id = None
        self.sandbox_id = str(uuid.uuid4())[:8]
        self.image_name = f"docker_sandbox:{self.sandbox_id}"
        self.container_name = f"docker_sandbox_{self.sandbox_id}"
        self.ready = False
        self.status = "not_started"
        
        logger.info(f"Initialized Docker sandbox {self.sandbox_id}")
        logger.debug(f"Base image: {self.base_image}")
        logger.debug(f"Packages: {self.packages}")
        logger.debug(f"Ports: {self.ports}")
        logger.debug(f"Volumes: {self.volumes}")
    
    def build_image(self) -> bool:
        """Build Docker image with specified packages"""
        logger.info(f"Building Docker image {self.image_name}")
        
        # Create a temporary Dockerfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dockerfile', delete=False) as f:
            dockerfile_path = f.name
            
            # Write Dockerfile content
            f.write(f"FROM {self.base_image}\n")
            f.write("WORKDIR /app\n")
            
            # Add packages if specified
            if self.packages:
                packages_str = " ".join(self.packages)
                f.write(f"RUN pip install --no-cache-dir {packages_str}\n")
            
            # Set working directory
            f.write("WORKDIR /app\n")
            
            # Default CMD
            f.write('CMD ["python3", "-c", "print(\'Docker sandbox ready\')"]')
        
        try:
            # Build Docker image
            logger.debug(f"Building image from Dockerfile: {dockerfile_path}")
            result = subprocess.run(
                ["docker", "build", "-t", self.image_name, "-f", dockerfile_path, "."],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Clean up temporary Dockerfile
            os.unlink(dockerfile_path)
            
            logger.info(f"Successfully built Docker image {self.image_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to build Docker image: {e.stderr}")
            # Clean up temporary Dockerfile
            os.unlink(dockerfile_path)
            return False
    
    def start(self) -> bool:
        """Start Docker container"""
        logger.info(f"Starting Docker container {self.container_name}")
        
        # Build image if not already built
        if not self.build_image():
            logger.error("Failed to start container: Image build failed")
            return False
        
        # Prepare Docker run command
        cmd = ["docker", "run", "-d", "--name", self.container_name, "--rm"]
        
        # Add port mappings
        for container_port, host_port in self.ports.items():
            cmd.extend(["-p", f"{host_port}:{container_port}"])
        
        # Add volume mappings
        for host_path, container_path in self.volumes.items():
            cmd.extend(["-v", f"{host_path}:{container_path}"])
        
        # Add environment variables
        for key, value in self.env_vars.items():
            cmd.extend(["-e", f"{key}={value}"])
        
        # Add image name and command to keep container running
        cmd.extend([self.image_name, "tail", "-f", "/dev/null"])
        
        try:
            # Start Docker container
            logger.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.container_id = result.stdout.strip()
            self.ready = True
            self.status = "running"
            
            logger.info(f"Successfully started Docker container {self.container_name} (ID: {self.container_id})")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start Docker container: {e.stderr}")
            return False
    
    def execute(self, command: List[str]) -> Dict[str, Any]:
        """Execute command in Docker container"""
        if not self.ready or not self.container_id:
            logger.error("Cannot execute command: Container not ready")
            return {"error": "Container not ready", "returncode": 1}
        
        logger.info(f"Executing command in container {self.container_id}: {' '.join(command)}")
        
        try:
            # Execute command in container
            result = subprocess.run(
                ["docker", "exec", self.container_id] + command,
                capture_output=True,
                text=True
            )
            
            # Prepare result
            output = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            logger.debug(f"Command execution result: {output}")
            return output
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to execute command: {e}")
            return {"error": str(e), "returncode": 1}
    
    def cleanup(self) -> bool:
        """Stop and remove Docker container"""
        if not self.container_id:
            logger.warning("No container to clean up")
            return True
        
        logger.info(f"Cleaning up Docker container {self.container_id}")
        
        try:
            # Stop container
            subprocess.run(
                ["docker", "stop", self.container_id],
                capture_output=True,
                check=True
            )
            
            # Container is automatically removed due to --rm flag when starting
            self.container_id = None
            self.ready = False
            self.status = "stopped"
            
            logger.info("Successfully cleaned up Docker container")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clean up Docker container: {e}")
            return False
    
    def __del__(self):
        """Destructor to ensure container is cleaned up"""
        if self.container_id:
            self.cleanup()


# Example usage
if __name__ == "__main__":
    # Create sandbox
    sandbox = DockerSandbox(
        base_image="python:3.12-slim",
        packages=["numpy", "pandas", "matplotlib"],
        ports={8000: 8888},  # Map container port 8000 to host port 8888
        volumes={os.path.dirname(os.path.abspath(__file__)): "/app/examples"},
        env_vars={"PYTHONUNBUFFERED": "1"}
    )
    
    # Start sandbox
    if sandbox.start():
        print(f"Sandbox started with container ID: {sandbox.container_id}")
        
        # Execute a Python command
        result = sandbox.execute(["python", "-c", "print('Hello from Docker sandbox!')"])
        print(f"Command output: {result['stdout']}")
        
        # Execute a system command
        result = sandbox.execute(["ls", "-la", "/app"])
        print(f"Directory listing: {result['stdout']}")
        
        # Create and execute a Python file
        code = """
import numpy as np
import matplotlib.pyplot as plt

# Generate some data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Print some values
print(f"x: {x[:5]}")
print(f"y: {y[:5]}")
print("NumPy and Matplotlib are working!")
"""
        
        # Write code to a file in the container
        sandbox.execute(["bash", "-c", f"echo '{code}' > /app/test.py"])
        
        # Execute the file
        result = sandbox.execute(["python", "/app/test.py"])
        print(f"Python script output: {result['stdout']}")
        
        # Clean up
        sandbox.cleanup()
        print("Sandbox cleaned up")
    else:
        print("Failed to start sandbox")
