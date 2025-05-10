import os
import sys
import subprocess
import uuid
import time
import signal
import atexit
import threading
import json
from functools import wraps
from pathlib import Path
import importlib.util
from typing import List, Dict, Any, Optional, Union, Callable

# Ensure the devopy package is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from devopy.sandbox.docker import DockerSandbox
from devopy.utils.auto_install import ensure_packages

# Global registry for running sandboxes
SANDBOX_REGISTRY = {}
SANDBOX_LOCK = threading.Lock()

class EditorDockerSandbox:
    """
    Class to manage Docker sandbox instances for the editor
    """
    def __init__(self, base_image: str = "python:3.12-slim", 
                 packages: List[str] = None, 
                 ports: Dict[int, int] = None,
                 volumes: Dict[str, str] = None,
                 env_vars: Dict[str, str] = None,
                 auto_remove: bool = True):
        self.base_image = base_image
        self.packages = packages or []
        self.ports = ports or {}
        self.volumes = volumes or {}
        self.env_vars = env_vars or {}
        self.auto_remove = auto_remove
        self.container_id = None
        self.sandbox_id = str(uuid.uuid4())[:8]
        self.docker_sandbox = DockerSandbox()
        self.ready = False
        self.status = "initializing"
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def start(self):
        """Start the Docker sandbox"""
        try:
            # Create Docker image with required packages
            image_tag, env_id = self.docker_sandbox.create_env(self.packages)
            
            # Prepare port mappings
            port_args = []
            for host_port, container_port in self.ports.items():
                port_args.extend(["-p", f"{host_port}:{container_port}"])
            
            # Prepare volume mappings
            volume_args = []
            for host_path, container_path in self.volumes.items():
                volume_args.extend(["-v", f"{host_path}:{container_path}"])
            
            # Prepare environment variables
            env_args = []
            for key, value in self.env_vars.items():
                env_args.extend(["-e", f"{key}={value}"])
            
            # Run the container
            cmd = [
                "docker", "run", "-d", "--name", f"devopy_editor_{self.sandbox_id}"
            ]
            
            if self.auto_remove:
                cmd.append("--rm")
                
            cmd.extend(port_args)
            cmd.extend(volume_args)
            cmd.extend(env_args)
            cmd.append(image_tag)
            
            # Start container with a simple command to keep it running
            cmd.extend(["tail", "-f", "/dev/null"])
            
            self.container_id = subprocess.check_output(cmd).decode('utf-8').strip()
            self.status = "running"
            self.ready = True
            
            print(f"[INFO] Docker sandbox started: {self.sandbox_id} (Container ID: {self.container_id})")
            return True
        except Exception as e:
            self.status = f"error: {str(e)}"
            print(f"[ERROR] Failed to start Docker sandbox: {e}")
            return False
    
    def execute(self, command: List[str], workdir: str = "/app") -> Dict[str, Any]:
        """Execute a command in the Docker sandbox"""
        if not self.ready or not self.container_id:
            return {"success": False, "error": "Sandbox not ready"}
        
        try:
            # Execute command in the container
            exec_cmd = ["docker", "exec", "-w", workdir]
            
            # Add environment variables if needed
            for key, value in self.env_vars.items():
                exec_cmd.extend(["-e", f"{key}={value}"])
            
            exec_cmd.append(self.container_id)
            exec_cmd.extend(command)
            
            result = subprocess.run(
                exec_cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cleanup(self):
        """Stop and remove the Docker container"""
        if self.container_id:
            try:
                subprocess.run(["docker", "stop", self.container_id], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                
                if not self.auto_remove:
                    subprocess.run(["docker", "rm", self.container_id], 
                                  stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL)
                
                print(f"[INFO] Docker sandbox stopped: {self.sandbox_id}")
            except Exception as e:
                print(f"[ERROR] Failed to stop Docker sandbox: {e}")
            
            self.container_id = None
            self.ready = False
            self.status = "stopped"

def editor_sandbox(base_image: str = "python:3.12-slim", 
                  packages: List[str] = None,
                  ports: Dict[int, int] = None,
                  volumes: Dict[str, str] = None,
                  env_vars: Dict[str, str] = None,
                  auto_start: bool = True,
                  auto_install: bool = True):
    """
    Decorator to automatically set up a Docker sandbox for a function.
    
    Args:
        base_image: Base Docker image to use
        packages: List of Python packages to install
        ports: Dictionary mapping host ports to container ports
        volumes: Dictionary mapping host paths to container paths
        env_vars: Dictionary of environment variables
        auto_start: Whether to start the sandbox automatically
        auto_install: Whether to automatically install required packages
    
    Example:
        @editor_sandbox(
            base_image="python:3.12-slim",
            packages=["flask==2.0.1", "requests==2.28.1"],
            ports={5000: 5000},
            volumes={"/home/user/project": "/app"},
            env_vars={"DEBUG": "true"}
        )
        def my_editor_app():
            # This function will have access to a Docker sandbox
            ...
    """
    def decorator(func):
        # If auto_install is enabled, wrap with ensure_packages
        if auto_install and packages:
            func = ensure_packages(packages)(func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique ID for this function instance
            func_id = f"{func.__module__}.{func.__name__}"
            
            with SANDBOX_LOCK:
                # Check if sandbox already exists for this function
                if func_id in SANDBOX_REGISTRY:
                    sandbox = SANDBOX_REGISTRY[func_id]
                else:
                    # Create new sandbox
                    sandbox = EditorDockerSandbox(
                        base_image=base_image,
                        packages=packages,
                        ports=ports,
                        volumes=volumes,
                        env_vars=env_vars
                    )
                    
                    # Start sandbox if auto_start is enabled
                    if auto_start:
                        sandbox.start()
                    
                    # Register sandbox
                    SANDBOX_REGISTRY[func_id] = sandbox
            
            # Add sandbox to function kwargs
            kwargs['sandbox'] = sandbox
            
            # Call the original function
            return func(*args, **kwargs)
        
        # Add metadata to the wrapper function
        wrapper._sandbox_config = {
            "base_image": base_image,
            "packages": packages,
            "ports": ports,
            "volumes": volumes,
            "env_vars": env_vars,
            "auto_start": auto_start
        }
        
        return wrapper
    
    return decorator

def get_sandbox(func_id: str) -> Optional[EditorDockerSandbox]:
    """Get a sandbox by function ID"""
    return SANDBOX_REGISTRY.get(func_id)

def list_sandboxes() -> Dict[str, Dict[str, Any]]:
    """List all registered sandboxes and their status"""
    result = {}
    for func_id, sandbox in SANDBOX_REGISTRY.items():
        result[func_id] = {
            "sandbox_id": sandbox.sandbox_id,
            "container_id": sandbox.container_id,
            "status": sandbox.status,
            "ready": sandbox.ready,
            "base_image": sandbox.base_image,
            "packages": sandbox.packages,
            "ports": sandbox.ports
        }
    return result

def cleanup_all_sandboxes():
    """Stop and remove all Docker sandboxes"""
    for func_id, sandbox in list(SANDBOX_REGISTRY.items()):
        sandbox.cleanup()
        del SANDBOX_REGISTRY[func_id]
