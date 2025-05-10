#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import subprocess
import argparse
import venv
import importlib.util
import pkgutil
import re
import time
import threading
import webbrowser
from pathlib import Path

# Base directory for virtual environments
VENV_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venvs")
os.makedirs(VENV_BASE_DIR, exist_ok=True)

# Cache file for dependencies
DEPS_CACHE_FILE = os.path.join(VENV_BASE_DIR, "dependencies.json")

# Metadata directory for examples
METADATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metadata")
os.makedirs(METADATA_DIR, exist_ok=True)

class Example:
    def __init__(self, path, name=None, description=None, dependencies=None, category=None):
        self.path = path
        self.name = name or os.path.splitext(os.path.basename(path))[0]
        self.description = description or self._extract_description()
        self.dependencies = dependencies or []
        self.category = category or self._determine_category()
        self.venv_path = os.path.join(VENV_BASE_DIR, self.name)
    
    def _extract_description(self):
        """Extract description from file docstring or comments"""
        try:
            with open(self.path, 'r') as f:
                content = f.read()
                
            # Try to find docstring
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if docstring_match:
                return docstring_match.group(1).strip()
            
            # Try to find comment at the top
            lines = content.split('\n')
            comments = []
            for line in lines:
                if line.strip().startswith('#'):
                    comments.append(line.strip()[1:].strip())
                elif line.strip() and not line.strip().startswith('import') and not line.strip().startswith('from'):
                    break
            
            if comments:
                return ' '.join(comments)
            
            return f"Example: {self.name}"
        except Exception:
            return f"Example: {self.name}"
    
    def _determine_category(self):
        """Determine the category of the example based on its content"""
        with open(self.path, 'r') as f:
            content = f.read().lower()
        
        if "smart_editor" in self.name:
            return "Editor"
        elif "text2python" in self.name:
            return "Code Generation"
        elif "restapi" in content or "graphql" in content or "grpc" in content:
            return "API"
        elif "docker" in content:
            return "Docker"
        elif "visualization" in content or "matplotlib" in content:
            return "Visualization"
        else:
            return "General"
    
    def analyze_dependencies(self):
        """Analyze the example file to determine its dependencies"""
        dependencies = ["flask", "pyyaml"]  # Base dependencies for all examples
        
        # Read the file and look for import statements
        with open(self.path, 'r') as f:
            content = f.read()
            
        # Extract all import statements
        import_lines = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_\.]+)', content, re.MULTILINE)
        
        # Map common module names to pip package names
        module_to_package = {
            "flask": "flask",
            "yaml": "pyyaml",
            "graphql": "graphql-core",
            "grpc": "grpcio",
            "requests": "requests",
            "openai": "openai",
            "numpy": "numpy",
            "pandas": "pandas",
            "matplotlib": "matplotlib",
            "torch": "torch",
            "tensorflow": "tensorflow",
            "sklearn": "scikit-learn",
            "scipy": "scipy",
            "django": "django",
            "sqlalchemy": "sqlalchemy",
            "bs4": "beautifulsoup4",
            "selenium": "selenium",
            "pytest": "pytest",
        }
        
        # Add dependencies based on imports
        for module in import_lines:
            base_module = module.split('.')[0]
            if base_module in module_to_package:
                dependencies.append(module_to_package[base_module])
        
        # Check for specific patterns in the content
        if "graphql" in content:
            dependencies.append("graphql-core")
        if "grpc" in content:
            dependencies.extend(["grpcio", "grpcio-tools"])
        if "rest" in content or "restapi" in content:
            dependencies.append("requests")
        
        # Add devopy itself as a dependency
        dependencies.append("-e " + os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self.dependencies = list(set(dependencies))  # Remove duplicates
        return self.dependencies
    
    def create_or_update_venv(self):
        """Create or update a virtual environment for the example"""
        # Check if venv already exists
        if not os.path.exists(os.path.join(self.venv_path, "bin", "python")):
            print(f"Creating virtual environment for {self.name}...")
            venv.create(self.venv_path, with_pip=True)
        else:
            print(f"Using existing virtual environment for {self.name}...")
        
        # Install or update dependencies
        pip_path = os.path.join(self.venv_path, "bin", "pip")
        for dep in self.dependencies:
            print(f"Installing {dep}...")
            subprocess.run([pip_path, "install", "-U", dep], check=True)
        
        return self.venv_path
    
    def run(self, args=None):
        """Run the example with its own virtual environment"""
        # Make sure dependencies are analyzed
        if not self.dependencies:
            self.analyze_dependencies()
        
        # Create or update the virtual environment
        self.create_or_update_venv()
        
        # Run the example
        python_path = os.path.join(self.venv_path, "bin", "python")
        
        # Add the project root to PYTHONPATH
        env = os.environ.copy()
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{project_root}:{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = project_root
        
        # Prepare command arguments
        cmd = [python_path, self.path]
        if args:
            cmd.extend(args)
        
        print(f"Running {self.name} with arguments: {args if args else 'None'}")
        return subprocess.Popen(cmd, env=env)
    
    def to_dict(self):
        """Convert the example to a dictionary"""
        return {
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "dependencies": self.dependencies,
            "category": self.category,
            "venv_path": self.venv_path
        }

class ExampleManager:
    def __init__(self):
        self.examples = {}
        self.deps_cache = self._load_dependencies_cache()
    
    def _load_dependencies_cache(self):
        """Load the dependencies cache from file"""
        if os.path.exists(DEPS_CACHE_FILE):
            with open(DEPS_CACHE_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_dependencies_cache(self):
        """Save the dependencies cache to file"""
        cache_data = {}
        for path, example in self.examples.items():
            cache_data[path] = example.dependencies
        
        with open(DEPS_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def discover_examples(self):
        """Discover all examples in the examples directory"""
        examples_dir = os.path.dirname(os.path.abspath(__file__))
        
        for file in os.listdir(examples_dir):
            if file.endswith(".py") and file not in ["devopy_launcher.py", "run_example.py"]:
                path = os.path.join(examples_dir, file)
                example = Example(path)
                
                # Check if we have cached dependencies
                if path in self.deps_cache:
                    example.dependencies = self.deps_cache[path]
                else:
                    example.analyze_dependencies()
                
                self.examples[path] = example
        
        # Save the updated dependencies cache
        self._save_dependencies_cache()
        
        return self.examples
    
    def get_example(self, name_or_path):
        """Get an example by name or path"""
        # If it's a path and exists in our examples, return it
        if name_or_path in self.examples:
            return self.examples[name_or_path]
        
        # If it's a full path that exists
        if os.path.exists(name_or_path):
            if name_or_path not in self.examples:
                example = Example(name_or_path)
                example.analyze_dependencies()
                self.examples[name_or_path] = example
                self._save_dependencies_cache()
            return self.examples[name_or_path]
        
        # Try to find by name
        examples_dir = os.path.dirname(os.path.abspath(__file__))
        
        # If it doesn't end with .py, add it
        if not name_or_path.endswith(".py"):
            name_or_path += ".py"
        
        path = os.path.join(examples_dir, name_or_path)
        
        if os.path.exists(path):
            if path not in self.examples:
                example = Example(path)
                example.analyze_dependencies()
                self.examples[path] = example
                self._save_dependencies_cache()
            return self.examples[path]
        
        return None
    
    def run_example(self, name_or_path, args=None):
        """Run an example by name or path"""
        example = self.get_example(name_or_path)
        if example:
            return example.run(args)
        else:
            print(f"Example {name_or_path} not found!")
            return None
    
    def get_examples_by_category(self):
        """Get examples grouped by category"""
        categories = {}
        
        for example in self.examples.values():
            if example.category not in categories:
                categories[example.category] = []
            categories[example.category].append(example)
        
        return categories
    
    def export_metadata(self):
        """Export metadata about all examples"""
        metadata = {
            "examples": {ex.name: ex.to_dict() for ex in self.examples.values()},
            "categories": {cat: [ex.name for ex in examples] 
                          for cat, examples in self.get_examples_by_category().items()}
        }
        
        metadata_path = os.path.join(METADATA_DIR, "examples_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata_path

class DevopyLauncher:
    def __init__(self):
        self.manager = ExampleManager()
        self.examples = self.manager.discover_examples()
    
    def list_examples(self):
        """List all available examples"""
        categories = self.manager.get_examples_by_category()
        
        print("Available examples:")
        for category, examples in categories.items():
            print(f"\n{category}:")
            for example in examples:
                print(f"  - {example.name}: {example.description[:50]}...")
    
    def run_example(self, name_or_path, args=None):
        """Run an example by name or path"""
        return self.manager.run_example(name_or_path, args)
    
    def run_smart_editor(self):
        """Run the Smart Editor with all examples loaded"""
        # Make sure the smart editor example exists
        smart_editor = self.manager.get_example("smart_editor.py")
        if not smart_editor:
            print("Smart Editor example not found!")
            return None
        
        # Export metadata for all examples
        self.manager.export_metadata()
        
        # Run the Smart Editor
        process = smart_editor.run()
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        # Open the browser
        webbrowser.open("http://localhost:5051/?layout=matrix")
        
        return process
    
    def main(self):
        """Main entry point for the launcher"""
        parser = argparse.ArgumentParser(description="Devopy Launcher - Run examples with auto-generated virtual environments")
        parser.add_argument("example", nargs="?", help="Example to run (filename or 'list' to see available examples, 'editor' to launch Smart Editor)")
        parser.add_argument("args", nargs="*", help="Arguments to pass to the example")
        
        args = parser.parse_args()
        
        if not args.example or args.example == "list":
            self.list_examples()
            return
        
        if args.example == "editor":
            self.run_smart_editor()
            return
        
        self.run_example(args.example, args.args)

if __name__ == "__main__":
    launcher = DevopyLauncher()
    launcher.main()
