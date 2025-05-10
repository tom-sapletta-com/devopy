#!/usr/bin/env python3
"""
Launcher script for the matrix editor application
Checks if ports are available before starting the application
"""
import os
import sys
import socket
import subprocess
import time
import logging
import argparse
import signal
import requests
from typing import List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('launcher')

def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port: int = 8000, max_attempts: int = 100) -> Optional[int]:
    """Find an available port starting from start_port"""
    current_port = start_port
    attempts = 0
    
    while attempts < max_attempts:
        if not is_port_in_use(current_port):
            return current_port
        current_port += 1
        attempts += 1
    
    return None

def check_service_health(url: str, max_attempts: int = 20, delay: float = 1.0) -> bool:
    """Check if the service is healthy by making a request to the URL"""
    attempts = 0
    
    logger.info(f"Waiting for service to be available at {url}")
    
    while attempts < max_attempts:
        try:
            logger.debug(f"Health check attempt {attempts+1}/{max_attempts}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"Service is healthy at {url} (status code: {response.status_code})")
                return True
            else:
                logger.warning(f"Service returned status code {response.status_code}")
        except requests.RequestException as e:
            logger.debug(f"Request failed: {str(e)}")
        
        time.sleep(delay)
        attempts += 1
    
    logger.error(f"Service health check failed after {max_attempts} attempts")
    return False

def start_application(app_script: str, port: int) -> Tuple[subprocess.Popen, int]:
    """Start the application on the specified port"""
    # Activate virtual environment if it exists
    venv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.venv')
    python_executable = os.path.join(venv_path, 'bin', 'python') if os.path.exists(venv_path) else 'python'
    
    # Start the application process
    env = os.environ.copy()
    env['PORT'] = str(port)  # Set PORT environment variable for the application
    
    logger.info(f"Starting {app_script} on port {port}")
    
    # Run the application directly with the python executable
    process = subprocess.Popen(
        [python_executable, app_script],
        env=env,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Start a thread to monitor the process output
    def monitor_output():
        while process.poll() is None:
            stdout_line = process.stdout.readline()
            if stdout_line:
                logger.info(f"[APP] {stdout_line.strip()}")
            
            stderr_line = process.stderr.readline()
            if stderr_line:
                logger.error(f"[APP] {stderr_line.strip()}")
    
    import threading
    output_thread = threading.Thread(target=monitor_output, daemon=True)
    output_thread.start()
    
    return process, port

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Launch matrix editor application')
    parser.add_argument('--app', default='matrix_editor.py', help='Application script to run')
    parser.add_argument('--port', type=int, default=None, help='Port to run the application on (default: auto-detect)')
    parser.add_argument('--check-url', default=None, help='URL to check for service health')
    args = parser.parse_args()
    
    # Determine the application script path
    app_script = os.path.abspath(os.path.join(os.path.dirname(__file__), args.app))
    if not os.path.exists(app_script):
        logger.error(f"Application script not found: {app_script}")
        return 1
    
    # Find an available port if not specified
    port = args.port
    if port is None:
        port = find_available_port()
        if port is None:
            logger.error("Could not find an available port")
            return 1
    else:
        # Check if the specified port is available
        if is_port_in_use(port):
            logger.error(f"Port {port} is already in use")
            return 1
    
    # Start the application
    process, port = start_application(app_script, port)
    
    # Check if the application started successfully
    check_url = args.check_url or f"http://localhost:{port}/"
    logger.info(f"Checking service health at {check_url}")
    
    if check_service_health(check_url):
        logger.info(f"Service is running and healthy at {check_url}")
        
        # Keep the application running until interrupted
        try:
            while process.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt, shutting down...")
            process.send_signal(signal.SIGINT)
            process.wait()
    else:
        logger.error("Service failed to start or is not healthy")
        process.terminate()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
