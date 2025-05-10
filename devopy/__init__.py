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
except ImportError:
    # W przypadku błędu importu (np. podczas instalacji) nie robimy nic
    pass
