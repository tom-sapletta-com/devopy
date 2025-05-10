#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import argparse
import importlib.util
import venv
import json
from pathlib import Path

# Base directory for virtual environments
VENV_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venvs")
os.makedirs(VENV_BASE_DIR, exist_ok=True)

# Cache file for dependencies
DEPS_CACHE_FILE = os.path.join(VENV_BASE_DIR, "dependencies.json")

def get_example_dependencies(example_path):
    """
    Analyze the example file to determine its dependencies
    """
    dependencies = ["flask", "pyyaml"]  # Base dependencies for all examples
    
    # Read the file and look for import statements
    with open(example_path, 'r') as f:
        content = f.read()
        
    # Check for specific imports and add corresponding packages
    if "graphql" in content:
        dependencies.append("graphql-core")
    if "grpc" in content:
        dependencies.extend(["grpcio", "grpcio-tools"])
    if "rest" in content or "restapi" in content:
        dependencies.append("requests")
    if "openai" in content:
        dependencies.append("openai")
    if "numpy" in content:
        dependencies.append("numpy")
    if "pandas" in content:
        dependencies.append("pandas")
    if "matplotlib" in content or "plt" in content:
        dependencies.append("matplotlib")
    if "torch" in content:
        dependencies.append("torch")
    if "tensorflow" in content or "tf" in content:
        dependencies.append("tensorflow")
    
    return list(set(dependencies))  # Remove duplicates

def create_or_update_venv(example_name, dependencies):
    """
    Create or update a virtual environment for the example
    """
    venv_path = os.path.join(VENV_BASE_DIR, example_name)
    
    # Check if venv already exists
    if not os.path.exists(os.path.join(venv_path, "bin", "python")):
        print(f"Creating virtual environment for {example_name}...")
        venv.create(venv_path, with_pip=True)
    else:
        print(f"Using existing virtual environment for {example_name}...")
    
    # Install or update dependencies
    pip_path = os.path.join(venv_path, "bin", "pip")
    for dep in dependencies:
        print(f"Installing {dep}...")
        subprocess.run([pip_path, "install", "-U", dep], check=True)
    
    return venv_path

def load_dependencies_cache():
    """
    Load the dependencies cache from file
    """
    if os.path.exists(DEPS_CACHE_FILE):
        with open(DEPS_CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_dependencies_cache(cache):
    """
    Save the dependencies cache to file
    """
    with open(DEPS_CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def run_example(example_path, args=None):
    """
    Run an example with its own virtual environment
    """
    # Get the example name from the file path
    example_name = os.path.splitext(os.path.basename(example_path))[0]
    
    # Load dependencies cache
    deps_cache = load_dependencies_cache()
    
    # Check if we need to analyze dependencies
    if example_path not in deps_cache:
        print(f"Analyzing dependencies for {example_name}...")
        dependencies = get_example_dependencies(example_path)
        deps_cache[example_path] = dependencies
        save_dependencies_cache(deps_cache)
    else:
        dependencies = deps_cache[example_path]
    
    # Create or update the virtual environment
    venv_path = create_or_update_venv(example_name, dependencies)
    
    # Run the example
    python_path = os.path.join(venv_path, "bin", "python")
    
    # Add the project root to PYTHONPATH
    env = os.environ.copy()
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{project_root}:{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = project_root
    
    # Prepare command arguments
    cmd = [python_path, example_path]
    if args:
        cmd.extend(args)
    
    print(f"Running {example_name} with arguments: {args if args else 'None'}")
    subprocess.run(cmd, env=env)

def list_examples():
    """
    List all available examples
    """
    examples_dir = os.path.dirname(os.path.abspath(__file__))
    examples = []
    
    for file in os.listdir(examples_dir):
        if file.endswith(".py") and file != os.path.basename(__file__):
            examples.append(file)
    
    return examples

def main():
    parser = argparse.ArgumentParser(description="Run devopy examples with auto-generated virtual environments")
    parser.add_argument("example", nargs="?", help="Example to run (filename or 'list' to see available examples)")
    parser.add_argument("args", nargs="*", help="Arguments to pass to the example")
    
    args = parser.parse_args()
    
    if not args.example or args.example == "list":
        print("Available examples:")
        for example in list_examples():
            print(f"  - {example}")
        return
    
    # Find the example file
    examples_dir = os.path.dirname(os.path.abspath(__file__))
    
    # If the example is a full path, use it directly
    if os.path.exists(args.example):
        example_path = args.example
    else:
        # If it's just a name, look for it in the examples directory
        if not args.example.endswith(".py"):
            args.example += ".py"
        
        example_path = os.path.join(examples_dir, args.example)
        
        if not os.path.exists(example_path):
            print(f"Example {args.example} not found!")
            return
    
    # Run the example
    run_example(example_path, args.args)

if __name__ == "__main__":
    main()
