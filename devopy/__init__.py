"""Devopy - Modularny asystent AI do automatyzacji kodu i środowisk Python"""

__version__ = "0.1.0"
__author__ = "tom-sapletta-com"

# Importy będą dostępne po zainstalowaniu paczki
try:
    # Próbujemy zaimportować główne komponenty
    from devopy.api import app
    from devopy.cli import main as cli_main
    from devopy.orchestrator import Orchestrator
    
    # Importujemy narzędzia pomocnicze
    from devopy.utils.resource_monitor import ResourceMonitor
    from devopy.utils.dependency_manager import DependencyManager, fix_code_dependencies
    
    # Importujemy konwertery
    from devopy.converters.text2python import Text2Python, convert_text_to_python
    
    # Importujemy piaskownice
    from devopy.sandbox.docker_sandbox import DockerSandbox, run_code_in_sandbox
    
    # Importujemy nowe komponenty
    from .api import *
    from .api_extensions import *
    from .auto_diag_import import *
    from .auto_heal import *
    from .auto_import import *
    from .bootstrap import *
    from .cli import *
    from .config import *
    from .dependency import *
    from .evolution import *
    from .llm import *
    from .log_db import *
    from .logger import *
    from .main import *
    from .orchestrator import *
    from .output_utils import *
    
    # Importujemy nowy dekorator editor_sandbox
    from .decorators.editor_sandbox import editor_sandbox, EditorDockerSandbox, get_sandbox, list_sandboxes, cleanup_all_sandboxes

    __all__ = [
        'editor_sandbox',
        'EditorDockerSandbox',
        'get_sandbox',
        'list_sandboxes',
        'cleanup_all_sandboxes',
        'app',
        'cli_main',
        'Orchestrator',
        'ResourceMonitor',
        'DependencyManager',
        'fix_code_dependencies',
        'Text2Python',
        'convert_text_to_python',
        'DockerSandbox',
        'run_code_in_sandbox',
    ]
except ImportError:
    # W przypadku błędu importu (np. podczas instalacji) nie robimy nic
    pass
