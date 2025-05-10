import subprocess
import sys
import ast
import inspect
from functools import wraps
from typing import Optional, List, Set

def ensure_packages(packages: Optional[List[str]] = None):
    """
    Decorator to ensure required packages are installed before running the function.
    If packages is None, detect imports in the function source code automatically.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            pkgs: Set[str] = set(packages or [])
            if not pkgs:
                # Automatic detection of imports in the function
                source = inspect.getsource(func)
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            pkgs.add(n.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            pkgs.add(node.module.split('.')[0])
            for pkg in pkgs:
                try:
                    __import__(pkg)
                except ImportError:
                    print(f"Instaluję brakujący pakiet: {pkg}")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            return func(*args, **kwargs)
        return wrapper
    return decorator
